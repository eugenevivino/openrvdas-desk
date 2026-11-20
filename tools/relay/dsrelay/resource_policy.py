"""Staged pure DeepSignal policy; never samples, reserves, or launches work.

The sole shared authority must verify policy/measurement freshness and reservation
compatibility before calling this function. Flags are trusted caller assertions,
not authentication. No real authority hook is installed by this module.
Mini memory calculation/gating calls the exact pinned common owner source. Input
VM text and physical size come from the verified authority; this module never
calls the common sampler. Headroom excludes competing reservations, not job peak.
"""
import hashlib
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType


COMMON_POLICY_PATH = Path(
    '/private/tmp/deepsignal/relay-20261120/common-policy/c9547b03ee746b6bb97f4feaf94f8c235007472c3bdef415cf23604798f1b064/'
    'mini_light_admission.py')
COMMON_POLICY_SHA256 = (
    'c9547b03ee746b6bb97f4feaf94f8c235007472c3bdef415cf23604798f1b064')

GIB = 1_073_741_824
MINI_LIGHTWEIGHT_FLOOR_BYTES = GIB
DEFAULT_FLOOR_BYTES = 3 * GIB
SWAP_LIMIT_BYTES = 8 * GIB
SWAP_GROWTH_5M_LIMIT_BYTES = 512 * 1_048_576


@dataclass(frozen=True)
class Decision:
    allowed: bool
    reason: str


def _load_common_policy():
    """Read once, verify, then execute those same bytes; no import cache/write."""
    source = COMMON_POLICY_PATH.read_bytes()
    if hashlib.sha256(source).hexdigest() != COMMON_POLICY_SHA256:
        raise ValueError('common policy hash mismatch')
    module = ModuleType('deepsignal_pinned_mini_policy')
    exec(compile(source, str(COMMON_POLICY_PATH), 'exec'), module.__dict__)
    return module


def evaluate_admission(*, host, lightweight, policy_verified, policy_fresh,
                       measurement_verified, measurement_fresh, pressure,
                       swap_used_bytes, swap_growth_5m_bytes,
                       available_headroom_bytes, job_peak_bytes,
                       remaining_job_budget_bytes, reservation_compatible,
                       vm_stat=None, physical_bytes=None, reserved_bytes=None):
    """Evaluate one proposed job against verified authority inputs, in bytes.

    Hosts use the shared authority labels ``mini`` and ``macbook``. Remaining
    budget is the authority's unconsumed memory allowance for this proposed job.
    Both budget and measured headroom must cover the peak independently. The
    floor is safe memory left AFTER the peak, not the job's allocation budget.
    Mini also requires authority VM text, physical bytes and competing reserved
    bytes; reported headroom must equal common available minus reservations.
    This decision cannot create a lease or replace any existing execution guard.
    """
    if host not in ('mini', 'macbook'):
        return Decision(False, 'unsupported_host')
    if type(lightweight) is not bool:
        return Decision(False, 'invalid_workload_class')
    if policy_verified is not True or policy_fresh is not True:
        return Decision(False, 'policy_unverified_or_stale')
    if measurement_verified is not True or measurement_fresh is not True:
        return Decision(False, 'measurement_unverified_or_stale')
    if reservation_compatible is not True:
        return Decision(False, 'reservation_incompatible')
    amounts = (swap_used_bytes, available_headroom_bytes,
               job_peak_bytes, remaining_job_budget_bytes)
    if (any(type(value) is not int or value < 0 for value in amounts)
            or type(swap_growth_5m_bytes) is not int):
        return Decision(False, 'invalid_byte_measurement')
    if swap_used_bytes >= SWAP_LIMIT_BYTES:
        return Decision(False, 'swap_limit')
    if swap_growth_5m_bytes > SWAP_GROWTH_5M_LIMIT_BYTES:
        return Decision(False, 'swap_growth')
    if job_peak_bytes == 0 or remaining_job_budget_bytes == 0:
        return Decision(False, 'missing_or_exhausted_job_budget')
    if job_peak_bytes > remaining_job_budget_bytes:
        return Decision(False, 'job_peak_exceeds_budget')
    if host == 'mini':
        if (not isinstance(vm_stat, str) or type(physical_bytes) is not int
                or physical_bytes <= 0 or type(reserved_bytes) is not int
                or reserved_bytes < 0):
            return Decision(False, 'invalid_common_memory_inputs')
        try:
            common = _load_common_policy()
        except (OSError, ValueError):
            return Decision(False, 'common_policy_unavailable_or_changed')
        try:
            available = common.available_bytes(vm_stat, physical_bytes)
            if available_headroom_bytes != available - reserved_bytes:
                return Decision(False, 'authority_headroom_mismatch')
            floor = (MINI_LIGHTWEIGHT_FLOOR_BYTES if lightweight
                     else DEFAULT_FLOOR_BYTES)
            reason = common.memory_gate(
                dict(available_bytes=available, physical_bytes=physical_bytes,
                     pressure_level=1 if pressure == 'normal' else 2),
                peak_bytes=job_peak_bytes, headroom_bytes=floor,
                reserved_bytes=reserved_bytes, job_minimum_bytes=floor)
        except (ValueError, TypeError, KeyError):
            return Decision(False, 'invalid_common_memory_inputs')
        reasons = {'pressure': 'memory_pressure',
                   'available memory below admission floor': 'below_host_floor',
                   'insufficient headroom for peak': 'insufficient_post_peak_headroom'}
        if reason != 'memory eligible':
            return Decision(False, reasons.get(reason, 'unsupported_common_decision'))
    else:
        if pressure != 'normal':
            return Decision(False, 'memory_pressure')
        if available_headroom_bytes < DEFAULT_FLOOR_BYTES:
            return Decision(False, 'below_host_floor')
        if available_headroom_bytes - job_peak_bytes < DEFAULT_FLOOR_BYTES:
            return Decision(False, 'insufficient_post_peak_headroom')
    return Decision(True, 'admitted_by_staged_policy')
