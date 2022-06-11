import json

import humps

from .common.LiveInstrument import LiveInstrument
from .common.LiveInstrumentType import LiveInstrumentType
from .common.LiveSourceLocation import LiveSourceLocation
from .common.throttle.HitThrottle import HitThrottle
from .common.throttle.ThrottleStep import ThrottleStep


class LiveMeter(LiveInstrument):
    def __init__(self, location: LiveSourceLocation):
        super().__init__(location)
        self.hit_limit = -1
        self.type = LiveInstrumentType.METER

    def to_dict(self):
        dict = humps.camelize(json.loads(self.to_json()))
        dict["meta"] = self.__dict__["meta"]
        return dict

    @classmethod
    def from_dict(cls, json_dict):
        # todo: easier way to convert
        location = LiveSourceLocation(json_dict["location"]["source"], json_dict["location"]["line"])
        meter = LiveMeter(location)
        for key in json_dict:
            setattr(meter, key, json_dict[key])
        meter.location = LiveSourceLocation(json_dict["location"]["source"], json_dict["location"]["line"])

        if "throttle" in json_dict:
            meter.throttle = HitThrottle(json_dict["throttle"]["limit"], ThrottleStep(json_dict["throttle"]["step"]))

        meter.type = LiveInstrumentType.METER
        return meter

    @classmethod
    def from_json(cls, json_str):
        json_dict = humps.decamelize(json.loads(json_str))
        return cls.from_dict(json_dict)
