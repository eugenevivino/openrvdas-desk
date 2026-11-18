# State (rewritten each session, 60 lines max)

Updated 2026-11-18 by the DeepSignal wind thread (Code section only).

## Now
- Desk tree drafted; not yet in a repo. Waiting on Eugene to create
  `eugenevivino/openrvdas-desk`.
- Mini set up 2026-11-18 (Eugene's yes): ~/OpenRVDAS-Work with fork clone,
  venv-3.12 (Python 3.12.13), deps stamp e241119e. Desk clone waits on the
  desk repo. 102 GB free after; folder is 200 MB.

## Code
- Fork `eugenevivino/openrvdas` default branch `master` at 3f3d0c3
  (v2.7.2).
- DeepSignal (D-NAME1): fork branch `claude/project-thread-un3kq6` at
  558e45b, based on openrvdas_contrib `master` 3b4b76e. Adds
  `contrib/deepsignal/` with VectorWindAverageTransform. 23 tests pass on
  contrib master and on core master, flake8 clean. Gate NOT RUN (gate.sh
  does not run contrib tests yet, IDEAS #49). PR draft in
  `pr/deepsignal-vector-wind.md`; Eugene sends it.

## Baseline (cloud dry run of gate.sh, Python 3.13, NOT the Mini gate)
- Fork `dev` 1a6f1ed: pytest 631 passed, 59 skipped (4630 subtests);
  Django 47 run, 1 error `TestDjangoServerAPI.test_basic`
  (MultipleObjectsReturned), reproducible, order independent. Verdict RED
  on that row only. Same error on `master` 3f3d0c3.
- Gate locking test: 21 tests OK.
- Mini baseline (Python 3.12.13, macOS, dev 1a6f1ed, by hand, not gate.sh):
  pytest 4 failed, 627 passed, 59 skipped in 115 s; Django 47 run, 1 error
  (same test_basic). The 4 pass on Linux: test_udp_reader test_broadcast,
  test_udp_writer test_binary and test_unicast_with_eol (packets read out of
  order), test_simulate_data test_use_timestamps (0.310 vs 0.26 timing).
- Gate on the Mini: NOT RUN (needs the desk clone).

## Designs ready (all PROPOSED, see DECISIONS)
- D-SCORE1 scoreboard writer, D-METACQ1 MetAcq gap map, D-CONSOLE1 Cruise
  Console, D-MCP1 MCP server, D-AI1 AI methods.

## Open asks for Eugene
- Create the desk repo (public or private).
- Yes for the Mini setup in mini/SETUP.md.
- First scoreboard make, model, protocol; stale threshold.
- OK to contact upstream (drafts first).

## Next bounded task
- Mini setup, then `gate/remote.sh` on fork `dev` head.
