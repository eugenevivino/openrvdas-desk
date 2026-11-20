"""Compile DeepSignal contracts into Relay's existing job graph."""
import json
import platform
import sqlite3
import subprocess
import time
from pathlib import Path
import sys
from urllib.parse import quote
from .common import owned, sha, digest, git, file_record, verify_files, tree_manifest, verify_tree, load_contract, code_version
from relay.plan import validate, compile_plan, module_status, submit_plan, batch_callback, _batch_matches_plan
from relay.cli import install_plan, plan_lock, metrics
from relay.engine import run
from relay.store import Store
from relay.worker import atomic_json

PACKAGE = Path(__file__).resolve().parent.parent
DESK = Path('/private/tmp/deepsignal/desk-main')


def build_plan(contracts):
    # Older macOS Python uses a process-relative monotonic clock. Its samples
    # cannot establish the cross-worker swap window required by admission.
    if sys.version_info < (3, 12):
        raise ValueError('Python 3.12 or newer is required to compile Relay plans')
    version=code_version()
    adapters={}
    for stage in ('piece','assemble','test','review','batch'):
        resources={'local_test':1} if stage in ('test','assemble') else {'metadata':1}
        if stage=='batch': resources={'local_test':1,'integration':1}
        adapters[stage]={'command':[sys.executable,'-m','dsrelay.adapter'],'version':version,
                         'actor':'existing-independent-review-evidence' if stage=='review' else 'deepsignal-candidate-adapter',
                         'timeout_s':600,'resources':resources,'max_attempts':3,'retry_exit_codes':[75]}
    pieces=[]; modules=[]
    for path in contracts:
        r=file_record(path); c=load_contract({'contract':r}); name=c['module']
        pieces.append({'id':name+'-source','adapter':'piece','identity':{'commit':c['commit'],'tree':c['tree'],'contract':r['sha256']},'inputs':{'contract':r}})
        modules.append({'id':name,'pieces':[name+'-source'],'assemble':'assemble','test':'test','review':'review',
                        'inputs':{'contract':r},'acceptance':c['acceptance'],
                        'compatibility_key':c['integration_base']+':'+c['commit']})
    plan={'schema':1,'project':'deepsignal','workspace':str(PACKAGE),'policy_version':'deepsignal-relay-shadow-v1',
          'environment_id':digest({'python':platform.python_version(),'executable':str(Path(sys.executable).resolve()),'platform':platform.platform()}),
          'capacities':{'metadata':2,'local_test':1,'integration':1},'max_parallel':3,
          'adapters':adapters,'pieces':pieces,'modules':modules,'batch':{'adapter':'batch','max_size':5,'integration_mode':'test_only'}}
    validate(plan); return plan


class Snapshot:
    def __init__(self, rows, attempt_events=None):
        self.rows = rows
        self.attempt_events = attempt_events

    def jobs(self): return self.rows


def _read_snapshot(conn):
    conn.row_factory = sqlite3.Row
    # Job rows and the matching attempt history must come from one SQLite view.
    with conn:
        conn.execute('BEGIN')
        rows = [Store._row(row) for row in conn.execute('SELECT * FROM jobs ORDER BY created_at,id')]
        events = [dict(row) for row in conn.execute(
            "SELECT kind,job_id,created_at,data FROM events WHERE kind IN ('claimed','finished') ORDER BY id")]
    for event in events:
        try:
            event['data'] = json.loads(event['data'])
        except (TypeError, ValueError):
            event['data'] = None
    return Snapshot(rows, events)


def current_rows(store,plan):
    specs,_=compile_plan(plan); ids={s['id'] for s in specs}
    return [r for r in store.jobs() if r['id'] in ids or
            (r['spec']['kind']=='batch' and set(r['spec']['deps'])<=ids
             and _batch_matches_plan(plan,r))]


def _retain_invalidations(store,invalid):
    """Retain receipts; never reclaim an active or uncertain worker."""
    if not invalid: return
    with store._transaction() as conn:
        for job,reason in invalid.items():
            row=conn.execute('SELECT state,reason FROM jobs WHERE id=?',(job,)).fetchone()
            if row is None or row['state'] not in {'queued','approval','passed'}: continue
            conn.execute("UPDATE jobs SET state='blocked',reason=?,blocked_from=NULL,ready_at=NULL,finished_at=COALESCE(finished_at,?) WHERE id=?",
                         (reason,time.time(),job))
            store._event(conn,'evidence_invalidated',job,{'previous_state':row['state'],'previous_reason':row['reason'],'reason':reason})


def audit_cached(store,plan,mutate=False):
    """Audit only the current graph, preserving scoped evidence holds."""
    rows=current_rows(store,plan); invalid={}
    for row in rows:
        if row['state']=='blocked' and row.get('reason','').startswith('evidence: invalid'):
            invalid[row['id']]=row['reason']
        try:
            if row['spec']['kind']=='piece': load_contract(row['spec']['inputs'])
            if row['state']=='passed':
                data=row['result']['receipt']['data']; verify_files(data['artifacts'])
                if 'source_manifest' in data:
                    from .adapter import verify_candidate
                    verify_candidate(data)
        except (OSError,ValueError,KeyError,TypeError,subprocess.SubprocessError) as exc:
            invalid[row['id']]='evidence: invalid '+str(exc)
    changed=True
    while changed:
        changed=False
        for row in rows:
            if row['id'] in invalid: continue
            bad=[dep for dep in row['spec']['deps'] if dep in invalid]
            if bad:
                invalid[row['id']]='evidence: invalid prerequisite '+bad[0]
                changed=True
    if mutate: _retain_invalidations(store,invalid)
    return invalid


def execute(plan,state):
    if any(a['version']!=code_version() for a in plan['adapters'].values()): raise ValueError('implementation changed; compile a new plan')
    state=owned(state); store=install_plan(plan,state)
    with plan_lock(state):
        live=json.loads((state/'plan.json').read_text())
        if digest(live)!=digest(plan): raise ValueError('plan changed before dispatch')
        submit_plan(store,live)
        invalid=audit_cached(store,live,mutate=True)
        materialize=batch_callback(live)
        def guarded_batch(queue):
            # Finish supervising already-running work, then invalidate any
            # affected recovered result before it can admit new dependents.
            _retain_invalidations(queue,invalid)
            return materialize(queue)
        result=run(store,state,live['capacities'],max_parallel=live['max_parallel'],poll_s=0.05,batch_callback=guarded_batch)
        audit_cached(store,live,mutate=True)
        report=measure(store,live)
        atomic_json(state/'report.json',report)
        return report


def measure(store,plan):
    if isinstance(store, Store):
        with store._connection() as conn:
            store = _read_snapshot(conn)
    invalid=audit_cached(store,plan)
    rows=[{**r,'state':'blocked','reason':invalid[r['id']]} if r['id'] in invalid
          and r['state'] not in {'running','uncertain'} else r for r in current_rows(store,plan)]
    view=Snapshot(rows); blocked={'resources':[],'evidence':[],'other':[]}
    for r in rows:
        if r['state']=='blocked':
            reason=r.get('reason',''); group='resources' if reason.startswith('resource:') else 'evidence' if reason.startswith('evidence:') else 'other'
            blocked[group].append({'id':r['id'],'reason':reason})
    from .latency import samples, summarize
    handoffs = samples(rows, plan['capacities'], plan['max_parallel'],
                       attempt_events=store.attempt_events, reservation_rows=store.jobs())
    available = [x['capacity_available_to_start_s'] for x in handoffs
                 if x['capacity_available_to_start_s'] is not None]
    statuses=module_status(view,plan)
    _,mapping=compile_plan(plan)
    for status in statuses:
        failures=[invalid[job] for job in mapping[status['module']].values() if job in invalid]
        failures.extend(invalid[row['id']] for row in rows if row['id'] in invalid
                        and row['spec']['kind']=='batch'
                        and mapping[status['module']]['review'] in row['spec']['deps'])
        if failures: status.update(state='evidence_invalid',reason=failures[0])
    return {'evidence_audit':{'invalid':[{'id':job,'reason':reason} for job,reason in invalid.items()],'scope':'current plan only; superseded history retained but not reused'},'capacity_available_handoff_s':summarize(available),'handoff_samples':handoffs,'schema':1,'mode':'test_only','modules':statuses,'metrics':metrics(view),
            'handoff_capacity_scope':'Relay reservations only. Host availability and dispatch delay are unverified. Null samples indicate incomplete attempt history.',
            'attempts':sum(r['attempt'] for r in rows),'failed_attempts':sum(r['attempt'] for r in rows if r['state']=='failed'),
            'ai_calls':sum((((r.get('result') or {}).get('receipt') or {}).get('data') or {}).get('ai_calls',0) for r in rows),
            'ai_implementation_review_seconds':None,'repeated_model_reviews':0,
            'integrated_modules':0,'integrated_modules_per_day':0,
            'blocked':blocked,'ready_undispatched':[r['id'] for r in rows if r['state']=='queued' and r.get('ready_at') is not None],
            'ownership':'existing dispatcher retained; no transfer or publication',
            'release_requirements_remaining':'product gates in contracts, independent controller review, Linux qualification, complete pilot and verified transfer',
            'note':'AI authoring time is not measured by the queue. Zero integration is observed for this pilot, not a throughput projection.'}


def read_report(state):
    """Read existing state without Store initialization, transitions or launch."""
    state=owned(state); plan=json.loads((state/'plan.json').read_text())
    uri='file:'+quote(str(state/'queue.sqlite3'),safe='/')+'?mode=ro'
    with sqlite3.connect(uri,uri=True) as conn:
        snapshot = _read_snapshot(conn)
    return measure(snapshot,plan)


def prepare(root):
    root=owned(root); root.mkdir(parents=True,exist_ok=True); inputs=root/'inputs'; inputs.mkdir(exist_ok=True)
    specs=[('console-ui','/private/tmp/deepsignal/pilot-combination-20261120/recut/repo','bff54ec722bd8bf2c0ee949c91528642e0140e26','console.md',
            ['/private/tmp/deepsignal/pilot-combination-20261120/return-qualification/candidate.sha','/private/tmp/deepsignal/pilot-combination-20261120/return-qualification/self-check.log','/private/tmp/deepsignal/pilot-combination-20261120/return-decision/answer.md'],
            [{'name':'independent-review','status':'hold','reason':'Exact-head independent HOLD: three operator-display findings; recorded in return-decision/answer.md','independent':True},
             {'name':'linux-release-gate','status':'missing','reason':'Existing Linux run 44695593537 must be imported with authenticated workflow and exact-candidate binding'}]),
           ('stream-health-view','/private/tmp/deepsignal/stream-health-view/repo','1dc7a5e001f9535520ac8986922253c2ea20e01e','stream-health-view.md',
            ['/private/tmp/deepsignal/stream-health-view/qualification/candidate.sha','/private/tmp/deepsignal/stream-health-view/qualification/self-check.log','/private/tmp/deepsignal/stream-health-view/qualification/linux-final.log'],
            [{'name':'current-integration','status':'missing','reason':'Re-cut from old 1dc7a5e base onto current integration and qualify combined source'},
             {'name':'machine-release-gate','status':'hold','reason':'Historical self-check is RED; new policy passing elsewhere does not qualify this source'},
             {'name':'independent-review','status':'missing','reason':'No independent final review exists for this candidate','independent':True}])]
    contracts=[]
    for name,repo,base,design,evidence,gates in specs:
        repo=owned(repo); commit=git(repo,'rev-parse','HEAD')
        policy=[DESK/'docs/designs'/design,DESK/'docs/RULES.md',DESK/'docs/DECISIONS.md']
        deps=repo/'contrib/deepsignal/console/node_modules'
        accepts=[{'name':'frontend-unit-tests','cwd':'contrib/deepsignal/console','argv':['npm','test','--','--maxWorkers=1'],'timeout_s':180},
                 {'name':'frontend-lint','cwd':'contrib/deepsignal/console','argv':['npm','run','lint'],'timeout_s':60},
                 {'name':'frontend-type-check','cwd':'contrib/deepsignal/console','argv':['npm','run','type-check'],'timeout_s':90}]
        c={'schema':1,'project':'deepsignal','module':name,'mode':'test_only','repository':str(repo),'commit':commit,'tree':git(repo,'rev-parse',commit+'^{tree}'),
           'integration_base':base,'policy_files':[file_record(p) for p in policy],'prior_evidence':[file_record(p) for p in evidence],
           'acceptance':accepts,'required_gates':gates,'scientific_change':False,'author_runs':['existing-product-authors'],
           'dependency_copies':[{'source':str(deps),'destination':'contrib/deepsignal/console/node_modules','tree_digest':digest(tree_manifest(deps,links=True)),
                                 'lockfiles':[file_record(repo/'contrib/deepsignal/console/package-lock.json')]}],
           'scope':'controller pilot verification of existing exact source; full design/browser/security/Linux gates remain separate'}
        path=inputs/(name+'.json'); atomic_json(path,c); contracts.append(path)
    manifest=json.loads((DESK/'docs/units.json').read_text())
    atomic_json(root/'inventory.json',{'desk_commit':git(DESK,'rev-parse','HEAD'),'units':manifest['units'],'selected':[x[0] for x in specs],
                                     'scope':'existing approved candidates only; paused modules remain paused'})
    plan=build_plan(contracts); atomic_json(root/'plan.json',plan); return plan
