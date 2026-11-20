from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ADAPTER = Path(__file__).resolve().parents[1] / "examples" / "demo_adapter.py"


class DemoAdapterTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="relay-demo-fixture-")
        self.root = Path(self.temporary.name)
        self.sequence = 0

    def tearDown(self):
        self.temporary.cleanup()

    def invoke(self, stage, inputs=None, dependencies=None, expected_code=0):
        self.sequence += 1
        directory = self.root / str(self.sequence)
        directory.mkdir()
        packet = {"schema": 1, "job_id": str(self.sequence), "attempt": 1, "token": 1,
                  "spec": {"inputs": inputs or {}}, "dependencies": dependencies or {}}
        packet["input_digest"] = hashlib.sha256(json.dumps(packet, sort_keys=True).encode()).hexdigest()
        (directory / "input.json").write_text(json.dumps(packet), encoding="utf-8")
        environment = {**os.environ, "RELAY_INPUT_FILE": str(directory / "input.json"),
                       "RELAY_RESULT_FILE": str(directory / "result.json"),
                       "RELAY_ATTEMPT_DIR": str(directory)}
        result = subprocess.run([sys.executable, str(ADAPTER), stage], env=environment,
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, expected_code, result.stdout + result.stderr)
        receipt = json.loads((directory / "result.json").read_text())
        self.assertEqual(receipt["input_digest"], packet["input_digest"])
        self.assertTrue(all(Path(path).exists() for path in receipt["evidence"]))
        return {"receipt": receipt}

    def build_reviewed(self, module):
        names = {"math": ["add", "multiply"], "display": ["render", "unwrap"]}[module]
        pieces = {piece: self.invoke("piece", {"module": module, "piece": piece}) for piece in names}
        assembly = self.invoke("assemble", {"module": module}, pieces)
        tests = self.invoke("test", {"module": module}, {"assembled": assembly})
        return self.invoke("review", {"module": module}, {"tested": tests})

    def test_pieces_become_two_modules_then_one_real_integration_batch(self):
        modules = {name: self.build_reviewed(name) for name in ("math", "display")}
        batch = self.invoke("batch", dependencies=modules)["receipt"]
        self.assertEqual(batch["outcome"], "pass")
        self.assertEqual(batch["data"]["modules"], ["display", "math"])
        self.assertEqual(batch["data"]["batch_invocations"], 1)
        self.assertTrue(batch["data"]["cross_module_check"])
        self.assertEqual(batch["data"]["checks_passed"], 11)
        self.assertFalse(batch["data"]["published"])

    def test_missing_piece_fails_before_module_testing(self):
        piece = self.invoke("piece", {"module": "math", "piece": "add"})
        failed = self.invoke("assemble", {"module": "math"}, {"one": piece}, expected_code=1)
        self.assertEqual(failed["receipt"]["outcome"], "fail")
        self.assertIn("missing required", failed["receipt"]["summary"])

    def test_tampered_piece_invalidates_assembly(self):
        pieces = {name: self.invoke("piece", {"module": "math", "piece": name})
                  for name in ("add", "multiply")}
        Path(pieces["add"]["receipt"]["data"]["artifact"]).write_text("def add(a,b): return 0\n")
        failed = self.invoke("assemble", {"module": "math"}, pieces, expected_code=1)
        self.assertIn("changed", failed["receipt"]["summary"])

    def test_negative_assertion_produces_failure_receipt(self):
        reviewed = self.build_reviewed("math")
        failed = self.invoke("test", {"module": "math", "checks": [
            {"function": "multiply", "args": [6, 7], "expected": 41}]},
            {"module": reviewed}, expected_code=1)
        self.assertEqual(failed["receipt"]["outcome"], "fail")

    def test_single_module_can_proceed_without_waiting_for_full_batch(self):
        reviewed = self.build_reviewed("math")
        batch = self.invoke("batch", dependencies={"math": reviewed})["receipt"]
        self.assertEqual(batch["data"]["modules"], ["math"])
        self.assertFalse(batch["data"]["cross_module_check"])

    def test_unreviewed_module_does_not_enter_batch(self):
        pieces = {name: self.invoke("piece", {"module": "math", "piece": name})
                  for name in ("add", "multiply")}
        assembled = self.invoke("assemble", {"module": "math"}, pieces)
        failed = self.invoke("batch", dependencies={"math": assembled}, expected_code=1)
        self.assertIn("review", failed["receipt"]["summary"])

    def test_review_accepts_assembly_and_test_receipts_for_one_artifact(self):
        pieces = {name: self.invoke("piece", {"module": "math", "piece": name})
                  for name in ("add", "multiply")}
        assembled = self.invoke("assemble", {"module": "math"}, pieces)
        tested = self.invoke("test", {"module": "math"}, {"assembled": assembled})
        reviewed = self.invoke("review", {"module": "math"},
                               {"assembled": assembled, "tested": tested})
        self.assertEqual(reviewed["receipt"]["outcome"], "pass")
        self.assertEqual(reviewed["receipt"]["data"]["stage"], "review")

    def test_review_requires_actual_test_evidence(self):
        pieces = {name: self.invoke("piece", {"module": "math", "piece": name})
                  for name in ("add", "multiply")}
        assembled = self.invoke("assemble", {"module": "math"}, pieces)
        failed = self.invoke("review", {"module": "math"},
                             {"assembled": assembled}, expected_code=1)
        self.assertIn("test evidence", failed["receipt"]["summary"])

    def test_review_rejects_different_artifacts_with_same_contents(self):
        pieces = {name: self.invoke("piece", {"module": "math", "piece": name})
                  for name in ("add", "multiply")}
        first = self.invoke("assemble", {"module": "math"}, pieces)
        second = self.invoke("assemble", {"module": "math"}, pieces)
        tested = self.invoke("test", {"module": "math"}, {"assembled": first})
        failed = self.invoke("review", {"module": "math"},
                             {"assembled": second, "tested": tested}, expected_code=1)
        self.assertIn("same artifact", failed["receipt"]["summary"])


if __name__ == "__main__":
    unittest.main()
