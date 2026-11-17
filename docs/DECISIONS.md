# Decision log

One entry per decision. IDs `D-<AREA><n>`. Status: PROPOSED, DECIDED,
SUPERSEDED (by D-x). Never edit a DECIDED entry; add a new one that supersedes
it. Seeded 2026-11-17 from the project's design threads; entries marked
PROPOSED wait for Eugene or the named evidence.

## Team and process

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
A new `ScoreboardWriter` in its own small display logger, reading the latest
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

### D-CONSOLE1 Build an open Cruise Console over OpenRVDAS, after asking OSU (2026-11-17, PROPOSED)
CORIOLIX already uses OpenRVDAS for acquisition; its value is the layer on
top (sensor registry, event log, QC flags, binned downloads, alerts,
ship-to-shore sync), with no public license found. Plan: three phases
starting with a health board and a night-safe bridge display. Gate: talk to
OSU and David Cohn first; if CORIOLIX is going open source, contribute
instead of compete. Outreach is Eugene-only (rule 14).

## MCP server

### D-MCP1 Separate read-only-first package `openrvdas-mcp` (2026-11-17, PROPOSED)
Own pip package on the official MCP Python SDK, not in `contrib/`. Read-only
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
