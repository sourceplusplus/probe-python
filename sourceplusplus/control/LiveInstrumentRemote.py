import json
import sys
import threading
from nopdb import nopdb
from vertx import EventBus

from sourceplusplus.models.command.CommandType import CommandType
from sourceplusplus.models.command.LiveInstrumentCommand import LiveInstrumentCommand
from sourceplusplus.models.command.LiveInstrumentContext import LiveInstrumentContext
from sourceplusplus.models.instrument.LiveBreakpoint import LiveBreakpoint
from sourceplusplus.models.instrument.LiveLog import LiveLog
from sourceplusplus.models.instrument.LiveMeter import LiveMeter
from sourceplusplus.models.instrument.common.LiveInstrumentType import LiveInstrumentType
from sourceplusplus.models.instrument.common.LiveSourceLocation import LiveSourceLocation


class LiveInstrumentRemote(object):
    instruments = {}
    eb = None
    dbg = None

    def __init__(self, eb: EventBus):
        LiveInstrumentRemote.eb = eb
        LiveInstrumentRemote.dbg = nopdb.get_nopdb()
        LiveInstrumentRemote.dbg.start()
        threading.settrace(sys.gettrace())

    def add_live_instrument(self, context: LiveInstrumentContext, instrument_type: LiveInstrumentType):
        for i in context.instruments:
            if instrument_type == LiveInstrumentType.BREAKPOINT:
                live_instrument = LiveBreakpoint.from_json(i)
            elif instrument_type == LiveInstrumentType.LOG:
                live_instrument = LiveLog.from_json(i)
            else:
                live_instrument = LiveMeter.from_json(i)
            bp = LiveInstrumentRemote.dbg.breakpoint(
                file=live_instrument.location.source[live_instrument.location.source.rfind("/") + 1:],
                line=live_instrument.location.line
            )
            LiveInstrumentRemote.instruments[live_instrument.id] = [bp, live_instrument]
            if instrument_type == LiveInstrumentType.BREAKPOINT:
                bp.exec("import sourceplusplus.control.ContextReceiver as ContextReceiver\n"
                        "ContextReceiver.apply_breakpoint('" + live_instrument.id + "',globals(),locals())")
                self.eb.publish(address="spp.platform.status.live-breakpoint-applied", body=json.loads(i))
            elif instrument_type == LiveInstrumentType.LOG:
                bp.exec("import sourceplusplus.control.ContextReceiver as ContextReceiver\n"
                        "ContextReceiver.apply_log('" + live_instrument.id + "',globals(),locals())")
                self.eb.publish(address="spp.platform.status.live-log-applied", body=json.loads(i))
            else:
                bp.exec("import sourceplusplus.control.ContextReceiver as ContextReceiver\n"
                        "ContextReceiver.apply_meter('" + live_instrument.id + "',globals(),locals())")
                self.eb.publish(address="spp.platform.status.live-meter-applied", body=json.loads(i))

    def remove_live_instrument(self, context: LiveInstrumentContext, type: LiveInstrumentType):
        print("Removing live instrument(s)")
        for i in context.instruments:
            if type == LiveInstrumentType.BREAKPOINT:
                instrument = LiveBreakpoint.from_json(i)
            elif type == LiveInstrumentType.LOG:
                instrument = LiveLog.from_json(i)
            else:
                instrument = LiveMeter.from_json(i)
            try:
                LiveInstrumentRemote.dbg.remove_callback(LiveInstrumentRemote.instruments.pop(instrument.id)[0]._handle)
            except KeyError:
                pass
        for i in context.locations:
            loc = LiveSourceLocation.from_json(i)
            delete = []
            for key, val in LiveInstrumentRemote.instruments.items():
                if val[1].type == type and val[1].location == loc:
                    delete.append(key)
            for i in delete:
                del LiveInstrumentRemote.instruments[i]

    def handle_instrument_command(self, command: LiveInstrumentCommand, instrument_type: LiveInstrumentType):
        print("Received command: " + command.command_type)
        if command.command_type == CommandType.ADD_LIVE_INSTRUMENT:
            if instrument_type == LiveInstrumentType.BREAKPOINT:
                self.add_live_instrument(command.context, LiveInstrumentType.BREAKPOINT)
            elif instrument_type == LiveInstrumentType.LOG:
                self.add_live_instrument(command.context, LiveInstrumentType.LOG)
            else:
                self.add_live_instrument(command.context, LiveInstrumentType.METER)
        elif command.command_type == CommandType.REMOVE_LIVE_INSTRUMENT:
            self.remove_live_instrument(command.context, instrument_type)
