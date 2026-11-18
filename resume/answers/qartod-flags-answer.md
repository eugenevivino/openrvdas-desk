Implemented `QartodFlagTransform` on `deepsignal/qartod-flags` at `3b4b76e6`. It adds QC flags to copied records and preserves the original values, timestamps, and field order. No commits were made.

**Files changed**

- [Transform](/private/tmp/deepsignal/qartod-flags/repo/contrib/deepsignal/logger/transforms/qartod_flag_transform.py) and [unit tests](/private/tmp/deepsignal/qartod-flags/repo/contrib/deepsignal/test/logger/transforms/test_qartod_flag_transform.py)
- [Sample logger config](/private/tmp/deepsignal/qartod-flags/repo/contrib/deepsignal/configs/qartod_flags_logger.yaml), [operator docs](/private/tmp/deepsignal/qartod-flags/repo/contrib/deepsignal/docs/qartod_flags.md), and six empty `__init__.py` files

**Tests**  
`test_gross_range`, `test_climatology_static_and_utc_months`, `test_spike_uses_prior_median_and_default_window`  
`test_rate_of_change_uses_seconds_and_checks_positive_step`, `test_flat_line_duration_and_current_value_tolerance`  
`test_timing_order_gap_future_and_unusable_timestamp`, `test_timing_uses_previous_record_even_if_field_absent`, `test_timing_checks_present_missing_values_without_overriding_missing`  
`test_aggregate_priority_and_per_test_flags`, `test_missing_absent_and_syntax`, `test_history_skips_syntax_and_gross_range_failures`  
`test_preserves_record_type_timestamp_field_order_and_input`, `test_existing_qc_field_is_preserved`, `test_raw_string_passes_through_with_one_warning`  
`test_front_moving_flat_missing_bad_and_without_prior_value`, `test_front_rate_and_hard_failures_take_priority`, `test_front_ignores_companion_history_older_than_jump_window`, `test_front_reason_keeps_missing_companion_when_suspect_checks_tie`  
`test_configuration_errors_explain_setting_value_expectation_and_example`

**RED → GREEN**

```text
ModuleNotFoundError: No module named 'contrib.deepsignal.logger'
Ran 1 test in 0.000s
FAILED (errors=1)

Ran 19 tests in 0.003s
OK
```

**VERIFIED**  
All 19 tests passed on macOS Python 3.12 against the pinned checkout and the current core interfaces from `3f3d0c37`. Flake8 passed with `.flake8` in an existing Python 3.12 environment. The default interpreter lacks flake8.  
The listener emitted 5,000 JSON records from the sample, including 1,667 with both QC flags, after bypassing unrelated driver imports in memory. The stock command stops during import because `paho-mqtt` is absent locally.

**INFERRED**  
Linux Python 3.12 compatibility and stock listener startup with the core dependencies installed.

**Design review**  
No disagreements. Where the brief left a choice, existing fields take priority on name collisions, and a hard failure takes priority in the single reason field.