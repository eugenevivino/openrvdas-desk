# Decision log

One entry per decision. IDs `D-<AREA><n>`. Status: PROPOSED, DECIDED,
SUPERSEDED (by D-x). Never edit a DECIDED entry; add a new one that supersedes
it. Seeded 2026-11-17 from the project's design threads; entries marked
PROPOSED wait for Eugene or the named evidence.

## Architecture

### D-ARCH1 Everything is an overlay on the existing core, for now (2026-11-18, DECIDED, Eugene)
New capability ships as a separate layer on top of unmodified OpenRVDAS: its
own package and repo, reading through the core's public interfaces
(CachedDataServer websocket, logger configs, the ServerAPI, recorded files)
and adding readers, transforms and writers through the normal config
`module:` path. Core changes are limited to small upstream bug fixes with a
test. Why: ships keep running stock OpenRVDAS, upgrades stay painless, and
upstream can adopt pieces later on their merits. How to apply: a brief that
needs a core change must say why the overlay cannot do it, and that change
goes upstream as its own small PR first. Working name for the package:
`openrvdas-overlay` (rename is cheap until the first release).

### D-ARCH2 Overlay lives in OceanDataTools `openrvdas_contrib` (2026-11-18, DECIDED, Eugene)
New modules go to upstream's `openrvdas_contrib` repo, not core. Supersedes
the working name `openrvdas-overlay` in D-ARCH1: the package layout, tests and
release rules follow contrib's conventions, and our gate runs contrib's tests
plus ours against a pinned OpenRVDAS core. Work happens on a fork of
`openrvdas_contrib` (to be created by Eugene), same topic-branch rules as the
core fork. First step: read contrib's layout and CONTRIBUTING and write the
brief for the skeleton. Separate packages with their own life (the MCP server)
stay separate unless contrib's maintainer prefers otherwise.

## Team and process


### D-ARCH3 Contrib work: branches on the existing fork, PRs to openrvdas_contrib `master` (2026-11-18, DECIDED)
Verified 2026-11-18 by reading `OceanDataTools/openrvdas_contrib` (shallow, read-only):
- It shares history with core (69 identical commits across refs), so GitHub
  gives Eugene one fork for both. `gh repo fork openrvdas_contrib` answers
  "eugenevivino/openrvdas already exists" for that reason. No second fork.
- Target branch is `master`, not `dev`. Its `dev` stopped at cc7b9e8 on
  2024-06-05 and is fully contained in `master`, which is 24 commits ahead
  (latest 3b4b76e, 2024-10-07). All three merged PRs (#1, #2, #4) went to
  `master`. Its CONTRIBUTING.md is a copy of core's and says nothing about contrib
  PRs, so this rests on history, not a written rule. If a maintainer says
  otherwise, they win.
- Layout rule (its `contrib/README.md`): code lives in `contrib/<project>/`
  mirroring core (`logger/`, `database/`, `utils/`, plus `test/`) and is loaded
  with `module: contrib.<project>.<path>`. Project folder name: `deepsignal`
  (decided, see D-ARCH4).
- Mechanics: fork checkout in a separate folder, remote `contrib` pointing at
  OceanDataTools/openrvdas_contrib, branch from `contrib/master`, push to
  `origin`, PR with base `OceanDataTools/openrvdas_contrib` `master`. Builders
  do this; Eugene sends the PR (his message naming it). Core fixes still go to
  core `dev` (D-ARCH1).
- The cloud session cannot open PRs on either upstream repo (fork only), so the
  PR step stays with Eugene or a session that has the upstream attached.

### D-NAME1 Contribution name DeepSignal, folder `contrib/deepsignal/` (2026-11-18, DECIDED, Eugene)
Eugene named the contribution "DeepSignal". Code lives in
`contrib/deepsignal/` in `openrvdas_contrib`, loaded with
`module: contrib.deepsignal.<path>`. Supersedes the PROPOSED folder name
`openrvdas_overlay` in D-ARCH3. Treat the name as permanent: renaming later
breaks ship configs.

### D-DSWIND1 Vector wind averaging design (2026-11-18, DECIDED, builder)
- Speed-weighted vector mean (u, v averaged), not core `polar_average`
  (unweighted unit vectors, one field). Core stays the tool for heading
  and course. No core code duplicated.
- Trailing windows ending on whole multiples of `interval`, from the data
  clock, never wall clock. Output emitted when a newer record arrives.
- Never invent a value: a sample needs speed and direction in the same
  record, finite, speed not negative; windows under `min_count` give no
  value; a calm or cancelling window gives speeds but no direction.
- Works on both contrib's old core (formats) and current core (type hints),
  because contrib `master` still carries a 2024 core tree.

### D-TEAM1 Kalon-style desk structure (2026-11-17, PROPOSED)
Use the Kalon desk's structure (shared AGENTS.md, decision log, briefs, lead
handoffs, research desk, gate with exact expected failures, Eugene-only list),
without its merge train, runners, or machine account (OPERATING-SYSTEM 14).
Why: the structure is what made Kalon recoverable across sessions; the train
and runners solve a PR volume we do not have. Decider: Eugene.

### D-TEAM2 Desk files live in a companion repo (2026-11-17, PROPOSED)
Team files go in `eugenevivino/openrvdas-desk`, not in the fork. Why: upstream
already has its own CLAUDE.md and OPERATIONS.md, and a desk branch in the fork
would leak into PR diffs or rebase fights. A companion repo keeps every
upstream PR clean with zero discipline cost. Alternative rejected: orphan
branch in the fork (works, but agents must switch branches to read the rules).
Public or private: public matches "everything open source"; private is fine
while notes mention ships or people. Decider: Eugene.

### D-TEAM3 Mini is the gate host, over SSH (2026-11-17, PROPOSED)
The Mini runs `gate/gate.sh` on an exact sha in `~/OpenRVDAS-Work/`, started
from the MacBook over SSH. No GitHub runner on the Mini. Why: same pattern as
Kalon's Mini leg, no new service, nothing listening, and Kalon keeps priority.

### D-TEAM4 Gate content (2026-11-17, PROPOSED)
Gate = full pytest suite minus `test/django_gui`, plus `manage.py test
test.django_gui` through a recording runner, plus flake8 on changed files.
Dry run of `gate/gate.sh` in the cloud (Python 3.13, test seams for host and
disk) on fork `dev` 1a6f1ed: pytest 631 passed, 59 skipped, 4630 subtests;
Django 47 run, 1 error (`TestDjangoServerAPI.test_basic`,
MultipleObjectsReturned); verdict RED on that one row, 1m44s. Same error on
`master` 3f3d0c3. To confirm on the Mini under 3.12.

## Scoreboard

### D-SCORE1 One ScoreboardWriter fed from CachedDataServer (2026-11-17, PROPOSED)
Lives in the overlay (D-ARCH1). A new `ScoreboardWriter` in its own small display logger, reading the latest
value of every field from CachedDataServer. Four parts: latest-value cache,
page and cell layout, swappable per-model formatter, transport reusing the
Serial, TCP, and UDP writers. Why: the existing FormatTransform plus
SerialWriter chain shows blanks on boards that mix instruments, and
SerialWriter has no framing, checksums, or pacing. Open: first scoreboard
make, model, and protocol manual; stale threshold in seconds. Upstream home
(core or contrib) to ask first.

## MetAcq parity

### D-METACQ1 Rebuild what MetAcq produces, not how (2026-11-17, PROPOSED)
Target the outputs of MetAcq Rev 2.15: $WICOR broadcast, daily files,
calibration step, wind averaging, SAMOS and NOAA emails. OpenRVDAS has about
60% of the plumbing. Gaps in order: vector wind averaging (359 and 1 degree
average to 0, not 180), $WICOR writer, per-sensor calibration records,
alarms, display layer. Open: close read of manual sections 10, 11, and
appendices before the $WICOR writer.

## Cruise Console (CORIOLIX-class layer)

### D-CONSOLE1 Build an open Cruise Console over OpenRVDAS (2026-11-17, PROPOSED)
CORIOLIX already uses OpenRVDAS for acquisition; its value is the layer on
top (sensor registry, event log, QC flags, binned downloads, alerts,
ship-to-shore sync), with no public license found. Plan: three phases
starting with a health board and a night-safe bridge display. Update
2026-11-18 (Eugene): the upstream developer is already well aware of
CORIOLIX, so the "talk to OSU first" gate is dropped. Outreach is still
Eugene-only (rule 14).

## MCP server

### D-MCP1 Separate read-only-first package `openrvdas-mcp` (2026-11-17, PROPOSED)
Own pip package on the official MCP Python SDK, not in `contrib/`; an overlay
consumer under D-ARCH1. Read-only
by default; config help writes only to a drafts folder; live control behind a
start flag and a human confirmation per call. Analysis runs server-side so
each call sends kilobytes over the satellite link. No core changes needed for
phase 1. High-risk tier for any write path.

## AI methods

### D-AI1 Simple statistics first, as flags (2026-11-17, PROPOSED)
From the AI methods research: QARTOD and SAMOS-style QC on the ship as flags,
never deletions; layered anomaly detectors simplest first; drift needs an
independent reference; LLMs narrate over tools, they do not analyze raw data;
foundation models are a secondary signal for now. See
`research/2026-11-17-ai-methods.md`.

### D-REAN1 Reanalysis of old cruise data as a scored, reversible loop (2026-11-18, PROPOSED)
Eugene asked for a program that analyzes and recursively improves old data.
Plan: `research/2026-11-18-reanalysis-program.md`. Each pass reads the
untouched raw archive, writes flags and proposed corrections as reversible
ledger layers, and is kept only if it beats the last accepted pass on
independent holdout references and the fault bench, with a person signing off
every value change. Stops on no gain, the reference noise floor, a spent
holdout budget, or a pass cap. Live-mode numbers only from causal replay.
21 Codex-sized modules over milestones M0 to M5. Open choices for Eugene in
section 9 of the plan.

## Process


### D-REAN2 Drift report folded in: detect freely, correct only when identifiable (2026-11-18, PROPOSED)
Eugene's Deep Research report (`research/2026-11-18-drift-detection-report.md`)
is adopted into the reanalysis plan (section 10) and the #52, #54, #56 briefs:
seven verdict states (GOOD, SUSPECT, FAULT_LIKELY, CORRECTABLE, AMBIGUOUS,
UNCORRECTABLE, POSTHOC_REVIEW), offset and gain state model with Kalman
filter and RTS smoother, changepoints on residuals, maintenance events as
forced breaks, external references as noisy observations with independence
class and gradient-inflated representativeness, an evidence dependency graph
so fitting evidence never counts as validation, GUM or Monte Carlo
uncertainty on every correction, and the C0 to C5 calibration model ladder.
Paper candidate: the independence-aware calibration evidence graph (IDEAS
#74). Report citations are leads, not verified.
### D-PA1 Adopt four ProjectArchitect ideas as desk rules (2026-11-18, DECIDED)
Eugene approved "the good parts" of Druthulu/ProjectArchitect (PA3, read-only
review of commit edcc2b0, nothing installed). Adopted as rules 19 to 22 in our
own terms: retrievers, machine-checked milestones, a cost ledger for Claude and
Codex, a plain-English recap at each phase close.
Not adopted, and why: the installer and its plugin (rule 15: nothing installed
without Eugene naming it; it edits `~/.claude/settings.json` globally and
`install.sh` can run `sudo apt-get`); its usage poller (reads
`~/.claude/.credentials.json` and sends the OAuth token to an undocumented
`api.anthropic.com/api/oauth/usage` endpoint); external coders through
OpenRouter (code and prompts leave the machine on a new key); its planner/expert
loop (we already have briefs, gate and review tiers). Revisit the statusline
only as our own small script over local logs.
See `research/2026-11-18-projectarchitect.md`.

### D-TEAM5 Claude manages, Codex builds (2026-11-18, DECIDED)
Eugene: "Codex can run in the cloud and on my Macs. I only want Claude to do
management mainly, Codex for all the work work. Use an appropriately scoped
model, can use Astra with whatever thinking we need for harder stuff."
Effect: rule 23, `docs/BUILDERS.md`, role table and `docs/CODEX.md` updated.
Claude writes briefs, plans, desk docs and routes reviews; Codex writes code,
tests and scripts. Astra at any needed effort is approved (it still goes through
`codex-run` locally). Cloud path needs one-time Eugene setup (connect the fork,
create an environment); until then local `codex-run` is the path. The Django
fix ad10eb1 was written by Claude before this rule and is the last such change.

### D-ARCH4 Overlay is built as tightly scoped independent modules (2026-11-18, DECIDED)
Eugene: build it module based, tightly scoped. Rule 24. One module per branch
(`deepsignal/<module>`), PR and brief; own tests, sample config and README
section; minimal dependencies; usable alone in a stock logger config. This fits
the contrib layout (`contrib/<project>/logger/...`) and keeps each upstream PR
small. The contrib project folder is `deepsignal`, DECIDED by Eugene 2026-11-18
("DeepSignal is fine for the folder"; supersedes the `openrvdas_overlay`
proposal in D-ARCH3). It is part of every `module:` path, so it does not change.

### D-ARCH5 Standard interfaces, Linux only (2026-11-18, DECIDED)
Eugene: modules integrate with the existing codebase, standard interfaces, and
"I doubt there will be Mac support. This is for Linux." Rule 25. Note: upstream's
install script and README do list macOS as supported; Linux-only is our target
for DeepSignal by Eugene's choice, not a claim about upstream. macOS stays a dev
convenience and its failures never block (the 4 Mini-only baseline failures are
exactly that class: UDP ordering and timing).
The Mini gate is macOS, so the authoritative gate becomes a Linux gate. Options,
cheapest first (Linux gate, PROPOSED to Eugene, see `briefs/gate-linux.md`):
1. GitHub Actions workflow in the public desk repo, input sha, checks out the
   fork, Ubuntu 22.04 runner, Python 3.12, same pytest, Django and flake8
   steps. Free for public repos, no Mini load, no Kalon contention. Preferred.
2. Linux container (Docker or Colima) on the Mini. Real, local, offline, but the
   Mini is an 8 GB M1 shared with Kalon (rule 17), so it queues behind Kalon.
3. Codex cloud environment. Fast check only: no receipt we control.

### D-UX1 User-facing must be exceptional for non-expert techs (2026-11-18, DECIDED)
Eugene: user-facing has to be exceptional and extremely usable, even by techs
who are not cyber prodigies. Rule 26 and `docs/USABILITY.md` turn that into 14
checkable lines (sample config, 5-minute enable guide, safe defaults, validated
config with plain messages, no stack traces as the main message, stale and
missing shown honestly, night-safe screens, no hidden actions, 15-minute
enable test). Every review answers it; a FAIL blocks. Applies to the scoreboard,
the console, the MCP server's replies, error messages and docs alike.

### D-TEAM6 Codex models: Sol 6.2 and Astra 6.2 (2026-11-18, DECIDED)
Eugene: new Codex models are out; use Astra 6.2 and Sol 6.2 in place of the
earlier Astra and Sol picks. Tiers and efforts in `docs/CODEX.md` section 2 are
unchanged, only the versions. Running jobs finish on their current model.
Ids verified on the MacBook: `gpt-6.2-sol`, `gpt-6.2-astra`. `~/bin/codex-run`
(Kalon's script) needs no change: no allow-list, Astra guard matches `astra`.
Mini verified 05:2x Z: Codex 0.170.0 via codex-run, lists both 6.2 ids, login
present, no upgrade needed; 6.2 already runs there. Kalon replaced `codex-run`
on both Macs at 05:19Z (maps ids to 6.2, refuses no model, narrower clean-up).

### D-TEAM7 Codex cloud is the main build lane (2026-11-18, DECIDED)
Eugene: use Codex cloud to take load off the Macs; the Macs stay as extra capacity.
Cloud by default and in parallel for Linux-safe work (rule 8, `docs/BUILDERS.md`).
Update (Eugene, same day): cloud always runs Sol medium, so cloud takes standard,
well-specified modules; Astra and Sol-high work stays on the Macs. Briefs name the
lane; `-m` applies to Mac jobs (rule 27). Unverified: cloud flags. Needs Eugene's
environment id; first job is a small smoke test on Sol medium (Luna is not
selectable in cloud).

### D-SOII1 Build four modules from the SOII proposal (2026-11-18, DECIDED)

Eugene approved building the top ideas mined from his Oct 2026 SOII/DeepSignal
proposal. Order and briefs:
1. #52 instrument history (`briefs/deepsignal-instrument-history.md`), lane cloud (Sol medium).
2. #53 fault-injection bench (`briefs/deepsignal-fault-bench.md`), lane cloud (Sol medium).
3. #56 correction ledger (`briefs/deepsignal-correction-ledger.md`), Sol 6.2 high, Astra xhigh review.
4. #54 post-cruise drift review (`briefs/deepsignal-post-cruise-drift.md`), Astra 6.2 high, after 2 and 3.
#55 ("cannot tell" verdict) goes to the QARTOD flags thread. Rules carried from
the proposal: raw data immutable; tools suggest with evidence and never
rewrite data or command ship systems; live mode never uses future data.
Not yet launched. PRs still need Eugene.

### D-ARCH6 Build on the fork first; nothing goes upstream until Eugene says the set is ready (2026-11-18, DECIDED)
Eugene: "Build on my repo first." Hard rule. All work lands on branches in
`eugenevivino/openrvdas` (core fixes and `contrib/deepsignal/` modules). No
upstream PR, issue or comment is prepared as "ready to send", and agents do not
prompt him to send one, until he says the set is ready. PR drafts may be kept in
`pr/` as drafts only. Supersedes any earlier "send when ready" wording. The
Django fix stays on its fork branch and is also on hold for the upstream
developer's reply (issue filed by Eugene). The vector wind module is done and
parked on the fork.

### D-TEAM8 DeepSignal always has one Codex slot on the MacBook (2026-11-18, DECIDED)
Eugene: "So unblock it." The one-job-only-if-Kalon-leaves-room wait left the gate job
idle for 30 minutes under 2 to 9 Kalon jobs. Now DeepSignal always gets one slot,
one job at a time, queue order: Linux gate, QARTOD flags build, then the Mac-lane
briefs. Overloaded MacBook (memory pressure or swap): use the Mini for that slot.

### D-SYNC1 Sync GitHub regularly (2026-11-18, DECIDED)
Eugene: sync GitHub regularly. Rules in `docs/CODEX.md` section 3: push finished
work promptly, fetch upstream core and contrib into the fork daily and before each
new module branch (never push upstream), rebase active branches, apply pending patches
at once.


### D-ADOPT1 Separate versioned package vs contrib code drop (2026-11-18, OPEN for Eugene)
Adoption research recommends DeepSignal ship as an independently versioned MIT package with
thin OpenRVDAS adapters, proven first by a read-only shadow pilot on one Scripps vessel.
This conflicts with D-ARCH3 (modules in `contrib/deepsignal/`, PRs to contrib `master`).
No change of course. Both can hold: keep building module-by-module on the fork, and decide
the packaging and upstream shape before Eugene says the set is ready (D-ARCH6).
Research: `research/2026-11-18-adoption-strategy.md`. Eugene decides.

### D-SEP1 DeepSignal and Kalon are fully separate, including Codex home (2026-11-18, DECIDED)
Eugene: "I want these two projects utterly separated." DeepSignal uses its own Codex home
`~/.codex-deepsignal` and its own workspace and cloud environments, via a DeepSignal-owned
wrapper `~/bin/ds-codex`. Kalon's workspace, `~/.codex` and `~/bin/codex-run` are not edited
or relied on for identity. See `docs/CODEX.md` section 5. This replaces the earlier plan to
use the l2audio-listed environments.

### D-SIG1 Signals-of-opportunity report: backlog plus two modules (2026-11-18, DECIDED)

Eugene's Deep Research report #2 added as IDEAS #78 to #103 (scores N/S/F and
tier R = R2R-reproducible or V = on-vessel telemetry), and strengthened #9,
#39, #42, #43. Report citations are leads to verify, not facts. Two modules
briefed, both cloud lane (Sol medium, formulas pinned in the brief), Astra
xhigh review on a Mac, each a live transform plus an offline runner, both
scored on the fault bench (#53, now with configurable flag suffix and plug-in
injectors):
1. #78 ship-coupling discovery engine (`briefs/deepsignal-ship-coupling.md`).
2. #79 dependency-graph fault detector (`briefs/deepsignal-dependency-graph.md`).
Order: after #53 so bench numbers are real; they may build before #53 lands
and report the bench run as pending. Nothing deletes or corrects data.

### D-SUB1 Codex sub-agents allowed only pinned and capped (2026-11-18, DECIDED in principle, mechanism UNVERIFIED)
Eugene: sub-agents are important, as long as cost does not blow up. After the #56 incident
(INCIDENTS 2026-11-18) they were switched off. Now: `ds-codex --sub-agents` (default OFF) may re-enable
them only if the sub-agent model is pinned to the parent's model or cheaper (Sol or Luna), Astra
needs the parent job's own opt-in, and depth, thread and token caps exist. A sub-agent helps the
author; it never counts as the independent review (fresh session, rule 21). If the pin cannot be
enforced in codex-cli 0.169.0, sub-agents stay off. Every job is audited afterward for
`thread_spawn` sessions and their models.

### D-LEDGER1 Correction ledger: reviewer allowlist and trusted checkpoint (2026-11-18, DECIDED by build lead under Eugene's "take the recommended option" rule)
Codex's two open questions on #56. Authorized reviewers: an allowlist file (`reviewers.yaml`:
id, display name, role) kept OUTSIDE the ledger file and owned by the cruise lead; an approve or
roll-back entry by an id not on the list is refused and shown plainly. Trusted checkpoint: a
small separate file holding the ledger's head hash and entry count, rewritten on every append;
at startup the ledger is compared to it, and a mismatch (truncation, full rehash) is a loud
REFUSED to apply, never silent. Default checkpoint path is next to the config, and the docs
recommend syncing a copy to shore with the cruise data. This detects accidents and casual edits,
not a hostile root user (said plainly in the docs). Follow-up fix round on #56 after its independent
review; no change to the pushed branch yet. Eugene can overrule.

## Target parity

### D-PARITY1 One scorecard for CORIOLIX, MetAcq and our plan (2026-11-18, PROPOSED)
`docs/TARGET-PARITY.md` scores 85 capability rows (42 CORIOLIX, 43 MetAcq)
against OpenRVDAS core and DeepSignal, generated by
`tools/target-parity/gen.py`. Goal: at least 80% of CORIOLIX rows fully
covered and every gap valued 12 or more closed. Today 6 of 42; planned work
22; with the scorecard's 21 drafts 40. Re-score after each module lands.

### D-SETUP1 "Easier to set up" is a measured number (2026-11-18, PROPOSED)
First light (clean Ubuntu 24.04 to live simulated data in the console) in 10
minutes or less and 3 or fewer human actions; first real sensor in 15 minutes
or less, 10 or fewer actions, no YAML typed; 1 server per ship. Baseline is
about 25 actions (17 installer prompts) with no maintained live display;
wall-clock to be measured by `briefs/install-clock.md`. Installer changes are
core and need Eugene's go-ahead (OPERATIONS.md traps).

### D-NIGHT1 Overnight authority while Eugene sleeps (2026-11-18, DECIDED)
Eugene: work through blockers; for a non-critical choice that would block work, consult Astra at `ultra`
(read-only, Mac, KALON_ALLOW_ASTRA=1) and do what it recommends. Every such decision is logged here with the
question, Astra's answer in one line and the file path of the full answer. Hard rules still stand: nothing upstream
(D-ARCH6), Kalon untouched, no deleting outside `/private/tmp/deepsignal/`, no secrets, nothing outward-facing,
no spending beyond the agreed lanes. Anything that truly needs Eugene goes to `docs/MORNING.md` and work continues
on everything else. A morning summary is kept in `docs/STATE.md`.

### D-CONSOLE2 Night mode: configurable, one click, red by default (2026-11-18, FINAL, answered by Eugene)
Final: configurable per screen, one-click Night button, red default at dim 0.8, console.yaml night_palette sets the station default. Core 82ec7ca already works this way. No rebuild.
Eugene answered: configurable, default red (bridge safe, preserves night vision); the station default is the one token `night_palette` in console.yaml. Low-contrast warnings in red at dim 0.8 (11)
are accepted until the onboard luminance test decides.

### D-SOAK1 Where the 24-hour soak runs (2026-11-18, DECIDED by the build lead under D-NIGHT1)
GitHub Actions jobs cap at 6 hours, so: a 5.5 h soak on Linux via the desk Actions workflow (counts toward the gate),
plus the real 24 h soak on the Mini when Kalon is idle, and on the MacBook under the memory gate if the Mini is not
available (the soak is light, under 1 GB resident). A Mac-only failure does not block the gate (rule 25). Starting by
11-22 stays the target. Kalon yields first on any conflict.

### D-111A #111 met reports narrowed to what is publicly specified (2026-11-18, DECIDED by the parity thread, logged by the build lead)
SHIPTRACK, OPSUM and PCO2 are dropped from #111 v1 (no public spec found). The SAMOS writer emits the ship text format
(one `$SAMOS:` key:value line per minute, daily file), not netCDF; the NOAA hourly report is FM-13 BBXX, automated groups only,
marked UNVERIFIED. KAOU is the Revelle call sign. See `research/2026-11-18-samos-ship-format-and-fm13.md`.

### D-VISUAL1 Gate visual quality how? (2026-11-18, Eugene: "gorgeous and functional")
Choice: checks V1 to V9 (design/console-VISUAL-GATE.md) plus a lead and Astra 6.2 visual review of the contact sheet before the MVP merge. Lint runs in cloud; screenshots, contrast, motion are lead_run on the MacBook.

### D-MCP2 MCP as DeepSignal modules over one setup engine (2026-11-18, PROPOSED, subject to D-ADOPT1)
11 high-level tools over one shared setup engine; `apply` is the only write path; read-only by default; DeepSignal modules, not a separate `openrvdas-mcp` package. Supersedes D-MCP1.

### D-121A #121 device-pack manual downloads (2026-11-18, HELD for Eugene's explicit yes; RC rule requires it)
Option (a): download only publicly hosted manufacturer manuals, listed first in a manifest with URL, size and SHA-256, into /private/tmp/deepsignal/p2-device-pack/manuals/. Codex then runs offline on them. Manuals are never committed to the repo (cite formats and page numbers only). Inbound read-only fetches, no logins, no robots-blocked sites. Reversible; Eugene can veto in the morning.

### D-UPSTREAM0 Nothing goes to OceanDataTools until Eugene approves, much later (2026-11-18, DECIDED by Eugene)
No pushes, PRs, issues or comments to any OceanDataTools repo, by anyone, for any reason. Technical guards: every DeepSignal clone has origin = eugenevivino/*; any remote whose URL contains OceanDataTools gets pushurl DISABLED; a pre-push hook refuses any OceanDataTools URL; gh CLI calls never target OceanDataTools (fetching by URL is read-only and allowed); cloud prompts carry the same rule. Supersedes any softer "issue before PR" wording until Eugene lifts it.

### D-BATCH7 Ecosystem and compression decisions (2026-11-18, logged by build lead)
#135 v1 is lossless-only: zstd via CLI, falling back to xz; offline NetCDF and Parquet deferred (ERDDAP #104 serves netCDF). #132 extends the #120 cruise-meta format, no second metadata model. #109 reads winch-data-processing outputs for SWL and RVSS logic, not re-derived (see docs/ECOSYSTEM.md).

### D-REVIEW1 Astra ultra auto-approval of non-critical changes (2026-11-18, DECIDED by Eugene)
Astra at ultra (read-only) reviews non-critical changes and PRs; when it recommends approval, merge on the fork or desk without waiting for Eugene. Fork and desk only, never OceanDataTools (D-UPSTREAM0). CRITICAL, queued in MORNING.md and never auto-merged: anything touching OpenRVDAS core behavior, writes to instruments or ship systems (#130 instrument-init), security or auth code (#115, MCP remote/security (e)(f)), the gate itself, or anything Astra flags as risky. Every auto-approval is logged here with the reviewer verdict, branch and head SHA.

### D-ONBOARD1 onboard-wizard parked after two failed acceptances (2026-11-18, logged by build lead)
Failed acceptance twice (attempt 1, fix round 1). No more cloud retries. Re-brief as a Mac Sol high job after the console MVP chain, with the failing tests attached; not on the MVP critical path.

### D-137A eez-mode decisions (2026-11-18, logged by build lead)
Unknown position applies the strictest action within 24 nm; with no last fix every logger gets its uncleared action; docs state the tradeoff. v1 has no download code; EEZ data is never committed until the Marine Regions license is verified. Treated as CRITICAL under D-REVIEW1 (changes logger behavior): no auto-merge.
### D-SHIP1 Ship systems: passive first, sonar and bridge never written (2026-11-18, PROPOSED by the ship-systems thread under D-NIGHT1 authority)
DeepSignal interfaces with sonars, motion systems, the bridge and engineering by listening only (multicast join, UDP listen, file tail, receive-only serial, Modbus read codes 1 to 4). It never changes sonar, bridge, DP, ECDIS, motion-system control, engine, power or winch settings, automatically or on approval; it recommends and the operator acts in vendor software. Instrument configuration (#152 to #155) is propose, approve, apply, verify, roll back, for science sensors and DAS serial servers on an allowlist only, on the #130 engine and the #65 approval service; AI may propose, never approve or apply. Writes to instruments stay CRITICAL under D-REVIEW1 (never auto-merged). See `docs/SHIP-SYSTEMS.md`.

### D-NOC1 Network monitoring: link health in DeepSignal, NOC tool for the network (2026-11-18, DECIDED by Eugene: "Yes to your recommendation")
DeepSignal builds per-instrument link health (#156) on what OpenRVDAS already publishes (logger status, stderr fields, cache timestamps) and adds only reachability, rate, error counts, one verdict per link, a read-only health endpoint and a NOC alert webhook. Topology, SNMP and discovery stay in an existing open-source NOC tool (Uptime Kuma, Zabbix or LibreNMS). No Intermapper clone. Probes never touch data ports.

### D-FUSE1 Use all available good data, within reason (2026-11-18, DECIDED by Eugene: "We should use all available good data within reason to improve our outcomes.")
Every DeepSignal cross-check fuses at least two independent sources, weights each by quality and age, names the odd one out, and records which sources it used. External data (Argo, climatology, ocean models) is fetched ashore or when bandwidth allows, never required for a module to work. Applied first to sound speed (#140, #147, #161) and to heading, depth, position and shot position in `docs/SHIP-SYSTEMS.md`.

### D-ONBOARD1a onboard-wizard un-parked (2026-11-18, logged by build lead)
Its second "failure" was the paho-mqtt NameError on the Mac (contrib mqtt_reader reads mqtt.* at class definition), not a real defect. Acceptance now uses a stub at /private/tmp/deepsignal/shims/paho/ (nothing installed). Ten modules re-queued for acceptance with the stub. The real Linux gate installs real dependencies, so stubbed passes are provisional until the gate runs them.

### D-POSITION1 DeepSignal is the vessel's operational truth layer (2026-11-18, Eugene approved the pain-points recommendations)
Interoperate with UHDAS, SIS and SCS, do not replace them. Freshness and staleness already in the MVP, nothing moves; console chain v0 (#162) is an MVP stretch that joins console-mvp only if green by Fri 11-21. Phase 2 order after the MVP: truth-layer core (#162, #164, #165, #163, #168, #167, #166, #169), then ecosystem (#133, #131, #134, #132), then setup assist, then parity. Seismic #158 and #159 held from merge-priority until interviews (evidence rated insufficient); #158 may finish but is not prioritized.

### D-SCORE2 Vendor-agnostic scoreboard output (2026-11-18, ACCEPTED by Eugene)
Target is outdoor deck LED scoreboards (Eugene: "not the LCI-90i, the outside LED scoreboards").
Ships differ and public sources name no deck board brands, so the writer knows no vendors (Eugene:
"let's make it agnostic since various ships probably have various methods"). Three layers: transport
(serial, rs485, tcp, udp, modbus_rtu, modbus_tcp), codec (text, alpha, modbus), profile (YAML data
per board model; ship profiles in `local/scoreboard_profiles/` shadow packaged ones). New board =
new profile, no code. Transports are written on pyserial and sockets, not by wrapping OpenRVDAS
writers, because the contrib base tree's writers differ from current core. Shared interface
`briefs/scoreboard/contract.py`. Briefs #182 to #187. Eugene gathers board models himself.


### D-AI188 #188 cloud escalation default off (2026-11-18, logged by build lead)
SUPERSEDED by D-AI188a: API model is primary and on by default (caps $2/day and $30/month, redaction, offline queue of 50); local model optional and off by default. AI is advise-only; write steps become #65 or #154 proposals and are never executed.

### D-AI188a #188 API-first provider, local as offline fallback (2026-11-18, Eugene)
Eugene: an API-based model may be better. Provider is pluggable (OpenAI-compatible); default configuration uses the ship's own API key with daily and monthly caps and redacted context packs; local model and deterministic briefing are fallbacks. No key means nothing leaves the ship. Supersedes the "local default, cloud off" line in D-AI188 for the default configuration; enabling the key and budget remains Eugene's. Advise-only. A fix round on the running cloud task follows acceptance.

### D-SEC0 CDS exposure noted for the console MVP (2026-11-18, logged by build lead)
Upstream CachedDataServer binds all interfaces on 8766 with unauthenticated publish (also via nginx /cds-ws). Console MVP install brief (briefs/console/install.md) must bind CDS to localhost and proxy read-only; full lockdown belongs to the security block #189-#198. Console stays LAN-only until then.

### D-GATE1 Gate rewrite, then stop (2026-11-18, build lead under D-NIGHT1)
r2, r3 and r4 each fixed four findings and the next review found four more (bash evidence handling). Decision: one structural rewrite (r5), verdict logic in a single pure Python function with fail-closed design and mutation tests, built by Astra high. If its ultra review is not PASS, the Linux gate ships as advisory only (raw results, no GREEN/RED) and acceptance stays on the Mac and Mini gates. The console MVP does not wait on the gate.

### D-QARTOD2 QARTOD fix round 2 judged on realistic inputs (2026-11-18, build lead, from the QARTOD thread's view)
(1) Python 3.9 is dropped as a blocker if the branch's base requires 3.11 or newer (OpenRVDAS pyproject requires-python, rule 25 targets 3.12); verify the base and any deployed contrib base first. (2) Decimal, Fraction and 10**4300 inputs cannot come from stock parsers (they emit int, float or str), so they are should-fix. (3) The blocker is the flat-line scan: 80 ms per record against a 50 ms interval; needs an O(1) or amortized check with a timed 20 Hz stream test. (4) The re-review judges against the brief's data-integrity rules and realistic input types and labels which findings stock parsers can produce. If round 2 is red only on type-(2) items: SHIP WITH FIXES, log them in IDEAS, no third round.

### D-QARTOD3 One final structural round (2026-11-18, build lead)
Fix round 2 still BLOCKs on STOCK inputs: linear flat-line (23.85 ms per record at 20 Hz alternating readings), a stock CSV row `,10` loses the record, and an OverflowError at +-1e308. Because these are specific and two Sol rounds left a linear scan, one last round by Astra high (briefs/mac/qartod-flags-fix3.md) with monotonic-deque flat-line, then an ultra re-review. If still BLOCK on stock inputs the branch stays unmerged and the call goes to Eugene in MORNING. No further rounds.

## D-ACCEPT-RAM (2026-11-18 16:20Z, build lead, DeepSignal-only deviation from the shared Kalon memory rule)
Acceptance test runs only (accept.sh: light unit tests, lint, builds) gate on: available RAM >= 4 GB including
reclaimable pages, kernel pressure level 1, swap used not growing versus a reading at least 5 minutes old, and an
absolute stop at 5.5 GB swap used. Reason: macOS keeps swap allocated while RAM is healthy (16:18Z: 12.9 GB available,
pressure 1, swap 4.7 GB), so the 3.8 GB swap ceiling stalled all acceptance for hours. Codex jobs (ds-codex) keep the
shared 3.8 GB swap ceiling unchanged. Nothing of Kalon's is changed. Eugene may veto (MORNING).

## D-RAM2 (Eugene, 2026-11-18 16:41Z): health-based memory gate for all DeepSignal jobs
Replaces the fixed 3.8 GB swap ceiling and supersedes D-ACCEPT-RAM. One gate for acceptance runs and Codex jobs
(ds-codex, desk tools/ds-codex): start only when macOS memory pressure is normal (level 1), available RAM including
reclaimable is at least 3 GB, swap has not grown more than 0.5 GB over 5 minutes, and swap used is under the 8 GB hard
stop. One heavy DeepSignal job at a time; pause new starts on warn or critical pressure; Kalon still yields first.
Nothing of Kalon's is changed.

### D-UNITS1 Ship whole modules as one unit (2026-11-18, Eugene)
Standing rule, effective now. One job per module unit (2 to 3 slices), prerequisites proven first, one review pass of at most 2 rounds on the whole diff (P1 blocks, rest become tickets), one mark, one gate, one merge. Pure R100 moves skip model review. Core logic, security and math keep full review. No new small-piece branches or tasks; in-flight pieces finish as they are; existing small pieces fold into whole units. Reporting is modules landed and modules finished. Full text in AGENTS.md and docs/OPERATING-SYSTEM.md. Applies to DeepSignal only; nothing of Kalon's is touched.

### D-INTEG1 Fork integration branch is the D-REVIEW1 merge target (2026-11-18, coordinator under D-NIGHT1)
On a PASS from the Astra ultra review, a non-critical module merges with one merge commit into the fork-only branch `deepsignal/integration`, created 2026-11-18 from contrib master 3b4b76e, the base of every module branch (first created from fork dev 1a6f1edb, recreated before any merge so no unrelated commits come in). It is fork-only. Never fork dev or master, never OceanDataTools (D-UPSTREAM0). Critical items (core behavior, security or auth, the gate, ship or instrument writes) never auto-merge. Any later upstream proposal happens only after Eugene approves (D-UPSTREAM0) and is rebased onto upstream dev as its own step.

### D-RECOVER1 Logger restart after a kill is not an MVP promise (2026-11-18, coordinator under D-NIGHT1)
The console promises that loss and recovery of a source are visible within seconds (stale banner, then clear). Restarting a killed logger is an operator action, or supervisord in production. Finding: the 2024 core in contrib master 3b4b76e (the base of every module branch and the harness fixture) builds a LoggerSupervisor whose restart loop (`LoggerSupervisor.run`) the LoggerManager CLI never starts, so a SIGKILLed logger stays dead. Current core dev (1a6f1edb) restarts dead loggers itself (`LoggerManager._run_loggers_loop` started from `start()`, with `_consider_restart`). This is already fixed upstream, so there is no upstream proposal. The harness test asserts recovery after a manager restart and `contrib/deepsignal/test/harness/SOURCE-LOSS.md` records the operator action. No overlay supervisor code.

### D-UNITS1a One extra console fix round (2026-11-18, coordinator under D-NIGHT1)
Logged one-time exception to the D-UNITS1 two-round limit, console MVP only, because the console is the MVP critical path. One more fix job (3 slices on `deepsignal/console-mvp`) for the 11 new and 3 partly open P1s from review round 2 plus a test-side same-origin `/cds-ws` relay for the browser tests, then one Astra ultra review of the whole diff. If that review still HOLDs, stop and put it in MORNING; no further rounds. Install and security parts stay critical and never auto-merge.

### D-P1DEF1 What a P1 blocks (2026-11-18, coordinator under D-NIGHT1)
A P1 blocks only if (a) it shows an operator wrong or misleading data with valid inputs in normal operation (for example kt shown as m/s, stale plus fail shown as only stale, a wrong trend), (b) it is a security hole or an install-gate hole, or (c) it crashes or hangs the shell on inputs the real CDS can actually produce. Hardening for invalid inputs (latitude 99, out-of-range longitude, empty `pages: []`, an invalid page object in the registry, flaky load tests) becomes tickets; a one-line guard is fine when trivial.

### D-UNITS1b Final targeted console round (2026-11-18, coordinator under D-NIGHT1)
Console MVP only, the last extra round. Astra ultra (read-only) triages the 12 round-3 P1s against D-P1DEF1; one targeted fix job closes the must-fix list (Bridge scroll at 1366x768 and unit labeling are must-fix) with a regression test each; the re-review covers only the fix diff plus a re-check of the must-fix list, and a new finding blocks only under D-P1DEF1. The install-gate items are security and critical: fixed where possible, never auto-merged, listed in MORNING. Non-critical parts merge into `deepsignal/integration` per D-REVIEW1 only if they separate cleanly from the critical install parts; otherwise the unit stays unmerged.

### D-PILOT1 Console UI is the pilot candidate; security unit redesigned (2026-11-19, Eugene: option A, via the coordinator)
(1) The console UI from `deepsignal/console-mvp` 0fd4dee, without the installer (`console/install/**` and its test), is merged with one merge commit into fork `deepsignal/integration` (7c60dbf) and tagged `deepsignal/pilot-candidate`. Lead acceptance on the merged tree: tsc clean, vitest 178, build ok, pytest 35, flake8 clean. Open UI items are tickets in `docs/TICKETS.md` (T-CON-1 to T-CON-10). (2) The installer and relay stay on the critical branch `deepsignal/sec-cds-joint`, which is rebuilt per `research/2026-11-19-cds-gate-redesign.md` (installer owns one nginx template, loopback-only CDS with the 8767 relay, outside black-box probe, plus probe nonce, gateway 64 KiB limit and wildcard cap) as one unit, at most 3 slices and 2 review rounds; critical, push-only, Eugene approves its merge.

### D-PIPE1 Nine pipeline rules (2026-11-19, Eugene via the coordinator)
Kalon's nine pipeline rules are DeepSignal standing rules; full text in AGENTS.md and docs/OPERATING-SYSTEM.md ("Pipeline rules"). Tooling: `tools/finish-line.py` computes LANDED, QUALIFIED and FINISHED from `docs/units.json` (stamps count only with evidence at the unit head); `docs/UNITS.md` lists SUPERSEDED-BY-UNIT branches; the Mac launcher takes claim files; brief template and cloud header carry the macOS done-line rules. First count (2026-11-19): LANDED 1, QUALIFIED 0, FINISHED 0. DeepSignal files only; nothing of Kalon's is touched.

### D-PIPE1a Machine-wide heavy-job cap counts every project (2026-11-19, Eugene via the coordinator)
Rule 8 applied literally. One total cap of 2 heavy jobs machine-wide (`DS_HEAVY_CAP`), counted read-only from the process list with the patterns in `tools/heavy-jobs/heavy-patterns.txt` (codex exec, xcodebuild, swift-build): Kalon's running jobs count, but the counter never signals, stops, opens or touches any Kalon job, folder or file. `~/bin/ds-codex` refuses with exit 12 or waits (with `--wait-ram`); the launcher waits. The D-RAM2 memory gate stays as well. Kalon still yields first, so DeepSignal only waits more. Guard: `tools/heavy-jobs/test-heavy-jobs-guard.sh` proves in a sandbox that the counter writes nothing outside `/private/tmp/deepsignal` and signals nothing (passed 2026-11-19).

### D-WIP3 Work in progress capped at 3 units on the Nov 25 path; non-math reviews in the cloud (2026-11-19, Eugene via the coordinator)
(1) WIP is capped at 3 units, all on the Nov 25 path: the console (pilot candidate and follow-ups), the security redesign (`deepsignal/sec-cds-joint`) and the 24 h soak. Everything else (sonar estimators, scoreboard, MCP, ship systems, parity, ecosystem, other cloud queues, QARTOD, ship-coupling, fault-bench) is PAUSED in `docs/UNITS.md` and `docs/units.json`: nothing new launches for them, in-flight jobs finish as they are, and the Mac launcher refuses non-path jobs while all slots are taken (exit 4). (2) Review routing: non-math reviews run in Codex cloud (`cloud-review.sh`); the Mac runs only math reviews and work (launcher exit 5 otherwise); rule text in `docs/CODEX.md`.

### PENDING EUGENE: ship QARTOD, ship-coupling and fault-bench with tickets? (2026-11-19, recommended by the build lead)
Rule applied: ship with tickets unless an open P1 meets D-P1DEF1. Classification of each unit's last-round P1s (VERIFIED from the final reviews in desk research/):
- fault-bench (58e66c8, 6 P1): none meets D-P1DEF1. It is a developer benchmark, not operator-facing; four findings skew benchmark scores on valid plug-in input (slice-relative index, untouched duplicate-timestamp row, same-name overlapping truth intervals, wrapped clock_reset) and two are invalid input (NaN fault parameters, None plug-in timestamp). Recommendation: SHIP WITH TICKETS.
- QARTOD (736ef2e, 4 P1): 2 meet D-P1DEF1(a): a timestamp-less row (which the stock parse path produces) clears flat-line history and turns a flag 4 into 1; and 20 to 21 one second apart now flags 2 instead of 4. Not meeting: a raw `T_QC` column in the input (real instruments do not produce it) and the decimal Inexact trap (caller settings). Recommendation: HOLD until those 2 are fixed in one targeted job, then ship with tickets.
- ship-coupling (4882b47, 7 P1): 5 meet D-P1DEF1(a): lags [0,1] confirm a flat field; positions within 1 m treated as one environment; `temp` vs `temp_residual` channel collision; late heading bins lost when the clock advances; negative heading rate classed as transit. Not meeting: the 1e-200 underflow and the 1e308 overflow. Recommendation: HOLD until those 5 are fixed, then ship with tickets.
All three stay PAUSED under D-WIP3 until Eugene decides and a WIP slot is free.

### D-DESIGN1 Design first (2026-11-19, Eugene via the coordinator)
Every unit gets a one-page testable design note (`docs/designs/<unit>.md`, template `docs/designs/_TEMPLATE.md`) written by Astra before Sol builds: fixed target, acceptance tests as commands, out of scope, prerequisites on trunk, who judges. Reviews judge against the note; findings outside its scope are tickets unless they meet D-P1DEF1. Enforced by the Mac launcher (build jobs for a unit with no note exit 6; reviews and design-note jobs exempt). WIP units: security-redesign points to `research/2026-11-19-cds-gate-redesign.md` and its three slice briefs; the 24 h soak gets an Astra note; the console gets one only before more is built on it.

### D-FASTREV1 Fast review pipeline (2026-11-19, Eugene via the coordinator)
One review round should take about 10 to 20 minutes. (1) Machine checks first (`tools/fast-review/pre-review.sh`): tests, tsc, flake8, oxlint and installed security scanners must be green before any model review; the review refuses a red head. (2) Reviewers judge only against the unit's design note (D-DESIGN1) and the D-P1DEF1 list; everything else is a TICKET line collected into docs/TICKETS.md. (3) The diff is split by path into logic, UI and install-security parts, reviewed in parallel by Codex cloud reviewers, each writing only `REVIEW-<part>.md`; a merge step gives one verdict. (4) Sol low does the first pass; Astra high is called on an ESCALATE flag and always for the install-security part. (5) The builder runs `self-check.sh` (same checklist) and a review without a GREEN self-check receipt is refused (exit 7). Pilot: the security redesign slices 1 and 2 (plus install) at 5fb327f, with measured round time. Security scanners bandit and pip-audit are not installed on the Mac; installing them needs Eugene, so they report SKIP until then.

### D-FIX1 Every fix needs a production-path regression plus one preserving variation (2026-11-19, Eugene via the coordinator)
From the why-reviews analysis (research/2026-11-19-why-reviews-fail.md): builders fixed what was named, but the next valid variation of the same scenario still broke. Every fix now needs a production-path regression test and one variation that must keep the same answer. In the brief template; enforced as a heuristic in `tools/fast-review/self-check.sh` (at least two new tests when code changes); mirrored in OPERATING-SYSTEM.md and RULES-FOR-OTHER-CHATS.md.

### D-SCAN1 Security scanners (2026-11-19, Eugene's standing "smart and non-blocking" rule via the coordinator)
bandit and pip-audit were to go into a DeepSignal-owned venv (`/private/tmp/deepsignal/venv-scan`). The Mac permission check refused creating it ("Undermining Oversight"), as it did for venv-sci, so it was not worked around: the scanners run inside each fast-review cloud task where the cloud allows (`SCAN:` line in each REVIEW file), and `pre-review.sh` reports SKIP on the Mac with that reason. Installing on the Mac needs Eugene himself (MORNING line).

### D-CLOUD1 Cloud runs Sol on medium only (2026-11-19, Eugene via the coordinator)
Codex cloud runs Sol on medium only: a test on 2026-11-19 (two tiny tasks, with and without `-c model="gpt-6.2-astra"`) reported "GPT-5.6 Sol" both times, so the `-c model` override is ignored and cloud "escalation" is not a stronger model. Builds that touch data correctness run on the Mac with Sol high within the memory gate and the DeepSignal cap of 2; everything else stays on cloud medium. Recorded in `docs/CODEX.md` and `docs/CODEX-HANDOVER.md`.

### D-PIPE2 Kalon's process lessons as DeepSignal rules (2026-11-19, Eugene via the coordinator)
Items 1 to 4 (design first, WIP cap 3, fast reviews, cloud for non-math) were already adopted (D-DESIGN1, D-WIP3, D-FASTREV1, D-WIP3 routing). Added: (5) preflight of a brief's `needs:` front matter before any slot or claim (`preflight.sh`, launcher exit 8); (7) narrow reruns (per-job receipts `receipts/job-<slug>.tsv`, `mac-build.sh --rerun-skipped`); (8) one launch path with claims and a pinned branch head (mac-build refuses to launch or push if the head moved), single-instance guards on the heartbeat and autopilot, race audit in `tools/pipe2/AUDIT.md`; (9) never merge trunk into a unit branch (`trunk-merge-check.sh` in the pre-push hook and `lead-push.sh`; remedy: re-cut onto the tip); (10) plain scope language for fuzz, mutant and sanitizer tests; (6) Swift not applicable. D-PIPE1a updated: machine heavy cap 3 with 1 slot reserved for Kalon, so DeepSignal launches only while the total is under 2 (`DS_MACHINE_CAP`, `DS_KALON_RESERVED`); Kalon counted read-only. Design note `docs/designs/pipe2-tooling.md` (Astra in cloud, which per D-CLOUD1 actually ran Sol). Tests `tools/pipe2/tests/` all pass. This tooling unit is counted outside the D-WIP3 cap because it is process tooling.

### November 19: Stream Health view and cloud verification dispatch

Eugene approved replacing the held soak in slot 3 with the read-only Stream Health console view. The existing stream-health engine keeps its own status. Eugene also approved the cloud verification dispatch design as desk process tooling. The security owner retains the critical merge and ticket ownership.

Eugene approved the Stream Health view design. For comparable non-critical scope or design decisions the DeepSignal lead may approve after a recorded Astra Ultra concurrence. Existing security, gate, merge and external-action ownership still applies.

### November 20: Pilot release approvals

Eugene identified himself as the final reviewer and approved landing product hardening 8f0794e and desk policy d06ad2d. Fork integration advanced to bff54ec and desk main to 460914c. The installed gate matched the approved files and passed on the integration commit with 188 individually matched findings. The original scanner report is retained.

### November 20: One focused pilot round

Eugene authorized one focused correction and re-review of the page-return last-good defect on b19dde0. Keep the pilot unmerged until the review passes. The existing T-CON-1 target and D-FIX1 apply.

### D-REVIEW1 pilot approval: Console and Stream Health view (2026-11-20)
Fresh standalone gpt-6.2-astra, ultra, read-only session
01a1f8d7-55fd-7622-b89f-7de9ad0cd9fd returned explicit PASS, CRITICAL:no, no
blocking P1, and recommended noncritical fork integration after exact Linux PASS.
Approved topic: eugenevivino/openrvdas:deepsignal/relay-combined-pilot-20261120.
Exact head b67f3072daee63d0d307a16bc1d34e24b3c75002; tree
4b19186fca8315d2fdab1de5b90fe17797dbcd72; target deepsignal/integration, last
verified base bff54ec722bd8bf2c0ee949c91528642e0140e26. Both full native design
checks PASS. Linux44732250214, workflow07f277efaf6ce84b152368fc4832d1ff6d8777ef,
all3jobs PASS on that exact source, including272frontend tests and browser pilot.
Evidence: research/2026-11-20-relay-pilots/{combined-astra-r9-pass.md,r9-native-checks.json,r9-linux-jobs.json}.
This entry records approval under the existing rule; it changes no acceptance,
scientific or security requirement. The exact governing DECISIONS bytes used by
tests/review (SHA25656435a6f0fe32e5a827c58de32db2806d7330f1f89f245335fad6a52615cdf2e)
are preserved as governing-decisions-before-pilot-integration.md in that directory.
Historical receipts are unchanged. Older HOLDs remain preserved and are superseded
only for this exact candidate by the fresh PASS. Installer/live deployment, the
24-hour soak, Stream Health engine, shared scheduling activation and supervisor
replacement are outside this approval.
