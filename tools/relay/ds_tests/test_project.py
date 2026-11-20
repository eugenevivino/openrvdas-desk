import json, os, subprocess, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from dsrelay import adapter
from dsrelay.common import file_record, verify_files
from dsrelay.project import build_plan
from relay.plan import compile_plan
SCRATCH=Path('/private/tmp/deepsignal/relay-20261120/tests'); SCRATCH.mkdir(parents=True,exist_ok=True)
class ProjectTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(dir=SCRATCH); self.root=Path(self.temp.name); self.repo=self.root/'repo'; self.repo.mkdir()
  def git(*args): return subprocess.check_output(['git','-C',str(self.repo),*args],text=True).strip()
  git('init','-q'); git('config','user.email','fixture@example.invalid'); git('config','user.name','Fixture')
  (self.repo/'module.py').write_text('VALUE = 42\n'); git('add','.'); git('commit','-qm','fixture')
  self.pin=git('rev-parse','HEAD'); self.policy=self.root/'policy'; self.policy.write_text('gate')
  self.c={'schema':1,'project':'deepsignal','module':'alpha','mode':'test_only','repository':str(self.repo),'commit':self.pin,'tree':git('rev-parse','HEAD^{tree}'),'integration_base':self.pin,'policy_files':[file_record(self.policy)],'prior_evidence':[],'acceptance':[{'name':'check','argv':[sys.executable,'-c','from module import VALUE; assert VALUE == 42']}],'required_gates':[{'name':'independent-review','status':'missing','reason':'review missing','independent':True}]}
  self.path=self.root/'contract.json'; self.path.write_text(json.dumps(self.c))
 def tearDown(self): self.temp.cleanup()
 def candidate(self):
  a=self.root/'piece'; a.mkdir(); d=adapter.piece(self.c,a); b=self.root/'assemble'; b.mkdir(); return adapter.assemble(self.c,[d],b)
 def checks(self,data):
  d=self.root/'test'; d.mkdir()
  with patch.object(adapter,'admission'),patch.object(adapter,'LOCAL_LOCK',self.root/'lock'): return adapter.checks(self.c,data,d)
 def test_evidence_mutation_and_deletion(self):
  r=file_record(self.policy); self.policy.write_text('changed')
  with self.assertRaises(ValueError): verify_files([r])
  self.policy.unlink()
  with self.assertRaises(OSError): verify_files([r])
 def test_policy_invalidates_all_downstream_jobs(self):
  a,_=compile_plan(build_plan([self.path])); self.policy.write_text('new gate'); self.c['policy_files']=[file_record(self.policy)]; self.path.write_text(json.dumps(self.c)); b,_=compile_plan(build_plan([self.path]))
  self.assertTrue(all(x['id']!=y['id'] for x,y in zip(a,b)))
 def test_snapshot_ignores_dirty_checkout(self):
  (self.repo/'module.py').write_text('VALUE=0\n'); self.assertTrue(self.checks(self.candidate())['checks']['passed'])
 def test_changed_candidate_refused(self):
  d=self.candidate(); (Path(d['candidate'])/'module.py').write_text('VALUE=0\n')
  with self.assertRaises(ValueError): self.checks(d)
 def test_green_checks_do_not_replace_review(self):
  d=self.checks(self.candidate()); a=self.root/'review'; a.mkdir()
  with self.assertRaises(adapter.Blocked): adapter.review(self.c,[d],a)
  self.assertTrue(json.loads((a/'review-request.json').read_text())['request_ai'])
 def test_hold_stays_hold(self):
  d=self.checks(self.candidate()); a=self.root/'review'; a.mkdir(); self.c['required_gates'][0].update(status='hold',reason='wrong display')
  with self.assertRaisesRegex(adapter.Blocked,'wrong display'): adapter.review(self.c,[d],a)
 def test_author_cannot_review_self(self):
  d=self.checks(self.candidate()); a=self.root/'review'; a.mkdir(); self.c['author_runs']=['same']; self.c['required_gates'][0].update(status='pass',candidate_commit=self.pin,verifier='fixture',evidence=[file_record(self.policy)],reviewer_run='same')
  with self.assertRaisesRegex(adapter.Blocked,'independent reviewer'): adapter.review(self.c,[d],a)
 def test_science_needs_reference(self):
  d=self.checks(self.candidate()); a=self.root/'review'; a.mkdir(); self.c['scientific_change']=True
  with self.assertRaisesRegex(adapter.Blocked,'reference dataset'): adapter.review(self.c,[d],a)
 def test_different_candidates_refused(self):
  d=self.candidate(); d['review']={'missing':[]}
  with self.assertRaisesRegex(adapter.Blocked,'different candidates'): adapter.batch({'integration_mode':'test_only'},[d,{**d,'candidate_commit':'f'*40}],self.root)
 def test_compatible_batch_checks_union(self):
  d=self.candidate(); d['review']={'missing':[]}; e={**d,'contract':{**self.c,'module':'beta','acceptance':[{'name':'beta-variation','argv':[sys.executable,'-c','from module import VALUE; assert VALUE % 2 == 0']}]}}; a=self.root/'batch'; a.mkdir()
  with patch.object(adapter,'admission'),patch.object(adapter,'LOCAL_LOCK',self.root/'lock'): r=adapter.batch({'integration_mode':'test_only'},[d,e],a)
  self.assertTrue(r['checks']['passed']); self.assertEqual([x['name'] for x in r['checks']['commands']],['check','beta-variation']); self.assertEqual(r['integration']['modules'],['alpha','beta']); self.assertFalse(r['integration']['merged'])
 def test_second_module_failure_fails_combined_batch(self):
  d=self.candidate(); d['review']={'missing':[]}; e={**d,'contract':{**self.c,'module':'beta','acceptance':[{'name':'beta-fails','argv':[sys.executable,'-c','from module import VALUE; assert VALUE == 43']}]}}; a=self.root/'batch'; a.mkdir()
  with patch.object(adapter,'admission'),patch.object(adapter,'LOCAL_LOCK',self.root/'lock'): r=adapter.batch({'integration_mode':'test_only'},[d,e],a)
  self.assertFalse(r['checks']['passed']); self.assertEqual(len(r['checks']['commands']),2); self.assertNotEqual(r['checks']['commands'][1]['returncode'],0)
 def test_checks_disable_pytest_cache_without_weakening_source_manifest(self):
  self.c['acceptance']=[{'name':'pytest-cache-policy','argv':[sys.executable,'-c','import os; assert os.environ["PYTEST_ADDOPTS"] == "-p no:cacheprovider"']}]
  self.assertTrue(self.checks(self.candidate())['checks']['passed'])
 def test_foreign_slot_preserved(self):
  d=self.candidate(); lock=self.root/'lock'; lock.mkdir(); (lock/'owner').write_text('foreign')
  with self.assertRaises(adapter.Blocked): self.checks(d)
  self.assertEqual((lock/'owner').read_text(),'foreign')
 def test_output_cap(self):
  log=self.root/'output'
  with patch.object(adapter,'OUTPUT_LIMIT',1024):
   with self.assertRaisesRegex(ValueError,'output limit'): adapter.command([sys.executable,'-c','print("x"*4096)'],self.root,os.environ.copy(),log,5)
  self.assertEqual(log.stat().st_size,1024)
 def test_timeout(self):
  with self.assertRaises(TimeoutError): adapter.command([sys.executable,'-c','import time; time.sleep(10)'],self.root,os.environ.copy(),self.root/'out',0.1)
 def test_cwd_escape(self):
  self.c['acceptance'][0]['cwd']='../../../../'; d=self.candidate()
  with self.assertRaises(ValueError): self.checks(d)
 def test_failure_is_not_pass(self):
  self.c['acceptance'][0]['argv']=[sys.executable,'-c','raise SystemExit(7)']; self.assertFalse(self.checks(self.candidate())['checks']['passed'])
