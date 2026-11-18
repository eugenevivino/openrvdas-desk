# Brief: qartod-flags fix round 3 (final), Astra high on the Mac

- Branch `deepsignal/qartod-flags` at c243788. Review answer: `/private/tmp/deepsignal/qartod-fix2-review/answer.md`. Lane: Mac, `-m gpt-6.2-astra` high, scratch `/private/tmp/deepsignal/qartod-flags/`, fresh session, 40 turns. No sub-agents, no commit or push (the lead does).
- Why Astra not Sol: (1) is an algorithm change; two Sol rounds left a linear scan.

## Fix exactly these (each with a failing test first, then green)
1. Flat-line check must be O(1) amortized per record for ANY input pattern. Use a sliding-window max and min with monotonic deques (or an equivalent amortized structure) and compare (max - min) against the tolerance; keep exact arithmetic where the existing code does. Timed test: an alternating two-value pattern within tolerance (the reviewer's 0.01 alternation, tolerance 1) at 20 Hz for at least 5000 records must stay under 5 ms median per record and show no growth with window length (test window 100 and 10000, medians within 2x).
2. A stock CSV row `,10` gives timestamp None: the flat-line cache must not call Fraction(None); records with no timestamp must pass through unflagged-by-time without being dropped or crashing, with a documented flag (NOT_EVALUATED) and a test using the stock CSV reader row.
3. A window-1 spike from -1e308 to 1e308 raises OverflowError while formatting: compute differences safely (Fraction or Decimal, no float overflow), format reasons without overflow, test it.
4. Should-fix: circular companion references A->B->C->A must be detected at config load with a clear error (test); reason strings keep adequate precision (test); the conflicting-climatology test must use a config that is valid except for the conflict (replace `months: []`).
5. Non-stock (10**4300 window) must at least not crash the record loop: catch, flag NOT_EVALUATED, log once.

## Constraints and acceptance
All 13 original regressions and the fix-1 and fix-2 tests keep passing (python 3.12); no deleted or loosened tests; flake8 clean; stdlib only. Run the full QARTOD test module and report counts. Report under 40 lines, RED then GREEN, verified versus inferred.

## Stop rule (D-QARTOD3)
After this round an Astra ultra re-review (same prompt as D-QARTOD2, realistic inputs, stock-producible labels). If it still BLOCKs on stock inputs: stop, leave the branch unmerged, queue the decision in MORNING.
