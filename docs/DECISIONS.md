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
  with `module: contrib.<project>.<path>`. Project folder name: PROPOSED
  `openrvdas_overlay`, Eugene to confirm.
- Mechanics: fork checkout in a separate folder, remote `contrib` pointing at
  OceanDataTools/openrvdas_contrib, branch from `contrib/master`, push to
  `origin`, PR with base `OceanDataTools/openrvdas_contrib` `master`. Builders
  do this; Eugene sends the PR (his message naming it). Core fixes still go to
  core `dev` (D-ARCH1).
- The cloud session cannot open PRs on either upstream repo (fork only), so the
  PR step stays with Eugene or a session that has the upstream attached.

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

