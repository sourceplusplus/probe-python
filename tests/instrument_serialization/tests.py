import json
import time
import unittest

from sourceplusplus.models.command.LiveInstrumentCommand import LiveInstrumentCommand
from sourceplusplus.models.instrument.LiveBreakpoint import LiveBreakpoint
from sourceplusplus.models.instrument.LiveLog import LiveLog
from sourceplusplus.models.instrument.common.LiveSourceLocation import LiveSourceLocation
from sourceplusplus.models.instrument.common.throttle.HitThrottle import HitThrottle
from sourceplusplus.models.instrument.common.throttle.ThrottleStep import ThrottleStep


class TestSum(unittest.TestCase):

    def test_command_serialization(self):
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
                    "expiresAt": None,
                    "hitLimit": 1,
                    "id": "3145bbee-8d81-4184-8c3d-f97f208a6e15",
                    "applyImmediately": False,
                    "applied": False,
                    "pending": True,
                    "throttle": {
                        "limit": 1,
                        "step": "SECOND"
                    },
                    "meta": {
                        "created_at": "1644293169743",
                        "created_by": "system",
                        "hit_count": 0
                    },
                    "type": "BREAKPOINT"
                }
            ],
            "locations": []
        }
        command = LiveInstrumentCommand.from_json(json.dumps(raw_command))
        bp = LiveBreakpoint.from_dict(command.instruments[0])
        self.assertEqual(raw_command["instruments"][0], LiveBreakpoint.from_json(bp.to_json()).to_dict())

    def test_deserialize_breakpoint(self):
        raw_bp = {
            "location": {
                "source": "File.py",
                "line": 1,
                "commitId": None,
                "fileChecksum": None
            },
            "condition": "1==1",
            "expiresAt": None,
            "hitLimit": 2,
            "id": "id1",
            "type": "BREAKPOINT",
            "applyImmediately": True,
            "applied": True,
            "pending": True,
            "throttle": {
                "limit": 2,
                "step": "MINUTE"
            }
        }
        bp = LiveBreakpoint.from_json(json.dumps(raw_bp))
        self.assertEqual(bp.location.source, "File.py")
        self.assertEqual(bp.location.line, 1)
        self.assertEqual(bp.condition, "1==1")
        self.assertEqual(bp.expires_at, None)
        self.assertEqual(bp.hit_limit, 2)
        self.assertEqual(bp.type, "BREAKPOINT")
        self.assertEqual(bp.apply_immediately, True)
        self.assertEqual(bp.applied, True)
        self.assertEqual(bp.pending, True)
        self.assertEqual(bp.throttle.limit, 2)
        self.assertEqual(bp.throttle.step, ThrottleStep.MINUTE)

    def test_deserialize_log(self):
        raw_log = {
            "location": {
                "source": "File.py",
                "line": 1,
                "commitId": None,
                "fileChecksum": None
            },
            "condition": "1==1",
            "expiresAt": None,
            "hitLimit": 2,
            "id": None,
            "type": "LOG",
            "applyImmediately": True,
            "applied": True,
            "pending": True,
            "throttle": {
                "limit": 2,
                "step": "MINUTE"
            },
            "logFormat": "Hello {}",
            "logArguments": ["world"]
        }
        log = LiveLog.from_json(json.dumps(raw_log))
        self.assertEqual(log.location.source, "File.py")
        self.assertEqual(log.location.line, 1)
        self.assertEqual(log.condition, "1==1")
        self.assertEqual(log.expires_at, None)
        self.assertEqual(log.hit_limit, 2)
        self.assertEqual(log.type, "LOG")
        self.assertEqual(log.apply_immediately, True)
        self.assertEqual(log.applied, True)
        self.assertEqual(log.pending, True)
        self.assertEqual(log.throttle.limit, 2)
        self.assertEqual(log.throttle.step, ThrottleStep.MINUTE)
        self.assertEqual(log.log_format, "Hello {}")
        self.assertEqual(log.log_arguments, ["world"])

    def test_serialize_breakpoint(self):
        bp = LiveBreakpoint(LiveSourceLocation("File.py", 1))
        bp.condition = "1==1"
        bp.expires_at = round(time.time() * 1000)
        bp.hit_limit = 5
        bp.throttle = HitThrottle(2, ThrottleStep.MINUTE)

        bp_json = bp.to_json()
        raw_bp = {
            "location": {
                "source": "File.py",
                "line": 1,
                "service": None,
                "serviceInstance": None,
                "commitId": None,
                "fileChecksum": None
            },
            "condition": bp.condition,
            "expiresAt": bp.expires_at,
            "hitLimit": bp.hit_limit,
            "id": None,
            "type": "BREAKPOINT",
            "applyImmediately": False,
            "applied": False,
            "pending": False,
            "throttle": {
                "limit": bp.throttle.limit,
                "step": bp.throttle.step
            }
        }
        self.assertEqual(json.dumps(raw_bp), bp_json)

    def test_serialize_log(self):
        log = LiveLog(LiveSourceLocation("File.py", 1))
        log.log_format = "Hello {}"
        log.log_arguments = ["world"]
        log.condition = "1==1"
        log.expires_at = round(time.time() * 1000)
        log.hit_limit = 5
        log.throttle = HitThrottle(2, ThrottleStep.MINUTE)

        log_json = log.to_json()
        raw_log = {
            "location": {
                "source": "File.py",
                "line": 1,
                "service": None,
                "serviceInstance": None,
                "commitId": None,
                "fileChecksum": None
            },
            "condition": log.condition,
            "expiresAt": log.expires_at,
            "hitLimit": log.hit_limit,
            "id": None,
            "type": "LOG",
            "applyImmediately": False,
            "applied": False,
            "pending": False,
            "throttle": {
                "limit": log.throttle.limit,
                "step": log.throttle.step
            },
            "logFormat": "Hello {}",
            "logArguments": ["world"]
        }
        self.assertEqual(json.dumps(raw_log), log_json)
