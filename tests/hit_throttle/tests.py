import threading
import unittest

import time

from sourceplusplus.models.instrument.common.throttle.HitThrottle import HitThrottle
from sourceplusplus.models.instrument.common.throttle.ThrottleStep import ThrottleStep


class TestSum(unittest.TestCase):
    hit_throttle: HitThrottle = None

    def test_one_per_second(self):
        def done():
            self.assertAlmostEqual(TestSum.hit_throttle._total_hit_count, 5, delta=1)
            self.assertAlmostEqual(TestSum.hit_throttle._total_limited_count, 45, delta=1)

        TestSum.hit_throttle = HitThrottle(1, ThrottleStep.SECOND)
        PeriodicSleeper(TestSum.hit_throttle.is_rate_limited, 0.1, 5000, done).join()

    def test_two_per_second(self):
        def done():
            self.assertAlmostEqual(TestSum.hit_throttle._total_hit_count, 10, delta=1)
            self.assertAlmostEqual(TestSum.hit_throttle._total_limited_count, 12, delta=1)

        TestSum.hit_throttle = HitThrottle(2, ThrottleStep.SECOND)
        PeriodicSleeper(TestSum.hit_throttle.is_rate_limited, 0.225, 5000, done).join()

    def test_four_per_second(self):
        def done():
            self.assertEqual(TestSum.hit_throttle._total_hit_count, 20)
            self.assertEqual(TestSum.hit_throttle._total_limited_count, 3)

        TestSum.hit_throttle = HitThrottle(4, ThrottleStep.SECOND)
        PeriodicSleeper(TestSum.hit_throttle.is_rate_limited, 0.225, 5000, done).join()


class PeriodicSleeper(threading.Thread):
    def __init__(self, task_function, period, stop, done):
        super().__init__()
        self.task_function = task_function
        self.period = period
        self.done = done
        self.i = 0
        self.t0 = time.time()
        self.stop = int(round(time.time() * 1000)) + stop
        self.start()

    def sleep(self):
        self.i += 1
        delta = self.t0 + self.period * self.i - time.time()
        if delta > 0 and round(time.time() * 1000) < self.stop:
            time.sleep(delta)

    def run(self):
        while round(time.time() * 1000) < self.stop:
            self.task_function()
            self.sleep()
        self.done()


if __name__ == '__main__':
    unittest.main()
