from enum import Enum


class LiveInstrumentType(str, Enum):
    BREAKPOINT = "BREAKPOINT"
    LOG = "LOG"
    METER = "METER"
    SPAN = "SPAN"

    @staticmethod
    def from_string(value):
        return LiveInstrumentType(value)
