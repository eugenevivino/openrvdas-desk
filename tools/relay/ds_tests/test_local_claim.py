"""Native exclusive publication, restricted to disposable DeepSignal paths."""
from concurrent.futures import ThreadPoolExecutor
import errno
import os
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
from dsrelay import adapter, local_claim


class LocalClaimTests(unittest.TestCase):
    def setUp(self):
        root=Path('/private/tmp/deepsignal/relay-20261120/tests'); root.mkdir(parents=True,exist_ok=True)
        self.tmp=tempfile.TemporaryDirectory(dir=root); self.root=Path(self.tmp.name)
        self.attempt=self.root/'attempt'; self.attempt.mkdir(); self.lock=self.root/'lock'
    def tearDown(self): self.tmp.cleanup()

    def test_publication_and_withdrawal_expose_only_complete_claims(self):
        rename=local_claim.rename_exclusive; observed=[]
        def inspect(source,destination):
            self.assertEqual((Path(source)/'pid').read_text(),str(os.getpid()))
            self.assertEqual((Path(source)/'relay-owner').read_text(),str(self.attempt))
            observed.append((Path(source),Path(destination)))
            return rename(source,destination)
        with patch.object(local_claim,'rename_exclusive',side_effect=inspect):
            with local_claim.LocalClaim(self.attempt,self.lock) as claim:
                private=claim.private; self.assertFalse(self.lock.exists()); claim.publish()
                self.assertFalse(private.exists())
                self.assertEqual(self.lock.stat().st_mode&0o777,0o700)
                self.assertEqual((self.lock/'pid').stat().st_mode&0o777,0o600)
        self.assertEqual(observed,[(private,self.lock),(self.lock,private)])
        self.assertFalse(self.lock.exists()); self.assertEqual(list(self.attempt.iterdir()),[])

    def test_empty_incomplete_and_populated_foreign_directories_are_not_replaced(self):
        self.lock.mkdir(); identity=self.lock.stat().st_ino
        for contents in ({},{'pid':'999999999'},{'pid':'1','owner':'foreign'}):
            for name,text in contents.items(): (self.lock/name).write_text(text)
            before={p.name:p.read_bytes() for p in self.lock.iterdir()}
            with local_claim.LocalClaim(self.attempt,self.lock) as claim:
                with self.assertRaises(FileExistsError): claim.publish()
            self.assertEqual(self.lock.stat().st_ino,identity)
            self.assertEqual({p.name:p.read_bytes() for p in self.lock.iterdir()},before)
            self.assertEqual(list(self.attempt.iterdir()),[])

    def test_existing_symlink_is_a_collision_not_a_target_to_replace(self):
        target=self.root/'foreign'; target.mkdir(); self.lock.symlink_to(target,target_is_directory=True)
        with local_claim.LocalClaim(self.attempt,self.lock) as claim:
            with self.assertRaises(FileExistsError): claim.publish()
        self.assertTrue(self.lock.is_symlink()); self.assertTrue(target.is_dir())

    def test_simultaneous_claims_have_exactly_one_publisher(self):
        attempts=[self.root/'first',self.root/'second']
        for path in attempts: path.mkdir()
        claims=[local_claim.LocalClaim(path,self.lock) for path in attempts]; barrier=threading.Barrier(2)
        def publish(claim):
            barrier.wait(timeout=5)
            try: claim.publish(); return True
            except FileExistsError: return False
        try:
            with ThreadPoolExecutor(max_workers=2) as executor: results=list(executor.map(publish,claims))
            self.assertEqual(sum(results),1); winner=claims[results.index(True)]
            self.assertEqual((self.lock/'relay-owner').read_text(),str(winner.attempt))
        finally:
            for claim in claims: claim.close()
        self.assertFalse(self.lock.exists()); self.assertTrue(all(not list(path.iterdir()) for path in attempts))

    def test_metadata_failure_cleans_private_staging_only(self):
        self.lock.mkdir(); (self.lock/'foreign').write_text('keep'); write=local_claim.LocalClaim._write_file
        def fail_second(claim,name,value):
            if name=='relay-owner': raise OSError('fixture metadata failure')
            return write(claim,name,value)
        with patch.object(local_claim.LocalClaim,'_write_file',fail_second):
            with self.assertRaises(OSError): local_claim.LocalClaim(self.attempt,self.lock)
        self.assertEqual(list(self.attempt.iterdir()),[]); self.assertEqual((self.lock/'foreign').read_text(),'keep')

    def test_unsupported_publication_has_no_fallback_and_cleans_staging(self):
        with patch.object(local_claim,'rename_exclusive',side_effect=OSError(errno.ENOTSUP,'fixture unsupported')):
            with self.assertRaises(OSError):
                with local_claim.LocalClaim(self.attempt,self.lock) as claim: claim.publish()
        self.assertFalse(self.lock.exists()); self.assertEqual(list(self.attempt.iterdir()),[])

    def test_replaced_claim_is_quarantined_without_foreign_cleanup(self):
        claim=local_claim.LocalClaim(self.attempt,self.lock); claim.publish()
        displaced=self.root/'displaced-owned'; self.lock.rename(displaced)
        self.lock.mkdir(); (self.lock/'foreign').write_text('keep')
        with self.assertRaisesRegex(RuntimeError,'ownership changed'): claim.close()
        self.assertEqual((self.lock/'foreign').read_text(),'keep')
        self.assertEqual((displaced/'pid').read_text(),str(os.getpid()))

    def test_changed_owner_metadata_is_not_cleaned_as_our_claim(self):
        claim=local_claim.LocalClaim(self.attempt,self.lock); claim.publish()
        (self.lock/'relay-owner').write_text('different owner')
        with self.assertRaisesRegex(RuntimeError,'ownership changed'): claim.close()
        self.assertEqual((self.lock/'relay-owner').read_text(),'different owner')

    def test_work_failure_withdraws_only_own_complete_claim(self):
        with patch.object(adapter,'admission'),patch.object(adapter,'LOCAL_LOCK',self.lock):
            with self.assertRaisesRegex(ValueError,'fixture work failure'):
                with adapter.execution_slot(self.attempt): raise ValueError('fixture work failure')
        self.assertFalse(self.lock.exists()); self.assertEqual(list(self.attempt.iterdir()),[])


if __name__=='__main__': unittest.main()
