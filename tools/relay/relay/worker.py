"""Detached, durable supervisor for one immutable Relay attempt.

Adapters are trusted programs. This module validates receipt shape/provenance,
not the truth of adapter-specific engineering assertions.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import select
import signal
import subprocess
import sys
import tempfile
import time
from typing import Any

HEARTBEAT_INTERVAL_S = 0.5
TERMINATE_GRACE_S = 2.0
OUTPUT_LIMIT_BYTES = 8 * 1024 * 1024


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def input_digest(value: dict) -> str:
    return hashlib.sha256(canonical_json({k: v for k, v in value.items()
                                         if k != "input_digest"})).hexdigest()


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix="." + path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
        try:
            directory_fd = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        except OSError:
            pass  # Some supported filesystems cannot fsync directories.
    finally:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return value


def validate_receipt(receipt: Any, digest: str, attempt_dir: Path) -> dict:
    if not isinstance(receipt, dict):
        raise ValueError("adapter receipt must be a JSON object")
    if type(receipt.get("schema")) is not int or receipt["schema"] != 1:
        raise ValueError("adapter receipt schema must be 1")
    if receipt.get("outcome") not in ("pass", "fail", "blocked"):
        raise ValueError("adapter receipt outcome must be pass, fail, or blocked")
    if receipt.get("input_digest") != digest:
        raise ValueError("adapter receipt input_digest does not match this attempt")
    if not isinstance(receipt.get("summary"), str):
        raise ValueError("adapter receipt summary must be a string")
    if not isinstance(receipt.get("data"), dict):
        raise ValueError("adapter receipt data must be an object")
    evidence = receipt.get("evidence")
    if not isinstance(evidence, list):
        raise ValueError("adapter receipt evidence must be a list")
    for entry in evidence:
        if not isinstance(entry, str) or not entry:
            raise ValueError("evidence entries must be nonempty path strings")
        path = Path(entry)
        if not path.is_absolute():
            path = attempt_dir / path
        if not path.exists():
            raise ValueError(f"receipt evidence does not exist: {entry}")
    return receipt


def _signal_group(pid: int, sig: int) -> None:
    try:
        os.killpg(pid, sig)
    except ProcessLookupError:
        pass


def supervise(input_path: Path) -> int:
    input_path = input_path.resolve()
    attempt_dir = input_path.parent
    request = read_json(input_path)
    digest = input_digest(request)
    if request.get("schema") != 1 or request.get("input_digest") != digest:
        raise ValueError("input schema or digest is invalid")
    spec = request["spec"]
    command = spec["command"]
    if not isinstance(command, list) or not command or any(
            not isinstance(part, str) or "\x00" in part for part in command):
        raise ValueError("command must be a nonempty argv list")
    cwd = Path(spec["cwd"])
    if not cwd.is_absolute() or not cwd.is_dir():
        raise ValueError("cwd must be an existing absolute directory")
    timeout = spec["timeout_s"]
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not (
            math.isfinite(timeout) and timeout > 0):
        raise ValueError("timeout_s must be finite and positive")

    cancelled = False
    timed_out = False
    child: subprocess.Popen | None = None
    started = time.time()
    start_monotonic = time.monotonic()
    termination_started: float | None = None
    killed = False
    receipt = None
    receipt_error = None
    error = None
    returncode = None
    output_bytes = 0
    output_limited = False
    output_eof = False

    def cancel(_signum: int, _frame: Any) -> None:
        nonlocal cancelled
        cancelled = True

    signal.signal(signal.SIGTERM, cancel)
    signal.signal(signal.SIGINT, cancel)

    def heartbeat() -> None:
        atomic_json(attempt_dir / "worker-heartbeat.json", {
            "schema": 1, "job_id": request["job_id"], "attempt": request["attempt"],
            "token": request["token"], "input_digest": digest,
            "supervisor_pid": os.getpid(), "child_pid": child.pid if child else None,
            "input_path": str(input_path), "timestamp": time.time(),
        })

    env = os.environ.copy()
    env.update(RELAY_INPUT_FILE=str(input_path),
               RELAY_RESULT_FILE=str(attempt_dir / "adapter-result.json"),
               RELAY_ATTEMPT_DIR=str(attempt_dir))
    try:
        heartbeat()
        with (attempt_dir / "output.log").open("ab", buffering=0) as output:
            output_bytes = output.tell()

            def capture():
                nonlocal output_bytes, output_limited, output_eof, error
                try:
                    data = os.read(child.stdout.fileno(), 65536)
                except BlockingIOError:
                    return False
                if not data:
                    output_eof = True
                    return False
                retained = data[:max(0, OUTPUT_LIMIT_BYTES - output_bytes)]
                output.write(retained)
                output_bytes += len(retained)
                if len(retained) != len(data):
                    output_limited = True
                    error = f"adapter output exceeded {OUTPUT_LIMIT_BYTES} bytes"
                return True

            if not cancelled:
                child = subprocess.Popen(command, cwd=str(cwd), env=env, shell=False,
                                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                         stdin=subprocess.DEVNULL, start_new_session=True)
                os.set_blocking(child.stdout.fileno(), False)
            next_heartbeat = 0.0
            while child is not None:
                now = time.monotonic()
                if now >= next_heartbeat:
                    heartbeat()
                    next_heartbeat = now + HEARTBEAT_INTERVAL_S
                if now - start_monotonic >= timeout:
                    timed_out = True
                if output_eof:
                    time.sleep(0.05)
                    readable = []
                else:
                    readable, _, _ = select.select([child.stdout], [], [], 0.05)
                if readable:
                    capture()
                if (cancelled or timed_out or output_limited) and termination_started is None:
                    _signal_group(child.pid, signal.SIGTERM)
                    termination_started = now
                if termination_started is not None and not killed and (
                        now - termination_started >= TERMINATE_GRACE_S):
                    _signal_group(child.pid, signal.SIGKILL)
                    killed = True
                returncode = child.poll()
                # Finish cancellation cleanup even if the immediate child exits first:
                # grandchildren in its process group may ignore SIGTERM.
                if returncode is not None:
                    # Adapters may not leave background children consuming an
                    # execution slot after completion. This is our own group.
                    # Descendants deliberately creating new sessions require
                    # stronger external containment.
                    _signal_group(child.pid, signal.SIGKILL)
                    # Keep the final buffered bytes from a short-lived child;
                    # bounded capture also detects overflow on its final write.
                    while capture():
                        pass
                    break
    except BaseException as exc:
        error = f"{type(exc).__name__}: {exc}"
        if child is not None:
            _signal_group(child.pid, signal.SIGKILL)
            try:
                returncode = child.wait(timeout=TERMINATE_GRACE_S)
            except subprocess.TimeoutExpired:
                returncode = None
    finally:
        if child is not None and child.stdout is not None:
            child.stdout.close()
        receipt_path = attempt_dir / "adapter-result.json"
        if receipt_path.exists():
            try:
                receipt = validate_receipt(read_json(receipt_path), digest, attempt_dir)
            except (OSError, ValueError, TypeError) as exc:
                receipt_error = f"{type(exc).__name__}: {exc}"
        elif spec.get("receipt_required", True):
            receipt_error = "required adapter-result.json is missing"
        result = {
            "schema": 1, "job_id": request["job_id"], "attempt": request["attempt"],
            "token": request["token"], "supervisor_pid": os.getpid(),
            "input_digest": digest, "returncode": returncode, "timed_out": timed_out,
            "cancelled": cancelled, "started_at": started, "finished_at": time.time(),
            "receipt": receipt, "receipt_error": receipt_error, "error": error,
            "output_bytes": output_bytes, "output_limited": output_limited,
        }
        atomic_json(attempt_dir / "worker-result.json", result)
    return 0


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("usage: python -m relay.worker INPUT_PATH", file=sys.stderr)
        return 2
    try:
        return supervise(Path(args[0]))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        # The controller quarantines an attempt without a trustworthy terminal file.
        print(f"relay worker refused input: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
