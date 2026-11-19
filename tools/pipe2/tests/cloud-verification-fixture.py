"""Exercise the launcher with real claims and simulated GitHub."""

import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
from shlex import quote
import subprocess
import sys
from tempfile import TemporaryDirectory
import time

DESK_SHA = "a" * 40
PRODUCT_SHA = "b" * 40
NEXT_SHA = "c" * 40
DESK_REPO = "eugenevivino/openrvdas-desk"
PRODUCT_REPO = "eugenevivino/openrvdas"
DESK_REF = "refs/heads/deepsignal/cloud-verification-dispatch"
PRODUCT_REF = "refs/heads/deepsignal/console-supervised-pilot"
WORKFLOW = ".github/workflows/cloud-verification.yml"
LAUNCHER = Path("tools/fast-review/ds-launch-when-ok.sh").resolve()
SOURCE_DESK = LAUNCHER.parents[2]
COMMANDS = ("pin", "dependencies", "console-tests", "console-types")
NEEDS = "---\nneeds:\n  network: no\n  tools: git, gh\n---\n"


def stage(root):
    """Stage the entry point and policy files before running any launcher."""
    desk = root / "desk"
    installed = root / "desk-main"
    for target in (desk, installed):
        shutil.copytree(SOURCE_DESK / "docs/designs", target / "docs/designs")
    for name in ("preflight.sh", "cloud-verification-dispatch.py"):
        target = desk / "tools/pipe2" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SOURCE_DESK / "tools/pipe2" / name, target)
    shutil.copy2(desk / "tools/pipe2/preflight.sh", root / "preflight.sh")

    launcher = desk / LAUNCHER.relative_to(SOURCE_DESK)
    launcher.parent.mkdir(parents=True)
    lines = LAUNCHER.read_text().splitlines(keepends=True)
    root_line = "state=/private/tmp/deepsignal\n"
    draft_line = "state=${DS_LAUNCH_STATE_DIR:-/private/tmp/deepsignal}\n"
    state_lines = [index for index, line in enumerate(lines)
                   if line in (root_line, draft_line)]
    index, = state_lines
    lines[index] = lines[index].replace(
        "/private/tmp/deepsignal", quote(str(root)),
    )
    launcher.write_text("".join(lines))

    bins = root / "bin"
    bins.mkdir()
    script = Path(__file__).resolve()
    for tool in ("git", "gh"):
        stub = bins / tool
        stub.write_text(
            f'#!/bin/bash\nexec "{sys.executable}" "{script}" '
            'fake-host "$0" "$@"\n'
        )
        stub.chmod(0o700)
    stub = bins / "perl"
    stub.write_text(
        '#!/bin/bash\n'
        'if [[ ${2:-} == "alarm 9900; exec @ARGV" ]]; then\n'
        f'  touch {quote(str(root / "mac-called"))}\n'
        '  echo "fixture: blocked local Codex execution" >&2\n'
        '  exit 99\n'
        'fi\n'
        'exec /usr/bin/perl "$@"\n'
    )
    stub.chmod(0o700)
    return launcher


def fake_host():
    """Invoked as git or gh on PATH. All remote state lives in the fixture."""
    root = Path(os.environ["DISPATCH_FIXTURE"])
    state_path = root / "host.json"
    state = json.loads(state_path.read_text())
    args = sys.argv[1:]
    if Path(sys.argv[0]).name == "git":
        repo = None
        if args[:1] == ["-C"]:
            repo = (
                DESK_REPO if Path(args[1]) == root / "desk"
                else PRODUCT_REPO
            )
            args = args[2:]
        match args:
            case ["remote", "get-url", "origin"]:
                print("https://github.com/" + repo + ".git")
            case ["rev-parse", "HEAD"]:
                print(DESK_SHA if repo == DESK_REPO else state["local"])
            case ["rev-parse", "--show-toplevel"]:
                if repo == DESK_REPO:
                    print(root / "desk")
                else:
                    print(root / "product")
            case ["status", "--porcelain", "--untracked-files=all"]:
                assert repo == DESK_REPO
            case ["ls-remote", "--refs", url, ref]:
                if url == f"https://github.com/{PRODUCT_REPO}.git":
                    assert ref == PRODUCT_REF
                    sha = state["product"]
                else:
                    assert url == f"https://github.com/{DESK_REPO}.git"
                    sha = (
                        state.get("desk", DESK_SHA) if ref == DESK_REF
                        else state["tags"].get(ref)
                    )
                if sha:
                    print(f"{sha}\t{ref}")
            case ["push", *options, url, spec]:
                assert options == [
                    "--no-follow-tags", "--recurse-submodules=no",
                ]
                assert repo == DESK_REPO
                assert url == f"https://github.com/{DESK_REPO}.git"
                sha, ref = spec.split(":")
                assert sha == DESK_SHA
                expected = f"refs/tags/cloud-verification/v1/{state['local']}"
                assert ref == f"{expected}-{DESK_SHA}"
                if state.get("occupant"):
                    lock = root / ".ds-codex.lock" / "pid"
                    assert int(lock.read_text()) == state["occupant"]
                    os.kill(state["occupant"], 0)
                if state.get("parallel"):
                    root.joinpath(f"pusher-{os.getpid()}").touch()
                    deadline = time.monotonic() + 5
                    while len(list(root.glob("pusher-*"))) < 2:
                        assert time.monotonic() < deadline, "push did not race"
                        time.sleep(0.02)
                with root.joinpath("host.guard").open("a") as guard:
                    fcntl.flock(guard, fcntl.LOCK_EX)
                    state = json.loads(state_path.read_text())
                    if ref in state["tags"]:
                        sys.exit(1)
                    state["tags"][ref] = sha
                    state["pushes"].append(ref)
                    partial = root / "host.new"
                    partial.write_text(json.dumps(state))
                    partial.replace(state_path)
                sys.exit(1 if state.get("uncertain") else 0)
            case _:
                raise AssertionError(args)
        return

    assert args[:3] == ["api", "--hostname", "github.com"]
    assert args[3:5] == ["--paginate", "--slurp"]
    endpoint, = args[5:]
    assert endpoint.startswith(f"repos/{DESK_REPO}/actions/")
    if "/jobs?" in endpoint:
        assert any(
            f"/runs/{run_id}/attempts/1/jobs?" in endpoint
            for run_id in (41, 42)
        )
        outcomes = state.get("outcomes", ["success"] * len(COMMANDS))
        started = "2026-11-19T10:00:00Z"
        jobs = [{"name": "pilot", "steps": [
            {"name": name, "status": "completed", "conclusion": result,
             "started_at": started if result != "skipped" else None}
            for name, result in zip(COMMANDS, outcomes)
        ]}]
        print(json.dumps([{"jobs": jobs}]))
        return

    assert endpoint.startswith(f"repos/{DESK_REPO}/actions/runs?")
    runs = [{"id": 40, "display_title": "another-request", "path": WORKFLOW,
             "head_sha": DESK_SHA, "event": "push"}]
    if state.get("visible", True):
        for offset, ref in enumerate(state["tags"]):
            runs.append({
                "id": 41 + offset,
                "display_title": f"Pilot cloud verification ({ref})",
                "path": WORKFLOW, "head_sha": state.get("run_sha", DESK_SHA),
                "event": "push", "run_attempt": state.get("attempt", 1),
                "status": state.get("status", "completed"),
                "conclusion": state.get("result", "success"),
            })
    pages = [{"workflow_runs": runs[:1]}, {"workflow_runs": runs[1:]}]
    print(json.dumps(pages))


class Fixture:
    def __init__(self, root):
        self.root = root
        self.launcher = stage(root)
        self.product = root / "product"
        self.product.mkdir()
        self.prompt = root / "pilot.md"
        self.prompt.write_text(NEEDS)
        self.claims = root / "claims"
        self.claims.mkdir()
        self.lock = root / ".ds-codex.lock"
        self.lock.mkdir()
        self.lock.joinpath("pid").write_text(str(os.getpid()))
        self.wip = root / "wip-units.txt"
        self.wip.write_text("console|/product$\n")
        # A cloud submission must never read the heavy-job count.
        heavy = root / "heavy-jobs.sh"
        called = root / "heavy-called"
        heavy.write_text(f'#!/bin/bash\ntouch "{called}"\necho 99\n')
        heavy.chmod(0o700)
        self.env = os.environ | {
            "PATH": f"{root / 'bin'}:{os.environ['PATH']}",
            "DISPATCH_FIXTURE": str(root), "DS_POLL": "1",
        }
        self.env.pop("DS_REVIEW_ROUTE", None)
        self.env.pop("DS_WIP_EXEMPT", None)
        self.env.pop("DS_LAUNCH_STATE_DIR", None)
        self.host = root / "host.json"
        self.update(
            local=PRODUCT_SHA, product=PRODUCT_SHA,
            tags={}, pushes=[], occupant=os.getpid(),
        )

    def state(self):
        return json.loads(self.host.read_text()) if self.host.exists() else {}

    def update(self, **changes):
        self.host.write_text(json.dumps(self.state() | changes))

    def invocation(self, label, cloud=True, sha=None):
        receipt = self.root / f"{label}.json"
        args = ["bash", str(self.launcher), str(self.product),
                str(self.prompt), str(receipt), "0"]
        if cloud:
            args += ["--cloud-verify", DESK_SHA, sha or self.state()["local"]]
        else:
            args += ["--", "-m", "test-model", "-"]
        return args, receipt

    def launch(self, label, expected, contains, cloud=True, sha=None,
               **overrides):
        args, receipt = self.invocation(label, cloud, sha)
        result = subprocess.run(
            args, env=self.env | overrides, text=True, capture_output=True,
            timeout=20,
        )
        output = result.stdout + result.stderr
        self.root.joinpath(f"{label}.log").write_text(output)
        assert result.returncode == expected, (label, result, output)
        assert contains in output, (label, output)
        assert not self.root.joinpath("heavy-called").exists()
        assert not self.root.joinpath("mac-called").exists()
        return json.loads(receipt.read_text()) if receipt.exists() else None


def overlap(fixture):
    fixture.launch("local-baseline", 1, "NOT launched after", cloud=False)
    assert fixture.state()["pushes"] == []
    first = fixture.launch("first-pin", 0, "success")
    assert first["product_sha"] == PRODUCT_SHA
    assert first["desk_sha"] == DESK_SHA
    assert first["run_id"] == 41
    assert first["commands"]["console-tests"]["conclusion"] == "success"
    fixture.update(local=NEXT_SHA, product=NEXT_SHA)
    second = fixture.launch("second-pin", 0, "success")
    assert second["product_sha"] == NEXT_SHA and second["run_id"] == 42
    assert len(set(fixture.state()["pushes"])) == 2
    assert fixture.lock.joinpath("pid").read_text() == str(os.getpid())


def preflight_and_claims(fixture):
    fixture.prompt.write_text("# no needs\n")
    fixture.launch("missing-needs", 8, "no needs block")
    assert not list(fixture.claims.iterdir())
    fixture.prompt.write_text(NEEDS)
    fixture.wip.write_text("one|/one$\ntwo|/two$\nthree|/three$")
    fixture.launch("wip", 4, "D-WIP3")
    fixture.wip.write_text("one|/product$\ntwo|/two$\nthree|/three$\n")
    fixture.launch("other-unit-wip", 4, "D-WIP3")
    fixture.wip.write_text("fixture-missing-design|/product$\n")
    fixture.launch("design", 6, "D-DESIGN1")
    fixture.wip.write_text("console|/product$\n")
    args, _ = fixture.invocation("holder", cloud=False)
    args[5] = "8"
    with subprocess.Popen(
        args, env=fixture.env, stdout=subprocess.DEVNULL,
    ) as holder:
        try:
            for _ in range(500):
                if any(fixture.claims.glob("*/pid")):
                    break
                time.sleep(0.01)
            else:
                raise AssertionError("local fixture never acquired a claim")
            fixture.launch("active-claim", 3, "already claimed")
        finally:
            holder.terminate()
            holder.wait(timeout=5)
    key = hashlib.sha1(f"{fixture.product}|{fixture.prompt}".encode())
    claim = fixture.claims / key.hexdigest()[:16]
    claim.mkdir()
    fixture.launch("claim-without-pid", 3, "already claimed")
    with subprocess.Popen(["true"]) as exited:
        exited.wait()
        claim.joinpath("pid").write_text(str(exited.pid))
    fixture.update(product=NEXT_SHA)
    fixture.launch("moved-ref", 9, "product ref")
    assert not claim.exists()
    fixture.launch("moved-checkout", 9, "checkout", sha=NEXT_SHA)
    fixture.update(product=PRODUCT_SHA, desk=NEXT_SHA)
    fixture.launch("untrusted-desk-topic", 9, "trusted desk topic")
    assert not fixture.state()["pushes"]
    assert not list(fixture.claims.iterdir())


def caller_state(fixture):
    alternate = fixture.root / "caller-state"
    alternate.mkdir()
    alternate.joinpath("wip-units.txt").write_text("console|/product$\n")
    return {"DS_LAUNCH_STATE_DIR": str(alternate)}


def test_caller_state_cannot_bypass_wip(fixture):
    fixture.wip.write_text("one|/one$\ntwo|/two$\nthree|/three$\n")
    alternate = caller_state(fixture)
    assert fixture.launch("caller-state-wip", 4, "D-WIP3", **alternate) is None
    assert fixture.launch("caller-wip-exemption", 4, "D-WIP3", **alternate,
                          DS_WIP_EXEMPT="caller-supplied exemption") is None
    assert fixture.launch("caller-state-mac-wip", 4, "D-WIP3", cloud=False,
                          **alternate) is None
    assert not Path(alternate["DS_LAUNCH_STATE_DIR"], "claims").exists()
    assert not list(fixture.claims.iterdir())
    assert fixture.state()["pushes"] == []


def test_caller_state_cannot_bypass_claim(fixture):
    key = hashlib.sha1(f"{fixture.product}|{fixture.prompt}".encode())
    claim = fixture.claims / key.hexdigest()[:16]
    claim.mkdir()
    pid = str(os.getpid())
    claim.joinpath("pid").write_text(pid)
    alternate = caller_state(fixture)
    for route, cloud in (("cloud", True), ("mac", False)):
        assert fixture.launch(f"caller-state-{route}-claim", 3,
                              f"already claimed by pid {pid}", cloud=cloud,
                              **alternate) is None
    assert not Path(alternate["DS_LAUNCH_STATE_DIR"], "claims").exists()
    assert list(fixture.claims.iterdir()) == [claim]
    assert claim.joinpath("pid").read_text() == pid
    assert fixture.state()["pushes"] == []


def test_hosted_refuses_foreign_unit_claim(fixture):
    claim = fixture.claims / "unit-console"
    claim.mkdir()
    owner = claim / "owner.txt"
    owner.write_text("Foreign console owner | in progress\n")
    assert fixture.launch("unit-claim", 3, "unit console already claimed",
                          **caller_state(fixture)) is None
    assert list(fixture.claims.iterdir()) == [claim]
    assert owner.read_text() == "Foreign console owner | in progress\n"
    assert fixture.state()["pushes"] == []


def test_hosted_uses_installed_policy(fixture):
    preflight = fixture.root / "preflight.sh"
    preflight.rename(preflight.with_suffix(".held"))
    assert fixture.launch("installed-preflight", 8, str(preflight)) is None
    preflight.with_suffix(".held").rename(preflight)
    for unit in ("console", "cloud-verification-dispatch"):
        note = fixture.root / "desk-main/docs/designs" / f"{unit}.md"
        note.rename(note.with_suffix(".held"))
        result = fixture.launch(f"installed-design-{unit}", 6, str(note))
        assert result is None
        note.with_suffix(".held").rename(note)
    assert not list(fixture.claims.iterdir())
    assert fixture.state()["pushes"] == []


def reconcile_and_receipts(fixture):
    fixture.update(uncertain=True, visible=False)
    pending = fixture.launch("uncertain-push", 75, "pending")
    assert pending["run_id"] is None
    fixture.launch("hidden-run", 75, "pending")
    assert len(fixture.state()["pushes"]) == 1
    fixture.update(visible=True, status="in_progress", result=None)
    running = fixture.launch("running", 75, "pending")
    assert running["status"] == "in_progress" and running["run_id"] == 41
    fixture.update(visible=True, run_sha=NEXT_SHA)
    fixture.launch("wrong-run", 9, "run identity")
    fixture.update(
        run_sha=DESK_SHA, status="completed", product=NEXT_SHA,
        result="failure",
        outcomes=["success", "failure", "skipped", "skipped"],
    )
    failed = fixture.launch("failed-run", 1, "failure")
    assert failed["run_id"] == 41
    assert failed["url"].endswith("/actions/runs/41")
    assert failed["commands"]["dependencies"]["conclusion"] == "failure"
    assert failed["commands"]["console-tests"]["conclusion"] == "skipped"
    assert len(fixture.state()["pushes"]) == 1
    duplicate = fixture.launch("repeated-run", 1, "failure")
    assert duplicate == failed
    assert len(fixture.state()["pushes"]) == 1

    fixture.update(result="success")
    fixture.launch("incomplete-success", 1, "incomplete command evidence")

    fixture.update(
        local=NEXT_SHA, parallel=True, uncertain=False, result="success",
        outcomes=["success"] * len(COMMANDS),
    )
    left, left_receipt = fixture.invocation("parallel-left")
    right, right_receipt = fixture.invocation("parallel-right")
    other_prompt = fixture.root / "other-pilot.md"
    other_prompt.write_text(NEEDS)
    right[3] = str(other_prompt)
    options = dict(env=fixture.env, stdout=subprocess.PIPE, text=True)
    with (subprocess.Popen(left, **options) as first,
          subprocess.Popen(right, **options) as second):
        for job in (first, second):
            output, _ = job.communicate(timeout=15)
            assert job.returncode == 0, output
    receipt = json.loads(left_receipt.read_text())
    assert receipt == json.loads(right_receipt.read_text())
    assert receipt["run_id"] == 42
    assert len(list(fixture.root.glob("pusher-*"))) == 2
    assert len(fixture.state()["pushes"]) == 2


if __name__ == "__main__":
    if sys.argv[1] == "fake-host":
        sys.argv = sys.argv[2:]
        fake_host()
    elif sys.argv[1] == "stage":
        print(stage(Path(sys.argv[2])))
    else:
        case = sys.argv[1]
        tests = {
            "overlap": [overlap],
            "preflight-and-claims": [
                preflight_and_claims, test_caller_state_cannot_bypass_wip,
                test_caller_state_cannot_bypass_claim,
                test_hosted_refuses_foreign_unit_claim,
                test_hosted_uses_installed_policy,
            ],
            "reconcile-and-receipts": [reconcile_and_receipts],
            "caller-state-wip": [test_caller_state_cannot_bypass_wip],
            "caller-state-claim": [test_caller_state_cannot_bypass_claim],
            "foreign-unit-claim": [test_hosted_refuses_foreign_unit_claim],
            "installed-policy": [test_hosted_uses_installed_policy],
        }[case]
        for test in tests:
            with TemporaryDirectory(prefix=f"{case}-") as directory:
                test(Fixture(Path(directory)))
            if test.__name__.replace("_", "-") != case:
                print(f"PASS {test.__name__}")
        print(f"PASS {case}")
