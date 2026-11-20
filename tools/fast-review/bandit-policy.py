"""Run Bandit and publish separate raw and policy receipts."""

import base64
from collections import Counter, defaultdict
import fcntl
from fnmatch import fnmatchcase
import hashlib
import io
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile
import uuid


SCOPE = "contrib/deepsignal"
EXCLUDES = ("*/test/*", "*/node_modules/*")
MANIFEST = Path(__file__).with_name("bandit-policy.json")
MANIFEST_SHA256 = (
    "4a83d80929ea3111f6d410b232866769acf55b090d5db26087071a32586833b9"
)
LEVELS = ("UNDEFINED", "LOW", "MEDIUM", "HIGH")
RATINGS = ("confidence", "severity")
SCORES = {f"{kind.upper()}.{level}" for kind in RATINGS for level in LEVELS}
METRICS = SCORES | {"loc", "nosec", "skipped_tests"}
PROBE = (
    "import importlib.util; "
    "print('absent' if importlib.util.find_spec('bandit') is None "
    "else 'Bandit ' + __import__('bandit').__version__)"
)


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("ascii")


def json_object(pairs):
    result = dict(pairs)
    require(len(result) == len(pairs), "duplicate JSON key")
    return result


def invalid_constant(value):
    raise ValueError(f"invalid JSON constant {value}")


def read_json(data):
    return json.loads(data.decode("utf-8"), object_pairs_hook=json_object,
                      parse_constant=invalid_constant)


def publish(path, document):
    data = canonical(document) + b"\n"
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        try:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
            os.replace(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)
    return digest(data)


def capture(argv, cwd=None):
    status, stdout, stderr, error = None, b"", b"", None
    try:
        result = subprocess.run(
            argv, cwd=cwd, capture_output=True, timeout=120, check=False,
        )
        status = result.returncode
        stdout, stderr = result.stdout, result.stderr
    except subprocess.TimeoutExpired as exc:
        stdout, stderr = exc.stdout or b"", exc.stderr or b""
        error = "scanner command timed out"
    except OSError as exc:
        error = str(exc)
    return {
        "exit_status": status,
        "stdout_b64": base64.b64encode(stdout).decode("ascii"),
        "stderr_b64": base64.b64encode(stderr).decode("ascii"),
        "error": error,
    }


def excluded(path):
    return any(fnmatchcase(path, pattern) for pattern in EXCLUDES)


def scanned_source(path):
    return path.endswith((".py", ".pyw")) and not excluded(path)


def walk_error(error):
    raise error


def file_stamp(info):
    # Exclude atime, which can change as Bandit reads. ctime detects writes
    # even when the original bytes and mtime are restored.
    return (info.st_dev, info.st_ino, info.st_mode, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns)


def source_inventory(repo, stamps=None):
    scope = repo / SCOPE
    for directory in (scope.parent, scope):
        require(directory.is_dir() and not directory.is_symlink(),
                f"scan scope directory unavailable: {directory.name}")
    files = {}
    for root, dirs, names in os.walk(scope, onerror=walk_error):
        root = Path(root)
        local = root.relative_to(repo).as_posix()
        if stamps is not None:
            stamps[local] = file_stamp(root.lstat())
        dirs[:] = [d for d in dirs if not excluded(f"{local}/{d}/")]
        for directory in dirs:
            require(not (root / directory).is_symlink(),
                    f"symlink directory in scan scope: {local}/{directory!r}")
        for name in names:
            path = root / name
            relative = path.relative_to(repo).as_posix()
            if not scanned_source(relative):
                continue
            info = path.lstat()
            require(stat.S_ISREG(info.st_mode), f"non-regular scan source {relative!r}")
            if stamps is not None:
                stamps[relative] = file_stamp(info)
            files[relative] = digest(path.read_bytes())
    require(files, "no source files in scan scope")
    return files


def git_output(repo, *args, input_bytes=None):
    return subprocess.run(
        ["git", "--no-replace-objects", "-C", repo, *args],
        env={**os.environ, "GIT_NO_LAZY_FETCH": "1"},
        input=input_bytes, capture_output=True, check=True, timeout=120,
    ).stdout


def committed_snapshot(repo, head, snapshot):
    listing = git_output(repo, "ls-tree", "-rz", "--full-tree", head, "--", SCOPE)
    sources = {}
    for line in listing.split(b"\0")[:-1]:
        metadata, name = line.split(b"\t", 1)
        relative = os.fsdecode(name)
        if not scanned_source(relative):
            continue
        require(relative.startswith(f"{SCOPE}/")
                and not {"", ".", ".."}.intersection(relative.split("/")),
                f"invalid committed source path {relative!r}")
        mode, kind, oid = metadata.split()
        require(kind == b"blob" and mode in (b"100644", b"100755"),
                f"non-regular committed scan source {relative!r}")
        sources[relative] = oid
    require(sources, "no source files in pinned Git tree")

    # Read the raw blobs in one Git invocation, without checkout filters or
    # archive attributes modifying the source bytes or file list.
    batch = b"\n".join(sources.values()) + b"\n"
    blobs = io.BytesIO(git_output(repo, "cat-file", "--batch", input_bytes=batch))
    inventory = {}
    for relative, oid in sources.items():
        header = blobs.readline().split()
        require(len(header) == 3 and header[:2] == [oid, b"blob"] and header[2].isdigit(),
                f"invalid Git blob for {relative!r}")
        size = int(header[2])
        data = blobs.read(size)
        require(len(data) == size and blobs.read(1) == b"\n",
                f"incomplete Git blob for {relative!r}")
        inventory[relative] = digest(data)
        destination = snapshot / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
    require(not blobs.read(1), "unexpected data after Git blobs")
    return inventory


def verify_candidate(repo, head, inventory):
    current = git_output(repo, "rev-parse", "--verify", "HEAD^{commit}").decode("ascii").strip()
    require(current == head, "candidate head moved")
    try:
        actual = source_inventory(repo)
    except (OSError, ValueError) as exc:
        reason = f"candidate source cannot be verified against pinned Git tree: {exc}"
        raise ValueError(reason) from exc
    require(actual == inventory, "candidate source does not match pinned Git tree")


def run_scan(scanner, repo, receipts, raw):
    probe = raw["scanner_probe"]
    require(probe["exit_status"] == 0 and not probe["stderr_b64"],
            "scanner probe failed")
    with tempfile.TemporaryDirectory(prefix=".bandit-scan-", dir=receipts) as temp:
        snapshot = Path(temp)
        head = raw["candidate_head"]
        inventory = committed_snapshot(repo, head, snapshot)
        raw["source_inventory_sha256"] = digest(canonical(inventory))
        raw["file_count"] = len(inventory)
        integrity_error = None
        try:
            verify_candidate(repo, head, inventory)
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            # The committed snapshot can still produce independent scan evidence.
            integrity_error = str(exc)
        ini = snapshot / "desk-bandit.ini"
        ini.write_text("[bandit]\n", encoding="ascii")
        before = {}
        require(source_inventory(snapshot, before) == inventory,
                "scan snapshot does not match pinned Git tree")
        args = [
            "-q", "-r", SCOPE, "-x", ",".join(EXCLUDES),
            "--ini", ini.name, "--ignore-nosec", "-f", "json",
        ]
        raw["scanner_args"] = args
        raw.update(capture([*scanner, "-m", "bandit", *args], cwd=snapshot))
        try:
            after = {}
            require(source_inventory(snapshot, after) == inventory and before == after,
                    "source bytes or file metadata differ")
        except (OSError, ValueError) as exc:
            integrity_error = f"scan snapshot changed during scan: {exc}"
        return inventory, integrity_error


def report_findings(raw, report, inventory):
    require(not raw["stderr_b64"], "scanner emitted diagnostics")
    require(
        isinstance(report, dict)
        and report.keys() == {"generated_at", "errors", "metrics", "results"}
        and isinstance(report["generated_at"], str)
        and re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", report["generated_at"])
        and isinstance(report["results"], list)
        and isinstance(report["errors"], list)
        and isinstance(report["metrics"], dict),
        "incomplete scanner report",
    )
    require(not report["errors"], "scanner reported skipped files or errors")
    metrics = report["metrics"]
    require(metrics.keys() == {"_totals", *inventory},
            "scanner report file coverage mismatch")
    require(raw["exit_status"] == bool(report["results"]),
            "scanner exit disagrees with report")

    findings = defaultdict(list)
    for finding in report["results"]:
        require(
            isinstance(finding, dict)
            and isinstance(finding.get("filename"), str)
            and finding["filename"] in inventory
            and all(finding.get(f"issue_{kind}") in LEVELS for kind in RATINGS),
            "malformed scanner finding",
        )
        findings[finding["filename"]].append(finding)

    totals = Counter()
    for path in inventory:
        counts = Counter(
            f"{kind.upper()}.{item[f'issue_{kind}']}"
            for item in findings[path] for kind in RATINGS
        )
        row = metrics[path]
        require(
            isinstance(row, dict) and row.keys() == METRICS
            and all(type(value) is int and value >= 0 for value in row.values()),
            f"malformed scanner metrics for {path!r}",
        )
        require(row["nosec"] == row["skipped_tests"] == 0,
                f"scanner skipped tests for {path!r}")
        require(all(row[key] == counts[key] for key in SCORES),
                f"scanner metrics disagree with findings for {path!r}")
        totals.update(row)
    require(canonical(metrics["_totals"]) == canonical(dict(totals)),
            "inconsistent scanner metrics totals")
    return findings


def site(finding):
    return (
        finding["test_id"], finding["issue_severity"], finding["issue_confidence"],
        finding["line_number"], finding["col_offset"], finding["end_col_offset"],
    )


def match_policy(policy, head, inventory, findings):
    files = policy["files"]
    require(head != policy["reviewed_head"] or files.keys() <= inventory.keys(),
            "reviewed source missing at the pinned head")
    for path, actual in findings.items():
        require(not actual or path in files, f"unlisted finding in {path!r}")
    rationales = Counter()
    for path, entry in files.items():
        if path not in inventory:
            continue
        require(inventory[path] == entry["source_sha256"],
                f"reviewed source changed in {path!r}")
        actual = findings[path]
        require(digest(canonical(sorted(actual, key=canonical))) == entry["findings_sha256"],
                f"finding multiset mismatch in {path!r}")
        expected = Counter(
            (group["rule"], group["severity"], group["confidence"], *span)
            for group in entry["groups"] for span in group["sites"]
        )
        require(Counter(map(site, actual)) == expected,
                f"finding site manifest mismatch in {path!r}")
        for group in entry["groups"]:
            rationales[group["rationale"]] += len(group["sites"])
    return rationales


def verdict_for(raw, repo, inventory, raw_sha, integrity_error):
    verdict = {
        "candidate_head": raw["candidate_head"],
        "run_id": raw["run_id"],
        "raw_sha256": raw_sha,
        "policy_sha256": None,
        "verdict": "FAIL",
        "finding_count": None,
        "rationale": None,
    }
    try:
        try:
            require(not MANIFEST.is_symlink(), "policy manifest is a symlink")
            manifest_bytes = MANIFEST.read_bytes()
            verdict["policy_sha256"] = digest(manifest_bytes)
        except OSError:
            manifest_bytes = b""

        require(not raw["error"], raw["error"])
        require(raw["exit_status"] in (0, 1), "unexpected scanner exit")
        try:
            report = read_json(base64.b64decode(raw["stdout_b64"]))
        except (ValueError, RecursionError) as exc:
            raise ValueError("malformed scanner report JSON") from exc
        if isinstance(report, dict) and isinstance(report.get("results"), list):
            verdict["finding_count"] = len(report["results"])

        require(verdict["policy_sha256"] == MANIFEST_SHA256,
                "missing or mismatched policy manifest")
        policy = read_json(manifest_bytes)
        require(policy["schema"] == 1, "unsupported policy manifest schema")
        verdict["policy_reviewed_head"] = policy["reviewed_head"]
        version = f'Bandit {policy["bandit_version"]}\n'.encode("ascii")
        observed = base64.b64decode(raw["scanner_probe"]["stdout_b64"])
        require(observed == version, "scanner version drift")
        findings = report_findings(raw, report, inventory)

        require(integrity_error is None, integrity_error)
        head = raw["candidate_head"]
        verify_candidate(repo, head, inventory)
        rationales = match_policy(policy, head, inventory, findings)
        verdict.update(
            verdict="PASS",
            rationale=("all findings match reviewed sites" if rationales
                       else "complete scan with no findings"),
            site_rationales=dict(rationales),
        )
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        verdict["rationale"] = " ".join(str(exc).splitlines())
    return verdict


def main(scanner_path, repo_path, head, receipt_path):
    require(re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", head),
            "invalid candidate head")
    repo, receipts = Path(repo_path), Path(receipt_path)
    scanner = [scanner_path, "-I", "-B"]
    with (receipts / f".bandit-{head}.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        probe = capture([*scanner, "-c", PROBE])
        if (probe["exit_status"] == 0 and not probe["stderr_b64"]
                and base64.b64decode(probe["stdout_b64"]) == b"absent\n"):
            print("SKIP bandit (not installed, D-SCAN1; runs in the cloud review)")
            return 0

        raw = {
            "candidate_head": head,
            "run_id": uuid.uuid4().hex,
            "scanner_probe": probe,
            "exit_status": None,
            "stdout_b64": "",
            "stderr_b64": "",
            "error": None,
        }
        inventory = {}
        integrity_error = None
        try:
            inventory, integrity_error = run_scan(scanner, repo, receipts, raw)
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            raw["error"] = str(exc)
        raw_sha = publish(receipts / f"bandit-raw-{head}.json", raw)
        verdict = verdict_for(raw, repo, inventory, raw_sha, integrity_error)
        publish(receipts / f"bandit-policy-{head}.json", verdict)
        print(f'{verdict["verdict"]} bandit (run {raw["run_id"]}, findings '
              f'{verdict["finding_count"]}): {verdict["rationale"]}')
        return int(verdict["verdict"] != "PASS")


if __name__ == "__main__":
    try:
        sys.exit(main(*sys.argv[1:]))
    except (OSError, ValueError) as error:
        print(f"FAIL bandit: {error}", file=sys.stderr)
        sys.exit(1)
