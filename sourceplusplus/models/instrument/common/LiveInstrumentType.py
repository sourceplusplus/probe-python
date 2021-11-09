from enum import Enum


class LiveInstrumentType(str, Enum):
    BREAKPOINT = "BREAKPOINT"
    LOG = "LOG"
    METER = "METER"
