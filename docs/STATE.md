# State (rewritten each session, 60 lines max)

Updated 2026-11-20 by the build lead (MacBook lane, D-NIGHT1, D-UNITS1).

## Relay pilots (2026-11-20)

- Console57182e5: full Mac acceptance GREEN, Linux44710257259 all3 jobs PASS; individual independent review PASS.
- Streama3532f3: full Mac acceptance GREEN, Linux44712385947 PASS; source/artifact reviews PASS.
- Combined2ea3e609: both Mac design checks PASS; Linux44714303424 attempt2 all3 jobs PASS after checkout-only failure.
- Fresh standalone Astra Ultra integration review HOLD: outage navigation loses report history, delayed return distorts cadence, valid `_QC_` stream names lose QC subscription. No merge; targeted regression/repairs active.
- Candidate9935ed82 passed all gates but R2 held3 variations. Six new regressions RED then229frontend/lint/type checks PASS; two corrected-replay variants also repaired.
- Final bundle4f28b56d: both full Mac checks PASS; Linux44720535508 all3 jobs PASS,231frontend tests. R3 review terminal HOLD on four valid-input variations; no integration.
- See CODEX-HANDOVER.md for immutable evidence and review provenance. Newly qualified0, integrated0; original failures/HOLDs preserved.
- Repair80abbf83 adds eight regressions for cached-return cadence, historical QC alignment, configured QC suffixes and ordered stderr callbacks; 239frontend tests, lint/type PASS. Bundlea284c1c7 is published; both full Mac checks PASS. Linux44723265628 all3 jobs PASS; R4 terminal HOLD; all10 reported variants reproduced then repaired. Source01e83671 passes251frontend/lint/types. Bundle3db4e630 published; both full native PASS, Linux44725528266 all3 PASS; R5 terminal HOLD2variations; four regressions RED, repair85e9307e passes255frontend/lint/types. Bundle9b344665 full native/Linux active; R6 review prepared.
- Relay source247f58f: Python3.12 plan guard and stable boot identity for swap evidence; focused tests PASS. Six measured v9 handoffs median0.044s/max0.058s after Relay reservation waits; no machine-throughput gain claimed.
- Mini1GiB common policy pinned; no admitted Mini job or live shared allocator activation. Kalon remains allocator owner.
- Codex verified3% remaining; retain1% reserve. Any authorized ready successor is optional after exhaustion; no takeover.
- Existing supervisors and Kalon playback untouched. The24-hour soak remains held. Topic-branch sync only; direct desk-main push rejected.

## Handoff (2026-11-19 03:42Z)
- Eugene drives new work from the Codex GUI using docs/CODEX-HANDOVER.md; Codex takes unclaimed units.
- Security redesign MERGED into deepsignal/integration 1dc7a5e (Eugene approved 03:49Z), tag deepsignal/pilot-candidate-2;
  claim released. Nothing is claimed by the MacBook Claude session now.
- Current claims supersede this historical handoff; inspect units.json and active claim directories.
- Counts: see `python3 tools/finish-line.py` (LANDED 2 after the security merge).

## Landed (fork eugenevivino/openrvdas, branch deepsignal/integration, base contrib master 3b4b76e)
- Console UI pilot candidate: integration 7c60dbf, tag deepsignal/pilot-candidate (D-PILOT1). From
  console-mvp 0fd4dee without the installer. tsc clean, vitest 178, pytest 35, flake8 clean.
  Open UI items: docs/TICKETS.md (T-CON-1 to T-CON-10).

## Finished, not landed (all unmerged; MORNING lines on desk)
- #78 ship-coupling 4882b47 (HOLD after 3 rounds), fault-bench 58e66c8 (HOLD after 3 rounds),
  QARTOD 736ef2e (HOLD, final unit round), sec-cds-joint 82c8f3d (HOLD r2, superseded by the redesign).
- Incident: fork deepsignal/console-mvp head is f38b52e (joint commits pushed by the hourly sync);
  restoring it to 0fd4dee needs Eugene's force push (docs/INCIDENTS.md).

## Rules in force
- D-UPSTREAM0 nothing to OceanDataTools. D-UNITS1 whole units, at most 2 review rounds. D-P1DEF1 what
  blocks. D-REVIEW1 and D-INTEG1: non-critical PASS merges into deepsignal/integration. D-RECOVER1.
- Kalon is hard separate: DeepSignal uses ~/.codex-deepsignal and ~/bin/ds-codex only.
- D-RAM2 memory gate for every DeepSignal job; one heavy job at a time.

## Mac automation
- Detached: heartbeat.sh (15 min, restarts autopilot), autopilot.sh, hourly-sync.sh; session cron for
  turns (keepalive after the 18:01Z network outage, see OVERNIGHT.md).

## Held for Eugene
- #121 and #139 downloads; venv-sci install (sonar estimators); nginx not installed on the Mac (by decision).

## Sync (D-SYNC1)
- Last sync 2026-11-20T11:23:11Z: fork branches pushed ok; upstream fetched ok (core dev b61ebd6e, contrib master 3b4b76e6); desk main pushed after this line.
