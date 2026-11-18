# Operating system for the OpenRVDAS desk

The architecture of the team: machines, roles, how work flows, the gate,
approvals, and how to rebuild all of it from zero. Adapted from the Kalon desk
(`l2audio` `docs/process/OPERATING-SYSTEM.md` and `RULES-V2.md`, read
2026-11-17), keeping its structure and rules and leaving out its product,
business, licensing, and audio content.

This file records how things are meant to work. It is not proof that a machine,
job, or branch is live now. Verify live state before acting.

## 1. Machines

| Machine | Role | Limits |
|---|---|---|
| MacBook (`Eugenes-MacBook-Pro`) | Eugene's workstation. Local Claude Code and Codex sessions, fork checkout `~/openrvdas`, Homebrew Python 3.12 venv. Starts gate runs on the Mini over SSH (`gate/remote.sh`). | Kalon work has priority on this machine. No OpenRVDAS long runs while a Kalon full gate is running. |
| Mac Mini (`EugeneMacMini`, ssh alias `kalon-mini`, reached over Tailscale) | Gate host. Runs `gate/gate.sh` against an exact sha in its own clone `~/OpenRVDAS-Work/openrvdas`. Also the right place for long soak tests (listener runs against recorded NBP1406 data). | M1, 8 GB, shared with Kalon. One OpenRVDAS gate at a time (lock). Refuses to start below 10 GB free disk or when a Kalon gate holds the Mini. Never a public service. Nothing installed or changed without Eugene's message naming it. |
| Cloud threads (Claude projects, Linux containers) | Planning, research, design docs, portable Python work, fast checks. | No serial ports, no shipboard UDP, no MQTT broker. A cloud green is a fast check, never the gate. |
| GitHub hosted Actions | Only upstream's own workflows (`release-tags`, `shell-checks`, `update-docs`). | Actions spend stays $0. We add no hosted workflows to the fork. |

Identify a Mac by `scutil --get LocalHostName`, never by `hostname`, which
changes with the network (Kalon incident 2026-11-09).

## 2. Team roles

One person, several agents. Each role is a kind of session, not a person.

| Role | Who fills it | Owns | Never |
|---|---|---|---|
| Owner | Eugene | Goals, priorities, every rule-10 approval, final say on upstream contact | |
| Lead (coordinator) | The project chat session | Priorities, turning asks into briefs, assigning threads, reading results, keeping `docs/STATE.md` true | Writes production code itself on a large unit; merges without a gate receipt |
| Builder | A thread or Codex job per brief (Codex on the Macs launches through Kalon's `~/bin/codex-run`, Sol low by default, one bounded task per job) | One unit: code plus its locking test on one fork branch | Touches files outside the brief; reviews its own work |
| Reviewer | A fresh session, stronger model than the builder for medium and high risk | Reads diff plus gate receipt, checks the brief's acceptance list, trust boundaries, and data-integrity rules | Edits the code it reviews |
| Decision desk | A fresh high-reasoning session per question | Architecture and design rulings, answers to blockers, logged as `D-` entries | Implements its own ruling |
| Research desk | A thread per question | Dated findings in `research/`, verified separate from inferred, sources listed | Makes product decisions |
| Ops | A thread when needed | The gate scripts, Mini setup, expected-failures bookkeeping (rows still need Eugene) | Changes the Mini without Eugene's message |
| Upstream liaison | The lead, drafting only | Draft issues, PR descriptions, and emails to OceanDataTools, OSU, NOAA | Posts anything; Eugene sends |

A relayed message, copied approval, or thread summary is not Eugene's word.
Only his own message is.

## 3. How work flows

```
Eugene ask
   |
Lead: clarify outcome, write brief (briefs/<area>-<slug>.md)
   |
Builder: fork branch <area>/<slug>, failing test first, then code
   |
Fast check (cloud or MacBook): changed tests + flake8
   |
Gate on the Mini, exact head sha  --red-->  back to builder (max 2 fix rounds, then decision desk)
   | green receipt
Reviewer (fresh session, risk tier)  --changes-->  builder
   | approve
Eugene: opens or approves upstream PR to dev   (or keeps it on the fork)
   |
Lead: WORKLOG line, STATE rewrite, DECISIONS entry if a decision changed
```

Blockers: stuck on design, root cause, or architecture means ask the decision
desk through the lead, do what it rules, keep moving. No answer in 30 minutes:
the lead decides under the same limits and logs it.

## 4. Repos and branches

- Code: fork `eugenevivino/openrvdas`. Its `dev` and `master` mirror upstream
  and are only fast-forwarded from upstream. All work is on topic branches
  `<area>/<slug>` cut from the fork's `dev`. Areas: `scoreboard`, `metacq`,
  `console`, `mcp`, `qc`, `fix`, `docs`, `infra`.
- Upstream PRs target `OceanDataTools/openrvdas` `dev`. One topic per PR. New
  modules: ask upstream first whether they belong in `openrvdas_contrib`
  (CONTRIBUTING.md). Separate packages (for example `openrvdas-mcp`) get their
  own repo.
- Desk: this repo, `main` only, small direct commits by the lead. Briefs and
  handoffs are files here, never in the fork.
- Never force-push. Never push to fork `dev` or `master` except an upstream
  fast-forward sync.

## 5. The gate

`gate/gate.sh <sha>` on the Mini. It is the only thing that says green.

1. Refuses (exit 2, no rows, never read as red or green) when: wrong machine,
   another OpenRVDAS gate holds the lock, a Kalon gate holds the Mini, free disk
   is under 10 GB, or the sha is not in the clone after fetch.
2. Checks out the exact sha in a clean worktree, copies the `.dist` settings,
   reuses the shared venv (reinstalls only when `pyproject.toml` changed).
3. Runs `pytest test/ --ignore=test/django_gui`, then
   `python manage.py test test.django_gui`, then flake8 on Python files changed
   versus `origin/dev`.
4. Writes `receipts/<sha>/results.tsv` rows `row<TAB>PASS|FAIL|SKIP`, then
   `__END__<TAB>PASS` as its last act, plus `full.log` and `receipt.json`
   (sha, utc, host, python, counts, sha256 of results).
5. Verdict: GREEN only with `__END__` and no FAIL row outside
   `gate/expected-failures.txt` (exact name match). Anything else is RED or
   REFUSED.

Expected failures need Eugene's message to add or remove a row, and each row
names the issue that will retire it. The baseline row at setup is
`test.django_gui.test_django_server_api.TestDjangoServerAPI.test_basic`
(fails on fork `master` 3f3d0c3 and `dev` 1a6f1ed under Python 3.13 in the
cloud; confirm on the Mini under 3.12 before listing it).

Skips are reported, not hidden. Database tests skip when MySQL or InfluxDB is
absent (OPERATIONS.md section 6), so every receipt prints its skip count and
the reviewer asks which tests skipped.

Locking test for the gate itself: `python3 -I gate/tests/test_gate.py`.

## 6. Review by risk

| Tier | What | Review |
|---|---|---|
| Low | Docs, tests only, desk files, an isolated new module with no callers yet | One review by a stronger model than the author |
| Medium | A new or changed reader, transform, or writer; display code; config schema | One review by a strong model, plus the gate |
| High | Listener core, LoggerManager, server API, CachedDataServer, `install_openrvdas.sh`, anything that changes data values, timestamps, or QC flags, any live-control path (MCP write tools, logger start/stop) | Design review before code, one deep code review, gate, and a replay check against recorded data (NBP1406) showing unchanged output except where intended |

Every review checks the brief's trust boundaries: serial and network input is
untrusted; configs are code; anything an AI agent can call is least-privilege
and read-only by default.

## 7. Records

- `docs/DECISIONS.md`: one entry per decision. ID `D-<AREA><n>` (for example
  `D-SCORE1`), date, decision, why, who decided, status (PROPOSED, DECIDED,
  SUPERSEDED by D-x). Never edit a decided entry; supersede it.
- `docs/WORKLOG.md`: one line per finished item: date, what, branch or PR,
  PASS, FAIL, or PARKED.
- `docs/INCIDENTS.md`: same day for every break, stall, or rule change:
  cause, fix, guard. A repeat without a new guard is itself an incident.
- `docs/STATE.md`: rewritten at the end of every working session, 60 lines max.
- Research: `research/YYYY-MM-DD-<topic>.md`, one question each.

## 8. Handoffs

A session that stops before its work is done writes
`handoffs/LEAD_BRIEF_<YYYY-MM-DD>-<slug>.md` from the template: goal, exact
state (branch, sha, gate result), what was tried, the next bounded task, open
questions, and what not to redo. The next session starts from that file and
`docs/STATE.md`, not from chat history.

## 9. Cost and models

- Cheapest model with a good chance: small models for mechanical edits and
  reading; a mid model for normal code; the strongest model for high-risk
  review, decision-desk rulings, and hard root causes.
- One unit per job, fresh session, under about 40 turns. Long sessions cost
  more because every step rereads the context (Kalon measured about 99.7% of
  tokens as input).
- Campaigns (sweeps, soak tests, replays) are scripts with a summary file. A
  model reads the summary, never loops over raw logs.
- No polling sessions. Wait on events or a scheduled check.

## 10. Eugene-only decisions

By his own message naming it: money; installs, launchd, reboots on any Mac;
anything public or outside (upstream issues, PRs, comments; emails to OSU,
NOAA, OceanDataTools, vendors); force-push or history rewrite; changes to
`docs/RULES.md`; expected-failure rows; deletes outside a job's own scratch;
tokens, keys, and accounts.

Everything else (branches, commits on topic branches, briefs, reviews, desk
docs, gate runs, research) proceeds on the lead's or desk's say-so and is
logged. No gate is relaxed either way.

## 11. Sharing the Mini with Kalon

Kalon owns the Mini first. OpenRVDAS stays in `~/OpenRVDAS-Work/` and never
reads, writes, or locks anything under `~/L2Audio-Work`, `~/KalonWork`, or
`~/Projects/l2audio`. The gate refuses while a Kalon gate is active (it checks
for Kalon's live worker locks `~/KalonWork/lock-w0` to `lock-w2` and a running
`mini-gate-suite.sh`), runs under `nice -n 10`, and is light (about two
minutes of Python on the cloud baseline). If Kalon's disk floor is at risk the
gate refuses first.

## 12. Bootstrap from zero

Someone with only GitHub and these two repos can rebuild the setup.

1. Eugene creates `eugenevivino/openrvdas-desk` and pushes this tree.
2. MacBook: clone the fork to `~/openrvdas`, Homebrew Python 3.12 venv,
   `pip install -e ".[dev]" flake8`. Clone the desk to `~/openrvdas-desk`.
3. Mini: follow `mini/SETUP.md` (Eugene's yes covers the clone, venv, and
   package install it lists).
4. Verify: `python3 -I gate/tests/test_gate.py` passes on the Mini; one
   `bash gate/remote.sh <current dev sha>` from the MacBook returns a receipt
   with an `__END__` row.
5. Record the receipt sha256 in `docs/WORKLOG.md` and the baseline counts in
   `docs/STATE.md`.

Not in git: SSH keys, Tailscale login, GitHub tokens, venvs.

## 13. Process change rule

Any change to machines, gate, roles, or approvals updates this file in the same
commit, naming the new behavior, owner, entry point, limits, approval boundary,
and how it was verified.

## 14. What we did not copy from Kalon, and when to add it

Kalon's pipeline grew to fit a closed-source app with two-host Swift gates and
hundreds of open PRs. OpenRVDAS is Python, light to test, and lands upstream
through a human maintainer. Copying all of it would cost more than it saves.

| Kalon piece | Here | Add it when |
|---|---|---|
| Merge train (batched, bisecting, fast-forward trunk) | Not used. Upstream's maintainer merges. | We run our own trunk with more than about 5 PRs waiting at once |
| Self-hosted GitHub runners, `agent-worker` and `agent-review` workflows | Not used. Gate over SSH, review by a fresh session. | Units arrive faster than a lead can hand them out by hand |
| Machine account and approver token | Not needed with no runners | Same time as runners |
| Spawn guard, slot scheduler, heartbeat, stall alarms | Gate lock and disk floor only | Two or more concurrent long jobs on the Mini |
| Two-host gate (MacBook plus Mini) | Mini only | A change is platform sensitive (install script, serial on macOS vs Linux): add a Linux VM leg first, since ships run Linux |

Kept from Kalon: shared AGENTS.md contract with a thin CLAUDE.md shim, decision
log with IDs, lead briefs and handoffs, research desk, locking-test rule, exact
expected-failure names, `__END__` row and REFUSED verdict, machine identity by
LocalHostName, Eugene-only list, cost rules, incident log with guards, and this
operating guide as the single source of process truth.
