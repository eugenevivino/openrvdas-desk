# State (rewritten each session, 60 lines max)

Updated 2026-11-17 by the setup thread.

## Now
- Desk tree drafted; not yet in a repo. Waiting on Eugene to create
  `eugenevivino/openrvdas-desk`.
- Mini not set up for OpenRVDAS. Nothing has been run or changed there.

## Code
- Fork `eugenevivino/openrvdas` default branch `master` at 3f3d0c3
  (v2.7.2). No team branches yet.

## Baseline (cloud dry run of gate.sh, Python 3.13, NOT the Mini gate)
- Fork `dev` 1a6f1ed: pytest 631 passed, 59 skipped (4630 subtests);
  Django 47 run, 1 error `TestDjangoServerAPI.test_basic`
  (MultipleObjectsReturned), reproducible, order independent. Verdict RED
  on that row only. Same error on `master` 3f3d0c3.
- Gate locking test: 20 tests OK.
- Gate on the Mini: NOT RUN.

## Designs ready (all PROPOSED, see DECISIONS)
- D-SCORE1 scoreboard writer, D-METACQ1 MetAcq gap map, D-CONSOLE1 Cruise
  Console, D-MCP1 MCP server, D-AI1 AI methods.

## Open asks for Eugene
- Create the desk repo (public or private).
- Yes for the Mini setup in mini/SETUP.md.
- First scoreboard make, model, protocol; stale threshold.
- OK to contact upstream and OSU (drafts first).

## Next bounded task
- Mini setup, then `gate/remote.sh` on fork `dev` head.
