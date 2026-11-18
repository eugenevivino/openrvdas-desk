# Brief: fault-bench (#53) fix round 3 (final, approved by the coordinator 17:36Z; after the Astra ultra re-review of fix round 2: HOLD)

- Module: the fault-injection benchmark only. Branch `deepsignal/fault-bench`, base 823e7c0 (fix round 2). This is the last round; no round 4.
- Lane: Mac, `gpt-6.2-astra` high (scoring math). Re-review: fresh `gpt-6.2-astra` ultra on the Mac, read-only.
- Parent briefs: desk `briefs/deepsignal-fault-bench.md`, `briefs/mac/fault-bench-fix1.md` and `briefs/mac/fault-bench-fix2.md`; their rules hold.

## Required tests
1. One regression test per finding below (all 9 P1s, the 3 P2s and the P3 doc fix where testable). Each test must fail on 823e7c0 and pass after the fix. Exercise the real replay and injector paths; do not hand-supply sample indices or bypass attribution.
2. A small property test for order independence: for a fixed set of truth intervals, alarms and verdict rows, every shuffle of the truth interval list and of the verdict row order (use a fixed seed, at least 50 permutations, or all permutations for small sets) gives the same miss count, detection count and false-alarm count.

## Re-review findings to close (verbatim from desk research/2026-11-18-fault-bench-final-review.md)
**Findings at `823e7c0`**

- VERIFIED P1 An empty `--flag-suffix` makes the runner read raw measurements as verdicts, giving a detector that emitted no flags a zero-second detection when the measurement was 4. [run.py:264](/private/tmp/deepsignal/fault-bench-rr2/contrib/deepsignal/bench/run.py:264)
- VERIFIED P1 A step applied to two rows at the same timestamp earned one false alarm when both rows were correctly flagged, because replay selected only one injected row. [run.py:277](/private/tmp/deepsignal/fault-bench-rr2/contrib/deepsignal/bench/run.py:277)
- VERIFIED P1 With alarms at seconds 0 and 1, reversing truth intervals `[0,1]` and `[0,0]` changed the miss count from one to zero. [run.py:144](/private/tmp/deepsignal/fault-bench-rr2/contrib/deepsignal/bench/run.py:144)
- VERIFIED P1 Calling the same `clock_reset` function through `injector:` changed its recovery alarm from zero false flags to one. [run.py:281](/private/tmp/deepsignal/fault-bench-rr2/contrib/deepsignal/bench/run.py:281)
- VERIFIED P1 Returning a second verdict for the same source record silently overwrote its earlier 4 with 1, changing a detected fault into a miss. [run.py:264](/private/tmp/deepsignal/fault-bench-rr2/contrib/deepsignal/bench/run.py:264)
- VERIFIED P1 A NaN immediately before the lag window turned the next two valid readings, 20 and 19, into NaNs. [faults.py:55](/private/tmp/deepsignal/fault-bench-rr2/contrib/deepsignal/bench/faults.py:55)
- VERIFIED P1 The spike injector selected a NaN despite an available finite reading and recorded spike truth without producing a spike. [faults.py:119](/private/tmp/deepsignal/fault-bench-rr2/contrib/deepsignal/bench/faults.py:119)
- VERIFIED P1 Hysteresis emitted 18 versus 15 for the same reading of 15 depending on whether the preceding gap was NaN or `None`. [faults.py:78](/private/tmp/deepsignal/fault-bench-rr2/contrib/deepsignal/bench/faults.py:78)
- VERIFIED P1 A NaN step bias converted every finite reading in the window to NaN and produced a scored miss. [faults.py:46](/private/tmp/deepsignal/fault-bench-rr2/contrib/deepsignal/bench/faults.py:46)
- VERIFIED P2 Replay rejected a newly constructed, flagged `DASRecord` when the detector omitted the runner’s undocumented metadata key. [run.py:261](/private/tmp/deepsignal/fault-bench-rr2/contrib/deepsignal/bench/run.py:261)
- VERIFIED P2 Duplicate scenario names inside an inline YAML merge silently discard the first configuration. [run.py:332](/private/tmp/deepsignal/fault-bench-rr2/contrib/deepsignal/bench/run.py:332)
- VERIFIED P2 Replay fixtures still default to the system temporary directory, which is outside the brief’s permitted scratch path on this Mac. [test_run.py:192](/private/tmp/deepsignal/fault-bench-rr2/contrib/deepsignal/test/bench/test_run.py:192)
- VERIFIED P3 The guide omits QARTOD 2 from the verdicts counted as missing and excluded from exposure. [fault_bench.md:86](/private/tmp/deepsignal/fault-bench-rr2/contrib/deepsignal/docs/fault_bench.md:86)

## Acceptance (exact commands, from repo root)
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
No new features, no loosened or deleted tests, no bare except, no sleeps, no value rewriting, no sub-agents. Tests must not write outside the scratch path the parent brief permits.

## Stop rule
Report any finding that needs a change to the parent brief's design instead of changing it.
