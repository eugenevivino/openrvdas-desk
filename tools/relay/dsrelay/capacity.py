"""Staged client for Kalon's sole capacity authority. No production activation.

Normal transports execute status only; mutating calls are reported as STAGED.
The disposable transport exists for protocol tests against a pinned local fake.
The owner hook supports a held prelaunch fence and prelaunch retirement only.
Actual process ownership/absence reporters are deliberately not invented: an
attempted start or unknown process identity remains quarantined indefinitely.
This is not an allocator, worker launcher, or installation mechanism.
"""
from contextlib import contextmanager
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time

from .common import owned


class CapacityError(RuntimeError):
    """Messages intentionally exclude authority output and capabilities."""


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode()


def redacted(value, secrets=()):
    secrets = tuple(secrets)
    if isinstance(value, dict) and isinstance(value.get('token'), str):
        secrets += (value['token'],)
    if isinstance(value, dict):
        return {k: redacted(v, secrets) for k, v in value.items() if k != 'token'}
    if isinstance(value, list):
        return [redacted(v, secrets) for v in value]
    if isinstance(value, str):
        for secret in secrets:
            if secret:
                value = value.replace(secret, '[redacted]')
    return value


def boot_identity():
    try:
        if sys.platform == 'linux':
            return Path('/proc/sys/kernel/random/boot_id').read_text().strip()
        if sys.platform == 'darwin':
            value = subprocess.check_output(['/usr/sbin/sysctl', '-n', 'kern.boottime'],
                                            stderr=subprocess.DEVNULL, timeout=2)
            return hashlib.sha256(value).hexdigest()
    except (OSError, subprocess.SubprocessError):
        pass
    return None


def private_directory(path):
    path = owned(path)
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    if path.stat().st_uid != os.getuid() or path.stat().st_mode & 0o077:
        raise CapacityError('capacity state must be private to its owner')
    return path


def write_private(path, value):
    fd, temp = tempfile.mkstemp(prefix='.record-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(canonical(value) + b'\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


class Transport:
    """Explicit local/approved SSH argv. Never pass tokens through argv."""

    def __init__(self, argv, timeout_s=10):
        if not isinstance(argv, (list, tuple)) or not argv or any(
                not isinstance(a, str) or not a or '\0' in a for a in argv):
            raise CapacityError('authority argv must be explicit')
        self.argv = list(argv)
        self.timeout_s = timeout_s
        self._disposable = None

    @classmethod
    def disposable(cls, root, script):
        """Tests only: no SSH and no production authority configuration."""
        root = private_directory(root)
        script = owned(script)
        if not script.is_relative_to(root) or not script.is_file():
            raise CapacityError('fake authority must be inside its disposable root')
        result = cls([sys.executable, str(script)])
        result._disposable = (script, hashlib.sha256(script.read_bytes()).hexdigest())
        return result

    def call(self, command, payload):
        if command not in {'request', 'claim', 'start', 'heartbeat', 'reconcile', 'status'}:
            raise CapacityError('unsupported capacity operation')
        if command != 'status' and self._disposable is None:
            return {'status': 'STAGED', 'operation': command,
                    'reason': 'production capacity activation is not implemented'}
        if self._disposable is not None:
            script, expected = self._disposable
            if hashlib.sha256(script.read_bytes()).hexdigest() != expected:
                raise CapacityError('disposable authority identity changed')
        try:
            response = subprocess.run(self.argv + [command], input=canonical(payload),
                                      stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                      timeout=self.timeout_s, check=False, shell=False)
            if response.returncode != 0 or len(response.stdout) > 65536:
                raise CapacityError('authority refused or returned invalid output')
            result = json.loads(response.stdout)
            if not isinstance(result, dict) or not isinstance(result.get('status'), str):
                raise ValueError('reply shape')
            return result
        except (OSError, subprocess.TimeoutExpired, ValueError):
            raise CapacityError('authority response unavailable or ambiguous') from None


class Client:
    def __init__(self, root, transport, project='deepsignal', clock=time.monotonic,
                 boot=boot_identity):
        if project != 'deepsignal':
            raise CapacityError('this hook owns DeepSignal jobs only')
        self.root = private_directory(root)
        self.transport = transport
        self.project = project
        self.clock = clock
        self.boot = boot
        self._held = {}

    def directory(self, job):
        if not isinstance(job, str) or not job:
            raise CapacityError('stable job identity required')
        name = hashlib.sha256(canonical([self.project, job])).hexdigest()
        return private_directory(self.root / name)

    @contextmanager
    def guard(self, job):
        """Hold this guard across start. No production spawn right is offered."""
        directory = self.directory(job)
        fd = os.open(directory / 'owner.lock', os.O_CREAT | os.O_RDWR, 0o600)
        acquired = False
        try:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise CapacityError('another local owner holds this job') from None
            self._held[job] = threading.get_ident()
            acquired = True
            yield
        finally:
            if acquired:
                self._held.pop(job, None)
            os.close(fd)

    def _read(self, job):
        path = self.directory(job) / 'record.json'
        if path.stat().st_mode & 0o077:
            raise CapacityError('private job record permissions changed')
        return json.loads(path.read_text())

    def _write(self, job, record):
        write_private(self.directory(job) / 'record.json', record)

    def request(self, job, host, work_class, limits, retry_of=None, *,
                local_locks=(), scratch_reservations=()):
        payload = {'project': self.project, 'job': job, 'host': host,
                   'work_class': work_class, 'limits': limits}
        if retry_of is not None:
            payload['retry_of'] = retry_of
        reservations = [str(owned(p)) for p in tuple(local_locks) + tuple(scratch_reservations)]
        with self.guard(job):
            path = self.directory(job) / 'record.json'
            if path.exists():
                record = self._read(job)
                if record['request'] != payload or record['reservations'] != reservations:
                    raise CapacityError('immutable request changed')
                return {'status': 'LOCAL_EXISTS', 'phase': record['phase']}
            record = {'schema': 1, 'request': payload, 'phase': 'request_pending',
                      'start_attempted': False, 'reservations': reservations}
            self._write(job, record)
            result = self.transport.call('request', payload)
            if result['status'] not in {'STAGED', 'QUEUED', 'ALREADY_OWNED', 'CLOSED'}:
                raise CapacityError('unexpected request outcome')
            record['phase'] = 'staged' if result['status'] == 'STAGED' else 'requested'
            self._write(job, record)
            return redacted(result)

    def claim(self, job):
        with self.guard(job):
            record = self._read(job)
            if record['phase'] == 'staged':
                return {'status': 'STAGED', 'operation': 'claim'}
            if record['phase'] != 'requested':
                raise CapacityError('claim is already owned, closed or ambiguous')
            record['phase'] = 'claim_pending'
            self._write(job, record)
            before = self.clock()
            result = self.transport.call('claim', {'project': self.project, 'job': job})
            status = result['status']
            if status == 'WAIT':
                record['phase'] = 'requested'
            elif status == 'GRANTED':
                duration = result.get('expires_in_s')
                if (type(result.get('fence')) is not int or result['fence'] < 1
                        or not isinstance(result.get('token'), str) or not result['token']
                        or type(duration) not in (int, float) or not math.isfinite(duration)
                        or duration <= 0 or any(result.get(k) != record['request'][k]
                                               for k in ('project', 'job', 'host'))):
                    raise CapacityError('invalid grant identity or freshness')
                record.update(phase='claimed', lease={k: result[k] for k in
                              ('project', 'job', 'host', 'fence', 'token')},
                              deadline=before + duration, monotonic_claimed=before,
                              wall_claimed=time.time(), boot_id=self.boot())
            else:
                record['phase'] = 'quarantined'
            self._write(job, record)
            return redacted(result)

    def start(self, job):
        if self._held.get(job) != threading.get_ident():
            raise CapacityError('exclusive local guard required across start')
        record = self._read(job)
        if record['phase'] == 'staged':
            return {'status': 'STAGED', 'operation': 'start'}
        now = self.clock()
        if (record['phase'] != 'claimed' or record['start_attempted']
                or now < record['monotonic_claimed'] or now >= record['deadline']
                or not record.get('boot_id') or record['boot_id'] != self.boot()
                or abs((time.time() - record['wall_claimed']) -
                       (now - record['monotonic_claimed'])) > 2):
            raise CapacityError('launch right absent, expired or freshness uncertain')
        record.update(phase='start_pending', start_attempted=True)
        self._write(job, record)
        result = self.transport.call('start', record['lease'])
        record['phase'] = 'start_acknowledged' if result['status'] == 'STARTED' else 'quarantined'
        self._write(job, record)
        # Even a disposable STARTED response is not permission to spawn here.
        return {**redacted(result, [record['lease']['token']]), 'production_spawn_permitted': False}

    def heartbeat(self, job):
        with self.guard(job):
            record = self._read(job)
            if record['phase'] == 'staged':
                return {'status': 'STAGED', 'operation': 'heartbeat'}
            if record['phase'] != 'start_acknowledged':
                raise CapacityError('no acknowledged start to heartbeat')
            return redacted(self.transport.call('heartbeat', record['lease']), [record['lease']['token']])

    def retire_prelaunch(self, job):
        """No worker-supplied truth flags. Inspect every registered reservation.

        Started/ambiguous attempts cannot be retired by this staged hook; they
        need a future reviewed host process identity and group-absence reporter.
        """
        with self.guard(job):
            record = self._read(job)
            if record['start_attempted'] or record['phase'] != 'claimed':
                raise CapacityError('process ownership unknown; reservation quarantined')
            paths = [owned(p) for p in record['reservations']]
            if any(os.path.lexists(p) for p in paths):
                raise CapacityError('local locks or scratch reservations still exist')
            lease = record['lease']
            archive = {'schema': 1, 'identity': redacted(lease),
                       'no_start_attempted': True, 'verified_absent_paths': [str(p) for p in paths]}
            archive_sha = hashlib.sha256(canonical(archive)).hexdigest()
            receipt = {'schema': 1, **redacted(lease), 'outcome': 'cancelled',
                       'launch_right_retired': True, 'process_group_gone': True,
                       'locks_released': True, 'scratch_released': True, 'spawned': False,
                       'archive_sha256': archive_sha}
            # Closing the right is durable before any reconciliation request.
            record.update(phase='retired', archive=archive, receipt=receipt,
                          evidence_sha256=hashlib.sha256(canonical(receipt)).hexdigest())
            self._write(job, record)
            return redacted(receipt)

    def reconcile(self, job):
        with self.guard(job):
            record = self._read(job)
            if record['phase'] != 'retired':
                raise CapacityError('no independently retired local launch right')
            payload = {**redacted(record['lease']), 'evidence_sha256': record['evidence_sha256']}
            return redacted(self.transport.call('reconcile', payload), [record['lease']['token']])

    def owner_hook(self, request):
        """Read-only hook data for disposable integration tests; not registered."""
        job = request.get('job')
        record = self._read(job)
        lease = record.get('lease', {})
        if any(request.get(k) != lease.get(k) for k in ('project', 'job', 'host', 'fence')):
            raise CapacityError('owner fence mismatch')
        base = {'host': request['host'], 'nonce': request['nonce'],
                'project': self.project, 'job': job, 'fence': lease['fence']}
        if request['action'] == 'retire' and record['phase'] == 'retired':
            if hashlib.sha256(canonical(record['archive'])).hexdigest() != record['receipt']['archive_sha256']:
                raise CapacityError('retirement archive changed')
            if (hashlib.sha256(canonical(record['receipt'])).hexdigest() != record['evidence_sha256']
                    or record['archive']['identity'] != redacted(lease)
                    or record['start_attempted']):
                raise CapacityError('retirement identity or evidence changed')
            if any(os.path.lexists(p) for p in record['archive']['verified_absent_paths']):
                raise CapacityError('retired reservation reappeared')
            return {**base, 'receipt': record['receipt'], 'evidence_sha256': record['evidence_sha256']}
        # Start/heartbeat require genuine host process identity and ownership
        # reporters. Never claim exclusivity from a worker-provided boolean/PID.
        raise CapacityError('host process identity reporter not qualified; quarantine')

    def status(self, host=None):
        return redacted(self.transport.call('status', {} if host is None else {'host': host}))
