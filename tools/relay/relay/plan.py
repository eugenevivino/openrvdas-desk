"""Content-addressed piece/module jobs and immediate compatible batches."""
from __future__ import annotations
import copy
import hashlib
import json
import math
import re
from pathlib import Path
from collections import defaultdict
from .store import _normalize as normalize_job_spec


def digest(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(raw.encode()).hexdigest()


def load_plan(path):
    path = Path(path).resolve()
    plan = json.loads(path.read_text())
    if not isinstance(plan, dict):
        raise ValueError("plan must be an object")
    workspace = plan.get("workspace", ".")
    if not isinstance(workspace, str) or not workspace:
        raise ValueError("workspace must be a path string")
    plan["workspace"] = str((path.parent / workspace).resolve())
    validate(plan)
    return plan


def validate(plan):
    def name(s):
        if not isinstance(s, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,79}", s):
            raise ValueError(f"invalid identifier: {s!r}")
    if not isinstance(plan, dict):
        raise ValueError("plan must be an object")
    if type(plan.get("schema")) is not int or plan["schema"] != 1:
        raise ValueError("schema must be 1")
    name(plan.get("project"))
    for key in ("policy_version", "environment_id"):
        if not isinstance(plan.get(key), str) or not plan[key].strip():
            raise ValueError(f"{key} is required")
    if not isinstance(plan.get("workspace"), str) or not Path(plan["workspace"]).is_dir():
        raise ValueError("workspace must exist")
    caps = plan.get("capacities", {})
    if not isinstance(caps, dict):
        raise ValueError("capacities must be an object")
    for k, n in caps.items():
        name(k)
        if type(n) is not int or n < 1:
            raise ValueError("capacities must be positive integers")
    if type(plan.get("max_parallel", 4)) is not int or plan.get("max_parallel", 4) < 1:
        raise ValueError("max_parallel must be a positive integer")
    adapters = plan.get("adapters", {})
    if not isinstance(adapters, dict) or not adapters:
        raise ValueError("adapters required")
    for k, a in adapters.items():
        name(k)
        if not isinstance(a, dict):
            raise ValueError(f"{k}: adapter must be an object")
        argv = a.get("command")
        if not isinstance(argv, list) or not argv or not argv[0] or any(not isinstance(x, str) or "\0" in x for x in argv):
            raise ValueError(f"{k}: command must be an argv array")
        if not isinstance(a.get("version"), str) or not a["version"].strip():
            raise ValueError(f"{k}: adapter version required")
        if not isinstance(a.get("cwd", "."), str) or not a.get("cwd", "."):
            raise ValueError(f"{k}: cwd must be a path string")
        t = a.get("timeout_s", 600)
        if type(t) not in (int, float) or not math.isfinite(t) or t <= 0:
            raise ValueError(f"{k}: invalid timeout")
        if type(a.get("max_attempts", 1)) is not int or not 1 <= a.get("max_attempts", 1) <= 20:
            raise ValueError("max_attempts must be 1..20")
        if not isinstance(a.get("resources", {}), dict):
            raise ValueError(f"{k}: resources must be an object")
        for r, n in a.get("resources", {}).items():
            if r not in caps or type(n) is not int or not 1 <= n <= caps[r]:
                raise ValueError(f"{k}: impossible or undeclared resource {r}")
        # Check every adapter, including the dynamically materialized batch
        # adapter, against the same schema the store will enforce before writes.
        normalize_job_spec(_job(plan, "validation", "piece", k, [], {}))
    pieces, modules = plan.get("pieces", []), plan.get("modules", [])
    if not isinstance(pieces, list) or not isinstance(modules, list) or not modules:
        raise ValueError("at least one module required")
    pids, mids = set(), set()
    for p in pieces:
        if not isinstance(p, dict):
            raise ValueError("pieces must be objects")
        name(p.get("id"))
        if p["id"] in pids or p.get("adapter") not in adapters:
            raise ValueError("duplicate piece or unknown adapter")
        pids.add(p["id"])
        if not isinstance(p.get("identity"), dict) or not p["identity"]:
            raise ValueError("each piece needs immutable source identity")
        if not isinstance(p.get("inputs", {}), dict):
            raise ValueError("piece inputs must be an object")
        actor = adapters[p["adapter"]].get("actor")
        if not isinstance(actor, str) or not actor.strip():
            raise ValueError("piece adapter must name its author actor")
    for m in modules:
        if not isinstance(m, dict):
            raise ValueError("modules must be objects")
        name(m.get("id"))
        if m["id"] in mids:
            raise ValueError("duplicate module")
        mids.add(m["id"])
        if not isinstance(m.get("pieces"), list) or not m["pieces"] or any(not isinstance(p, str) for p in m["pieces"]) or not set(m["pieces"]) <= pids or len(set(m["pieces"])) != len(m["pieces"]):
            raise ValueError("module must name distinct known pieces")
        if not isinstance(m.get("inputs", {}), dict):
            raise ValueError("module inputs must be an object")
        if not isinstance(m.get("compatibility_key", "default"), str) or not m.get("compatibility_key", "default"):
            raise ValueError("compatibility_key must be a nonempty string")
        dependencies = m.get("depends_on", [])
        if not isinstance(dependencies, list) or any(not isinstance(d, str) for d in dependencies) or len(set(dependencies)) != len(dependencies):
            raise ValueError("depends_on must name distinct modules")
        for stage in ("assemble", "test", "review"):
            if m.get(stage) not in adapters or not adapters[m[stage]].get("receipt_required", True):
                raise ValueError(f"module {m['id']} needs receipt-producing {stage} adapter")
        author, reviewer = adapters[m["assemble"]].get("actor"), adapters[m["review"]].get("actor")
        if not isinstance(author, str) or not author.strip() or not isinstance(reviewer, str) or not reviewer.strip() or author == reviewer:
            raise ValueError("assembly/review must name distinct actors")
        if any(adapters[p["adapter"]].get("actor") == reviewer for p in pieces if p["id"] in m["pieces"]):
            raise ValueError("reviewer cannot be the configured piece author")
    if any(not set(m.get("depends_on", [])) <= mids for m in modules):
        raise ValueError("unknown module dependency")
    batch = plan.get("batch", {})
    if not isinstance(batch, dict) or not isinstance(batch.get("inputs", {}), dict):
        raise ValueError("batch and batch inputs must be objects")
    if batch.get("adapter") not in adapters:
        raise ValueError("batch adapter required")
    a = adapters[batch["adapter"]]
    if not a.get("receipt_required", True) or a.get("resources", {}).get("integration") != 1 or caps.get("integration") != 1:
        raise ValueError("batch needs evidence receipts and singleton integration resource")
    if type(batch.get("max_size", 5)) is not int or batch.get("max_size", 5) < 1:
        raise ValueError("batch max_size must be positive")


def _job(plan, logical, kind, adapter, deps, inputs, module=None):
    a = plan["adapters"][adapter]
    spec = dict(kind=kind, deps=deps, command=a["command"],
                cwd=str((Path(plan["workspace"]) / a.get("cwd", ".")).resolve()),
                inputs={**copy.deepcopy(inputs), "policy_version": plan["policy_version"],
                        "environment_id": plan["environment_id"], "adapter_version": a["version"],
                        "actor": a.get("actor")}, resources=a.get("resources", {}),
                timeout_s=a.get("timeout_s", 600), max_attempts=a.get("max_attempts", 1),
                retry_exit_codes=a.get("retry_exit_codes", []),
                approval_required=a.get("approval_required", False),
                receipt_required=a.get("receipt_required", True), priority=a.get("priority", 0))
    if module is not None:
        spec["module"] = module
    spec["id"] = f"{plan['project']}.{kind}.{logical}.{digest(spec)[:16]}"
    return spec


def compile_plan(plan):
    validate(plan)
    jobs, pieces, modules = [], {}, {}
    for p in plan["pieces"]:
        inputs = {**p.get("inputs", {}), "piece_id": p["id"], "identity": p["identity"]}
        spec = _job(plan, p["id"], "piece", p["adapter"], [], inputs)
        pieces[p["id"]] = spec["id"]
        jobs.append(spec)
    remaining = list(plan["modules"])
    while remaining:
        progress = False
        for m in remaining[:]:
            if any(p not in modules for p in m.get("depends_on", [])):
                continue
            inputs = {**m.get("inputs", {}), "module": m["id"],
                      "required_pieces": m["pieces"], "acceptance": m.get("acceptance", {}),
                      "compatibility_key": m.get("compatibility_key", "default")}
            deps = [pieces[p] for p in m["pieces"]] + [modules[p]["review"] for p in m.get("depends_on", [])]
            assembly = _job(plan, m["id"], "assemble", m["assemble"], deps, inputs, m["id"])
            test = _job(plan, m["id"], "test", m["test"], [assembly["id"]], inputs, m["id"])
            review = _job(plan, m["id"], "review", m["review"], [assembly["id"], test["id"]], inputs, m["id"])
            jobs.extend([assembly, test, review])
            modules[m["id"]] = {"assemble": assembly["id"], "test": test["id"], "review": review["id"]}
            remaining.remove(m)
            progress = True
        if not progress:
            raise ValueError("module dependency cycle")
    for spec in jobs:
        normalize_job_spec(spec)
    return jobs, modules


def submit_plan(store, plan):
    jobs, modules = compile_plan(plan)
    for spec in jobs:
        store.submit(spec)
    return modules


def _batch_spec(plan, members, key):
    inputs = {**plan["batch"].get("inputs", {}), "members": members,
              "compatibility_key": key,
              "integration_mode": plan["batch"].get("integration_mode", "test_only")}
    return _job(plan, digest(members)[:12], "batch", plan["batch"]["adapter"],
                [member["review_job"] for member in members], inputs)


def _batch_matches_plan(plan, row):
    """Historical integration evidence is valid only for this integration spec."""
    spec = row["spec"]
    if spec["kind"] != "batch":
        return False
    members = spec["inputs"].get("members", [])
    if not members:
        return False
    expected = _batch_spec(plan, members, spec["inputs"].get("compatibility_key", "default"))
    return row["id"] == expected["id"] and spec == expected


def batch_callback(plan):
    _, modules = compile_plan(plan)
    def materialize(store):
        rows = {j["id"]: j for j in store.jobs()}
        # Leave newly reviewed modules unreserved while a batch is queued or
        # using the train. They can accumulate during necessary execution and
        # form a larger next batch without any artificial collection delay.
        if any(j["spec"]["kind"] == "batch" and j["state"] in
               {"queued", "approval", "running", "uncertain"} for j in rows.values()):
            return 0
        reserved = set()
        for row in rows.values():
            if _batch_matches_plan(plan, row):
                # An unsuccessful batch retains its members until diagnosed.
                reserved.update(m["review_job"] for m in row["spec"]["inputs"].get("members", []))
        eligible = defaultdict(list)
        for m in plan["modules"]:
            ids = modules[m["id"]]
            if rows.get(ids["review"], {}).get("state") == "passed" and ids["review"] not in reserved:
                eligible[m.get("compatibility_key", "default")].append({
                    "module": m["id"], "review_job": ids["review"],
                    "assembly_job": ids["assemble"], "test_job": ids["test"]})
        # Oldest eligible group first; no permanent starvation by module name.
        def group_age(item):
            return min(rows[m["review_job"]].get("finished_at") or 0 for m in item[1])
        for key, members in sorted(eligible.items(), key=group_age):
            members.sort(key=lambda m: m["module"])
            maximum = plan["batch"].get("max_size", 5)
            chosen = members[:maximum]
            spec = _batch_spec(plan, chosen, key)
            return int(store.submit(spec))
        return 0
    return materialize


def module_status(store, plan):
    _, mapping = compile_plan(plan)
    rows = {j["id"]: j for j in store.jobs()}
    result = []
    for m in plan["modules"]:
        ids = mapping[m["id"]]
        state, reason = "ready_for_batch", ""
        for stage in ("assemble", "test", "review"):
            row = rows.get(ids[stage], {})
            if row.get("state") != "passed":
                state, reason = f"{stage}:{row.get('state', 'not_submitted')}", row.get("reason", "")
                break
        for batch in rows.values():
            if _batch_matches_plan(plan, batch) and any(x["review_job"] == ids["review"] for x in batch["spec"]["inputs"].get("members", [])):
                state, reason = "batch:" + batch["state"], batch.get("reason", "")
                if batch["state"] == "passed":
                    state = "batch_tested" if batch["spec"]["inputs"].get("integration_mode") == "test_only" else "integration_adapter_passed"
                break
        result.append({"module": m["id"], "state": state, "reason": reason})
    return result
