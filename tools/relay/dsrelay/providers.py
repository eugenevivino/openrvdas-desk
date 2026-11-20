"""Pure new-attempt routing; no provider calls, credits, resets or ownership writes.

The caller verifies provenance, supplies the applicable normalized quota windows, and
enforces the selected provider's existing launch and monetary-budget controls.
This decision neither authorizes additional spend nor changes acceptance.
"""
from dataclasses import dataclass
import math
import re


@dataclass(frozen=True)
class Decision:
    provider: str | None
    launch_new: bool
    reason: str


def _number(value):
    try:
        return type(value) in (int, float) and math.isfinite(value)
    except OverflowError:
        return False


def _provider(value):
    return isinstance(value, str) and bool(re.fullmatch(r'[a-z][a-z0-9_-]{0,63}', value))


def select_provider(usage, *, now, successor=None, attempt=None, max_age_s=60):
    """Choose for a NEW attempt, or retain an existing active provider.

    usage: verified=True, observed_at=epoch seconds, ordinaryAllowed=bool,
    applicable_windows=['primary', 'secondary'], remaining_percent maps each
    applicable window to its percentage. Primary is required; secondary may be
    omitted ONLY when verified not applicable. An unavailable/unknown secondary
    must remain applicable with a missing/invalid value, which refuses dispatch.
    Never normalize unknown/not-applicable quota to 100 percent.
    successor: provider=name, approved=True, auth_ready=True,
    budget_permits=True, each supplied explicitly by existing controls.
    attempt: existing state/provider/owner/token; never mutated or re-owned.
    Unknown/stale quota blocks all new dispatch, including successor fallback.
    """
    if attempt is not None:
        if not isinstance(attempt, dict):
            return Decision(None, False, 'invalid_attempt')
        state = attempt.get('state')
        if state in ('running', 'uncertain'):
            provider = attempt.get('provider')
            if (not _provider(provider) or not isinstance(attempt.get('owner'), str)
                    or not attempt['owner'] or type(attempt.get('token')) is not int
                    or attempt['token'] < 1):
                return Decision(None, False, 'active_ownership_unknown')
            return Decision(provider, False, 'retain_active_attempt')
        if state not in ('passed', 'failed', 'blocked', 'cancelled'):
            return Decision(None, False, 'attempt_not_terminal')
    if (not _number(now) or now < 0 or not _number(max_age_s)
            or not 0 < max_age_s <= 60 or not isinstance(usage, dict)
            or usage.get('verified') is not True):
        return Decision(None, False, 'unverified_usage')
    observed = usage.get('observed_at')
    if not _number(observed) or observed < 0 or not 0 <= now - observed <= max_age_s:
        return Decision(None, False, 'stale_or_invalid_usage_time')
    allowed = usage.get('ordinaryAllowed')
    windows = usage.get('remaining_percent')
    applicable = usage.get('applicable_windows')
    if (type(allowed) is not bool or not isinstance(windows, dict)
            or not isinstance(applicable, list)
            or applicable not in (['primary'], ['primary', 'secondary'], ['secondary', 'primary'])
            or set(windows) != set(applicable)
            or any(not _number(v) or not 0 <= v <= 100 for v in windows.values())):
        return Decision(None, False, 'invalid_usage_windows')
    if allowed and min(windows.values()) > 1:
        return Decision('codex', True, 'ordinary_quota_available')
    if (isinstance(successor, dict) and _provider(successor.get('provider'))
            and successor['provider'] != 'codex'
            and all(successor.get(k) is True for k in ('approved', 'auth_ready', 'budget_permits'))):
        return Decision(successor['provider'], True, 'approved_successor')
    return Decision(None, False, 'reserve_or_ordinary_access_unavailable')
