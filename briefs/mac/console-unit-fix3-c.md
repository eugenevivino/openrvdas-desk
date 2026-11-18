# Brief: console unit fix job round 3, slice C of 3 (D-UNITS1a, the one extra round; after unit review round 2: HOLD)

- Branch `deepsignal/console-mvp` (the checked-out branch, base 7efd237). Review: desk `research/2026-11-18-console-unit-review-r2.md`. Lane: Mac, `gpt-6.2-sol` high, slices A then B then C on the same branch.
- Parent briefs: desk `briefs/console/core-v2.md`, `briefs/console/INTEGRATION.md` (D-RECOVER1 applies), the module briefs in `briefs/console/`, `contrib/deepsignal/console/CONTRACT.md` and `DESIGN.md`.
- Each finding below needs code plus a regression test that fails at 7efd237. P2 and P3 items become tickets; do not work on them.

## P1 findings to close in this slice (verbatim from the review)
- **P1 VERIFIED.** The soak returned PASS with one interval reporting 60-second lag followed by 29 silent intervals because silence contributes zero lag and one positive interval satisfies the traffic check. [soak.py:54](/private/tmp/deepsignal/console-unit-rr2/contrib/deepsignal/test/harness/soak.py:54), [soak.py:188](/private/tmp/deepsignal/console-unit-rr2/contrib/deepsignal/test/harness/soak.py:188)
- Browser-test relay (lead): the console now accepts only the same-origin `/cds-ws` relay, so `contrib/deepsignal/test/console/test_console_live.py` and `test_source_loss_browser.py` (and any other lead_run browser test) fail with an empty page. Add a small test-side static server for `dist` that also relays `/cds-ws` to the fixture's cache on the same origin (stdlib plus the existing websockets package, no new dependencies), and point the browser tests at it. Test-side only: do not change console source or the production rule. The tests must pass when run by the lead with playwright on macOS.

## Acceptance (exact commands, from repo root)
```
python3.12 -m pytest -p no:cacheprovider contrib/deepsignal/test/ -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal
```

## Scope
Only `contrib/deepsignal/test/**` and harness docs. No console source edits, no core edits.

## Non-goals and banned
No new features, no deleted, skipped or loosened tests, no sleeps in tests, no new dependencies, no sub-agents, no dist edits by hand.

## Stop rule
Report any finding that needs a change to a parent brief's design instead of changing it.
