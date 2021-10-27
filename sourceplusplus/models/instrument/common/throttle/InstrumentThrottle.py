from .ThrottleStep import ThrottleStep


class InstrumentThrottle(object):
    def __init__(self, limit: int, step: ThrottleStep):
        self.limit = limit
        self.step = step

    DEFAULT = object.__init__(1, ThrottleStep.SECOND)
