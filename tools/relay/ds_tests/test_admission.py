"""Read-only sampling and bounded claim waits with no real host commands."""
import json
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from dsrelay import adapter


class AdmissionTests(unittest.TestCase):
    def setUp(self):
        root=Path('/private/tmp/deepsignal/relay-20261120/tests'); root.mkdir(parents=True,exist_ok=True)
        self.tmp=tempfile.TemporaryDirectory(dir=root); self.root=Path(self.tmp.name)
        self.attempt=self.root/'attempt'; self.attempt.mkdir()
        self.history=self.root/'history'; self.history.write_text('700 1024\n')
        self.patterns=self.root/'patterns'; self.patterns.write_text('/bin/codex exec( |$)\n(^|/)xcodebuild( |$)\n')
        self.lock=self.root/'lock'; self.now=1000
        self.values={'hw.pagesize':'4096','hw.memsize':str(16*1024**3),
                     'kern.boottime':'{ sec = 1, usec = 0 }',
                     'vm.swapusage':'total = 8192.00M  used = 1024.00M  free = 7168.00M',
                     'kern.memorystatus_vm_pressure_level':'1',
                     'vm_stat':'Pages free: 1048576.\nPages speculative: 0.\nPages purgeable: 0.\nFile-backed pages: 0.\nPages wired down: 262144.\nPages occupied by compressor: 0.',
                     'ps':'python fixture'}
        self.calls=[]
        def read(argv,**kwargs):
            self.calls.append(argv)
            key=argv[-1] if argv[0].endswith('sysctl') else Path(argv[0]).name
            value=self.values[key]
            if isinstance(value,Exception): raise value
            return value
        self.patches=[patch.object(adapter,'SWAP_HISTORY',self.history),
                      patch.object(adapter,'SWAP_CACHE',self.root/'cache'/'swap.sqlite3'),
                      patch.object(adapter,'HEAVY_PATTERNS',self.patterns),
                      patch.object(adapter,'LOCAL_LOCK',self.lock),
                      patch.object(adapter.subprocess,'check_output',side_effect=read),
                      patch.object(adapter.shutil,'disk_usage',return_value=SimpleNamespace(free=6*1024**3)),
                      patch.object(adapter.time,'time',side_effect=lambda:self.now),
                      patch.object(adapter.time,'monotonic',side_effect=lambda:self.now)]
        for item in self.patches: item.start()

    def tearDown(self):
        for item in reversed(self.patches): item.stop()
        self.tmp.cleanup()

    def test_healthy_sample_preserves_shared_history_and_never_executes_launcher(self):
        before=self.history.read_bytes(); adapter.admission_once(self.attempt)
        self.assertEqual(self.history.read_bytes(),before)
        self.assertTrue((self.attempt/'swap-history.json').exists())
        self.assertEqual(json.loads((self.attempt/'admission.log').read_text())['available_mib'],4096)
        self.assertTrue(all(call[0] in {'/usr/sbin/sysctl','/usr/bin/vm_stat','/bin/ps'} for call in self.calls))

    def test_foreign_and_ambiguous_claims_are_never_removed_or_sampled(self):
        self.lock.mkdir()
        for pid in (None,'999999999','1'):
            if pid is not None: (self.lock/'pid').write_text(pid)
            before={p.name:p.read_bytes() for p in self.lock.iterdir()}
            with self.assertRaises(adapter.Blocked): adapter.admission_once(self.attempt)
            self.assertEqual({p.name:p.read_bytes() for p in self.lock.iterdir()},before)
            self.assertEqual(self.calls,[])

    def test_missing_counter_or_failed_process_sample_never_becomes_zero_load(self):
        original=self.values['vm_stat']
        self.values['vm_stat']=original.replace('Pages purgeable: 0.\n','')
        with self.assertRaises(adapter.Blocked): adapter.admission_once(self.attempt)
        self.values['vm_stat']=original
        self.values['ps']=subprocess.CalledProcessError(1,['/bin/ps'])
        with self.assertRaises(adapter.Blocked): adapter.admission_once(self.attempt)

    def test_existing_thresholds_remain_enforced(self):
        variants=[('kern.memorystatus_vm_pressure_level','2'),
                  ('vm.swapusage','used = 8192.00M'),
                  ('vm.swapusage','used = 1537.00M'),
                  ('ps','/bin/codex exec one\n/usr/bin/xcodebuild'),
                  ('vm_stat',self.values['vm_stat'].replace('1048576','524288'))]
        for key,value in variants:
            with self.subTest(key=key,value=value):
                old=self.values[key]; self.values[key]=value
                with self.assertRaises(adapter.Blocked): adapter.admission_once(self.attempt)
                self.values[key]=old

    def test_private_history_requires_full_five_minute_baseline(self):
        self.history.unlink()
        with self.assertRaises(adapter.Blocked): adapter.admission_once(self.attempt)
        self.now+=299
        with self.assertRaises(adapter.Blocked): adapter.admission_once(self.attempt)
        self.now+=1
        adapter.admission_once(self.attempt)
        self.assertFalse(self.history.exists())

    def test_bad_shared_history_preserved_while_private_baseline_recovers(self):
        self.history.write_text('700 1024\ninvalid old sandbox counter\n')
        before=self.history.read_bytes()
        with self.assertRaises(adapter.Blocked): adapter.admission_once(self.attempt)
        self.assertTrue((self.attempt/'swap-history.json').exists())
        self.now+=299
        with self.assertRaises(adapter.Blocked): adapter.admission_once(self.attempt)
        self.now+=1
        next_attempt=self.root/'next-attempt'; next_attempt.mkdir()
        adapter.admission_once(next_attempt)
        sample=json.loads((next_attempt/'admission.log').read_text())
        self.assertFalse(sample['shared_swap_history_valid'])
        self.assertTrue(sample['project_cache_baseline_available'])
        self.assertEqual(sample['swap_growth_5min_mib'],0)
        self.assertEqual(self.history.read_bytes(),before)

    def test_held_claim_wait_uses_one_bounded_window_and_preserves_owner(self):
        self.lock.mkdir(); (self.lock/'owner').write_text('foreign')
        clock=[0.0]
        def sleep(seconds): clock[0]+=seconds
        with patch.object(adapter,'ADMISSION_WAIT_S',3),patch.object(adapter,'ADMISSION_POLL_S',1),patch.object(adapter.time,'monotonic',side_effect=lambda:clock[0]),patch.object(adapter.time,'sleep',side_effect=sleep):
            with self.assertRaises(adapter.Blocked):
                with adapter.execution_slot(self.attempt): self.fail('occupied slot admitted')
        self.assertEqual(clock[0],3)
        self.assertEqual((self.lock/'owner').read_text(),'foreign')
        self.assertEqual(self.calls,[])

    def test_acquisition_race_rechecks_admission_without_consuming_attempt(self):
        clock=[0.0]; calls=[]
        def admission(attempt,deadline=None):
            calls.append(deadline)
            if len(calls)==1:
                self.lock.mkdir(); (self.lock/'owner').write_text('fixture owner')
        def sleep(seconds):
            clock[0]+=seconds
            # The fixture owner independently releases its own claim.
            (self.lock/'owner').unlink(); self.lock.rmdir()
        with patch.object(adapter,'admission',side_effect=admission),patch.object(adapter,'ADMISSION_WAIT_S',3),patch.object(adapter,'ADMISSION_POLL_S',1),patch.object(adapter.time,'monotonic',side_effect=lambda:clock[0]),patch.object(adapter.time,'sleep',side_effect=sleep):
            with adapter.execution_slot(self.attempt): self.assertTrue((self.lock/'relay-owner').exists())
        self.assertEqual(calls,[3,3]); self.assertFalse(self.lock.exists())


if __name__=='__main__': unittest.main()
