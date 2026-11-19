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
UNRELATED = f"{SCOPE}/__init__.py"


def git(repo, *args):
    return subprocess.check_output(
        ["git", "-C", repo, "-c", "core.hooksPath=/dev/null", *args],
        env={**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1"},
    )


def commit(candidate, *paths):
    repo, _ = candidate
    git(repo, "add", "--force", "--", *paths)
    git(repo, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
        "commit", "-m", "Test candidate variation")
    return repo, git(repo, "rev-parse", "HEAD").decode().strip()


@pytest.fixture(scope="module")
def pinned(tmp_path_factory):
    head = (JOBS / "pilot-bandit-qualification/candidate.sha").read_text().strip()
    assert git(PINNED, "rev-parse", "HEAD").decode().strip() == head
    seed = tmp_path_factory.mktemp("seed")
    git(seed, "init", "--quiet")
    # Copy the exact reviewed commit from a local path without sharing its object store.
    git(seed, "-c", "protocol.file.allow=always", "fetch", "--quiet", "--no-tags",
        "--depth=1", str(PINNED), head)
    git(seed, "update-ref", "HEAD", head)
    archive = git(PINNED, "archive", head, SCOPE, ".flake8")
    return head, seed, archive


@pytest.fixture
def candidate(tmp_path, pinned):
    head, seed, archive = pinned
    repo = tmp_path / "candidate"
    shutil.copytree(seed / ".git", repo / ".git")
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(repo, filter="data")
    git(repo, "read-tree", head)
    return repo, head


def pre_review(candidate, receipts, entrypoint=None):
    repo, head = candidate
    if entrypoint is None:
        entrypoint = stage_entrypoint(repo.parent)
        stage_scanner(entrypoint, f'exec {SCANNER} "$@"\n')
    receipts.mkdir()
    desk_receipts = entrypoint.parent / "receipts"
    if receipts != desk_receipts:
        desk_receipts.symlink_to(receipts, target_is_directory=True)
    return subprocess.run(
        ["bash", entrypoint, repo, head],
        capture_output=True, text=True, check=False,
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
    additions = [f"{SCOPE}/safe_extra.py", f"{SCOPE}/safe_extra.pyw"]
    (repo / additions[0]).write_text("def addition(a, b):\n    return a + b\n")
    (repo / additions[1]).write_text('LABEL = "harmless"\n')
    (repo / UNRELATED).write_bytes(git(repo, "show", f"HEAD:{UNRELATED}") + b"\n# Benign edit.\n")
    candidate = commit(candidate, UNRELATED, *additions)
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
    inventory = {
        path: hashlib.sha256(git(repo, "show", f"{candidate[1]}:{path}")).hexdigest()
        for path in report["metrics"] if path != "_totals"
    }
    encoded = json.dumps(inventory, sort_keys=True, separators=(",", ":")).encode("ascii")
    assert raw["source_inventory_sha256"] == hashlib.sha256(encoded).hexdigest()


@pytest.mark.parametrize("change", ["edited", "staged", "missing", "untracked", "ignored"])
def test_d_fix1_dirty_scanned_source_is_red(candidate, tmp_path, change):
    repo, head = candidate
    if change in {"edited", "staged"}:
        (repo / UNRELATED).write_text('LABEL = "dirty"\n')
        if change == "staged":
            git(repo, "add", "--", UNRELATED)
    elif change == "missing":
        (repo / UNRELATED).unlink()
    else:
        relative = f"{SCOPE}/dirty.py" if change == "untracked" else f"{SCOPE}/dirty.pyw"
        if change == "ignored":
            (repo / ".git/info/exclude").write_text(f"/{relative}\n")
        (repo / relative).write_text('LABEL = "dirty"\n')
        if change == "ignored":
            git(repo, "check-ignore", "--", relative)
    assert git(repo, "rev-parse", "HEAD").decode().strip() == head
    receipts = tmp_path / "receipts"
    result = pre_review(candidate, receipts)
    assert result.returncode == 1 and "FAIL bandit" in result.stdout, result
    raw, verdict = documents(candidate, receipts)
    report = json.loads(base64.b64decode(raw["stdout_b64"]))
    assert raw["exit_status"] == 1 and verdict["finding_count"] == 188
    assert report["metrics"][UNRELATED] == json.loads(EVIDENCE.read_bytes())["metrics"][UNRELATED]
    assert f"{SCOPE}/dirty.py" not in report["metrics"]
    assert f"{SCOPE}/dirty.pyw" not in report["metrics"]
    assert verdict["verdict"] == "FAIL" and "pinned Git tree" in verdict["rationale"]


def test_d_fix1_edits_outside_recursive_scan_scope_pass(candidate, tmp_path):
    repo = candidate[0]
    paths = ["outside.py", f"{SCOPE}/nested/test/ignored.py", f"{SCOPE}/node_modules/ignored.pyw"]
    for relative in paths:
        path = repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("assert __name__\n")
    candidate = commit(candidate, *paths)
    (repo / paths[0]).write_text("assert False\n")
    (repo / paths[1]).unlink()
    (repo / SCOPE / "node_modules/untracked.py").write_text("assert False\n")
    receipts = tmp_path / "receipts"
    result = pre_review(candidate, receipts)
    assert result.returncode == 0, result
    raw, verdict = documents(candidate, receipts)
    report = json.loads(base64.b64decode(raw["stdout_b64"]))
    assert not set(paths) & report["metrics"].keys()
    assert f"{SCOPE}/node_modules/untracked.py" not in report["metrics"]
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
    candidate = commit(candidate, relative)
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
    candidate = commit(candidate, REVIEWED)
    receipts = tmp_path / "receipts"
    result = pre_review(candidate, receipts)
    assert result.returncode == 1 and "FAIL bandit" in result.stdout, result
    raw, verdict = documents(candidate, receipts)
    report = json.loads(base64.b64decode(raw["stdout_b64"]))
    assert report["results"] == json.loads(EVIDENCE.read_bytes())["results"]
    assert verdict["verdict"] == "FAIL" and "source" in verdict["rationale"]


def test_real_scanner_skipped_file_is_red(candidate, tmp_path):
    (candidate[0] / SCOPE / "invalid.py").write_text("def invalid(:\n")
    candidate = commit(candidate, f"{SCOPE}/invalid.py")
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
    assert raw["exit_status"] == 1 and verdict["finding_count"] == 188
    assert verdict["verdict"] == "FAIL" and "pinned Git tree" in verdict["rationale"]


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


@pytest.mark.parametrize("restore", [False, True], ids=["persistent", "restored"])
def test_d_fix1_snapshot_write_during_scan_is_red(candidate, tmp_path, staged_entrypoint, restore):
    path = shlex.quote(UNRELATED)
    restore_source = f'cat original-source > {path}\n' if restore else ""
    stage_scanner(
        staged_entrypoint,
        f'if [[ " $* " == *" -m bandit "* ]]; then\n'
        f'    cp {path} original-source\n'
        f'    printf "LABEL = 42\\n" > {path}\n'
        f'    {SCANNER} "$@"\n'
        f'    status=$?\n    {restore_source}    exit "$status"\nfi\n'
        f'exec {SCANNER} "$@"\n',
    )
    receipts = tmp_path / "receipts"
    result = pre_review(candidate, receipts, staged_entrypoint)
    assert result.returncode == 1 and "FAIL bandit" in result.stdout, result
    raw, verdict = documents(candidate, receipts)
    report = json.loads(base64.b64decode(raw["stdout_b64"]))
    assert raw["exit_status"] == 1 and report["metrics"][UNRELATED]["loc"] == 1
    assert verdict["verdict"] == "FAIL" and "scan snapshot changed" in verdict["rationale"]


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
