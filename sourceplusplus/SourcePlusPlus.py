import json
import os
import ssl
import sys
import time
import uuid

import yaml
from skywalking import config, agent
from vertx import EventBus

from sourceplusplus import __version__
from .control.LiveInstrumentRemote import LiveInstrumentRemote
from .models.command.LiveInstrumentCommand import LiveInstrumentCommand
from .models.instrument.common.LiveInstrumentType import LiveInstrumentType


class SourcePlusPlus(object):

    def get_config_value(self, env, default, true_default):
        env_value = os.getenv(env)
        if env_value is not None:
            return env_value
        elif default is not None:
            return default
        else:
            return true_default

    def __init__(self, args: dict = None):
        if args is None:
            args = {}
        probe_config_file = os.getenv("SPP_PROBE_CONFIG_FILE", "spp-probe.yml")
        probe_config = {}
        if os.path.exists(probe_config_file):
            probe_config = yaml.full_load(open(probe_config_file, "r"))

        # ensure probe_config has required keys
        if probe_config.get("spp") is None:
            probe_config["spp"] = {}
        if probe_config.get("skywalking") is None:
            probe_config["skywalking"] = {}
        if probe_config["skywalking"].get("collector") is None:
            probe_config["skywalking"]["collector"] = {}
        if probe_config["skywalking"].get("agent") is None:
            probe_config["skywalking"]["agent"] = {}

        # set default values
        probe_config["spp"]["probe_id"] = self.get_config_value(
            "SPP_PROBE_ID", probe_config["spp"].get("probe_id"), str(uuid.uuid4())
        )
        probe_config["spp"]["platform_host"] = self.get_config_value(
            "SPP_PLATFORM_HOST", probe_config["spp"].get("platform_host"), "localhost"
        )
        probe_config["spp"]["platform_port"] = self.get_config_value(
            "SPP_PLATFORM_PORT", probe_config["spp"].get("platform_port"), 5450
        )
        probe_config["spp"]["verify_host"] = str(self.get_config_value(
            "SPP_TLS_VERIFY_HOST", probe_config["spp"].get("verify_host"), True
        )).lower() == "true"
        probe_config["spp"]["disable_tls"] = str(self.get_config_value(
            "SPP_DISABLE_TLS", probe_config["spp"].get("disable_tls"), False
        )).lower() == "true"
        probe_config["skywalking"]["agent"]["service_name"] = self.get_config_value(
            "SPP_SERVICE_NAME", probe_config["skywalking"]["agent"].get("service_name"), "spp"
        )

        skywalking_host = self.get_config_value("SPP_SKYWALKING_HOST", "localhost", "localhost")
        skywalking_port = self.get_config_value("SPP_SKYWALKING_PORT", 11800, 11800)
        probe_config["skywalking"]["collector"]["backend_service"] = self.get_config_value(
            "SPP_SKYWALKING_BACKEND_SERVICE",
            probe_config["skywalking"]["collector"].get("backend_service"),
            skywalking_host + ":" + str(skywalking_port)
        )

        for key, val in args.items():
            tmp_config = probe_config
            loc = key.split(".")
            for i in range(len(loc)):
                if tmp_config.get(loc[i]) is None:
                    tmp_config[loc[i]] = {}
                if i == len(loc) - 1:
                    tmp_config[loc[i]] = val
                else:
                    tmp_config = tmp_config[loc[i]]

        self.probe_config = probe_config
        self.instrument_remote = None

    def attach(self):
        config.init(
            collector_address=self.probe_config["skywalking"]["collector"]["backend_service"],
            service_name=self.probe_config["skywalking"]["agent"]["service_name"],
            log_reporter_active=True,
            force_tls=self.probe_config["spp"]["disable_tls"] is False,
            log_reporter_formatted=False
        )
        agent.start()

        ca_data = None
        if self.probe_config["spp"]["disable_tls"] is False \
                and self.probe_config["spp"].get("probe_certificate") is not None:
            ca_data = "-----BEGIN CERTIFICATE-----\n" + \
                      self.probe_config["spp"]["probe_certificate"] + \
                      "\n-----END CERTIFICATE-----"

        ssl_ctx = ssl.create_default_context(cadata=ca_data)
        ssl_ctx.check_hostname = self.probe_config["spp"]["verify_host"]
        if self.probe_config["spp"]["disable_tls"] is True:
            ssl_ctx = None
        elif ssl_ctx.check_hostname is True:
            ssl_ctx.verify_mode = ssl.CERT_REQUIRED
        else:
            ssl_ctx.verify_mode = ssl.CERT_NONE

        eb = EventBus(
            host=self.probe_config["spp"]["platform_host"], port=self.probe_config["spp"]["platform_port"],
            ssl_context=ssl_ctx
        )
        eb.connect()
        self.__send_connected(eb)
        self.instrument_remote = LiveInstrumentRemote(eb)

    def __send_connected(self, eb: EventBus):
        probe_metadata = {
            "language": "python",
            "probe_version": __version__,
            "python_version": sys.version,
            "service": config.service_name,
            "service_instance": config.service_instance
        }

        # add hardcoded probe meta data (if present)
        if self.probe_config["spp"].get("probe_metadata") is not None:
            for key, val in self.probe_config["spp"].get("probe_metadata").items():
                probe_metadata[key] = val

        # send probe connected event
        reply_address = str(uuid.uuid4())
        eb.send(address="spp.platform.status.probe-connected", body={
            "probeId": self.probe_config["spp"]["probe_id"],
            "connectionTime": round(time.time() * 1000),
            "meta": probe_metadata
        }, reply_handler=lambda msg: self.__register_remotes(eb, reply_address, msg["body"]["value"]))

    def __register_remotes(self, eb, reply_address, status):
        eb.unregister_handler(reply_address)
        eb.register_handler(
            address="spp.probe.command.live-breakpoint-remote:" + self.probe_config["spp"]["probe_id"],
            handler=lambda msg: self.instrument_remote.handle_instrument_command(
                LiveInstrumentCommand.from_json(json.dumps(msg["body"])), LiveInstrumentType.BREAKPOINT
            )
        )
        eb.register_handler(
            address="spp.probe.command.live-log-remote:" + self.probe_config["spp"]["probe_id"],
            handler=lambda msg: self.instrument_remote.handle_instrument_command(
                LiveInstrumentCommand.from_json(json.dumps(msg["body"])), LiveInstrumentType.LOG
            )
        )
        eb.register_handler(
            address="spp.probe.command.live-meter-remote:" + self.probe_config["spp"]["probe_id"],
            handler=lambda msg: self.instrument_remote.handle_instrument_command(
                LiveInstrumentCommand.from_json(json.dumps(msg["body"])), LiveInstrumentType.METER
            )
        )
