"""Deterministic local dispatcher with durable, independently supervised jobs."""
from __future__ import annotations

from collections import Counter
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import shlex
import signal
import subprocess
import sys
import time
import uuid
from typing import Any

from .worker import atomic_json, canonical_json, input_digest, read_json, validate_receipt

HEARTBEAT_MAX_AGE_S = 5.0
STARTUP_GRACE_S = 5.0
LEASE_S = 10.0
ACTIVE_STATES = {"running", "uncertain"}
TERMINAL_STATES = {"passed", "failed", "blocked", "cancelled"}


def _validate_capacities(capacities: dict, rows: list[dict]) -> None:
    if not isinstance(capacities, dict):
        raise ValueError("capacities must be a mapping")
    for name, capacity in capacities.items():
        if not isinstance(name, str) or not name or type(capacity) is not int or capacity < 1:
            raise ValueError("resource capacities must be positive integers with nonempty names")
    for row in rows:
        if row["state"] in TERMINAL_STATES:
            continue
        for name, requested in row["spec"].get("resources", {}).items():
            if name not in capacities:
                raise ValueError(f"job {row['id']} requires undeclared resource {name!r}")
            if type(requested) is not int or requested < 1 or requested > capacities[name]:
                raise ValueError(f"job {row['id']} requests invalid or excessive {name!r} capacity")


def _verified_process(pid: Any, input_path: Path) -> bool:
    if type(pid) is not int or pid <= 1:
        return False
    try:
        # Linux exposes argv boundaries, including paths containing spaces.
        proc_argv = Path(f"/proc/{pid}/cmdline")
        if proc_argv.exists():
            args = [os.fsdecode(part) for part in proc_argv.read_bytes().split(b"\x00") if part]
            return len(args) >= 4 and args[-3:] == ["-m", "relay.worker", str(input_path)]
        response = subprocess.run(["ps", "-p", str(pid), "-o", "command="],
                                  stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                  text=True, timeout=2, check=False)
        if response.returncode != 0:
            return False
        command = response.stdout.strip()
        args = shlex.split(command)
        exact_argv = len(args) >= 4 and args[-3:] == ["-m", "relay.worker", str(input_path)]
        # macOS ps can print spaces without quoting. The input is the final
        # argument, so require the exact complete module-and-path suffix.
        exact_suffix = command.endswith(" -m relay.worker " + str(input_path))
        return exact_argv or exact_suffix
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return False


def _matching_input(row: dict, attempt_dir: Path) -> dict:
    value = read_json(attempt_dir / "input.json")
    if (value.get("schema") != 1 or value.get("job_id") != row["id"]
            or value.get("token") != row["token"]
            or value.get("attempt") != row["attempt"]
            or value.get("input_digest") != input_digest(value)
            or canonical_json(value.get("spec")) != canonical_json(row["spec"])):
        raise ValueError("attempt input does not match the immutable claimed job")
    return value


def _terminal_result(row: dict, attempt_dir: Path, request: dict) -> tuple[str, dict, str]:
    result = read_json(attempt_dir / "worker-result.json")
    if (type(result.get("schema")) is not int or result["schema"] != 1
            or result.get("job_id") != row["id"]
            or result.get("token") != row["token"]
            or result.get("attempt") != row["attempt"]
            or result.get("input_digest") != request["input_digest"]):
        raise ValueError("terminal result does not match the current fenced attempt")
    if type(result.get("timed_out")) is not bool or type(result.get("cancelled")) is not bool:
        raise ValueError("terminal result has invalid cancellation/timeout fields")
    rc = result.get("returncode")
    if rc is not None and type(rc) is not int:
        raise ValueError("terminal returncode must be an integer or null")
    for name in ("started_at", "finished_at"):
        stamp = result.get(name)
        if isinstance(stamp, bool) or not isinstance(stamp, (int, float)) or not math.isfinite(stamp):
            raise ValueError(f"terminal result has invalid {name}")
    if result["finished_at"] < result["started_at"]:
        raise ValueError("terminal result ends before it starts")
    receipt = result.get("receipt")
    receipt_error = result.get("receipt_error")
    if receipt is not None:
        try:
            validate_receipt(receipt, request["input_digest"], attempt_dir)
        except (ValueError, OSError, TypeError) as exc:
            receipt_error = str(exc)
    elif row["spec"].get("receipt_required", True):
        receipt_error = receipt_error or "required adapter receipt is missing"
    result["receipt_error"] = receipt_error
    if result["cancelled"]:
        return "cancelled", result, "worker acknowledged cancellation and terminated its child group"
    if result["timed_out"]:
        return "failed", result, "worker exceeded its configured timeout"
    if result.get("error"):
        return "failed", result, str(result["error"])
    if receipt_error:
        return "failed", result, f"invalid adapter receipt: {receipt_error}"
    if receipt is not None and receipt["outcome"] == "blocked":
        return "blocked", result, receipt["summary"]
    if rc != 0:
        return "failed", result, f"adapter exited with code {rc}"
    if receipt is not None and receipt["outcome"] == "fail":
        return "failed", result, receipt["summary"]
    return "passed", result, receipt["summary"] if receipt else "adapter exited successfully; receipt not required"


def _uncertain(store: Any, row: dict, reason: str) -> None:
    if row["state"] != "uncertain":
        store.mark_uncertain(row["id"], row["token"], reason)


def _observe(store: Any, row: dict, local_workers: dict, cancelled_tokens: set) -> bool:
    """Import completion first; otherwise verify liveness. Never reclaim a lease."""
    if not row.get("attempt_dir"):
        _uncertain(store, row, "claimed attempt has no durable runtime directory; execution status unknown")
        return False
    attempt_dir = Path(row["attempt_dir"]).resolve()
    input_path = attempt_dir / "input.json"
    try:
        request = _matching_input(row, attempt_dir)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        _uncertain(store, row, f"cannot verify durable attempt input: {exc}")
        return False
    result_path = attempt_dir / "worker-result.json"
    if result_path.exists():
        try:
            state, result, reason = _terminal_result(row, attempt_dir, request)
        except (OSError, ValueError, TypeError, KeyError) as exc:
            _uncertain(store, row, f"cannot verify terminal result: {exc}")
            return False
        store.finish(row["id"], row["token"], row["owner"], state, result, reason, retry_on_exit=True)
        return False

    key = (row["id"], row["token"])
    local = local_workers.get(key)
    pid = row.get("pid")
    local_alive = local is not None and local.poll() is None and local.pid == pid
    heartbeat = None
    try:
        heartbeat = read_json(attempt_dir / "worker-heartbeat.json")
        if (heartbeat.get("schema") != 1 or heartbeat.get("job_id") != row["id"]
                or heartbeat.get("token") != row["token"]
                or heartbeat.get("attempt") != row["attempt"]
                or heartbeat.get("input_digest") != request["input_digest"]
                or heartbeat.get("input_path") != str(input_path)):
            heartbeat = None
    except (OSError, ValueError, TypeError):
        heartbeat = None
    stamp = heartbeat.get("timestamp") if heartbeat else None
    fresh = (type(stamp) in (int, float) and math.isfinite(stamp)
             and -2 <= time.time() - stamp <= HEARTBEAT_MAX_AGE_S)
    if fresh:
        heartbeat_pid = heartbeat.get("supervisor_pid")
        live = (local_alive and heartbeat_pid == pid) or _verified_process(heartbeat_pid, input_path)
        if live:
            if pid != heartbeat_pid:
                store.set_runtime(row["id"], row["token"], row["owner"], heartbeat_pid, str(attempt_dir))
                pid = heartbeat_pid
            store.heartbeat(row["id"], row["token"], row["owner"], LEASE_S)
            if row.get("cancel_requested") and key not in cancelled_tokens:
                # A verified supervisor owns cancellation of its own child process group.
                try:
                    os.kill(pid, signal.SIGTERM)
                    cancelled_tokens.add(key)
                    store.event("cancel_signal", row["id"], {"token": row["token"], "pid": pid})
                except ProcessLookupError:
                    pass  # Completion may be published between observation and signal.
            return True
    # Give a newly spawned interpreter time to publish its first heartbeat.
    age = time.time() - (row.get("started_at") or 0)
    if age < STARTUP_GRACE_S and (local_alive or _verified_process(pid, input_path)):
        return True
    if result_path.exists():
        return _observe(store, row, local_workers, cancelled_tokens)
    _uncertain(store, row, "missing/stale heartbeat or unverifiable supervisor; no duplicate execution authorized")
    return False


def _launch(store: Any, row: dict, state_dir: Path, local_workers: dict) -> None:
    key = (row["id"], row["token"])
    slug = hashlib.sha256(row["id"].encode("utf-8")).hexdigest()[:20]
    attempt_dir = state_dir / "attempts" / slug / f"{row['attempt']:06d}-{row['token']:06d}"
    attempt_dir.mkdir(parents=True, exist_ok=False)
    request = {
        "schema": 1, "job_id": row["id"], "attempt": row["attempt"], "token": row["token"],
        "spec": row["spec"],
        "dependencies": {dep: store.get(dep)["result"] for dep in row["spec"].get("deps", [])},
    }
    request["input_digest"] = input_digest(request)
    input_path = attempt_dir / "input.json"
    atomic_json(input_path, request)
    if not store.set_runtime(row["id"], row["token"], row["owner"], 0, str(attempt_dir)):
        return
    env = os.environ.copy()
    package_root = str(Path(__file__).resolve().parent.parent)
    env["PYTHONPATH"] = package_root + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    try:
        with (attempt_dir / "supervisor.log").open("ab", buffering=0) as output:
            process = subprocess.Popen([sys.executable, "-m", "relay.worker", str(input_path)],
                                       cwd=package_root, env=env, stdin=subprocess.DEVNULL,
                                       stdout=output, stderr=subprocess.STDOUT,
                                       start_new_session=True, close_fds=True)
        local_workers[key] = process
        if not store.set_runtime(row["id"], row["token"], row["owner"], process.pid, str(attempt_dir)):
            store.event("runtime_record_refused", row["id"], {"token": row["token"], "pid": process.pid})
    except OSError as exc:
        # Popen raised before returning a child: no worker has been launched.
        store.finish(row["id"], row["token"], row["owner"], "failed",
                     {"error": str(exc), "launch_failed": True}, f"worker launch failed: {exc}")


def _summary(store: Any) -> dict:
    rows = store.jobs()
    counts = dict(sorted(Counter(row["state"] for row in rows).items()))
    return {"counts": counts, "total": len(rows),
            "passed": counts.get("passed", 0),
            "complete": all(row["state"] == "passed" for row in rows),
            "unresolved": [{"id": row["id"], "state": row["state"], "reason": row.get("reason", "")}
                           for row in rows if row["state"] != "passed"]}


def run(store: Any, state_dir: str | Path, capacities: dict,
        max_parallel: int = 4, poll_s: float = 0.1, drain: bool = True,
        batch_callback: Any = None) -> dict:
    """Run until quiescent (drain) or until interrupted (persistent mode).

    The advisory lock protects one controller per state directory. Detached
    supervisors retain responsibility for their own timeout/cancellation after
    this controller exits. Uncertain attempts retain their resource reservations.
    """
    if type(max_parallel) is not int or max_parallel < 1:
        raise ValueError("max_parallel must be a positive integer")
    if isinstance(poll_s, bool) or not isinstance(poll_s, (int, float)) or not (
            math.isfinite(poll_s) and 0 < poll_s <= 60):
        raise ValueError("poll_s must be positive and at most 60 seconds")
    state_dir = Path(state_dir).resolve()
    state_dir.mkdir(parents=True, exist_ok=True)
    lock = (state_dir / "controller.lock").open("a+")
    try:
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError("another Relay controller owns this state directory") from exc
        owner = f"controller-{os.getpid()}-{uuid.uuid4().hex}"
        lock.seek(0)
        lock.truncate()
        lock.write(owner + "\n")
        lock.flush()
        local_workers: dict = {}
        cancelled_tokens: set = set()
        store.event("controller_started", data={"owner": owner, "state_dir": str(state_dir)})
        try:
            while True:
                alive = False
                for row in store.jobs():
                    if row["state"] in ACTIVE_STATES:
                        alive = _observe(store, row, local_workers, cancelled_tokens) or alive
                # Reap only supervisors this controller started; never kill them here.
                for key, process in list(local_workers.items()):
                    if process.poll() is None:
                        row = store.get(key[0])
                        if row["state"] in TERMINAL_STATES:
                            try:
                                process.wait(timeout=0.5)
                            except subprocess.TimeoutExpired:
                                pass
                    if process.poll() is not None:
                        del local_workers[key]
                store.propagate_blocked()
                if batch_callback is not None:
                    batch_callback(store)
                rows = store.jobs()
                _validate_capacities(capacities, rows)
                used: Counter = Counter()
                occupied = 0
                for row in rows:
                    if row["state"] in ACTIVE_STATES:
                        occupied += 1
                        used.update(row["spec"].get("resources", {}))
                states = {row["id"]: row["state"] for row in rows}
                queued = sorted((row for row in rows if row["state"] == "queued"),
                                key=lambda row: (-row["spec"].get("priority", 0), row["created_at"], row["id"]))
                launched = False
                for row in queued:
                    if occupied >= max_parallel:
                        break
                    if not all(states.get(dep) == "passed" for dep in row["spec"].get("deps", [])):
                        continue
                    resources = row["spec"].get("resources", {})
                    if any(used[name] + amount > capacities[name] for name, amount in resources.items()):
                        continue
                    claimed = store.claim(row["id"], owner, LEASE_S)
                    if claimed is None:
                        continue
                    try:
                        _launch(store, claimed, state_dir, local_workers)
                    except (OSError, ValueError, KeyError, TypeError) as exc:
                        # A partial launch remains quarantined; unrelated jobs
                        # can proceed without risking duplicate execution.
                        store.mark_uncertain(claimed["id"], claimed["token"],
                                             f"could not complete launch bookkeeping: {exc}")
                    occupied += 1
                    used.update(resources)
                    launched = True
                if drain and not alive and not launched:
                    return _summary(store)
                time.sleep(poll_s)
        finally:
            store.event("controller_stopped", data={"owner": owner, "supervisors_detached": True})
    finally:
        lock.close()
