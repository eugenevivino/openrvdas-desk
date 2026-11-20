"""Short generated-bundle fixtures. No npm build or real machine guard runs."""
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch
import test_project
from dsrelay import adapter


class BundleTests(unittest.TestCase):
    setUp = test_project.ProjectTests.setUp
    tearDown = test_project.ProjectTests.tearDown
    candidate = test_project.ProjectTests.candidate

    def prepare(self):
        distribution = self.repo / 'contrib/deepsignal/console/dist'
        distribution.mkdir(parents=True)
        (distribution / 'index.js').write_text('old bundle\n')
        subprocess.run(['git', '-C', str(self.repo), 'add', '.'], check=True)
        subprocess.run(['git', '-C', str(self.repo), 'commit', '-qm', 'bundle fixture'], check=True)
        self.c['commit'] = subprocess.check_output(['git', '-C', str(self.repo), 'rev-parse', 'HEAD'], text=True).strip()
        self.c['tree'] = subprocess.check_output(['git', '-C', str(self.repo), 'rev-parse', 'HEAD^{tree}'], text=True).strip()
        candidate = Path(self.candidate()['candidate'])
        attempt = self.root / 'bundle'
        attempt.mkdir()
        return candidate, attempt

    def build(self, candidate, attempt, build):
        with patch.object(adapter, 'admission'), patch.object(adapter, 'LOCAL_LOCK', self.root / 'lock'), patch.object(adapter, 'command', build):
            return adapter.build_bundle({**self.c, 'build_console_bundle': True}, candidate, attempt)

    def test_bundle_is_committed_and_source_identity_retained(self):
        candidate, attempt = self.prepare()
        def build(argv, cwd, env, log, timeout):
            (cwd / 'dist/index.js').write_text('new bundle\n')
            log.write_text('fixture build passed\n')
            return 0
        result = self.build(candidate, attempt, build)
        self.assertNotEqual(result['commit'], self.c['commit'])
        self.assertEqual(result['source_commit'], self.c['commit'])
        self.assertEqual(subprocess.check_output(['git', '-C', str(candidate), 'show', '-s', '--format=%P'], text=True).strip(), self.c['commit'])
        self.assertEqual((candidate / 'module.py').read_text(), 'VALUE = 42\n')

    def test_staged_source_change_cannot_enter_generated_commit(self):
        candidate, attempt = self.prepare()
        def build(argv, cwd, env, log, timeout):
            (candidate / 'module.py').write_text('VALUE = 0\n')
            subprocess.run(['git', '-C', str(candidate), 'add', 'module.py'], check=True)
            return 0
        with self.assertRaisesRegex(ValueError, 'outside generated'):
            self.build(candidate, attempt, build)
        self.assertEqual(subprocess.check_output(['git', '-C', str(candidate), 'rev-parse', 'HEAD'], text=True).strip(), self.c['commit'])

    def test_new_ignored_bundle_asset_is_in_generated_commit(self):
        (self.repo / '.gitignore').write_text('generated-*.js\n')
        candidate, attempt = self.prepare()
        def build(argv, cwd, env, log, timeout):
            (cwd / 'dist/generated-hash.js').write_text('new hashed asset\n')
            return 0
        self.build(candidate, attempt, build)
        value = subprocess.check_output(['git', '-C', str(candidate), 'show',
                 'HEAD:contrib/deepsignal/console/dist/generated-hash.js'], text=True)
        self.assertEqual(value, 'new hashed asset\n')

    def test_new_untracked_source_file_refuses_generated_commit(self):
        candidate, attempt = self.prepare()
        def build(argv, cwd, env, log, timeout):
            (candidate / 'new_source.py').write_text('VALUE = 0\n')
            return 0
        with self.assertRaisesRegex(ValueError, 'outside generated'):
            self.build(candidate, attempt, build)

    def test_dirty_index_refuses_build_before_running_command(self):
        candidate, attempt = self.prepare()
        (candidate / 'module.py').write_text('VALUE = 0\n')
        subprocess.run(['git', '-C', str(candidate), 'add', 'module.py'], check=True)
        with self.assertRaisesRegex(ValueError, 'tracked source changed'):
            self.build(candidate, attempt, lambda *args: self.fail('dirty input executed'))
