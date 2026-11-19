"""Hosted pilot verification. The desk launcher holds the job claim."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time

DESK = "eugenevivino/openrvdas-desk"
PRODUCT = "eugenevivino/openrvdas"
DESK_WEB = f"https://github.com/{DESK}"
DESK_REF = "refs/heads/deepsignal/cloud-verification-dispatch"
PRODUCT_REF = "refs/heads/deepsignal/console-supervised-pilot"
WORKFLOW = ".github/workflows/cloud-verification.yml"
SHA = re.compile(r"[0-9a-f]{40}")
COMMANDS = ("pin", "dependencies", "console-tests", "console-types")


class Refused(Exception):
    """A submission or its evidence failed validation."""


class Unavailable(Exception):
    """A requested Git or GitHub operation did not return usable data."""


def url(repo):
    return f"https://github.com/{repo}.git"


def command(*args):
    env = os.environ | {"GIT_TERMINAL_PROMPT": "0", "GIT_OPTIONAL_LOCKS": "0"}
    try:
        return subprocess.run(
            args, capture_output=True, text=True, check=True, timeout=25,
            env=env,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError) as exc:
        raise Unavailable(f"{args[0]} did not return usable data") from exc


def checkout(path, repo, sha):
    git = ("git", "-C", str(path))
    if (command(*git, "remote", "get-url", "origin") != url(repo)
            or command(*git, "rev-parse", "--show-toplevel") != str(path)
            or command(*git, "rev-parse", "HEAD") != sha):
        raise Refused(f"{repo} checkout does not match the pin")


def remote_ref(repo, ref):
    response = command("git", "ls-remote", "--refs", url(repo), ref)
    if not response:
        return None
    sha, separator, reported_ref = response.partition("\t")
    if not separator or reported_ref != ref or not SHA.fullmatch(sha):
        raise Refused(f"unexpected hosted ref response for {ref}")
    return sha


def api(path, collection):
    result = command(
        "gh", "api", "--hostname", "github.com", "--paginate", "--slurp",
        f"repos/{DESK}/actions/{path}",
    )
    try:
        pages = json.loads(result)
        rows = [item for page in pages for item in page[collection]]
        if any(not isinstance(item, dict) for item in rows):
            raise ValueError("invalid GitHub row")
        return rows
    except (ValueError, TypeError, KeyError) as exc:
        raise Unavailable("GitHub Actions response could not be read") from exc


def matching_run(ref, desk_sha):
    title = f"Pilot cloud verification ({ref})"
    runs = api(
        f"runs?event=push&head_sha={desk_sha}&per_page=100", "workflow_runs",
    )
    matches = [
        run for run in runs
        if run.get("display_title") == title
        and str(run.get("path", "")).split("@", 1)[0] == WORKFLOW
    ]
    if not matches:
        return None
    if len(matches) != 1:
        raise Refused("more than one Actions run has the exact request ref")
    run = matches[0]
    run_id = run.get("id")
    if (run.get("head_sha") != desk_sha or run.get("event") != "push"
            or run.get("run_attempt") != 1
            or type(run_id) is not int or run_id < 1):
        raise Refused("Actions run identity differs from the original request")
    return run


def outcomes(run_id):
    jobs = api(f"runs/{run_id}/attempts/1/jobs?per_page=100", "jobs")
    pilot = [job for job in jobs if job.get("name") == "pilot"]
    if len(pilot) > 1:
        raise Refused("more than one pilot job in the original run")
    steps = pilot[0].get("steps", []) if pilot else []
    return {
        step["name"]: {field: step.get(field) for field in
                       ("status", "conclusion", "started_at", "completed_at")}
        for step in steps if step["name"] in COMMANDS
    }


def write_receipt(path, receipt):
    with tempfile.NamedTemporaryFile(
        mode="w", dir=path.parent, delete=False,
    ) as output:
        partial = Path(output.name)
        try:
            json.dump(receipt, output, indent=2, sort_keys=True)
            output.write("\n")
            output.close()
            partial.replace(path)
        finally:
            partial.unlink(missing_ok=True)


def log(message):
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    print(f"{timestamp} {message}", flush=True)


def dispatch(desk, product, path, maxwait, desk_sha, product_sha):
    if not SHA.fullmatch(desk_sha) or not SHA.fullmatch(product_sha):
        raise Refused("both pins must be full lowercase commit SHAs")
    if not re.fullmatch(r"[0-9]{1,5}", maxwait):
        raise Refused("max wait must be seconds (0 to 99999)")
    deadline = time.monotonic() + int(maxwait)
    checkout(desk, DESK, desk_sha)
    if command("git", "-C", str(desk), "status", "--porcelain",
               "--untracked-files=all"):
        raise Refused("trusted desk checkout must be clean")
    checkout(product, PRODUCT, product_sha)

    ref = f"refs/tags/cloud-verification/v1/{product_sha}-{desk_sha}"
    receipt = {
        "desk_repo": DESK, "desk_ref": DESK_REF, "desk_sha": desk_sha,
        "workflow": WORKFLOW, "request_ref": ref,
        "product_repo": PRODUCT, "product_ref": PRODUCT_REF,
        "product_sha": product_sha,
        "run_id": None, "url": None, "status": "pending",
        "conclusion": None, "commands": {},
    }

    tag = remote_ref(DESK, ref)
    if tag and tag != desk_sha:
        raise Refused("request tag does not match the desk pin")
    if not tag:
        # Check for a prior run even if someone removed the request tag.
        if matching_run(ref, desk_sha):
            raise Refused("request tag is missing for an existing run")
        if remote_ref(DESK, DESK_REF) != desk_sha:
            raise Refused("trusted desk topic does not point at the desk pin")
        if remote_ref(PRODUCT, PRODUCT_REF) != product_sha:
            raise Refused("product ref moved or is missing")
        write_receipt(path, receipt)
        try:
            # An ordinary push only creates tags. An identical concurrent
            # push is a no-op or fails.
            command("git", "-C", str(desk), "push", "--no-follow-tags",
                    "--recurse-submodules=no", url(DESK), f"{desk_sha}:{ref}")
        except Unavailable:
            log(f"checking tag after uncertain push response for {ref}")
            try:
                tag = remote_ref(DESK, ref)
            except Unavailable:
                tag = None
            if tag is None:
                log(f"pending {ref}; repeat the same submission to reconcile")
                return 75
            if tag != desk_sha:
                raise Refused("request tag does not match the desk pin")
        log(f"request tag confirmed {ref}")
    else:
        log(f"reconciling {ref}")

    while True:
        try:
            run = matching_run(ref, desk_sha)
            if run:
                run_id = run["id"]
                receipt.update(
                    run_id=run_id, url=f"{DESK_WEB}/actions/runs/{run_id}",
                    status=run.get("status"), created_at=run.get("created_at"),
                    run_started_at=run.get("run_started_at"),
                )
                commands = outcomes(run_id)
                conclusion = run.get("conclusion")
                receipt.update(commands=commands, conclusion=conclusion)
                if receipt["status"] == "completed" and conclusion:
                    write_receipt(path, receipt)
                    log(f"run {run_id} {conclusion} {receipt['url']}")
                    if conclusion != "success":
                        return 1
                    if all(
                        commands.get(name, {}).get("conclusion") == "success"
                        for name in COMMANDS
                    ):
                        return 0
                    log("run has incomplete command evidence")
                    return 1
        except Unavailable as exc:
            log(str(exc))
        write_receipt(path, receipt)
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            log(f"pending {ref}; repeat the same submission to reconcile")
            return 75
        time.sleep(min(10, remaining))


def main(desk, product, receipt, maxwait, desk_sha, product_sha):
    try:
        return dispatch(
            Path(desk).resolve(), Path(product).resolve(), Path(receipt),
            maxwait, desk_sha, product_sha,
        )
    except (Refused, Unavailable, OSError) as exc:
        log(f"NOT launched or verified: {exc}")
        return 9


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
