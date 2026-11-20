"""Behavioral tests for durable claims, acceptance gates, and recovery."""
import concurrent.futures
import copy
import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path

from relay.store import Store


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.db = self.root / "relay.sqlite3"
        self.store = Store(self.db)

    def tearDown(self):
        self.temp.cleanup()

    def spec(self, name="job", **changes):
        value = {"id": name, "kind": "test", "deps": [], "command": ["python3", "-c", "print('fixture')"],
                 "cwd": str(self.root), "inputs": {}, "resources": {"cpu": 1}, "timeout_s": 30}
        value.update(changes)
        return value

    def complete(self, name, state="passed", owner="controller"):
        claim = self.store.claim(name, owner, 30)
        self.assertIsNotNone(claim)
        self.assertTrue(self.store.finish(name, claim["token"], owner, state, {"fixture": True}))
        return claim

    def test_idempotent_submission_preserves_immutable_copy(self):
        spec = self.spec()
        original = copy.deepcopy(spec)
        self.assertTrue(self.store.submit(spec))
        self.assertFalse(self.store.submit(original))
        spec["inputs"]["late_mutation"] = True
        self.assertEqual(self.store.get("job")["spec"]["inputs"], {})
        with self.assertRaises(ValueError):
            self.store.submit(spec)
        self.assertEqual(len(self.store.jobs()), 1)

    def test_concurrent_controllers_claim_once(self):
        self.store.submit(self.spec())
        barrier = threading.Barrier(8)

        def contender(index):
            local = Store(self.db)
            barrier.wait(timeout=10)
            return local.claim("job", f"controller-{index}", 30)

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(contender, range(8)))
        self.assertEqual(sum(result is not None for result in results), 1)
        row = self.store.get("job")
        self.assertEqual((row["attempt"], row["token"], row["state"]), (1, 1, "running"))

    def test_fencing_rejects_old_owner_and_attempt(self):
        self.store.submit(self.spec(max_attempts=2))
        first = self.store.claim("job", "old", 30)
        self.assertFalse(self.store.heartbeat("job", first["token"], "wrong", 30))
        self.assertFalse(self.store.finish("job", first["token"] + 1, "old", "passed", {}))
        self.assertFalse(self.store.set_runtime("job", first["token"], "wrong", 1234, str(self.root)))
        self.assertTrue(self.store.finish("job", first["token"], "old", "failed", {"returncode": 7}))
        self.store.retry("job", "explicit retry after diagnosis")
        second = self.store.claim("job", "new", 30)
        self.assertGreater(second["token"], first["token"])
        self.assertFalse(self.store.finish("job", first["token"], "old", "passed", {}))
        self.assertFalse(self.store.mark_uncertain("job", first["token"], "stale observation"))
        self.assertTrue(self.store.finish("job", second["token"], "new", "passed", {"checked": True}))
        self.assertFalse(self.store.finish("job", second["token"], "new", "failed", {}))

    def test_lease_expiry_does_not_authorize_duplicate(self):
        self.store.submit(self.spec(max_attempts=3))
        claim = self.store.claim("job", "first", 30)
        with sqlite3.connect(self.db) as conn:
            conn.execute("UPDATE jobs SET lease_until=0 WHERE id='job'")
        restarted = Store(self.db)
        self.assertIsNone(restarted.claim("job", "replacement", 30))
        self.assertTrue(restarted.mark_uncertain("job", claim["token"], "supervisor not yet verified"))
        with self.assertRaises(ValueError):
            restarted.retry("job", "unsafe speculative replacement")
        self.assertIsNone(restarted.claim("job", "replacement", 30))
        self.assertTrue(restarted.finish("job", claim["token"], "first", "passed", {"late_verified_receipt": True}))

    def test_approval_and_dependencies_both_gate_execution(self):
        self.store.submit(self.spec("review", deps=["tests"], approval_required=True))
        self.assertIsNone(self.store.get("review")["ready_at"])
        self.assertIsNone(self.store.claim("review", "owner", 30))
        self.store.approve("review", "Eugene", "approved this immutable job")
        self.assertIsNone(self.store.claim("review", "owner", 30))
        self.store.submit(self.spec("tests"))
        self.complete("tests")
        review = self.store.get("review")
        self.assertGreaterEqual(review["ready_at"], self.store.get("tests")["finished_at"])
        self.assertIsNotNone(self.store.claim("review", "reviewer", 30))
        approvals = [event for event in self.store.events() if event["kind"] == "approved"]
        self.assertEqual(approvals[0]["data"]["actor"], "Eugene")

    def test_passed_dependencies_do_not_approve_job(self):
        self.store.submit(self.spec("tests"))
        self.complete("tests")
        self.store.submit(self.spec("review", deps=["tests"], approval_required=True))
        self.assertIsNotNone(self.store.get("review")["ready_at"])
        self.assertIsNone(self.store.claim("review", "owner", 30))
        self.store.approve("review", "Eugene", "")
        self.assertIsNotNone(self.store.claim("review", "owner", 30))

    def test_restart_retains_runtime_and_evidence(self):
        self.store.submit(self.spec())
        claim = self.store.claim("job", "owner", 30)
        self.assertTrue(self.store.set_runtime("job", claim["token"], "owner", 0, str(self.root / "attempt-1")))
        self.assertTrue(self.store.set_runtime("job", claim["token"], "owner", 9876, str(self.root / "attempt-1")))
        restarted = Store(self.db)
        self.assertEqual(restarted.get("job")["pid"], 9876)
        receipt = {"outcome": "pass", "evidence": ["fixture.json"]}
        self.assertTrue(restarted.finish("job", claim["token"], "owner", "passed", receipt))
        self.assertEqual(Store(self.db).get("job")["result"], receipt)
        self.assertEqual(Store(self.db).events()[-1]["kind"], "finished")

    def test_failed_branch_blocks_descendants_not_independent_jobs(self):
        self.store.submit(self.spec("first", max_attempts=2))
        self.store.submit(self.spec("second", deps=["first"]))
        self.store.submit(self.spec("third", deps=["second"]))
        self.store.submit(self.spec("independent"))
        self.complete("first", "failed")
        self.assertEqual(self.store.propagate_blocked(), 2)
        self.assertEqual(self.store.get("third")["state"], "blocked")
        self.assertIsNotNone(self.store.claim("independent", "other", 30))
        self.store.retry("first", "fixed root cause")
        self.store.propagate_blocked()
        self.assertEqual(self.store.get("second")["state"], "blocked")
        self.complete("first")
        self.store.propagate_blocked()
        self.assertEqual(self.store.get("second")["state"], "queued")
        self.assertEqual(self.store.get("third")["state"], "blocked")
        self.complete("second")
        self.store.propagate_blocked()
        self.assertIsNotNone(self.store.claim("third", "owner", 30))

    def test_approval_is_preserved_when_dependency_recovers(self):
        self.store.submit(self.spec("first", max_attempts=2))
        self.store.submit(self.spec("approve-later", deps=["first"], approval_required=True))
        self.complete("first", "failed")
        self.store.propagate_blocked()
        self.assertEqual(self.store.get("approve-later")["state"], "blocked")
        self.store.retry("first", "retry")
        self.complete("first")
        self.store.propagate_blocked()
        self.assertEqual(self.store.get("approve-later")["state"], "approval")
        self.assertIsNone(self.store.claim("approve-later", "owner", 30))

    def test_adapter_blockage_is_not_automatically_cleared(self):
        self.store.submit(self.spec("first"))
        self.store.submit(self.spec("second", deps=["first"]))
        self.complete("first", "blocked")
        self.store.propagate_blocked()
        self.assertEqual(self.store.get("first")["state"], "blocked")
        self.assertEqual(self.store.get("second")["state"], "blocked")

    def test_explicit_retry_is_bounded_and_clears_runtime(self):
        self.store.submit(self.spec(max_attempts=2))
        first = self.store.claim("job", "one", 30)
        self.store.set_runtime("job", first["token"], "one", 1234, str(self.root))
        self.store.finish("job", first["token"], "one", "failed", {"returncode": 7}, "failed check")
        self.store.retry("job", "explicit decision")
        row = self.store.get("job")
        self.assertEqual(row["attempt"], 1)
        for field in ("pid", "owner", "lease_until", "attempt_dir", "started_at", "finished_at", "result"):
            self.assertIsNone(row[field])
        self.complete("job", "failed")
        with self.assertRaisesRegex(ValueError, "max_attempts"):
            self.store.retry("job", "too many attempts")

    def test_cancel_pending_never_runs(self):
        self.store.submit(self.spec("first"))
        self.store.submit(self.spec("second", deps=["first"]))
        self.store.request_cancel("first")
        self.assertEqual(self.store.get("first")["state"], "cancelled")
        self.assertIsNone(self.store.claim("first", "owner", 30))
        self.store.propagate_blocked()
        self.assertEqual(self.store.get("second")["state"], "blocked")

    def test_cancel_running_prevents_late_success_dispatch(self):
        self.store.submit(self.spec("first"))
        self.store.submit(self.spec("second", deps=["first"]))
        claim = self.store.claim("first", "owner", 30)
        self.store.request_cancel("first")
        self.assertEqual(self.store.get("first")["state"], "running")
        self.assertTrue(self.store.get("first")["cancel_requested"])
        self.store.finish("first", claim["token"], "owner", "passed", {"completed_before_signal": True})
        self.assertEqual(self.store.get("first")["state"], "cancelled")
        self.assertIsNone(self.store.claim("second", "owner", 30))

    def test_cancel_uncertain_does_not_claim_process_stopped(self):
        self.store.submit(self.spec())
        claim = self.store.claim("job", "owner", 30)
        self.store.mark_uncertain("job", claim["token"], "no heartbeat")
        self.store.request_cancel("job")
        self.assertEqual(self.store.get("job")["state"], "uncertain")
        self.assertTrue(self.store.get("job")["cancel_requested"])
        self.assertIsNone(self.store.claim("job", "other", 30))

    def test_uncertain_dependencies_wait_without_terminal_blockage(self):
        self.store.submit(self.spec("first"))
        self.store.submit(self.spec("second", deps=["first"]))
        claim = self.store.claim("first", "owner", 30)
        self.store.mark_uncertain("first", claim["token"], "restart check")
        self.assertEqual(self.store.propagate_blocked(), 0)
        self.assertEqual(self.store.get("second")["state"], "queued")
        self.assertIsNone(self.store.claim("second", "other", 30))
        self.store.finish("first", claim["token"], "owner", "passed", {})
        self.assertIsNotNone(self.store.claim("second", "other", 30))

    def test_validation_and_event_data(self):
        for changes in ({"resources": {"cpu": 0}}, {"max_attempts": 0}, {"timeout_s": float("inf")}, {"deps": ["job"]}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.store.submit(self.spec(**changes))
        self.store.event("note", data={"text": "spaces; $(not executable)"})
        self.assertEqual(self.store.events(limit=1)[0]["data"]["text"], "spaces; $(not executable)")
        self.assertEqual(self.store.events(limit=0), [])
        with self.assertRaises(KeyError):
            self.store.get("missing")


if __name__ == "__main__":
    unittest.main()
