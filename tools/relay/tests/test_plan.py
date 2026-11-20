"""Planner tests use simulated stage receipts, never production acceptance."""
import copy
import tempfile
import unittest
from pathlib import Path

from relay.cli import active_plan_complete, install_plan, make_demo_plan, metrics
from relay.plan import batch_callback, compile_plan, module_status, submit_plan
from relay.store import Store


class PlanTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = Store(Path(self.temp.name) / "queue.sqlite3")
        self.plan = make_demo_plan()

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def job_identity_map(plan):
        jobs, _ = compile_plan(plan)
        return {(job["kind"], job.get("module", job["inputs"].get("piece_id"))): job["id"] for job in jobs}

    def finish_job(self, job_id, state="passed", result=None):
        if self.store.get(job_id)["state"] == state:
            return
        claim = self.store.claim(job_id, "planner-test-fixture", 30)
        self.assertIsNotNone(claim, job_id)
        self.assertTrue(self.store.finish(job_id, claim["token"], "planner-test-fixture", state,
                                          {"planner_test_simulated_stage": True} if result is None else result))

    def finish_module(self, module_id):
        module = next(module for module in self.plan["modules"] if module["id"] == module_id)
        jobs, mapping = compile_plan(self.plan)
        for job in jobs:
            if job["kind"] == "piece" and job["inputs"]["piece_id"] in module["pieces"]:
                self.finish_job(job["id"])
        for stage in ("assemble", "test", "review"):
            self.finish_job(mapping[module_id][stage])

    def batches(self):
        return [row for row in self.store.jobs() if row["spec"]["kind"] == "batch"]

    def test_piece_identity_change_invalidates_only_affected_module(self):
        baseline = self.job_identity_map(self.plan)
        changed = copy.deepcopy(self.plan)
        changed["pieces"][0]["identity"]["revision"] = "new-source-content"
        updated = self.job_identity_map(changed)
        invalidated = {key for key in baseline if baseline[key] != updated[key]}
        self.assertEqual(invalidated, {("piece", "math-add"), ("assemble", "math"), ("test", "math"), ("review", "math")})
        submit_plan(self.store, self.plan)
        for job in self.store.jobs():
            self.finish_job(job["id"])
        submit_plan(self.store, changed)
        self.assertEqual(len(self.store.jobs()), 14)
        for key in baseline.keys() - invalidated:
            self.assertEqual(self.store.get(updated[key])["state"], "passed")
        for key in invalidated:
            self.assertEqual(self.store.get(updated[key])["state"], "queued")

    def test_policy_and_environment_change_invalidate_all_stage_identities(self):
        baseline = self.job_identity_map(self.plan)
        for field in ("policy_version", "environment_id"):
            with self.subTest(field=field):
                changed = copy.deepcopy(self.plan)
                changed[field] = "changed-policy-or-environment"
                updated = self.job_identity_map(changed)
                self.assertEqual(set(updated), set(baseline))
                self.assertTrue(all(baseline[key] != updated[key] for key in baseline))

    def test_review_adapter_change_preserves_implementation_and_test_identity(self):
        baseline = self.job_identity_map(self.plan)
        changed = copy.deepcopy(self.plan)
        changed["adapters"]["review"]["version"] = "reviewer-tool-version-2"
        updated = self.job_identity_map(changed)
        self.assertEqual({key for key in baseline if baseline[key] != updated[key]}, {("review", "math"), ("review", "display")})

    def test_module_dependency_change_invalidates_transitive_dependents(self):
        self.plan["modules"][1]["depends_on"] = ["math"]
        baseline = self.job_identity_map(self.plan)
        changed = copy.deepcopy(self.plan)
        changed["pieces"][0]["identity"]["revision"] = "new-content"
        updated = self.job_identity_map(changed)
        for module in ("math", "display"):
            for stage in ("assemble", "test", "review"):
                self.assertNotEqual(baseline[(stage, module)], updated[(stage, module)])
        self.assertEqual(baseline[("piece", "display-render")], updated[("piece", "display-render")])

    def test_passing_pieces_alone_are_not_batchable(self):
        submit_plan(self.store, self.plan)
        for row in self.store.jobs():
            if row["spec"]["kind"] == "piece":
                self.finish_job(row["id"])
        self.assertEqual(batch_callback(self.plan)(self.store), 0)
        self.assertEqual(self.batches(), [])
        self.assertTrue(all(status["state"] == "assemble:queued" for status in module_status(self.store, self.plan)))

    def test_tests_without_independent_review_are_not_batchable(self):
        mapping = submit_plan(self.store, self.plan)
        for row in self.store.jobs():
            if row["spec"]["kind"] == "piece":
                self.finish_job(row["id"])
        for stages in mapping.values():
            self.finish_job(stages["assemble"])
            self.finish_job(stages["test"])
        self.assertEqual(batch_callback(self.plan)(self.store), 0)
        self.assertEqual(self.batches(), [])

    def test_two_reviewed_compatible_modules_coalesce_into_one_batch(self):
        submit_plan(self.store, self.plan)
        self.finish_module("math")
        self.finish_module("display")
        self.assertEqual(batch_callback(self.plan)(self.store), 1)
        batches = self.batches()
        self.assertEqual(len(batches), 1)
        members = batches[0]["spec"]["inputs"]["members"]
        self.assertEqual([member["module"] for member in members], ["display", "math"])
        self.assertEqual(batches[0]["spec"]["deps"], [member["review_job"] for member in members])
        self.assertEqual(batches[0]["spec"]["resources"], {"integration": 1})

    def test_single_ready_module_is_dispatched_without_waiting_for_other(self):
        submit_plan(self.store, self.plan)
        callback = batch_callback(self.plan)
        self.finish_module("math")
        self.assertEqual(callback(self.store), 1)
        first = self.batches()[0]
        self.assertEqual([member["module"] for member in first["spec"]["inputs"]["members"]], ["math"])
        self.assertEqual(first["state"], "queued")
        self.finish_module("display")
        self.assertEqual(callback(self.store), 0)
        self.finish_job(first["id"])
        self.assertEqual(callback(self.store), 1)
        self.assertEqual(len(self.batches()), 2)
        self.assertTrue(all(len(row["spec"]["inputs"]["members"]) == 1 for row in self.batches()))

    def test_incompatible_modules_are_separate_batches(self):
        self.plan["modules"][1]["compatibility_key"] = "other-environment"
        submit_plan(self.store, self.plan)
        self.finish_module("math")
        self.finish_module("display")
        callback = batch_callback(self.plan)
        self.assertEqual(callback(self.store), 1)
        self.assertEqual(len(self.batches()), 1)
        self.finish_job(self.batches()[0]["id"])
        self.assertEqual(callback(self.store), 1)
        self.assertEqual({row["spec"]["inputs"]["compatibility_key"] for row in self.batches()}, {"fixture-python-v1", "other-environment"})

    def test_batch_maximum_is_respected(self):
        self.plan["batch"]["max_size"] = 1
        submit_plan(self.store, self.plan)
        self.finish_module("math")
        self.finish_module("display")
        callback = batch_callback(self.plan)
        self.assertEqual(callback(self.store), 1)
        self.finish_job(self.batches()[0]["id"])
        self.assertEqual(callback(self.store), 1)
        self.assertTrue(all(len(row["spec"]["inputs"]["members"]) == 1 for row in self.batches()))

    def test_modules_ready_during_batch_accumulate_for_next_batch(self):
        # Planner-only third module. No fixture adapter is executed in this test.
        extra_pieces = [copy.deepcopy(piece) for piece in self.plan["pieces"] if piece["inputs"]["module"] == "display"]
        for piece in extra_pieces:
            piece["id"] = piece["id"].replace("display-", "extra-")
            piece["inputs"]["module"] = "extra"
            piece["identity"]["module"] = "extra"
        extra_module = copy.deepcopy(self.plan["modules"][1])
        extra_module["id"] = "extra"
        extra_module["pieces"] = [piece["id"] for piece in extra_pieces]
        self.plan["pieces"].extend(extra_pieces)
        self.plan["modules"].append(extra_module)
        submit_plan(self.store, self.plan)
        callback = batch_callback(self.plan)
        self.finish_module("math")
        self.assertEqual(callback(self.store), 1)
        first = self.batches()[0]
        claimed = self.store.claim(first["id"], "integration-fixture", 30)
        self.assertIsNotNone(claimed)
        self.finish_module("display")
        self.assertEqual(callback(self.store), 0)
        self.finish_module("extra")
        self.assertEqual(callback(self.store), 0)
        self.assertEqual(len(self.batches()), 1)
        status = {row["module"]: row["state"] for row in module_status(self.store, self.plan)}
        self.assertEqual(status["display"], "ready_for_batch")
        self.assertEqual(status["extra"], "ready_for_batch")
        self.store.finish(first["id"], claimed["token"], "integration-fixture", "passed", {"planner_fixture": True})
        self.assertEqual(callback(self.store), 1)
        next_batch = next(row for row in self.batches() if row["id"] != first["id"])
        self.assertEqual([member["module"] for member in next_batch["spec"]["inputs"]["members"]], ["display", "extra"])

    def test_repeated_callback_preserves_failed_batch_without_automatic_retry(self):
        submit_plan(self.store, self.plan)
        self.finish_module("math")
        self.finish_module("display")
        callback = batch_callback(self.plan)
        self.assertEqual(callback(self.store), 1)
        self.assertEqual(callback(self.store), 0)
        batch = self.batches()[0]
        self.finish_job(batch["id"], "failed")
        self.assertEqual(callback(self.store), 0)
        self.assertEqual(len(self.batches()), 1)
        self.assertEqual(self.store.get(batch["id"])["attempt"], 1)
        self.assertEqual({row["state"] for row in module_status(self.store, self.plan)}, {"batch:failed"})

    def test_successful_fixture_batch_is_not_reported_as_production_release(self):
        submit_plan(self.store, self.plan)
        self.finish_module("math")
        self.finish_module("display")
        callback = batch_callback(self.plan)
        callback(self.store)
        self.finish_job(self.batches()[0]["id"])
        self.assertEqual(callback(self.store), 0)
        self.assertEqual({row["state"] for row in module_status(self.store, self.plan)}, {"batch_tested"})

    def test_changed_batch_adapter_invalidates_only_integration_acceptance(self):
        submit_plan(self.store, self.plan)
        self.finish_module("math")
        self.finish_module("display")
        batch_callback(self.plan)(self.store)
        previous = self.batches()[0]
        self.finish_job(previous["id"])
        self.assertTrue(active_plan_complete(self.store, self.plan))
        changed = copy.deepcopy(self.plan)
        changed["adapters"]["batch"]["version"] = "changed-integration-checks"
        submit_plan(self.store, changed)
        self.assertEqual(len(self.store.jobs()), 11)
        self.assertEqual({row["state"] for row in module_status(self.store, changed)}, {"ready_for_batch"})
        self.assertFalse(active_plan_complete(self.store, changed))
        self.assertEqual(batch_callback(changed)(self.store), 1)
        current = next(row for row in self.batches() if row["id"] != previous["id"])
        self.assertEqual({row["state"] for row in module_status(self.store, changed)}, {"batch:queued"})
        self.finish_job(current["id"])
        self.assertTrue(active_plan_complete(self.store, changed))
        self.assertEqual(batch_callback(changed)(self.store), 0)
        self.assertEqual(self.store.get(previous["id"])["state"], "passed")

    def test_changed_batch_adapter_can_replace_failed_integration_spec(self):
        submit_plan(self.store, self.plan)
        self.finish_module("math")
        self.finish_module("display")
        batch_callback(self.plan)(self.store)
        failed = self.batches()[0]
        self.finish_job(failed["id"], "failed")
        self.assertEqual(batch_callback(self.plan)(self.store), 0)
        changed = copy.deepcopy(self.plan)
        changed["adapters"]["batch"]["version"] = "fixed-integration-adapter"
        submit_plan(self.store, changed)
        self.assertEqual(batch_callback(changed)(self.store), 1)
        replacement = next(row for row in self.batches() if row["id"] != failed["id"])
        self.finish_job(replacement["id"])
        self.assertTrue(active_plan_complete(self.store, changed))
        self.assertEqual(self.store.get(failed["id"])["state"], "failed")
        self.assertEqual(self.store.get(failed["id"])["attempt"], 1)

    def test_changed_batch_inputs_or_mode_require_new_integration_evidence(self):
        submit_plan(self.store, self.plan)
        self.finish_module("math")
        self.finish_module("display")
        batch_callback(self.plan)(self.store)
        self.finish_job(self.batches()[0]["id"])
        for field, value in (("inputs", {"new_check": True}), ("integration_mode", "merge")):
            with self.subTest(field=field):
                changed = copy.deepcopy(self.plan)
                changed["batch"][field] = value
                self.assertEqual({row["state"] for row in module_status(self.store, changed)}, {"ready_for_batch"})

    def test_invalid_adapter_is_rejected_without_partial_submission(self):
        variants = (("command", [""]), ("priority", "high"), ("retry_exit_codes", "1"),
                    ("approval_required", "yes"), ("receipt_required", 1))
        for field, value in variants:
            with self.subTest(field=field):
                invalid = copy.deepcopy(self.plan)
                invalid["adapters"]["review"][field] = value
                with self.assertRaises(ValueError):
                    compile_plan(invalid)
                with self.assertRaises(ValueError):
                    submit_plan(self.store, invalid)
                self.assertEqual(self.store.jobs(), [])

    def test_invalid_dynamic_batch_adapter_is_rejected_before_submission(self):
        invalid = copy.deepcopy(self.plan)
        invalid["adapters"]["batch"]["priority"] = "high"
        with self.assertRaises(ValueError):
            submit_plan(self.store, invalid)
        self.assertEqual(self.store.jobs(), [])

    def test_invalid_install_creates_no_state_directory(self):
        invalid = copy.deepcopy(self.plan)
        invalid["adapters"]["review"]["command"] = [""]
        state = Path(self.temp.name) / "invalid-install"
        with self.assertRaises(ValueError):
            install_plan(invalid, state)
        self.assertFalse(state.exists())

    def test_piece_actor_is_required_to_check_review_independence(self):
        invalid = copy.deepcopy(self.plan)
        del invalid["adapters"]["piece"]["actor"]
        with self.assertRaisesRegex(ValueError, "author actor"):
            compile_plan(invalid)

    def test_full_handoff_metric_uses_worker_timestamps_and_latest_dependency(self):
        _, mapping = compile_plan(self.plan)
        submit_plan(self.store, self.plan)
        pieces = [row for row in self.store.jobs() if row["spec"]["kind"] == "piece" and row["spec"]["inputs"]["piece_id"].startswith("math-")]
        self.finish_job(pieces[0]["id"], result={"started_at": 2, "finished_at": 10})
        self.finish_job(pieces[1]["id"], result={"started_at": 3, "finished_at": 12})
        self.finish_job(mapping["math"]["assemble"], result={"started_at": 12.25, "finished_at": 13})
        self.finish_job(mapping["math"]["test"], result={"started_at": 13.5, "finished_at": 14})
        self.finish_job(mapping["math"]["review"], result={"started_at": 14.75, "finished_at": 15})
        handoff = metrics(self.store)["dependency_finish_to_worker_start_s"]
        self.assertEqual(handoff, {"samples": 3, "p50": 0.5, "p95": 0.75, "max": 0.75})

    def test_full_handoff_metric_skips_missing_dependency_timestamps(self):
        _, mapping = compile_plan(self.plan)
        submit_plan(self.store, self.plan)
        for row in self.store.jobs():
            if row["spec"]["kind"] == "piece":
                self.finish_job(row["id"])
        self.finish_job(mapping["math"]["assemble"], result={"started_at": 12.25, "finished_at": 13})
        self.assertEqual(metrics(self.store)["dependency_finish_to_worker_start_s"], {"samples": 0, "p50": None, "p95": None, "max": None})

    def test_independence_checks_reject_self_review(self):
        for role in ("assemble", "piece"):
            with self.subTest(role=role):
                changed = copy.deepcopy(self.plan)
                changed["adapters"][role]["actor"] = changed["adapters"]["review"]["actor"]
                with self.assertRaisesRegex(ValueError, "distinct actors|piece author"):
                    compile_plan(changed)

    def test_resource_errors_rejected_before_submission(self):
        variants = []
        undeclared = copy.deepcopy(self.plan)
        undeclared["adapters"]["piece"]["resources"] = {"unknown": 1}
        variants.append(undeclared)
        oversized = copy.deepcopy(self.plan)
        oversized["adapters"]["piece"]["resources"] = {"cpu": self.plan["capacities"]["cpu"] + 1}
        variants.append(oversized)
        parallel_integration = copy.deepcopy(self.plan)
        parallel_integration["capacities"]["integration"] = 2
        variants.append(parallel_integration)
        for plan in variants:
            with self.subTest(plan=plan["capacities"]), self.assertRaises(ValueError):
                submit_plan(self.store, plan)
        self.assertEqual(self.store.jobs(), [])

    def test_cycles_and_unknown_dependencies_are_rejected(self):
        cycle = copy.deepcopy(self.plan)
        cycle["modules"][0]["depends_on"] = ["display"]
        cycle["modules"][1]["depends_on"] = ["math"]
        with self.assertRaisesRegex(ValueError, "cycle"):
            compile_plan(cycle)
        self_cycle = copy.deepcopy(self.plan)
        self_cycle["modules"][0]["depends_on"] = ["math"]
        with self.assertRaisesRegex(ValueError, "cycle"):
            compile_plan(self_cycle)
        unknown = copy.deepcopy(self.plan)
        unknown["modules"][0]["depends_on"] = ["missing"]
        with self.assertRaisesRegex(ValueError, "unknown module dependency"):
            compile_plan(unknown)


if __name__ == "__main__":
    unittest.main()
