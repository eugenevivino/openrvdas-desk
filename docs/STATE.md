# State (rewritten each session, 60 lines max)

Updated 2026-11-20 by the build lead (MacBook lane, D-NIGHT1, D-UNITS1).

## Relay pilots (2026-11-20)

- Console and Stream Health view FINISHED as fixture pilots at b67f3072 on fork deepsignal/integration. Normal fast-forward verified remotely; no upstream/default-branch change.
- All 272 frontend tests, lint/types, both unchanged full native design checks and Linux 44732250214 all 3 jobs PASS at that exact candidate.
- Fresh standalone Astra Ultra R9 PASS, CRITICAL:no, no blocking P1; D-REVIEW1 approval logged. Original HOLDs/raw failures remain preserved.
- Both unit claims released after verified completion. Finish-line manifest updated with exact five stamps; compute counts with tools/finish-line.py.
- Relay source 247f58f requires Python 3.12/stable boot UUID. Queued independent worker handoff measured 0.061654 s. Two pilots newly finished; no machine-utilization percentage claimed.
- Relay remains PILOT/STAGED: typed gate import/policy version handling, forced-termination retirement and authoritative shared leases/ownership transfer still need qualification before production dispatch.
- Mini 1 GiB policy pinned; Kalon owns allocator. No admitted DeepSignal Mini job or shared scheduling activation. Protected playback and existing supervisors untouched.
- Codex last verified 2%; preserve 1%. Successor provider optional after exhaustion; no takeover or Claude setup underway.
- Live deployment/installer activation, Stream Health engine and 24-hour soak are not included. Existing scientific/security/approval holds remain.
- Current receipts and next actions: CODEX-HANDOVER.md. Desk topic sync only; direct desk-main push was rejected.

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
- Last sync 2026-11-20T14:23:27Z: fork branches pushed ok; upstream fetched ok (core dev b61ebd6e, contrib master 3b4b76e6); desk main pushed after this line.
