# Brief: qartod-flags fix round 2 (after the xhigh re-review of fix round 1: BLOCK)

- Module: `QartodFlagTransform` only. Branch `deepsignal/qartod-flags`, base 37441c1 (fix round 1). Last fix round allowed (rule: two rounds).
- Lane: cloud (plain code, Sol medium). Re-review: fresh `gpt-6.2-astra` xhigh on the Mac, read-only.
- Parent brief: desk `briefs/deepsignal-qartod-flags.md` (front_check version) and `briefs/mac/qartod-flags-fix1.md`. Their rules hold.
- The module must work on BOTH Python 3.12 and Python 3.9 (contrib master ships a 2024 core tree; finding 3 is a 3.9 crash).

## Re-review findings to close (verbatim from the reviewer; each needs code plus a regression test that fails before the fix)
1. **Blocking · verified.** `Decimal('0.1')` gets gross-range flag 4 at the inclusive lower limit `0.1`. At an upper limit of `0.1`, `Decimal('0.100000000000000003')` gets flag 1. Use the same numeric conversion for span checks, configuration comparisons and median ordering, and test mixed Decimal/float boundaries. [qartod_flag_transform.py:192](/private/tmp/deepsignal/qartod-fix1/repo/contrib/deepsignal/logger/transforms/qartod_flag_transform.py:192)
2. **Blocking · verified.** On Python 3.12, with gross range `[0, 40]` and `max_rate: 1`, `1 → 10**4300` raises `ValueError` while formatting the gross-range reason. `1 → Decimal('1e5000')` also loses the record while formatting the rate. Use bounded scientific notation for extreme values and test that both records reach the caller with flag 4. [qartod_flag_transform.py:193](/private/tmp/deepsignal/qartod-fix1/repo/contrib/deepsignal/logger/transforms/qartod_flag_transform.py:193) · [qartod_flag_transform.py:251](/private/tmp/deepsignal/qartod-fix1/repo/contrib/deepsignal/logger/transforms/qartod_flag_transform.py:251)
3. **Blocking · verified.** On the contrib core with Python 3.9.6, a window-1 spike from `0 → 3` with fail limit `2` raises `TypeError` before emitting the record. That runtime cannot format a `Fraction` with `:g`, which also affects rate, timing and flat-line reasons. Use compatible numeric formatting and run the existing flag tests on an older interpreter. [qartod_flag_transform.py:228](/private/tmp/deepsignal/qartod-fix1/repo/contrib/deepsignal/logger/transforms/qartod_flag_transform.py:228)
4. **Should-fix · verified.** Mutually checking A and B, with window 1, spike limits 1/2 and companion minimum 1, produce two `AMBIGUOUS` reasons for `(0,0) → (4,2)`. B cites A even though B supplied the sole evidence that softened A. Track which companion justified each downgrade and test that the evidence cannot return to its source. [qartod_flag_transform.py:493](/private/tmp/deepsignal/qartod-fix1/repo/contrib/deepsignal/logger/transforms/qartod_flag_transform.py:493)
5. **Should-fix · verified.** For `T: 10 → 10.3` over two seconds, flat-line tolerance `1`, flat-line fail duration `2`, spike fail limit `0.2` and absent companion S, both tests give 4. The reason reports only `spike …; S missing`. Give the hard flat-line failure priority and append the companion explanation, with a regression for this tie. [qartod_flag_transform.py:545](/private/tmp/deepsignal/qartod-fix1/repo/contrib/deepsignal/logger/transforms/qartod_flag_transform.py:545)
6. **Should-fix · verified.** With two 20 Hz fields and 600 seconds of flat-line history within tolerance, median processing time was 80.9 ms per record against a 50 ms arrival interval. The same input took 0.9 ms at `47da03b`. Cache normalized samples and reduce the repeated full-window scan, then verify sustained throughput. [qartod_flag_transform.py:267](/private/tmp/deepsignal/qartod-fix1/repo/contrib/deepsignal/logger/transforms/qartod_flag_transform.py:267)
7. **Should-fix · verified.** `1.0 → 1.1000000001` in one second correctly gets flag 3, but its reason says `0.1 per second over limit 0.1`. Preserve enough precision to show the exceedance and assert the reason in the boundary test. [qartod_flag_transform.py:251](/private/tmp/deepsignal/qartod-fix1/repo/contrib/deepsignal/logger/transforms/qartod_flag_transform.py:251)
8. **Should-fix · verified.** All 34 tests stayed green under four separate changes that ignored a custom future allowance, accepted a flat-line fail duration shorter than suspect, accepted both climatology forms together, or allowed a field to corroborate itself. Test a timestamp six seconds ahead with a five-second allowance and assert a configuration error for each invalid case. [test_qartod_flag_transform.py:75](/private/tmp/deepsignal/qartod-fix1/repo/contrib/deepsignal/test/logger/transforms/test_qartod_flag_transform.py:75) · [test_qartod_flag_transform.py:312](/private/tmp/deepsignal/qartod-fix1/repo/contrib/deepsignal/test/logger/transforms/test_qartod_flag_transform.py:312)
9. **Nit · verified.** The unknown setting `self: true` still raises a generic multiple-values `TypeError` before validation. Make the receiver positional-only and test that this key gets the same one-line diagnostic as other unknown settings. [qartod_flag_transform.py:302](/private/tmp/deepsignal/qartod-fix1/repo/contrib/deepsignal/logger/transforms/qartod_flag_transform.py:302)

## Acceptance (exact commands, from repo root)
```
python3.12 -m unittest contrib.deepsignal.test.logger.transforms.test_qartod_flag_transform -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal
```
Also run the test module with python3.9 if available and say so.

## Scope
Only `contrib/deepsignal/logger/transforms/qartod_flag_transform.py`, its test file and `contrib/deepsignal/docs/qartod_flags.md`.

## Non-goals and banned
No new features, no loosened or deleted tests, no bare except, no sleeps, no value rewriting, no sub-agents.

## Stop rule
If a finding needs a design change to the parent brief, stop and report it instead.
