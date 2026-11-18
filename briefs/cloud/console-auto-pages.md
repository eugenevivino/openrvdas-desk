You are building ONE piece of the DeepSignal Console, a display overlay on OpenRVDAS, on Eugene's own fork. Work only in this repository (eugenevivino/openrvdas). Do NOT touch, open pull requests against, or push to OceanDataTools or any upstream repository. Nothing here is sent upstream.

Branches: create branch `deepsignal/console-mod-auto-pages` from `origin/deepsignal/console-contract` (if `deepsignal/console-mod-auto-pages` already exists on origin, check it out instead). Commit your work on that branch only, with one clear commit message, and leave it pushed to origin `deepsignal/console-mod-auto-pages`. Do not touch any other branch, `dev` or `master`. If you cannot push, leave the commit on the branch in your task and say so.

Environment notes: Node 22 or newer, with `node_modules` already installed in `contrib/deepsignal/console` by the environment setup (if `node --version` is below 22 or `node_modules` is missing, stop and report). Use `python3.12` if it exists, otherwise `python3` (3.11 or newer). If pytest is missing use `python3 -m unittest`. If flake8 is missing, `pip install flake8` into a throwaway venv and say you did. Add no dependency of any kind. No network.

Write the failing test first and paste its RED output, then make it GREEN. Run every acceptance command at the end and paste the tails. Report under 40 lines: files changed, test names, RED then GREEN tail, acceptance results, any design point you disagree with (do not change a design silently), what you verified versus inferred, and what must run outside the sandbox.

Stop rule: two fix rounds still red means stop and report.

The full brief follows.

----------------------------------------------------------------

# Brief: console module `auto-pages` (zero-config pages)

- Decision: D-CONSOLE1, MVP #1 item a. Risk tier: low. Module id: `auto-pages`

## Goal
A ship that installs the console with no page files still gets useful pages on day one, built from what its loggers actually publish.

## Build
- Engine `auto-pages`:
  - After the cache's field list arrives (and again when it changes), recognize fields by name pattern, units and description (from `store.describe`).
  - Register pages with `ctx.pages.register()`, `source: 'auto:auto-pages'`. A ship file or preset with the same id always wins (core handles precedence).
  - Never subscribes to more fields than the pages show.
- Recognition table: `src/modules/auto-pages/rules.ts`, one entry per role. Roles:
  - heading, course, speed over ground, latitude, longitude.
  - true wind speed, true wind direction, averaged wind (`Avg*`).
  - air temperature, humidity, barometer.
  - sea temperature, salinity, fluorescence, depth.
  - Plus generic numeric fields.
  - Each rule takes a regex on the name, and optionally units and a description keyword. Write case-insensitive regexes that cover common OpenRVDAS and NBP1406 names (e.g. `HeadingTrue|Hdg`, `TrueWindSpeed`, `BaroPress|Baro`, `Tsg.*Temp|SST`, `Sal`, `Flr|Chl|Fluor`, `Depth`).
- Pages:
  - `bridge-auto`: "Bridge (auto)", order 11, only when heading or wind is found. Uses tile `wind-dial` if wind and heading are found, else `number`.
  - `science-auto`: "Science (auto)", order 21. Tile `chart` for each science role found, else `number`.
  - `all-fields`: "All fields", order 90. A `number` tile per numeric field, grouped by logger from `describe().logger`, max 200 tiles with a "and N more" note.
  - Emit the intended tile type plus `fallback: number` (contract section 3: core renders the fallback when a type is not installed).
- Each auto page title ends with "(auto)", and the page shows a one-line note: "Built from the fields this ship publishes. To change it, save a page file with id <id>."

## Tests first
`autoPages.test.ts`:
- From the fake feed's field list: the expected roles are found and the pages registered.
- No bridge page when heading and wind are absent.
- A name with mixed case still matches.
- The 200-tile cap.
- Re-registration when the field list changes.
- Never registers over a page id that already exists from a file (stub `pages.list()`).

## Scope
`contrib/deepsignal/console/src/modules/auto-pages/**`, `contrib/deepsignal/console/docs/auto-pages.md`.

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
