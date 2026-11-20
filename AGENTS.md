# OpenRVDAS desk: shared agent contract

Read this first. It is shared by Claude Code, Codex, and any other agent.
Project knowledge lives in this repo as Markdown, never only in a provider's
private memory. `CLAUDE.md` imports this file and adds nothing.

## Startup (every session)

1. Read `docs/STATE.md`, `docs/RULES.md`, and the `docs/DECISIONS.md` entries
   your task touches. Read `docs/OPERATING-SYSTEM.md` the first time and
   whenever your task touches process, machines, or the gate. For every pipeline
   continuation, read its **Deterministic orchestration** section and the dated
   Relay checkpoint in `docs/CODEX-HANDOVER.md` before acting on queued work. Mini
   admission uses the documented authorized floor only after common-policy verification.
2. Inspect the real checkout: branch, head sha, dirty files, remotes. A plan in
   a doc is not evidence of what the code does now.
3. If you were handed a brief, read it fully and work only inside its scope.

## The two repos

| Repo | Role | Upstream PRs |
|---|---|---|
| `eugenevivino/openrvdas` (fork of `OceanDataTools/openrvdas`) | Code | Yes, from topic branches, target `dev` |
| `eugenevivino/openrvdas-desk` (this repo) | Team, decisions, briefs, gate | Never |

Contrib work (D-ARCH3) uses the same fork on its own branches; those PRs target
`OceanDataTools/openrvdas_contrib` `master`, not core `dev`.

Never commit desk files (this repo's content, briefs, handoffs, agent notes)
into the fork. Upstream already has its own `CLAUDE.md` and `OPERATIONS.md`;
follow them when editing fork code, and do not edit them unless the change is
meant for upstream.

## Build and test (fork checkout)

Python 3.11 or newer; the team standard is Homebrew Python 3.12.

- Fast check: `pytest <changed test files>` plus `flake8 <changed .py files>`.
- Gate (authoritative): `bash gate/gate.sh <sha>` on the Mini, or
  `bash gate/remote.sh <sha>` from the MacBook. It runs the full pytest suite,
  the Django suite and flake8 on changed files, and writes one TSV row per
  test plus an `__END__` row. Missing `__END__` means the gate did not run;
  it is never read as green.
- Django tests need `python manage.py test test.django_gui`; plain pytest
  cannot create their database. Settings come from the `.dist` templates.

## Who builds

Claude manages (briefs, plans, routing, desk docs). Codex does all hands-on work,
local or cloud, right-sized model, Astra approved for hard work. A Claude session
writes no production code, tests or gate code. Read `docs/BUILDERS.md`.

## Codex

Codex jobs follow `docs/CODEX.md` and D-SEP1: use `~/bin/ds-codex` with
`~/.codex-deepsignal`, an explicit right-sized model and a bounded brief.
Admission follows the current approved machine guards and existing job ownership.

## How work flows

1. Lead turns an ask into a brief (`briefs/TEMPLATE.md`): goal, failing test
   first, acceptance commands, files in scope, stop rule.
2. Builder works on a fork branch named `<area>/<short-slug>`, one unit per
   branch, small diff.
3. Gate runs on the exact head sha. Red rows block unless listed by exact name
   in `gate/expected-failures.txt`.
4. Reviewer (a fresh session, never the author) reviews the diff and the gate
   receipt. Higher risk gets a stronger model (rule 6).
5. Eugene opens or approves the upstream PR to `dev`. Agents never post on
   upstream GitHub without his message naming it.

## Non-negotiables

- A bug is not fixed until a test locks it. Name the test after the issue.
- Never relax, skip, delete, or quarantine a test to get green.
- Never force-push, rewrite history, or push to `master` or `dev` on the fork.
- Shipboard data is safety data. A writer, transform, or display never invents
  a value: stale shows as stale, missing shows as missing, QC flags travel with
  values and never delete them.
- No secrets in code, logs, briefs, or docs. Keys stay on Eugene's machines.
- Separate observed, proven, failed, pending, and proposed. A historical PASS
  is not a current PASS.
- Respect upstream: small, focused PRs to `dev`, tests and flake8 clean, ask
  before building large new modules (they may belong in `openrvdas_contrib`).

## Eugene-only (his own message naming it)

Money; installs, launchd, reboots on any Mac; anything posted publicly or sent
outside (upstream issues, PRs, comments, emails to OSU, NOAA, or vendors);
force-push or history rewrite; changing `docs/RULES.md`; adding or removing an
expected-failure row; deleting anything outside a job's own scratch.
Everything else: the decision desk decides and logs it in `docs/DECISIONS.md`.

## Writing

Answer first, recommendation marked, short. No em dashes. Plain words, define
jargon once. Verified separate from inferred.

## Reference doc (Eugene 2026-11-18)

`docs/REFERENCE.md` is the canonical DeepSignal feature list. Any commit that changes a feature's
status (briefed, launched, built, reviewed, done, dropped, new idea) updates its row there in the same
commit; a new IDEAS row is added with `python3 tools/reference-check.py --backlog`. Run
`python3 tools/reference-check.py` before pushing; the `reference-check` workflow fails a push that
leaves an IDEAS number or brief out.

## Ending a session

Add any new idea as a row in `docs/IDEAS.md`, and update `docs/REFERENCE.md` for every status change. Rewrite `docs/STATE.md` (keep it under 60 lines), add one line to
`docs/WORKLOG.md` per finished item, add a `docs/DECISIONS.md` entry when a
decision changed, and if the work continues, write a handoff from
`handoffs/LEAD_BRIEF_TEMPLATE.md`. Record branch, sha, gate result
(PASS, FAIL, NOT RUN), and the next bounded task.

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

## Launch hygiene (D-PIPE2, Eugene 2026-11-19)

Each brief declares its needs (network, tools, disk, RAM, required files) in a front-matter block, and the launcher checks them in about two minutes before taking any slot or claim. A build is pinned to the branch head it started from and refuses to run or push if that head moves. Each job writes a receipt of its acceptance results, and a rerun can repeat only the failed or skipped commands. Unit jobs launch only through the one launcher, and the background loops run one copy each. Never merge main, dev or integration into a unit branch; re-cut the unit onto the trunk tip instead (a pre-push hook refuses it). Fuzz, mutant and sanitizer tests stay on our own code, local only, no network, no exploitation. Swift is not applicable. The machine heavy-job cap is 3 with one slot reserved for Kalon, so DeepSignal launches only while the total is under 2. Details and tests: `tools/pipe2/`, design note `docs/designs/pipe2-tooling.md`.
