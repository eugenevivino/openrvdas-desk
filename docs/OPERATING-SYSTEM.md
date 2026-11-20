# Operating system for the OpenRVDAS desk

The architecture of the team: machines, roles, how work flows, the gate,
approvals, and how to rebuild all of it from zero. Adapted from the Kalon desk
(`l2audio` `docs/process/OPERATING-SYSTEM.md` and `RULES-V2.md`, read
2026-11-17), keeping its structure and rules and leaving out its product,
business, licensing, and audio content.

This file records how things are meant to work. It is not proof that a machine,
job, or branch is live now. Verify live state before acting.

## Deterministic orchestration (2026-11-20 standing directive)

Routine handoffs through interactive AI sessions incurred avoidable dispatch waits
and repeated queue-reading calls. Relay, or the existing approved deterministic
controller until transfer, owns scheduling, dependency checks, worker allocation,
receipt collection and authorized transitions. AI owns implementation, debugging,
architecture, scientific analysis and required independent reviews. This directive
changes routine coordination, not acceptance criteria or approval boundaries.

The lifecycle is **pieces → assembled modules → tests → required reviews →
qualification → integration**. Advance an eligible step automatically within the
existing authorization. On failure, preserve evidence and the exact blocker while
independent eligible work continues. Existing pauses and ownership still apply;
standing authorization need not be requested again. The controller persists work
continuity; chat memory is neither the queue nor evidence of a live worker.

The implementation is `tools/relay/` in the isolated desk checkout identified in
[CODEX-HANDOVER.md](CODEX-HANDOVER.md). Its `DEEPSIGNAL.md` documents the executable
interface. Read the existing state report before resuming its immutable plan;
preserve active workers and reconcile claims instead of starting another pilot.

- Pin Git source and integration base, dependencies, policy, controller/adapter
  code and evidence identity. Seal the candidate after any distribution build;
  bind acceptance and review to that exact derived commit. Source additions,
  dependency changes and changed governing inputs invalidate affected reuse.
- Durable state, atomic controller/plan locks, fenced attempts and owner claims
  prevent duplicate dispatch. Restart reconciles existing attempts and receipts.
  Ambiguous liveness retains its reservation; time alone cannot clear a claim.
  Forced-termination recovery of the local directory/PID guard remains unqualified.
- Admit parallel jobs only on eligible MacBook, Mini or authorized cloud capacity,
  with measured RAM/disk/pressure and existing aggregate heavy-job guards. Resource
  waits and bounded infrastructure retries are separate from engineering HOLDs.
  Resource refusal does not authorize bypassing a guard or stopping foreign work.
  Eugene authorized a Mini-only lightweight admission floor of 1 GiB
  (1,073,741,824 bytes). Each job still needs its measured peak plus safe headroom,
  acceptable pressure/swap growth, an available budget and valid reservations.
  The Kalon lead remains sole allocator owner; actual Mini dispatch waits for its
  verified common policy. This floor is authorized, not deployed by DeepSignal.
- Batch reviewed modules only at the same exact candidate and run their union of
  checks. Different candidates require explicit current-base assembly and combined
  qualification. Re-cut unit changes onto current integration; never merge trunk
  into a unit. Relay currently implements no product merge or release action.
- Keep Kalon and DeepSignal queues, state databases, locks, evidence and project
  ownership separate. The Kalon lead, chat `01a1f223-16f2-73a0-a292-a688aab4af8f`,
  owns the sole shared MacBook/Mini capacity authority. DeepSignal's capacity
  adapter is a status-only shadow client; mutation remains disabled. No shared
  authority production service/state/listener has been installed by this pilot.

Existing design acceptance, self-check, security, Linux gate, independent review,
scientific/reference and release requirements remain mandatory. Reference records
must be readable and hashed as well as scientifically judged. Gate import fails
closed: no production PASS parser is qualified. A review-request outbox is not a
completed or dispatched review; labels and handwritten PASS cannot qualify work.
Preserve fixture isolation, private test HOME/TMPDIR and protected player/ship
boundaries. Critical merges, installs, upstream contact and deployment retain their
existing explicit approvals. Documentation adds no acceptance gate.

Status vocabulary applies to each capability, never to the whole system by proxy:

| Status | Evidence and current limit |
|---|---|
| IMPLEMENTED | Code exists; Relay scheduling, receipts, identity and recovery paths are present. |
| TESTED | Named checks passed for named source; core 71 and adapter 52 test receipts are recorded in the handover. This does not qualify product modules. |
| PILOT | Isolated Console and Stream workflows have exercised the controller; v6 prelaunch was cancelled before native execution. Existing supervisor ownership remains. |
| STAGED | Committed implementation and capacity client await qualification and deliberate owner transfer; production authority is absent. |
| PRODUCTION | Requires verified transfer and operational qualification. Relay has not reached this status. |

Before transfer, finish exact-candidate product gates/reviews, native gate import
and dispatch qualification, a real compatible integration batch, adapter restart
and reuse, Linux coverage, host cleanup and shared-lease/fencing evidence. Existing
supervisors retain authority until the owners deliberately transfer it.

Measure newly qualified and integrated modules, plus resource wait separately from
avoidable scheduling delay. The initial test-only pilot measured six handoffs with
internal capacity available: median 0.0504 s, maximum 0.1000 s. Raw maximum 12.93 s
included reservation wait. This proves neither whole-host utilization nor product
throughput gains; newly qualified 0, integrated 0 in that observation. Evidence:
`/private/tmp/deepsignal/relay-20261120/evidence/measured-latency.json`.

Historical reconciliation: `RULES.md` says newest wins. This directive assigns
routine coordination to software while keeping AI engineering/review duties. Older
machine/role tables below and Codex launcher examples are historical where D-SEP1,
D-PIPE1/2 and the current handover supersede them: use DeepSignal's separate launcher
and installed admission guards; the required unit Linux gate remains authoritative.
Protected RULES, DECISIONS, design notes and manifest are unchanged by this update.
An unresolved protected-policy conflict remains a blocker for its affected action;
it never authorizes silently weakening a gate or taking over a supervisor.

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
| Lead (coordinator) | The project chat session | Priorities, turning asks into briefs, assigning threads, reading results, keeping `docs/STATE.md` true | Writes production code, tests or gate code itself (rule 23); merges without a gate receipt |
| Builder | A Codex job per brief, local through `~/bin/codex-run` or in Codex cloud (`docs/BUILDERS.md`, rule 23). Claude does not write code | One unit: code plus its locking test on one fork branch | Touches files outside the brief; reviews its own work |
| Reviewer | A fresh session, stronger model than the builder for medium and high risk | Reads diff plus gate receipt, checks the brief's acceptance list, trust boundaries, and data-integrity rules | Edits the code it reviews |
| Decision desk | A fresh high-reasoning session per question | Architecture and design rulings, answers to blockers, logged as `D-` entries | Implements its own ruling |
| Research desk | A thread per question | Dated findings in `research/`, verified separate from inferred, sources listed | Makes product decisions |
| Ops | A thread when needed | The gate scripts, Mini setup, expected-failures bookkeeping (rows still need Eugene) | Changes the Mini without Eugene's message |
| Upstream liaison | The lead, drafting only | Draft issues, PR descriptions, and emails to OceanDataTools, OSU, NOAA | Posts anything; Eugene sends |

A relayed message, copied approval, or thread summary is not Eugene's word.
Only his own message is.

## Standing build rules (adopted 2026-11-18/19)

These rules govern every DeepSignal build from now on. Full texts and dates are in `docs/DECISIONS.md`; feature status is in [docs/REFERENCE.md](REFERENCE.md); counts come from `python3 tools/finish-line.py` (manifest `docs/units.json`).

1. **D-UNITS1, whole units.** Each module ships as one unit on its own branch: one build job of at most three slices, one review pass of at most two rounds on the whole diff, one approval mark, one gate, one merge. No new small-piece branches or tasks; pieces already in flight finish as they are and are folded into their unit.

2. **D-PIPE1, nine pipeline rules (adopted from Kalon's pipeline).** (1) Whole units only. (2) A finish line of five stamps per unit, each proven at the unit's current head: moved (on the integration branch), tested (unit and acceptance tests green), fixed (review passed with no open P1), in the app (served by the console or installed in the test fixture), tested in the app (a browser or black-box test passes against it). (3) Old small branches never block a unit; they are listed as superseded and retired after the unit lands. (4) Check a unit's prerequisites on the integration branch before starting it. (5) Launches never depend on a live chat session: one detached launcher runs approved jobs and takes a claim per job so two loops never launch the same job. (6) The gate of record is the unit's Linux CI job; local scripts are pre-checks. (7) Brief done-lines must work on macOS. (8) Shared machine: the heavy-job cap counts every project's jobs, and we never touch another project's jobs or folders. (9) Every snag gets a permanent guard and an incident line. **D-PIPE1a:** the cap is two heavy jobs machine-wide, and Kalon's running jobs count toward it; they are read from the process list only, never signalled or touched. Kalon still yields first, so DeepSignal only waits more.

3. **D-P1DEF1, what blocks.** A P1 blocks only if it shows an operator wrong or misleading data from valid inputs in normal operation, is a security or install-gate hole, or crashes or hangs on inputs the real data server can produce. Hardening for invalid inputs becomes a ticket. **D-UNITS1a and D-UNITS1b** were one-time exceptions that gave the console MVP two extra rounds past the two-round limit; there are no further exceptions.

4. **D-WIP3, three units in progress.** At most three units are in progress, all on the Nov 25 path: the console (pilot candidate and follow-ups), the security redesign, and the 24 h soak. Everything else is paused: nothing new launches for it, in-flight jobs finish, and the launcher refuses other units while all three slots are taken.

5. **Review routing.** Non-math reviews run in Codex cloud, read-only (the reviewer writes only its review file). The Mac runs only math reviews and build work.

6. **D-DESIGN1, design first.** Before Sol builds a unit, Astra writes a one-page testable design note: a fixed target, acceptance tests as commands, an out-of-scope list, prerequisites, and who judges. Sol builds against it and reviewers judge against it; a finding outside its scope is a ticket unless it meets D-P1DEF1. The launcher refuses a build for a unit with no design note; reviews and design-note jobs are exempt.

7. **Progress counts.** Progress is reported as three numbers computed by script from the unit manifest, never from PR or branch counts: LANDED (moved), QUALIFIED (tested and fixed) and FINISHED (all five stamps).

8. **D-FASTREV1, fast review (target 10 to 20 minutes per round).** Machine checks run first and must be green before any model review: tests, type checks, linters and the security scanners that are installed. The builder runs the same review checklist on its own work and gets a self-check receipt; a review request without one is refused. Reviewers judge only against the unit's design note (its acceptance tests and fixed target) plus the D-P1DEF1 list; everything else becomes a ticket. The diff is split by path into parts (logic, UI, install or security) and one cloud reviewer per part runs in parallel; a cheap first pass (Sol low) handles each part, and Astra is called only when the first pass escalates or for security or math code. A small merge step turns the part reviews into one verdict and the ticket list.

9. **D-FIX1, fixes that hold.** Every fix needs a production-path regression test plus one variation that must keep the same answer (for example a late QC flag delivered before and after history eviction gives the same result). The builder's self-check enforces a minimum of two new tests whenever code changes, and reviewers judge fixes against both.

10. **D-PIPE2, launch hygiene.** Each brief declares its needs (network, tools, disk, RAM, required files) in a front-matter block, and the launcher checks them in about two minutes before taking any slot or claim. A build is pinned to the branch head it started from and refuses to run or push if that head moves. Each job writes a receipt of its acceptance results, and a rerun can repeat only the failed or skipped commands. Unit jobs launch only through the one launcher, and the background loops run one copy each. Never merge main, dev or integration into a unit branch; re-cut the unit onto the trunk tip instead (a pre-push hook refuses it). Fuzz, mutant and sanitizer tests stay on our own code, local only, no network, no exploitation. Swift is not applicable. The machine heavy-job cap is 3 with one slot reserved for Kalon, so DeepSignal launches only while the total is under 2.

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

Every review, at any tier, also answers the usability checklist in
`docs/USABILITY.md` for anything a tech sees or edits (rule 26).

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

Full Codex rules, ported from Kalon with sources: `docs/CODEX.md`. Summary:

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

## Ship whole modules, never small pieces (Eugene 2026-11-18, standing rule)

Each module ships as ONE unit:

- One job per unit (2 to 3 slices at most), fixed in place on the unit branch `deepsignal/<module>`.
- Prove prerequisites exist before the unit starts (inputs merged, fixtures, env, briefs).
- One review pass on the whole diff, at most 2 rounds. A P1 blocks; everything else becomes a ticket.
- One approval mark on the final head, one gate, one merge.
- Pure file moves (`git diff -M100%` shows only R100) skip model review. Core logic, security and math changes keep full review.
- Do not cut or launch small-piece branches or tasks. Pieces already in flight finish as they are. Fold existing small pieces (for example console fix rounds) into their whole module unit.
- Report progress as modules landed and modules finished, not pieces.

Why: every small piece paid the full toll (queue, review, mark, gate, merge) and collided with others in shared files.

## Pipeline rules (D-PIPE1, Eugene 2026-11-19, adopted from Kalon's pipeline)

1. Whole units only (D-UNITS1).
2. Finish line, five stamps per unit, each with evidence at the unit head: moved (on fork `deepsignal/integration`), tested (unit and acceptance green at the unit head), fixed (review PASS, no open P1 under D-P1DEF1), in the app (served by the console or installed in the fixture on the Mac), tested in the app (a browser or black-box test passes against that app). Report LANDED (moved), QUALIFIED (tested plus fixed) and FINISHED (all five) every time, computed by `python3 tools/finish-line.py` from `docs/units.json`, never from PR or branch counts.
3. Old small PRs and branches never block a unit. List them as SUPERSEDED-BY-UNIT in `docs/UNITS.md`; fold one in only if the unit needs the fix; retire them after the unit lands.
4. Check a unit's prerequisites on trunk (fork `deepsignal/integration`) before starting it.
5. Launches never depend on a live chat session. One detached auto-launcher runs only approved jobs, and every launch takes a claim file (`/private/tmp/deepsignal/claims/<key>`, atomic mkdir, released on exit), so two loops never launch the same job. This extends the ds-codex lock, it does not replace it.
6. The gate of record for a unit is its Linux CI job on the desk (advisory per D-GATE1 until Eugene makes it a required check). Local scripts such as accept.sh are pre-checks, not the gate.
7. Brief done-lines work on macOS: `git status --short -uall`, never `grep -P`, pipe `wc -l` through `tr -d ' '`, Swift only if a unit has Swift.
8. Shared machine: the heavy-job cap counts every project's jobs (D-PIPE1a: one machine-wide total, default 2, counted read-only from the process list by `tools/heavy-jobs/heavy-jobs.sh`; ds-codex and the launcher wait at the cap). Never touch another project's jobs or folders.
9. Every snag gets a permanent guard plus a line in `docs/INCIDENTS.md`.

## Design first (D-DESIGN1, Eugene 2026-11-19)

Before Sol builds any unit, Astra writes a one-page testable design note at `docs/designs/<unit>.md` from `docs/designs/_TEMPLATE.md`: fixed target, acceptance tests as commands, out-of-scope list, prerequisites on trunk, who judges. Sol builds against the note and reviewers judge against it: a finding outside the note's scope is a ticket unless it meets D-P1DEF1 (a), (b) or (c). The Mac launcher refuses a build job for a unit whose note is missing (exit 6); reviews and design-note jobs are exempt.
