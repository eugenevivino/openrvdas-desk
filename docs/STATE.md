# State (rewritten each session, 60 lines max)

Updated 2026-11-20 by the build lead (MacBook lane, D-NIGHT1, D-UNITS1).

## Supervised pilot console (2026-11-20)

- Eugene approved product hardening 8f0794e and policy d06ad2d. Fork integration is bff54ec and desk policy 460914c is installed. The installed gate returned GREEN with all 188 raw findings matched to the approved sites. [Owner decision](https://github.com/eugenevivino/openrvdas-desk/issues/2#issuecomment-7032462805).
- Fork [pilot PR #3](https://github.com/eugenevivino/openrvdas/pull/3) was re-cut from bff54ec. Commit 50f3d46 resolved the conflicting README assertions. Commit b19dde0 kept the last good reading visible through multiple delayed revocations under continuous subscription. T-CON-11 and the three original pilot corrections are included.
- On b19dde0, the installed self-check and all nine design commands passed. The Mac passed 192 frontend tests plus 84 additional installer and server tests outside the design suite. Ubuntu passed 192 frontend tests, 207 console cases, 204 installer/security cases, and two real nginx cases. All ten modules passed in Chromium. [Three-job Linux run](https://github.com/eugenevivino/openrvdas-desk/actions/runs/44692067756).
- Astra Ultra held the second round at b19dde0. On page return the browser can retain an older usable depth sample that the shorter server backfill omits. If two later samples are revoked, the Number tile can omit that last good reading. Cloud logic passed. Cloud UI also held for multiple delayed failures under zero history. Both remaining cases were identified by inspection. See T-CON-14. The candidate remains a draft. The soak remains held.

## Throughput and Stream Health (2026-11-19)

- Hosted verification candidate `95e9edf` passed six desk checks. A real Mac fixture held its slot from 11:22:42 to 11:23:42 a.m. Eastern. Hosted tests started at 11:23:18 on console `fc31b54` and passed. Owner review precedes installation. [Desk PR](https://github.com/eugenevivino/openrvdas-desk/pull/4) and [Linux run](https://github.com/eugenevivino/openrvdas-desk/actions/runs/44565419757).
- Stream Health fork [PR #2](https://github.com/eugenevivino/openrvdas/pull/2), `9f156fa`, passed 186 frontend tests and a two-stream Chromium test on both macOS and Ubuntu. All design and P1 checklist items passed. The previous Bandit hold was resolved on integration bff54ec after this test. A re-cut and fresh checks are pending. T-CON-12 records a stock CDS startup delivery gap. Vessel producer integration is pending. [Linux receipt](https://github.com/eugenevivino/openrvdas-desk/actions/runs/44571508115).

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
- Last sync 2026-11-20T07:22:48Z: fork branches pushed ok; upstream fetched ok (core dev b61ebd6e, contrib master 3b4b76e6); desk main pushed after this line.
