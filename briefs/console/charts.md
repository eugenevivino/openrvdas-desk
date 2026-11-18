# Brief: console module `chart` (underway strip charts)

- Decision: D-CONSOLE1, MVP #1. Risk tier: medium. Module id: `chart`

## Goal
The science watch sees underway strip charts where missing data shows as a gap, never as a smooth line.

## Build
- Tile type `chart` on uPlot (already a dependency). Settings:
  - `field`, `label`, `unit`, `decimals`.
  - `window` (e.g. `30 min`, `6 h`).
  - `period` (optional), `wide`, `size: normal|large`.
- Y range is auto with a 12% margin, with min and max labels in `--f-mono`.
- Insert a gap where the spacing between samples is more than 3x the median interval.
- When the field is STALE or NO_DATA, draw a "NO DATA" label after the last point.
- Show the current value with the quality and freshness words above the plot. In SUSPECT or FAIL, mark the affected points with a hollow marker.
- Read tokens at draw time and redraw on `ctx.lighting.subscribe`. Data comes from `ctx.store.history()` plus live `subscribe`.
- Holds 6 h at 1 Hz per field. Budget: under 16 ms per redraw for 4 charts of 21,600 points (measure in a test with a fake canvas or a timing of the data step).
- Preset `science`: SST (`TsgTemp`), salinity (`TsgSal`), fluorescence (`FlrChl`), depth (`Knud3Depth`), 30 min each.

## Tests first
`chart.test.ts(x)`:
- Gap insertion on the `knud1_restart` gap.
- NO DATA after `flr1_fails`.
- SUSPECT markers from `tsg_suspect`.
- Redraw when lighting changes.
- `validate` errors for a bad window, in the PageProblem format.
- The performance budget.

## Scope
`contrib/deepsignal/console/src/modules/chart/**`, `contrib/deepsignal/console/docs/chart.md`.

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
