import time

from .ThrottleStep import ThrottleStep


class HitThrottle:
    def __init__(self, limit: int, step: ThrottleStep):
        self.limit = limit
        self.step = step
        self._last_reset = -1
        self._hit_count = 0
        self._total_hit_count = 0
        self._total_limited_count = 0

    def is_rate_limited(self) -> bool:
        if self._hit_count < self.limit:
            self._hit_count += 1
            self._total_hit_count += 1
            return False
        self._hit_count += 1

        if round(time.time() * 1000) - self._last_reset > self.step.get_millis(1):
            self._hit_count = 1
            self._total_hit_count += 1
            self._last_reset = round(time.time() * 1000)
            return False
        else:
            self._total_limited_count += 1
            return True

    def get_total_hit_count(self):
        return self._total_hit_count

    def get_total_limited_count(self):
        return self._total_limited_count
