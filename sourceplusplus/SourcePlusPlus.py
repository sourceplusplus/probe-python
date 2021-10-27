import json
import os
import sys
import time
import uuid

from skywalking import config, agent
from vertx import EventBus

from sourceplusplus import __version__
from .control.LiveInstrumentRemote import LiveInstrumentRemote
from .models.command.LiveInstrumentCommand import LiveInstrumentCommand
from .models.instrument.common.LiveInstrumentType import LiveInstrumentType


class SourcePlusPlus(object):

    def __init__(self, **kwargs):
        self.instrument_remote = None
        self.probe_id = os.getenv("SPP_PROBE_ID", str(uuid.uuid4()))
        self.service_name = os.getenv("SPP_SERVICE_NAME", "python")
        self.spp_host = os.getenv("SPP_PLATFORM_HOST", "localhost")
        self.spp_port = os.getenv("SPP_PLATFORM_PORT", 5450)
        self.skywalking_host = os.getenv("SPP_SKYWALKING_HOST", "localhost")
        self.skywalking_port = os.getenv("SPP_SKYWALKING_PORT", 11800)
        for key, val in kwargs.items():
            self.__dict__[key] = val

    def attach(self):
        eb = EventBus(host=self.spp_host, port=self.spp_port)
        eb.connect()
        self.__send_connected(eb)
        self.instrument_remote = LiveInstrumentRemote(eb)

        config.init(
            collector_address=self.skywalking_host + ':' + str(self.skywalking_port),
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
