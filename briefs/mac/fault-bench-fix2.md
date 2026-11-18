# Brief: fault-bench (#53) fix round 2 (final; after the Astra ultra re-review of fix round 1: HOLD)

- Module: the fault-injection benchmark only. Branch `deepsignal/fault-bench`, base 2b2be69 (fix round 1). Last fix round allowed.
- Lane: cloud (plain code, Sol medium). Re-review: fresh `gpt-6.2-astra` ultra on the Mac, read-only.
- Parent briefs: desk `briefs/deepsignal-fault-bench.md` and `briefs/mac/fault-bench-fix1.md`; their rules hold.

## Re-review findings to close (verbatim; each needs code plus a regression test that fails before the fix)
**Findings at `2b2be69`**

- VERIFIED P1 [run.py:248](/private/tmp/deepsignal/fault-bench-rr/contrib/deepsignal/bench/run.py:248) excludes unchanged values from injector truth, giving an always-alarming detector 1-second latency on the supplied drift and only 358 trap flags across 360 labeled turn samples.
- VERIFIED P1 [run.py:246](/private/tmp/deepsignal/fault-bench-rr/contrib/deepsignal/bench/run.py:246) assigns both same-timestamp spikes to both truth events, so one alarm earns two detections.
- VERIFIED P1 [run.py:238](/private/tmp/deepsignal/fault-bench-rr/contrib/deepsignal/bench/run.py:238) uses recyclable object IDs for attribution: a detector returning a flagged copy after `None` produced one miss and one false alarm, while a detector returning copies from its first call was rejected.
- VERIFIED P1 [run.py:250](/private/tmp/deepsignal/fault-bench-rr/contrib/deepsignal/bench/run.py:250) applies recovery handling only to `clock_jump`, so a timing detector correctly flagging the supplied `clock_reset` recovery received a false alarm.
- VERIFIED P1 [run.py:150](/private/tmp/deepsignal/fault-bench-rr/contrib/deepsignal/bench/run.py:150) also removes the clean time *after* a jump recovery sample, reducing 890 seconds of outside-fault exposure to 2 in an irregular replay.
- VERIFIED P1 [run.py:104](/private/tmp/deepsignal/fault-bench-rr/contrib/deepsignal/bench/run.py:104) counts QARTOD 2 as evaluated exposure, reporting zero false flags/hour and zero missing verdicts for an entire hour marked “not checked.”
- VERIFIED P1 [stub.py:33](/private/tmp/deepsignal/fault-bench-rr/contrib/deepsignal/bench/stub.py:33) labels a present, unconfigured barometer reading 9 (missing) instead of 2 (not checked), and returns 9 for 40°C with an explicit maximum of 21°C.
- VERIFIED P1 [stub.py:20](/private/tmp/deepsignal/fault-bench-rr/contrib/deepsignal/bench/stub.py:20) accepts a NaN maximum, allowing 999°C to receive QARTOD 1.
- VERIFIED P1 [stub.py:40](/private/tmp/deepsignal/fault-bench-rr/contrib/deepsignal/bench/stub.py:40) accepts an empty suffix and overwrites the raw temperature of 20 with the verdict 1.
- VERIFIED P1 [faults.py:130](/private/tmp/deepsignal/fault-bench-rr/contrib/deepsignal/bench/faults.py:130) turns `[None, 12, 13]` into three missing readings and fills an interior NaN with the held number.
- VERIFIED P1 [faults.py:62](/private/tmp/deepsignal/fault-bench-rr/contrib/deepsignal/bench/faults.py:62) lets one NaN poison the lag filter, turning subsequent valid readings of 20 and 19 into NaNs.
- VERIFIED P1 [run.py:144](/private/tmp/deepsignal/fault-bench-rr/contrib/deepsignal/bench/run.py:144) double-counts overlapping plug-in trap intervals, reporting 14 seconds of trap exposure in a 10-second replay.
- VERIFIED P2 [run.py:100](/private/tmp/deepsignal/fault-bench-rr/contrib/deepsignal/bench/run.py:100) silently classifies an infinite numeric verdict as absent despite the documented error for unsupported numeric codes.
- VERIFIED P2 [run.py:61](/private/tmp/deepsignal/fault-bench-rr/contrib/deepsignal/bench/run.py:61) converts the integer `MwxPortStatus` to a float, causing a detector that checks a status bit to raise `TypeError` on the supplied data.
- VERIFIED P2 [run.py:294](/private/tmp/deepsignal/fault-bench-rr/contrib/deepsignal/bench/run.py:294) rejects YAML scenario mappings using `<<` merges that the previous loader accepted.
- VERIFIED P2 [test_run.py:117](/private/tmp/deepsignal/fault-bench-rr/contrib/deepsignal/test/bench/test_run.py:117) puts replay fixtures in the checkout’s parent, which here is outside the brief’s permitted scratch directory.

**Round-one closure, design and tests**

- VERIFIED The reported wrong-suffix rates, suffix-dependent QARTOD 9 alarm, code 7 acceptance, point-spike exposure and `clock_jump` recovery alarm have code fixes and regression assertions. I also replayed the wrong-suffix turn and confirmed both rates are `n/a` across 1,666 missing verdicts. [test_run.py:89](/private/tmp/deepsignal/fault-bench-rr/contrib/deepsignal/test/bench/test_run.py:89) · [test_run.py:161](/private/tmp/deepsignal/fault-bench-rr/contrib/deepsignal/test/bench/test_run.py:161)
- VERIFIED Exact tests cover the reported interior `None` gaps, smooth turn recovery and NaN stub input. The same stub test requires the incorrect 9 for a present barometer reading. [test_faults.py:67](/private/tmp/deepsignal/fault-bench-rr/contrib/deepsignal/test/bench/test_faults.py:67) · [test_faults.py:84](/private/tmp/deepsignal/fault-bench-rr/contrib/deepsignal/test/bench/test_faults.py:84) · [test_run.py:57](/private/tmp/deepsignal/fault-bench-rr/contrib/deepsignal/test/bench/test_run.py:57)
- VERIFIED Duplicate-timestamp coverage supplies the correct sample index manually, bypassing the replay code that assigns it. Buffered same-object attribution and duplicate-name rejection have code fixes, but I confirmed both regression tests’ assertions also pass against the pre-fix runner. [test_run.py:108](/private/tmp/deepsignal/fault-bench-rr/contrib/deepsignal/test/bench/test_run.py:108) · [test_run.py:170](/private/tmp/deepsignal/fault-bench-rr/contrib/deepsignal/test/bench/test_run.py:170) · [test_run.py:209](/private/tmp/deepsignal/fault-bench-rr/contrib/deepsignal/test/bench/test_run.py:209)
- VERIFIED All nine faults, both traps, both sample layouts and plug-in injection are implemented. Replay reads source files into memory. Its silent departures from the brief include narrowing injector truth by value equality and requiring detector output to retain Python object identity.
- VERIFIED All 21 file-free tests passed and all 11 supplied scenarios ran in memory. I inspected the seven file-writing tests. Exact assertions cover fault values, labels, latency, misses and ship-day rates, but no test asserts a numeric trap-flags/hour result with positive exposure.

**VERIFIED verdict: HOLD.** The benchmark can award two detections for one alarm and charge a correct clock-recovery alarm as false.## Acceptance (exact commands, from repo root)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/bench -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal
```
```
python3.12 -m contrib.deepsignal.bench run --scenarios contrib/deepsignal/bench/scenarios.yaml --detector contrib.deepsignal.bench.stub:StubThresholdDetector --kwargs '{}'
```

## Scope
Only `contrib/deepsignal/bench/**`, `contrib/deepsignal/test/bench/**` and `contrib/deepsignal/docs/fault_bench.md`.

## Non-goals and banned
No new features, no loosened or deleted tests, no bare except, no sleeps, no value rewriting, no sub-agents.

## Stop rule
Report any finding that needs a change to the parent brief's design instead of changing it.
