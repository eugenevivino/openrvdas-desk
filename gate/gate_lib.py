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
        lines = [ln for ln in text.splitlines() if " in " in ln and re.search(r"\d+ (passed|failed)", ln)]
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
    suites = [root] if root.tag == "testsuite" else list(root.iter("testsuite"))
    rows, declared = [], 0
    for suite in suites:
        declared += int(suite.get("tests", "0"))
        for case in suite.iter("testcase"):
            name = "pytest::%s::%s" % (case.get("classname", ""), case.get("name", ""))
            if case.find("failure") is not None or case.find("error") is not None:
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
        rows.append(("pytest::__COUNT_MISMATCH__ declared=%d parsed=%d subtests=%d"
                     % (declared, len(rows), sub[0] + sub[1]), "FAIL"))
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
        if len(parts) != 2 or parts[1] not in STATUSES or not parts[0] or parts[0] == END:
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


def validated_suite(suite, status, rows_path):
    raw = Path(rows_path).read_bytes().decode("utf-8")
    lines = raw.split("\n")
    prefix = suite + "::"
    complete = prefix + "__COMPLETE__\tPASS"
    if len(lines) < 3 or lines[-2:] != [complete, ""]:
        raise ValueError(f"{suite} results are incomplete")
    has_failure = False
    for line in lines[:-2]:
        name, sep, outcome = line.partition("\t")
        if (not sep or outcome not in STATUSES or not name.isprintable()
                or not name.startswith(prefix) or name == prefix
                or name == prefix + "__COMPLETE__"):
            raise ValueError(f"{suite} results contain a malformed row")
        has_failure |= outcome == "FAIL"
    if status != str(int(has_failure)):
        raise ValueError(f"{suite} exit {status} disagrees with its rows")
    return raw.encode("utf-8")


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


def tree_entries(path):
    entries = {}
    for record in nul_records(Path(path).read_bytes()):
        metadata, _, name = record.partition(b"\t")
        mode, kind, oid = metadata.split(b" ")
        if (GIT_TYPES.get(mode) != kind or name in entries
                or not re.fullmatch(rb"[0-9a-f]{40}", oid)
                or set(name.split(b"/")) & {b"", b".", b".."}):
            raise ValueError("malformed Git tree entry")
        entries[name] = mode, oid
    return entries


def changed_python(paths, before_path, after_path):
    before, after = tree_entries(before_path), tree_entries(after_path)
    paths = nul_records(Path(paths).read_bytes())
    tree = b"040000"
    changed = {
        path for path in before.keys() | after.keys()
        if before.get(path) != after.get(path)
        and ((path in before and before[path][0] != tree)
             or (path in after and after[path][0] != tree))
    }
    if len(paths) != len(changed) or set(paths) != changed:
        raise ValueError("changed Git paths do not match the commit trees")
    lint_paths = []
    for path in paths:
        name = path.decode("utf-8", errors="surrogateescape")
        if not name.isprintable():
            raise ValueError(f"unusual characters in a changed file name: "
                             f"{ascii(name)}")
        old, new = (entries.get(path, (None,))[0]
                    for entries in (before, after))
        if old is not None and new is not None:
            if old != new and not {old, new} <= set(REGULAR_MODES):
                raise ValueError(f"Git type changed for {name}")
        if any(mode not in (None, *REGULAR_MODES) for mode in (old, new)):
            raise ValueError(f"changed Git path is not a regular file: {name}")
        if new is not None and path.endswith(b".py"):
            lint_paths.append(path + b"\0")
    return b"".join(lint_paths)


def verify_tree(tree_path, root):
    # Hash raw bytes without relying on Git's stat cache or checkout filters.
    for name, (mode, oid) in tree_entries(tree_path).items():
        path = Path(root) / os.fsdecode(name)
        try:
            info = path.lstat()
            if mode in (b"040000", b"160000") and stat.S_ISDIR(info.st_mode):
                continue
            if mode == b"120000" and stat.S_ISLNK(info.st_mode):
                content = os.fsencode(os.readlink(path))
                digest = hashlib.sha1(f"blob {len(content)}\0".encode())
                digest.update(content)
            elif mode in REGULAR_MODES and stat.S_ISREG(info.st_mode):
                executable = bool(info.st_mode & stat.S_IXUSR)
                if executable != (mode == b"100755"):
                    raise ValueError(f"tracked file mode changed: {path}")
                digest = hashlib.sha1(f"blob {info.st_size}\0".encode())
                with path.open("rb") as tracked:
                    for block in iter(lambda: tracked.read(1024 * 1024), b""):
                        digest.update(block)
            else:
                raise ValueError(f"tracked path changed type: {path}")
            if digest.hexdigest().encode() != oid:
                raise ValueError(f"tracked file bytes changed: {path}")
        except OSError as exc:
            raise ValueError(f"cannot verify tracked path: {path}") from exc


def lint_row(path, output):
    raw = Path(output).read_bytes().decode("utf-8")
    lines = raw.split("\n")
    if (len(lines) < 2 or lines[-1] or
            not re.fullmatch(r"0|[1-9][0-9]*", lines[-2])):
        raise ValueError(f"flake8 did not complete for {path} "
                         "(see flake8.log)")
    pattern = re.compile(
        r"([A-Z][0-9]{3}) " + re.escape("./" + path) + r":[0-9]+:[0-9]+: .+"
    )
    violations = lines[:-2]
    if int(lines[-2]) != len(violations):
        raise ValueError(f"flake8 count disagrees for {path} (see flake8.log)")
    for line in violations:
        match = pattern.fullmatch(line)
        if match is None:
            raise ValueError(f"malformed flake8 result for {path}")
        if match[1].startswith("E9"):
            raise ValueError(f"flake8 could not read {path} (see flake8.log)")
    return f"flake8::{path}\t{'FAIL' if violations else 'PASS'}\n".encode()


def main(argv):
    cmd = argv[1] if len(argv) > 1 else ""
    if cmd == "junit":
        for name, status in junit_rows(argv[2], argv[3] if len(argv) > 3 else None):
            print("%s\t%s" % (name, status))
        return 0
    if cmd == "verdict":
        return write_receipt(*argv[2:7])
    if cmd == "refused":
        return write_receipt(*argv[2:7], refusal=argv[7])
    try:
        if cmd == "suite":
            sys.stdout.buffer.write(validated_suite(*argv[2:]))
            return 0
        if cmd == "changed-python":
            sys.stdout.buffer.write(changed_python(*argv[2:]))
            return 0
        if cmd == "verify-tree":
            verify_tree(*argv[2:])
            return 0
        if cmd == "lint-row":
            sys.stdout.buffer.write(lint_row(*argv[2:]))
            return 0
    except (OSError, ValueError) as exc:
        print(exc, file=sys.stderr)
        return 2
    print(__doc__)
    return 64


if __name__ == "__main__":
    sys.exit(main(sys.argv))
