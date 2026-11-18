# Brief: console unit fix job, slice A of 3 (D-UNITS1; after console unit review round 1: HOLD, 19 P1s)

- Branch `deepsignal/console-mvp` (the checked-out branch). Unit review: desk `research/2026-11-18-console-unit-review-r1.md`. Lane: Mac, `gpt-6.2-sol` high, one slice per run, slices A then B then C on the same branch.
- Parent briefs: desk `briefs/console/core-v2.md`, `briefs/console/INTEGRATION.md`, the module briefs in `briefs/console/`, `contrib/deepsignal/console/CONTRACT.md` and `DESIGN.md`; their rules hold.
- Each finding below needs code plus a regression test that fails before the fix. P2 and P3 items in the review become tickets; do not work on them.

## P1 findings to close in this slice (verbatim from the review)
- **P1 VERIFIED, partly fixed.** The browser now defaults to same-origin `/cds-ws`, but the stock proxy still reaches publish-capable CDS, and install/self-test lacks the #197 relay check and warning covering both nginx templates and the optional UDP bind. [pages.ts:51](/private/tmp/deepsignal/console-unit-rr/contrib/deepsignal/console/src/pages.ts:51), [install_openrvdas.sh:652](/private/tmp/deepsignal/console-unit-rr/utils/install_openrvdas.sh:652), [SelfTest.tsx:35](/private/tmp/deepsignal/console-unit-rr/contrib/deepsignal/console/src/modules/self-test/SelfTest.tsx:35)
- **P1 VERIFIED, open.** The installer adds `/console/` to every matching virtual host and inserts the supplied root path directly into nginx syntax. [install.sh:66](/private/tmp/deepsignal/console-unit-rr/contrib/deepsignal/console/install/install.sh:66), [install.sh:72](/private/tmp/deepsignal/console-unit-rr/contrib/deepsignal/console/install/install.sh:72)
- **P1 VERIFIED, open.** Chart and Stale Banner have `index.tsx` entry points, so the shipped `index.ts` glob omits the Science preset and every stale-sensor alert. [registry.ts:4](/private/tmp/deepsignal/console-unit-rr/contrib/deepsignal/console/src/registry.ts:4)
- **P1 VERIFIED, open.** A throwing store subscriber interrupts notification before CDS requests its next batch, stalling data for every module. [store.ts:166](/private/tmp/deepsignal/console-unit-rr/contrib/deepsignal/console/src/store.ts:166), [cds.ts:302](/private/tmp/deepsignal/console-unit-rr/contrib/deepsignal/console/src/cds.ts:302)
- **P1 VERIFIED, new.** Core skips QC subscriptions for every field containing `:`, so a namespaced measurement requested by Bridge or Map can lose its published FAIL flag. [cds.ts:220](/private/tmp/deepsignal/console-unit-rr/contrib/deepsignal/console/src/cds.ts:220)

## Acceptance (exact commands, from `contrib/deepsignal/console`)
```
npx oxlint
```
```
npx tsc -b --noEmit
```
```
npx vitest run
```
```
npm run build
```

## Scope
`contrib/deepsignal/console/src/` core files (cds.ts, store.ts, registry.ts, pages.ts and their tests), the Chart and Stale Banner entry-point file names only, and `contrib/deepsignal/console/install/**` with its tests. No module behavior changes in this slice. Install and CDS exposure are security: keep the #197 read-only `/cds-ws` relay as the only browser path, add the install and self-test check and warning for both nginx templates and the optional UDP bind, and never edit nginx server blocks other than the one the operator names.

## Non-goals and banned
No new features, no deleted, skipped or loosened tests, no sleeps in tests, no new dependencies, no sub-agents, no dist edits by hand.

## Stop rule
Report any finding that needs a change to a parent brief's design instead of changing it.
