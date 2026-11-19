# State (rewritten each session, 60 lines max)

Updated 2026-11-19 02:05Z by the build lead (MacBook lane, D-NIGHT1, D-UNITS1).

## Supervised pilot console (2026-11-19 05:36Z)

- Fork topic `deepsignal/console-supervised-pilot` at `8652862` includes test-only T-CON-11 (`7b5f98e`) and the T-CON-1 through T-CON-3 fixes. Integration is at `1dc7a5e`.
- All nine design commands passed. Mac recorded 188 frontend tests and 150 Python tests. Linux recorded 150 passes and two additional fresh-start source-loss/recovery passes. All ten shipped modules passed Chromium checks on each OS. [Linux run](https://github.com/eugenevivino/openrvdas-desk/actions/runs/44465499779)
- Held before independent review. Bandit reports the same 188 low and two medium findings on integration and the candidate. The self-check also flags existing em dashes in rebuilt assets and replay pacing in the fixture. See `receipts/pre-review-8652862.txt` and `receipts/self-check-8652862.txt` under the desk job root.
- Security-scope decision pending. Console claim released for the handoff. The 24-hour soak is on hold.

## Handoff (2026-11-19 03:42Z)
- Eugene drives new work from the Codex GUI using docs/CODEX-HANDOVER.md; Codex takes unclaimed units.
- Security redesign MERGED into deepsignal/integration 1dc7a5e (Eugene approved 03:49Z), tag deepsignal/pilot-candidate-2;
  claim released. Nothing is claimed by the MacBook Claude session now.
- Everything else is unclaimed (units.json claimed_by), including the 24 h soak and the console follow-ups.
- Counts: see `python3 tools/finish-line.py` (LANDED 2 after the security merge).

## Landed (fork eugenevivino/openrvdas, branch deepsignal/integration, base contrib master 3b4b76e)
- Console UI pilot candidate: integration 7c60dbf, tag deepsignal/pilot-candidate (D-PILOT1). From
  console-mvp 0fd4dee without the installer. tsc clean, vitest 178, pytest 35, flake8 clean.
  Open UI items: docs/TICKETS.md (T-CON-1 to T-CON-10).

## Running
- Security unit deepsignal/sec-cds-joint (CRITICAL, push-only, Eugene approves the merge): rebuild per
  research/2026-11-19-cds-gate-redesign.md, Sol high on the Mac, nginx probe on the Linux runner
  (desk branch ci/sec-joint-nginx), Astra ultra review, at most 2 rounds.

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
- Last sync 2026-11-19T04:46:16Z: fork branches pushed ok; upstream fetched ok (core dev 8e3b07e0, contrib master 3b4b76e6); desk main pushed after this line.
