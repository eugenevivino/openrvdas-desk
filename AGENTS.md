# OpenRVDAS desk: shared agent contract

Read this first. It is shared by Claude Code, Codex, and any other agent.
Project knowledge lives in this repo as Markdown, never only in a provider's
private memory. `CLAUDE.md` imports this file and adds nothing.

## Startup (every session)

1. Read `docs/STATE.md`, `docs/RULES.md`, and the `docs/DECISIONS.md` entries
   your task touches. Read `docs/OPERATING-SYSTEM.md` the first time and
   whenever your task touches process, machines, or the gate.
2. Inspect the real checkout: branch, head sha, dirty files, remotes. A plan in
   a doc is not evidence of what the code does now.
3. If you were handed a brief, read it fully and work only inside its scope.

## The two repos

| Repo | Role | Upstream PRs |
|---|---|---|
| `eugenevivino/openrvdas` (fork of `OceanDataTools/openrvdas`) | Code | Yes, from topic branches, target `dev` |
| `eugenevivino/openrvdas-desk` (this repo) | Team, decisions, briefs, gate | Never |

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

## Codex

Codex jobs follow `docs/CODEX.md`: launch through `~/bin/codex-run`, right-size
the model, one bounded task per fresh session, tight briefs, one job at a time
on the Mini and none during a Kalon gate.

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

## Ending a session

Add any new idea as a row in `docs/IDEAS.md`. Rewrite `docs/STATE.md` (keep it under 60 lines), add one line to
`docs/WORKLOG.md` per finished item, add a `docs/DECISIONS.md` entry when a
decision changed, and if the work continues, write a handoff from
`handoffs/LEAD_BRIEF_TEMPLATE.md`. Record branch, sha, gate result
(PASS, FAIL, NOT RUN), and the next bounded task.
