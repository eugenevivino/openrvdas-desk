"""Engineering adapters; supplied Relay owns scheduling and supervision."""
import json
from contextlib import contextmanager
import os
from pathlib import Path
import shutil
import select
import subprocess
import sys
import tarfile
import time
from .common import owned, file_record, verify_files, tree_manifest, verify_tree, load_contract, digest, code_version, verify_gate, verify_reference_evidence
from relay.worker import atomic_json

LOCAL_LOCK = Path("/private/tmp/deepsignal/.ds-codex.lock")
OUTPUT_LIMIT = 8 * 1024 * 1024

class Blocked(Exception): pass

def command(argv, cwd, env, log, timeout):
    """Bound each test log and runtime; descendants stay in Relay's owned group."""
    started=time.monotonic(); count=0
    with log.open("wb") as out:
        p=subprocess.Popen(argv,cwd=cwd,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL)
        try:
            os.set_blocking(p.stdout.fileno(),False)
            eof=False
            while p.poll() is None or not eof:
                if time.monotonic()-started > timeout: raise TimeoutError("test command timeout")
                if eof:
                    time.sleep(0.02); continue
                ready,_,_=select.select([p.stdout],[],[],0.05)
                if ready:
                    data=os.read(p.stdout.fileno(),65536)
                    if not data: eof=True; continue
                    retained=data[:max(0,OUTPUT_LIMIT-count)]; out.write(retained); count+=len(retained)
                    if len(retained)!=len(data): raise ValueError("test output limit exceeded")
            return p.wait()
        finally:
            if p.poll() is None: p.kill()
            p.wait(); p.stdout.close()

def dependencies(request):
    result=[]
    for dep in request['dependencies'].values():
        r=dep['receipt']
        if r['outcome']!='pass': raise ValueError('nonpassing prerequisite')
        verify_files(r['data']['artifacts']); result.append(r['data'])
    return result

def admission_once(attempt):
    if shutil.disk_usage(attempt).free < 5*1024**3: raise Blocked('resource: disk below 5 GiB')
    p=subprocess.run([str(Path.home()/'bin/ds-codex'),'--dry-run','-m','gpt-6.2-sol','-'],cwd=attempt,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=30)
    (attempt/'admission.log').write_text(p.stdout)
    if p.returncode or 'RAM gate OK' not in p.stdout: raise Blocked('resource: existing RAM gate refused; see admission.log')
    n=subprocess.check_output(['/private/tmp/deepsignal/heavy-jobs.sh'],text=True,timeout=5).strip()
    if not n.isdigit() or int(n)>=2: raise Blocked('resource: machine cap reached or unverifiable')

def admission(attempt):
    deadline=time.monotonic()+360
    while True:
        try:
            admission_once(attempt)
            return
        except Blocked:
            if time.monotonic()>=deadline: raise
            time.sleep(5)


@contextmanager
def execution_slot(attempt):
    admission(attempt)
    lock=owned(LOCAL_LOCK)
    try: lock.mkdir()
    except FileExistsError: raise Blocked('resource: DeepSignal execution slot owned')
    (lock/'pid').write_text(str(os.getpid())); (lock/'relay-owner').write_text(str(attempt))
    try: yield
    finally:
        if (lock/'relay-owner').exists() and (lock/'relay-owner').read_text()==str(attempt) and (lock/'pid').read_text()==str(os.getpid()):
            (lock/'relay-owner').unlink(); (lock/'pid').unlink(); lock.rmdir()

def build_bundle(c, candidate, attempt):
    if not c.get('build_console_bundle'): return c
    before=c['commit']
    with execution_slot(attempt):
        def git(*args):
            return subprocess.check_output(['git','-C',str(candidate),*args],text=True,timeout=30).strip()
        excluded=[d['destination'] for d in c.get('dependency_copies',[])]
        def source():
            return {k:v for k,v in tree_manifest(candidate,exclude=excluded).items()
                    if not k.startswith('contrib/deepsignal/console/dist/')}
        if git('rev-parse','HEAD')!=before or git('status','--porcelain','--untracked-files=no'):
            raise ValueError('bundle input HEAD or tracked source changed')
        original=source()
        env={'PATH':'/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin','HOME':str(attempt),'CI':'true'}
        rc=command(['npm','run','build'],candidate/'contrib/deepsignal/console',env,attempt/'bundle.log',120)
        if rc: raise ValueError('console bundle build failed')
        if git('rev-parse','HEAD')!=before or source()!=original:
            raise ValueError('bundle build changed source outside generated distribution')
        changed=git('diff','--name-only','-z','HEAD','--').split('\0')
        if any(x and not x.startswith('contrib/deepsignal/console/dist/') for x in changed):
            raise ValueError('bundle build changed source outside generated distribution')
        # Hash-named generated assets may match the repository's ignore rules.
        # The new candidate must actually contain every distribution file.
        subprocess.run(['git','-C',str(candidate),'add','-f','--','contrib/deepsignal/console/dist'],check=True)
        pending=subprocess.run(['git','-C',str(candidate),'diff','--cached','--quiet']).returncode
        if pending not in (0,1): raise ValueError('could not inspect bundle index')
        if pending:
            stamp=subprocess.check_output(['git','-C',str(candidate),'show','-s','--format=%cI',before],text=True).strip()
            env.update(GIT_AUTHOR_DATE=stamp,GIT_COMMITTER_DATE=stamp)
            subprocess.run(['git','-C',str(candidate),'-c','user.name=DeepSignal Relay','-c','user.email=relay@localhost','commit','-qm','Build exact Console distribution from '+before],env=env,check=True)
        if source()!=original or git('diff','--name-only','HEAD','--'):
            raise ValueError('bundle commit left unexpected source or distribution changes')
    pin=subprocess.check_output(['git','-C',str(candidate),'rev-parse','HEAD'],text=True).strip()
    tree=subprocess.check_output(['git','-C',str(candidate),'rev-parse','HEAD^{tree}'],text=True).strip()
    return {**c,'source_commit':before,'commit':pin,'tree':tree,'repository':str(candidate)}


def piece(c, attempt):
    archive=attempt/'source.tar'
    with archive.open('wb') as out:
        subprocess.run(['git','-C',c['repository'],'archive','--format=tar',c['commit']],stdout=out,check=True,timeout=60)
    return {'candidate_commit':c['commit'],'candidate_tree':c['tree'],'source_archive':str(archive),'artifacts':[file_record(archive)]}

def assemble(c, deps, attempt):
    sources=[d for d in deps if 'source_archive' in d]
    if len(sources)!=1 or sources[0]['candidate_commit']!=c['commit']: raise ValueError('wrong source snapshot')
    candidate=attempt/'candidate'; candidate.mkdir()
    # Keep the real commit for existing Git-aware qualification scripts.
    subprocess.run(['git','clone','-q','--no-hardlinks','--no-checkout',c['repository'],str(candidate)],check=True,timeout=120)
    subprocess.run(['git','-C',str(candidate),'checkout','-q','--detach',c['commit']],check=True,timeout=60)
    manifest=attempt/'source-manifest.json'; atomic_json(manifest,tree_manifest(candidate))
    dependency_manifests=[]
    source_exclusions=[]
    for dep in c.get('dependency_copies',[]):
        source=owned(dep['source']); verify_files(dep['lockfiles'])
        if digest(tree_manifest(source,links=True))!=dep['tree_digest']: raise ValueError('dependency tree changed')
        dest=candidate/dep['destination']
        for record in dep['lockfiles']:
            candidate_lock=dest.parent/Path(record['path']).name
            if file_record(candidate_lock)['sha256']!=record['sha256']: raise ValueError('candidate lockfile differs from installed dependencies')
        if not dest.resolve().is_relative_to(candidate) or dest.exists(): raise ValueError('unsafe dependency destination')
        subprocess.run(['cp','-cR' if sys.platform=='darwin' else '-R',str(source),str(dest)],check=True,timeout=120)
        exclusions=['.tmp','.vite','.vite-temp']
        dep_manifest=attempt/f'dependencies-{len(dependency_manifests)}.json'
        atomic_json(dep_manifest,tree_manifest(dest,links=True,exclude=exclusions))
        dependency_manifests.append({'root':str(dest),'manifest':file_record(dep_manifest),'exclude':exclusions})
        source_exclusions.append(dep['destination'])
    c=build_bundle(c,candidate,attempt)
    atomic_json(manifest,tree_manifest(candidate,exclude=source_exclusions))
    return {'candidate_commit':c['commit'],'candidate_tree':c['tree'],'candidate':str(candidate),'source_manifest':str(manifest),'contract':c,'source_exclusions':source_exclusions,'dependency_manifests':dependency_manifests,'artifacts':[file_record(manifest)]+[d['manifest'] for d in dependency_manifests]+c['policy_files']+c['prior_evidence']}

def verify_candidate(data):
    verify_tree(data['candidate'],json.loads(Path(data['source_manifest']).read_text()),exclude=data.get('source_exclusions',[]))
    for dep in data.get('dependency_manifests',[]):
        verify_files([dep['manifest']])
        verify_tree(dep['root'],json.loads(Path(dep['manifest']['path']).read_text()),links=True,exclude=dep['exclude'])


def checks(c, data, attempt):
    candidate=owned(data['candidate']); manifest=json.loads(Path(data['source_manifest']).read_text()); verify_candidate(data)
    c=data['contract']
    rows=[]
    with execution_slot(attempt):
        home=attempt/'home'; home.mkdir(exist_ok=True); tmp=attempt/'tmp'; tmp.mkdir(exist_ok=True)
        env={'PATH':'/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin','HOME':str(home),'TMPDIR':str(tmp),'LANG':'en_US.UTF-8','CI':'true','PYTHONDONTWRITEBYTECODE':'1','PYTHONNOUSERSITE':'1','PYTEST_ADDOPTS':'-p no:cacheprovider','OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'}
        browser_cache=Path.home()/'Library/Caches/ms-playwright'
        if browser_cache.is_dir(): env['PLAYWRIGHT_BROWSERS_PATH']=str(browser_cache)
        start=time.time()
        for i,spec in enumerate(c['acceptance']):
            cwd=(candidate/spec.get('cwd','.')).resolve()
            if not cwd.is_relative_to(candidate): raise ValueError('check cwd escapes candidate')
            before=time.time(); log=attempt/f'check-{i}.log'
            rc=command(spec['argv'],cwd,env,log,spec.get('timeout_s',120))
            rows.append({'name':spec['name'],'argv':spec['argv'],'returncode':rc,'started_at':before,'finished_at':time.time(),'log':file_record(log)})
            if rc: break
        report={'candidate_commit':c['commit'],'work_started_at':start,'commands':rows,'passed':len(rows)==len(c['acceptance']) and all(x['returncode']==0 for x in rows),'scope':'declared checks only, not scientific or release acceptance'}
        atomic_json(attempt/'checks.json',report); verify_candidate(data)
        return {**data,'checks':report,'artifacts':data['artifacts']+[file_record(attempt/'checks.json')]+[x['log'] for x in rows]}

def review(c, deps, attempt):
    test=next(d for d in deps if 'checks' in d)
    c=test['contract']
    if not test['checks']['passed']: raise Blocked('evidence: machine checks failed')
    missing=[]
    gate_artifacts=[]
    for g in c['required_gates']:
        try:
            verify_gate(g,c)
            gate_artifacts.extend(g['evidence'])
        except ValueError as exc:
            missing.append({'gate':g['name'],'reason':str(exc)})
    try:
        verify_reference_evidence(c)
    except ValueError as exc:
        missing.append({'gate':'scientific-reference','reason':str(exc)})
    record={'candidate_commit':c['commit'],'missing':missing,'request_ai':bool(missing) and all(x['gate']=='independent-review' for x in missing)}
    atomic_json(attempt/'review-request.json',record)
    if missing: raise Blocked('evidence: '+'; '.join(x['gate']+': '+x['reason'] for x in missing))
    return {**test,'review':record,'artifacts':test['artifacts']+gate_artifacts+c.get('independent_reference_evidence',[])+[file_record(attempt/'review-request.json')]}

def batch(inputs,deps,attempt):
    if inputs.get('integration_mode')!='test_only': raise ValueError('publication is not implemented')
    if not deps or any('review' not in d or d['review']['missing'] for d in deps): raise ValueError('reviewed candidates required')
    if len({(d['candidate_commit'],d['candidate_tree']) for d in deps})!=1:
        raise Blocked('integration: different candidates need re-cut and combined qualification')
    chosen=deps[0]; c=dict(chosen['contract']); c['acceptance']=[]; seen=set()
    for d in deps:
        if d['contract']['integration_base']!=c['integration_base']: raise Blocked('integration: incompatible bases')
        for check in d['contract']['acceptance']:
            key=digest(check)
            if key not in seen: c['acceptance'].append(check); seen.add(key)
    # checks intentionally uses the assembled contract, so retain the complete
    # union there instead of silently reverting to the first member's checks.
    result=checks(c,{**chosen,'contract':c},attempt)
    result['integration']={'mode':'test_only','merged':False,'modules':[d['contract']['module'] for d in deps]}
    return result

def main():
    request=json.loads(Path(os.environ['RELAY_INPUT_FILE']).read_text()); attempt=owned(os.environ['RELAY_ATTEMPT_DIR'])
    inputs=request['spec']['inputs']; stage=request['spec']['kind']; outcome='fail'; data={'artifacts':[]}; started=time.time()
    try:
        if inputs['adapter_version']!=code_version(): raise ValueError('adapter implementation changed since plan compilation')
        deps=dependencies(request)
        if stage=='batch': data=batch(inputs,deps,attempt)
        else:
            c=load_contract(inputs)
            if stage=='piece': data=piece(c,attempt)
            elif stage=='assemble': data=assemble(c,deps,attempt)
            elif stage=='test': data=checks(c,deps[0],attempt)
            elif stage=='review': data=review(c,deps,attempt)
            else: raise ValueError('unknown stage')
        outcome='pass' if data.get('checks',{}).get('passed',True) else 'fail'; summary=f'{stage}: {outcome}, declared scope only'
    except Blocked as e: outcome,summary='blocked',str(e)
    except Exception as e: summary=f'{type(e).__name__}: {e}'
    resource_wait = outcome=='blocked' and summary.startswith('resource:')
    if resource_wait: outcome='fail'
    data.update(adapter_started_at=started,adapter_finished_at=time.time(),ai_calls=0,resource_wait=resource_wait)
    for p in attempt.iterdir():
        if p.is_file() and p.name in {'review-request.json','checks.json','admission.log','bundle.log'} and str(p) not in {x['path'] for x in data['artifacts']}: data['artifacts'].append(file_record(p))
    atomic_json(Path(os.environ['RELAY_RESULT_FILE']),{'schema':1,'outcome':outcome,'input_digest':request['input_digest'],'summary':summary,'evidence':[x['path'] for x in data['artifacts']],'data':data})
    print(summary,flush=True)
    return 75 if resource_wait else 0 if outcome in ('pass','blocked') else 1

if __name__=='__main__': sys.exit(main())
