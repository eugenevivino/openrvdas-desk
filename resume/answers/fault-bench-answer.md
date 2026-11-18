**VERIFIED on Mac.** Branch `deepsignal/fault-bench`, HEAD `3b4b76e61af8ca020a29afcea3660bb157e78138`. Work is uncommitted.

**What changed**

- Added nine fault injectors and two traps in `bench/faults.py` and `bench/traps.py`, with 11 NBP1406 scenarios in `bench/scenarios.yaml`.
- Added plug-in loading, DASRecord replay, scoring, and CLI reports in `bench/run.py` and `bench/__main__.py`, plus `bench/stub.py`.
- Added `test/bench/__init__.py`, both test files, and the [benchmark guide](/private/tmp/deepsignal/fault-bench/repo/contrib/deepsignal/docs/fault_bench.md).

**Tests.** `test_faults.py` covers each fault and trap, exact values, truth intervals, and seed repeatability. `test_run.py` covers latency, misses, false and trap rates, threshold and missing verdicts, custom suffix and clock reset, paired front replay, plug-in CLI output, and stub replay through both sample layouts.

- RED before implementation: `ModuleNotFoundError: No module named 'contrib.deepsignal.bench'`. Tail `Ran 2 tests in 0.000s` / `FAILED (errors=2)`.
- GREEN: `Ran 17 tests in 1.110s` / `OK`. Flake8 7.5.0 passed. Homebrew Python used the existing read-only venv dependencies via `PYTHONPATH`.
- The exact stub CLI command passed twice with identical reports. The sample file SHA-256 matched before and after replay. [results.json](/private/tmp/deepsignal/fault-bench/bench-results.UOn6Ye/results.json) · [summary.md](/private/tmp/deepsignal/fault-bench/bench-results.UOn6Ye/summary.md)

| Scenario | Median latency (s) | Missed/total | False flags/h | Trap flags | Trap flags/h | False alarms/ship-day | Missing flag samples |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| air_temperature_drift | 222.994 | 0/1 | 0.000 | 0 | n/a | 0.000 | 0 |
| air_temperature_step | 0.000 | 0/1 | 0.000 | 0 | n/a | 0.000 | 0 |
| air_temperature_lag | n/a | 1/1 | 0.000 | 0 | n/a | 0.000 | 0 |
| air_temperature_hysteresis | 0.000 | 0/1 | 0.000 | 0 | n/a | 0.000 | 0 |
| mwx_clock_jump | n/a | 1/1 | 0.000 | 0 | n/a | 0.000 | 0 |
| mwx_clock_reset | n/a | 1/1 | 0.000 | 0 | n/a | 0.000 | 0 |
| air_temperature_spikes | 0.000 | 0/4 | 0.000 | 0 | n/a | 0.000 | 0 |
| air_temperature_flatline | n/a | 1/1 | 0.000 | 0 | n/a | 0.000 | 0 |
| air_temperature_dropout | n/a | 1/1 | 0.000 | 0 | n/a | 0.000 | 0 |
| pir_temperature_front | n/a | 0/0 | 0.000 | 0 | 0.000 | 0.000 | 0 |
| port_wind_direction_turn | n/a | 0/0 | 0.000 | 0 | 0.000 | 0.000 | 0 |

**Design interpretations.** Replay follows original sample order so backward timestamps reach the detector. The turn uses relative wind direction as a heading proxy. The ship-day rate counts flagged samples, and QARTOD 9 is a separate missing verdict.

**INFERRED.** The ship-day rate extrapolates a short replay. Performance on other cruises and natural faults remains unknown.

**Open items.** The Linux check and fresh read-only Astra review remain pending.