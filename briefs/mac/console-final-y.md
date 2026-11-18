# Brief: console final targeted fix (D-UNITS1b), slice Y of 2

- Branch `deepsignal/console-mvp` (the checked-out branch, base aa74676). Triage: desk `research/2026-11-18-console-p1-triage.md` (D-P1DEF1). Lane: Mac, `gpt-6.2-sol` high. Slice X then slice Y on the same branch.
- Fix ONLY the must-fix rows below, each with a regression test that fails at aa74676. Everything else in the review is a ticket: do not touch it. This is the last round.

## Must-fix rows (verbatim from the triage)
| N | Short title | Disposition | CRITICAL | Files to change | One-sentence reason |
|---|---|---|---|---|---|
| 3 | Relay install gate | MUST-FIX (b) | yes | `install/install.sh`, `install/test_nginx_site.py`, #197 `security/check_cds.py` | VERIFIED: A missing checker fails closed, but the positive test stubs its exit code and never establishes that the selected nginx `/cds-ws` refuses publish. |
| 4 | Installer privileges | MUST-FIX (b) | yes | `install/install.sh`, `README.md`, `docs/install.md` | VERIFIED: The documented `sudo` command runs the installer, its AWK helper and the Python checker from a checkout the stock installer assigns to `rvdas`. |

## Fix plan (verbatim from the triage)
1. **#4:** Run the installer and helpers from a trusted location outside service-writable directories. In `test_nginx_site.py`, verify that a service-writable checker or helper cannot run with privilege or authorize an nginx change.
2. **#3:** Wire the real #197 checker to the selected virtual host. Test both Django and React nginx configurations through `/cds-ws`: subscription succeeds, publish is refused, the cache stays unchanged, and a writable endpoint fails the gate.

## Constraint from the lead (security, CRITICAL)
The real #197 checker (`contrib/deepsignal/security/check_cds.py`) lives on the separate unmerged critical unit `deepsignal/sec-cds-lockdown` (eadb0a2), which also changes core. Do NOT copy it or any #197 file into this branch. Instead: the installer must call the checker at that documented path from a trusted, root-owned location, and fail closed with a clear message when it is absent or not root-owned. Add the positive gate test so it runs when the checker is present and skips with a reason naming #197 when it is not; keep the fail-closed tests unconditional. Document in `docs/install.md` that #197 must land first.

## Acceptance (exact commands, from repo root)
```
python3.12 -m pytest -p no:cacheprovider contrib/deepsignal/console/install contrib/deepsignal/test/console/test_install.py -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal
```

## Scope
Only `contrib/deepsignal/console/install/**`, `contrib/deepsignal/test/console/test_install.py`, `contrib/deepsignal/console/README.md` and `contrib/deepsignal/console/docs/install.md`. No UI source.

## Non-goals and banned
No new features, no deleted, skipped or loosened tests, no new dependencies, no sub-agents, no #197 files.

## Stop rule
Report any finding that needs a change to a parent brief's design instead of changing it.
