# DeepSignal handover for Codex (2026-11-19, from the MacBook build lead)

Self-contained. Read this first, then `docs/STATE.md`, `docs/DECISIONS.md` and `MORNING.md`. Plain words; no secrets here.

## Master directive continuation (2026-11-21; current)

Current worktree `/private/tmp/deepsignal/product-m1-20261121`, branch
`deepsignal/workspace-m1`, based on integrated pilot b67f3072. Lead owns
`claims/unit-workspace-m1`; helpers have finished their disjoint UI/MCP work.
Read the worktree's `contrib/deepsignal/workspace/PROGRESS.md`, DESIGN.md and
compatibility.json. All work is fixture-only, with no live executor or Grafana
connection. The 22 deliverable tickets in MASTER-PRODUCT-TICKETS.md cover both
new directives. Full M1 and Grafana remain incomplete.

Build/test uses existing runtime-v11 Relay plans under
`/private/tmp/deepsignal/product-m1-evidence/`; inspect their actual receipts.
Source HEAD `1eb13ac2e46fd04f29828911fc21845677c9e6e4` includes Relay-built
Console distribution. R1 passed checks but audit rejected MCP child cache files;
retained as invalid. R2 audit is clean: six service/HTTP tests, actual 13-tool SDK
journey, CLI, 277 frontend tests, lint/build passed; browser found asset concurrency
refusals. R3 fixes the HTTP asset burst while serializing service calls; six tests
and actual Chromium full draft/replay/export journey PASS, audit clean. Unchanged
R2 frontend/MCP/CLI evidence is retained, not rerun. R3 report is at
`/private/tmp/deepsignal/product-m1-evidence/m1-r3-state/report.json`; all workers
terminal. Handoff max 0.064s, not an end-to-end engineering latency measurement.
Required gates remain HOLD: whole-module scientific/security/usability independent
review, independent reference evidence, exact-candidate Linux, remaining M1 scope.
Source-only independent findings were regression-tested and repaired; that is not
formal release approval. Next: finish bounded service/HTTP failure-case tests,
then current-head review/Linux; continue mandatory Grafana discovery/draft scope.
Do not call M1 complete or activate services/production. Preserve old receipts.
The user explicitly superseded the 1% reserve for this allowance window and
asked for useful engineering through exhaustion. No reset/overage purchase.

## Relay checkpoint (2026-11-20; inspect live state before continuing)

Continue DeepSignal product work. Provider succession is only a contingency after
Codex exhaustion; Claude is optional. Codex was verified at 2% remaining during
this checkpoint; retain the 1% reserve and recheck before any new model job.
No successor takeover or Claude engineering job is claimed.

Authoritative desk: `/private/tmp/deepsignal/desk-main`. Relay source:
`/private/tmp/deepsignal/relay-20261120/repo` at `247f58f`. Immutable runtime-v11
owns the current guarded validation; do not edit live runtimes or clear
uncertain claims. Kalon owns the shared allocator. Existing supervisors remain
in charge; Relay is PILOT/STAGED, not production.

Completed fixture pilots: Console and Stream Health view at
`b67f3072daee63d0d307a16bc1d34e24b3c75002`, tree 4b19186fca8315d2fdab1de5b90fe17797dbcd72.
Normal fast-forward to fork `eugenevivino/openrvdas:deepsignal/integration` was
pushed and verified from prior bff54ec. The pilot topic points to the same commit.
Both unit claims are released; docs/units.json preserves older stamps in history
and records all five exact-head stamps. Run tools/finish-line.py for counts.

Source: 272 frontend tests, lint/types, both unchanged full native design checks in
`combined-r9-release-state`, and Linux 44732250214 (workflow 07f277e, all 3 jobs) PASS.
Fresh standalone Astra Ultra session 01a1f8d7-55fd-7622-b89f-7de9ad0cd9fd returned
PASS, CRITICAL:no, no blocking P1, and recommended integration after exact Linux.
Evidence: research/2026-11-20-relay-pilots/{combined-astra-r9-pass.md,r9-native-checks.json,r9-linux-jobs.json}.
D-REVIEW1 approval is logged. This append changes no acceptance rule; exact prior
governing DECISIONS bytes are frozen as governing-decisions-before-pilot-integration.md
(SHA256 56435a6f0fe32e5a827c58de32db2806d7330f1f89f245335fad6a52615cdf2e).
Historical Relay receipts/contracts remain unchanged; do not rewrite old HOLDs as PASS.

No native/model pilot worker remains active after these terminal checks/review.
Check actual processes/claims before new work. Codex last verified 2%, reserve 1%.
A successor is optional after exhaustion, not a separate provider-setup project.
Next product work: verify eligible backlog prerequisites/design/acceptance before
claiming a new whole unit; existing scientific and critical holds remain.
Relay production remains held pending typed verified gate import/policy version
handling, forced-termination retirement, authoritative shared lease/fencing and
safe owner transfer. Kalon owns shared allocator; DeepSignal Mini client is staged,
no Mini job admitted. No supervisor/service replacement, ship deployment, installer
activation, Stream Health engine qualification or 24-hour soak is claimed.
## Historical checkpoints (superseded by the completion above)

All observations below are retained historical evidence, not current status.

Product evidence (all paths below relative to `/private/tmp/deepsignal/relay-20261120`):

- Console `57182e5eb5c7a76fdecd918d7b6de259762084fd`: full Mac self-check GREEN,
  Linux run44710257259 all three jobs PASS, 205 frontend tests. Fresh source and
  exact identity reviews PASS. The earlier branch-alias HOLD is preserved with
  its explicit independent clarification.
- Stream view `a3532f38c78305aa3a07d6f8be5d3c76ed6ae6c0`: full Mac self-check GREEN,
  Linux run44712385947 PASS (192 frontend tests plus Chromium). Source and final
  artifact reviews PASS. Stale and expired reports retain producer history and
  QC; the original75a71c1 HOLD and red regression evidence remain preserved.
- Combined `2ea3e609cef657398681adc5a0b2c866d0132a69`, tree
  `4e54acc5973211aa4073430f65e1f21001712c95`, base `bff54ec722bd8bf2c0ee949c91528642e0140e26`:
  both unchanged design self-checks PASS. Immutable check-0.log and check-1.log
  are in `combined-release-state/attempts/00ee6aff831b379be1e5/000001-000001/`.
  Linux44714303424 attempt1 failed only checkout before tests; source publication
  was corrected using a named, fetched remote without bypassing the hook.
  Attempt2 all3 jobs PASS, verified through the GitHub jobs API; snapshot is
  `research/2026-11-20-relay-pilots/combined-linux-jobs.json`.
- Fresh standalone Astra Ultra review at the combined SHA returned **HOLD**, not
  approval. Three P1 cases: navigating during an outage hides known failure
  history; the first delayed report after a completed page switch overwrites
  learned cadence; `_QC_` inside a valid stream name suppresses QC subscription.
  Formal answer is copied to `research/2026-11-20-relay-pilots/combined-astra-hold.md`.
  Prior individual PASS reviews do not clear these combined findings.
- Review job `deepsignal.final-integration-review.d76d141032fe171690a0c079`
  is terminal BLOCKED in `native-review/state`; session
  `01a1f85f-ade6-7941-be5a-bbad3b48e162` explicitly reports gpt-6.2-astra,
  ultra, read-only. Installed ds-codex was not changed: a hashed private copy
  retained its safety checks and delegated claim ownership to Relay. Provenance
  and bounded logs are in `native-review/`. No review subagent credit was used.
- Repaired final candidate `9935ed82d949f0ba057164d24cce502eca9110a4` is published
  on `deepsignal/relay-combined-pilot-20261120`. Source23abbd04 repairs all3 reported
  cases and preserves QC-only semantics. All223 frontend tests passed, both full
  Mac design self-checks passed, and exact Linux44718633913 all3 jobs PASS. The
  workflow source pin is2de07681382205209bf3ebf8f30c8d316d340343. Evidence snapshots
  are `research/2026-11-20-relay-pilots/repaired-{native-checks,linux-jobs}.json`.
- Historical native fresh independent Astra Ultra re-review is terminal HOLD in `native-review-r2/state`,
  job `deepsignal.final-integration-review.d99a8ae3eededc4d799cbe50`, supervisor68735,
  session `01a1f87c-fe63-7c61-9ca4-d82834ddacad`. Verify actual terminal state and
  answer before any integration. The original HOLD remains until explicit PASS.
- Focused red evidence is retained in integration-qc-red-state (2fail),
  integration-outage-red3-state (2Missing failures) and integration-repair-check2-state
  (2cadence failures: LIVE with30s/60s instead ofSTALE with1s/2s). Intermediate
  fixture mistakes and the full-suite regression are retained, never relabeled.
  The repaired frontend suite passed223 tests; unsupported role-option type error
  was removed at23abbd04, then final full gates reran on the generated bundle.
- Runtime-v11 pins required Python 3.12 and stable boot UUID. Earlier plans built
  with Xcode Python3.9 used process-relative clock samples and repeatedly warmed
  up. Sole owned prelaunch supervisor22797 was cancelled before any native test,
  its child22798 was verified retired, and the original terminal receipt retained.
  No foreign claim or protected worker was touched. Relay247f58f refuses plan
  generation belowPython 3.12; regression was RED then2focused tests PASS.
- Measured worker handoff: failed cadence regression to next independent frontend
  worker0.061654s. Source is two worker-result.json timestamps, preserved in
  `research/2026-11-20-relay-pilots/independent-job-handoff.json`. This measures
  supervisor start; command startup and host safety waits remain separate.


No new module is integrated or qualified by this checkpoint. Current P1 findings
block both pilot release stamps; preserve the registry's older historical stamps.
The held 24-hour soak, installer approval, security ownership and ship activation
are unchanged. Exact tests/review must cover the repaired combined candidate.

Relay tests: 74 core and105 adapter checks passed in
`evidence/core-final-repair-tests.log` and `evidence/adapter-final-repair-tests.log`;
later focused provider, latency and boot-identity regressions are separate receipts,
not a claimed fresh full-suite run. The latency correction includes all attempts,
including admission retries. Six v9 handoffs measured median0.043623s and max0.058267s
excluding recorded Relay reservation waits. Host admission is a separate guard;
there is no measured utilization or completed-module throughput improvement yet.
`38baeff` uses validated kern.bootsessionuuid and a versioned local swap-observation
cache so wall-clock adjustment cannot repeatedly invalidate same-boot evidence.
It preserves the five-minute rolling check; existing runtimes remain immutable.

Mini: approved common1GiB lightweight policy pinned at owner commit a54ebb87,
blob3a2ae7c1, SHA-256 c9547b03...f1b064. `mini-job/manifest.json` prepares19 bounded
Store/retry fixtures (128MiB peak, one CPU,60s, zero native slots); local preflight
passed. No DeepSignal Mini job or authoritative shared lease was launched.
Live owner policy, reservations and local guards must all admit it first.

Next: finish the focused red/green repairs, retain every original failure and HOLD,
run affected checks then exact bundle/native/Linux qualification and fresh bounded
Astra review. Only a new PASS can authorize fork integration under D-REVIEW1.
Review import, host retirement/restart safety and owner transfer still need their
own qualification before unattended Relay production. Continue independent eligible
work subject to current claims, pauses, scientific evidence and resource budgets.
The74-unit backlog inventory is evidence inventory, not launch or review approval.

Sync only the authorized topic branches. Desk main push was rejected by automatic
approval review; do not retry it or route around that refusal through a supervisor.

## 1. Goal

DeepSignal is an overlay on OpenRVDAS (ship data acquisition): a console, data-quality modules and setup tools,
built on Eugene's fork. The Nov 25 MVP (a Wednesday, D-SEC6) is a **supervised pilot** of the console beside the
existing bridge display, not a cutover. Cutover only after the release checks in D-SEC6.

## 2. Hard rules (never break these)

1. **Nothing to OceanDataTools** (D-UPSTREAM0): no pushes, PRs, issues or comments upstream until Eugene says so.
   Upstream is read-only fetch by URL. A shared pre-push hook refuses OceanDataTools pushes.
2. **Kalon is fully separate.** Never call, read, edit, stop or signal anything of Kalon's (`~/bin/codex-run`,
   `~/.codex`, `/private/tmp/kalon`, `~/Projects/l2audio`, `~/L2Audio-Work`, `~/KalonWork`). Kalon's running jobs are
   only counted, read-only, from the process list.
3. DeepSignal works only under `/private/tmp/deepsignal/` and uses `~/.codex-deepsignal` and `~/bin/ds-codex` only.
4. Every Codex launch names its model with `-m` (`gpt-6.2-sol`, `gpt-6.2-astra`, `gpt-6-luna`). Astra needs
   `KALON_ALLOW_ASTRA=1` set inline on that one launch only, never exported.
5. No secrets in repos, briefs, prompts or logs. Never commit the cloud environment id.
6. Never delete anything outside `/private/tmp/deepsignal/`. Mac storage floor is 5 GB free.
7. Never push fork `dev` or `master`; push only `deepsignal/*` fork branches and desk branches. Desk `main` only as
   fast-forward. Never force-push or rewrite history (Eugene only).
8. Installs on the Mac need Eugene himself (venv-sci and venv-scan were refused by the permission check).
9. Downloads of third-party files (#121 device manuals, #139 Kongsberg docs) need Eugene's own yes.
10. Critical code (core behavior, security or auth, the gate, instrument or ship writes) never auto-merges.
11. No sub-agents in Codex jobs. No em dashes in anything written.

## 3. Repos and branches

- Fork `eugenevivino/openrvdas` (code). Module branches are built on contrib master 3b4b76e.
- Desk `eugenevivino/openrvdas-desk` (rules, briefs, decisions, research). Local clone: `/private/tmp/deepsignal/desk-main`.
- **Trunk:** fork `deepsignal/integration` (1dc7a5e since the security merge; was 7c60dbf, created from 3b4b76e, D-INTEG1). Non-critical units that pass
  review merge here with one merge commit. Tag `deepsignal/pilot-candidate` = 7c60dbf (the console UI, D-PILOT1).
- **Console:** source of the pilot is `deepsignal/console-mvp` at **0fd4dee**. Caveat: the branch head is f38b52e
  because the hourly sync pushed joint security commits there (docs/INCIDENTS.md). Restoring it needs Eugene's force
  push. Until then use 0fd4dee or `deepsignal/integration`.
- **Security unit:** `deepsignal/sec-cds-joint` (critical, push-only). Head 5fb327f = slices 1 and 2 of the CDS gate
  redesign; slice 3 is building on the Mac.

## 4. The three launcher slots (D-WIP3; everything else is paused except approved desk process tooling)

1. **Console pilot candidate** (landed in integration, LANDED 1). Open items are tickets T-CON-1 to T-CON-10 in
   `docs/TICKETS.md` (late FAIL clears lastGood, learned period reset on page return, Map "Position aging" with no
   track, plus hardening and flaky tests). Needs a design note (`docs/designs/console.md`) before more is built.
2. **Security redesign**: MERGED into `deepsignal/integration` 1dc7a5e (Eugene approved 03:49Z), tag
   `deepsignal/pilot-candidate-2`. Linux nginx runtime probe PASS at 1dc7a5e. Claim released. Open: T-CON-11 (combined
   pytest run fails 12 tests from the global websockets shim in `test_ws_compat.py`), T-SEC-3 to T-SEC-6.
3. **Stream Health console view** (slot approved by Eugene on November 19). Read the current approval status in `docs/designs/stream-health-view.md`. The view consumes the published chain fields. The engine is a separate unit. The 24 h soak is held.

## Claims (2026-11-19 03:42Z)

Units carry `claimed_by` in `docs/units.json`. Nothing is claimed now (the security redesign was merged and released).
Check the live claim directories and manifest before starting work. The 24 h soak is held. Before starting
a unit, set its `claimed_by` and create `/private/tmp/deepsignal/claims/unit-<name>/owner.txt`; release both when done.

## 5. Decisions waiting on Eugene (short MORNING list)

- Merge approvals for critical items: `sec-cds-joint` (after its review passes), the console installer.
- Force push to restore `deepsignal/console-mvp` to 0fd4dee.
- Ship with tickets? fault-bench yes (recommended); QARTOD hold (2 D-P1DEF1 P1s); ship-coupling hold (5).
- D-SEC1 to D-SEC6: adopt the security architecture, login layer (Django accounts plus allauth MFA), role rename,
  vault core in the pilot, FIPS platform RHEL 9, Nov 25 supervised pilot.
- #121 and #139 downloads; venv-sci (sonar estimators); bandit and pip-audit on the Mac (scanners now run in cloud).
- Gate: `gate/linux-advisory` merge to desk main.

## 6. Standing rules (short form)

- **D-UNITS1:** whole units on `deepsignal/<module>`, one job of at most 3 slices, one review pass of at most 2 rounds.
- **D-P1DEF1:** a P1 blocks only for wrong or misleading operator data on valid input, a security or install-gate
  hole, or a crash or hang on inputs the real CDS produces. Everything else is a ticket.
- **D-PIPE1 and D-PIPE1a:** finish line with 5 stamps; old branches never block; launches never depend on a chat;
  claims per job; gate of record = the unit's Linux CI job; macOS-safe done-lines; heavy cap counts every project;
  every snag gets a guard and an incident line.
- **Heavy cap:** machine total 3 with 1 slot reserved for Kalon, so DeepSignal launches only while the total is
  under 2 (`DS_MACHINE_CAP=3`, `DS_KALON_RESERVED=1`).
- **D-WIP3:** 3 reserved slots (console, security redesign, Stream Health view); the launcher refuses others (exit 4).
- **Review routing and D-CLOUD1:** non-math reviews run in Codex cloud. **Cloud runs Sol on medium only** (a test on
  2026-11-19 showed `-c model=...` is ignored). Builds that touch data correctness run on the Mac with Sol high within
  the memory gate and our cap; everything else stays on cloud medium. The Mac runs math reviews and builds.
- **D-DESIGN1:** a one-page design note (`docs/designs/<unit>.md`) before any build; the launcher refuses builds
  without it (exit 6). **D-FIX1:** every fix needs a production-path regression plus one variation that keeps the
  same answer. **D-FASTREV1:** machine checks first, self-check receipt, parallel per-part cloud reviewers.
- **D-PIPE2 (done, tests in `tools/pipe2/tests`):** briefs carry a `needs:` front-matter block checked by preflight (exit 8); mac-build pins
  HEAD and writes per-command receipts (`--rerun-skipped`); never merge trunk into a unit branch (pre-push hook).

## 7. Tools and how to run them (all in `/private/tmp/deepsignal/`; desk copies in `tools/`)

- `ds-launch-when-ok.sh <wd> <prompt> <log> <maxwait> -- <ds-codex args>`: the one launch path. Order of checks:
  preflight (8), WIP cap (4), review routing (5), design note (6), claim (3), then waits for the lock, memory gate and
  heavy cap. Read-only reviews need `DS_REVIEW_ROUTE=math` or `exempt:<reason>`.
- `mac-build.sh <slug> <model> <effort> [--rerun-skipped]` with `MB_DIR` and `MB_BRANCH`: build from `<dir>/brief.md`,
  run its `## Acceptance` commands, push only if all pass.
- `self-check.sh <repo> <base> <design-note>`, then `fast-review.sh <unit> <branch> <base> <note> <outdir>`.
- `cloud-review.sh <branch> <prompt> <out>`: one cloud review writing only its review file.
- `heavy-jobs.sh` (read-only count), `preflight.sh <brief> <repo>`, `trunk-merge-check.sh`, `lead-push.sh`.
- Gate of record: desk Linux job (advisory, D-GATE1). nginx tests run on desk branch `ci/sec-joint-nginx`
  (edit the `ref:` sha in its workflow and push; read with `gh run list -R eugenevivino/openrvdas-desk -b ci/sec-joint-nginx`).
- Detached loops: `heartbeat.sh` (15 min, restarts `autopilot.sh`), `autopilot.sh` (accepts in-flight cloud tasks),
  `hourly-sync.sh` (pushes ahead `deepsignal/*` branches; see pitfall 1).
- Counts: `python3 tools/finish-line.py` in the desk (now LANDED 1, QUALIFIED 1, FINISHED 0).

## 8. Where things live (desk)

`docs/STATE.md` (now), `docs/DECISIONS.md` (every decision), `MORNING.md` (asks for Eugene), `docs/REFERENCE.md`
(feature list; run `python3 tools/reference-check.py` before pushing), `docs/UNITS.md` and `docs/units.json` (units,
PAUSED, superseded), `docs/TICKETS.md`, `docs/INCIDENTS.md`, `docs/designs/`, `research/` (reviews),
`docs/OPERATING-SYSTEM.md` (standing build rules), `docs/RULES-FOR-OTHER-CHATS.md`.

## 9. Known pitfalls (from the incident log)

1. The hourly sync pushes HEAD of every clone whose local branch is named `deepsignal/*`. Build on a local branch with
   the same name as the target, or detach (`git checkout --detach`).
2. zsh: `$var:r` eats refspecs (use `${var}`); no word splitting in loops (use `${=var}`). macOS bash 3.2: guard empty
   arrays. No `timeout`; use `perl -e 'alarm N; exec @ARGV'`.
3. `## Acceptance` must start its own line or 0 commands parse (mac-build now refuses).
4. Edit running scripts only by writing a new file and renaming it.
5. Chains must wait for a NEW CI run id before reading results.
6. Orphaned fixture processes cause flaky runs; the heartbeat reports them.
7. websockets 14+ breaks the 2024 CDS; the fixture shim fixes it. paho-mqtt is missing on the Mac; use the shim via `PYTHONPATH`.
8. The Mac has no nginx (by decision); nginx tests run on the Linux runner.

## 10. First 10 minutes

1. `cd /private/tmp/deepsignal/desk-main && git pull --ff-only`; read STATE, MORNING, this file.
2. `tail -20 /private/tmp/deepsignal/mac-builds.log` and `tail -2 /private/tmp/deepsignal/heartbeat.log`.
3. `/private/tmp/deepsignal/heavy-jobs.sh --list` and `memory_pressure | tail -1`; `df -g /System/Volumes/Data`.
4. `git ls-remote https://github.com/eugenevivino/openrvdas 'refs/heads/deepsignal/*'` for current heads.
5. `python3 tools/finish-line.py` for the counts.
6. Check whether `cds-final.sh` is still running (`pgrep -fl cds-final.sh`) and what it last logged.
7. Pick the next step from section 4; write a brief (needs block, design-note path, acceptance) before any build.
