You are building ONE piece of the DeepSignal Console, a display overlay on OpenRVDAS, on Eugene's own fork. Work only in this repository (eugenevivino/openrvdas). Do NOT touch, open pull requests against, or push to OceanDataTools or any upstream repository. Nothing here is sent upstream.

Branches: create branch `deepsignal/p2-console-chain` from `origin/deepsignal/console-contract` (if `deepsignal/p2-console-chain` already exists on origin, check it out instead). Commit your work on that branch only, with one clear commit message, and leave it pushed to origin `deepsignal/p2-console-chain`. Do not touch any other branch, `dev` or `master`. If you cannot push, leave the commit on the branch in your task and say so.

Environment notes: Node 22 or newer, with `node_modules` already installed in `contrib/deepsignal/console` by the environment setup (if `node --version` is below 22 or `node_modules` is missing, stop and report). Use `python3.12` if it exists, otherwise `python3`. Add no dependency of any kind. No network.

Write the failing test first and paste its RED output, then make it GREEN. Run every acceptance command at the end and paste the tails. Report under 40 lines: files changed, test names, RED then GREEN tail, acceptance results, any design point you disagree with (do not change a design silently), what you verified versus inferred, and what must run outside the sandbox.

Stop rule: two fix rounds still red means stop and report.

The full brief follows.

----------------------------------------------------------------
# Brief: p2-console-chain (Console chain view v0: why is this stream not healthy)

- Decision: IDEAS #162, from Eugene's 2026-11-18 asks (config assist, sensor init, ecosystem and compression); build per D-NIGHT1
- Risk tier: low
- Module: exactly one. Branch `deepsignal/p2-console-chain` from `deepsignal/console-contract`
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: console, fork only
- Value (techs/science/shore): 5/3/3
- Depends on: console contract only; reads the same store the health and stale-banner modules use; v1 stages come from #162 stream-health engine later

## Goal
For any stream, a tech sees one row of stages from logger to quality and the first stage that is not OK.
A dead feed, a silent parser and a bad sensor no longer look the same. Evidence: desk `docs/PAIN-POINTS.md` (Deep Research, 2026-11-18); mapping in `docs/PAIN-POINTS-MAP.md`. (pain points 1, 4, 6, 10).

## Build
- Module id `chain`, route `chain`, titled "Chain", order 31. Read-only.
- One row per logger (fields mapped with `describe().logger`, worst first). Each row has five stages, each
  with word plus shape plus age:
  1. **Logger**: from logger health (RUNNING OK, STARTING DEGRADED, FAILED FAILED, EXITED Off).
  2. **Arriving**: any of the logger's fields updated within its learned period (the core freshness rule).
     The rate is shown as records per minute.
  3. **Parsed**: the logger publishes its expected fields. Use the set seen in the last hour; a field that
     is missing while others arrive is DEGRADED. The latest stderr line matching `parse|could not|error`
     is the evidence.
  4. **Fresh**: the worst field freshness (LIVE, STALE, NO_DATA) with age.
  5. **Quality**: the worst `<field>_QC` flag when present (1 OK, 3 CHECK, 4 FAILED, 9 missing, absent shown
     as "not checked").
- Two more stages always show as "not monitored yet" (muted, no fault): Time and Stored. The engine (#162
  stream-health) fills them later through fields named `ds_chain:<logger>:<stage>` if present. Read those
  fields when they exist and prefer them over the v0 inference.
- The first stage that is not OK is outlined and its evidence line shown. Tapping a row expands the
  per-field list.
- Empty state: "Waiting for data from the logger manager."

## Tests first
`chain.test.tsx` with the fake feed:
- `flr1_fails` stops at Logger.
- `knud1_restart` stops at Arriving, then recovers.
- `tsg_suspect` stops at Quality.
- A field missing while others arrive stops at Parsed.
- Engine fields override inference.
- The not-monitored stages never count as faults.
- Sort order.
- Text-only rendering.

## Scope
`contrib/deepsignal/console/src/modules/chain/**`, `contrib/deepsignal/console/docs/chain.md`.

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
