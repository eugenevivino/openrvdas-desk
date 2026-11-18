You are building ONE piece of the DeepSignal Console, a display overlay on OpenRVDAS, on Eugene's own fork. Work only in this repository (eugenevivino/openrvdas). Do NOT touch, open pull requests against, or push to OceanDataTools or any upstream repository. Nothing here is sent upstream.

Branches: create branch `deepsignal/console-mod-kiosk-night` from `origin/deepsignal/console-contract` (if `deepsignal/console-mod-kiosk-night` already exists on origin, check it out instead). Commit your work on that branch only, with one clear commit message, and leave it pushed to origin `deepsignal/console-mod-kiosk-night`. Do not touch any other branch, `dev` or `master`. If you cannot push, leave the commit on the branch in your task and say so.

Environment notes: Node 22 or newer, with `node_modules` already installed in `contrib/deepsignal/console` by the environment setup (if `node --version` is below 22 or `node_modules` is missing, stop and report). Use `python3.12` if it exists, otherwise `python3` (3.11 or newer). If pytest is missing use `python3 -m unittest`. If flake8 is missing, `pip install flake8` into a throwaway venv and say you did. Add no dependency of any kind. No network.

Write the failing test first and paste its RED output, then make it GREEN. Run every acceptance command at the end and paste the tails. Report under 40 lines: files changed, test names, RED then GREEN tail, acceptance results, any design point you disagree with (do not change a design silently), what you verified versus inferred, and what must run outside the sandbox.

Stop rule: two fix rounds still red means stop and report.

The full brief follows.

----------------------------------------------------------------

# Brief: console module `kiosk-night` (bridge kiosk and automatic night)

- Decision: D-CONSOLE1, MVP #1 item c. Risk tier: low. Module id: `kiosk-night`

## Goal
A bridge screen stays on its page, stays awake, never flashes, and can switch to Night by itself at sunset.

## Build
- Kiosk mode:
  - Turned on by URL hash suffix `#<page>-kiosk` or by `console.yaml` `modules.kiosk-night.kiosk_page`.
  - The tab bar hides (keys 1-9 are ignored) and only the Night button and dimmer remain.
  - Holds a screen wake lock and re-requests it on `visibilitychange`; tolerates rejection with a small "Screen may sleep" note.
  - A topbar slot (order 90) shows "Kiosk" with a long-press (2 s) to exit. No other way out from touch.
- Auto Night, off by default:
  - `modules.kiosk-night.auto_night: true`.
  - Computes sun elevation from ship position (fields from settings, default `S330Latitude`/`S330Longitude`) with the NOAA solar position algorithm, written in `sun.ts` (pure, no dependency).
  - Switches to Night when elevation < -6° (civil dusk) and back at dawn.
  - Hysteresis of 0.5°, so it never flips back and forth.
  - A manual change wins until the next crossing.
  - If position is STALE or NO_DATA, auto Night pauses and says so in the topbar slot.
- Uses only `ctx.lighting.set()`, `ctx.route` and `ctx.clock`.

## Tests first
`sun.test.ts`:
- Elevation against reference values within 0.5°, for San Diego 2026-06-21 at solar noon and sunset, and an equator and a high-latitude case.

`kiosk.test.tsx`:
- Hash parsing; tabs hidden; long-press exit with a fake clock.
- The wake lock is requested, and a rejection shows the note.

`autoNight.test.ts`:
- Crossing switches the mode; hysteresis; manual override; position-stale pause.

## Scope
`contrib/deepsignal/console/src/modules/kiosk-night/**`, `contrib/deepsignal/console/docs/kiosk-night.md`.

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
