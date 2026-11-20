# State (rewritten each session, 60 lines max)

Updated 2026-11-20 by the build lead (MacBook lane, D-NIGHT1, D-UNITS1).

## Relay pilots (2026-11-20)

- Latest combined candidateb67f3072 is published on the authorized pilot topic; source73d97e74.
- All272frontend tests, lint/types PASS. Both full native gates are active; exact Linux workflow07f277e dispatched.
- Prior R8 review HOLD1: corrected QC lost observation provenance. Two real regressions RED, then fixed. R9 review prepared only; requires full native PASS and fresh quota before launch.
- All prior HOLDs/raw failures remain in research/2026-11-20-relay-pilots and immutable Relay states. No HOLD treated as PASS.
- Console and Stream view remain claimed by this Relay chat. Newly qualified0/integrated0. Finish-line registry: LANDED2, QUALIFIED0, FINISHED0 of74.
- Relay source247f58f requires Python3.12 and stable boot UUID. Measured queued independent worker handoff0.061654s; no machine/module throughput gain claimed yet.
- Mini1GiB policy pinned; allocator still Kalon's. No admitted DeepSignal Mini job or shared scheduling activation.
- Codex last verified3%; reserve1%. Provider-neutral successor optional after exhaustion; no takeover or Claude setup underway.
- Existing supervisors/protected playback untouched;24-hour soak held. Topic sync only; direct desk-main push was rejected.
- Current ownership, exact receipts and next actions: CODEX-HANDOVER.md.

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
