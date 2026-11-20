"""Pure routing fixtures; no accounts, subprocesses, storage or network."""
import copy
import unittest
from dsrelay.providers import select_provider


class ProviderTests(unittest.TestCase):
    def setUp(self):
        self.usage = {'verified': True, 'observed_at': 1000, 'ordinaryAllowed': True,
                      'applicable_windows': ['primary', 'secondary'],
                      'remaining_percent': {'primary': 7, 'secondary': 15}}
        self.successor = {'provider': 'approved-provider', 'approved': True,
                          'auth_ready': True, 'budget_permits': True}

    def choose(self, **kwargs):
        return select_provider(self.usage, now=1020, successor=self.successor, **kwargs)

    def test_exact_reserve_and_below_choose_only_approved_successor(self):
        for value, provider in ((0, 'approved-provider'), (0.99, 'approved-provider'),
                                (1, 'approved-provider'), (1.0001, 'codex')):
            for window in ('primary', 'secondary'):
                with self.subTest(value=value, window=window):
                    self.usage['remaining_percent'] = {'primary': 7, 'secondary': 15}
                    self.usage['remaining_percent'][window] = value
                    self.assertEqual(self.choose().provider, provider)

    def test_ordinary_access_denied_never_uses_credits_or_resets(self):
        self.usage.update(ordinaryAllowed=False, paidCredits=999, resets_at=1021)
        self.assertEqual(self.choose().provider, 'approved-provider')

    def test_successor_requires_explicit_auth_approval_and_budget(self):
        self.usage['remaining_percent']['primary'] = 1
        for key in ('approved', 'auth_ready', 'budget_permits'):
            for value in (False, None, 1, 'true'):
                with self.subTest(key=key, value=value):
                    successor = {**self.successor, key: value}
                    result = select_provider(self.usage, now=1020, successor=successor)
                    self.assertIsNone(result.provider); self.assertFalse(result.launch_new)
        self.assertFalse(select_provider(self.usage, now=1020).launch_new)

    def test_missing_unverified_stale_future_usage_never_falls_back(self):
        for usage in (None, {}, {**self.usage, 'verified': 1},
                      {**self.usage, 'observed_at': 959.9},
                      {**self.usage, 'observed_at': 1021}):
            result = select_provider(usage, now=1020, successor=self.successor)
            self.assertIsNone(result.provider); self.assertFalse(result.launch_new)

    def test_malformed_nan_bool_and_unknown_windows_fail_closed(self):
        for value in (None, True, '7', float('nan'), float('inf'), -1, 101, 10**1000):
            with self.subTest(value=value):
                self.usage['remaining_percent']['primary'] = value
                self.assertFalse(self.choose().launch_new)
                self.assertFalse(select_provider({**self.usage, 'observed_at': value}, now=1020).launch_new)
        for windows in ({}, {'primary': 7}, {'other': 7}, [7, 15]):
            self.usage['remaining_percent'] = windows
            self.assertFalse(self.choose().launch_new)

    def test_access_flag_clock_and_age_bound_are_strict(self):
        for allowed in (None, 0, 1, 'true'):
            self.assertFalse(select_provider({**self.usage, 'ordinaryAllowed': allowed}, now=1020).launch_new)
        for now in (True, float('nan'), float('inf'), -1, 10**1000):
            self.assertFalse(select_provider(self.usage, now=now).launch_new)
        for age in (True, 0, 61, float('nan')):
            self.assertFalse(select_provider(self.usage, now=1020, max_age_s=age).launch_new)
        self.assertTrue(select_provider(self.usage, now=1060).launch_new)
        self.assertFalse(select_provider(self.usage, now=1060.001).launch_new)

    def test_verified_primary_only_account_is_supported_without_inventing_secondary(self):
        self.usage.update(applicable_windows=['primary'], remaining_percent={'primary': 7})
        self.assertEqual(self.choose().provider, 'codex')
        self.usage['remaining_percent']['primary'] = 1
        self.assertEqual(self.choose().provider, 'approved-provider')

    def test_unknown_secondary_or_applicability_refuses_all_dispatch(self):
        for applicable, windows in ((['primary', 'secondary'], {'primary': 7}),
                                     (['primary', 'secondary'], {'primary': 7, 'secondary': None}),
                                     (None, {'primary': 7}), ([], {}),
                                     (['secondary'], {'secondary': 7}),
                                     (['primary', 'unknown'], {'primary': 7, 'unknown': 7}),
                                     (['primary', 'primary'], {'primary': 7})):
            self.usage.update(applicable_windows=applicable, remaining_percent=windows)
            result = self.choose()
            self.assertIsNone(result.provider); self.assertFalse(result.launch_new)

    def test_active_jobs_retain_provider_and_exact_ownership_even_without_usage(self):
        for state in ('running', 'uncertain'):
            attempt = {'state': state, 'provider': 'codex', 'owner': 'owner-a', 'token': 3,
                       'job_id': 'job-a', 'acceptance_identity': 'acceptance-a'}
            original = copy.deepcopy(attempt)
            result = select_provider(None, now=1020, successor=self.successor, attempt=attempt)
            self.assertEqual(result.provider, 'codex'); self.assertFalse(result.launch_new)
            self.assertEqual(attempt, original)
            del attempt['owner']
            self.assertFalse(self.choose(attempt=attempt).launch_new)

    def test_terminal_provider_transition_preserves_job_acceptance_and_inputs(self):
        attempt = {'state': 'failed', 'provider': 'codex', 'owner': 'owner-a', 'token': 3,
                   'job_id': 'job-a', 'acceptance_identity': 'acceptance-a'}
        self.usage['remaining_percent']['primary'] = 1
        before = copy.deepcopy((attempt, self.usage, self.successor))
        self.assertEqual(self.choose(attempt=attempt).provider, 'approved-provider')
        self.assertEqual((attempt, self.usage, self.successor), before)
        self.assertFalse(self.choose(attempt={'state': 'unknown'}).launch_new)


if __name__ == '__main__': unittest.main()
