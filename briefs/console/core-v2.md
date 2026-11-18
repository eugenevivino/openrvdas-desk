# Brief: console-core-v2 (implement the contract)

- Decision: D-CONSOLE1, MVP #1 (Eugene 2026-11-18, target 2026-11-25). Risk tier: medium (read-only display)
- Base state (2026-11-18 07:26Z): deepsignal/console-core is at 82ec7ca. It already has the v2 freshness model (T from page `period` or learned; a provisional 1 s period until two samples), QARTOD quality badges, two night palettes with default dim 0.8, the "Research system monitoring" label, a night-safe boot and error path, and the empty-backfill retry. 26 Vitest tests and the live browser test pass. Reuse that code: move it behind the contract types (store.ts, context.ts, modules/number). Do not rewrite working logic. Existing tests must stay green (adapt imports only).
- First step: `git merge --no-edit origin/deepsignal/console-contract`. It only adds files, so there should be no conflicts.
- Upstream home: openrvdas_contrib, `contrib/deepsignal/console/`

## Goal
Core becomes the host every other console module plugs into. It implements the contract exactly, so module branches merge in without edits.

## Build exactly this
1. `src/registry.ts`: `import.meta.glob('./modules/*/index.ts', { eager: true })` and collect every module's default `ConsoleModule`. If a module throws, or exports a bad shape, show a plain message naming the module and keep the rest of the console working.
2. `src/store.ts`: implements `FieldStore` on top of the existing `cds.ts` client.
   - Freshness, QARTOD quality (`qc_suffix` from console.yaml, default `_QC`; `_QC_<test>`, `_QC_reason`), health default UNKNOWN, `setHealth({logger})` using `describe(field).logger` or the tile `logger:` key, `lastGood`, and `history(field, s)` from the backfill plus live data.
   - Subscribe only to fields that visible tiles, routes and adapters ask for, plus `status:*` when an adapter asks.
   - Empty first backfill: if the window returns nothing for a field, request the latest value once with no window.
3. `src/context.ts`: builds `ConsoleContext`:
   - Alerts store and lighting API, with `nightPalette` red|neutral, dim 0.15 to 1.0 stored per screen, default dim 0.8 for red.
   - Pages registry: precedence file > preset > auto for the same id, and `console.yaml` `pages:` order.
   - Hash route API and the real clock.
4. `src/modules/number/`: the `number` tile.
   - Settings: label, field, unit, decimals, `sparkline` minutes, `period`, `logger`, `wide`, `trend` minutes (rising/falling/steady with the change per period), `compass: true` (adds NNW etc.).
   - Shows quality and freshness as separate word+shape badges; PASS and LIVE are small and muted.
   - NO_DATA shows "—" plus "Last: <value> <unit> at <UTC>".
   - Move the current number tile code here. Nothing else in the app may know tile internals.
5. `src/modules/example/`: the current example page as a preset.
6. App shell renders routes and tile pages from the registry, `topbar` and `banner` slots, and engines (started once, stopped on unmount). A banner slot area exists even when empty.
7. Lighting:
   - Two night palettes (DESIGN.md v2 tables).
   - Red/Neutral switch next to the dimmer.
   - Persistent top-bar label "Research system monitoring".
   - The boot script sets mode and palette before first paint on every path, including errors.
   - Error, config-error, loading and reconnect states all use tokens.
8. `src/testkit/`: `makeFakeContext(feed, opts)` and `stepClock(s)`, built from `src/contract/fake-feed.json`, for future module tests. Not used by production code.
9. Unknown tile types: if a tile's `type` is not registered and it has `fallback: <type>`, render the fallback; otherwise show the plain PageProblem message for that tile only (contract section 3).
10. `console.yaml` gains `qc_suffix`, `night_palette`, `modules:` (per-module settings), and `period` overrides. All have defaults and are documented in README.

## Tests first (RED then GREEN)
- `store.test.ts`:
  - Freshness boundaries at 2T, 5T and the hard timeout, with T learned from intervals.
  - `lastGood` is kept.
  - Quality mapping includes the absent flag and a custom suffix.
  - PASS+STALE and SUSPECT+LIVE are independent.
  - `setHealth` by logger.
  - The empty-backfill retry.
- `registry.test.ts`: two fake modules are discovered; a throwing module gives a message and does not break the others.
- `context.test.ts`: page precedence and order; alerts raise/ack/clear/subscribe; lighting persists and switches palettes; red at dim 0.15 and 1.0 has G,B <= 0.15 R; neutral keeps alarm hue distinct.
- `number.test.tsx`: badges, NO_DATA rendering, trend, compass, using the testkit and the fake feed's `flr1_fails` and `tsg_suspect` scenarios.
- Extend `contrib/deepsignal/test/console/test_console_live.py` (`@pytest.mark.lead_run`):
  - Stop publishing → AGING then STALE.
  - Publish `<field>_QC`=3 → SUSPECT badge while LIVE.
  - A Night red screenshot has no pixel with G or B > 0.15 R.
  - Reload in Night never paints a light first frame.

## Scope (you own these)
Everything under `contrib/deepsignal/console/` except `src/contract/**`, `CONTRACT.md`, and `src/modules/*` other than `number` and `example`. Also `contrib/deepsignal/test/console/test_console_live.py`. This task MAY change shared files; it is the only one that does. Rebuild and commit `dist/` at the end (the exception to the restore rule).

## Acceptance for this task (from contrib/deepsignal/console)
```
npm run lint && npm run type-check && npm run test && npm run build
```
```
python3 -m pytest contrib/deepsignal/test/console/ -v
```
(run from the repo root; lead_run tests skip here)
```
flake8 contrib/deepsignal/test/console/
```

## Rules every console task follows

Read these files in the repository first: `contrib/deepsignal/console/CONTRACT.md`, `contrib/deepsignal/console/src/contract/index.ts`, `contrib/deepsignal/console/DESIGN.md` (the "Rulebook v2 additions" section wins over v1 where they differ). The contract is fixed: never edit `src/contract/**` or `CONTRACT.md`. If the contract blocks you, stop and say exactly what you need.

Ownership: you own ONLY the paths listed under Scope. Everything else is read-only, in particular `src/registry.ts`, `src/App.tsx`, `src/main.tsx`, `src/cds.ts`, `src/store.ts`, `src/lighting*.ts`, `src/pages.ts`, `src/index.css`, `index.html`, `package.json`, `package-lock.json`, `vite.config.ts`, `tsconfig*.json`, `.oxlintrc.json`, `DESIGN.md`, `README.md`, `public/**`, `dist/**`, `demo_cache.py`, `contrib/deepsignal/configs/**`, other modules' folders, and `contrib/deepsignal/test/console/test_console_live.py`. No new dependency of any kind.

Your module is `src/modules/<id>/index.ts` default-exporting a `ConsoleModule` (types in the contract). Core discovers it by glob; do not register it anywhere. If core's registry is not on your branch yet, that is expected: your tests import your module directly.

Tests: Vitest on jsdom, beside your code (`src/modules/<id>/*.test.ts(x)`). Build a minimal fake `ConsoleContext` inside your own folder (for example `src/modules/<id>/testkit.ts`) from `src/contract/fake-feed.json`, with a fake clock you step. Cover every behavior named in this brief. Use only `ctx.clock.now()` for time.

Screens: word + shape for every state, color third; tokens only (`--bg --panel --panel2 --line --fg --muted --accent --ok --check --stale --down --chart --grid` and fonts `--f-number --f-body --f-mono`), never literal colors; canvas/SVG read tokens at draw time and redraw on `ctx.lighting.subscribe`; Night must never paint a light surface (empty, loading and error states included); plain English, units always shown; touch targets at least 44 px; bridge sizes: primary value 48 px, labels at least 18 px, metadata at least 16 px; render all data as text (no `innerHTML`, no `dangerouslySetInnerHTML`, no `eval`).

Browser checks: Chromium does not run in this sandbox. If the brief asks for a browser test, write it as `contrib/deepsignal/test/console/test_<id>_browser.py`, mark it `@pytest.mark.lead_run`, make it skip with reason "browser test, run by lead outside the sandbox" when Playwright is not importable, and list it in your report.

`dist/` is rebuilt once at integration. Prove the build works, then restore it before committing.

Banned: loosening, skipping or deleting existing tests; swallowed errors; sleeps or timers for test ordering; refactors, renames or formatting outside your scope.

Docs: README sections for core settings.
Not applicable to core-v2: the ownership list and the dist restore rule (core owns shared files and commits dist).

Module docs rule, for reference: write `contrib/deepsignal/console/docs/<id>.md` for a ship tech: what it does in one sentence, how to turn it on or configure it (copy-paste example), how to see it working, what it does NOT do.

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
