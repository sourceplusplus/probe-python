import json

import humps
import time

from .LiveSourceLocation import LiveSourceLocation
from .throttle.HitThrottle import HitThrottle
from ... import filter_model


class LiveInstrument(object):

    def __init__(self, location: LiveSourceLocation):
        self.location = location
        self.condition = None
        self.expires_at = None
        self.hit_limit = None
        self.id = None
        self.type = None
        self.apply_immediately = False
        self.applied = False
        self.pending = False
        self.throttle: HitThrottle = None

    def to_json(self):
        return json.dumps(self, default=lambda o: humps.camelize(filter_model(o.__dict__)))

    def is_finished(self):
        if self.expires_at is not None and round(time.time() * 1000) >= self.expires_at:
            return True
        else:
            return self.hit_limit != -1 and self.throttle._total_hit_count >= self.hit_limit
