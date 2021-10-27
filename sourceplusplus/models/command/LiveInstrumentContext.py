import json
from typing import List

import humps


class LiveInstrumentContext(object):
    def __init__(self, instruments: List[str], locations: List[str]):
        self.instruments = instruments
        self.locations = locations

    def to_json(self):
        return json.dumps(self, default=lambda o: humps.camelize(o.__dict__))
