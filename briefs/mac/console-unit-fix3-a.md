# Brief: console unit fix job round 3, slice A of 3 (D-UNITS1a, the one extra round; after unit review round 2: HOLD)

- Branch `deepsignal/console-mvp` (the checked-out branch, base 7efd237). Review: desk `research/2026-11-18-console-unit-review-r2.md`. Lane: Mac, `gpt-6.2-sol` high, slices A then B then C on the same branch.
- Parent briefs: desk `briefs/console/core-v2.md`, `briefs/console/INTEGRATION.md` (D-RECOVER1 applies), the module briefs in `briefs/console/`, `contrib/deepsignal/console/CONTRACT.md` and `DESIGN.md`.
- Each finding below needs code plus a regression test that fails at 7efd237. P2 and P3 items become tickets; do not work on them.

## P1 findings to close in this slice (verbatim from the review)
- **P1 VERIFIED, prior.** The installer rejects the stock publish-capable proxy, but the README’s manual installation bypasses that check, Self-test reports a connection without the required relay or UDP warning, and the regression uses a stub checker. [README.md:8](/private/tmp/deepsignal/console-unit-rr2/contrib/deepsignal/console/README.md:8), [install_openrvdas.sh:652](/private/tmp/deepsignal/console-unit-rr2/utils/install_openrvdas.sh:652), [SelfTest.tsx:55](/private/tmp/deepsignal/console-unit-rr2/contrib/deepsignal/console/src/modules/self-test/SelfTest.tsx:55), [test_nginx_site.py:107](/private/tmp/deepsignal/console-unit-rr2/contrib/deepsignal/console/install/test_nginx_site.py:107)
- **P1 VERIFIED.** The Number tile rendered a QARTOD 9 reading as `999 °C` beside `LIVE` and `MISSING`, and its sparkline also consumes the unmasked number. [NumberTile.tsx:50](/private/tmp/deepsignal/console-unit-rr2/contrib/deepsignal/console/src/modules/number/NumberTile.tsx:50), [Sparkline.tsx:18](/private/tmp/deepsignal/console-unit-rr2/contrib/deepsignal/console/src/modules/number/Sparkline.tsx:18)
- **P1 VERIFIED.** A late FAIL for a reading outside the 21-sample window left that exact reading in `lastGood`, available for display after timeout. [field-data.ts:52](/private/tmp/deepsignal/console-unit-rr2/contrib/deepsignal/console/src/field-data.ts:52)
- **P1 VERIFIED.** One stock CDS `NaN` causes the client to discard the entire batch, including valid FAIL flags for unrelated fields, and request the next batch. [cached_data_server.py:415](/private/tmp/deepsignal/console-unit-rr2/server/cached_data_server.py:415), [cds.ts:264](/private/tmp/deepsignal/console-unit-rr2/contrib/deepsignal/console/src/cds.ts:264)
- **P1 VERIFIED.** A throwing alert subscriber prevented the next subscriber from receiving the alert; lighting uses the same unguarded callback loop. [context.ts:11](/private/tmp/deepsignal/console-unit-rr2/contrib/deepsignal/console/src/context.ts:11)
- **P1 VERIFIED.** A module can register a page with a non-array `tiles` value, which throws in the shell before any module error boundary renders. [context.ts:25](/private/tmp/deepsignal/console-unit-rr2/contrib/deepsignal/console/src/context.ts:25), [App.tsx:152](/private/tmp/deepsignal/console-unit-rr2/contrib/deepsignal/console/src/App.tsx:152)
- Flaky test (lead): during the final acceptance at 7efd237, `npx vitest run` once reported 1 failed of 146 right after `npm run build`; 9 later runs passed. Find it: run `npx vitest run` at least 20 times (also with `--sequence.shuffle`), identify any test that depends on wall-clock time, timers, ordering or shared state, and make it deterministic (fake timers or injected clocks). Report the test name and cause, or say plainly that it did not reproduce.

## Acceptance (exact commands, from `contrib/deepsignal/console`)
```
npx oxlint
```
```
npx tsc -b --noEmit
```
```
npx vitest run
```
```
npm run build
```

## Scope
`contrib/deepsignal/console/src/` core files (cds.ts, store.ts, field-data.ts, context.ts, the shared tiles such as NumberTile, pages.ts and their tests), `contrib/deepsignal/console/install/**` and `contrib/deepsignal/console/README.md`. Module folders are read-only (slice B). The production same-origin `/cds-ws` rule must not be weakened.

## Non-goals and banned
No new features, no deleted, skipped or loosened tests, no sleeps in tests, no new dependencies, no sub-agents, no dist edits by hand.

## Stop rule
Report any finding that needs a change to a parent brief's design instead of changing it.
