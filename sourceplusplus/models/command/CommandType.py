from enum import Enum


class CommandType(str, Enum):
    ADD_LIVE_INSTRUMENT = "ADD_LIVE_INSTRUMENT"
    REMOVE_LIVE_INSTRUMENT = "REMOVE_LIVE_INSTRUMENT"
