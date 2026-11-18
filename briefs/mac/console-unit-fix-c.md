# Brief: console unit fix job, slice C of 3 (D-UNITS1; after console unit review round 1: HOLD, 19 P1s)

- Branch `deepsignal/console-mvp` (the checked-out branch). Unit review: desk `research/2026-11-18-console-unit-review-r1.md`. Lane: Mac, `gpt-6.2-sol` high, one slice per run, slices A then B then C on the same branch.
- Parent briefs: desk `briefs/console/core-v2.md`, `briefs/console/INTEGRATION.md`, the module briefs in `briefs/console/`, `contrib/deepsignal/console/CONTRACT.md` and `DESIGN.md`; their rules hold.
- Each finding below needs code plus a regression test that fails before the fix. P2 and P3 items in the review become tickets; do not work on them.

## P1 findings to close in this slice (verbatim from the review)
- **P1 VERIFIED, new.** The fixture advertises loopback but starts a publish-capable cache listening on all interfaces. [fixture.py:231](/private/tmp/deepsignal/console-unit-rr/contrib/deepsignal/test/harness/fixture.py:231), [cached_data_server.py:969](/private/tmp/deepsignal/console-unit-rr/server/cached_data_server.py:969)
- **P1 VERIFIED, new.** The fixture prints `READY ... loggers=4` after finding two field names, even though its true-winds reader omits the course field required to produce wind. [fixture.py:153](/private/tmp/deepsignal/console-unit-rr/contrib/deepsignal/test/harness/fixture.py:153), [cruise.yaml:66](/private/tmp/deepsignal/console-unit-rr/contrib/deepsignal/test/harness/cruise.yaml:66)
- **P1 VERIFIED, new.** The soak report returned PASS for a client receiving zero records and for an empty measurement set, and reconnecting resets the lag baseline even when the first record is already delayed. [soak.py:61](/private/tmp/deepsignal/console-unit-rr/contrib/deepsignal/test/harness/soak.py:61), [soak.py:97](/private/tmp/deepsignal/console-unit-rr/contrib/deepsignal/test/harness/soak.py:97), [soak.py:196](/private/tmp/deepsignal/console-unit-rr/contrib/deepsignal/test/harness/soak.py:196)
- **P1 VERIFIED, new.** The Mac soak gate discovers logger processes through Linux `/proc`, so it can pass without measuring any logger’s RSS or detecting its death. [fixture.py:42](/private/tmp/deepsignal/console-unit-rr/contrib/deepsignal/test/harness/fixture.py:42), [soak.py:107](/private/tmp/deepsignal/console-unit-rr/contrib/deepsignal/test/harness/soak.py:107)
- Known open item folded in (lead, 4 failed cloud attempts): `test_logger_loss_becomes_stale_and_recovers` on branch `deepsignal/console-harness-source-loss` (task attempt-2 diff at /private/tmp/deepsignal/accept/source-loss/a2/diff). After SIGKILL of the mwx1 logger, LoggerManager never restarts it within 60 s on macOS. Bring the source-loss test into this branch, find why the logger is not restarted (read server/logger_manager.py and the supervisor; do not edit core), and make the fixture or test correct. If restart is not a core guarantee, the test must assert what core does guarantee and the doc must say so.

## Acceptance (exact commands, from repo root)
```
python3.12 -m pytest -p no:cacheprovider contrib/deepsignal/test/harness/ -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal
```

## Scope
Only `contrib/deepsignal/test/harness/**`, `contrib/deepsignal/test/console/test_source_loss_browser.py` and harness docs. Process discovery must work on macOS and Linux (`ps -A -o pid=,ppid=,command=`, no /proc, no psutil). The fixture's cache must listen on loopback only. READY is printed only after every advertised logger has produced its fields. Soak returns FAIL for zero records, an empty measurement set, or an unmeasured logger.

## Non-goals and banned
No core edits, no new features, no deleted, skipped or loosened tests, no new dependencies, no sub-agents.

## Stop rule
Report any finding that needs a change to a parent brief's design instead of changing it.
