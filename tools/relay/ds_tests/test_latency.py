"""Handoff timing uses every durable attempt reservation."""
import unittest

from dsrelay.latency import samples


class LatencyTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            {"id": "prep", "spec": {"resources": {}, "deps": []}, "state": "passed",
             "attempt": 1, "token": 1, "started_at": 1, "finished_at": 10,
             "result": {"started_at": 2, "finished_at": 10}},
            {"id": "console", "spec": {"resources": {"local_test": 1}, "deps": ["prep"]},
             "state": "passed", "attempt": 1, "token": 1, "started_at": 33, "finished_at": 45,
             "result": {"started_at": 40, "finished_at": 44}},
            {"id": "stream", "spec": {"resources": {"local_test": 1}, "deps": []},
             "state": "passed", "attempt": 2, "token": 2, "started_at": 50, "finished_at": 60,
             "result": {"started_at": 51, "finished_at": 59}},
        ]
        self.events = []
        for job, attempt, claim, finish in (
                ("prep", 1, 1, 10), ("stream", 1, 12, 30),
                ("console", 1, 33, 45), ("stream", 2, 50, 60)):
            self.events.extend([
                {"kind": "claimed", "job_id": job, "created_at": claim,
                 "data": {"attempt": attempt, "token": attempt}},
                {"kind": "finished", "job_id": job, "created_at": finish,
                 "data": {"token": attempt}},
            ])

    def test_first_attempt_counts_after_retry(self):
        result, = samples(self.rows, {"local_test": 1}, 3, attempt_events=self.events)
        self.assertEqual(result["dependency_finish_to_start_s"], 30)
        self.assertEqual(result["reservation_wait_s"], 18)
        self.assertEqual(result["capacity_available_to_start_s"], 12)

    def test_missing_retry_history_keeps_only_raw_measurement(self):
        result, = samples(self.rows, {"local_test": 1}, 3, attempt_events=self.events[:2] + self.events[4:])
        self.assertEqual(result["dependency_finish_to_start_s"], 30)
        self.assertIsNone(result["reservation_wait_s"])
        self.assertIsNone(result["capacity_available_to_start_s"])
