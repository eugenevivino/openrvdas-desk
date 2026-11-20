"""Queue isolation with disposable adapters, never product review approval."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import test_project
from dsrelay import project
from dsrelay.common import code_version, file_record
from relay.cli import install_plan, make_demo_plan
from relay.plan import compile_plan
from relay.store import Store


FIXTURE = '''import hashlib,json,os,pathlib
r=json.loads(pathlib.Path(os.environ['RELAY_INPUT_FILE']).read_text())
p=pathlib.Path(os.environ['RELAY_ATTEMPT_DIR'])/'proof.txt'
p.write_text('deterministic queue fixture only')
record={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
pathlib.Path(os.environ['RELAY_RESULT_FILE']).write_text(json.dumps({'schema':1,'outcome':'pass','input_digest':r['input_digest'],'summary':'queue fixture, no product acceptance','evidence':[str(p)],'data':{'artifacts':[record],'ai_calls':0}}))
'''


class ScopedEvidenceTests(unittest.TestCase):
    setUp=test_project.ProjectTests.setUp
    tearDown=test_project.ProjectTests.tearDown

    def plan(self):
        fixture=self.root/'fixture.py'; fixture.write_text(FIXTURE)
        plan=make_demo_plan(); plan['project']='deepsignal'
        refs={}
        for name in ('math','display'):
            proof=self.root/(name+'-prior'); proof.write_text('prior fixture evidence')
            contract={**self.c,'module':name,'prior_evidence':[file_record(proof)]}
            path=self.root/(name+'.json'); path.write_text(json.dumps(contract))
            refs[name]=file_record(path)
        for piece in plan['pieces']: piece['inputs']['contract']=refs[piece['inputs']['module']]
        for module in plan['modules']: module['inputs']={'contract':refs[module['id']]}
        for adapter in plan['adapters'].values():
            adapter['command']=[sys.executable,str(fixture)]
            adapter['version']=code_version()
        return plan

    def test_missing_current_contract_blocks_only_its_dependency_graph(self):
        plan=self.plan(); (self.root/'math.json').unlink()
        result=project.execute(plan,self.root/'state')
        status={row['module']:row['state'] for row in result['modules']}
        self.assertEqual(status,{'math':'evidence_invalid','display':'batch_tested'})
        rows=Store(self.root/'state/queue.sqlite3').jobs()
        self.assertTrue(any(r['state']=='passed' and r['spec'].get('module')=='display' for r in rows))
        self.assertTrue(all(r['attempt']==0 for r in rows if r['spec'].get('module')=='math'))

    def test_mutated_current_evidence_does_not_halt_independent_jobs(self):
        plan=self.plan(); (self.root/'math-prior').write_text('changed')
        result=project.execute(plan,self.root/'state')
        self.assertEqual({row['module']:row['state'] for row in result['modules']},
                         {'math':'evidence_invalid','display':'batch_tested'})

    def test_superseded_pass_with_deleted_evidence_is_not_reused_or_blocking(self):
        plan=self.plan(); state=self.root/'state'; store=install_plan(plan,state)
        spec=copy.deepcopy(compile_plan(plan)[0][0]); spec['id']='superseded.fixture'
        store.submit(spec); claim=store.claim(spec['id'],'fixture',10)
        store.finish(spec['id'],claim['token'],'fixture','passed',
                     {'receipt':{'data':{'artifacts':[{'path':str(self.root/'deleted'),'sha256':'0'*64}]}}})
        result=project.execute(plan,state)
        self.assertTrue(all(row['state']=='batch_tested' for row in result['modules']))
        self.assertEqual(store.get(spec['id'])['state'],'passed')
        self.assertNotIn(spec['id'],{row['id'] for row in result['evidence_audit']['invalid']})

    def test_read_only_report_invalidates_old_pass_without_state_change_or_launch(self):
        plan=self.plan(); state=self.root/'state'; project.execute(plan,state)
        store=Store(state/'queue.sqlite3'); rows=store.jobs(); events=store.events(10000)
        piece=next(row for row in rows if row['spec']['kind']=='piece' and 'math' in row['id'])
        Path(piece['result']['receipt']['data']['artifacts'][0]['path']).unlink()
        with patch.object(project,'run',side_effect=AssertionError('report dispatched work')):
            result=project.read_report(state)
        self.assertEqual(store.jobs(),rows); self.assertEqual(store.events(10000),events)
        math=next(row for row in result['modules'] if row['module']=='math')
        self.assertEqual(math['state'],'evidence_invalid')
        self.assertTrue(result['evidence_audit']['invalid'])
        # Exercise the actual report CLI as well: it must not initialize or run.
        reply=subprocess.run([sys.executable,'-m','dsrelay','report','--state',str(state)],
                             cwd=project.PACKAGE,text=True,capture_output=True,check=True)
        self.assertIn('evidence_invalid',reply.stdout)
        self.assertEqual(store.events(10000),events)

    def test_missing_receipt_does_not_crash_report(self):
        plan=self.plan(); state=self.root/'state'; store=install_plan(plan,state)
        job=store.jobs()[0]; claim=store.claim(job['id'],'fixture',10)
        store.finish(job['id'],claim['token'],'fixture','failed',{'receipt':None})
        result=project.measure(store,plan)
        self.assertEqual(result['ai_calls'],0)

    def test_restored_evidence_does_not_silently_clear_recorded_hold(self):
        plan=self.plan(); path=self.root/'math-prior'; original=path.read_text()
        path.unlink(); state=self.root/'state'; project.execute(plan,state)
        path.write_text(original)
        result=project.execute(plan,state)
        self.assertEqual(next(row for row in result['modules'] if row['module']=='math')['state'],'evidence_invalid')

    def test_invalid_evidence_does_not_reclaim_an_active_attempt(self):
        plan=self.plan(); state=self.root/'state'; store=install_plan(plan,state)
        job=next(row for row in store.jobs() if row['spec']['kind']=='piece' and 'math' in row['id'])
        claim=store.claim(job['id'],'existing-fixture-owner',10)
        (self.root/'math-prior').unlink()
        invalid=project.audit_cached(store,plan,mutate=True)
        live=store.get(job['id'])
        self.assertEqual((live['state'],live['token'],live['owner']),('running',claim['token'],'existing-fixture-owner'))
        store.finish(job['id'],claim['token'],'existing-fixture-owner','passed',{'receipt':None})
        project._retain_invalidations(store,invalid)
        self.assertEqual(store.get(job['id'])['state'],'blocked')


if __name__=='__main__': unittest.main()
