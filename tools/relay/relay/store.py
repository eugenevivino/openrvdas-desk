"""Durable fenced job state. Lease expiry never authorizes duplicate execution."""
from __future__ import annotations

import json
import math
import os
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path


def _json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _positive(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be a finite positive number")
    return float(value)


def _normalize(spec):
    if not isinstance(spec, dict):
        raise ValueError("spec must be an object")
    value = json.loads(_json(spec))
    if not isinstance(value.get("id"), str) or not value["id"].strip():
        raise ValueError("id must be a nonempty string")
    if value.get("kind") not in {"piece", "assemble", "test", "review", "batch"}:
        raise ValueError("invalid kind")
    deps = value.get("deps")
    if not isinstance(deps, list) or any(not isinstance(d, str) or not d for d in deps):
        raise ValueError("deps must be job IDs")
    if len(set(deps)) != len(deps) or value["id"] in deps:
        raise ValueError("dependencies must be unique and cannot include self")
    argv = value.get("command")
    if not isinstance(argv, list) or not argv or any(not isinstance(a, str) or "\x00" in a for a in argv) or not argv[0]:
        raise ValueError("command must be a nonempty argv list")
    if not isinstance(value.get("cwd"), str) or not os.path.isabs(value["cwd"]):
        raise ValueError("cwd must be absolute")
    if not isinstance(value.get("inputs"), dict):
        raise ValueError("inputs must be an object")
    resources = value.get("resources")
    if not isinstance(resources, dict) or any(not name or isinstance(count, bool) or not isinstance(count, int) or count <= 0 for name, count in resources.items()):
        raise ValueError("resources must map names to positive integers")
    _positive(value.get("timeout_s"), "timeout_s")
    value.setdefault("max_attempts", 1)
    if isinstance(value["max_attempts"], bool) or not isinstance(value["max_attempts"], int) or value["max_attempts"] < 1:
        raise ValueError("max_attempts must be positive")
    value.setdefault("retry_exit_codes", [])
    if not isinstance(value["retry_exit_codes"], list) or any(isinstance(c, bool) or not isinstance(c, int) for c in value["retry_exit_codes"]):
        raise ValueError("retry_exit_codes must be integers")
    for key, default in (("approval_required", False), ("receipt_required", True)):
        value.setdefault(key, default)
        if not isinstance(value[key], bool):
            raise ValueError(f"{key} must be boolean")
    value.setdefault("priority", 0)
    if isinstance(value["priority"], bool) or not isinstance(value["priority"], int):
        raise ValueError("priority must be an integer")
    return value


class Store:
    """One connection per method; atomic claims use BEGIN IMMEDIATE."""

    def __init__(self, db_path):
        if str(db_path) == ":memory:":
            raise ValueError("Store requires a durable filesystem path")
        self.db_path = str(Path(db_path).expanduser().resolve())
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with self._connection() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY, spec TEXT NOT NULL,
                    state TEXT NOT NULL CHECK(state IN ('queued','approval','running','passed','failed','blocked','cancelled','uncertain')),
                    attempt INTEGER NOT NULL DEFAULT 0, token INTEGER NOT NULL DEFAULT 0,
                    owner TEXT, lease_until REAL, pid INTEGER, attempt_dir TEXT,
                    created_at REAL NOT NULL, ready_at REAL, started_at REAL, finished_at REAL,
                    cancel_requested INTEGER NOT NULL DEFAULT 0, result TEXT,
                    reason TEXT NOT NULL DEFAULT '', blocked_from TEXT
                );
                CREATE INDEX IF NOT EXISTS jobs_state_idx ON jobs(state);
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, created_at REAL NOT NULL,
                    kind TEXT NOT NULL, job_id TEXT, data TEXT
                );
            """)

    @contextmanager
    def _connection(self):
        conn = sqlite3.connect(self.db_path, timeout=30, isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout=30000")
        conn.execute("PRAGMA synchronous=FULL")
        try:
            yield conn
        finally:
            conn.close()

    @contextmanager
    def _transaction(self):
        with self._connection() as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                yield conn
            except BaseException:
                conn.rollback()
                raise
            else:
                conn.commit()

    @staticmethod
    def _row(row):
        result = dict(row)
        result["spec"] = json.loads(result["spec"])
        result["result"] = json.loads(result["result"]) if result["result"] is not None else None
        result["cancel_requested"] = bool(result["cancel_requested"])
        result.pop("blocked_from", None)
        return result

    @staticmethod
    def _required(conn, job_id):
        row = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        if row is None:
            raise KeyError(f"unknown job: {job_id}")
        return row

    @staticmethod
    def _event(conn, kind, job_id, data, now=None):
        conn.execute("INSERT INTO events(created_at,kind,job_id,data) VALUES(?,?,?,?)", (time.time() if now is None else now, kind, job_id, _json(data) if data is not None else None))

    @staticmethod
    def _deps_passed(conn, spec):
        for dep in spec["deps"]:
            row = conn.execute("SELECT state FROM jobs WHERE id=?", (dep,)).fetchone()
            if row is None or row["state"] != "passed":
                return False
        return True

    @classmethod
    def _refresh_ready(cls, conn, now):
        for row in conn.execute("SELECT id,spec FROM jobs WHERE state IN ('queued','approval') AND ready_at IS NULL").fetchall():
            if cls._deps_passed(conn, json.loads(row["spec"])):
                conn.execute("UPDATE jobs SET ready_at=? WHERE id=?", (now, row["id"]))

    def submit(self, spec):
        spec = _normalize(spec)
        encoded = _json(spec)
        with self._transaction() as conn:
            previous = conn.execute("SELECT spec FROM jobs WHERE id=?", (spec["id"],)).fetchone()
            if previous is not None:
                if previous["spec"] != encoded:
                    raise ValueError(f"job ID has a different immutable spec: {spec['id']}")
                return False
            now = time.time()
            state = "approval" if spec["approval_required"] else "queued"
            conn.execute("INSERT INTO jobs(id,spec,state,created_at) VALUES(?,?,?,?)", (spec["id"], encoded, state, now))
            self._refresh_ready(conn, now)
            self._event(conn, "submitted", spec["id"], {"state": state}, now)
            return True

    def jobs(self):
        with self._connection() as conn:
            return [self._row(row) for row in conn.execute("SELECT * FROM jobs ORDER BY created_at,id").fetchall()]

    def get(self, job_id):
        with self._connection() as conn:
            return self._row(self._required(conn, job_id))

    def claim(self, job_id, owner, lease_s):
        if not isinstance(owner, str) or not owner.strip():
            raise ValueError("owner must be nonempty")
        lease_s = _positive(lease_s, "lease_s")
        with self._transaction() as conn:
            row = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
            if row is None or row["state"] != "queued" or row["cancel_requested"]:
                return None
            spec = json.loads(row["spec"])
            if row["attempt"] >= spec["max_attempts"] or not self._deps_passed(conn, spec):
                return None
            now = time.time()
            conn.execute("""UPDATE jobs SET state='running',attempt=attempt+1,token=token+1,
                owner=?,lease_until=?,pid=NULL,attempt_dir=NULL,ready_at=COALESCE(ready_at,?),
                started_at=?,finished_at=NULL,result=NULL,reason='',blocked_from=NULL WHERE id=?""", (owner, now + lease_s, now, now, job_id))
            claimed = self._row(self._required(conn, job_id))
            self._event(conn, "claimed", job_id, {"owner": owner, "attempt": claimed["attempt"], "token": claimed["token"]}, now)
            return claimed

    def heartbeat(self, job_id, token, owner, lease_s):
        lease_s = _positive(lease_s, "lease_s")
        with self._transaction() as conn:
            return conn.execute("UPDATE jobs SET lease_until=? WHERE id=? AND token=? AND owner=? AND state IN ('running','uncertain')", (time.time() + lease_s, job_id, token, owner)).rowcount == 1

    def set_runtime(self, job_id, token, owner, pid, attempt_dir):
        # pid=0 records the attempt directory before spawning its supervisor.
        if isinstance(pid, bool) or not isinstance(pid, int) or pid < 0:
            raise ValueError("pid must be a nonnegative integer")
        attempt_dir = os.fspath(attempt_dir)
        if not os.path.isabs(attempt_dir):
            raise ValueError("attempt_dir must be absolute")
        with self._transaction() as conn:
            changed = conn.execute("UPDATE jobs SET pid=?,attempt_dir=? WHERE id=? AND token=? AND owner=? AND state IN ('running','uncertain')", (pid, attempt_dir, job_id, token, owner)).rowcount
            if changed:
                self._event(conn, "runtime_attached", job_id, {"pid": pid, "attempt_dir": attempt_dir, "token": token})
            return changed == 1

    def finish(self, job_id, token, owner, state, result, reason=""):
        if state not in {"passed", "failed", "blocked", "cancelled"}:
            raise ValueError("finish requires a terminal state")
        if result is not None and not isinstance(result, dict):
            raise ValueError("result must be an object or null")
        encoded = _json(result) if result is not None else None
        with self._transaction() as conn:
            row = conn.execute("SELECT * FROM jobs WHERE id=? AND token=? AND owner=? AND state IN ('running','uncertain')", (job_id, token, owner)).fetchone()
            if row is None:
                return False
            if row["cancel_requested"] and state == "passed":
                state, reason = "cancelled", reason or "Cancellation requested before completion was recorded"
            now = time.time()
            conn.execute("UPDATE jobs SET state=?,result=?,reason=?,finished_at=?,lease_until=NULL,blocked_from=NULL WHERE id=?", (state, encoded, reason, now, job_id))
            self._event(conn, "finished", job_id, {"state": state, "token": token, "reason": reason}, now)
            self._refresh_ready(conn, now)
            return True

    def mark_uncertain(self, job_id, token, reason):
        with self._transaction() as conn:
            changed = conn.execute("UPDATE jobs SET state='uncertain',reason=? WHERE id=? AND token=? AND state='running'", (reason, job_id, token)).rowcount
            if changed:
                self._event(conn, "uncertain", job_id, {"token": token, "reason": reason})
            return changed == 1

    def approve(self, job_id, actor, note):
        if not isinstance(actor, str) or not actor.strip():
            raise ValueError("approval requires an actor")
        with self._transaction() as conn:
            row = self._required(conn, job_id)
            if row["state"] != "approval":
                raise ValueError(f"job is not awaiting approval: {job_id} ({row['state']})")
            now = time.time()
            conn.execute("UPDATE jobs SET state='queued',reason='' WHERE id=?", (job_id,))
            self._refresh_ready(conn, now)
            self._event(conn, "approved", job_id, {"actor": actor, "note": note}, now)

    def request_cancel(self, job_id):
        with self._transaction() as conn:
            row = self._required(conn, job_id)
            if row["state"] in {"passed", "failed", "cancelled"} or row["cancel_requested"]:
                return
            now = time.time()
            if row["state"] in {"queued", "approval", "blocked"}:
                conn.execute("UPDATE jobs SET state='cancelled',cancel_requested=1,finished_at=?,reason='Cancelled before execution',blocked_from=NULL WHERE id=?", (now, job_id))
            else:
                conn.execute("UPDATE jobs SET cancel_requested=1 WHERE id=?", (job_id,))
            self._event(conn, "cancel_requested", job_id, {"previous_state": row["state"]}, now)

    def retry(self, job_id, note):
        """Explicit retry. The caller must enforce any automatic retry policy."""
        with self._transaction() as conn:
            row = self._required(conn, job_id)
            if row["state"] != "failed":
                raise ValueError(f"only terminal failed jobs can be retried: {job_id} ({row['state']})")
            if row["attempt"] >= json.loads(row["spec"])["max_attempts"]:
                raise ValueError(f"max_attempts exhausted for {job_id}")
            now = time.time()
            conn.execute("""UPDATE jobs SET state='queued',owner=NULL,lease_until=NULL,pid=NULL,attempt_dir=NULL,
                ready_at=NULL,started_at=NULL,finished_at=NULL,cancel_requested=0,result=NULL,reason='',blocked_from=NULL WHERE id=?""", (job_id,))
            self._refresh_ready(conn, now)
            self._event(conn, "retry_requested", job_id, {"note": note, "completed_attempts": row["attempt"]}, now)

    def propagate_blocked(self):
        """Derive dependency blockage; recover it after explicit upstream retry.

        Adapter-returned blocked states are never automatically cleared.
        Uncertain dependencies are unresolved, not terminal failures.
        Returns the number of newly blocked jobs.
        """
        count = 0
        with self._transaction() as conn:
            now = time.time()
            while True:
                rows = conn.execute("SELECT * FROM jobs ORDER BY created_at,id").fetchall()
                states = {row["id"]: row["state"] for row in rows}
                changed = False
                for row in rows:
                    if row["state"] not in {"queued", "approval"} and not (row["state"] == "blocked" and row["blocked_from"] is not None):
                        continue
                    deps = json.loads(row["spec"])["deps"]
                    blockers = [{"id": dep, "state": states.get(dep)} for dep in deps if states.get(dep) in {"failed", "blocked", "cancelled"}]
                    if blockers and row["state"] in {"queued", "approval"}:
                        reason = "Blocked by dependencies: " + ", ".join(f"{dep['id']} ({dep['state']})" for dep in blockers)
                        conn.execute("UPDATE jobs SET state='blocked',blocked_from=?,reason=?,finished_at=?,ready_at=NULL WHERE id=?", (row["state"], reason, now, row["id"]))
                        self._event(conn, "dependency_blocked", row["id"], {"dependencies": blockers}, now)
                        count += 1
                        changed = True
                    elif not blockers and row["state"] == "blocked" and all(states.get(dep) == "passed" for dep in deps):
                        conn.execute("UPDATE jobs SET state=?,blocked_from=NULL,reason='',finished_at=NULL,ready_at=NULL WHERE id=?", (row["blocked_from"], row["id"]))
                        self._event(conn, "dependency_unblocked", row["id"], {"state": row["blocked_from"]}, now)
                        changed = True
                if not changed:
                    break
            self._refresh_ready(conn, now)
        return count

    def event(self, kind, job_id=None, data=None):
        if not isinstance(kind, str) or not kind:
            raise ValueError("event kind must be nonempty")
        with self._transaction() as conn:
            self._event(conn, kind, job_id, data)

    def events(self, limit=100):
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 0:
            raise ValueError("limit must be a nonnegative integer")
        with self._connection() as conn:
            rows = conn.execute("SELECT * FROM events ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        result = []
        for row in reversed(rows):
            item = dict(row)
            item["data"] = json.loads(item["data"]) if item["data"] is not None else None
            result.append(item)
        return result
