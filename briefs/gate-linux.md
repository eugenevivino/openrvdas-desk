# Brief: gate-linux

- Decision: D-ARCH5 (Linux only)
- Risk tier: medium (it decides what counts as green)
- Module: none (desk tooling). Branch in the desk repo: `gate/linux-actions`
- Base: desk `main`
- Model and effort: Sol high, fresh session, under 40 turns (a Codex builder, rule 23)
- Upstream home: desk repo only
- Mac scratch path: `/private/tmp/deepsignal/gate-linux/` (clone in `repo/`, brief in `brief.md`, patches in `patches/`). Never touch other `/private/tmp` folders (Kalon uses them). Eugene's ruling, 2026-11-18.

## Goal
A Linux gate that checks out a given fork sha on a real Ubuntu 22.04 runner with
Python 3.12 and returns GREEN, RED or REFUSED with the same receipt shape as the Mini gate.

## Failing test first
Extend `gate/tests/test_gate.py` (or a sibling) so that a gate run with a missing
`__END__` row, a wrong sha, or a failed dependency install returns REFUSED, and
a macOS-only failure listed by exact name in `gate/expected-failures.txt` never
turns the verdict red on Linux. Must fail before the change.

## Acceptance (exact commands)
```
python -m unittest discover gate/tests
```
```
flake8 gate
```
A workflow run on fork `dev` 1a6f1ed ends with the Django `test_basic` row RED
(known dev bug, fixed on `django-gui/shared-config-names`) and every other row green,
and uploads results.tsv with its `__END__` row plus receipt.json.

## Scope
`.github/workflows/linux-gate.yml` (workflow_dispatch, input `sha`), a small
`gate/gate-linux.sh` reusing `gate/gate_lib.py` and `gate/orv_django_runner.py`,
its tests. Everything else read-only. Dependents: `docs/OPERATING-SYSTEM.md` section 5.

## Trust boundaries and data integrity
The workflow checks out a public fork sha with a read-only token and no secrets.
Missing evidence is REFUSED, never green or red. No test is skipped, loosened or
quarantined; expected failures stay exact-name only (rule 1 of Eugene-only: rows need his message).

## Non-goals and banned
No macOS job. No changes to `gate/gate.sh`. No sleeps for ordering, no swallowed errors.

## Report format
Diff summary, test names, one workflow run link, verified separate from inferred. Under 40 lines.

## Stop rule
Two fix rounds still red: stop and send to the decision desk through the lead.

## Result (builder fills in)
- Head sha:
- RED receipt:
- Gate receipt sha256 and verdict:
- What changed, in three lines:
- Open questions:
