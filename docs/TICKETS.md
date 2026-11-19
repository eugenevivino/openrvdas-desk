# Tickets (non-blocking follow-ups; not IDEAS)

Opened 2026-11-19 under D-PILOT1 for the console UI pilot candidate (fork `deepsignal/integration` 7c60dbf,
tag `deepsignal/pilot-candidate`). Each ticket gets a regression test that fails before its fix.

## Console UI (open items from the final review, research/2026-11-18-console-final-review.md)
- T-CON-1 lastGood after a late FAIL: a FAIL that arrives after the 21-sample window rolls over clears all
  last-good data instead of only the failed reading (`field-data.ts`).
- T-CON-2 Learned period reset on page return: switching away and back discards the learned sample period,
  resets it to one second, and marks a healthy field STALE (`cds.ts`).
- T-CON-3 Map "Position aging" with zero track points: valid latitude and longitude at different timestamps
  give no track point but the notice says aging instead of NO DATA (`MapTile.tsx`).

## Console UI hardening (triage tickets, research/2026-11-18-console-p1-triage.md rows 9 to 12)
- T-CON-4 Self-test misses a manifest 404 with `pages: []` (`pages.ts`); one-line fix makes manifest fetches required.
- T-CON-5 A mutated registered page object bypasses validation (`context.ts`); copy at registration.
- T-CON-7 Auto Night accepts latitude 99 (`autoNight.ts`); bounds check reusing the pause path.
- T-CON-8 Out-of-range longitude can stall the raster tile loop (`MapTile.tsx`, inferred); bounds check in `pairTrack`.

## Tests and tooling
- T-CON-6 Source-loss and browser tests are flaky under load (scripted runs right after a build fail 1 to 3
  tests; reruns pass). Find the timing dependence; no sleeps.
- T-CON-9 Chart test "prepares four six-hour charts under 16 ms" measures wall-clock time; move the budget
  into a controlled performance gate.
- T-CON-10 Bridge average wind and other fields: confirm units from the contract feed for every preset.

## Security (stay with the critical unit, fork `deepsignal/sec-cds-joint`)
- T-SEC-1 UDP fixture baseline is not RED at f38b52e (round 2 review ticket).
- T-SEC-2 Side-effect-free gate probe (IDEAS #200).
