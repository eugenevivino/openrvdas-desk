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
import re
import json
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


def main(argv):
    cmd = argv[1] if len(argv) > 1 else ""
    if cmd == "junit":
        for name, status in junit_rows(argv[2], argv[3] if len(argv) > 3 else None):
            print("%s\t%s" % (name, status))
        return 0
    if cmd == "verdict":
        results, expected, receipt, sha, host = argv[2:7]
        v, counts, unexcused, reason = verdict(results, expected)
        try:
            digest = hashlib.sha256(open(results, "rb").read()).hexdigest()
        except FileNotFoundError:
            digest = None
        data = {"sha": sha, "host": host, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "verdict": v, "reason": reason, "counts": counts,
                "unexcused_failures": unexcused, "results_sha256": digest}
        with open(receipt, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=1, sort_keys=True)
        print("VERDICT %s sha=%s pass=%d fail=%d skip=%d excused=%d%s" % (
            v, sha[:12], counts["PASS"], counts["FAIL"], counts["SKIP"], counts.get("excused", 0),
            (" reason=" + reason) if reason else ""))
        for name in unexcused:
            print("  FAIL %s" % name)
        return {"GREEN": 0, "RED": 1}.get(v, 2)
    print(__doc__)
    return 64


if __name__ == "__main__":
    sys.exit(main(sys.argv))
