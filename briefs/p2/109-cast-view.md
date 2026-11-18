# Brief: p2-cast-view (Winch and CTD cast view)

- Decision: D-PARITY1, IDEAS #109 (Eugene approved building #104-#124, 2026-11-18)
- Risk tier: medium
- Module: exactly one. Branch `deepsignal/p2-cast-view` from `deepsignal/console-contract`
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: console, fork only
- Value (techs/science/shore): 5/4/2
- Depends on: console contract branch `deepsignal/console-contract`
- Needs Eugene: Safe working load numbers are ship-specific: the module reads them from config and shows "SWL not set" when absent. Eugene or the ship supplies real values.

## Goal
The winch operator and CTD watch see wire out, payout speed, tension against its safe working load, CTD
depth and altimeter on one night-safe page, with a plain warning before trouble.

## Build
- Route `cast`, titled "Cast", order 40, plus a tile `cast` usable on other pages.
- Settings (all field names configurable, none hard-coded): `wire_out`, `wire_speed`, `tension`,
  `ctd_depth`, `altimeter`, `swl` (number, same unit as tension), `warn_fraction` (default 0.8),
  `alarm_fraction` (default 0.95), `altimeter_warn` (default 10 m), `altimeter_alarm` (default 5 m).
- Big readouts for wire out, speed (signed: down positive; show "down" or "up" in words), tension.
- Tension bar with bands at `warn_fraction` and `alarm_fraction` of SWL: word plus shape plus color
  ("OK", "Near limit", "Over limit"). Missing `swl` shows "SWL not set" and no bands.
- Altimeter: shows "Bottom in N m" and warns under the thresholds; values outside 0 to 100 m are shown as
  "No bottom" (altimeters report a sentinel when out of range: treat any value over 100 as no bottom).
- Tension strip chart for the last 15 minutes from `store.history()`.
- Max tension this cast, reset when wire out returns under 5 m.
- Every value shows freshness; STALE tension or wire out shows the age in words and greys the bar.

## Tests first
`cast.test.tsx` with the fake feed: band thresholds at exactly 0.8 and 0.95 of SWL; no SWL; direction
words; altimeter no-bottom sentinel; altimeter warn and alarm; max tension reset; stale tension state;
values rendered as text.

## Scope
`contrib/deepsignal/console/src/modules/cast/**`, `contrib/deepsignal/console/docs/cast.md`.

## Rules every console task follows

Read these files in the repository first: `contrib/deepsignal/console/CONTRACT.md`, `contrib/deepsignal/console/src/contract/index.ts`, `contrib/deepsignal/console/DESIGN.md` (the "Rulebook v2 additions" section wins over v1 where they differ). The contract is fixed: never edit `src/contract/**` or `CONTRACT.md`. If the contract blocks you, stop and say exactly what you need.

Ownership: you own ONLY the paths listed under Scope. Everything else is read-only, in particular `src/registry.ts`, `src/App.tsx`, `src/main.tsx`, `src/cds.ts`, `src/store.ts`, `src/lighting*.ts`, `src/pages.ts`, `src/index.css`, `index.html`, `package.json`, `package-lock.json`, `vite.config.ts`, `tsconfig*.json`, `.oxlintrc.json`, `DESIGN.md`, `README.md`, `public/**`, `dist/**`, `demo_cache.py`, `contrib/deepsignal/configs/**`, other modules' folders, and `contrib/deepsignal/test/console/test_console_live.py`. No new dependency of any kind.

Your module is `src/modules/<id>/index.ts` default-exporting a `ConsoleModule` (types in the contract). Core discovers it by glob; do not register it anywhere. If core's registry is not on your branch yet, that is expected: your tests import your module directly.

Tests: Vitest on jsdom, beside your code (`src/modules/<id>/*.test.ts(x)`). Build a minimal fake `ConsoleContext` inside your own folder (for example `src/modules/<id>/testkit.ts`) from `src/contract/fake-feed.json`, with a fake clock you step. Cover every behavior named in this brief. Use only `ctx.clock.now()` for time.

Screens: word + shape for every state, color third; tokens only (`--bg --panel --panel2 --line --fg --muted --accent --ok --check --stale --down --chart --grid` and fonts `--f-number --f-body --f-mono`), never literal colors; canvas/SVG read tokens at draw time and redraw on `ctx.lighting.subscribe`; Night must never paint a light surface (empty, loading and error states included); plain English, units always shown; touch targets at least 44 px; bridge sizes: primary value 48 px, labels at least 18 px, metadata at least 16 px; render all data as text (no `innerHTML`, no `dangerouslySetInnerHTML`, no `eval`).

Browser checks: Chromium does not run in this sandbox. If the brief asks for a browser test, write it as `contrib/deepsignal/test/console/test_<id>_browser.py`, mark it `@pytest.mark.lead_run`, make it skip with reason "browser test, run by lead outside the sandbox" when Playwright is not importable, and list it in your report.

`dist/` is rebuilt once at integration. Prove the build works, then restore it before committing.

Banned: loosening, skipping or deleting existing tests; swallowed errors; sleeps or timers for test ordering; refactors, renames or formatting outside your scope.

Docs: write `contrib/deepsignal/console/docs/<id>.md` for a ship tech: what it does in one sentence, how to turn it on or configure it (copy-paste example), how to see it working, what it does NOT do.

## Acceptance (run from `contrib/deepsignal/console`, paste the tails)
```
npx oxlint && npx tsc -b --noEmit
```
```
npx vitest run
```
```
npm run build && git checkout -- dist && git clean -fdq dist
```

## Result (builder fills in)
- Head sha:
- RED receipt:
- Acceptance tails:
- Open questions:
