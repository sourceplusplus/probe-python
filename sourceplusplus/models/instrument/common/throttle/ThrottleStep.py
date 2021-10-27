from enum import Enum


class ThrottleStep(str, Enum):
    SECOND = "SECOND"
    MINUTE = "MINUTE"
    HOUR = "HOUR"
    DAY = "DAY"

    def get_millis(self, duration):
        if self == ThrottleStep.SECOND:
            return 1000 * duration
        elif self == ThrottleStep.MINUTE:
            return 1000 * 60 * duration
        elif self == ThrottleStep.HOUR:
            return 1000 * 60 * 60 * duration
        elif self == ThrottleStep.DAY:
            return 1000 * 60 * 60 * 24 * duration
        else:
            raise ValueError
