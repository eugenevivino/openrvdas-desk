"""Candidate metadata and copied dependency binding regressions."""
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch
import test_project
from dsrelay import adapter, common


class CandidateIdentityTests(unittest.TestCase):
    setUp = test_project.ProjectTests.setUp
    tearDown = test_project.ProjectTests.tearDown
    candidate = test_project.ProjectTests.candidate

    def test_same_tree_new_commit_invalidates_candidate(self):
        data = self.candidate()
        subprocess.run(['git', '-C', data['candidate'], '-c', 'user.name=Fixture',
                        '-c', 'user.email=fixture@example.invalid', 'commit',
                        '--allow-empty', '-qm', 'different identity'], check=True)
        with self.assertRaisesRegex(ValueError, 'Git identity'):
            adapter.verify_candidate(data)

    def test_mode_only_change_invalidates_candidate(self):
        data = self.candidate()
        source = Path(data['candidate']) / 'module.py'
        source.chmod(source.stat().st_mode ^ 0o100)
        with self.assertRaises(ValueError):
            adapter.verify_candidate(data)

    def test_dependency_change_during_copy_is_not_sealed_as_valid(self):
        deps = self.root / 'installed'
        deps.mkdir()
        package = deps / 'package.js'
        package.write_text('original')
        lock = self.repo / 'package-lock.json'
        lock.write_text('{}')
        subprocess.run(['git', '-C', str(self.repo), 'add', '.'], check=True)
        subprocess.run(['git', '-C', str(self.repo), 'commit', '-qm', 'lockfile'], check=True)
        self.c.update(commit=common.git(self.repo, 'rev-parse', 'HEAD'),
                      tree=common.git(self.repo, 'rev-parse', 'HEAD^{tree}'))
        self.c['dependency_copies'] = [{'source': str(deps), 'destination': 'node_modules',
            'lockfiles': [common.file_record(lock)],
            'tree_digest': common.digest(common.tree_manifest(deps, links=True))}]
        real_run = subprocess.run
        def racing_copy(argv, **kwargs):
            if argv[0] == 'cp':
                package.write_text('changed during dependency copy')
            return real_run(argv, **kwargs)
        with patch.object(adapter.subprocess, 'run', side_effect=racing_copy):
            with self.assertRaisesRegex(ValueError, 'copied dependencies'):
                self.candidate()
