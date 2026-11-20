"""Disposable shadow transport only; no live authority, lease, SSH or worker."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

from dsrelay.capacity import CapacityError, Client, Transport


FAKE = '''import json, pathlib, sys
root=pathlib.Path(__file__).parent
op=sys.argv[-1]
request=json.load(sys.stdin)
with (root/'calls.jsonl').open('a') as f:
 f.write(json.dumps({'operation':op,'has_token':'token' in request})+'\\n')
mode=(root/'mode').read_text() if (root/'mode').exists() else ''
if mode==op+'-lost':
 print('private-test-capability',file=sys.stderr)
 sys.exit(2)
if op=='status': result={'status':'STATUS','reservations':[]}
elif op=='request': result={'status':'QUEUED'}
elif op=='claim':
 result={'status':'WAIT'} if mode=='wait' else {'status':'GRANTED','project':request['project'],'job':request['job'],'host':'macbook','fence':7,'token':'private-test-capability','expires_in_s':30,'echo':'private-test-capability'}
elif op=='start': result={'status':'STARTED','reason':'private-test-capability'}
elif op=='heartbeat': result={'status':'QUARANTINED'}
elif op=='reconcile': result={'status':'CLOSED'}
print(json.dumps(result))
'''


class CapacityTests(unittest.TestCase):
    def setUp(self):
        scratch = Path('/private/tmp/deepsignal/relay-20261120/capacity-tests')
        scratch.mkdir(mode=0o700, parents=True, exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(prefix='capacity-', dir=scratch)
        self.root = Path(self.tmp.name)
        self.script = self.root / 'fake_authority.py'
        self.script.write_text(FAKE)
        self.transport = Transport.disposable(self.root, self.script)
        self.now = 100.0
        self.boot = 'fixture-boot-1'
        self.client = Client(self.root / 'client', self.transport,
                             clock=lambda: self.now, boot=lambda: self.boot)
        self.limits = {'cpu': 1, 'ram_mib': 128, 'disk_mib': 16, 'native_slots': 0}

    def tearDown(self):
        self.tmp.cleanup()

    def request(self, **kwargs):
        return self.client.request('job-1', 'macbook', 'portable', self.limits, **kwargs)

    def claim(self):
        self.request()
        return self.client.claim('job-1')

    def calls(self):
        path = self.root / 'calls.jsonl'
        return [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else []

    def test_normal_transport_stages_mutations_and_only_queries_status(self):
        normal = Client(self.root / 'shadow', Transport([sys.executable, str(self.script)]))
        self.assertEqual(normal.request('x', 'macbook', 'portable', self.limits)['status'], 'STAGED')
        self.assertEqual(normal.claim('x')['status'], 'STAGED')
        with normal.guard('x'):
            self.assertEqual(normal.start('x')['status'], 'STAGED')
        self.assertEqual(normal.heartbeat('x')['status'], 'STAGED')
        self.assertEqual(self.calls(), [])
        self.assertEqual(normal.status()['status'], 'STATUS')
        self.assertEqual([c['operation'] for c in self.calls()], ['status'])

    def test_capability_is_private_and_absent_from_public_results(self):
        result = self.claim()
        self.assertNotIn('private-test-capability', json.dumps(result))
        record = self.client.directory('job-1') / 'record.json'
        self.assertEqual(record.stat().st_mode & 0o777, 0o600)
        self.assertEqual(record.parent.stat().st_mode & 0o777, 0o700)
        self.assertIn('private-test-capability', record.read_text())
        with self.client.guard('job-1'):
            started = self.client.start('job-1')
        self.assertNotIn('private-test-capability', json.dumps(started))
        self.assertFalse(started['production_spawn_permitted'])

    def test_immutable_request_and_duplicate_claim_are_refused(self):
        self.claim()
        with self.assertRaises(CapacityError):
            self.client.request('job-1', 'mini', 'portable', self.limits)
        with self.assertRaises(CapacityError):
            self.client.claim('job-1')
        self.assertEqual([c['operation'] for c in self.calls()], ['request', 'claim'])

    def test_wait_is_retryable_without_new_job_identity(self):
        self.request()
        (self.root / 'mode').write_text('wait')
        self.assertEqual(self.client.claim('job-1')['status'], 'WAIT')
        (self.root / 'mode').unlink()
        self.assertEqual(self.client.claim('job-1')['status'], 'GRANTED')

    def test_lost_claim_reply_never_reclaims(self):
        self.request()
        (self.root / 'mode').write_text('claim-lost')
        with self.assertRaises(CapacityError) as error:
            self.client.claim('job-1')
        self.assertNotIn('private-test-capability', str(error.exception))
        (self.root / 'mode').unlink()
        recovered = Client(self.root / 'client', self.transport)
        with self.assertRaises(CapacityError):
            recovered.claim('job-1')
        self.assertEqual(len([c for c in self.calls() if c['operation'] == 'claim']), 1)

    def test_start_requires_guard_and_is_consumed_exactly_once(self):
        self.claim()
        with self.assertRaises(CapacityError):
            self.client.start('job-1')
        with self.client.guard('job-1'):
            self.client.start('job-1')
            with self.assertRaises(CapacityError):
                self.client.start('job-1')
        self.assertEqual(len([c for c in self.calls() if c['operation'] == 'start']), 1)

    def test_competing_local_owner_cannot_acquire_start_right(self):
        self.claim()
        other = Client(self.root / 'client', self.transport)
        with self.client.guard('job-1'):
            with self.assertRaises(CapacityError):
                with other.guard('job-1'):
                    self.fail('competing owner acquired fence')
            with self.assertRaises(CapacityError):
                other.start('job-1')

    def test_expiry_boot_change_and_clock_rollback_refuse_start(self):
        self.claim()
        for now, boot in ((131, 'fixture-boot-1'), (99, 'fixture-boot-1'),
                          (100, 'fixture-boot-2')):
            self.now, self.boot = now, boot
            with self.client.guard('job-1'):
                with self.assertRaises(CapacityError):
                    self.client.start('job-1')
        self.assertNotIn('start', [c['operation'] for c in self.calls()])

    def test_ambiguous_start_quarantines_retirement_and_retry(self):
        self.claim()
        (self.root / 'mode').write_text('start-lost')
        with self.client.guard('job-1'):
            with self.assertRaises(CapacityError):
                self.client.start('job-1')
        with self.assertRaises(CapacityError):
            self.client.retire_prelaunch('job-1')
        with self.assertRaises(CapacityError):
            self.client.reconcile('job-1')
        with self.client.guard('job-1'):
            with self.assertRaises(CapacityError):
                self.client.start('job-1')

    def test_retirement_checks_registered_reservations_and_retires_before_reconcile(self):
        reservation = self.root / 'scratch-reservation'
        reservation.mkdir()
        self.request(scratch_reservations=[reservation])
        self.client.claim('job-1')
        with self.assertRaises(CapacityError):
            self.client.retire_prelaunch('job-1')
        reservation.rmdir()
        receipt = self.client.retire_prelaunch('job-1')
        self.assertFalse(receipt['spawned'])
        with self.client.guard('job-1'):
            with self.assertRaises(CapacityError):
                self.client.start('job-1')
        self.assertEqual(self.client.reconcile('job-1')['status'], 'CLOSED')
        self.assertEqual(self.client.reconcile('job-1')['status'], 'CLOSED')

    def test_owner_hook_refuses_unknown_process_identity_and_changed_retirement(self):
        self.claim()
        request = {'action': 'start', 'project': 'deepsignal', 'job': 'job-1',
                   'host': 'macbook', 'fence': 7, 'nonce': 'fixture-nonce'}
        with self.assertRaisesRegex(CapacityError, 'identity reporter'):
            self.client.owner_hook(request)
        self.client.retire_prelaunch('job-1')
        request['action'] = 'retire'
        self.assertEqual(self.client.owner_hook(request)['receipt']['outcome'], 'cancelled')
        request['fence'] = 8
        with self.assertRaises(CapacityError):
            self.client.owner_hook(request)

    def test_heartbeat_uses_private_capability_but_reconciliation_does_not(self):
        self.claim()
        with self.client.guard('job-1'):
            self.client.start('job-1')
        self.assertEqual(self.client.heartbeat('job-1')['status'], 'QUARANTINED')
        calls = {entry['operation']: entry for entry in self.calls()}
        self.assertTrue(calls['start']['has_token'])
        self.assertTrue(calls['heartbeat']['has_token'])
        self.assertFalse(calls['claim']['has_token'])
        with self.assertRaises(CapacityError):
            self.client.retire_prelaunch('job-1')

    def test_retirement_hook_rechecks_absence_and_archive_integrity(self):
        reservation = self.root / 'reservation'
        self.request(local_locks=[reservation])
        self.client.claim('job-1')
        self.client.retire_prelaunch('job-1')
        request = {'action': 'retire', 'project': 'deepsignal', 'job': 'job-1',
                   'host': 'macbook', 'fence': 7, 'nonce': 'n'}
        reservation.touch()
        with self.assertRaises(CapacityError):
            self.client.owner_hook(request)
        reservation.unlink()
        path = self.client.directory('job-1') / 'record.json'
        record = json.loads(path.read_text())
        record['receipt']['outcome'] = 'success'
        path.write_text(json.dumps(record))
        with self.assertRaises(CapacityError):
            self.client.owner_hook(request)

    def test_pinned_fake_authority_and_private_state_permissions_are_enforced(self):
        self.script.write_text(FAKE + '\n# changed\n')
        with self.assertRaisesRegex(CapacityError, 'identity changed'):
            self.request()
        self.client.root.chmod(0o755)
        with self.assertRaises(CapacityError):
            Client(self.client.root, self.transport)


if __name__ == '__main__':
    unittest.main()
