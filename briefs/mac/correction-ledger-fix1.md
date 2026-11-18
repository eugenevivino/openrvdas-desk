# Brief: correction-ledger (#56) fix round 1 (after the independent Astra high review: HOLD)

- Module: correction ledger plus apply transform only. Branch `deepsignal/correction-ledger`, base 99c01919 (fix on top)
- Lane: cloud (plain code, Sol medium). Re-review: fresh `gpt-6.2-astra` xhigh on the Mac, read-only (high-risk tier).
- Parent brief: desk `briefs/deepsignal-correction-ledger.md` (with D-REAN2); its design and data-integrity rules hold.
- Note: the first build's self-review by an unauthorized Astra sub-agent does not count; this review is the independent one.

## Review findings to close (verbatim from the reviewer; each needs code plus a regression test that fails before the fix)
**Findings**

- **P1 VERIFIED** A writer can approve their own proposal under a second `--by` name because approval checks only that two strings differ, and the ledger contains no authenticated reviewer signature. [ledger.py:283](/private/tmp/deepsignal/correction-ledger/repo/contrib/deepsignal/corrections/ledger.py:283)
- **P1 VERIFIED** `gain_offset` returned `0.0` for integer raw value `9007199254740993`, float offset `9007199254740992.0`, and gain `1`, although the exact corrected value is `1`. [apply_transform.py:132](/private/tmp/deepsignal/correction-ledger/repo/contrib/deepsignal/corrections/apply_transform.py:132)
- **P1 VERIFIED** `time_shift` published both `None` and `NaN` as corrected readings with an approval ID, uncertainty, and corrected timestamp. [apply_transform.py:109](/private/tmp/deepsignal/correction-ledger/repo/contrib/deepsignal/corrections/apply_transform.py:109)
- **P1 VERIFIED** An approved `0.00000001`-second shift at Unix time `1406937600` produced exactly `1406937600.0`, silently losing the entire shift. [apply_transform.py:110](/private/tmp/deepsignal/correction-ledger/repo/contrib/deepsignal/corrections/apply_transform.py:110)
- **P1 VERIFIED** An offset correction added a new value and approval ID alongside an existing `TSG1Temp_corr_time=0`, leaving an unrelated timestamp attached to the new correction. [apply_transform.py:75](/private/tmp/deepsignal/correction-ledger/repo/contrib/deepsignal/corrections/apply_transform.py:75)
- **P1 VERIFIED** The CLI converts `--standard-uncertainty 1e-400` to `0.0`, allowing a positive uncertainty to be recorded as zero. [__main__.py:14](/private/tmp/deepsignal/correction-ledger/repo/contrib/deepsignal/corrections/__main__.py:14)
- **P1 INFERRED** If the ledger path is replaced during an append, a rollback can report success after syncing the old inode while the live ledger still shows approval. [ledger.py:217](/private/tmp/deepsignal/correction-ledger/repo/contrib/deepsignal/corrections/ledger.py:217)
- **P2 VERIFIED** The circular-validation guard accepted `cast-7` as a fit reference and `cast-7 ` as a validation reference, so a trailing space can conceal reuse of the same evidence. [ledger.py:114](/private/tmp/deepsignal/correction-ledger/repo/contrib/deepsignal/corrections/ledger.py:114)

**Design and integrity.** VERIFIED The hash chain, transition rules, rollback, overlap suppression, reload, and raw-field preservation follow the detailed design. The docs disclose that identity authentication and detection of rehashed or truncated history at startup require external trust. That leaves the brief’s signed-record goal unmet. The numeric losses and stale timestamp above are silent deviations. [correction_ledger.md:109](/private/tmp/deepsignal/correction-ledger/repo/contrib/deepsignal/docs/correction_ledger.md:109)

**Tests.** VERIFIED The 25 tests exercise the implementation and assert exact method outputs, IDs, uncertainty, state transitions, warning pairs, and serialized raw bytes. They omit the cases above and an end-to-end sample-config check. I ran the sample’s transform chain in memory and confirmed five corrected readings followed by five untouched readings. I did not run discovery because the suite creates and deletes temporary files. [test_apply.py:21](/private/tmp/deepsignal/correction-ledger/repo/contrib/deepsignal/test/corrections/test_apply.py:21) · [test_ledger.py:51](/private/tmp/deepsignal/correction-ledger/repo/contrib/deepsignal/test/corrections/test_ledger.py:51)

**Verdict: HOLD.** VERIFIED Valid inputs produced a wrong corrected value and a lost time shift, and approval does not establish an independent signer.
## Acceptance (exact commands, from repo root)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/corrections -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal
```

## Scope
Only `contrib/deepsignal/corrections/**`, `contrib/deepsignal/test/corrections/**`, `contrib/deepsignal/configs/correction_apply_*`
and `contrib/deepsignal/docs/correction_ledger.md`.

## Non-goals and banned
No new features, no loosened or deleted tests, no bare except, no sleeps, no value rewriting, no sub-agents.
