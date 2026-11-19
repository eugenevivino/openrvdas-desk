# DeepSignal handover for Codex (2026-11-19, from the MacBook build lead)

Self-contained. Read this first, then `docs/STATE.md`, `docs/DECISIONS.md` and `MORNING.md`. Plain words; no secrets here.

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
- **Trunk:** fork `deepsignal/integration` (7c60dbf, created from 3b4b76e, D-INTEG1). Non-critical units that pass
  review merge here with one merge commit. Tag `deepsignal/pilot-candidate` = 7c60dbf (the console UI, D-PILOT1).
- **Console:** source of the pilot is `deepsignal/console-mvp` at **0fd4dee**. Caveat: the branch head is f38b52e
  because the hourly sync pushed joint security commits there (docs/INCIDENTS.md). Restoring it needs Eugene's force
  push. Until then use 0fd4dee or `deepsignal/integration`.
- **Security unit:** `deepsignal/sec-cds-joint` (critical, push-only). Head 5fb327f = slices 1 and 2 of the CDS gate
  redesign; slice 3 is building on the Mac.

## 4. The three units in progress (D-WIP3; everything else is PAUSED)

1. **Console pilot candidate** (landed in integration, LANDED 1). Open items are tickets T-CON-1 to T-CON-10 in
   `docs/TICKETS.md` (late FAIL clears lastGood, learned period reset on page return, Map "Position aging" with no
   track, plus hardening and flaky tests). Needs a design note (`docs/designs/console.md`) before more is built.
2. **Security redesign** (`sec-cds-joint`, design note `docs/designs/security-redesign.md`, spec
   `research/2026-11-19-cds-gate-redesign.md`). State: slice 1 cdc9f71, slice 2 5fb327f pushed; slice 3 (outside
   black-box probe) building. Fast review pilot at 5fb327f: HOLD on one P1 (gateway upstream `max_size=None`), queued as
   `briefs/mac/cds-redesign-fix1.md`. The chain `/private/tmp/deepsignal/cds-final.sh` runs: slice 3, fix1, self-check,
   fast review of the whole unit (base 0fd4dee) and the Linux nginx run. Next by hand if the chain stops:
   `MB_DIR=/private/tmp/deepsignal/cds-redesign-fix1 MB_BRANCH=deepsignal/sec-cds-joint /private/tmp/deepsignal/mac-build.sh cds-redesign-fix1 gpt-6.2-sol high`
3. **24 h soak** of the pilot candidate. Design note `docs/designs/soak.md` (DRAFT; criteria from D-SOAK1 and the soak
   brief). Not started. D-RECOVER1: a killed logger is restarted by an operator or supervisord, not by our code.

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
- **D-WIP3:** 3 units in progress (console, security redesign, soak); the launcher refuses others (exit 4).
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
- Counts: `python3 tools/finish-line.py` in the desk (now LANDED 1, QUALIFIED 0, FINISHED 0).

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
