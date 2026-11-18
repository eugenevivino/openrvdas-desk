You are building ONE piece of the DeepSignal Console, a display overlay on OpenRVDAS, on Eugene's own fork. Work only in this repository (eugenevivino/openrvdas). Do NOT touch, open pull requests against, or push to OceanDataTools or any upstream repository. Nothing here is sent upstream.

Branches: create branch `deepsignal/console-mod-stale-banner` from `origin/deepsignal/console-contract` (if `deepsignal/console-mod-stale-banner` already exists on origin, check it out instead). Commit your work on that branch only, with one clear commit message, and leave it pushed to origin `deepsignal/console-mod-stale-banner`. Do not touch any other branch, `dev` or `master`. If you cannot push, leave the commit on the branch in your task and say so.

Environment notes: Node 22 or newer, with `node_modules` already installed in `contrib/deepsignal/console` by the environment setup (if `node --version` is below 22 or `node_modules` is missing, stop and report). Use `python3.12` if it exists, otherwise `python3` (3.11 or newer). If pytest is missing use `python3 -m unittest`. If flake8 is missing, `pip install flake8` into a throwaway venv and say you did. Add no dependency of any kind. No network.

Write the failing test first and paste its RED output, then make it GREEN. Run every acceptance command at the end and paste the tails. Report under 40 lines: files changed, test names, RED then GREEN tail, acceptance results, any design point you disagree with (do not change a design silently), what you verified versus inferred, and what must run outside the sandbox.

Stop rule: two fix rounds still red means stop and report.

The full brief follows.

----------------------------------------------------------------

# Brief: console module `stale-banner` (dead and stale sensor alerts)

- Decision: D-CONSOLE1, MVP #1 item b (meets the "bad sensor noticed in under 1 hour" metric). Risk tier: medium. Module id: `stale-banner`

## Goal
When a sensor goes quiet or a logger fails, everyone sees one clear line saying what, since when, and what to try first, without noise.

## Build
- Engine `stale-alerts`, evaluated once per second with `ctx.clock`:
  - A field that has been STALE for more than 30 s raises A3 Caution: "<label or field> stale for <age>".
  - A field in NO_DATA raises A2 Warning: "<field> no data since <UTC>".
  - A logger FAILED (from field health FAILED) raises A2: "<logger> logger failed".
  - Group by logger (`groupKey = logger`) so one dead logger gives one row with a count of affected fields, not one row per field.
  - Clear automatically when the condition ends, and log the clear in the alert history (in-memory, last 200).
  - `firstAction` comes from a small built-in table: serial loggers say to check the cable and port; network ones the source host; else "Check the Health page."
  - Fields with no `describe().logger` group under "unassigned".
  - Settings in `console.yaml` `modules.stale-banner`: `ignore: [field globs]`, `stale_grace_s` (default 30).
- Slot `banner`, order 10. It shows the highest tier first, one line per group: tier word + shape, title, age, first action.
  - Tap to expand the affected fields. Ack button for A1/A2 (acked rows stay, dimmed but readable).
  - Shows "N more" past 3 rows. No audio. No animation, except an unacknowledged A1 (none raised here).
  - Empty means nothing is rendered.
- Never raises anything from AI or quality flags in this module (quality is separate).

## Tests first
`staleAlerts.test.ts(x)`, stepping the fake clock through the fake feed:
- `flr1_fails` gives one grouped A2 by about t=240, with the FAILED logger and the field as children.
- `knud1_restart` gives an A3 that clears after recovery.
- `tsg_suspect` raises nothing.
- `ignore` works.
- Ack keeps the row.
- The banner renders text only and sorts by tier.

## Scope
`contrib/deepsignal/console/src/modules/stale-banner/**`, `contrib/deepsignal/console/docs/stale-banner.md`.

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
