import sys
import threading

from nopdb import nopdb
from vertx import EventBus

from sourceplusplus.models.command.CommandType import CommandType
from sourceplusplus.models.command.LiveInstrumentCommand import LiveInstrumentCommand
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

    def add_live_instrument(self, command: LiveInstrumentCommand):
        for inst_dict in command.instruments:
            instrument_type: LiveInstrumentType = LiveInstrumentType.from_string(inst_dict["type"])
            if instrument_type == LiveInstrumentType.BREAKPOINT:
                live_instrument = LiveBreakpoint.from_dict(inst_dict)
            elif instrument_type == LiveInstrumentType.LOG:
                live_instrument = LiveLog.from_dict(inst_dict)
            else:
                live_instrument = LiveMeter.from_dict(inst_dict)
            bp = LiveInstrumentRemote.dbg.breakpoint(
                file=live_instrument.location.source[live_instrument.location.source.rfind("/") + 1:],
                line=live_instrument.location.line
            )
            LiveInstrumentRemote.instruments[live_instrument.id] = [bp, live_instrument]
            if instrument_type == LiveInstrumentType.BREAKPOINT:
                bp.exec("import sourceplusplus.control.ContextReceiver as ContextReceiver\n"
                        "ContextReceiver.apply_breakpoint('" + live_instrument.id + "',globals(),locals())")
                self.eb.publish(address="spp.processor.status.live-instrument-applied", body=live_instrument.to_dict())
            elif instrument_type == LiveInstrumentType.LOG:
                bp.exec("import sourceplusplus.control.ContextReceiver as ContextReceiver\n"
                        "ContextReceiver.apply_log('" + live_instrument.id + "',globals(),locals())")
                self.eb.publish(address="spp.processor.status.live-instrument-applied", body=live_instrument.to_dict())
            else:
                bp.exec("import sourceplusplus.control.ContextReceiver as ContextReceiver\n"
                        "ContextReceiver.apply_meter('" + live_instrument.id + "',globals(),locals())")
                self.eb.publish(address="spp.processor.status.live-instrument-applied", body=live_instrument.to_dict())

    def remove_live_instrument(self, command: LiveInstrumentCommand):
        print("Removing live instrument(s)")
        for inst_dict in command.instruments:
            if type == LiveInstrumentType.BREAKPOINT:
                instrument = LiveBreakpoint.from_dict(inst_dict)
            elif type == LiveInstrumentType.LOG:
                instrument = LiveLog.from_dict(inst_dict)
            else:
                instrument = LiveMeter.from_dict(inst_dict)
            try:
                LiveInstrumentRemote.dbg.remove_callback(LiveInstrumentRemote.instruments.pop(instrument.id)[0]._handle)
            except KeyError:
                pass
        for inst_dict in command.locations:
            loc = LiveSourceLocation.from_json(inst_dict)
            delete = []
            for key, val in LiveInstrumentRemote.instruments.items():
                if val[1].type == type and val[1].location == loc:
                    delete.append(key)
            for inst_dict in delete:
                del LiveInstrumentRemote.instruments[inst_dict]

    def handle_instrument_command(self, command: LiveInstrumentCommand):
        print("Received command: " + command.command_type)
        if command.command_type == CommandType.ADD_LIVE_INSTRUMENT:
            self.add_live_instrument(command)
        elif command.command_type == CommandType.REMOVE_LIVE_INSTRUMENT:
            self.remove_live_instrument(command)
