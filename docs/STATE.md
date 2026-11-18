# State (rewritten each session, 60 lines max)

Updated 2026-11-18 05:35Z by the setup thread. Wind module line is from the DeepSignal thread.

## Now
- RULE: build on the fork first. No upstream PR or "ready to send" prompt until
  Eugene says the set is ready (D-ARCH6).
- Desk repo `eugenevivino/openrvdas-desk` is live (public, `main`). Rules 1 to 28,
  decisions through D-TEAM7, briefs, gate scripts and ideas 1 to 62 are in it.
- Mini set up (2026-11-18): ~/OpenRVDAS-Work, venv-3.12, deps stamp e241119e.
  Desk clone on the Mini and the first real `gate/remote.sh` run: NOT DONE.
- Team method: Claude manages, Codex builds (rule 23). Cloud is the default lane,
  always Sol medium; Astra and Sol-high work on a Mac (rule 8). Mac jobs pass `-m`
  (rule 27) and use only /private/tmp/deepsignal/ (rule 28).

## Code
- Django fix PR: fork branch `django-gui/shared-config-names` ad10eb1 (on dev 1a6f1ed).
  Django 48 OK, pytest 631 passed, flake8 clean on changed lines. Gate NOT RUN.
  PR text in `pr/` (draft only). Parked on the fork (D-ARCH6); also waiting on the
  developer's reply to Eugene's issue, then "Fixes #N". Eugene sends it.
- DeepSignal wind: fork branch `claude/project-thread-un3kq6` 558e45b, based on
  contrib master 3b4b76e. VectorWindAverageTransform, 23 tests pass, gate NOT RUN.
  DONE, parked on the fork (D-ARCH6). Draft `pr/deepsignal-vector-wind.md`, not for sending yet.
- Contrib: branches on the existing fork, PRs to openrvdas_contrib `master`,
  folder `contrib/deepsignal/` (D-ARCH3, D-ARCH4).

## In flight
- gate-linux (briefs/gate-linux.md): Codex job on the MacBook, lane mac, waiting
  for Kalon's Codex count to drop. Clone ready at /private/tmp/deepsignal/gate-linux.
- Briefs ready, not launched: #52 history and #53 fault bench (lane cloud), #56 ledger
  and #54 drift (lane mac), QARTOD flags.

## Baseline (cloud dry run of gate.sh, Python 3.13, NOT the Mini gate)
- Fork `dev` 1a6f1ed: pytest 631 passed, 59 skipped; Django 47 run, 1 error
  `TestDjangoServerAPI.test_basic` (fixed on the branch above).
- Mini baseline (3.12.13, macOS, by hand): 4 macOS-only pytest failures that pass
  on Linux (UDP ordering and timing). macOS failures never block (rule 25).

## Open asks for Eugene
- Codex cloud setup: connect the fork, create the environment (Python 3.12, deps,
  internet off after setup), send the environment id.
- Nothing goes upstream until you say the set is ready (D-ARCH6).
- Codex capacity: which way to go for DeepSignal jobs (hold stands until you answer).
- First scoreboard make, model, protocol; stale threshold.

## Next bounded task
- Linux gate built by Codex, then desk clone on the Mini and the first real gate.
