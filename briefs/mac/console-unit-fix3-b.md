# Brief: console unit fix job round 3, slice B of 3 (D-UNITS1a, the one extra round; after unit review round 2: HOLD)

- Branch `deepsignal/console-mvp` (the checked-out branch, base 7efd237). Review: desk `research/2026-11-18-console-unit-review-r2.md`. Lane: Mac, `gpt-6.2-sol` high, slices A then B then C on the same branch.
- Parent briefs: desk `briefs/console/core-v2.md`, `briefs/console/INTEGRATION.md` (D-RECOVER1 applies), the module briefs in `briefs/console/`, `contrib/deepsignal/console/CONTRACT.md` and `DESIGN.md`.
- Each finding below needs code plus a regression test that fails at 7efd237. P2 and P3 items become tickets; do not work on them.

## P1 findings to close in this slice (verbatim from the review)
- **P1 VERIFIED, prior.** After a page unsubscribed from Depth, Stale Banner raised “Depth no data” from its retained timestamp; its regression covers only never-observed catalog entries and skips even a known FAILED logger before its first sample. [StaleBanner.tsx:52](/private/tmp/deepsignal/console-unit-rr2/contrib/deepsignal/console/src/modules/stale-banner/StaleBanner.tsx:52), [staleAlerts.test.tsx:88](/private/tmp/deepsignal/console-unit-rr2/contrib/deepsignal/console/src/modules/stale-banner/staleAlerts.test.tsx:88)
- **P1 VERIFIED, prior.** Self-test now rejects stale status, old records, presets and explicit failure placeholders, but one valid file plus a configured page returning 404 produced `Page files: PASS` because the loader discards the missing file. [pages.ts:114](/private/tmp/deepsignal/console-unit-rr2/contrib/deepsignal/console/src/pages.ts:114), [SelfTest.tsx:71](/private/tmp/deepsignal/console-unit-rr2/contrib/deepsignal/console/src/modules/self-test/SelfTest.tsx:71), [selfTest.test.tsx:50](/private/tmp/deepsignal/console-unit-rr2/contrib/deepsignal/console/src/modules/self-test/selfTest.test.tsx:50)
- **P1 VERIFIED.** Self-test reported `Logger status: PASS` for `{mwx1: null}` because it counts keys without validating the logger entries. [SelfTest.tsx:38](/private/tmp/deepsignal/console-unit-rr2/contrib/deepsignal/console/src/modules/self-test/SelfTest.tsx:38)
- **P1 VERIFIED.** The Bridge preset labels instantaneous fallback wind in knots although the shipped replay produces metres per second, so 10 m/s displays as 10 kn. [preset.yaml:12](/private/tmp/deepsignal/console-unit-rr2/contrib/deepsignal/console/src/modules/bridge/preset.yaml:12), [cruise.yaml:81](/private/tmp/deepsignal/console-unit-rr2/contrib/deepsignal/test/harness/cruise.yaml:81)
- **P1 VERIFIED.** Map includes numeric coordinates flagged MISSING in historical tracks, drops SUSPECT from the current position marker, and draws a north-pointing ship when its configured heading is unavailable. [MapTile.tsx:26](/private/tmp/deepsignal/console-unit-rr2/contrib/deepsignal/console/src/modules/map/MapTile.tsx:26), [MapTile.tsx:100](/private/tmp/deepsignal/console-unit-rr2/contrib/deepsignal/console/src/modules/map/MapTile.tsx:100), [MapTile.tsx:254](/private/tmp/deepsignal/console-unit-rr2/contrib/deepsignal/console/src/modules/map/MapTile.tsx:254)
- **P1 VERIFIED.** When manager reports stop, shared field health retains the previous OK; when only cruise-mode reports stop, Health continues displaying the old mode without its age. [health/page.tsx:82](/private/tmp/deepsignal/console-unit-rr2/contrib/deepsignal/console/src/modules/health/page.tsx:82), [health/page.tsx:142](/private/tmp/deepsignal/console-unit-rr2/contrib/deepsignal/console/src/modules/health/page.tsx:142)
- **P1 VERIFIED.** Auto Night accepted fresh coordinates flagged MISSING and switched the screen from Night to Day. [autoNight.ts:57](/private/tmp/deepsignal/console-unit-rr2/contrib/deepsignal/console/src/modules/kiosk-night/autoNight.ts:57)

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
Only `contrib/deepsignal/console/src/modules/{bridge,map,stale-banner,health,self-test,kiosk-night}/**` and their tests. Core files are read-only in this slice. MISSING, SUSPECT, stale and FAIL values never render as current or OK; units match the replayed data.

## Non-goals and banned
No new features, no deleted, skipped or loosened tests, no sleeps in tests, no new dependencies, no sub-agents, no dist edits by hand.

## Stop rule
Report any finding that needs a change to a parent brief's design instead of changing it.
