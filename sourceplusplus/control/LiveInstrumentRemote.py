import json
import sys
import threading

from vertx import EventBus

from nopdb import nopdb
from sourceplusplus.models.command.CommandType import CommandType
from sourceplusplus.models.command.LiveInstrumentCommand import LiveInstrumentCommand
from sourceplusplus.models.command.LiveInstrumentContext import LiveInstrumentContext
from sourceplusplus.models.instrument.LiveBreakpoint import LiveBreakpoint
from sourceplusplus.models.instrument.LiveLog import LiveLog
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

    def add_live_log(self, context: LiveInstrumentContext):
        for i in context.instruments:
            live_log = LiveLog.from_json(i)
            bp = LiveInstrumentRemote.dbg.breakpoint(file=live_log.location.source, line=live_log.location.line)
            LiveInstrumentRemote.instruments[live_log.id] = [bp, live_log]
            bp.exec("import sourceplusplus.control.ContextReceiver as ContextReceiver\n"
                    "ContextReceiver.do_log('" + live_log.id + "',globals(),locals())")
            self.eb.publish(address="spp.platform.status.live-log-applied", body=json.loads(i))

    def remove_live_log(self, context: LiveInstrumentContext):
        print("Removing live log(s)")
        for i in context.instruments:
            live_log = LiveLog.from_json(i)
            try:
                LiveInstrumentRemote.dbg.remove_callback(LiveInstrumentRemote.instruments.pop(live_log.id)[0]._handle)
            except KeyError:
                pass
        for i in context.locations:
            loc = LiveSourceLocation.from_json(i)
            delete = []
            for key, val in LiveInstrumentRemote.instruments.items():
                if isinstance(val[1], LiveLog) and val[1].location == loc:
                    delete.append(key)
            for i in delete:
                del LiveInstrumentRemote.instruments[i]

    def add_live_breakpoint(self, context: LiveInstrumentContext):
        print("Adding live breakpoint(s)")
        for i in context.instruments:
            live_bp = LiveBreakpoint.from_json(i)
            bp = LiveInstrumentRemote.dbg.breakpoint(file=live_bp.location.source, line=live_bp.location.line)
            LiveInstrumentRemote.instruments[live_bp.id] = [bp, live_bp]
            bp.exec("import sourceplusplus.control.ContextReceiver as ContextReceiver\n"
                    "ContextReceiver.do_breakpoint('" + live_bp.id + "',globals(),locals())")
            self.eb.publish(address="spp.platform.status.live-breakpoint-applied", body=json.loads(i))

    def remove_live_breakpoint(self, context: LiveInstrumentContext):
        print("Removing live breakpoint(s)")
        for i in context.instruments:
            live_bp = LiveBreakpoint.from_json(i)
            try:
                LiveInstrumentRemote.dbg.remove_callback(LiveInstrumentRemote.instruments.pop(live_bp.id)[0]._handle)
            except KeyError:
                pass
        for i in context.locations:
            loc = LiveSourceLocation.from_json(i)
            delete = []
            for key, val in LiveInstrumentRemote.instruments.items():
                if isinstance(val[1], LiveBreakpoint) and val[1].location == loc:
                    delete.append(key)
            for i in delete:
                del LiveInstrumentRemote.instruments[i]

    def handle_instrument_command(self, command: LiveInstrumentCommand, instrument_type: LiveInstrumentType):
        print("Received command: " + command.command_type)
        if command.command_type == CommandType.ADD_LIVE_INSTRUMENT:
            if instrument_type == LiveInstrumentType.BREAKPOINT:
                self.add_live_breakpoint(command.context)
            else:
                self.add_live_log(command.context)
        elif command.command_type == CommandType.REMOVE_LIVE_INSTRUMENT:
            if instrument_type == LiveInstrumentType.BREAKPOINT:
                self.remove_live_breakpoint(command.context)
            else:
                self.remove_live_log(command.context)
