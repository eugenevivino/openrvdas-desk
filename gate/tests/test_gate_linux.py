"""Exercise Linux gate receipts without a network or installs."""
import copy
import hashlib
import json
import os
from pathlib import Path
import random
import runpy
import shutil
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch


GATE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GATE))
import gate_lib  # noqa: E402

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

# Substitute the runner's system file.
BASH_FIXTURE = r'''
source() {
    if [[ "$1" == /etc/os-release ]]; then
        builtin source "$OS_RELEASE"
    else
        builtin source "$@"
    fi
}
'''

# Stand-ins for the runner's OS, checkout and fork execution. The gate and
# shared JUnit parser and verdict run for real.
RUNNER = r'''
import hashlib
import os
from pathlib import Path
import sys
import tarfile
import json


def object_id(kind, content):
    header = f"{kind} {len(content)}\0".encode()
    return hashlib.sha1(header + content).hexdigest()


def git_tree(snapshot, clean, changed, change_type, old):
    directory = "test"
    clean_content = b"old\n" if old else (snapshot / clean).read_bytes()
    leaves = {clean: ("100644", clean_content)}
    for extra in (".flake8", "test/test_receipt.py", "test/test_extra.py",
                  "test/logger/readers/test_udp_reader.py"):
        if (snapshot / extra).is_file():
            leaves[extra] = ("100644", (snapshot / extra).read_bytes())
    mode = "100644"
    node = snapshot / changed
    if old and change_type == "T":
        mode = "120000"
    content = node.read_bytes() if node.is_file() else b"value = 1\n"
    leaves[changed] = (mode, b"old\n" if old else content)
    trees = [directory]
    if not old and change_type == "D":
        del leaves[changed]
        if node.is_dir():
            trees.append(changed)
            child = changed + "/child.txt"
            leaves[child] = ("100644", (snapshot / child).read_bytes())
    for path in trees:
        sys.stdout.buffer.write(b"040000 tree " + b"0" * 40 + b"\t"
                                + os.fsencode(path) + b"\0")
    for path, (mode, content) in leaves.items():
        oid = object_id("blob", content)
        sys.stdout.buffer.write(f"{mode} blob {oid}\t".encode()
                                + os.fsencode(path) + b"\0")


tool = Path(sys.argv[0]).name
args = sys.argv[1:]
if tool == "uname":
    print(os.environ.get("UNAME", "Linux"))
elif tool == "git":
    snapshot = Path(os.environ["FORK_SNAPSHOT"])
    clean = os.environ["LINT_CLEAN"]
    changed = os.environ["LINT_CHANGED"]
    change_type = os.environ.get("LINT_CHANGE_TYPE", "M")
    if args[2:] == ["remote", "get-url", "origin"]:
        print("https://github.com/eugenevivino/openrvdas")
    elif args[2:] == ["rev-parse", "--verify", "HEAD"]:
        print(os.environ["CHECKOUT_SHA"])
    elif args[2:] == ["for-each-ref", "--contains", os.environ["CHECKOUT_SHA"],
                      "--count=1", "--format=%(refname)",
                      "refs/remotes/origin/"]:
        if os.environ.get("FORK_CONTAINS_SHA", "1") == "1":
            print("refs/remotes/origin/topic")
    elif args[2] == "merge-base":
        print("b" * 40)
    elif args[2:4] == ["diff", "--name-only"]:
        garbage = os.environ.get("CHANGED_GARBAGE")
        if garbage is not None:
            sys.stdout.buffer.write(bytes.fromhex(garbage))
            sys.exit(0)
        paths = [] if os.getenv("EMPTY_DIFF") else [clean, changed]
        if change_type == "D" and (snapshot / changed).is_dir():
            paths.append(changed + "/child.txt")
        for path in paths:
            sys.stdout.buffer.write(os.fsencode(path) + b"\0")
    elif args[2:4] == ["diff", "--quiet"] or args[2] == "status":
        # Simulate a Git stat cache that does not detect a byte rewrite.
        pass
    elif args[2:] == ["ls-files", "-s", "-z"]:
        print("fixture index")
    elif args[2] == "ls-tree":
        old = args[-1] == "b" * 40 and not os.getenv("EMPTY_DIFF")
        git_tree(snapshot, clean, changed, change_type, old)
    elif args[2] == "archive":
        with tarfile.open(fileobj=sys.stdout.buffer, mode="w|") as archive:
            archive.add(snapshot / "test", arcname="test")
            if (snapshot / ".flake8").exists():
                archive.add(snapshot / ".flake8", arcname=".flake8")
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
    print("flake8==7.5.0\npytest-timeout==2.4.0")
    sys.exit(int(os.environ.get("PIP_FREEZE_STATUS", "0")))
elif args[:2] == ["-m", "pytest"]:
    if os.environ.get("REWRITE_DURING_PYTEST"):
        Path(os.environ["LINT_CHANGED"]).write_text("value = 2\n")
    junit = next(arg.split("=", 1)[1] for arg in args
                 if arg.startswith("--junitxml="))
    name = os.environ.get("PYTEST_FAILURE", "")
    outcome = "<failure/>" if name else ""
    good_case = ('<testcase/>' if os.getenv("UNNAMED_CASE") else
                 '<testcase classname="test.test_receipt" name="test_ok"/>')
    fixture_class = "test.logger.readers.test_udp_reader.TestUDPReader"
    Path(junit).write_text(
        '<testsuite tests="2" errors="0" skipped="0" '
        f'failures="{int(bool(name))}">'
        f'{good_case}'
        f'<testcase classname="{fixture_class}" name="{name or "test_other"}">'
        f'{outcome}</testcase></testsuite>', encoding="utf-8")
    deselected = int(os.getenv("DESELECTED", 0))
    module = "test/logger/readers/test_udp_reader.py"
    other_id = module + "::TestUDPReader::" + (name or "test_other")
    items = ["test/test_receipt.py::test_ok", other_id]
    reports = [dict(id=items[0], outcome="PASS"),
               dict(id=other_id, outcome="FAIL" if name else "PASS")]
    if os.getenv("MISSING_OUTCOME"):
        reports.pop()
    if "ORV_COLLECTION" in os.environ:
        Path(os.environ["ORV_COLLECTION"]).write_text(json.dumps(dict(
            collected=2+deselected, started=2,
            excluded=1, deselected=deselected,
            items=items, reports=reports, finished=2,
            subtests=0, subfailures=0,
            modules=[module, "test/test_receipt.py"])))
    if os.getenv("INVALID_COLLECTION"):
        Path(os.environ["ORV_COLLECTION"]).write_text('{"collected":NaN}')
    selection = f", {deselected} deselected" if deselected else ""
    summary = "1 failed, 1 passed" if name else "2 passed"
    print(summary + selection + " in 1s")
    sys.exit(int(os.environ.get("PYTEST_STATUS", str(int(bool(name))))))
elif args[:3] == ["manage.py", "test", "test.django_gui"]:
    failure = os.environ.get("DJANGO_FAILURE", "")
    rows = "django::test.ok\tPASS\n"
    if failure:
        rows += failure + "\tFAIL\n"
    if os.environ.get("DJANGO_COMPLETE", "1") == "1":
        rows += "django::__COMPLETE__\tPASS\n"
    out = Path(os.environ["ORV_DJ_ROWS"])
    raw = os.environ.get("DJANGO_RAW")
    out.write_bytes(rows.encode() if raw is None else bytes.fromhex(raw))
    sys.exit(int(os.environ.get("DJANGO_STATUS", str(int(bool(failure))))))
elif args[:3] == ["-I", "-m", "flake8"] or args[:2] == ["-m", "flake8"]:
    def benchmark(files=1):
        if "--benchmark" in args:
            print("0.01 seconds elapsed")
            units = ("logical lines", "physical lines", "tokens", "files")
            for label in units:
                print(files, "total", label, "processed")
                print("100", label, "processed per second")

    path = args[-1]
    if path == "--":
        if Path.cwd().name != "lint-empty" or any(Path.cwd().iterdir()):
            sys.exit("expected a new empty lint directory")
        if os.getenv("FLAKE8_STATUS"):
            sys.exit(int(os.environ["FLAKE8_STATUS"]))
        benchmark(0)
        print(0)
        sys.exit(0)
    if not Path(path).is_file():
        sys.exit("flake8 input does not exist: " + path)
    if Path.cwd().name != "lint-export":
        sys.exit("flake8 input is not in the lint export")
    if os.getenv("TRUNCATE_RESULTS"):
        (Path.cwd().parent / "results.tsv").write_bytes(b"")
        for suite in ("pytest", "django"):
            (Path.cwd().parent / (suite + ".valid")).write_bytes(b"")
    if path == "./" + os.environ["LINT_CHANGED"]:
        garbage = os.environ.get("FLAKE8_GARBAGE")
        if garbage is not None:
            sys.stdout.buffer.write(bytes.fromhex(garbage))
            sys.exit(0)
        code = os.environ.get("FLAKE8_CODE", "")
        status = int(os.environ.get("FLAKE8_STATUS", "0"))
        real_flake8 = os.environ.get("GATE_REAL_FLAKE8")
        if code == "E501" and status == 0 and real_flake8:
            os.execv(real_flake8, [real_flake8, *args])
        if os.getenv("CONFIG_EXCLUDE") and "--isolated" not in args:
            print(0)
            sys.exit(0)
        if code.startswith("E9"):
            print(f"{code} {path}:0:0: could not parse input: {path}")
        elif code:
            print(f"{code} {path}:1:1: fixture violation")
        if status == 0:
            benchmark()
            print(int(bool(code)))
        sys.exit(status)
    benchmark()
    print(0)
elif (args[0] == "-I" and args[1].endswith("/gate_linux.py")
      and os.getenv("OMIT_END")):
    # Inject the same lost final write at the Python publisher boundary.
    import runpy
    module = runpy.run_path(args[1])
    publish = module["publish"]
    def drop_end(path, data):
        if path.name == "rows.pending":
            data = data.removesuffix(b"__END__\tPASS\n")
        publish(path, data)
    module["main"].__globals__["publish"] = drop_end
    sys.exit(module["main"](args[2:]))
elif args[0] == "-I":
    real_python = os.environ["REAL_PYTHON"]
    os.execv(real_python, [real_python, *args])
else:
    sys.exit("unexpected python call: " + repr(args))
'''


def seal(obj):
    encoded = json.dumps(obj["facts"], sort_keys=True,
                         separators=(",", ":")).encode()
    obj["sha256"] = hashlib.sha256(encoded).hexdigest()


class LinuxGateTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        self.gate = root / "desk" / "gate"
        self.gate.mkdir(parents=True)
        for name in ("gate-linux.sh", "gate_lib.py", "gate_linux.py",
                     "orv_pytest.py"):
            if (GATE / name).is_file():
                shutil.copyfile(GATE / name, self.gate / name)
        (self.gate / "expected-failures.txt").write_text(
            f"{MAC_FAILURE} # macOS UDP baseline\n", encoding="utf-8"
        )
        self.fork = root / "fork"
        (self.fork / "test").mkdir(parents=True)
        reader = self.fork / "test/logger/readers/test_udp_reader.py"
        reader.parent.mkdir(parents=True)
        reader.write_text("class TestUDPReader: pass")
        (self.fork / "test/test_receipt.py").write_text("def test_ok(): pass")
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
            "GATE_REAL_FLAKE8": os.environ.get("GATE_REAL_FLAKE8", ""),
            "LINT_CLEAN": LINT_CLEAN,
            "LINT_CHANGED": LINT_CHANGED,
            "OS_RELEASE": str(self.os_release),
            "BASH_ENV": str(bash_env),
        }

    def invoke_gate(self, sha=SHA, **fixture):
        snapshot = self.receipts.with_name(self.receipts.name + "-snapshot")
        shutil.copytree(self.fork, snapshot, symlinks=True)
        return subprocess.run(
            ["bash", str(self.gate / "gate-linux.sh"), sha, str(self.fork),
             str(self.receipts)],
            env={**self.env, "FORK_SNAPSHOT": str(snapshot), **fixture},
            capture_output=True, text=True,
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
        payload = (self.receipts / "evidence.json").read_bytes()
        self.assertEqual(receipt["evidence_sha256"],
                         hashlib.sha256(payload).hexdigest())
        self.assertEqual(gate_lib.decide(json.loads(payload)).label, verdict)
        self.assertEqual((self.receipts / "evidence.json").stat().st_mode
                         & 0o222, 0)
        if verdict == "REFUSED":
            self.assertNotIn(b"__END__\tPASS\n", results)
            if refusal is not None:
                notice = (self.receipts / "REFUSED.txt").read_text()
                self.assertIn(refusal, notice)
        else:
            self.assertTrue(results.endswith(b"__END__\tPASS\n"))
        return receipt

    def test_flake8_exclusion_hiding_explicit_file(self):
        (self.fork / ".flake8").write_text(
            "[flake8]\nexclude = test/changed.py\n"
        )
        (self.fork / LINT_CHANGED).write_text('value = "' + 'x' * 95 + '"\n')
        receipt = self.run_gate(1, "RED", CONFIG_EXCLUDE="1",
                                FLAKE8_CODE="E501")
        self.assertEqual(receipt["unexcused_failures"],
                         [f"flake8::{LINT_CHANGED}"])

    def test_empty_diff_needs_observed_flake8_completion(self):
        self.run_gate(2, "REFUSED", EMPTY_DIFF="1", FLAKE8_STATUS="1")
        self.receipts = self.receipts.with_name("empty-complete")
        self.run_gate(0, "GREEN", EMPTY_DIFF="1")
        facts = json.loads((self.receipts / "evidence.json").read_bytes())
        self.assertEqual(facts["facts"]["lint"][0]["processed"], 0)

    def test_pytest_addopts_deselection(self):
        (self.fork / "pytest.ini").write_text("[pytest]\naddopts = -k ok\n")
        self.run_gate(2, "REFUSED", DESELECTED="20")

    def test_pytest_additional_excluded_module(self):
        (self.fork / "test/test_extra.py").write_text("def test_extra(): pass")
        self.run_gate(2, "REFUSED", refusal="missing pytest module")

    def test_started_pytest_item_without_outcome(self):
        self.run_gate(2, "REFUSED", MISSING_OUTCOME="1")

    def test_nonfinite_collection_json_is_refused(self):
        self.run_gate(2, "REFUSED", INVALID_COLLECTION="1",
                      refusal="invalid JSON number")

    def test_unnamed_junit_testcase(self):
        self.run_gate(2, "REFUSED", UNNAMED_CASE="1")

    def test_results_truncated_after_validation(self):
        receipt = self.run_gate(1, "RED", DJANGO_FAILURE=DJANGO_FAILURE,
                                TRUNCATE_RESULTS="1")
        self.assertEqual(receipt["unexcused_failures"], [DJANGO_FAILURE])
        results = (self.receipts / "results.tsv").read_text()
        self.assertIn(DJANGO_FAILURE, results)

    def test_resealed_but_inconsistent_proofs(self):
        self.run_gate(0, "GREEN")
        good = json.loads((self.receipts / "evidence.json").read_bytes())
        facts = good["facts"]
        lint = facts["lint"][0]
        suite = facts["pytest"]
        xml = suite["junit"]
        unnamed = xml.replace('classname="test.test_receipt"', 'classname=""')
        duplicate = xml.replace("test_other", "test_ok").replace(
            "test.logger.readers.test_udp_reader.TestUDPReader",
            "test.test_receipt")
        no_reason = xml.replace('skipped="0"', 'skipped="1"').replace(
            'name="test_ok"/>', 'name="test_ok"><skipped/></testcase>')
        changes = [
            ((), "unknown", False),
            (("pytest", "collection"), "unknown", 0),
            (("pytest", "collection"), "excluded", True),
            (("pytest", "collection"), "collected", 1),
            (("pytest",), "argv", suite["argv"] + ["-m", "quick"]),
            (("pytest",), "junit", unnamed),
            (("pytest",), "junit", duplicate),
            (("pytest",), "junit", no_reason),
            (("lint", 0), "argv", [s for s in lint["argv"]
                                   if s != "--exclude="]),
            (("lint", 0), "argv", [s for s in lint["argv"]
                                   if s != "--isolated"]),
            (("lint", 0), "processed", 0),
            (("lint", 0), "count", False),
            (("lint", 0), "findings", ["E501 ./other.py:1:80: too long"]),
            (("changed", 0), "old_type", "tree"),
            ((), "lint", facts["lint"][1:]),
            ((), "results", "flake8::__COMPLETE__\tPASS\n__END__\tPASS\n"),
        ]
        for path, key, value in changes:
            obj = copy.deepcopy(good)
            target = obj["facts"]
            for part in path:
                target = target[part]
            target[key] = value
            seal(obj)
            self.assertEqual(gate_lib.decide(obj).label, "REFUSED",
                             (path, key, value))

    def test_single_field_corruption_and_2000_seeded_mutations(self):
        def locations(node, path=()):
            if isinstance(node, dict):
                children = node.items()
            elif isinstance(node, list):
                children = enumerate(node)
            else:
                return
            for key, child in children:
                yield path + (key,)
                yield from locations(child, path + (key,))

        def damage(original, path, operation):
            obj = copy.deepcopy(original)
            parent = obj
            for key in path[:-1]:
                parent = parent[key]
            key = path[-1]
            if operation == "drop":
                del parent[key]
            elif operation == "substitute":
                was = parent[key]
                if type(was) is int:
                    parent[key] = was + 1
                elif type(was) is str:
                    parent[key] = was + "?"
                elif type(was) is list:
                    was.append("extra")
                else:
                    was["extra"] = 1
            else:
                parent[key] = {"unexpected": 3}
            return obj

        self.run_gate(0, "GREEN")
        green = json.loads((self.receipts / "evidence.json").read_text())
        self.assertEqual(gate_lib.decide(green).label, "GREEN")
        for path in locations(green):
            for operation in ("drop", "wrong type", "substitute"):
                damaged = damage(green, path, operation)
                self.assertEqual(gate_lib.decide(damaged).label, "REFUSED",
                                 path)

        self.receipts = self.receipts.with_name("red")
        self.run_gate(1, "RED", DJANGO_FAILURE=DJANGO_FAILURE)
        red = json.loads((self.receipts / "evidence.json").read_text())
        refused = copy.deepcopy(green)
        refused["facts"]["tracked"]["after"] = "0" * 64
        seal(refused)
        self.assertEqual(gate_lib.decide(red).label, "RED")
        self.assertEqual(gate_lib.decide(refused).label, "REFUSED")
        rng = random.Random(51490)
        seeds = [(obj, list(locations(obj["facts"]))) for obj in
                 (red, refused)]
        for index in range(2000):
            obj, paths = seeds[index % 2]
            path = ("facts",) + rng.choice(paths)
            reseal = index % 4 < 2
            operations = ["drop", "wrong type"]
            if not reseal:
                operations.append("substitute")
            candidate = damage(obj, path, rng.choice(operations))
            if reseal:
                seal(candidate)  # Exercise semantic validation independently.
            self.assertNotEqual(gate_lib.decide(candidate).label, "GREEN",
                                (index, path))

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
        receipt = self.run_gate(1, "RED", FLAKE8_CODE="E225")
        self.assertEqual(receipt["unexcused_failures"],
                         [f"flake8::{LINT_CHANGED}"])
        results = (self.receipts / "results.tsv").read_text()
        self.assertIn(f"flake8::{LINT_CLEAN}\tPASS\n", results)
        self.assertIn(f"flake8::{LINT_CHANGED}\tFAIL\n", results)

    def test_linux_gate_refuses_symlink_replaced_by_regular_file(self):
        self.run_gate(2, "REFUSED", LINT_CHANGE_TYPE="T",
                      refusal=f"Git type changed for {LINT_CHANGED}")
        changed = (self.receipts / "changed.txt").read_bytes().split(b"\0")
        self.assertIn(os.fsencode(LINT_CHANGED), changed)
        self.assertFalse((self.receipts / "pip.log").exists())

    def test_linux_gate_refuses_nonregular_changed_python_paths(self):
        for kind in ("symlink", "directory", "missing"):
            with self.subTest(kind=kind):
                name = f"test/{kind}.py"
                path = self.fork / name
                if kind == "symlink":
                    path.symlink_to(self.fork / LINT_CLEAN)
                if kind == "directory":
                    path.mkdir()
                self.receipts = self.receipts.with_name(f"receipt-{kind}")
                self.run_gate(2, "REFUSED", LINT_CHANGED=name,
                              refusal=f"changed Python path is not a regular "
                                      f"file: {name}")
                self.assertFalse((self.receipts / "pip.log").exists())

    def test_linux_gate_refuses_flake8_e902(self):
        self.run_gate(2, "REFUSED", FLAKE8_CODE="E902",
                      refusal=f"flake8 could not read {LINT_CHANGED}")
        self.assertIn("E902", (self.receipts / "flake8.log").read_text())
        results = (self.receipts / "results.tsv").read_text()
        self.assertNotIn(f"flake8::{LINT_CHANGED}\t", results)

    def test_linux_gate_refuses_sha_outside_fork_remote_refs(self):
        self.run_gate(2, "REFUSED", FORK_CONTAINS_SHA="0",
                      refusal="not reachable from any fork origin branch")
        self.assertFalse((self.receipts / "pip.log").exists())

    def test_linux_gate_refuses_unusual_changed_python_names_up_front(self):
        for kind, char in (("tab", "\t"), ("newline", "\n"), ("cr", "\r"),
                           ("line-separator", "\u2028")):
            with self.subTest(kind=kind):
                name = f"test/unusual{char}name.py"
                (self.fork / name).write_text("value = 1\n")
                self.receipts = self.receipts.with_name(f"receipt-{kind}")
                self.run_gate(2, "REFUSED", LINT_CHANGED=name,
                              refusal="unusual characters in a changed file "
                                      f"name: {name!r}")
                self.assertFalse((self.receipts / "pip.log").exists())

    def test_linux_gate_refuses_flake8_crash_with_empty_output(self):
        self.run_gate(2, "REFUSED", FLAKE8_STATUS="1",
                      refusal=f"flake8 did not complete for {LINT_CHANGED}")
        self.assertEqual((self.receipts / "flake8.out").read_bytes(), b"")
        benchmark = b"0.01 seconds elapsed\n"
        units = (b"logical lines", b"physical lines", b"tokens", b"files")
        for label in units:
            benchmark += b"1 total " + label + b" processed\n"
            benchmark += b"100 " + label + b" processed per second\n"
        self.assertEqual((self.receipts / "flake8.log").read_bytes(),
                         benchmark + b"0\n")
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
                         "flake8==7.5.0\npytest-timeout==2.4.0\n")

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

    def test_linux_gate_refuses_malformed_suite_without_recording_rows(self):
        raw = b"foreign::test\tPASS\n__END__\tPASS\n"
        self.run_gate(2, "REFUSED", DJANGO_RAW=raw.hex())
        self.assertEqual((self.receipts / "results.tsv").read_bytes(), b"")
        self.assertEqual((self.receipts / "django.tsv").read_bytes(), raw)

    def test_linux_gate_refuses_file_replaced_by_directory(self):
        path = self.fork / LINT_CHANGED
        path.unlink()
        path.mkdir()
        (path / "child.txt").write_text("fixture\n")
        self.run_gate(2, "REFUSED", LINT_CHANGE_TYPE="D",
                      refusal=f"Git type changed for {LINT_CHANGED}")
        self.assertFalse((self.receipts / "pip.log").exists())

    def test_linux_gate_refuses_flake8_interruption_after_violation(self):
        self.run_gate(2, "REFUSED", FLAKE8_STATUS="1", FLAKE8_CODE="E501",
                      refusal=f"flake8 did not complete for {LINT_CHANGED}")
        self.assertIn("E501", (self.receipts / "flake8.log").read_text())

    def test_linux_gate_records_complete_e501_as_red(self):
        (self.fork / LINT_CHANGED).write_text(f'value = "{"x" * 95}"\n')
        receipt = self.run_gate(1, "RED", FLAKE8_CODE="E501")
        self.assertEqual(receipt["unexcused_failures"],
                         [f"flake8::{LINT_CHANGED}"])
        self.assertIn(f"E501 ./{LINT_CHANGED}:",
                      (self.receipts / "flake8.log").read_text())

    def test_linux_gate_refuses_tracked_rewrite_during_pytest(self):
        self.run_gate(2, "REFUSED", REWRITE_DURING_PYTEST="1",
                      refusal="after pytest")
        self.assertFalse((self.receipts / "flake8.log").exists())

    def test_linux_gate_random_garbage_in_evidence_never_yields_green(self):
        rng = random.Random(341)
        for channel in ("DJANGO_RAW", "CHANGED_GARBAGE", "FLAKE8_GARBAGE"):
            for case in range(4):
                with self.subTest(channel=channel, case=case):
                    garbage = b"?" + rng.randbytes(rng.randrange(1, 40))
                    if channel == "DJANGO_RAW":
                        garbage += b"\n__END__\tPASS\n"
                    if channel == "CHANGED_GARBAGE":
                        garbage = os.fsencode(LINT_CLEAN) + b"\0" + garbage
                    self.receipts = self.receipts.with_name(
                        f"receipt-{channel}-{case}"
                    )
                    self.run_gate(2, "REFUSED", **{channel: garbage.hex()})


class DjangoRunnerTest(unittest.TestCase):
    def test_django_cooperative_stop_does_not_mark_suite_complete(self):
        result = unittest.TestResult()
        result.startTest(self)
        result.rows = {"django::test.ok": "PASS"}
        result.stop()

        class DiscoverRunner:
            def run_suite(self, suite, **kwargs):
                return result

        fake_django = SimpleNamespace(DiscoverRunner=DiscoverRunner)
        with patch.dict(sys.modules, {"django.test.runner": fake_django}):
            runner_path = str(GATE / "orv_django_runner.py")
            runner = runpy.run_path(runner_path)["Runner"]
        with tempfile.TemporaryDirectory() as temp:
            rows = Path(temp) / "rows.tsv"
            with patch.dict(os.environ, {"ORV_DJ_ROWS": str(rows)}):
                runner().run_suite(None)
            self.assertIn("django::test.ok\tPASS\n", rows.read_text())
            self.assertNotIn("::__COMPLETE__", rows.read_text())
