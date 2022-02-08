import json

import humps

from .common.LiveInstrument import LiveInstrument
from .common.LiveInstrumentType import LiveInstrumentType
from .common.LiveSourceLocation import LiveSourceLocation
from .common.throttle.HitThrottle import HitThrottle
from .common.throttle.ThrottleStep import ThrottleStep


class LiveLog(LiveInstrument):
    def __init__(self, location: LiveSourceLocation):
        super().__init__(location)
        self.log_format = None
        self.log_arguments = []
        self.hit_limit = None
        self.type = LiveInstrumentType.LOG

    def to_dict(self):
        dict = humps.camelize(json.loads(self.to_json()))
        dict["meta"] = self.__dict__["meta"]
        return dict

    @classmethod
    def from_dict(cls, json_dict):
        # todo: easier way to convert
        location = LiveSourceLocation(json_dict["location"]["source"], json_dict["location"]["line"])
        log = LiveLog(location)
        for key in json_dict:
            setattr(log, key, json_dict[key])
        log.location = LiveSourceLocation(json_dict["location"]["source"], json_dict["location"]["line"])
        log.throttle = HitThrottle(json_dict["throttle"]["limit"], ThrottleStep(json_dict["throttle"]["step"]))
        log.type = LiveInstrumentType.LOG
        return log

    @classmethod
    def from_json(cls, json_str):
        json_dict = humps.decamelize(json.loads(json_str))
        return cls.from_dict(json_dict)
