import json
import threading
import time
import traceback

from skywalking import config, agent
from skywalking.protocol.common.Common_pb2 import KeyStringValuePair
from skywalking.protocol.logging.Logging_pb2 import LogData, LogDataBody, TextLog, TraceContext, LogTags
from skywalking.trace.context import SpanContext, get_context
from skywalking.trace.tags import Tag

from sourceplusplus.control.LiveInstrumentRemote import LiveInstrumentRemote
from sourceplusplus.models.instrument.LiveBreakpoint import LiveBreakpoint
from sourceplusplus.models.instrument.LiveLog import LiveLog
from sourceplusplus.models.instrument.LiveMeter import LiveMeter


def try_find(var, globals, locals):
    try:
        return locals[var]
    except KeyError:
        return globals[var]


def apply_meter(live_meter_id, globals, locals):
    live_meter: LiveMeter = LiveInstrumentRemote.instruments[live_meter_id][1]
    if live_meter.throttle.is_rate_limited():
        return
    if live_meter.condition is not None and not eval(live_meter.condition, globals, locals):
        return
    pass


def apply_log(live_log_id, globals, locals):
    live_log: LiveLog = LiveInstrumentRemote.instruments[live_log_id][1]
    if live_log.throttle.is_rate_limited():
        return
    if live_log.condition is not None and not eval(live_log.condition, globals, locals):
        return

    log_tags = LogTags()
    core_tags = [
        KeyStringValuePair(key='thread', value=threading.current_thread().name),
        KeyStringValuePair(key='log_id', value=live_log.id)
    ]
    log_tags.data.extend(core_tags)

    for i, arg in enumerate(live_log.log_arguments):
        try:
            log_tags.data.append(KeyStringValuePair(
                key='argument.' + str(i),
                value=str(try_find(arg, globals, locals))
            ))
        except KeyError:
            log_tags.data.append(KeyStringValuePair(
                key='argument.' + str(i),
                value=None
            ))
        except Exception as e:
            print(e)

    sw_context = get_context()
    log_data = LogData(
        timestamp=round(time.time() * 1000),
        service=config.service_name,
        serviceInstance=config.service_instance,
        body=LogDataBody(
            type='text',
            text=TextLog(text=live_log.log_format)
        ),
        traceContext=TraceContext(
            traceId=str(sw_context.segment.related_traces[0]),
            traceSegmentId=str(sw_context.segment.segment_id),
            spanId=sw_context.active_span().sid if sw_context.active_span() else -1
        ),
        tags=log_tags,
    )
    agent.archive_log(log_data)

    if live_log.is_finished():
        try:
            LiveInstrumentRemote.dbg.remove_callback(
                LiveInstrumentRemote.instruments.pop(live_log_id)[0]._handle
            )
        except Exception:
            pass
        LiveInstrumentRemote.eb.send(address="spp.platform.status.live-log-removed", body={
            "log": live_log.to_json(),
            "occurredAt": round(time.time() * 1000)
        })


def apply_breakpoint(live_breakpoint_id, globals, locals):
    globals.pop("SourcePlusPlus", None)
    locals.pop("ContextReceiver", None)

    live_breakpoint: LiveBreakpoint = LiveInstrumentRemote.instruments[live_breakpoint_id][1]
    if live_breakpoint.throttle.is_rate_limited():
        return
    if live_breakpoint.condition is not None and not eval(live_breakpoint.condition, globals, locals):
        return

    operation = live_breakpoint.location.source + ":" + str(live_breakpoint.location.line)
    context: SpanContext = get_context()

    with context.new_local_span(op=operation) as span:
        for key, value in globals.items():
            tag = StringTag(json.dumps({
                key: str(value),  # todo: don't str everything
                "@class": str(type(value)),
                "@identity": id(value)
            }))
            tag.key = "spp.global-variable:" + live_breakpoint.id + ":" + key
            span.tag(tag)

        for key, value in locals.items():
            tag = StringTag(json.dumps({
                key: str(value),  # todo: don't str everything
                "@class": str(type(value)),
                "@identity": id(value)
            }))
            tag.key = "spp.local-variable:" + live_breakpoint.id + ":" + key
            span.tag(tag)

        tag = StringTag(live_breakpoint.location.to_json())
        tag.key = "spp.breakpoint:" + live_breakpoint.id
        span.tag(tag)

        tag = StringTag(''.join(traceback.format_stack()[:-5]))  # todo: can't hardcode depth
        tag.key = "spp.stack-trace:" + live_breakpoint.id
        span.tag(tag)

        tag = StringTag(live_breakpoint.location.source)
        tag.key = "spp.location-source:" + live_breakpoint.id
        span.tag(tag)

        tag = StringTag(str(live_breakpoint.location.line))
        tag.key = "spp.location-line:" + live_breakpoint.id
        span.tag(tag)

    if live_breakpoint.is_finished():
        try:
            LiveInstrumentRemote.dbg.remove_callback(
                LiveInstrumentRemote.instruments.pop(live_breakpoint_id)[0]._handle
            )
        except Exception:
            pass
        LiveInstrumentRemote.eb.send(address="spp.platform.status.live-breakpoint-removed", body={
            "breakpoint": live_breakpoint.to_json(),
            "occurredAt": round(time.time() * 1000)
        })


class ContextReceiver(object):
    pass


class StringTag(Tag):
    key = ""
