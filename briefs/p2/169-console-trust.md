# Brief: p2-console-trust (Science trust view (read-only console page))

- Decision: IDEAS #169, from Eugene's 2026-11-18 asks (config assist, sensor init, ecosystem and compression); build per D-NIGHT1
- Risk tier: low
- Module: exactly one. Branch `deepsignal/p2-console-trust` from `deepsignal/console-contract`
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: console, fork only
- Value (techs/science/shore): 2/5/4
- Depends on: console contract; reads QC, freshness and, when present, #164 calibration and #162 chain fields

## Goal
A scientist answers "can I trust this number right now?" without waking a tech. For each variable the page
shows freshness, QC state, the calibration in use, source instrument, units, known outages and notes, with
no controls. Evidence: desk `docs/PAIN-POINTS.md` (Deep Research, 2026-11-18); mapping in `docs/PAIN-POINTS-MAP.md`. (science-party findings; opportunity "Role-based displays").

## Build
- Module id `trust`, route `trust`, titled "Can I trust it?", order 15. Read-only and no actions.
- One card per variable group (by logger). Each variable has:
  - its value with units
  - freshness word plus shape plus age
  - QC word from `<field>_QC` (absent shown as "not checked")
  - `<field>_cal_version` and `_cal_state` when present (else "calibration not tracked")
  - source logger
  - the chain root from `ds_chain:<logger>:root` when present
- A verdict line per variable, in order:
  - "Not trustworthy now" when stale, no data, or QC 4.
  - "Use with care" when QC 3 or 9, the calibration state is none, or the chain is degraded.
  - "Looks good" only when fresh, QC 1 and no chain problem.
  - Otherwise "Not checked".
  The page never says "Looks good" without a QC flag.
- A "Known outages" list: the last 24 h of STALE or NO_DATA periods per variable, from the store's
  history, if the contract exposes it. If not, the section says it is not available yet.

## Tests first
`trust.test.tsx`:
- Each verdict rule including the no-QC case.
- Calibration fields shown when present.
- The chain root shown when present.
- Units always shown.
- Text-only rendering.
- Night mode tokens only.

## Scope
`contrib/deepsignal/console/src/modules/trust/**`, `contrib/deepsignal/console/docs/trust.md`.

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
