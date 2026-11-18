# Brief: console final targeted fix (D-UNITS1b), slice X of 2

- Branch `deepsignal/console-mvp` (the checked-out branch, base aa74676). Triage: desk `research/2026-11-18-console-p1-triage.md` (D-P1DEF1). Lane: Mac, `gpt-6.2-sol` high. Slice X then slice Y on the same branch.
- Fix ONLY the must-fix rows below, each with a regression test that fails at aa74676. Everything else in the review is a ticket: do not touch it. This is the last round.

## Must-fix rows (verbatim from the triage)
| N | Short title | Disposition | CRITICAL | Files to change | One-sentence reason |
|---|---|---|---|---|---|
| 1 | Bridge scroll | MUST-FIX (a) | no | [index.css](/private/tmp/deepsignal/console-unit-rr3/contrib/deepsignal/console/src/index.css:149) | VERIFIED: With live temperature visible at 1366×768, the recorded run failed the viewport-height assertion, which blocks by decision. |
| 2 | False Depth alarm | MUST-FIX (a) | no | [cds.ts](/private/tmp/deepsignal/console-unit-rr3/contrib/deepsignal/console/src/cds.ts:117) | VERIFIED: Catalog mode retains Depth after a page switch unsubscribes it, so the banner ages its timestamp into an A2 outage. |
| 5 | Expired last-good reading | MUST-FIX (a) | no | [field-data.ts](/private/tmp/deepsignal/console-unit-rr3/contrib/deepsignal/console/src/field-data.ts:60) | VERIFIED: A FAIL at 100.5 cleared the reading at 100 before eviction but left the identical reading marked good after the 21-sample window rolled over. |
| 6 | Number trend includes FAIL | MUST-FIX (a) | no | [NumberTile.tsx](/private/tmp/deepsignal/console-unit-rr3/contrib/deepsignal/console/src/modules/number/NumberTile.tsx:28) | VERIFIED: History masks flag 9 only, so a failed 999 becomes the trend baseline for a passing 10. |
| 7 | Bridge wind units | MUST-FIX (a) | no | [bridge/components.tsx](/private/tmp/deepsignal/console-unit-rr3/contrib/deepsignal/console/src/modules/bridge/components.tsx:123), `bridge/preset.yaml` | VERIFIED: The contract feed declares the averaged speed in kt, but the preset labels its unchanged value of 18.1 as m/s. |
| 8 | Map hides position FAIL | MUST-FIX (a) | no | [MapTile.tsx](/private/tmp/deepsignal/console-unit-rr3/contrib/deepsignal/console/src/modules/map/MapTile.tsx:104) | VERIFIED: The STALE branch returns before checking quality, so the position notice omits a simultaneous FAIL. |

## Fix plan (verbatim from the triage)
3. **#1:** Fit every Bridge tile within the viewport. In `test_bridge_browser.py`, keep the live `19.1 °C` assertion and verify the last tile is in view as well as `scrollHeight <= innerHeight`.
4. **#2:** Remove unsubscribed readings from the live snapshot in catalog mode. In `staleAlerts.test.tsx`, switch away from Depth and advance past the no-data threshold. Assert that only a still-subscribed silent field alarms.
5. **#5:** Retain the timestamp boundary needed to associate delayed QC with an evicted reading. In `quality.test.ts`, deliver FAIL at 100.5 before and after rollover and require the same `lastGood`, while preserving the existing unrelated-flag case.
6. **#6:** Exclude failed historical samples from trend endpoints. In `number.test.tsx`, feed FAIL 999 then PASS 10 and require no trend until a second usable reading arrives.
7. **#7:** Label speed using the selected field’s source units. In `windDial.test.tsx`, assert `18.1 kt` for the contract average and `10.0 m/s` for the replay fallback.
8. **#8:** Build the position notice from both freshness and quality. In `map.test.tsx`, give one coordinate STALE and FAIL together and assert that both labels and the age are visible.

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
The lead also runs `contrib/deepsignal/test/console/test_bridge_browser.py` with playwright after this slice.

## Scope
`contrib/deepsignal/console/src/**` files named in the rows above, their tests, and `contrib/deepsignal/test/console/test_bridge_browser.py`. No install files (slice Y). The production same-origin `/cds-ws` rule stays.

## Non-goals and banned
No new features, no ticket items, no deleted, skipped or loosened tests, no sleeps in tests, no new dependencies, no sub-agents, no dist edits by hand.

## Stop rule
Report any finding that needs a change to a parent brief's design instead of changing it.
