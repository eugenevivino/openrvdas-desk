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

## Process

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

