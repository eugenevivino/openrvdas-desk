"""Parsers and verdict for the OpenRVDAS gate. Standard library only.

Rows are `row<TAB>PASS|FAIL|SKIP`. The last row of a complete run is
`__END__<TAB>PASS`. Verdicts:
  GREEN    complete evidence, no FAIL outside expected-failures.txt
  RED      complete evidence, at least one unexcused FAIL
  REFUSED  incomplete evidence (no __END__, malformed row, missing stage).
           Never green, never red, never blames a change.

Usage:
  gate_lib.py junit <pytest.xml> [pytest.log]    -> rows on stdout
  gate_lib.py verdict <results.tsv> <expected> <receipt.json> <sha> <host>
"""
from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import re
import json
import stat
import sys
import time
import xml.etree.ElementTree as ET

STATUSES = ("PASS", "FAIL", "SKIP")
END = "__END__"


def _subtests(log_path):
    """(passed, failed) subtest counts from pytest's final summary line."""
    passed = failed = 0
    if log_path:
        try:
            text = open(log_path, encoding="utf-8", errors="replace").read()
        except FileNotFoundError:
            return None
        lines = [ln for ln in text.splitlines()
                 if " in " in ln and re.search(r"\d+ (passed|failed)", ln)]
        if not lines:
            return None
        last = lines[-1]
        m = re.search(r"(\d+) subtests passed", last)
        passed = int(m.group(1)) if m else 0
        m = re.search(r"(\d+) subtests failed", last)
        failed = int(m.group(1)) if m else 0
    return passed, failed


def junit_rows(path, log_path=None):
    """Rows from a pytest junit xml. A count mismatch adds a FAIL row.

    pytest counts each subtest in the suite's `tests` attribute without a
    testcase element, so the subtest counts come from the log summary.
    """
    root = ET.parse(path).getroot()
    suites = ([root] if root.tag == "testsuite"
              else list(root.iter("testsuite")))
    rows, declared = [], 0
    for suite in suites:
        declared += int(suite.get("tests", "0"))
        for case in suite.iter("testcase"):
            name = "pytest::%s::%s" % (case.get("classname", ""),
                                       case.get("name", ""))
            if (case.find("failure") is not None or
                    case.find("error") is not None):
                status = "FAIL"
            elif case.find("skipped") is not None:
                status = "SKIP"
            else:
                status = "PASS"
            rows.append((name, status))
    sub = _subtests(log_path) if log_path else (0, 0)
    if sub is None:
        rows.append(("pytest::__NO_SUMMARY_LINE__", "FAIL"))
        return rows
    if sub[1]:
        rows.append(("pytest::__SUBTESTS_FAILED__ %d" % sub[1], "FAIL"))
    if declared != len(rows) - (1 if sub[1] else 0) + sub[0] + sub[1]:
        detail = "declared=%d parsed=%d subtests=%d" % (
            declared, len(rows), sub[0] + sub[1])
        rows.append(("pytest::__COUNT_MISMATCH__ " + detail, "FAIL"))
    elif rows:
        rows.append(("pytest::__COMPLETE__", "PASS"))
    return rows


def read_expected(path):
    names = set()
    try:
        for line in open(path, encoding="utf-8"):
            line = line.split("#", 1)[0].strip()
            if line:
                names.add(line)
    except FileNotFoundError:
        pass
    return names


def verdict(results_path, expected_path):
    """Return (verdict, counts, unexcused_fail_rows, reason)."""
    counts = {s: 0 for s in STATUSES}
    unexcused, excused = [], []
    expected = read_expected(expected_path)
    try:
        lines = open(results_path, encoding="utf-8").read().splitlines()
    except FileNotFoundError:
        return "REFUSED", counts, [], "no results file"
    if not lines or lines[-1] != END + "\tPASS":
        return "REFUSED", counts, [], "missing __END__ as last row"
    for i, line in enumerate(lines[:-1]):
        parts = line.split("\t")
        if (len(parts) != 2 or parts[1] not in STATUSES or
                not parts[0] or parts[0] == END):
            return "REFUSED", counts, [], "malformed row %d" % (i + 1)
        name, status = parts
        counts[status] += 1
        if status == "FAIL":
            (excused if name in expected else unexcused).append(name)
    if counts["PASS"] == 0:
        return "REFUSED", counts, [], "no passing rows (suite did not run)"
    counts["excused"] = len(excused)
    return ("RED" if unexcused else "GREEN"), counts, unexcused, ""


def write_receipt(results, expected, receipt, sha, host, *, refusal=None):
    if refusal is None:
        v, counts, unexcused, reason = verdict(results, expected)
    else:
        v, counts, unexcused, reason = (
            "REFUSED", dict.fromkeys(STATUSES, 0), [], refusal,
        )
    try:
        digest = hashlib.sha256(Path(results).read_bytes()).hexdigest()
    except FileNotFoundError:
        digest = None
    data = {
        "sha": sha, "host": host,
        "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "verdict": v, "reason": reason, "counts": counts,
        "unexcused_failures": unexcused, "results_sha256": digest,
    }
    with open(receipt, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, sort_keys=True)
    print("VERDICT %s sha=%s pass=%d fail=%d skip=%d excused=%d%s" % (
        v, sha[:12], counts["PASS"], counts["FAIL"], counts["SKIP"],
        counts.get("excused", 0), (" reason=" + reason) if reason else "",
    ))
    for name in unexcused:
        print("  FAIL %s" % name)
    return {"GREEN": 0, "RED": 1}.get(v, 2)


def nul_records(data):
    if not data:
        return []
    records = data.split(b"\0")
    if records[-1] or not all(records[:-1]):
        raise ValueError("incomplete Git path list")
    return records[:-1]


GIT_TYPES = {
    b"040000": b"tree", b"100644": b"blob", b"100755": b"blob",
    b"120000": b"blob", b"160000": b"commit",
}
REGULAR_MODES = (b"100644", b"100755")


def tree_entries(data):
    entries = {}
    for record in nul_records(data):
        metadata, _, name = record.partition(b"\t")
        mode, kind, oid = metadata.split(b" ")
        if (GIT_TYPES.get(mode) != kind or name in entries
                or not re.fullmatch(rb"[0-9a-f]{40}", oid)
                or set(name.split(b"/")) & {b"", b".", b".."}):
            raise ValueError("malformed Git tree entry")
        entries[name] = mode, kind, oid
    return entries


def changed_entries(paths, before, after):
    tree = b"040000"
    changed = {
        path for path in before.keys() | after.keys()
        if before.get(path) != after.get(path)
        and ((path in before and before[path][0] != tree)
             or (path in after and after[path][0] != tree))
    }
    if len(paths) != len(changed) or set(paths) != changed:
        raise ValueError("changed Git paths do not match the commit trees")
    return [
        {"path": os.fsdecode(path),
         "old": before[path][0].decode() if path in before else "absent",
         "new": after[path][0].decode() if path in after else "absent",
         "old_type": before[path][1].decode() if path in before else "absent",
         "new_type": after[path][1].decode() if path in after else "absent"}
        for path in paths
    ]


def tracked_hash(entries, root):
    # Verify Git blob identity and hash bytes independently of the stat cache.
    snapshot = hashlib.sha256()
    for name, (mode, _, oid) in sorted(entries.items()):
        snapshot.update(name + b"\0" + mode + b"\0")
        path = Path(root) / os.fsdecode(name)
        try:
            info = path.lstat()
            if mode == b"040000" and stat.S_ISDIR(info.st_mode):
                continue
            if mode == b"120000" and stat.S_ISLNK(info.st_mode):
                content = os.fsencode(os.readlink(path))
                digest = hashlib.sha1(f"blob {len(content)}\0".encode())
                digest.update(content)
                snapshot.update(hashlib.sha256(content).digest())
            elif mode in REGULAR_MODES and stat.S_ISREG(info.st_mode):
                executable = bool(info.st_mode & stat.S_IXUSR)
                if executable != (mode == b"100755"):
                    raise ValueError(f"tracked file mode changed: {path}")
                digest = hashlib.sha1(f"blob {info.st_size}\0".encode())
                file_hash = hashlib.sha256()
                with path.open("rb") as tracked:
                    for block in iter(lambda: tracked.read(1024 * 1024), b""):
                        digest.update(block)
                        file_hash.update(block)
                snapshot.update(file_hash.digest())
            else:
                raise ValueError(f"tracked path changed type: {path}")
            if digest.hexdigest().encode() != oid:
                raise ValueError(f"tracked file bytes changed: {path}")
        except OSError as exc:
            raise ValueError(f"cannot verify tracked path: {path}") from exc

    return snapshot.hexdigest()


# The Mini uses the historical TSV interface above. Linux decisions use only
# the sealed object below. None of these validators open a file or run a tool.
TRACKED_STAGES = ("before", "installed", "frozen", "pytest", "django",
                  "export_before", "before_lint", "export_after", "after")
PYTEST_ARGS = ("-m", "pytest", "test/", "-c", "/dev/null", "--rootdir=.",
               "-o", "addopts=", "-p", "no:cacheprovider", "-p", "orv_pytest",
               "--ignore=test/django_gui", "-q", "--timeout=300")
FLAKE8_ARGS = ("-I", "-m", "flake8", "--isolated", "--exclude=", "--jobs=1",
               "--exit-zero", "--count", "--benchmark",
               "--format=%(code)s %(path)s:%(row)d:%(col)d: %(text)s")


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def fields(obj, keys):
    require(type(obj) is dict and set(obj) == set(keys.split()),
            f"expected fields: {keys}")


def string(value):
    return type(value) is str and value.strip() and value.isprintable()


def count(value):
    return type(value) is int and value >= 0


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode()


def platform_proof(f):
    require(f["system"] == "Linux", "Linux runner required")
    require(f["distribution"] == "ubuntu" and f["release"] == "22.04",
            "Ubuntu 22.04 required")
    require(re.fullmatch(r"3\.12\.\d+", f["python"]), "Python 3.12 required")


def runner_proof(f):
    platform_proof(f)
    require(re.fullmatch("[0-9a-f]{40}", f["requested"]),
            "need a full 40-hex sha")
    require(f["head"] == f["requested"], "fork HEAD does not match request")
    require(f["origin"].removesuffix(".git") ==
            "https://github.com/eugenevivino/openrvdas", "wrong fork origin")
    ref = f["ref"]
    require(string(ref) and re.fullmatch(r"refs/remotes/origin/[^\s]+", ref),
            "not reachable from any fork origin branch")


def lint_paths(changes):
    require(type(changes) is list, "expected changed paths")
    seen = set()
    paths = []
    for entry in changes:
        fields(entry, "path old new old_type new_type")
        for side in ("old", "new"):
            mode = entry[side]
            if mode == "absent":
                kind = "absent"
            else:
                require(string(mode) and mode.encode() in GIT_TYPES,
                        "invalid Git mode")
                kind = GIT_TYPES[mode.encode()].decode()
            require(entry[side + "_type"] == kind, "Git mode/type mismatch")
        path, old, new = (entry[k] for k in ("path", "old", "new"))
        require(string(path), f"unusual characters in a changed file name: "
                f"{ascii(path)}")
        require(path not in seen and
                not set(path.split("/")) & {"", ".", ".."},
                "invalid or duplicate changed path")
        seen.add(path)
        regular = {"100644", "100755"}
        if old != "absent" and new != "absent" and old != new:
            require({old, new} <= regular, f"Git type changed for {path}")
        require({old, new} <= regular | {"absent"} and
                (old, new) != ("absent", "absent"),
                f"changed Git path is not a regular file: {path}")
        if new != "absent" and path.endswith(".py"):
            paths.append(path)
    return paths


def pytest_command(directory):
    return [directory + "/venv/bin/python", *PYTEST_ARGS,
            "--junitxml=" + directory + "/pytest.xml"]


def suite_status(suite, status, rows):
    require(count(status) and status == int(any(s == "FAIL" for _, s in rows)),
            f"{suite} exit {status} disagrees with its rows")


def pytest_module(path):
    name = path.rsplit("/", 1)[-1]
    return (path.startswith("test/")
            and not path.startswith("test/django_gui/")
            and name.endswith(".py") and
            (name.startswith("test_") or name.endswith("_test.py")))


def pytest_report_rows(items, reports, collected, modules):
    """Match pytest's node IDs to JUnit, preserving parametrized names."""
    require(type(items) is list and len(items) == collected and
            all(string(node) for node in items) and
            len(set(items)) == collected,
            "invalid collected pytest items")
    require(type(reports) is list and len(reports) == collected,
            "collected pytest item without an outcome")
    remaining = set(items)
    rows = []
    for report in reports:
        fields(report, "id outcome")
        node, outcome = report["id"], report["outcome"]
        require(node in remaining and outcome in STATUSES,
                "invalid or duplicate pytest report")
        remaining.remove(node)
        path, sep, address = node.partition("::")
        require(sep and address and path in modules, "invalid pytest node ID")
        base, bracket, params = address.partition("[")
        *classes, name = base.split("::")
        cls = ".".join([path.removesuffix(".py").replace("/", "."), *classes])
        rows.append((f"pytest::{cls}::{name}{bracket}{params}", outcome))
    return rows


def pytest_rows(data, directory):
    fields(data, "argv status collection modules junit")
    require(data["argv"] == pytest_command(directory), "wrong pytest command")
    c = data["collection"]
    counters = ("collected started finished deselected excluded "
                "subtests subfailures")
    fields(c, counters + " modules items reports")
    require(all(count(c[k]) for k in counters.split()),
            "invalid pytest counts")
    modules = data["modules"]
    require(type(modules) is list and modules and
            all(string(p) and pytest_module(p) for p in modules) and
            modules == sorted(set(modules)), "invalid tracked pytest modules")
    require(c["modules"] == modules, "missing pytest module or extra module")
    require(c["excluded"] == 1 and c["deselected"] == 0,
            "unexpected pytest exclusion or deselection")
    require(0 < c["started"] == c["collected"] == c["finished"],
            "incomplete pytest execution")
    reports = pytest_report_rows(c["items"], c["reports"], c["collected"],
                                 set(modules))
    require(type(data["junit"]) is str, "expected JUnit XML")
    root = ET.fromstring(data["junit"])
    if root.tag == "testsuites":
        require(len(root) == 1, "expected one pytest suite")
        root = root[0]
    require(root.tag == "testsuite", "missing pytest suite")
    rows, names = [], set()
    totals = dict(failure=0, error=0, skipped=0)
    for case in root:
        require(case.tag == "testcase", "unexpected JUnit suite child")
        cls, name = case.get("classname"), case.get("name")
        require(string(cls) and string(name), "unnamed JUnit testcase")
        key = f"pytest::{cls}::{name}"
        require(key not in names, "duplicate JUnit testcase")
        names.add(key)
        outcomes = set()
        for child in case:
            if child.tag == "properties":
                require(all(p.tag == "property" and not len(p) for p in child),
                        "malformed JUnit properties")
                continue
            require(not len(child), "nested JUnit testcase or outcome")
            if child.tag in ("system-out", "system-err"):
                continue
            require(child.tag in totals, "unknown JUnit outcome")
            totals[child.tag] += 1
            outcomes.add(child.tag)
            if child.tag == "skipped":
                require((child.get("message") or "").strip(),
                        "pytest skip without a reason")
        if outcomes & {"failure", "error"}:
            status = "FAIL"
        elif "skipped" in outcomes:
            status = "SKIP"
        else:
            status = "PASS"
        rows.append((key, status))
    require(sum(totals.values()) <= len(rows) + c["subtests"],
            "more JUnit outcomes than tests and subtests")
    for attr, number in (("tests", len(rows) + c["subtests"]),
                         ("failures", totals["failure"]),
                         ("errors", totals["error"]),
                         ("skipped", totals["skipped"])):
        require(root.get(attr) == str(number), f"JUnit {attr} mismatch")
    require(len(rows) == c["collected"] and
            c["subfailures"] <= min(c["subtests"], totals["failure"]),
            "JUnit disagrees with pytest collection or subtests")
    require(sorted(reports) == sorted(rows),
            "JUnit names or outcomes disagree with pytest reports")
    suite_status("pytest", data["status"], rows)
    if c["subfailures"]:
        failed = c["subfailures"]
        rows.append((f"pytest::__SUBTESTS_FAILED__ {failed}", "FAIL"))
    return rows + [("pytest::__COMPLETE__", "PASS")]


def django_rows(data):
    fields(data, "tsv status")
    require(type(data["tsv"]) is str, "expected django TSV")
    lines = data["tsv"].split("\n")
    require(len(lines) >= 3 and
            lines[-2:] == ["django::__COMPLETE__\tPASS", ""],
            "django results are incomplete")
    rows, seen = [], set()
    for line in lines[:-2]:
        name, _, status = line.partition("\t")
        require(string(name) and name.startswith("django::") and name[8:] and
                not name.startswith("django::__") and name not in seen and
                status in STATUSES, "django results contain a malformed row")
        seen.add(name)
        rows.append((name, status))
    suite_status("django", data["status"], rows)
    return rows + [("django::__COMPLETE__", "PASS")]


def lint_command(directory, path):
    args = [] if path is None else ["./" + path]
    return [directory + "/venv/bin/python", *FLAKE8_ARGS, "--", *args]


def lint_result(data, directory, path):
    fields(data, "argv cwd status processed count findings")
    workdir = "lint-empty" if path is None else "lint-export"
    require(data["cwd"] == directory + "/" + workdir, "wrong lint directory")
    require(data["argv"] == lint_command(directory, path),
            f"wrong flake8 command for {path}")
    require(count(data["status"]) and data["status"] == 0 and
            count(data["processed"]) and
            data["processed"] == int(path is not None),
            f"flake8 did not complete for {path}")
    findings = data["findings"]
    require(type(findings) is list and count(data["count"]) and
            len(findings) == data["count"],
            f"flake8 count disagrees for {path}")
    if path is None:
        require(not findings, "unexpected finding for an empty lint list")
        return None
    pattern = re.compile(r"([A-Z][0-9]{3}) " + re.escape("./" + path) +
                         r":[0-9]+:[0-9]+: .+")
    for finding in findings:
        match = pattern.fullmatch(finding)
        require(match, f"malformed flake8 result for {path}")
        require(not match[1].startswith("E9"), f"flake8 could not read {path}")
    return f"flake8::{path}", "FAIL" if findings else "PASS"


def tsv(rows):
    return "".join(f"{name}\t{status}\n" for name, status in rows)


@dataclass(frozen=True)
class Verdict:
    label: str
    reason: str
    counts: dict
    failures: tuple


def decide(evidence) -> Verdict:
    refused = Verdict("REFUSED", "incomplete evidence",
                      dict.fromkeys(STATUSES, 0), ())
    try:
        fields(evidence, "sha256 facts")
        f = evidence["facts"]
        require(evidence["sha256"] == sha256(canonical(f)),
                "evidence digest mismatch")
        require(type(f) is dict and type(f.get("error")) is str,
                "missing collection status")
        require(not f["error"], f["error"])
        fields(f, "requested head origin ref system distribution release "
               "python directory changed paths tracked install freeze "
               "pins expected "
               "pytest django lint results error")
        runner_proof(f)
        directory = f["directory"]
        require(string(directory) and os.path.isabs(directory) and
                os.path.normpath(directory) == directory, "bad receipt path")
        paths = lint_paths(f["changed"])
        require(f["paths"] == [entry["path"] for entry in f["changed"]],
                "Git changed paths disagree")
        tracked = f["tracked"]
        fields(tracked, " ".join(TRACKED_STAGES))
        require(re.fullmatch("[0-9a-f]{64}", tracked["before"]) and
                all(h == tracked["before"] for h in tracked.values()),
                "tracked file hashes differ")
        require(all(count(f[k]) and f[k] == 0 for k in ("install", "freeze")),
                "dependency setup failed")
        require(f["pins"] == ["flake8==7.5.0", "pytest-timeout==2.4.0"],
                "dependency pin mismatch")
        expected = f["expected"]
        require(type(expected) is list and all(string(s) for s in expected)
                and len(expected) == len(set(expected)),
                "invalid expected rows")
        rows = pytest_rows(f["pytest"], directory) + django_rows(f["django"])
        targets = paths or [None]
        require(type(f["lint"]) is list and len(f["lint"]) == len(targets),
                "missing or extra changed-file lint result")
        for target, observation in zip(targets, f["lint"]):
            row = lint_result(observation, directory, target)
            if row is not None:
                rows.append(row)
        rows.append(("flake8::__COMPLETE__", "PASS"))
        require(type(f["results"]) is str and
                f["results"].endswith("__END__\tPASS\n"),
                "missing __END__ as last row")
        require(f["results"] == tsv(rows + [(END, "PASS")]),
                "results.tsv disagrees with suite or lint evidence")
        counts = {s: sum(outcome == s for _, outcome in rows)
                  for s in STATUSES}
        failures = tuple(name for name, outcome in rows if outcome == "FAIL"
                         and (name.startswith("flake8::")
                              or name not in expected))
        counts["excused"] = counts["FAIL"] - len(failures)
    except (ValueError, TypeError, AttributeError, RecursionError,
            ET.ParseError) as exc:
        return Verdict(refused.label, str(exc), refused.counts, ())
    if failures:
        return Verdict("RED", "", counts, failures)
    return Verdict("GREEN", "", counts, ())


def main(argv):
    cmd = argv[1] if len(argv) > 1 else ""
    if cmd == "junit":
        log = argv[3] if len(argv) > 3 else None
        for name, status in junit_rows(argv[2], log):
            print("%s\t%s" % (name, status))
        return 0
    if cmd == "verdict":
        return write_receipt(*argv[2:7])
    print(__doc__)
    return 64


if __name__ == "__main__":
    sys.exit(main(sys.argv))
