"""D-FIX1 coverage through the desk pre-review entrypoint."""

import base64
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import shlex
import subprocess
import tarfile

import pytest


DESK = Path(__file__).resolve().parents[1]
JOBS = Path("/private/tmp/deepsignal")
PINNED = JOBS / "pilot-bandit-remediation/repo"
EVIDENCE = PINNED.parent / "bandit-after.json"
SCANNER = JOBS / "venv-scan/bin/python"
BASELINE = "ec69d0ebd92cf8854b91a7a50fc53e748b886c6e"
REVIEWED = "contrib/deepsignal/console/install/install_site.py"
SCOPE = "contrib/deepsignal"


def git(repo, *args):
    return subprocess.check_output(["git", "-C", repo, *args])


@pytest.fixture(scope="module")
def pinned():
    head = (JOBS / "pilot-bandit-qualification/candidate.sha").read_text().strip()
    assert git(PINNED, "rev-parse", "HEAD").decode().strip() == head
    git_dir = git(PINNED, "rev-parse", "--absolute-git-dir").decode().strip()
    archive = git(PINNED, "archive", head, SCOPE, ".flake8")
    return head, git_dir, archive


@pytest.fixture
def candidate(tmp_path, pinned):
    head, git_dir, archive = pinned
    repo = tmp_path / "candidate"
    repo.mkdir()
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(repo, filter="data")
    git_env = {"GIT_DIR": git_dir, "GIT_WORK_TREE": str(repo)}
    return repo, head, git_env


def pre_review(candidate, receipts, entrypoint=None):
    repo, head, git_env = candidate
    if entrypoint is None:
        entrypoint = stage_entrypoint(repo.parent)
        stage_scanner(entrypoint, f'exec {SCANNER} "$@"\n')
    receipts.mkdir()
    desk_receipts = entrypoint.parent / "receipts"
    if receipts != desk_receipts:
        desk_receipts.symlink_to(receipts, target_is_directory=True)
    return subprocess.run(
        ["bash", entrypoint, repo, head],
        env={**os.environ, **git_env}, capture_output=True, text=True, check=False,
    )


def documents(candidate, receipts):
    head = candidate[1]
    raw_bytes = (receipts / f"bandit-raw-{head}.json").read_bytes()
    raw = json.loads(raw_bytes)
    verdict = json.loads((receipts / f"bandit-policy-{head}.json").read_bytes())
    assert raw["candidate_head"] == verdict["candidate_head"] == head
    assert raw["run_id"] == verdict["run_id"]
    assert hashlib.sha256(raw_bytes).hexdigest() == verdict["raw_sha256"]
    return raw, verdict


def test_d_fix1_original_entrypoint_is_red(candidate, tmp_path):
    # Replay the original shell with a scratch desk and the real Bandit scanner.
    source = git(DESK, "show", f"{BASELINE}:tools/fast-review/pre-review.sh").decode()
    original = stage_entrypoint(tmp_path, source)
    stage_scanner(original, f'exec {SCANNER} "$@"\n')
    result = pre_review(candidate, original.parent / "receipts", original)
    assert result.returncode == 1, result
    assert "PASS flake8" in result.stdout
    assert "FAIL bandit rc=1" in result.stdout
    assert "RESULT RED" in result.stdout


def test_d_fix1_exact_reviewed_head(candidate, tmp_path):
    receipts = tmp_path / "receipts"
    result = pre_review(candidate, receipts)
    assert result.returncode == 0, result
    assert "PASS bandit" in result.stdout and "RESULT GREEN" in result.stdout
    raw, verdict = documents(candidate, receipts)
    report = json.loads(base64.b64decode(raw["stdout_b64"]))
    assert raw["exit_status"] == 1
    assert report["results"] == json.loads(EVIDENCE.read_bytes())["results"]
    assert verdict["verdict"] == "PASS"
    assert verdict["finding_count"] == 188
    assert sum(verdict["site_rationales"].values()) == 188
    assert verdict["policy_sha256"] and verdict["rationale"]


def test_d_fix1_unrelated_safe_variations_and_checkout_config(candidate, tmp_path):
    repo = candidate[0]
    (repo / SCOPE / "safe_extra.py").write_text("def addition(a, b):\n    return a + b\n")
    (repo / SCOPE / "safe_extra.pyw").write_text('LABEL = "harmless"\n')
    # Product-provided scanner settings and policy data are untrusted.
    (repo / SCOPE / ".bandit").write_text("[bandit]\nskips = B101,B603,B104,B404\n")
    (repo / SCOPE / "bandit-policy.json").write_text("{}\n")
    receipts = tmp_path / "receipts"
    result = pre_review(candidate, receipts)
    assert result.returncode == 0, result
    raw, verdict = documents(candidate, receipts)
    report = json.loads(base64.b64decode(raw["stdout_b64"]))
    assert report["metrics"][f"{SCOPE}/safe_extra.py"]["loc"] == 2
    assert report["metrics"][f"{SCOPE}/safe_extra.pyw"]["loc"] == 1
    assert verdict["verdict"] == "PASS" and verdict["finding_count"] == 188


@pytest.mark.parametrize(
    ("name", "source", "rule"),
    [
        ("new_extra.py", "assert __name__\n", "B101"),
        ("new_extra.py", "import subprocess  # noqa: F401\n", "B404"),
        (".py", "assert __name__\n", "B101"),
    ],
)
def test_d_fix1_unlisted_sites_are_red(candidate, tmp_path, name, source, rule):
    repo = candidate[0]
    relative = f"{SCOPE}/{name}"
    (repo / relative).write_text(source)
    (repo / SCOPE / ".bandit").write_text(f"[bandit]\nskips = {rule}\n")
    receipts = tmp_path / "receipts"
    result = pre_review(candidate, receipts)
    assert result.returncode == 1 and "RESULT RED" in result.stdout, result
    raw, verdict = documents(candidate, receipts)
    report = json.loads(base64.b64decode(raw["stdout_b64"]))
    assert any(r["filename"] == relative and r["test_id"] == rule for r in report["results"])
    assert verdict["verdict"] == "FAIL" and verdict["finding_count"] == 189
    assert "unlisted" in verdict["rationale"]


def test_d_fix1_reviewed_source_change_is_red(candidate, tmp_path):
    path = candidate[0] / REVIEWED
    with path.open("a") as stream:
        stream.write("\n# Harmless source change outside the findings' reported context.\n")
    receipts = tmp_path / "receipts"
    result = pre_review(candidate, receipts)
    assert result.returncode == 1 and "FAIL bandit" in result.stdout, result
    raw, verdict = documents(candidate, receipts)
    report = json.loads(base64.b64decode(raw["stdout_b64"]))
    assert report["results"] == json.loads(EVIDENCE.read_bytes())["results"]
    assert verdict["verdict"] == "FAIL" and "source" in verdict["rationale"]


def test_real_scanner_skipped_file_is_red(candidate, tmp_path):
    (candidate[0] / SCOPE / "invalid.py").write_text("def invalid(:\n")
    receipts = tmp_path / "receipts"
    result = pre_review(candidate, receipts)
    assert result.returncode == 1 and "FAIL bandit" in result.stdout, result
    raw, verdict = documents(candidate, receipts)
    report = json.loads(base64.b64decode(raw["stdout_b64"]))
    assert raw["exit_status"] == 1
    assert report["errors"][0]["filename"] == f"{SCOPE}/invalid.py"
    assert verdict["verdict"] == "FAIL" and "skipped" in verdict["rationale"]


def test_missing_reviewed_file_at_pinned_head_is_red(candidate, tmp_path):
    (candidate[0] / REVIEWED).unlink()
    receipts = tmp_path / "receipts"
    result = pre_review(candidate, receipts)
    assert result.returncode == 1 and "FAIL bandit" in result.stdout, result
    raw, verdict = documents(candidate, receipts)
    assert raw["exit_status"] == 1 and verdict["finding_count"] == 183
    assert verdict["verdict"] == "FAIL" and "reviewed source missing" in verdict["rationale"]


def stage_entrypoint(tmp_path, source=None):
    """Relocate the desk root to keep receipts and unrelated audit in scratch."""
    root = tmp_path / "desk"
    root.mkdir()
    for name in ("console-core", "shims"):
        (root / name).symlink_to(JOBS / name)
    for path in DESK.glob("bandit-policy.*"):
        shutil.copy2(path, root / path.name)
    source = source or (DESK / "pre-review.sh").read_text()
    script = root / "pre-review.sh"
    assert source.count("D=/private/tmp/deepsignal;") == 1
    source = source.replace("D=/private/tmp/deepsignal;", f"D={shlex.quote(str(root))};")
    script.write_text(source.replace("SC=/private/tmp/deepsignal/", "SC=$D/"))
    return script


@pytest.fixture
def staged_entrypoint(tmp_path):
    return stage_entrypoint(tmp_path)


def stage_scanner(entrypoint, body):
    path = entrypoint.parent / "venv-scan/bin/python"
    path.parent.mkdir(parents=True)
    path.write_text('#!/bin/bash\nif [[ "$*" == *"import pip_audit"* ]]; then exit 1; fi\n' + body)
    path.chmod(0o700)


@pytest.mark.parametrize("damage", ["missing", "corrupt", "version", "shortened"])
def test_policy_faults_preserve_the_raw_scan(candidate, tmp_path, staged_entrypoint, damage):
    manifest = staged_entrypoint.with_name("bandit-policy.json")
    if damage == "missing":
        manifest.unlink()
    elif damage == "corrupt":
        manifest.write_text('{"unfinished"')
    else:
        document = json.loads(manifest.read_bytes())
        if damage == "version":
            document["bandit_version"] = "0.0.0"
        else:
            document["files"].pop(REVIEWED)
        manifest.write_text(json.dumps(document))
    stage_scanner(staged_entrypoint, f'exec {SCANNER} "$@"\n')
    receipts = tmp_path / "receipts"
    result = pre_review(candidate, receipts, staged_entrypoint)
    assert result.returncode == 1 and "FAIL bandit" in result.stdout, result
    raw, verdict = documents(candidate, receipts)
    assert raw["exit_status"] == 1 and verdict["finding_count"] == 188
    assert verdict["verdict"] == "FAIL" and "manifest" in verdict["rationale"]


@pytest.mark.parametrize(
    ("fault", "reason"),
    [
        ("duplicate", "finding"),
        ("changed_span", "finding"),
        ("changed_line", "finding"),
        ("changed_rule", "finding"),
        ("changed_confidence", "finding"),
        ("changed_severity", "finding"),
        ("changed_context", "finding"),
        ("missing_finding", "finding"),
        ("metrics", "metrics"),
        ("missing_scanned_file", "coverage"),
        ("skipped_tests", "skipped"),
        ("empty_stdout", "report"),
        ("partial", "report"),
        ("empty_report", "report"),
        ("duplicate_json_key", "report"),
        ("exit_mismatch", "exit"),
        ("unexpected_exit", "exit"),
        ("stderr", "diagnostic"),
        ("version", "version"),
        ("broken_import", "probe"),
    ],
)
def test_scanner_faults_fail_closed(candidate, tmp_path, staged_entrypoint, fault, reason):
    # Start with real 1.9.4 evidence, mutate the transport, and retain the shell entrypoint.
    original = EVIDENCE.read_bytes()
    report = json.loads(original)
    findings = report["results"]

    def adjust_counts(finding, delta):
        for path in (finding["filename"], "_totals"):
            for field in ("severity", "confidence"):
                key = f"{field.upper()}.{finding[f'issue_{field}']}"
                report["metrics"][path][key] += delta

    if fault == "duplicate":
        findings.append(findings[0].copy())
        adjust_counts(findings[0], 1)
    elif fault == "changed_span":
        findings[0]["end_col_offset"] += 1
    elif fault == "changed_line":
        findings[0]["line_number"] += 1
    elif fault == "changed_rule":
        findings[0]["test_id"] = "B603"
    elif fault in ("changed_confidence", "changed_severity"):
        adjust_counts(findings[0], -1)
        key = fault.removeprefix("changed_")
        findings[0][f"issue_{key}"] = "MEDIUM"
        adjust_counts(findings[0], 1)
    elif fault == "changed_context":
        findings[0]["code"] += "invented source context"
    elif fault == "missing_finding":
        adjust_counts(findings.pop(0), -1)
    elif fault == "metrics":
        del report["metrics"][REVIEWED]["loc"]
    elif fault == "missing_scanned_file":
        del report["metrics"][REVIEWED]
    elif fault == "skipped_tests":
        report["metrics"][REVIEWED]["skipped_tests"] = 1
    elif fault == "empty_report":
        report["results"] = []
        report["metrics"] = {"_totals": {}}
    payload = tmp_path / "scanner-output"
    encoded = json.dumps(report).encode()
    if fault == "partial":
        encoded = original[:len(original) // 2]
    elif fault == "empty_stdout":
        encoded = b""
    elif fault == "duplicate_json_key":
        encoded = encoded.replace(b'"errors": []', b'"errors": [1], "errors": []', 1)
    payload.write_bytes(encoded)
    status = {"exit_mismatch": 0, "unexpected_exit": 2, "empty_report": 0}.get(fault, 1)
    probe = f'exec {SCANNER} "$@"'
    if fault == "version":
        probe = 'echo "Bandit 0.0.0"; exit 0'
    elif fault == "broken_import":
        probe = 'echo "broken import" >&2; exit 1'
    diagnostic = 'echo "scanner warning" >&2' if fault == "stderr" else ":"
    stage_scanner(
        staged_entrypoint,
        f'if [[ " $* " == *" -m bandit "* ]]; then\n'
        f'    cat {shlex.quote(str(payload))}\n    {diagnostic}\n    exit {status}\nfi\n'
        f'{probe}\n',
    )
    receipts = tmp_path / "receipts"
    result = pre_review(candidate, receipts, staged_entrypoint)
    assert result.returncode == 1 and "FAIL bandit" in result.stdout, result
    raw, verdict = documents(candidate, receipts)
    if fault != "broken_import":
        assert raw["exit_status"] == status
        assert base64.b64decode(raw["stdout_b64"]) == encoded
    else:
        assert raw["exit_status"] is None
    assert verdict["verdict"] == "FAIL" and reason in verdict["rationale"]


def test_absent_scanner_preserves_d_scan1(candidate, tmp_path, staged_entrypoint):
    stage_scanner(staged_entrypoint, 'exec /opt/homebrew/bin/python3.12 "$@"\n')
    receipts = tmp_path / "receipts"
    result = pre_review(candidate, receipts, staged_entrypoint)
    assert result.returncode == 0 and "SKIP bandit" in result.stdout, result
    assert not list(receipts.glob("bandit-*.json"))


def test_nonexecutable_installed_scanner_is_red(candidate, tmp_path, staged_entrypoint):
    stage_scanner(staged_entrypoint, f'exec {SCANNER} "$@"\n')
    (staged_entrypoint.parent / "venv-scan/bin/python").chmod(0o600)
    receipts = tmp_path / "receipts"
    result = pre_review(candidate, receipts, staged_entrypoint)
    assert result.returncode == 1 and "FAIL bandit" in result.stdout, result
    raw, verdict = documents(candidate, receipts)
    assert raw["exit_status"] is None and raw["scanner_probe"]["error"]
    assert verdict["verdict"] == "FAIL" and "probe" in verdict["rationale"]
