"""Boundary checks for staged policy; no sampling or live allocator operations."""
import unittest
from unittest.mock import patch

from dsrelay import resource_policy

from dsrelay.resource_policy import (
    DEFAULT_FLOOR_BYTES, GIB, MINI_LIGHTWEIGHT_FLOOR_BYTES,
    SWAP_GROWTH_5M_LIMIT_BYTES, SWAP_LIMIT_BYTES, evaluate_admission,
)


class ResourcePolicyTests(unittest.TestCase):
    def decision(self, **changes):
        values = dict(host='mini', lightweight=True, policy_verified=True,
                      policy_fresh=True, measurement_verified=True,
                      measurement_fresh=True, pressure='normal',
                      swap_used_bytes=0, swap_growth_5m_bytes=0,
                      available_headroom_bytes=2 * GIB, job_peak_bytes=GIB,
                      remaining_job_budget_bytes=GIB,
                      reservation_compatible=True, physical_bytes=8 * GIB,
                      reserved_bytes=0)
        values.update(changes)
        if 'vm_stat' not in values:
            headroom = values['available_headroom_bytes']
            reserved = values['reserved_bytes']
            amount = (headroom + reserved if type(headroom) is int
                      and type(reserved) is int else 2 * GIB)
            values['vm_stat'] = self.vm_text(amount)
        return evaluate_admission(**values)

    @staticmethod
    def vm_text(available):
        return ('Mach Virtual Memory Statistics: (page size of 1 bytes)\n'
                f'Pages free: {available}.\nPages inactive: 0.\n'
                'Pages speculative: 0.\n')

    def test_exact_byte_constants(self):
        self.assertEqual(MINI_LIGHTWEIGHT_FLOOR_BYTES, 1073741824)
        self.assertEqual(DEFAULT_FLOOR_BYTES, 3221225472)
        self.assertEqual(SWAP_LIMIT_BYTES, 8589934592)
        self.assertEqual(SWAP_GROWTH_5M_LIMIT_BYTES, 536870912)

    def test_floor_passes_at_one_gib_but_job_still_needs_peak_room(self):
        self.assertEqual(self.decision(available_headroom_bytes=GIB).reason,
                         'insufficient_post_peak_headroom')
        self.assertEqual(self.decision(available_headroom_bytes=GIB - 1).reason,
                         'below_host_floor')

    def test_post_peak_exact_fit_and_above_are_allowed(self):
        for headroom in (2 * GIB, 2 * GIB + 1):
            with self.subTest(headroom=headroom):
                self.assertTrue(self.decision(
                    available_headroom_bytes=headroom).allowed)
        self.assertFalse(self.decision(
            available_headroom_bytes=2 * GIB - 1).allowed)

    def test_macbook_floor_is_unaffected_by_lightweight_label(self):
        for lightweight in (False, True):
            with self.subTest(lightweight=lightweight):
                self.assertFalse(self.decision(
                    host='macbook', lightweight=lightweight).allowed)
                self.assertFalse(self.decision(host='macbook',
                    lightweight=lightweight,
                    available_headroom_bytes=4 * GIB - 1).allowed)
                self.assertTrue(self.decision(host='macbook',
                    lightweight=lightweight,
                    available_headroom_bytes=4 * GIB).allowed)

    def test_mini_nonlightweight_retains_three_gib_floor(self):
        self.assertFalse(self.decision(lightweight=False).allowed)
        self.assertTrue(self.decision(lightweight=False,
                                     available_headroom_bytes=4 * GIB).allowed)

    def test_pressure_and_swap_limits(self):
        for pressure in ('warning', 'critical', 'unknown', None):
            with self.subTest(pressure=pressure):
                self.assertEqual(self.decision(pressure=pressure).reason,
                                 'memory_pressure')
        self.assertTrue(self.decision(swap_used_bytes=SWAP_LIMIT_BYTES - 1,
            swap_growth_5m_bytes=SWAP_GROWTH_5M_LIMIT_BYTES).allowed)
        self.assertEqual(self.decision(swap_used_bytes=SWAP_LIMIT_BYTES).reason,
                         'swap_limit')
        self.assertEqual(self.decision(
            swap_growth_5m_bytes=SWAP_GROWTH_5M_LIMIT_BYTES + 1).reason,
            'swap_growth')

    def test_unverified_stale_or_nonboolean_assertions_fail_closed(self):
        for flag in ('policy_verified', 'policy_fresh', 'measurement_verified',
                     'measurement_fresh', 'reservation_compatible'):
            for value in (False, None, 1, 'true'):
                with self.subTest(flag=flag, value=value):
                    self.assertFalse(self.decision(**{flag: value}).allowed)

    def test_competing_kalon_reservations_reduce_authority_headroom(self):
        # Same measured pool, with authority accounting for another project's
        # reservation before providing this project's available headroom.
        pool = 3 * GIB
        self.assertTrue(self.decision(available_headroom_bytes=pool - GIB).allowed)
        self.assertFalse(self.decision(
            available_headroom_bytes=pool - (GIB + 1)).allowed)
        self.assertEqual(self.decision(reservation_compatible=False).reason,
                         'reservation_incompatible')

    def test_budget_is_independent_of_memory_floor(self):
        for changes in ({'job_peak_bytes': 0}, {'remaining_job_budget_bytes': 0},
                        {'remaining_job_budget_bytes': GIB - 1}):
            with self.subTest(changes=changes):
                self.assertFalse(self.decision(**changes).allowed)
        self.assertTrue(self.decision(remaining_job_budget_bytes=GIB).allowed)

    def test_invalid_byte_values_and_unsupported_hosts_fail_closed(self):
        for field in ('swap_used_bytes',
                      'available_headroom_bytes', 'job_peak_bytes',
                      'remaining_job_budget_bytes'):
            for value in (-1, True, 1.0, None, '1073741824'):
                with self.subTest(field=field, value=value):
                    self.assertFalse(self.decision(**{field: value}).allowed)
        self.assertFalse(self.decision(host='unknown').allowed)
        self.assertFalse(self.decision(lightweight='true').allowed)

    def test_swap_decrease_is_safe_but_invalid_growth_is_refused(self):
        self.assertTrue(self.decision(swap_growth_5m_bytes=-1048576).allowed)
        for value in (True, 1.0, None, '0'):
            self.assertFalse(self.decision(swap_growth_5m_bytes=value).allowed)

    def test_both_pinned_common_functions_are_called_without_sampling(self):
        common = resource_policy._load_common_policy()
        with patch.object(resource_policy, '_load_common_policy', return_value=common), \
                patch.object(common, 'available_bytes', wraps=common.available_bytes) as available, \
                patch.object(common, 'memory_gate', wraps=common.memory_gate) as gate, \
                patch.object(common, 'sample', side_effect=AssertionError('no sampling')):
            self.assertTrue(self.decision().allowed)
        available.assert_called_once()
        gate.assert_called_once()
        self.assertEqual(gate.call_args.kwargs['headroom_bytes'], GIB)

    def test_changed_hash_refused_before_execution_and_missing_source_refused(self):
        with patch.object(resource_policy.Path, 'read_bytes',
                          return_value=b'raise AssertionError("must not execute")'):
            self.assertEqual(self.decision().reason,
                             'common_policy_unavailable_or_changed')
        with patch.object(resource_policy.Path, 'read_bytes', side_effect=OSError):
            self.assertEqual(self.decision().reason,
                             'common_policy_unavailable_or_changed')
            self.assertTrue(self.decision(host='macbook',
                                         available_headroom_bytes=4 * GIB).allowed)

    def test_loader_reads_and_executes_same_verified_bytes_once(self):
        source = resource_policy.COMMON_POLICY_PATH.read_bytes()
        with patch.object(resource_policy.Path, 'read_bytes', return_value=source) as read:
            common = resource_policy._load_common_policy()
        read.assert_called_once_with()
        self.assertEqual(common.available_bytes(self.vm_text(2 * GIB), 8 * GIB), 2 * GIB)

    def test_common_metric_excludes_file_backed_and_purgeable_pages(self):
        text = ('Mach Virtual Memory Statistics: (page size of 4096 bytes)\n'
                'Pages free: 131072.\nPages inactive: 131072.\n'
                'Pages speculative: 262144.\nPages purgeable: 999999.\n'
                'File-backed pages: 999999.\n')
        self.assertTrue(self.decision(vm_stat=text).allowed)
        self.assertEqual(self.decision(vm_stat=text,
                         available_headroom_bytes=3 * GIB).reason,
                         'authority_headroom_mismatch')

    def test_common_gate_accounts_for_competing_reservation(self):
        text = self.vm_text(3 * GIB)
        self.assertTrue(self.decision(vm_stat=text, reserved_bytes=GIB).allowed)
        self.assertEqual(self.decision(vm_stat=text, reserved_bytes=GIB + 1,
                         available_headroom_bytes=2 * GIB - 1).reason,
                         'insufficient_post_peak_headroom')

    def test_invalid_physical_vm_and_reservation_inputs_fail_closed(self):
        for changes in ({'physical_bytes': GIB}, {'physical_bytes': True},
                        {'physical_bytes': None}, {'physical_bytes': 0},
                        {'reserved_bytes': -1}, {'reserved_bytes': None},
                        {'vm_stat': ''}, {'vm_stat': None},
                        {'vm_stat': self.vm_text(2 * GIB) + 'Pages free: 0.\n'}):
            with self.subTest(changes=changes):
                self.assertFalse(self.decision(**changes).allowed)


if __name__ == '__main__':
    unittest.main()
