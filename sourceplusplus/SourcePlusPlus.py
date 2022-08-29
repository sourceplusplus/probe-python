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


class SourcePlusPlus(object):

    @staticmethod
    def __set_config_default(config_dict, config_name, env, default):
        config_path = config_name.split(".")
        tmp_config = config_dict
        for i in range(len(config_path)):
            if i == len(config_path) - 1 and tmp_config.get(config_path[i]) is None:
                if default is bool:
                    tmp_config[config_path[i]] = str(os.getenv(env, default)).lower() == "true"
                else:
                    tmp_config[config_path[i]] = os.getenv(env, default)

            if tmp_config.get(config_path[i]) is None:
                tmp_config[config_path[i]] = {}
                tmp_config = tmp_config[config_path[i]]
            else:
                tmp_config = tmp_config[config_path[i]]

    def __init__(self, args: dict = None):
        if args is None:
            args = {}
        probe_config_file = os.getenv("SPP_PROBE_CONFIG_FILE", "spp-probe.yml")
        probe_config = {}
        if os.path.exists(probe_config_file):
            probe_config = yaml.full_load(open(probe_config_file, "r"))

        # set spp default values
        self.__set_config_default(
            probe_config, "spp.probe_id", "SPP_PROBE_ID",
            str(uuid.uuid4())
        )
        self.__set_config_default(
            probe_config, "spp.platform_host", "SPP_PLATFORM_HOST",
            "localhost"
        )
        self.__set_config_default(
            probe_config, "spp.platform_port", "SPP_PLATFORM_PORT",
            12800
        )
        self.__set_config_default(
            probe_config, "spp.verify_host", "SPP_TLS_VERIFY_HOST",
            True
        )
        self.__set_config_default(
            probe_config, "spp.ssl_enabled", "SPP_HTTP_SSL_ENABLED",
            True
        )
        self.__set_config_default(
            probe_config, "skywalking.agent.service_name", "SPP_SERVICE_NAME",
            "spp"
        )

        # set sw default values
        self.__set_config_default(
            probe_config, "skywalking.collector.backend_service", "SPP_SKYWALKING_BACKEND_SERVICE",
            probe_config["spp"]["platform_host"] + ":11800"
        )
        self.__set_config_default(
            probe_config, "skywalking.plugin.toolkit.log.transmit_formatted", "SPP_SKYWALKING_LOG_TRANSMIT_FORMATTED",
            True
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
            force_tls=self.probe_config["spp"]["ssl_enabled"],
            log_reporter_formatted=self.probe_config["skywalking"]["plugin"]["toolkit"]["log"]["transmit_formatted"]
        )
        agent.start()

        ca_data = None
        if self.probe_config["spp"]["ssl_enabled"] is True \
                and self.probe_config["spp"].get("probe_certificate") is not None:
            ca_data = "-----BEGIN CERTIFICATE-----\n" + \
                      self.probe_config["spp"]["probe_certificate"] + \
                      "\n-----END CERTIFICATE-----"

        ssl_ctx = ssl.create_default_context(cadata=ca_data)
        ssl_ctx.check_hostname = self.probe_config["spp"]["verify_host"]
        if self.probe_config["spp"]["ssl_enabled"] is False:
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
            "instanceId": self.probe_config["spp"]["probe_id"],
            "connectionTime": round(time.time() * 1000),
            "meta": probe_metadata
        }, reply_handler=lambda msg: self.__register_remotes(eb, reply_address, msg["body"]))

    def __register_remotes(self, eb, reply_address, status):
        eb.unregister_handler(reply_address)
        eb.register_handler(
            address="spp.probe.command.live-instrument-remote",
            handler=lambda msg: self.instrument_remote.handle_instrument_command(
                LiveInstrumentCommand.from_json(json.dumps(msg["body"]))
            )
        )
        eb.register_handler(
            address="spp.probe.command.live-instrument-remote:" + self.probe_config["spp"]["probe_id"],
            handler=lambda msg: self.instrument_remote.handle_instrument_command(
                LiveInstrumentCommand.from_json(json.dumps(msg["body"]))
            )
        )
