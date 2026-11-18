# Brief: fault-bench (#53) fix round 1 (after the independent Astra high review: HOLD)

- Module: the fault-injection benchmark only. Branch `deepsignal/fault-bench`, base 9d87d99a (fix on top; no history rewrite)
- Lane: cloud (plain code, Sol medium), fresh task. Re-review: fresh `gpt-6.2-astra` ultra on the Mac, read-only.
- Parent brief: desk `briefs/deepsignal-fault-bench.md`; its design holds. Risk tier: medium (wrong scoring misleads).

## Review findings to close (verbatim from the reviewer; each needs code plus a regression test that fails before the fix)
- VERIFIED P1 `bench/run.py:125` With the wrong flag suffix, all 1,666 turn samples lacked a verdict, yet the summary reported `0.000` false flags/hour and `0.000` trap flags/hour.
- VERIFIED P1 `bench/run.py:98` Changing only the stub’s output suffix from `_QC` to `_DG` made the same dropout switch from missed to detected at 0 seconds because the scorer counted QARTOD 9 as an alarm.
- VERIFIED P1 `bench/stub.py:35` The stub returned QARTOD 1 (good) for both a NaN air temperature and a barometer reading for which it had no configured range.
- VERIFIED P1 `bench/run.py:97` Invalid QARTOD codes such as 7 count as present verdicts and silently contribute zero alarms.
- VERIFIED P1 `bench/traps.py:27`, `bench/faults.py:131` Both `turn` and `flatline` replaced an interior `None` with a numeric reading, inventing an observation at a source gap.
- VERIFIED P1 `bench/faults.py:108` The supplied 90-second clock jump creates a backward transition when the window ends, and the benchmark scored the timing detector’s flag on that injected transition as a false alarm.
- VERIFIED P1 `bench/traps.py:28` The supplied smooth-turn scenario jumps from 95° to 318° in one second when the trap ends, placing an artificial 137° reversal outside its truth interval.
- VERIFIED P1 `bench/run.py:121` A point spike at second 1 with the next sample at second 100 removes 99 seconds from outside-fault exposure, inflating the false-alarm rate.
- VERIFIED P1 `bench/run.py:107` When two samples share a timestamp, a flag on the clean sample can earn detection credit for a spike injected into the other.
- VERIFIED P1 `bench/run.py:202` A detector that returns a buffered record has its verdict scored against the current input’s source time, even when the returned record belongs to an earlier sample.
- VERIFIED P2 `bench/run.py:254` Duplicate YAML scenario names silently discard the earlier scenario and produce a report containing only the later one.
Also cover the gaps the reviewer listed: source gaps, invalid QC codes, suffix-equivalent verdicts, duplicate timestamps,
buffered output and recovery boundaries; fix the rate test that encodes the disputed point-spike denominator.

## Rules
- QARTOD 9 (missing) and absent verdicts are never alarms and never detections; report them as missing verdicts.
- Invalid QC codes are an error in the report, never a silent zero.
- Injectors and traps never invent an observation at a source gap; the benchmark never scores a detector for an
  artifact the benchmark itself created (clock-jump window end, trap end).
- Duplicate scenario names are a config error with a plain-English message.

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
No new features, no loosened or deleted tests, no bare except, no sleeps, no value rewriting, no sub-agents.

## Stop rule
Report any finding that needs a change to the parent brief's design instead of changing it.
