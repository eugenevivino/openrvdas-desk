"""Disposable measurement storage; no host sampling, jobs or leases."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sqlite3
import tempfile
import unittest

from dsrelay.measurements import record_swap


class MeasurementTests(unittest.TestCase):
    def setUp(self):
        root=Path('/private/tmp/deepsignal/relay-20261120/tests'); root.mkdir(parents=True,exist_ok=True)
        self.tmp=tempfile.TemporaryDirectory(dir=root); self.root=Path(self.tmp.name)
        self.path=self.root/'measurements'/'swap.sqlite3'

    def tearDown(self): self.tmp.cleanup()

    def sample(self,wall=1000,mono=500,used=1024,boot='boot-a',path=None):
        return record_swap(path or self.path,boot_id=boot,wall_s=wall,monotonic_s=mono,used_mib=used)

    def test_exact_five_to_ten_minute_window(self):
        for age,accepted in ((299,False),(300,True),(600,True),(601,False)):
            with self.subTest(age=age):
                path=self.root/str(age)/'swap.sqlite3'
                self.assertIsNone(self.sample(path=path))
                baseline=self.sample(wall=1000+age,mono=500+age,path=path)
                self.assertEqual(baseline is not None,accepted)

    def test_boot_and_both_clocks_must_match(self):
        for boot,wall,mono in (('boot-b',1300,800),('boot-a',1300,799),
                               ('boot-a',1300,850),('boot-a',999,800),('boot-a',1300,499)):
            with self.subTest(boot=boot,wall=wall,mono=mono):
                path=self.root/f'{boot}-{wall}-{mono}'/'swap.sqlite3'
                self.sample(path=path)
                self.assertIsNone(self.sample(wall,mono,boot=boot,path=path))

    def test_separate_callers_reuse_verified_baseline(self):
        self.sample()
        self.assertEqual(self.sample(1300,800)['used_mib'],1024)
        self.assertEqual(self.sample(1305,805)['wall_s'],1000)
        self.assertEqual(self.path.stat().st_mode&0o777,0o600)
        self.assertEqual(self.path.parent.stat().st_mode&0o777,0o700)

    def test_corrupt_database_refuses_without_resetting(self):
        self.path.parent.mkdir(mode=0o700); self.path.write_bytes(b'not sqlite'); self.path.chmod(0o600)
        before=self.path.read_bytes()
        with self.assertRaises(ValueError): self.sample()
        self.assertEqual(self.path.read_bytes(),before)

    def test_corrupt_observation_refuses(self):
        self.sample()
        with sqlite3.connect(self.path) as db: db.execute("UPDATE samples SET used_mib='unknown'")
        with self.assertRaises(ValueError): self.sample(1300,800)

    def test_concurrent_initialization_and_inserts_are_atomic(self):
        def insert(i): return self.sample(1000+i,500+i)
        with ThreadPoolExecutor(max_workers=4) as workers:
            self.assertEqual(list(workers.map(insert,range(12))),[None]*12)
        with sqlite3.connect(self.path) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM samples').fetchone()[0],12)
        self.assertEqual(self.sample(1311,811)['wall_s'],1011)

    def test_foreign_symlink_database_untouched(self):
        foreign=self.root/'foreign'; foreign.write_bytes(b'untouched')
        self.path.parent.mkdir(mode=0o700); self.path.symlink_to(foreign)
        with self.assertRaises(ValueError): self.sample()
        self.assertEqual(foreign.read_bytes(),b'untouched')


if __name__=='__main__': unittest.main()
