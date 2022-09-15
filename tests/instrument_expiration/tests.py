import json
import time
import unittest
from unittest.mock import MagicMock

from sourceplusplus.control.LiveInstrumentRemote import LiveInstrumentRemote
from sourceplusplus.models.command.LiveInstrumentCommand import LiveInstrumentCommand


class TestSum(unittest.TestCase):

    def test_breakpoint_expires(self):
        eb_mock = MagicMock()
        instrument_remote = LiveInstrumentRemote(eb_mock)

        # Add breakpoint
        raw_command = {
            "commandType": "ADD_LIVE_INSTRUMENT",
            "instruments": [
                {
                    "location": {
                        "source": "E2ETest.py",
                        "line": 18, "service": None,
                        "serviceInstance": None,
                        "commitId": None,
                        "fileChecksum": None
                    },
                    "condition": None,
                    "expiresAt": round(time.time() * 1000) + 2000,
                    "hitLimit": 1,
                    "id": "3145bbee-8d81-4184-8c3d-f97f208a6e15",
                    "applyImmediately": False,
                    "applied": False,
                    "pending": True,
                    "throttle": {
                        "limit": 1,
                        "step": "SECOND"
                    },
                    "meta": {},
                    "type": "BREAKPOINT"
                }
            ],
            "locations": []
        }
        command = LiveInstrumentCommand.from_json(json.dumps(raw_command))
        instrument_remote.add_live_instrument(command)

        # Ensure breakpoint was added
        self.assertEqual(len(instrument_remote.instruments), 1)

        # Wait for breakpoint to expire
        time.sleep(5)

        # Ensure breakpoint was removed
        self.assertEqual(len(instrument_remote.instruments), 0)
