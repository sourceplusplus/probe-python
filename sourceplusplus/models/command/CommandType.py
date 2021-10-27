from enum import Enum


class CommandType(str, Enum):
    GET_LIVE_INSTRUMENTS = "GET_LIVE_INSTRUMENTS"
    ADD_LIVE_INSTRUMENT = "ADD_LIVE_INSTRUMENT"
    REMOVE_LIVE_INSTRUMENT = "REMOVE_LIVE_INSTRUMENT"
