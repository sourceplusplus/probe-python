import json

import humps

from .common.LiveInstrument import LiveInstrument
from .common.LiveInstrumentType import LiveInstrumentType
from .common.LiveSourceLocation import LiveSourceLocation
from .common.throttle.HitThrottle import HitThrottle
from .common.throttle.ThrottleStep import ThrottleStep


class LiveBreakpoint(LiveInstrument):
    def __init__(self, location: LiveSourceLocation):
        super().__init__(location)
        self.hit_limit = 1
        self.type = LiveInstrumentType.BREAKPOINT

    def to_dict(self):
        dict = humps.camelize(json.loads(self.to_json()))
        dict["meta"] = self.__dict__["meta"]
        return dict

    @classmethod
    def from_dict(cls, json_dict):
        # todo: easier way to convert
        location = LiveSourceLocation(json_dict["location"]["source"], json_dict["location"]["line"])
        bp = LiveBreakpoint(location)
        for key in json_dict:
            setattr(bp, key, json_dict[key])
        bp.location = LiveSourceLocation(json_dict["location"]["source"], json_dict["location"]["line"])
        bp.throttle = HitThrottle(json_dict["throttle"]["limit"], ThrottleStep(json_dict["throttle"]["step"]))
        bp.type = LiveInstrumentType.BREAKPOINT
        return bp

    @classmethod
    def from_json(cls, json_str):
        return cls.from_dict(humps.decamelize(json.loads(json_str)))
