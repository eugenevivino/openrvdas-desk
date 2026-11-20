"""Fail-closed source, dependency and imported evidence identity checks."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from dsrelay import common


SCRATCH = Path('/private/tmp/deepsignal/relay-20261120/tests')
SCRATCH.mkdir(parents=True, exist_ok=True)


class IdentityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=SCRATCH)
        self.root = Path(self.temp.name)
        self.candidate = self.root / 'candidate'
        self.candidate.mkdir()
        (self.candidate / 'module.py').write_text('VALUE = 42\n')

    def tearDown(self):
        self.temp.cleanup()

    def test_added_python_import_and_sitecustomize_are_detected(self):
        manifest = common.tree_manifest(self.candidate)
        for name in ('shadow.py', 'sitecustomize.py'):
            added = self.candidate / name
            added.write_text('VALUE = 7\n')
            with self.assertRaisesRegex(ValueError, 'added, removed or modified'):
                common.verify_tree(self.candidate, manifest)
            added.unlink()
        common.verify_tree(self.candidate, manifest)

    def test_removed_or_modified_source_is_detected(self):
        manifest = common.tree_manifest(self.candidate)
        source = self.candidate / 'module.py'
        source.write_text('VALUE = 7\n')
        with self.assertRaises(ValueError):
            common.verify_tree(self.candidate, manifest)
        source.unlink()
        with self.assertRaises(ValueError):
            common.verify_tree(self.candidate, manifest)

    def test_dependency_addition_and_mutation_are_detected(self):
        deps = self.candidate / 'node_modules'
        deps.mkdir()
        entry = deps / 'package.js'
        entry.write_text('export const value = 1;')
        manifest = common.tree_manifest(deps, links=True)
        extra = deps / 'unexpected.js'
        extra.write_text('export const value = 2;')
        with self.assertRaises(ValueError):
            common.verify_tree(deps, manifest, links=True)
        extra.unlink()
        entry.write_text('export const value = 3;')
        with self.assertRaises(ValueError):
            common.verify_tree(deps, manifest, links=True)

    def test_internal_file_and_directory_links_are_recorded(self):
        directory = self.candidate / 'package'
        directory.mkdir()
        (directory / 'entry.js').write_text('export {};')
        (self.candidate / 'package-alias').symlink_to('package', target_is_directory=True)
        (self.candidate / 'module-alias').symlink_to('module.py')
        manifest = common.tree_manifest(self.candidate, links=True)
        self.assertEqual(manifest['package-alias'], 'link:package')
        self.assertEqual(manifest['module-alias'], 'link:module.py')
        common.verify_tree(self.candidate, manifest, links=True)
        with self.assertRaises(ValueError):
            common.verify_tree(self.candidate, manifest)

    def test_dangling_link_cannot_disappear_from_manifest(self):
        (self.candidate / 'dangling').symlink_to('absent')
        for links in (False, True):
            with self.assertRaisesRegex(ValueError, 'dangling'):
                common.tree_manifest(self.candidate, links=links)

    def test_external_link_is_rejected_even_with_link_support(self):
        outside = self.root / 'outside'
        outside.write_text('unrelated')
        (self.candidate / 'external').symlink_to(outside)
        with self.assertRaises(ValueError):
            common.tree_manifest(self.candidate, links=True)

    def test_changed_symlink_target_is_detected(self):
        (self.candidate / 'second.py').write_text('VALUE = 42\n')
        alias = self.candidate / 'alias'
        alias.symlink_to('module.py')
        manifest = common.tree_manifest(self.candidate, links=True)
        alias.unlink()
        alias.symlink_to('second.py')
        with self.assertRaises(ValueError):
            common.verify_tree(self.candidate, manifest, links=True)

    def test_exact_cache_directory_exclusion_does_not_hide_neighbors(self):
        manifest = common.tree_manifest(self.candidate)
        cache = self.candidate / '.pytest_cache'
        cache.mkdir()
        (cache / 'lastfailed').write_text('{}')
        common.verify_tree(self.candidate, manifest, exclude=('.pytest_cache',))
        (self.candidate / '.pytest_cache.py').write_text('print(1)')
        with self.assertRaises(ValueError):
            common.verify_tree(self.candidate, manifest, exclude=('.pytest_cache',))

    def test_broad_extensions_and_arbitrary_source_exclusions_refused(self):
        for exclude in ('*.py', 'module.py', '../node_modules', '.', '/tmp/node_modules'):
            with self.assertRaises(ValueError):
                common.tree_manifest(self.candidate, exclude=(exclude,))

    def test_explicit_subset_cannot_escape_candidate(self):
        for name in ('../outside', '/etc/hosts', './module.py'):
            with self.assertRaises(ValueError):
                common.tree_manifest(self.candidate, paths=[name])

    def test_code_version_covers_both_packages_and_nested_code(self):
        package = self.root / 'code'
        for name in ('relay', 'dsrelay'):
            (package / name).mkdir(parents=True)
            (package / name / '__init__.py').write_text('')
        nested = package / 'relay' / 'nested'
        nested.mkdir()
        worker = nested / 'worker.py'
        worker.write_text('VERSION = 1')
        with patch.object(common, '__file__', str(package / 'dsrelay' / 'common.py')):
            first = common.code_version()
            worker.write_text('VERSION = 2')
            second = common.code_version()
            (package / 'dsrelay' / 'adapter.py').write_text('VERSION = 1')
            third = common.code_version()
        self.assertEqual(len(first), 64)
        self.assertEqual(len({first, second, third}), 3)

    def gate(self):
        evidence = self.root / 'review.txt'
        evidence.write_text('Verdict: PASS')
        contract = {'commit': 'a' * 40, 'author_runs': ['author']}
        gate = {'name': 'independent-review', 'status': 'pass',
                'candidate_commit': contract['commit'], 'independent': True,
                'reviewer_run': 'someone-else', 'verifier': 'trusted-label',
                'evidence': [common.file_record(evidence)]}
        return gate, contract

    def test_hashed_passing_text_and_verifier_label_cannot_approve(self):
        gate, contract = self.gate()
        with self.assertRaisesRegex(ValueError, 'unsupported gate verifier'):
            common.verify_gate(gate, contract)

    def test_gate_rejects_changed_evidence_before_verifier(self):
        gate, contract = self.gate()
        Path(gate['evidence'][0]['path']).write_text('Verdict: HOLD')
        with self.assertRaisesRegex(ValueError, 'evidence changed'):
            common.verify_gate(gate, contract)

    def test_hold_and_wrong_candidate_remain_failures(self):
        gate, contract = self.gate()
        gate.update(status='hold', reason='wrong reading')
        with self.assertRaisesRegex(ValueError, 'wrong reading'):
            common.verify_gate(gate, contract)
        gate.update(status='pass', candidate_commit='b' * 40)
        with self.assertRaisesRegex(ValueError, 'candidate commit mismatch'):
            common.verify_gate(gate, contract)

    def test_independence_requires_distinct_reviewer_run(self):
        gate, contract = self.gate()
        gate['reviewer_run'] = 'author'
        with self.assertRaisesRegex(ValueError, 'independent reviewer'):
            common.verify_gate(gate, contract)

    def test_scientific_reference_requires_readable_hashed_records(self):
        for records in (None, True, 'present', [{'path': 'label'}]):
            with self.assertRaises(ValueError):
                common.verify_reference_evidence({'scientific_change': True,
                                                 'independent_reference_evidence': records})
        reference = self.root / 'recorded-cruise.csv'
        reference.write_text('time,value\n0,42\n')
        contract = {'scientific_change': True,
                    'independent_reference_evidence': [common.file_record(reference)]}
        common.verify_reference_evidence(contract)
        reference.write_text('time,value\n0,0\n')
        with self.assertRaisesRegex(ValueError, 'evidence changed'):
            common.verify_reference_evidence(contract)


if __name__ == '__main__':
    unittest.main()
