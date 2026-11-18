"""Exercise Linux gate receipts without a network or installs."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


GATE = Path(__file__).resolve().parents[1]
SHA = "a" * 40
MAC_FAILURE = (
    "pytest::test.logger.readers.test_udp_reader.TestUDPReader::test_broadcast"
)
DJANGO_FAILURE = (
    "django::test.django_gui.test_django_server_api."
    "TestDjangoServerAPI.test_basic"
)

# Stand-ins for the runner's OS, checkout and fork execution. The gate and
# shared JUnit parser and verdict run for real.
RUNNER = '''
import os
from pathlib import Path
import sys

tool = Path(sys.argv[0]).name
args = sys.argv[1:]
if tool == "uname":
    print("Linux")
elif tool == "git":
    if args[2:] == ["rev-parse", "--verify", "HEAD"]:
        print(os.environ["CHECKOUT_SHA"])
    elif args[2] == "merge-base":
        print(os.environ["CHECKOUT_SHA"])
    elif args[2] != "diff":
        sys.exit("unexpected git call: " + repr(args))
elif args[:2] == ["-I", "-c"]:
    sys.exit(0)
elif args[:2] == ["-m", "venv"]:
    python = Path(args[2]) / "bin" / "python"
    python.parent.mkdir(parents=True)
    python.symlink_to(Path(sys.argv[0]).resolve())
elif args[:2] == ["-m", "pip"]:
    sys.exit(int(os.environ.get("PIP_STATUS", "0")))
elif args[:2] == ["-m", "pytest"]:
    junit = next(arg.split("=", 1)[1] for arg in args
                 if arg.startswith("--junitxml="))
    name = os.environ.get("PYTEST_FAILURE", "")
    outcome = "<failure/>" if name else ""
    fixture_class = "test.logger.readers.test_udp_reader.TestUDPReader"
    Path(junit).write_text(
        '<testsuite tests="2">'
        f'<testcase classname="{fixture_class}" name="test_ok"/>'
        f'<testcase classname="{fixture_class}" name="{name or "test_other"}">'
        f'{outcome}</testcase></testsuite>', encoding="utf-8")
    print("1 failed, 1 passed in 1s" if name else "2 passed in 1s")
    sys.exit(int(os.environ.get("PYTEST_STATUS", str(int(bool(name))))))
elif args[:3] == ["manage.py", "test", "test.django_gui"]:
    failure = os.environ.get("DJANGO_FAILURE", "")
    rows = "django::test.ok\\tPASS\\n"
    if failure:
        rows += failure + "\\tFAIL\\n"
    if os.environ.get("DJANGO_COMPLETE", "1") == "1":
        rows += "django::__COMPLETE__\\tPASS\\n"
    Path(os.environ["ORV_DJ_ROWS"]).write_text(rows, encoding="utf-8")
    sys.exit(int(bool(failure)))
elif args[0] == "-I":
    real_python = os.environ["REAL_PYTHON"]
    os.execv(real_python, [real_python, *args])
else:
    sys.exit("unexpected python call: " + repr(args))
'''


class LinuxGateTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        self.gate = root / "desk" / "gate"
        self.gate.mkdir(parents=True)
        for name in ("gate-linux.sh", "gate_lib.py"):
            if (GATE / name).is_file():
                shutil.copyfile(GATE / name, self.gate / name)
        (self.gate / "expected-failures.txt").write_text(
            f"{MAC_FAILURE} # macOS UDP baseline\n", encoding="utf-8"
        )
        self.fork = root / "fork"
        self.fork.mkdir()
        self.receipts = root / "receipt"
        tools = root / "bin"
        tools.mkdir()
        runner = tools / "runner"
        runner.write_text(f"#!{sys.executable}\n{RUNNER}", encoding="utf-8")
        runner.chmod(0o755)
        for name in ("git", "python3", "uname"):
            (tools / name).symlink_to(runner)
        self.env = {
            "PATH": os.pathsep.join((str(tools), os.defpath)),
            "REAL_PYTHON": sys.executable,
            "CHECKOUT_SHA": SHA,
        }

    def run_gate(self, code, verdict, **fixture):
        run = subprocess.run(
            ["bash", str(self.gate / "gate-linux.sh"), SHA, str(self.fork),
             str(self.receipts)],
            env={**self.env, **fixture}, capture_output=True, text=True,
            timeout=30,
        )
        self.assertEqual(run.returncode, code, run.stdout + run.stderr)
        receipt = json.loads((self.receipts / "receipt.json").read_text())
        results = (self.receipts / "results.tsv").read_bytes()
        self.assertEqual(receipt["verdict"], verdict, run.stdout + run.stderr)
        self.assertEqual(receipt["sha"], SHA)
        self.assertEqual(
            receipt["results_sha256"], hashlib.sha256(results).hexdigest()
        )
        if verdict == "REFUSED":
            self.assertNotIn(b"__END__\tPASS\n", results)
        else:
            self.assertTrue(results.endswith(b"__END__\tPASS\n"))
        return receipt

    def test_linux_gate_refuses_missing_end(self):
        self.run_gate(2, "REFUSED", DJANGO_COMPLETE="0")

    def test_linux_gate_refuses_wrong_checkout_sha(self):
        self.run_gate(2, "REFUSED", CHECKOUT_SHA="b" * 40)
        self.assertFalse((self.receipts / "pip.log").exists())

    def test_linux_gate_refuses_failed_dependency_install(self):
        self.run_gate(2, "REFUSED", PIP_STATUS="1")
        self.assertTrue((self.receipts / "pip.log").is_file())
        self.assertFalse((self.receipts / "pytest.log").exists())

    def test_linux_gate_excuses_exact_macos_failure(self):
        receipt = self.run_gate(0, "GREEN", PYTEST_FAILURE="test_broadcast")
        self.assertEqual(receipt["counts"]["excused"], 1)
        self.assertEqual(receipt["unexcused_failures"], [])

    def test_linux_gate_rejects_macos_failure_prefix(self):
        receipt = self.run_gate(1, "RED", PYTEST_FAILURE="test_broadcas")
        self.assertEqual(receipt["unexcused_failures"], [MAC_FAILURE[:-1]])

    def test_linux_gate_preserves_unexcused_django_failure(self):
        receipt = self.run_gate(1, "RED", DJANGO_FAILURE=DJANGO_FAILURE)
        self.assertEqual(receipt["unexcused_failures"], [DJANGO_FAILURE])

    def test_linux_gate_refuses_interrupted_pytest(self):
        self.run_gate(2, "REFUSED", PYTEST_STATUS="2")
