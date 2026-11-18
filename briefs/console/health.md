# Brief: console module `health` (logger health page)

- Decision: D-CONSOLE1, MVP #1. Risk tier: medium. Module id: `health`. Read-only: no start or stop buttons.

## Goal
A tech sees every logger worst first, with a plain line saying what to try for anything not OK.

## OpenRVDAS facts (quoted from server/logger_manager.py; do not re-derive)
- `status:logger_status` value: `{logger_name: {'config': config_name, 'status': status}}`. The status is one of `RUNNING`, `STARTING` (runnable, not running, not given up), `FAILED`, or `EXITED` (not runnable, e.g. the off config). It is sent every manager loop (a few seconds).
- `status:cruise_mode`: `{'active_mode': name}`.
- `stderr:logger:<logger>`: one formatted stderr line per record.

## Build
- Adapter `logger-status`:
  - Subscribes `status:logger_status`, `status:cruise_mode`, and `stderr:logger:*` (use `store.listFields()` to expand the wildcard).
  - Maps RUNNING to OK, STARTING to DEGRADED, FAILED to FAILED, and EXITED to "Off" (shown as Off, not a fault; health UNKNOWN).
  - Calls `store.setHealth({logger}, ...)` with the evidence text.
  - If `status:logger_status` itself goes STALE (its period is learned), the page says "Logger manager not reporting since <UTC>" and does not invent states.
- Route `health`, titled "Health", order 30. It shows:
  - A summary row of counts per state (word + shape).
  - One row per logger, sorted worst first and then by name. Columns: state, logger, config name, newest field's freshness and age (fields mapped via `describe().logger`), the latest stderr line shortened to 120 chars (full text on tap), and a "What to try" line.
  - The cruise mode at the top.
- Hints: `src/modules/health/hints.default.yaml` (imported `?raw`). It is a list of `{match: {logger?: glob, stderr?: regex}, hint: text}`, first match wins.
  - Ship override: fetch `hints.yaml` next to the bundle if it exists. A missing file is fine; a bad file gives a plain message and the defaults are used.
  - Defaults cover: no data on a serial port, permission denied on /dev/tty*, could not open port, parse errors, disk full, clock or time offset, and a logger restarting repeatedly.
- Empty state (no status yet): "Waiting for the logger manager. If this lasts over a minute, check that logger_manager is running (supervisorctl status)."

## Tests first
`health.test.tsx`, using the fake feed:
- State mapping for all four statuses.
- `flr1_fails` sorts first with the serial-port hint.
- `rad1_off` shows Off and is not counted as a fault.
- `knud1_restart` shows DEGRADED then OK.
- Manager stale message.
- Hint precedence and a bad override file.
- stderr rendered as text (a `<script>` string stays literal).

## Scope
`contrib/deepsignal/console/src/modules/health/**`, `contrib/deepsignal/console/docs/health.md`.

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
