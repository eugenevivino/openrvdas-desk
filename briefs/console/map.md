# Brief: console module `map` (offline ship track map)

- Decision: D-CONSOLE1, IDEAS #107 (P-MAP in desk docs/TARGET-PARITY.md). MVP only if it lands and passes by 2026-11-21, else stretch. Risk tier: low. Module id: `map`

## Goal
The watch sees where the ship has been, colored by an underway measurement, with no internet.

## Build (no new dependency: no map library)
- Tile `map`. Settings:
  - `lat`, `lon` (fields; default `S330Latitude`/`S330Longitude`), `window` (default `2 h`).
  - `color_by` (optional field, e.g. `TsgTemp`), `events` (optional list of field names whose values are event text, e.g. `event:log`), `wide`.
  - `tiles` (optional URL template for local raster tiles, e.g. `tiles/{z}/{x}/{y}.png`, served next to the bundle), `zoom` (auto by default).
- Rendering on canvas with Web Mercator math in `mercator.ts` (pure):
  - Track line from `store.history()`, with breaks where position was missing (same gap rule as charts: more than 3x the median interval).
  - The current position is drawn as a ship marker rotated to heading if a `heading` field is set.
  - With `color_by`, color the track segments on a sequential scale built from the theme tokens (`--chart` to `--accent`; in Night red, brightness steps only), with a small legend showing the min and max and unit.
  - Event markers are hollow squares with labels on tap.
- Without `tiles`, draw a plain graticule (lat/lon lines and labels) on `--panel`. With `tiles`, draw the raster tiles under the track and in Night dim them through a dark overlay (never a light surface). A missing tile leaves the background; no error spam.
- Tap or click a track point: a tooltip with UTC time, position, and the `color_by` value with its quality and freshness words. The tooltip uses tokens (no light surface in Night).
- Position STALE or NO_DATA: the marker turns hollow, with "Position stale <age>".
- Preset: none (the Science page owner adds it at integration). Provide `docs/map.md` with an example tile config and how to make an offline tile folder from an existing MBTiles file using a common tool (instructions only, no script).

## Tests first
`mercator.test.ts`:
- Round-trip lat/lon to pixel at zooms 3, 8 and 12.
- The antimeridian case.
- Gap splitting.

`map.test.tsx`, with the fake feed:
- The track has the right number of segments.
- Color scale min and max.
- The tooltip shows the value as text.
- Stale position state.
- The tile URL template is filled correctly.
- A missing tile is handled.

## Scope
`contrib/deepsignal/console/src/modules/map/**`, `contrib/deepsignal/console/docs/map.md`.

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
