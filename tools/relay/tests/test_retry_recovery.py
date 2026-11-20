"""Exercise interrupted completion imports against the durable Relay store."""
import sqlite3
import tempfile
import unittest
from pathlib import Path

from relay.engine import run
from relay.store import Store
from relay.worker import atomic_json, input_digest


class ControllerInterrupted(BaseException):
    """Simulate the controller stopping at the completion boundary."""


class InterruptedAfterFinish(Store):
    def finish(self, *args, **kwargs):
        super().finish(*args, **kwargs)
        raise ControllerInterrupted


class CancelBeforeFinish(Store):
    def finish(self, job_id, *args, **kwargs):
        Store(self.db_path).request_cancel(job_id)
        return super().finish(job_id, *args, **kwargs)


class RetryRecoveryTests(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory(prefix="relay-retry-recovery-")
        self.addCleanup(scratch.cleanup)
        self.root = Path(scratch.name)
        self.db = self.root / "jobs.sqlite"
        self.state = self.root / "state"
        self.store = Store(self.db)
        for job_id, deps in (("source", []), ("dependent", ["source"])):
            self.store.submit({
                "id": job_id, "kind": "test", "deps": deps,
                "command": ["fixture-never-spawned"], "cwd": str(self.root),
                "inputs": {}, "resources": {"cpu": 1}, "timeout_s": 3,
                "receipt_required": False, "max_attempts": 2, "retry_exit_codes": [75],
            })
        self.first = self.store.claim("source", "old-controller", 30)
        self.publish_result(self.first, 75)

    def publish_result(self, row, returncode):
        attempt_dir = self.root / f"attempt-{row['attempt']}"
        attempt_dir.mkdir()
        request = {"schema": 1, "job_id": row["id"], "token": row["token"],
                   "attempt": row["attempt"], "spec": row["spec"], "dependencies": {}}
        request["input_digest"] = input_digest(request)
        atomic_json(attempt_dir / "input.json", request)
        atomic_json(attempt_dir / "worker-result.json", {
            "schema": 1, "job_id": row["id"], "token": row["token"], "attempt": row["attempt"],
            "input_digest": request["input_digest"], "returncode": returncode,
            "timed_out": False, "cancelled": False, "started_at": 100, "finished_at": 101,
        })
        self.assertTrue(self.store.set_runtime(row["id"], row["token"], row["owner"], 0, attempt_dir))

    def import_without_dispatch(self, store):
        # The production controller imports durable results before this callback.
        # Stop here to test restart without running an adapter or inspecting PIDs.
        def stop_before_dispatch(_store):
            raise ControllerInterrupted

        with self.assertRaises(ControllerInterrupted):
            run(store, self.state, {"cpu": 1}, batch_callback=stop_before_dispatch)

    def claim_recovered_retry(self):
        restarted = Store(self.db)
        self.import_without_dispatch(restarted)
        row = restarted.get("source")
        self.assertEqual((row["state"], row["attempt"], row["token"]), ("queued", 1, self.first["token"]))
        events = [event["kind"] for event in restarted.events() if event["job_id"] == "source"]
        self.assertEqual(events[-2:], ["finished", "retry_requested"])
        self.assertEqual(events.count("retry_requested"), 1)
        self.assertIsNone(restarted.claim("dependent", "new-controller", 30))
        second = restarted.claim("source", "new-controller", 30)
        self.assertEqual((second["attempt"], second["token"]), (2, self.first["token"] + 1))
        self.assertIsNone(restarted.claim("source", "other-controller", 30))
        self.assertFalse(restarted.finish("source", self.first["token"], self.first["owner"], "passed", {}))
        return restarted, second

    def test_restart_after_completion_commit_keeps_exit_75_retry(self):
        with self.assertRaises(ControllerInterrupted):
            run(InterruptedAfterFinish(self.db), self.state, {"cpu": 1})

        restarted, second = self.claim_recovered_retry()
        self.publish_result(second, 0)
        self.import_without_dispatch(restarted)
        self.assertEqual(restarted.get("source")["state"], "passed")
        self.assertIsNotNone(restarted.claim("dependent", "new-controller", 30))

    def test_restart_after_retry_transaction_abort_reimports_same_attempt(self):
        # Reject the retry audit insert to interrupt after the state update but before commit.
        with sqlite3.connect(self.db) as connection:
            connection.execute("""
                CREATE TRIGGER interrupt_retry BEFORE INSERT ON events
                WHEN NEW.kind = 'retry_requested'
                BEGIN SELECT RAISE(ABORT, 'interrupted retry transaction'); END
            """)
        try:
            with self.assertRaisesRegex(sqlite3.IntegrityError, "interrupted retry transaction"):
                run(self.store, self.state, {"cpu": 1})
        finally:
            with sqlite3.connect(self.db) as connection:
                connection.execute("DROP TRIGGER interrupt_retry")

        restarted, second = self.claim_recovered_retry()
        self.publish_result(second, 75)
        self.import_without_dispatch(restarted)
        self.assertEqual(restarted.get("source")["state"], "failed")
        self.assertEqual(restarted.get("dependent")["state"], "blocked")
        self.assertIsNone(restarted.claim("source", "other-controller", 30))

    def test_cancel_requested_during_result_import_prevents_retry(self):
        self.import_without_dispatch(CancelBeforeFinish(self.db))
        row = self.store.get("source")
        self.assertEqual((row["state"], row["attempt"], row["cancel_requested"]), ("failed", 1, True))
        self.assertIsNone(self.store.claim("source", "other-controller", 30))
