import json
from typing import List

import humps

from .CommandType import CommandType


class LiveInstrumentCommand(object):
    def __init__(self, command_type: CommandType, instruments: List[dict], locations: List[dict]):
        self.command_type = command_type
        self.instruments = instruments
        self.locations = locations

    def to_json(self):
        return json.dumps(self, default=lambda o: humps.camelize(o.__dict__))

    @classmethod
    def from_json(cls, json_str):
        json_dict = humps.decamelize(json.loads(json_str))
        return LiveInstrumentCommand(json_dict["command_type"], json_dict["instruments"], json_dict["locations"])
