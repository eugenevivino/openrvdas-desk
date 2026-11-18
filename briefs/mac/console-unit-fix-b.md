# Brief: console unit fix job, slice B of 3 (D-UNITS1; after console unit review round 1: HOLD, 19 P1s)

- Branch `deepsignal/console-mvp` (the checked-out branch). Unit review: desk `research/2026-11-18-console-unit-review-r1.md`. Lane: Mac, `gpt-6.2-sol` high, one slice per run, slices A then B then C on the same branch.
- Parent briefs: desk `briefs/console/core-v2.md`, `briefs/console/INTEGRATION.md`, the module briefs in `briefs/console/`, `contrib/deepsignal/console/CONTRACT.md` and `DESIGN.md`; their rules hold.
- Each finding below needs code plus a regression test that fails before the fix. P2 and P3 items in the review become tickets; do not work on them.

## P1 findings to close in this slice (verbatim from the review)
- **P1 VERIFIED, open.** Bridge labels fresh FAIL wind “OK” and displays retained heading, course, speed and gust without their stale or timed-out state. [components.tsx:62](/private/tmp/deepsignal/console-unit-rr/contrib/deepsignal/console/src/modules/bridge/components.tsx:62), [components.tsx:105](/private/tmp/deepsignal/console-unit-rr/contrib/deepsignal/console/src/modules/bridge/components.tsx:105)
- **P1 VERIFIED, open.** Missing wind direction draws a north arrow, stale heading rotates the ship-up dial, and instantaneous fallback wind keeps the “1 min vector mean” label. [components.tsx:59](/private/tmp/deepsignal/console-unit-rr/contrib/deepsignal/console/src/modules/bridge/components.tsx:59), [components.tsx:96](/private/tmp/deepsignal/console-unit-rr/contrib/deepsignal/console/src/modules/bridge/components.tsx:96)
- **P1 VERIFIED, open.** Map converts null coordinates and measurements to zero, inventing track points and readings. [MapTile.tsx:20](/private/tmp/deepsignal/console-unit-rr/contrib/deepsignal/console/src/modules/map/MapTile.tsx:20)
- **P1 VERIFIED, open.** Map memoizes the track without a data dependency and checks only latitude freshness, so a stopped longitude can leave an old position marked current. [MapTile.tsx:119](/private/tmp/deepsignal/console-unit-rr/contrib/deepsignal/console/src/modules/map/MapTile.tsx:119)
- **P1 VERIFIED, open.** A map tap selects by horizontal sample index and applies current QC and freshness to that historical value, allowing a failed sample to read PASS and LIVE. [MapTile.tsx:176](/private/tmp/deepsignal/console-unit-rr/contrib/deepsignal/console/src/modules/map/MapTile.tsx:176), [MapTile.tsx:191](/private/tmp/deepsignal/console-unit-rr/contrib/deepsignal/console/src/modules/map/MapTile.tsx:191)
- **P1 VERIFIED, open.** Raster tiles paint over the track, and the 58% black overlay preserves non-red channels in Night red. [MapTile.tsx:105](/private/tmp/deepsignal/console-unit-rr/contrib/deepsignal/console/src/modules/map/MapTile.tsx:105)
- **P1 VERIFIED, open.** Chart maps historical QARTOD 9 to NOT_EVALUATED, plots the missing sample’s number and shows a retained number as current after NO_DATA. [chart/index.tsx:126](/private/tmp/deepsignal/console-unit-rr/contrib/deepsignal/console/src/modules/chart/index.tsx:126), [chart/index.tsx:164](/private/tmp/deepsignal/console-unit-rr/contrib/deepsignal/console/src/modules/chart/index.tsx:164)
- **P1 VERIFIED, open.** Self-test passes stale logger status, stale cruise mode and arbitrarily old records, and counts presets and failed page placeholders as loaded files. [SelfTest.tsx:34](/private/tmp/deepsignal/console-unit-rr/contrib/deepsignal/console/src/modules/self-test/SelfTest.tsx:34)
- **P1 VERIFIED, open.** When loaded, Stale Banner treats unsubscribed catalog fields as outages and assigns never-observed fields a new “no data since” time on every evaluation. [stale-banner/index.tsx:48](/private/tmp/deepsignal/console-unit-rr/contrib/deepsignal/console/src/modules/stale-banner/index.tsx:48)
- **P1 VERIFIED, new.** The Health adapter retains a logger’s previous OK in the shared store after a malformed report or a valid snapshot that omits that logger. [health/page.tsx:68](/private/tmp/deepsignal/console-unit-rr/contrib/deepsignal/console/src/modules/health/page.tsx:68), [store.ts:118](/private/tmp/deepsignal/console-unit-rr/contrib/deepsignal/console/src/store.ts:118)

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
Only `contrib/deepsignal/console/src/modules/{bridge,map,chart,stale-banner,health,self-test}/**` and their tests. Core files are read-only in this slice (slice A owns them). Stale, timed-out, missing and FAIL values must never render as current or OK; Night mode stays pure red.

## Non-goals and banned
No new features, no deleted, skipped or loosened tests, no sleeps in tests, no new dependencies, no sub-agents, no dist edits by hand.

## Stop rule
Report any finding that needs a change to a parent brief's design instead of changing it.
