# State (rewritten each session, 60 lines max)

Updated 2026-11-20 by the build lead (MacBook lane, D-NIGHT1, D-UNITS1).

## Relay pilots (2026-11-20)

- Console candidate5b892601: full Mac self-check GREEN, 205 frontend tests. Linux44708749952 pilot and hardening PASS; frontend204 PASS/1FAIL (Self-test socket readiness fixture). Correction in progress, no gate weakened.
- Independent Console cloud review task_e_6b000f5c4134832fbe92c376a32815ec PASS at5b892601; final Astra Ultra approval remains.
- Stream candidate75a71c1: full Mac self-check and Linux44709129369 PASS; fresh independent review task_e_6b000f9fd45c832fa1e37fecce36b4e7 HOLD (expired observation hidden). Repair in progress.
- Relay v7 terminal:6 stages PASS,2 review gates BLOCKED; active unit claims retained by this Relay chat. Newly qualified0, integrated0. See CODEX-HANDOVER.md for exact source and evidence.
- Relay source/tests synced on desk deepsignal/relay-pilot-20261120; fork candidates on deepsignal/relay-console-20261120 and deepsignal/relay-stream-health-20261120. Default-branch push rejected; use separate branch.
- Mini1GiB common policy pinned; no DeepSignal Mini job or live shared-allocator activation. Await owner verified policy/leases and local admission.
- Codex last observed7% remaining; preserve1% reserve. Successor provider optional, handoff ready; Claude auth not a dependency of current work.
- Kalon playback and existing supervisors untouched. The 24-hour soak remains held.

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
- Last sync 2026-11-20T09:22:59Z: fork branches pushed ok; upstream fetched ok (core dev b61ebd6e, contrib master 3b4b76e6); desk main pushed after this line.
