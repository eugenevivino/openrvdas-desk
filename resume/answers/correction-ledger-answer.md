Implemented the correction ledger and apply transform on `deepsignal/correction-ledger`. HEAD is `3b4b76e61af8ca020a29afcea3660bb157e78138`. All changes are uncommitted.

**What changed**

- Added the hash-chained ledger, CLI, review state machine, and independent validation guard. [Ledger](/private/tmp/deepsignal/correction-ledger/repo/contrib/deepsignal/corrections/ledger.py) [CLI](/private/tmp/deepsignal/correction-ledger/repo/contrib/deepsignal/corrections/__main__.py) [Package init](/private/tmp/deepsignal/correction-ledger/repo/contrib/deepsignal/corrections/__init__.py)
- Added the transform to publish corrected values, proposal IDs, and uncertainty alongside raw readings. Reload requires the previously verified history to be present. [Transform](/private/tmp/deepsignal/correction-ledger/repo/contrib/deepsignal/corrections/apply_transform.py)
- Added the NBP1406 replay, sample ledger with one approval and one rollback, and event format contract. [Config](/private/tmp/deepsignal/correction-ledger/repo/contrib/deepsignal/configs/correction_apply_logger.yaml) [Sample ledger](/private/tmp/deepsignal/correction-ledger/repo/contrib/deepsignal/configs/correction_apply_ledger.jsonl) [Docs](/private/tmp/deepsignal/correction-ledger/repo/contrib/deepsignal/docs/correction_ledger.md)

**Tests**

- Ledger tests include `test_every_state_transition`, `test_author_cannot_review_own_proposal`, `test_tampered_line_is_reported_and_never_repaired`, `test_valid_event_hash_does_not_excuse_wrong_previous_link`, `test_legacy_uncertainty_alias_on_disk`, `test_overlapping_refs_rejected_and_named`, `test_noncorrectable_state_rejected`, and `test_cli_round_trip`. [test_ledger.py](/private/tmp/deepsignal/correction-ledger/repo/contrib/deepsignal/test/corrections/test_ledger.py)
- Apply tests include `test_each_method_and_uncertainty`, `test_raw_values_timestamp_order_and_inputs_preserved`, `test_dasrecord_list_and_none`, `test_overlap_warns_once_per_pair_and_skips_correction`, `test_reload_on_change_and_rollback_removes_effect`, `test_reload_rejects_truncated_rollback`, and `test_microsecond_windows_match_iso_records_exactly`. [test_apply.py](/private/tmp/deepsignal/correction-ledger/repo/contrib/deepsignal/test/corrections/test_apply.py) [Test package init](/private/tmp/deepsignal/correction-ledger/repo/contrib/deepsignal/test/corrections/__init__.py)

**VERIFIED**

- **RED receipt** · `ModuleNotFoundError: No module named 'contrib.deepsignal.corrections'` · `Ran 2 tests in 0.000s` · `FAILED (errors=2)`.
- **GREEN** · Homebrew Python 3.12 · `Ran 25 tests in 0.734s` · `OK`. Flake8 7.5.0 exited 0.
- **Replay** · 5,000 NBP1406 rows, exactly five corrected. The checkout’s listener startup required an in-memory shim for its missing `paho-mqtt` import.
- **Review** · Fresh read-only `gpt-6.2-astra` xhigh review found issues in reload integrity, numeric precision, and compatibility. Follow-up verified the fixes and reported no remaining blockers.

**INFERRED / DESIGN**

- Windows include `start` and exclude `end`. Matching uses field and time, with instrument IDs retained for provenance. Shifted timestamps use Unix seconds.
- **Design disagreement** · Names and hashes provide attribution and chain integrity. Authenticating reviewers and detecting a fully rehashed or truncated file at startup require external trust.
- **Linux check** · Not run. **Open question** · Does production require authenticated reviewers or a persisted, trusted ledger checkpoint?