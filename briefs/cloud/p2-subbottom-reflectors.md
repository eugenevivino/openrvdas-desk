You are building ONE module for the DeepSignal overlay on OpenRVDAS, on Eugene's own fork. Work only in this repository (eugenevivino/openrvdas). Do NOT touch, open pull requests against, or push to OceanDataTools or any upstream repository. Nothing here is sent upstream.

Branches: create branch `deepsignal/p2-subbottom-reflectors` from commit `3b4b76e` (the contrib master tree; it is in this fork's history, for example `git merge-base origin/deepsignal/vector-wind origin/deepsignal/instrument-history`) (if `deepsignal/p2-subbottom-reflectors` already exists on origin, check it out instead). Commit your work on that branch only, with one clear commit message, and leave it pushed to origin `deepsignal/p2-subbottom-reflectors`. Do not touch any other branch, `dev` or `master`. If you cannot push, leave the commit on the branch in your task and say so.

Environment notes: Python only; Node is not needed. Use `python3.12` if it exists, otherwise `python3` (3.11 or newer). If pytest is missing use `python3 -m unittest`. If flake8 is missing, `pip install flake8` into a throwaway venv and say you did. PyYAML is already an OpenRVDAS dependency. You may add only the pinned `numpy==2.2.6` and `scipy==1.15.3` in the module-local requirements file the brief names, and must say so. No network.

YOUR LANE: cloud scaffolding only. Write the record contract, synthetic-truth fixtures and the failing tests the brief names, plus stubs that raise NotImplementedError for the estimator. Paste the RED output. Do NOT implement the estimator math: a Mac Astra session does that next on the same branch. Push the branch with the RED receipt in the commit message. Run every acceptance command at the end and paste the tails. Report under 40 lines: files changed, test names, RED then GREEN tail, acceptance results, any design point you disagree with (do not change a design silently), what you verified versus inferred, and what must run outside the sandbox.

Stop rule: two fix rounds still red means stop and report.

The full brief follows.

----------------------------------------------------------------
# Brief: p2-subbottom-reflectors (Sub-bottom reflectors with multiple-echo competition)

- Decision: reserved #173, D-SHIP1, D-FUSE1, D-REAN1 and D-REAN2. Research status BRIEFED.
- Risk tier: medium (new contrib transform and derived fields, independent math review and Linux gate).
- Module: `subbottom_reflectors` only. Branch `deepsignal/p2-subbottom-reflectors`. Base: fork contrib/master tree at `3b4b76e`.
- Lane: cloud Sol medium for record scaffolding, synthetic fixtures and RED tests only. Hand the same branch and RED receipt to mac `gpt-6.2-astra`, effort high, for estimator code and reviewable numerical evidence. Sequential owners.
- Mac scratch path: `/private/tmp/deepsignal/p2-subbottom-reflectors/` only. Fresh session per lane, under 40 turns.
- Upstream home: openrvdas_contrib, fork only. Linux Python 3.12, CPU. Estimator dependencies pinned `numpy==2.2.6` and `scipy==1.15.3` in a module-local requirements file.
- Value (techs/science/shore): 4/5/4. Mode: offline SEG-Y replay. Method: NOVEL.
- Depends on in use: #139 EM seabed reference, #142 time alignment and #143 acquisition gaps. #170 depth may be used with its SBP ancestry excluded. Synthetic tests and the standalone logger demo use the field contract below.

## Goal

Mark a coherent shallow reflector and the stretches where a water-bottom multiple could explain the same return, so a geologist can review the right traces.

## Background facts

The contrib base carries the older Transform API. Use OpenRVDAS Transform and standard reader records with the import-compatibility pattern already used by the overlay. The loadable class is `SubbottomReflectorsTransform`, module `contrib.deepsignal.subbottom_reflectors.transform`. Accept dicts and DASRecords with timestamp and fields, lists of either, or None. Pass None through. Preserve incoming record and event timestamps, raw fields and existing QC. A new derived record carries its own provenance.

Archive SBP29 SEG-Y traces at native TWT sampling, sample delay and units, shot time/coordinates, processing/gain history and matched EM nadir. Correct EM and SBP head offsets and express water-bottom time T_i relative to the same acoustic emission origin, using the local water speed. Propagate T_i uncertainty. Without an external bottom use a separately picked SBP seabed with shared ancestry. Generic SEG-Y proves reader plumbing only. R2R/NCEI candidate Revelle/Atlantis/Sally Ride requires a confirmed SBP29 export (F4/V4).

## Design and estimator contract

After documented matched filtering where needed, calculate robust log-envelope contrast e_i(k)=(log(A_i(k)+ε)−median_local)/(1.4826 MAD_local+ε_s), clipped to [−6,6]. Compare a multiple-only model with a multiple-plus-primary model. For each order m=2,3 predict M_im=T_i+(m−1)T_surface-bed,i, where the extra round trip includes the transducer-to-surface water path. For vertical monostatic propagation at constant c and head depth d the extra water-column time is T_i+2d/c. Use matched water level and trace timing for changing draft/heave. In both models fit arrivals at M_im+δ on training traces, with δ~N(0,s_M²) from bottom/time uncertainty, searched within ±2s_M. Estimate the repeatable multiple envelope in a one-pulse tube from neighboring training traces, separately by m and local gain. Subtract its predicted contrast only in estimator memory, and widen s_M for timing and wavelet error. Inside unresolved tubes mark the primary emission missing. On the residual contrast e' fit primary k_i=T_i+ℓ_i with positive lag. Minimize −Σ e'_i(k_i)+Σ |ℓ_i−ℓ_{i−1}|/(s_ℓ Δx_i) plus γ per gap trace and κ per gap entry. Compare gain over the same multiple-only background on interleaved withheld traces, deleting their emissions in the fit and interpolating only for scoring bounded gaps. This tests whether a separate bed predicts energy the multiple cannot explain.

Use band-limited dynamic programming for primary and gap states. Apply one-pulse exclusion and require ordered picks for a second horizon. Priors favor bounded reflector dip, narrow multiple timing offsets and short gaps. Return AMBIGUOUS and retain both candidate times where their tubes overlap within one wavelet length. Require independent trace support outside those tubes on both sides to link a reflector across them. After three consecutive missing traces terminate the track. A linked gap carries no pick. Normalize predictive gain by supported trace count and calibrate the margin on blinded lines.

Implement a read-only SEG-Y reader (document supported revision, fixed-length IEEE float traces, explicit byte order, time base and coordinate reference). Expose decoded trace input for other documented formats. Distinguish raw chirp, compressed signed trace and envelope in config. Use independent bottom for multiple discrimination or disclose shared provenance. Initial search defaults γ=2, κ=2, maximum primary dip 0.2 ms/m, s_ℓ=0.1 ms/m, δ grid spacing one bin, primary lag at least one pulse. A gap has no observation reward, pays γ and κ on entry. Where whole-window scores tie within a configured margin or contiguous local tubes overlap unresolved, retain both hypotheses. Emit picks after a closed window with trace IDs, never retroactively at acquisition time.

Trace reader must honor SEG-Y sample interval (µs), trace delay (ms), coordinate scalar sign, coordinate units and documented UTC convention. Support explicit known-format, signed precompressed traces and envelope traces in v1. When raw FM has a supplied replica, matched-filter via scipy.signal with documented time-zero/group-delay correction. Unsupported formats return a reason before trace allocation. Lead to verify (INFERRED): SBP29 export revision, header offsets, UTC and time-zero semantics, AGC and pulse history on the ship. Give input shape {trace_id,x_m,y_m,time_utc,delay_s,dt_s,samples,representation,source_hash,bottom_twt_s,bottom_sd_s,pulse_resolution_s}. Limit sample count, window size and max jump before allocating the DP table. Optional EM bottom is matched by footprint and time. With SBP-derived bottom record the shared raw parent and require explicit weaker-evidence labeling.

For each order, estimate the aligned local multiple at k−M_im by robust median in neighboring training traces. Interpolate its template across held-out traces only within support. On held-out traces score the residual contrast at the training path prediction minus the multiple-only baseline, with matching coverage. Compare to a null fit without the added primary. Do not score the fitted training picks as confirmation. After the test optionally pick on all traces while retaining blind line scores separately. Treat every tracked gap as a missing pick. Ambiguity above overlapping tubes needs an interval and alternative. Secondary tracks must pass the same blind test. A local sample decoder plus the pure estimator is sufficient for the branch demo.

**Result fields.** Prefix each of `TraceId`, `HorizonId`, `PickTWT_s`, `SupportCount`, `EnergyMargin`, `Alternative`, `Gap`, `Resolution_s` with `SBPH_`. Also emit prefixed `Score`, `Verdict`, `Reason`, `Support`, `Persistence`, `SourceIds`, `Stale` and `Excluded`. Units, nullability, shapes, record/interval keys and score direction go in the module docs. Explain the first check in watch language. Count independent trace/line support in Persistence, with its unit. Emit a result only for the documented processing window. Score is additional predictive contrast per supported trace. Initial threshold 1 MAD unit, minimum five separated trace supports and positive blind gain. Expose these as configuration.

The tech sees shadow zones and heave breaks. The scientist gets trace ID, TWT picks, gap intervals and alternatives for annotation. A dipping multiple crossing a bed, gas blanking, gain discontinuity, datum mismatch or a genuinely pinching layer can erase tilt evidence. Resolve two horizons only when pulse bandwidth and SNR support the spacing. Convert to metres only with independently measured sediment velocity.

## Math review fixes (binding; `research/2026-11-18-sonar-math-review.md`, cdb7efb)

These override anything above or below that conflicts. Each added test is part of "Failing test first".

1. **Track termination (P1).** Terminate a track when `missing_run >= 3` consecutive traces, everywhere (code, docs, SONAR-SCIENCE). Test `test_terminate_at_three_missing` (exactly three missing terminates, two does not); the old four-trace fixture is not enough.
2. **Multiple timing uncertainty (P2).** For order m at fixed draft and sound speed, M_m = mT + 2(m-1)d/c and SD(M_m) = m SD(T). With uncertain draft or speed, propagate the full gradient with their covariance. Never reuse the bottom-pick SD for higher orders. Test `test_order3_timing_sd` (SD triples at m=3).
3. **Score units (P3).** The contrast threshold is 1 standardized contrast unit (equal to 1.4826 raw log-envelope MADs when the floor is negligible). State it that way in code and docs.
4. **Added tests.** `test_repeated_positions` (Delta x = 0 between traces: no division by zero, traces merged or flagged), `test_withheld_traces_one_footprint` (adjacent withheld traces inside one footprint count as one independent block). Repeatability counts independent footprint or line blocks, not traces.

Simulation targets (fault recall, Monte Carlo covariance error, reflector recall, false-repeat rate) are acceptance claims only once the run's realized outputs are pasted in the report; the review could not verify them from the brief.

## Failing test first

Add `contrib/deepsignal/test/subbottom_reflectors/test_estimator.py`. Run `test_primary_disappears_inside_multiple_tube` and `test_no_pick_in_trace_gap` on the base before implementing the estimator. Capture the actual RED output. Each test must exercise the future public class or function, with explicit expected numbers or verdicts. Follow with tests for record shape, replay determinism, immutable inputs, absent channels and the demo logger chain.

## Synthetic-truth fixtures

Generate 256 traces at 1 m spacing, dt=0.00025 s, zero delay then nonzero trace delay. Convolve unit reflectors with a band-limited zero-phase wavelet of declared 1 ms resolution. Deterministic noise SD=0.05 times primary amplitude. Set T_i=0.040+0.00004i s, primary T_i+0.044 s, stronger multiple 2T_i. Use a positive standard-deviation floor on flat background windows. Use zero draft for this crossing, which occurs at i=100. In a second fixture with 3 m draft and c=1500 m/s, the order-two arrival shifts by +4 ms relative to 2T_i at the same head-to-bed T_i. Include another primary at T_i+0.012 s and verify that it remains separate from the stronger multiple. Add a multiple-only stretch, four missing traces and a pinch-out in separate fixtures. Assert timing on separated branches, sustained overlap AMBIGUOUS, no post-gap invented picks and identical coordinates after SEG-Y scalar −100 conversion. Hand-build a small standard IEEE-float SEG-Y stream with nonzero delay. Verify truncation, bad units, unsupported gain/encoding and rotation.

Use fixed construction parameters, a local random generator seeded 17001 for development and disjoint seeds 27001 through 27020 for final injection trials. Preserve input hashes. Split fit and holdout by line/site/time block with a footprint buffer. Confirm in a test that the fit receives no holdout IDs. Treat correlated samples in an ensemble or trace as one evidence block. Compare blind feature scores by whole line and count easy abstentions as misses.

## Validation target and falsifier

Test on synthetic chirps with crossing primary/multiple, heave jitter and missing traces, then on NCEI/R2R SEG-Y with two independent blind interpreters (V4). Compare against strongest peak plus continuity. Target median TWT error ≤1 pulse resolution and ≤5% of labeled multiple-only stretches called primary, at ≥80% recall on separable segments. Reject if ambiguity is suppressed at sustained overlap or a path bridges a file gap.

**INFERRED, lead to verify.** F4/V4 means public SEG-Y rev 1/2, R2R ship inventories and NCEI Marine Trackline Geophysical Data. Confirm a real SBP29 export and independent picks before field-performance claims. These are later validation candidates. Do not fetch sonar data to the Mac. Synthetic unit acceptance and real-cruise validation have separate receipts.

## Module contract and platform

Own the estimator, its documented input adapter and transform, tests, one offline-safe logger config `contrib/deepsignal/configs/subbottom_reflectors_demo.yaml`, and `contrib/deepsignal/docs/subbottom_reflectors.md`. The sample connects a local Reader to the Transform to a local text output with synthetic input built from this module’s own fixtures. Test the config by loading its class/module declarations and running its normal record path on a fixture. Document each knob's unit, expected range, example, and first check after an alarm. Respond to the desk usability checklist or mark an item N/A with a reason. No browser or GPU.

## Acceptance (from the fork root on Linux)

The first command must be RED before estimator code, then pass with both named tests and the rest of the suite. The second exits zero. The third prints True using the module's installed environment.

```sh
python3.12 -m unittest discover -s contrib/deepsignal/test/subbottom_reflectors -t . -v
```

```sh
python3.12 -m flake8 --config .flake8 contrib/deepsignal/subbottom_reflectors contrib/deepsignal/test/subbottom_reflectors
```

```sh
python3.12 -c "import numpy, scipy; assert (numpy.__version__, scipy.__version__) == ('2.2.6', '1.15.3'); print(True)"
```

Record the exact tested fork SHA. The lead's subsequent gate checks that same SHA and requires a complete receipt with `__END__` and no unexpected FAIL. Science targets need a separate blocked-holdout report.

## Scope

Only `contrib/deepsignal/subbottom_reflectors/**`, `contrib/deepsignal/test/subbottom_reflectors/**`, `contrib/deepsignal/docs/subbottom_reflectors.md`, `contrib/deepsignal/configs/subbottom_reflectors_demo.yaml` and missing empty package markers. The requirements pins belong under the module. Check the config load path, old and current Transform imports, existing field consumers and logger output serialization. Consume upstream fields through schema adapters. A standalone demo can supply those same fields. Any integration with shared factors imports the versioned API when available.

## Trust boundaries and data integrity

D-SHIP1 is listen-only. Accept existing operator-distributed UDP through a core reader, complete public-format file tails when supported, or local archives. No module socket, vendor subscription, instrument query, configuration or triggering. Validate version, units, timestamps, frame, datum, finite numeric values, bounds and ancestry before estimation. Bound record counts and memory before allocation, count invalid/duplicate/partial inputs, report stale or unsupported inputs as missing. A short tail read waits for a complete record. A torn archive record is reported. No extrapolation across a file gap. Reject a prefix collision. A test must show the input bytes/fields and original timestamp survive unchanged.

Use the evidence graph: trace each fit to raw channels, calibration, clock, navigation and parent fits. Collapse duplicates and keep covariance for shared errors. Science feature scores have independent QC. Use GOOD/1, SUSPECT/3, FAULT_LIKELY/4, AMBIGUOUS/3, UNCORRECTABLE/4 and POSTHOC_REVIEW/2 as appropriate. An obscured cause is AMBIGUOUS. Score, support/persistence and a plain explanation accompany every flag. Only independent post-cruise evidence can qualify a CORRECTABLE proposal for #56. A named allowlisted reviewer approves any reversible ledger correction at a trusted checkpoint. This module produces derived observations only.

## Non-goals and banned

No lithology or impedance assignment, edits to SEG-Y headers, reconstruction of lost picks or proprietary chirp decoder. No core changes or global dependency changes. No loosened/skipped tests, silent errors or unrelated refactors. No writes outside module scope and its dedicated scratch during the build.

## Stop rule and result

If no change is needed, report the evidence. After two red fix rounds report the remaining failure to the lead. For an unverified format version, disable that version and continue with the documented input contract. Report within 30 lines.

- Head SHA and short diff:
- RED test names and actual output:
- Linux acceptance tails, gate receipt SHA256/verdict if run:
- Synthetic truth, baseline, achieved error/coverage, ambiguity and resource use:
- Real evidence checked, remaining inferred leads and limitations:
