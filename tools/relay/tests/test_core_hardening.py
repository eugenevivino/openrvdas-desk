"""Activation recovery and bounded capture on real local supervisor paths."""
from contextlib import redirect_stdout
import copy
import fcntl
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from relay.cli import install_plan, main, make_demo_plan
from relay.engine import run
from relay.plan import compile_plan
from relay.store import Store
from relay.worker import OUTPUT_LIMIT_BYTES


class HardeningTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='relay-hardening-')
        self.root = Path(self.tmp.name)
        self.state = self.root / 'state'
        self.plan = make_demo_plan()

    def tearDown(self):
        self.tmp.cleanup()

    def test_existing_controller_refuses_install_without_publication(self):
        self.state.mkdir()
        with (self.state / 'controller.lock').open('a+') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with self.assertRaisesRegex(RuntimeError, 'another Relay controller'):
                install_plan(self.plan, self.state)
        self.assertFalse((self.state / 'plan.json').exists())
        self.assertFalse((self.state / 'queue.sqlite3').exists())

    def test_failed_publication_makes_no_jobs_runnable(self):
        with patch('relay.cli.atomic_json', side_effect=OSError('disk unavailable')):
            with self.assertRaisesRegex(OSError, 'disk unavailable'):
                install_plan(self.plan, self.state)
        self.assertEqual(Store(self.state / 'queue.sqlite3').jobs(), [])
        self.assertFalse((self.state / 'plan.json').exists())

    def test_interrupted_submission_recovers_published_plan_on_run(self):
        original = Store.submit
        count = 0

        def interrupted(store, spec):
            nonlocal count
            count += 1
            if count == 3:
                raise OSError('interrupted installation')
            return original(store, spec)

        with patch.object(Store, 'submit', interrupted):
            with self.assertRaisesRegex(OSError, 'interrupted installation'):
                install_plan(self.plan, self.state)
        self.assertEqual(json.loads((self.state / 'plan.json').read_text()), self.plan)
        self.assertEqual(len(Store(self.state / 'queue.sqlite3').jobs()), 2)
        with redirect_stdout(io.StringIO()):
            self.assertEqual(main(['--state', str(self.state), 'run']), 0)
        rows = Store(self.state / 'queue.sqlite3').jobs()
        required, _ = compile_plan(self.plan)
        self.assertTrue({j['id'] for j in required} <= {j['id'] for j in rows})
        self.assertTrue(all(row['state'] == 'passed' for row in rows))
        self.assertTrue(all(row['attempt'] == 1 for row in rows))

    def test_idle_watcher_prevents_plan_replacement_and_unchanged_submission(self):
        install_plan(self.plan, self.state)
        with redirect_stdout(io.StringIO()):
            self.assertEqual(main(['--state', str(self.state), 'run']), 0)
        store = Store(self.state / 'queue.sqlite3')
        before = max(e['id'] for e in store.events(1000))
        proc = subprocess.Popen(
            [sys.executable, '-m', 'relay', '--state', str(self.state), 'run', '--watch'],
            cwd=Path(__file__).resolve().parents[1], stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, start_new_session=True)
        try:
            deadline = time.monotonic() + 5
            while time.monotonic() < deadline:
                if any(e['id'] > before and e['kind'] == 'controller_started'
                       for e in store.events(1000)):
                    break
                time.sleep(0.02)
            else:
                self.fail('watcher did not acquire its locks')
            changed = copy.deepcopy(self.plan)
            changed['policy_version'] = 'updated-policy'
            for plan in (changed, self.plan):
                with self.assertRaisesRegex(RuntimeError, 'plan activation'):
                    install_plan(plan, self.state)
            self.assertEqual(json.loads((self.state / 'plan.json').read_text()), self.plan)
            self.assertTrue(all(row['attempt'] == 1 for row in store.jobs()))
        finally:
            proc.terminate()
            proc.wait(timeout=5)

    def execute_output(self, code, timeout=5):
        store = Store(self.root / 'jobs.sqlite')
        prefix = ('import json, os, pathlib, sys\n'
                  'r=json.loads(pathlib.Path(os.environ["RELAY_INPUT_FILE"]).read_text())\n')
        receipt = ('\npathlib.Path(os.environ["RELAY_RESULT_FILE"]).write_text(json.dumps('
                   '{"schema":1,"outcome":"pass","input_digest":r["input_digest"],'
                   '"summary":"fixture","evidence":[],"data":{}}))\n')
        spec = {'id': 'output', 'kind': 'piece', 'deps': [],
                'command': [sys.executable, '-c', prefix + code + receipt],
                'cwd': str(self.root), 'inputs': {}, 'resources': {'cpu': 1},
                'timeout_s': timeout, 'max_attempts': 1, 'retry_exit_codes': [],
                'approval_required': False, 'receipt_required': True, 'priority': 0}
        store.submit(spec)
        independent = copy.deepcopy(spec)
        independent['id'] = 'independent'
        independent['command'] = [sys.executable, '-c', prefix + receipt]
        store.submit(independent)
        run(store, self.state, {'cpu': 1}, poll_s=0.02)
        self.assertEqual(store.get('independent')['state'], 'passed')
        return store.get('output')

    def test_output_limit_fails_owned_writer_and_independent_work_proceeds(self):
        row = self.execute_output('while True: sys.stdout.buffer.write(b"x" * 65536)\n')
        self.assertEqual(row['state'], 'failed')
        self.assertTrue(row['result']['output_limited'])
        self.assertIn('output exceeded', row['reason'])
        self.assertEqual((Path(row['attempt_dir']) / 'output.log').stat().st_size,
                         OUTPUT_LIMIT_BYTES)

    def test_exact_limit_and_final_stderr_bytes_are_preserved(self):
        code = (f'sys.stdout.buffer.write(b"x" * {OUTPUT_LIMIT_BYTES - 4})\n'
                'sys.stdout.buffer.flush()\nos.write(2,b"TAIL")\n')
        row = self.execute_output(code)
        self.assertEqual(row['state'], 'passed')
        self.assertFalse(row['result']['output_limited'])
        output = (Path(row['attempt_dir']) / 'output.log').read_bytes()
        self.assertEqual(len(output), OUTPUT_LIMIT_BYTES)
        self.assertEqual(output[-4:], b'TAIL')

    def test_one_byte_over_limit_fails_even_when_adapter_exits_successfully(self):
        row = self.execute_output(f'sys.stdout.buffer.write(b"x" * {OUTPUT_LIMIT_BYTES + 1})\n')
        self.assertEqual(row['state'], 'failed')
        self.assertTrue(row['result']['output_limited'])

    def test_closed_output_does_not_disable_timeout(self):
        row = self.execute_output('import time\nos.close(1)\nos.close(2)\ntime.sleep(5)\n', timeout=0.2)
        self.assertEqual(row['state'], 'failed')
        self.assertTrue(row['result']['timed_out'])


if __name__ == '__main__':
    unittest.main()
