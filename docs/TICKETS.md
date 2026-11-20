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

All three fixes are on fork topic `deepsignal/console-supervised-pilot` at `fc31b54`, pending integration.
Both regression cases per ticket failed on the integration baseline and passed on the candidate.
The Mac passed all nine commands in `docs/designs/console.md`. Release blockers are recorded in `docs/STATE.md`.

## Console UI hardening (triage tickets, research/2026-11-18-console-p1-triage.md rows 9 to 12)
- T-CON-4 Self-test misses a manifest 404 with `pages: []` (`pages.ts`); one-line fix makes manifest fetches required.
- T-CON-5 A mutated registered page object bypasses validation (`context.ts`); copy at registration.
- T-CON-7 Auto Night accepts latitude 99 (`autoNight.ts`); bounds check reusing the pause path.
- T-CON-8 Out-of-range longitude can stall the raster tile loop (`MapTile.tsx`, inferred); bounds check in `pairTrack`.

## Console data delivery

- T-CON-12 During startup, stock CDS can omit a root update published between the first history response and the fallback subscription for an empty background field. With an initial sample 400 seconds old, the protocol trace delivered the initial root and then two empty batches. Publishing the same update after fallback acknowledgement delivered it. An initial sample 45 seconds old also delivered the early update. The Stream Health view shows missing evidence in the first case. Verify delivery across the subscription change before relying on a single root transition. Evidence is in the Stream Health job under `tmp/stream-health-cds-timing.log`.

## Tests and tooling
- T-CON-6 Source-loss and browser tests are flaky under load (scripted runs right after a build fail 1 to 3
  tests; reruns pass). Find the timing dependence; no sleeps.
- T-CON-9 Chart test "prepares four six-hour charts under 16 ms" measures wall-clock time; move the budget
  into a controlled performance gate.
- T-CON-10 Bridge average wind and other fields: confirm units from the contract feed for every preset.

## Security (stay with the critical unit, fork `deepsignal/sec-cds-joint`)
- T-SEC-1 UDP fixture baseline is not RED at f38b52e (round 2 review ticket).
- T-SEC-2 Side-effect-free gate probe (IDEAS #200).

## Security (from the CDS gate redesign fast review at 814353a, 2026-11-19)
- T-SEC-3 [sec-cds-joint logic] contrib/deepsignal/docs/security-cds.md:43 says each run publishes a nonce, but the documented `--site-only` run below it performs only a byte comparison and does not publish.
- T-SEC-4 [sec-cds-joint install-security] contrib/deepsignal/security/cds_gateway.py:99 accumulates every prior subscription when enforcing MAX_FIELDS even though the CDS replaces a subscription, so a valid client that rotates through more than 200 distinct fields is disconnected.
- T-SEC-5 [sec-cds-joint install-security] contrib/deepsignal/security/cds_gateway.py:90 forwards structurally invalid but allowed CDS requests such as a subscribe field with a null specification, letting an unauthenticated LAN client trigger an exception in the upstream CDS connection instead of receiving a refusal.
- T-SEC-6 [sec-cds-joint install-security] contrib/deepsignal/console/install/install_site.py:96 busy-spins without a sleep while waiting up to five seconds for a worker generation, unnecessarily consuming a CPU during every nginx reload.
- T-CON-11 Test isolation: `contrib/deepsignal/test/harness/test_ws_compat.py` calls `ws_compat.apply()` in-process with no undo, so a combined pytest run of `contrib/deepsignal/test` (harness plus security) fails 12 tests (1 harness, 11 gateway) at integration 1dc7a5e; each suite passes alone. Fix: undo the patch at teardown (or run the shim test in a subprocess). Blocks the "tested" stamp of the integration head.
  Fixed on fork topic `deepsignal/console-t-con-11` at `7b5f98e`, pending integration. The shim tests restore both server exports; the loopback test double now supplies the stock host. Desk receipt `receipts/job-console-t-con-11.tsv`: 133 passed for the full test directory, 217 passed and 2 Linux-only cases deselected in the expanded run. Both test files passed flake8.

## Nov 20 pilot qualification

- T-CON-13. The operator README linked to the correct guide, but its console test forbade even naming the trusted installer and the unchanged installer test required it. The console-only correction on the pilot re-cut is 50f3d46. It keeps the HTTP and HTTPS examples in the guide, preserves both visible guide links and rejects copied commands and unsupported arguments.
- Desk review tooling. The shell expands Markdown command examples when composing the cloud review prompt in fast-review.sh. The installed machine gate retained its own raw and policy receipts. Quote those prompt examples and verify that composing a prompt cannot invoke host tools. The pilot reviewers received the scanner instructions in their appended design notes.
- T-CON-14. Independent UI review of 50f3d46 noted that the bounded history of evicted usable readings can exhaust both fallback entries when multiple delayed FAIL flags arrive. The reviewer classified this as an inferred follow-up. Check three previously usable evicted readings with delayed failures on the two newest; report what the operator sees.
  Astra Ultra held 50f3d46 for this case with a valid depth stream. The Number tile should retain the oldest still-good value after the two newer readings are revoked. It falls under the existing T-CON-1 acceptance target.
  Fixed under continuous subscription at b19dde0. On page return the browser may have retained a value older than the server backfill. The rebuilt candidate list can omit this still valid value after two newer delayed FAIL flags. Astra Ultra held the merge for this case on November 20.
