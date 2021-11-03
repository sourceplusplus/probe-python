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

    def __init__(self, **kwargs):
        probe_config = yaml.full_load(open("config/spp-probe.yml", "r"))
        probe_config["spp"]["platform_host"] = self.get_config_value(
            "SPP_PLATFORM_HOST", probe_config["spp"]["platform_host"], "localhost"
        )
        probe_config["spp"]["platform_port"] = self.get_config_value(
            "SPP_PLATFORM_PORT", probe_config["spp"]["platform_port"], 5450
        )
        probe_config["spp"]["verify_host"] = self.get_config_value(
            "SPP_TLS_VERIFY_HOST", probe_config["spp"]["verify_host"], True
        )

        skywalking_host = self.get_config_value("SPP_SKYWALKING_HOST", "localhost", "localhost")
        skywalking_port = self.get_config_value("SPP_SKYWALKING_PORT", 11800, 11800)
        probe_config["skywalking"]["collector"]["backend_service"] = self.get_config_value(
            "SPP_SKYWALKING_BACKEND_SERVICE",
            probe_config["skywalking"]["collector"]["backend_service"],
            skywalking_host + ":" + str(skywalking_port)
        )
        self.probe_config = probe_config

        self.instrument_remote = None
        self.probe_id = os.getenv("SPP_PROBE_ID", str(uuid.uuid4()))
        self.service_name = os.getenv("SPP_SERVICE_NAME", "python")
        for key, val in kwargs.items():
            self.__dict__[key] = val

    def attach(self):
        options = {}
        if not os.getenv("SPP_DISABLE_TLS", False):
            options = {"ssl_options": {
                "ca_data": "-----BEGIN CERTIFICATE-----\n" +
                           self.probe_config["spp"]["platform_certificate"] +
                           "\n-----END CERTIFICATE-----",
                "check_hostname": self.probe_config["spp"]["verify_host"]
            }}

        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        eb = EventBus(
            host=self.probe_config["spp"]["platform_host"], port=self.probe_config["spp"]["platform_port"],
            ssl_context=ssl_ctx
        )
        eb.connect()
        self.__send_connected(eb)
        self.instrument_remote = LiveInstrumentRemote(eb)

        config.init(
            collector_address=self.probe_config["skywalking"]["collector"]["backend_service"],
            service_name=self.service_name,
            log_reporter_active=True
        )
        agent.start()

    def __send_connected(self, eb: EventBus):
        reply_address = str(uuid.uuid4())
        eb.send(address="spp.platform.status.probe-connected", body={
            "probeId": self.probe_id,
            "connectionTime": round(time.time() * 1000),
            "meta": {
                "language": "python",
                "probe_version": __version__,
                "python_version": sys.version
            }
        }, reply_handler=lambda msg: self.__register_remotes(eb, reply_address, msg["body"]["value"]))

    def __register_remotes(self, eb, reply_address, status):
        eb.unregister_handler(reply_address)
        eb.register_handler(
            address="spp.probe.command.live-breakpoint-remote",
            handler=lambda msg: self.instrument_remote.handle_instrument_command(
                LiveInstrumentCommand.from_json(json.dumps(msg["body"])), LiveInstrumentType.BREAKPOINT
            )
        )
        eb.register_handler(
            address="spp.probe.command.live-log-remote",
            handler=lambda msg: self.instrument_remote.handle_instrument_command(
                LiveInstrumentCommand.from_json(json.dumps(msg["body"])), LiveInstrumentType.LOG
            )
        )
