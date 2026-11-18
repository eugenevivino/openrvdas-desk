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
LINT_CLEAN = "test/clean file.py"
LINT_CHANGED = "test/changed.py"

# Substitute the runner's system file and simulate a lost final write.
BASH_FIXTURE = r'''
source() {
    if [[ "$1" == /etc/os-release ]]; then
        builtin source "$OS_RELEASE"
    else
        builtin source "$@"
    fi
}
printf() {
    if [[ ${OMIT_END:-0} == 1 && "$1" == *'__END__\tPASS\n' ]]; then
        set -- "${1%__END__\\tPASS\\n}" "${@:2}"
    fi
    builtin printf "$@"
}
'''

# Stand-ins for the runner's OS, checkout and fork execution. The gate and
# shared JUnit parser and verdict run for real.
RUNNER = r'''
import os
from pathlib import Path
import sys

tool = Path(sys.argv[0]).name
args = sys.argv[1:]
if tool == "uname":
    print(os.environ.get("UNAME", "Linux"))
elif tool == "git":
    if args[2:] == ["rev-parse", "--verify", "HEAD"]:
        print(os.environ["CHECKOUT_SHA"])
    elif args[2] == "merge-base":
        print(os.environ["CHECKOUT_SHA"])
    elif args[2] == "diff":
        for path in (os.environ["LINT_CLEAN"], os.environ["LINT_CHANGED"]):
            sys.stdout.buffer.write(os.fsencode(path) + b"\0")
    else:
        sys.exit("unexpected git call: " + repr(args))
elif args[:2] == ["-I", "-c"]:
    version = os.environ.get("PYTHON_VERSION", "3.12.0")
    print(version)
    sys.exit(version.split(".")[:2] != ["3", "12"])
elif args[:2] == ["-m", "venv"]:
    python = Path(args[2]) / "bin" / "python"
    python.parent.mkdir(parents=True)
    python.symlink_to(Path(sys.argv[0]).resolve())
elif args[:3] == ["-m", "pip", "install"]:
    print(" ".join(args[3:]))
    sys.exit(int(os.environ.get("PIP_STATUS", "0")))
elif args == ["-m", "pip", "freeze"]:
    print("pytest-timeout==2.4.0")
    sys.exit(int(os.environ.get("PIP_FREEZE_STATUS", "0")))
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
    rows = "django::test.ok\tPASS\n"
    if failure:
        rows += failure + "\tFAIL\n"
    if os.environ.get("DJANGO_COMPLETE", "1") == "1":
        rows += "django::__COMPLETE__\tPASS\n"
    Path(os.environ["ORV_DJ_ROWS"]).write_text(rows, encoding="utf-8")
    sys.exit(int(os.environ.get("DJANGO_STATUS", str(int(bool(failure))))))
elif args[:2] == ["-m", "flake8"]:
    path = args[-1]
    if not Path(path).is_file():
        sys.exit("flake8 input does not exist: " + path)
    if path == "./" + os.environ["LINT_CHANGED"]:
        code = os.environ.get("FLAKE8_CODE")
        if code:
            print(f"{code} {path}:1:1: fixture violation")
        sys.exit(int(os.environ.get("FLAKE8_STATUS", "0")))
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
        (self.fork / "test").mkdir(parents=True)
        for path in (LINT_CLEAN, LINT_CHANGED):
            (self.fork / path).write_text("value = 1\n", encoding="utf-8")
        self.receipts = root / "receipt"
        self.os_release = root / "os-release"
        self.os_release.write_text('ID=ubuntu\nVERSION_ID="22.04"\n')
        bash_env = root / "bash-env"
        bash_env.write_text(BASH_FIXTURE, encoding="utf-8")
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
            "LINT_CLEAN": LINT_CLEAN,
            "LINT_CHANGED": LINT_CHANGED,
            "OS_RELEASE": str(self.os_release),
            "BASH_ENV": str(bash_env),
        }

    def invoke_gate(self, sha=SHA, **fixture):
        return subprocess.run(
            ["bash", str(self.gate / "gate-linux.sh"), sha, str(self.fork),
             str(self.receipts)],
            env={**self.env, **fixture}, capture_output=True, text=True,
            timeout=30,
        )

    def run_gate(self, code, verdict, *, sha=SHA, refusal=None, **fixture):
        run = self.invoke_gate(sha, **fixture)
        self.assertEqual(run.returncode, code, run.stdout + run.stderr)
        receipt = json.loads((self.receipts / "receipt.json").read_text())
        results = (self.receipts / "results.tsv").read_bytes()
        self.assertEqual(receipt["verdict"], verdict, run.stdout + run.stderr)
        self.assertEqual(receipt["sha"], sha)
        self.assertEqual(
            receipt["results_sha256"], hashlib.sha256(results).hexdigest()
        )
        if verdict == "REFUSED":
            self.assertNotIn(b"__END__\tPASS\n", results)
            if refusal is not None:
                notice = (self.receipts / "REFUSED.txt").read_text()
                self.assertIn(refusal, notice)
        else:
            self.assertTrue(results.endswith(b"__END__\tPASS\n"))
        return receipt

    def test_linux_gate_records_flake8_pass_and_changed_paths(self):
        self.run_gate(0, "GREEN")
        results = (self.receipts / "results.tsv").read_text()
        paths = (LINT_CLEAN, LINT_CHANGED)
        for path in paths:
            self.assertIn(f"flake8::{path}\tPASS\n", results)
        expected = b"".join(os.fsencode(path) + b"\0" for path in paths)
        self.assertEqual(
            (self.receipts / "changed.txt").read_bytes(), expected
        )

    def test_linux_gate_records_flake8_violation_as_red(self):
        receipt = self.run_gate(
            1, "RED", FLAKE8_STATUS="1", FLAKE8_CODE="E225"
        )
        self.assertEqual(receipt["unexcused_failures"],
                         [f"flake8::{LINT_CHANGED}"])
        results = (self.receipts / "results.tsv").read_text()
        self.assertIn(f"flake8::{LINT_CLEAN}\tPASS\n", results)
        self.assertIn(f"flake8::{LINT_CHANGED}\tFAIL\n", results)

    def test_linux_gate_refuses_flake8_crash_with_empty_output(self):
        self.run_gate(2, "REFUSED", FLAKE8_STATUS="1",
                      refusal=f"flake8 did not complete for {LINT_CHANGED}")
        self.assertEqual((self.receipts / "flake8.log").read_bytes(), b"")
        results = (self.receipts / "results.tsv").read_text()
        self.assertIn(f"flake8::{LINT_CLEAN}\tPASS\n", results)
        self.assertNotIn(f"flake8::{LINT_CHANGED}\t", results)

    def test_linux_gate_finish_refuses_missing_end_after_all_stages_pass(self):
        receipt = self.run_gate(2, "REFUSED", OMIT_END="1")
        self.assertEqual(receipt["reason"], "missing __END__ as last row")
        self.assertFalse((self.receipts / "REFUSED.txt").exists())
        results = (self.receipts / "results.tsv").read_text()
        for suite in ("pytest", "django", "flake8"):
            self.assertIn(f"{suite}::__COMPLETE__\tPASS\n", results)
        self.assertNotIn("\tFAIL\n", results)

    def test_linux_gate_refuses_wrong_python(self):
        self.run_gate(2, "REFUSED", PYTHON_VERSION="3.11.9",
                      refusal="Python 3.12 required")

    def test_linux_gate_refuses_non_linux_uname(self):
        self.run_gate(2, "REFUSED", UNAME="Darwin",
                      refusal="Linux runner required")

    def test_linux_gate_refuses_malformed_sha(self):
        self.run_gate(2, "REFUSED", sha="zz", refusal="need a full 40-hex sha")

    def test_linux_gate_refuses_existing_receipt_directory(self):
        self.receipts.mkdir()
        results = self.receipts / "results.tsv"
        results.write_text("existing receipt\n")
        run = self.invoke_gate()
        self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
        self.assertIn("could not create a new receipt directory", run.stderr)
        self.assertEqual(list(self.receipts.iterdir()), [results])
        self.assertEqual(results.read_text(), "existing receipt\n")

    def test_linux_gate_refuses_pytest_exit_status_disagreeing_with_rows(self):
        self.run_gate(2, "REFUSED", PYTEST_FAILURE="test_broadcast",
                      PYTEST_STATUS="0",
                      refusal="pytest exit 0 disagrees with its rows")

    def test_linux_gate_refuses_django_exit_status_disagreeing_with_rows(self):
        self.run_gate(2, "REFUSED", DJANGO_STATUS="1",
                      refusal="django exit 1 disagrees with its rows")

    def test_linux_gate_records_runner_release(self):
        self.run_gate(0, "GREEN")
        meta = (self.receipts / "meta.txt").read_text().splitlines()
        self.assertIn("ID=ubuntu", meta)
        self.assertIn("VERSION_ID=22.04", meta)

    def test_linux_gate_refuses_unsupported_release(self):
        self.os_release.write_text('ID=ubuntu\nVERSION_ID="24.04"\n')
        self.run_gate(2, "REFUSED", refusal="Ubuntu 22.04 required")
        meta = (self.receipts / "meta.txt").read_text().splitlines()
        self.assertIn("ID=ubuntu", meta)
        self.assertIn("VERSION_ID=24.04", meta)

    def test_linux_gate_refuses_unsupported_distribution(self):
        self.os_release.write_text('ID=debian\nVERSION_ID="22.04"\n')
        self.run_gate(2, "REFUSED", refusal="Ubuntu 22.04 required")

    def test_linux_gate_pins_lint_and_timeout_and_records_pip_freeze(self):
        self.run_gate(0, "GREEN")
        install = (self.receipts / "pip.log").read_text().split()
        self.assertIn("flake8==7.5.0", install)
        self.assertIn("pytest-timeout==2.4.0", install)
        self.assertEqual((self.receipts / "pip-freeze.txt").read_text(),
                         "pytest-timeout==2.4.0\n")

    def test_linux_gate_refuses_failed_pip_freeze(self):
        self.run_gate(2, "REFUSED", PIP_FREEZE_STATUS="1",
                      refusal="could not record pip freeze")

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
