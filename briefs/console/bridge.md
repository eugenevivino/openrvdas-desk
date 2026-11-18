# Brief: console module `bridge` (wind dial and bridge page)

- Decision: D-CONSOLE1, MVP #1. Risk tier: medium (angle math). Module id: `bridge`

## Goal
The bridge sees wind, heading, speed, depth, barometer trend, temperatures and position at a glance, day or night, on one screen with no scrolling.

## Vector-wind facts (from branch deepsignal/vector-wind docs; do not re-derive)
The VectorWindAverageTransform emits `<prefix><speed_field>` and `<prefix><direction_field>`, e.g. `Avg1mPortTrueWindSpeed` and `Avg1mPortTrueWindDir`, plus optional `...SpeedMax` (gust), `...SpeedSteadiness`, `...DirStdDev` and `...SpeedCount`. Directions are degrees in [0, 360) in the convention given (true wind "from"). A window with too few samples is missing, never filled.

## Build
- Tile `wind-dial`. Settings:
  - `speed`, `direction`, `heading` (fields).
  - `gust` (optional field), `unit` (default kn), `label`.
  - `average_label` (e.g. "1 min vector mean").
- The dial is SVG and per the mockup:
  - A North up / Ship up toggle, stored per screen.
  - A ship outline rotated to the heading (North up).
  - The wind arrow points from the direction the wind comes from.
  - The numbers show speed, "from" with compass point, and "relative to bow" with port/starboard.
- All angle math lives in one pure file, `angles.ts`: relative angle, side, compass point, wraparound. If heading is STALE or NO_DATA, the relative-to-bow value shows "—" with the reason, never a stale computation.
- Tile `nav`: heading true (big), COG and SOG beneath. Fields are settings.
- Preset `bridge`, order 10. Fields:
  - Wind: `Avg1mPortTrueWindSpeed`/`Avg1mPortTrueWindDir`, falling back to `PortTrueWindSpeed`/`PortTrueWindDir`.
  - Heading `S330HeadingTrue`, COG `S330CourseTrue`, SOG `S330SpeedKt`.
  - Depth `Knud3Depth`, barometer `MwxBaroPress` (number with `trend: 180`), air `MwxAirTemp`, SST `TsgTemp`, position `S330Latitude`/`S330Longitude`.
  - Uses core's `number` tile type for plain values.
- Fits a 1366x768 screen without scrolling.

## Tests first
`angles.test.ts`:
- Relative angle at 0, 90, 180, 270, 359/1 and 1/359.
- Port vs starboard.
- Compass points at boundaries.
- Heading-stale behavior.

`windDial.test.tsx`:
- The toggle persists.
- Rotations are correct for the fake feed.
- Token colors only.

Browser test (lead_run): the Bridge preset in Night red has no pixel with G or B > 0.15 R, and there is no vertical scroll at 1366x768.

## Scope
`contrib/deepsignal/console/src/modules/bridge/**`, `contrib/deepsignal/console/docs/bridge.md`, `contrib/deepsignal/test/console/test_bridge_browser.py`.

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
