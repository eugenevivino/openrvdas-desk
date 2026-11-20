"""Content identities for trusted local DeepSignal plans."""
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess

ROOT = Path('/private/tmp/deepsignal')

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for part in iter(lambda: f.read(1048576), b''): h.update(part)
    return h.hexdigest()

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()

def owned(path):
    p = Path(path).resolve()
    if not p.is_relative_to(ROOT): raise ValueError('outside DeepSignal scratch: ' + str(p))
    return p

def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(owned(repo)), *args], text=True).strip()

def file_record(path):
    p = owned(path)
    return {'path': str(p), 'sha256': sha(p)}

def verify_files(records):
    if not isinstance(records, (list, tuple)):
        raise ValueError('evidence records must be a list')
    for r in records:
        if (not isinstance(r, dict) or set(r) != {'path', 'sha256'}
                or not isinstance(r['path'], str)
                or not isinstance(r['sha256'], str)
                or not re.fullmatch('[0-9a-f]{64}', r['sha256'])):
            raise ValueError('invalid hashed evidence record')
        if file_record(r['path']) != r: raise ValueError('evidence changed: ' + r['path'])


def _relative(name):
    if not isinstance(name, str) or not name or '\\' in name:
        raise ValueError('manifest paths must be relative POSIX paths')
    p = Path(name)
    if p.is_absolute() or '..' in p.parts or str(p) != name or name == '.':
        raise ValueError('unsafe manifest path: ' + name)
    return p


def _exclusions(exclude):
    # Only exact cache/dependency directory paths may be omitted. Callers that
    # exclude node_modules must independently verify its dependency manifest.
    allowed = {'.git', '__pycache__', '.pytest_cache', '.mypy_cache',
               '.ruff_cache', '.vite', '.vite-temp', '.tmp', 'node_modules'}
    result = {'.git'}
    for name in exclude:
        p = _relative(name)
        if p.name not in allowed:
            raise ValueError('only named cache/dependency directories may be excluded')
        result.add(name)
    return result


def tree_manifest(root, paths=None, links=False, exclude=()):
    root = owned(root)
    if not root.is_dir():
        raise ValueError('manifest root must be a directory')
    excluded = _exclusions(exclude)
    def omitted(name):
        return any(name == e or name.startswith(e + '/') for e in excluded)
    def unreadable(error):
        raise error
    if paths is None:
        paths = []
        for directory, dirs, files in os.walk(root, followlinks=False, onerror=unreadable):
            for name in list(dirs):
                p = Path(directory) / name
                relative = p.relative_to(root).as_posix()
                if omitted(relative):
                    dirs.remove(name)
                elif p.is_symlink():
                    paths.append(relative)
                    dirs.remove(name)
            paths.extend((Path(directory) / name).relative_to(root).as_posix()
                         for name in files
                         if not omitted((Path(directory) / name).relative_to(root).as_posix()))
    result = {}
    for name in sorted(paths):
        p = root / _relative(name)
        if omitted(name):
            continue
        if p.is_symlink():
            try:
                target = p.resolve(strict=True)
            except (OSError, RuntimeError) as exc:
                raise ValueError('dangling or cyclic source symlink: ' + name) from exc
            if links and target.is_relative_to(root):
                result[name] = 'link:' + str(p.readlink()); continue
            raise ValueError('source symlink requires explicit support: ' + name)
        if not p.resolve(strict=True).is_relative_to(root): raise ValueError('source escapes candidate')
        if not p.is_file():
            raise ValueError('manifest entry is not a regular file: ' + name)
        result[name] = f'file:{stat.S_IMODE(p.stat().st_mode):o}:{sha(p)}'
    return result


def verify_tree(root, manifest, links=False, exclude=()):
    if not isinstance(manifest, dict):
        raise ValueError('manifest must be an object')
    for name in manifest:
        _relative(name)
    if tree_manifest(root, links=links, exclude=exclude) != manifest:
        raise ValueError('candidate source changed: added, removed or modified entries')


def code_version():
    package = Path(__file__).resolve().parent.parent
    return digest({p.relative_to(package).as_posix(): sha(p)
                   for name in ('relay', 'dsrelay')
                   for p in sorted((package / name).rglob('*.py'))})


def verify_reference_evidence(contract):
    records = contract.get('independent_reference_evidence', [])
    if contract.get('scientific_change') and not records:
        raise ValueError('independent reference dataset required')
    verify_files(records)


def verify_gate(gate, contract):
    """Refuse unverifiable imported approvals; labels are never proof.

    No native release/review receipt verifier has been qualified for this pilot.
    Adding one requires an explicit format, identity and integrity validator.
    This function deliberately has no passing verifier type yet.
    """
    if not isinstance(gate, dict):
        raise ValueError('gate must be an object')
    if gate.get('status') != 'pass':
        raise ValueError(gate.get('reason') or 'gate has no passing evidence')
    if gate.get('candidate_commit') != contract.get('commit'):
        raise ValueError('gate candidate commit mismatch')
    if not gate.get('evidence'):
        raise ValueError('gate needs hashed evidence')
    verify_files(gate['evidence'])
    verify_reference_evidence(contract)
    if gate.get('independent') and (not gate.get('reviewer_run')
            or gate['reviewer_run'] in contract.get('author_runs', [])):
        raise ValueError('independent reviewer identity missing')
    raise ValueError('unsupported gate verifier: ' + str(gate.get('verifier')))

def load_contract(inputs):
    r = inputs['contract']; verify_files([r]); c = json.loads(Path(r['path']).read_text())
    if c['schema'] != 1 or c['project'] != 'deepsignal' or c['mode'] != 'test_only':
        raise ValueError('only DeepSignal test-only contracts supported')
    if git(c['repository'], 'rev-parse', c['commit']+'^{commit}') != c['commit']: raise ValueError('exact commit required')
    if git(c['repository'], 'rev-parse', c['commit']+'^{tree}') != c['tree']: raise ValueError('source tree mismatch')
    verify_files(c['policy_files'] + c['prior_evidence'])
    if 'independent_reference_evidence' in c:
        verify_files(c['independent_reference_evidence'])
    if not c['acceptance'] or not c['required_gates']: raise ValueError('checks and explicit gates required')
    return c
