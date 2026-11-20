import json
import fcntl
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from relay.engine import run
from relay.store import Store
from relay.worker import atomic_json,input_digest

PREFIX='import json,os,pathlib,time,sys\nr=json.loads(pathlib.Path(os.environ["RELAY_INPUT_FILE"]).read_text())\n'
PASS='\npathlib.Path(os.environ["RELAY_RESULT_FILE"]).write_text(json.dumps({"schema":1,"outcome":"pass","input_digest":r["input_digest"],"summary":"test verified","evidence":[],"data":{"deps":list(r["dependencies"])}}))\n'

class EngineTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='relay-test-')
        self.root=Path(self.tmp.name)
        self.db=self.root/'jobs.sqlite'
        self.state=self.root/'state'
        self.store=Store(self.db)
    def tearDown(self): self.tmp.cleanup()
    def spec(self,id='one',code=None,**changes):
        v={'id':id,'kind':'piece','deps':[],'command':[sys.executable,'-c',code if code is not None else PREFIX+PASS], 'cwd':str(self.root),'inputs':{},'resources':{'cpu':1},'timeout_s':3,'max_attempts':1,'retry_exit_codes':[],'approval_required':False,'receipt_required':True,'priority':0}
        v.update(changes)
        return v
    def execute(self): return run(self.store,self.state,{'cpu':1},poll_s=0.05)
    def test_dependency_handoff(self):
        self.store.submit(self.spec('one',PREFIX+'time.sleep(0.1)\n'+PASS))
        self.store.submit(self.spec('two',deps=['one']))
        self.assertTrue(self.execute()['complete'])
        a,b=self.store.get('one'),self.store.get('two')
        self.assertEqual(b['result']['receipt']['data']['deps'],['one'])
        self.assertGreaterEqual(b['result']['started_at'],a['result']['finished_at'])
    def test_exit_zero_without_receipt_fails(self):
        self.store.submit(self.spec(code="print('no receipt')"))
        self.execute()
        self.assertEqual(self.store.get('one')['state'],'failed')
        self.assertIn('receipt',self.store.get('one')['reason'])
    def test_wrong_digest_and_missing_evidence_fail(self):
        self.store.submit(self.spec('digest',PREFIX+'r["input_digest"]="wrong"\n'+PASS))
        self.store.submit(self.spec('evidence',PREFIX+PASS.replace('"evidence":[]','"evidence":["missing"]')))
        self.execute()
        for id in ['digest','evidence']: self.assertEqual(self.store.get(id)['state'],'failed')
    def test_explicit_exit_retry(self):
        code=PREFIX+'count=pathlib.Path("tries")\nn=int(count.read_text())+1 if count.exists() else 1\ncount.write_text(str(n))\nif n==1: sys.exit(75)\n'+PASS
        self.store.submit(self.spec(code=code,max_attempts=2,retry_exit_codes=[75]))
        self.execute()
        row=self.store.get('one')
        self.assertEqual((row['state'],row['attempt']),('passed',2))
        self.assertEqual((self.root/'tries').read_text(),'2')
    def test_unlisted_failure_not_retried(self):
        self.store.submit(self.spec(code='import sys;sys.exit(2)',max_attempts=3,retry_exit_codes=[75]))
        self.execute()
        row=self.store.get('one')
        self.assertEqual((row['state'],row['attempt']),('failed',1))
    def test_timeout_only_kills_own_descendants(self):
        code=PREFIX+'import subprocess\nchild=subprocess.Popen([sys.executable,"-c","import signal,time;signal.signal(signal.SIGTERM,signal.SIG_IGN);time.sleep(30)"])\npathlib.Path("descendant.pid").write_text(str(child.pid))\ntime.sleep(30)\n'
        other=subprocess.Popen([sys.executable,'-c','import time;time.sleep(30)'])
        try:
            self.store.submit(self.spec(code=code,timeout_s=0.4)); self.execute()
            row=self.store.get('one')
            self.assertEqual(row['state'],'failed'); self.assertTrue(row['result']['timed_out'])
            self.assertIsNone(other.poll())
            pid=(self.root/'descendant.pid').read_text()
            p=subprocess.run(['ps','-p',pid,'-o','stat='],capture_output=True,text=True)
            self.assertTrue(p.returncode!=0 or not p.stdout.strip() or p.stdout.strip().startswith('Z'))
        finally: other.terminate();other.wait(timeout=3)
    def test_undeclared_resource_errors(self):
        self.store.submit(self.spec(resources={'unknown':1}))
        with self.assertRaisesRegex(ValueError,'undeclared'): self.execute()
        self.assertEqual(self.store.get('one')['state'],'queued')
    def test_independent_jobs_obey_shared_capacity(self):
        for id in ['one','two']:
            self.store.submit(self.spec(id,PREFIX+'time.sleep(0.15)\n'+PASS))
        self.execute()
        a,b=self.store.get('one'),self.store.get('two')
        self.assertGreaterEqual(b['result']['started_at'],a['result']['finished_at'])
    def test_second_controller_cannot_take_lock(self):
        self.state.mkdir()
        with (self.state/'controller.lock').open('a+') as lock:
            fcntl.flock(lock.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
            with self.assertRaisesRegex(RuntimeError,'another Relay controller'):
                self.execute()
    def manual_result(self,delta=0):
        self.store.submit(self.spec()); row=self.store.claim('one','old',0.01)
        p=self.state/'attempts'/'manual';p.mkdir(parents=True)
        r={'schema':1,'job_id':'one','attempt':row['attempt'],'token':row['token'],'spec':row['spec'],'dependencies':{}}
        r['input_digest']=input_digest(r);atomic_json(p/'input.json',r)
        self.store.set_runtime('one',row['token'],row['owner'],0,str(p))
        receipt={'schema':1,'outcome':'pass','input_digest':r['input_digest'],'summary':'late valid result','evidence':[],'data':{}}
        atomic_json(p/'worker-result.json',{'schema':1,'job_id':'one','attempt':row['attempt'],'token':row['token']+delta,'input_digest':r['input_digest'],'returncode':0,'timed_out':False,'cancelled':False,'started_at':time.time()-0.1,'finished_at':time.time(),'receipt':receipt,'receipt_error':None,'error':None})
        return row
    def test_late_result_resolves_same_uncertain_attempt(self):
        row=self.manual_result();self.store.mark_uncertain('one',row['token'],'lost coordinator')
        self.execute();row=self.store.get('one')
        self.assertEqual((row['state'],row['attempt']),('passed',1))
    def test_wrong_token_never_completes_or_duplicates(self):
        self.manual_result(delta=1);self.execute();row=self.store.get('one')
        self.assertEqual((row['state'],row['attempt']),('uncertain',1))
    def test_restart_adopts_without_duplicate(self):
        code=PREFIX+'with pathlib.Path("executions").open("a") as f: f.write("one\\n")\ntime.sleep(1.0)\n'+PASS
        self.store.submit(self.spec(code=code,timeout_s=5))
        script='import sys\nfrom relay.store import Store\nfrom relay.engine import run\nrun(Store(sys.argv[1]),sys.argv[2],{"cpu":1},poll_s=0.05)'
        proc=subprocess.Popen([sys.executable,'-c',script,str(self.db),str(self.state)],cwd=str(Path(__file__).resolve().parents[1]),start_new_session=True)
        try:
            deadline=time.monotonic()+4
            while time.monotonic()<deadline:
                row=self.store.get('one')
                if row.get('attempt_dir') and (Path(row['attempt_dir'])/'worker-heartbeat.json').exists(): break
                time.sleep(0.02)
            else: self.fail('supervisor did not start')
            proc.terminate();proc.wait(timeout=3)
            self.execute();row=self.store.get('one')
            self.assertEqual((row['state'],row['attempt']),('passed',1))
            self.assertEqual((self.root/'executions').read_text(),'one\n')
        finally:
            if proc.poll() is None: proc.terminate();proc.wait(timeout=3)
    def test_cancellation_after_restart_reaches_owned_supervisor(self):
        self.store.submit(self.spec(code=PREFIX+'time.sleep(20)\n'+PASS,timeout_s=30))
        script='import sys\nfrom relay.store import Store\nfrom relay.engine import run\nrun(Store(sys.argv[1]),sys.argv[2],{"cpu":1},poll_s=0.05)'
        proc=subprocess.Popen([sys.executable,'-c',script,str(self.db),str(self.state)],cwd=str(Path(__file__).resolve().parents[1]),start_new_session=True)
        try:
            deadline=time.monotonic()+4
            while time.monotonic()<deadline:
                row=self.store.get('one')
                if row.get('attempt_dir') and (Path(row['attempt_dir'])/'worker-heartbeat.json').exists(): break
                time.sleep(0.02)
            else: self.fail('supervisor did not start')
            proc.terminate();proc.wait(timeout=3)
            self.store.request_cancel('one')
            self.execute();row=self.store.get('one')
            self.assertEqual((row['state'],row['attempt']),('cancelled',1))
            self.assertTrue(row['result']['cancelled'])
        finally:
            if proc.poll() is None: proc.terminate();proc.wait(timeout=3)

if __name__=='__main__': unittest.main()
