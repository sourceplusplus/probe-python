import json

import humps

from .CommandType import CommandType
from .LiveInstrumentContext import LiveInstrumentContext


class LiveInstrumentCommand(object):
    def __init__(self, command_type: CommandType, context: LiveInstrumentContext):
        self.command_type = command_type
        self.context = context

    def to_json(self):
        return json.dumps(self, default=lambda o: humps.camelize(o.__dict__))

    @classmethod
    def from_json(cls, json_str):
        json_dict = humps.decamelize(json.loads(json_str))
        # todo: easier way to convert
        context = LiveInstrumentContext([], [])
        for key in json_dict["context"]:
            setattr(context, key, json_dict["context"][key])
        return LiveInstrumentCommand(json_dict["command_type"], context)
