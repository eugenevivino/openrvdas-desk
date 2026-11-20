"""Command-line control and observable queue latency."""
from __future__ import annotations
import argparse
from collections import Counter
from contextlib import contextmanager
import fcntl
import json
import math
from pathlib import Path
import platform
import statistics
import sys
import time

from .plan import load_plan, compile_plan, submit_plan, batch_callback, module_status, digest
from .store import Store
from .worker import atomic_json


def make_demo_plan():
    root = Path(__file__).resolve().parent.parent
    adapter = root / "examples" / "demo_adapter.py"
    import hashlib
    version = hashlib.sha256(adapter.read_bytes()).hexdigest()
    adapters = {}
    for stage in ("piece", "assemble", "test", "review", "batch"):
        adapters[stage] = {"command": [sys.executable, str(adapter), stage],
            "version": version, "actor": "fixture-reviewer" if stage == "review" else "fixture-builder",
            "timeout_s": 10, "resources": {"integration": 1} if stage == "batch" else {"cpu": 1}}
    pieces = [{"id": f"{module}-{piece}", "adapter": "piece",
               "identity": {"fixture": version, "module": module, "piece": piece},
               "inputs": {"module": module, "piece": piece}}
              for module, names in (("math", ["add", "multiply"]), ("display", ["render", "unwrap"]))
              for piece in names]
    modules = [{"id": module, "pieces": [p["id"] for p in pieces if p["inputs"]["module"] == module],
                "assemble": "assemble", "test": "test", "review": "review",
                "acceptance": {"fixture_only": True}, "compatibility_key": "fixture-python-v1"}
               for module in ("math", "display")]
    return {"schema": 1, "project": "demo", "workspace": str(root),
            "policy_version": "fixture-only-v1", "environment_id": f"python-{platform.python_version()}",
            "capacities": {"cpu": 4, "integration": 1}, "max_parallel": 4,
            "adapters": adapters, "pieces": pieces, "modules": modules,
            "batch": {"adapter": "batch", "max_size": 5, "integration_mode": "test_only"}}


@contextmanager
def plan_lock(state):
    """Serialize plan publication with CLI runs, including a watcher's lifetime."""
    state = Path(state)
    state.mkdir(parents=True, exist_ok=True)
    with (state / "plan.lock").open("a+") as lock:
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError("another Relay command owns plan activation") from exc
        yield


def install_plan(plan, state):
    # Complete validation before creating state or submitting the first job.
    jobs, _ = compile_plan(plan)
    state = Path(state)
    with plan_lock(state), (state / "controller.lock").open("a+") as lock:
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError("another Relay controller owns this state directory") from exc
        path = state / "plan.json"
        store = Store(state / "queue.sqlite3")
        rows = store.jobs()
        if path.exists():
            old = json.loads(path.read_text())
            if digest(old) != digest(plan) and any(j["state"] in {"queued", "approval", "running", "uncertain"} for j in rows):
                raise ValueError("finish or explicitly cancel pending work before replacing the active plan; use a separate state directory for another project")
        existing = {row["id"]: row["spec"] for row in rows}
        for spec in jobs:
            if spec["id"] in existing and existing[spec["id"]] != spec:
                raise ValueError(f"job ID has a different immutable spec: {spec['id']}")
        # Publish before making any new job runnable. If interrupted during
        # submissions, the next run replays the published plan idempotently.
        atomic_json(path, plan)
        for spec in jobs:
            store.submit(spec)
    return store


def metrics(store):
    rows = store.jobs()
    by_id = {row["id"]: row for row in rows}

    def distribution(values):
        values = sorted(values)
        return {"samples": len(values), "p50": statistics.median(values) if values else None,
                "p95": values[min(len(values)-1, max(0, math.ceil(len(values)*0.95)-1))] if values else None,
                "max": max(values) if values else None}

    def timestamp(value):
        return type(value) in (int, float) and math.isfinite(value)

    handoffs = []
    for row in rows:
        result = row.get("result") or {}
        dependencies = row["spec"]["deps"]
        start = result.get("started_at")
        if not dependencies or row.get("finished_at") is None or not timestamp(start) or not timestamp(result.get("finished_at")):
            continue
        finishes = [(by_id.get(dep, {}).get("result") or {}).get("finished_at") for dep in dependencies]
        if all(timestamp(finish) for finish in finishes):
            gap = start - max(finishes)
            if gap >= 0:
                handoffs.append(gap)
    waits = sorted(max(0, j["started_at"] - j["ready_at"]) for j in rows
                   if j.get("ready_at") is not None and j.get("started_at") is not None)
    age = [max(0, time.time() - j["ready_at"]) for j in rows if j["state"] == "queued" and j.get("ready_at") is not None]
    duration = {}
    for j in rows:
        if j.get("started_at") is not None and j.get("finished_at") is not None:
            duration.setdefault(j["spec"]["kind"], []).append(max(0, j["finished_at"] - j["started_at"]))
    return {"job_counts": dict(Counter(j["state"] for j in rows)),
            "eligible_to_claim_s": distribution(waits),
            "dependency_finish_to_worker_start_s": distribution(handoffs),
            "oldest_ready_wait_s": max(age) if age else 0,
            "stage_wall_s": {k: {"count": len(v), "total": sum(v), "median": statistics.median(v)} for k, v in duration.items()}}


def active_plan_complete(store, plan, statuses=None):
    """Historical superseded failures remain visible without failing a new plan."""
    jobs, _ = compile_plan(plan)
    rows = {row["id"]: row for row in store.jobs()}
    statuses = module_status(store, plan) if statuses is None else statuses
    return (all(rows.get(spec["id"], {}).get("state") == "passed" for spec in jobs)
            and all(row["state"] in {"batch_tested", "integration_adapter_passed"} for row in statuses))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Relay: deterministic piece-to-module-to-batch coordination")
    parser.add_argument("--state", default="relay-state", help="durable local state directory (one per project)")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("demo", help="run four fixture pieces through two modules and integration")
    p = commands.add_parser("validate"); p.add_argument("plan")
    p = commands.add_parser("submit"); p.add_argument("plan")
    p = commands.add_parser("run"); p.add_argument("--watch", action="store_true"); p.add_argument("--poll", type=float, default=0.1)
    p = commands.add_parser("status"); p.add_argument("--json", action="store_true")
    p = commands.add_parser("events"); p.add_argument("--limit", type=int, default=30)
    p = commands.add_parser("approve"); p.add_argument("job"); p.add_argument("--actor", required=True); p.add_argument("--note", required=True)
    p = commands.add_parser("cancel"); p.add_argument("job")
    p = commands.add_parser("retry"); p.add_argument("job"); p.add_argument("--note", required=True)
    args = parser.parse_args(argv)
    state = Path(args.state).resolve()
    try:
        if args.command == "validate":
            jobs, modules = compile_plan(load_plan(args.plan))
            print(json.dumps({"valid": True, "jobs_before_batch": len(jobs), "modules": list(modules)}, indent=2))
            return 0
        if args.command == "submit":
            plan = load_plan(args.plan)
            store = install_plan(plan, state)
            print(json.dumps({"submitted": len(store.jobs()), "state": str(state)}, indent=2))
            return 0
        if args.command == "demo":
            plan = make_demo_plan()
            store = install_plan(plan, state)
        else:
            if not (state / "plan.json").exists():
                raise ValueError("no submitted plan in this state directory; use submit or demo first")
            plan = load_plan(state / "plan.json")
            store = Store(state / "queue.sqlite3")
        if args.command in ("run", "demo"):
            from .engine import run
            started = time.monotonic()
            with plan_lock(state):
                # Reload under the activation lock: a submit may have completed
                # after the preliminary read above. Heal interrupted installs.
                plan = load_plan(state / "plan.json")
                submit_plan(store, plan)
                summary = run(store, state, plan["capacities"], max_parallel=plan.get("max_parallel", 4),
                              poll_s=getattr(args, "poll", 0.1), drain=not getattr(args, "watch", False),
                              batch_callback=batch_callback(plan))
            summary.update(elapsed_s=time.monotonic()-started, modules=module_status(store, plan), metrics=metrics(store))
            summary["history_complete"] = summary["complete"]
            summary["complete"] = active_plan_complete(store, plan, summary["modules"])
            if args.command == "demo":
                summary["fixture_only"] = True
                summary["production_modules_qualified"] = 0
                atomic_json(state / "demo-report.json", summary)
            print(json.dumps(summary, indent=2))
            return 0 if summary["complete"] else 2
        if args.command == "status":
            data = {"modules": module_status(store, plan), "metrics": metrics(store),
                    "jobs": [{k: j.get(k) for k in ("id", "state", "attempt", "reason", "attempt_dir")} for j in store.jobs()]}
            if args.json:
                print(json.dumps(data, indent=2))
            else:
                print("MODULE\tSTATE\tREASON")
                for row in data["modules"]:
                    print(f"{row['module']}\t{row['state']}\t{row['reason']}")
                print("\nJOB\tSTATE\tATTEMPT\tREASON")
                for row in data["jobs"]:
                    print(f"{row['id']}\t{row['state']}\t{row['attempt']}\t{row['reason']}")
                print("\n" + json.dumps(data["metrics"], indent=2))
        elif args.command == "events":
            print(json.dumps(store.events(args.limit), indent=2))
        elif args.command == "approve":
            store.approve(args.job, args.actor, args.note)
        elif args.command == "cancel":
            store.request_cancel(args.job)
        elif args.command == "retry":
            store.retry(args.job, args.note)
        return 0
    except (ValueError, KeyError, OSError, RuntimeError) as exc:
        print(f"relay: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("Controller stopped. Claimed workers remain supervised; rerun to recover their receipts.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
