You are building ONE module for the DeepSignal overlay on OpenRVDAS, on Eugene's own fork. Work only in this repository (eugenevivino/openrvdas). Do NOT touch, open pull requests against, or push to OceanDataTools or any upstream repository. Nothing here is sent upstream.

Branches: create branch `deepsignal/p2-sounding-uncertainty` from commit `3b4b76e` (the contrib master tree; it is in this fork's history, for example `git merge-base origin/deepsignal/vector-wind origin/deepsignal/instrument-history`) (if `deepsignal/p2-sounding-uncertainty` already exists on origin, check it out instead). Commit your work on that branch only, with one clear commit message, and leave it pushed to origin `deepsignal/p2-sounding-uncertainty`. Do not touch any other branch, `dev` or `master`. If you cannot push, leave the commit on the branch in your task and say so.

Environment notes: Python only; Node is not needed. Use `python3.12` if it exists, otherwise `python3` (3.11 or newer). If pytest is missing use `python3 -m unittest`. If flake8 is missing, `pip install flake8` into a throwaway venv and say you did. PyYAML is already an OpenRVDAS dependency. You may add only the pinned `numpy==2.2.6` and `scipy==1.15.3` in the module-local requirements file the brief names, and must say so. No network.

YOUR LANE: cloud scaffolding only. Write the record contract, synthetic-truth fixtures and the failing tests the brief names, plus stubs that raise NotImplementedError for the estimator. Paste the RED output. Do NOT implement the estimator math: a Mac Astra session does that next on the same branch. Push the branch with the RED receipt in the commit message. Run every acceptance command at the end and paste the tails. Report under 40 lines: files changed, test names, RED then GREEN tail, acceptance results, any design point you disagree with (do not change a design silently), what you verified versus inferred, and what must run outside the sandbox.

Stop rule: two fix rounds still red means stop and report.

The full brief follows.

----------------------------------------------------------------
# Brief: p2-sounding-uncertainty (Crossline-tested sounding uncertainty)

- Decision: reserved #172, D-SHIP1, D-FUSE1, D-REAN1 and D-REAN2. Research status BRIEFED.
- Risk tier: medium (new contrib transform and derived fields, independent math review and Linux gate).
- Module: `sounding_uncertainty` only. Branch `deepsignal/p2-sounding-uncertainty`. Base: fork contrib/master tree at `3b4b76e`.
- Lane: cloud Sol medium for record scaffolding, synthetic fixtures and RED tests only. Hand the same branch and RED receipt to mac `gpt-6.2-astra`, effort high, for estimator code and reviewable numerical evidence. Sequential owners.
- Mac scratch path: `/private/tmp/deepsignal/p2-sounding-uncertainty/` only. Fresh session per lane, under 40 turns.
- Upstream home: openrvdas_contrib, fork only. Linux Python 3.12, CPU. Estimator dependencies pinned `numpy==2.2.6` and `scipy==1.15.3` in a module-local requirements file.
- Value (techs/science/shore): 5/5/5. Mode: live per sounding with offline calibration. Method: ADAPTED.
- Depends on in use: #57 uncertainty, #139 raw ping identity/context, #142 clock/lag, #146 motion RMS and #147 profile history. #161/#171 optional and ancestry checked. Synthetic tests and the standalone logger demo use the field contract below.

## Goal

Tell the watch the uncertainty on a sounding in metres and which measured input dominates it. Let the shore processor check the interval on a separate line.

## Background facts

The contrib base carries the older Transform API. Use OpenRVDAS Transform and standard reader records with the import-compatibility pattern already used by the overlay. The loadable class is `SoundingUncertaintyTransform`, module `contrib.deepsignal.sounding_uncertainty.transform`. Accept dicts and DASRecords with timestamp and fields, lists of either, or None. Pass None through. Preserve incoming record and event timestamps, raw fields and existing QC. A new derived record carries its own provenance.

Per valid sounding use range time/detection quality, beam angle, measured attitude/heading/heave and covariance, time lag and its uncertainty from #142, trajectory and rates, #113 lever arms, draft/datum errors, per-depth SV covariance, and detection/range uncertainty by sector. #139 `MB_AttTime`, `MB_PingTime`, `MB_ClockOffset` support the join. A clock offset is not its standard deviation. Pose RMS from #146 if supported, else documented spec priors labeled as such. Revelle RR2214 or Armstrong AR74 conditional on motion metadata. Batch Jacobians by sector per ping. Archive calibration needs independent check soundings or crosslines with known covariance.

## Design and estimator contract

For sounding p=f(q)=(E,N,depth) on a stated datum, propagate Σ_p=JΣ_qJᵀ+Σ_detect, J=∂f/∂q. Use radians, seconds, metres and m/s. Differentiate the full pose/lever-arm/ray equation, including ∂p/∂t from ship translation and angular rates. Keep correlations and label priors. Report vertical SD and horizontal ellipse axes from eigenvalues of the horizontal block (95% Gaussian axes multiply SD by sqrt(5.991)). For a crossline on terrain gradient g use n=(−g_E,−g_N,1). Difference variance s²=nᵀ(Σ_i+Σ_j−C_ij−C_ijᵀ)n+s²_match, with C_ij from shared ancestry. Compare |d|/s to 1.96. Crossing residuals alone constrain differences.

For vertical calibration against an independent surveyed reference with negligible uncertainty relative to the minimum tested SD (default ≤0.1×), use a predeclared random representative sounding from each independent line block per angle/regime class. Use a level site or account for gradient and horizontal uncertainty. Order scores |z−z_ref|/s_z, k=ceil((B+1)0.95). Multiplier q is score k (1-indexed). Keep classes with ≥39 independent calibration blocks and a finite order statistic. Freeze q for live use. With appreciable reference uncertainty use combined comparison variance and label the resulting interval as a prediction of disagreement. Calibration on crossline differences yields a difference multiplier only. Apply a vertical multiplier to single soundings solely for the independently anchored, matching regime. Coverage is marginal for exchangeable representative blocks. Horizontal coverage needs independent horizontal control.

Ship a documented public KMALL sounding adapter for #MRZ, #SKM and mapped context or accept the normalized ray/pose packet from #171. Standalone config uses the same packet contract from a local text reader. Carry head/sector/sounding IDs, launch vector, transmit/receive times, nav/pose, ray model, units, datum and positive semidefinite covariance with source identifiers. A supported first geometry is a straight ray in verified homogeneous water, p=origin+R(lever+(c t/2)u). Use full profile ray function for stratified data or return incomplete-model status. Offline calibration is a pure function over block-keyed samples, validating units, regime and hashes of the frozen calibration table. Separate 95% lower/upper endpoints from half-widths in the schema. Attribute correlated error with signed cross terms displayed separately.

Minimum normalized packet contains event time, system/head/swath/ping/beam/sector, local origin ENZ, tilt/pointing, travel time, pose and lever arm, unit-tagged q-vector and labeled covariance, static/installation ID, measured-versus-prior source IDs, validity masks and optional profile/ray function. Include sampling/detection variance exactly once. Map public #MRZ twoWayTravelTime_sec, beamAngleReRx_deg, sector tilt, txTransducerDepth_m and nav. Use #SKM or measured motion records, bracketed at the correct transmit/receive times. Lead to verify (INFERRED): offsets and corrections for each KMALL version, clock-error covariance, alignment of live fields on each installation. A .kmall tail or existing UDP receiver may feed the module. Legacy .all N/X and independently decoded normalized rays have the same contract. Never infer RMS from a single absolute offset.

Accept a positive-semidefinite Σ with physically valid units, finite diagonals and checked symmetry. Missing cross-covariance between shared terms uses a flagged sensitivity bound or an incomplete result. Offline calibration records include target (single vertical depth or difference), alpha, angle/mode/epoch bins, number of independent blocks, representative selection seed and fit hashes. Look up using only prior records in live mode. Propagate horizontal ellipse orientation east of north, modulo 180°, suppress orientation for a circular ellipse. Show component units, calibration source and whether the interval refers to an individual sounding or a comparison.

**Result fields.** Prefix each of `SoundingId`, `Cov_ENZ_m2`, `VerticalSD_m`, `Vertical95_m`, `HorizontalAxes95_m`, `HorizontalAzimuth_deg`, `DominantTerm`, `CalibrationId`, `IntervalTarget` with `TPU_`. Also emit prefixed `Score`, `Verdict`, `Reason`, `Support`, `Persistence`, `SourceIds`, `Stale` and `Excluded`. Units, nullability, shapes, record/interval keys and score direction go in the module docs. Explain the first check in watch language. Use record time for live persistence. An alert requires 60 s continuously over threshold and clears after 60 s below 75% of threshold. A gap resets the timer. Replay must be causal and deterministic. For the watch score, use vertical half-width divided by the configured science tolerance (both metres), threshold 1. Record target and calibration status.

A tech can see timing dominate on turns and SV dominate at large incidence. Science can select soundings by stated precision. Wrong covariance, sound-speed/motion double counting, a new installation epoch and common datum errors defeat crossline tests. Report an uncalibrated propagated interval or missing component on unsupported inputs. Offline seed-fixed Monte Carlo checks strong nonlinearity and bounded inputs.

## Failing test first

Add `contrib/deepsignal/test/sounding_uncertainty/test_estimator.py`. Run `test_common_draft_survives_per_sounding_covariance` and `test_difference_quantile_never_labels_absolute_depth` on the base before implementing the estimator. Capture the actual RED output. Each test must exercise the future public class or function, with explicit expected numbers or verdicts. Follow with tests for record shape, replay determinism, immutable inputs, absent channels and the demo logger chain.

## Synthetic-truth fixtures

For z=c t cosθ/2 + heave, c=1500, t=0.1, θ=0, σ_t=0.001 s, σ_heave=0.2 m, independent, expect vertical variance 0.6025 m². With corr(t,heave)=+0.5 expect 0.7525 m². Check off-diagonal sign in a turn and rotate ellipse through 90°. Compare a finite-difference derivative with analytic rays, and Monte Carlo covariance within 5% for 50000 offline draws in a near-linear fixture. For 39 blocks with sorted synthetic scores 0.1,0.2,...,3.9 expect q=3.8. Replay identical pings as one block. Assert they add zero support. A shared 2 m draft error cancels on crosslines and survives in the individual sounding covariance. Score undercoverage after regime shift, missing lag uncertainty, and class too small.

Use fixed construction parameters, a local random generator seeded 17001 for development and disjoint seeds 27001 through 27020 for final injection trials. Preserve input hashes. Split fit and holdout by line/site/time block with a footprint buffer. Confirm in a test that the fit receives no holdout IDs. Treat correlated samples in an ensemble or trace as one evidence block. Use a guard reader to reject future records in live replay. Report p95 process time and high-water working memory against the measured arrival interval on a one-core ship PC.

## Validation target and falsifier

Use independently surveyed check patches and DCDB crossing lines (V1/V2), plus correlated simulated pose, clock and SV errors. Compare with fixed manufacturer uncertainty and independence-only propagation. Target 90 to 98% coverage for nominal 95% on unseen cruise blocks, mean interval width ≤1.25× the narrowest baseline attaining that coverage, with sample counts and binomial intervals. Reject calibration if outer beams under-cover, bins have too few independent blocks or repeating a line boosts the calibration count.

**INFERRED, lead to verify.** V1/V2 means NCEI DCDB and R2R with independent surveyed check depths. Confirm position/datum, calibration covariance and independent line/site membership. These are later validation candidates. Do not fetch sonar data to the Mac. Synthetic unit acceptance and real-cruise validation have separate receipts.

## Module contract and platform

Own the estimator, its documented input adapter and transform, tests, one offline-safe logger config `contrib/deepsignal/configs/sounding_uncertainty_demo.yaml`, and `contrib/deepsignal/docs/sounding_uncertainty.md`. The sample connects a local Reader to the Transform to a local text output with synthetic input built from this module’s own fixtures. Test the config by loading its class/module declarations and running its normal record path on a fixture. Document each knob's unit, expected range, example, and first check after an alarm. Respond to the desk usability checklist or mark an item N/A with a reason. No browser or GPU.

## Acceptance (from the fork root on Linux)

The first command must be RED before estimator code, then pass with both named tests and the rest of the suite. The second exits zero. The third prints True using the module's installed environment.

```sh
python3.12 -m unittest discover -s contrib/deepsignal/test/sounding_uncertainty -t . -v
```

```sh
python3.12 -m flake8 --config .flake8 contrib/deepsignal/sounding_uncertainty contrib/deepsignal/test/sounding_uncertainty
```

```sh
python3.12 -c "import numpy, scipy; assert (numpy.__version__, scipy.__version__) == ('2.2.6', '1.15.3'); print(True)"
```

Record the exact tested fork SHA. The lead's subsequent gate checks that same SHA and requires a complete receipt with `__END__` and no unexpected FAIL. Science targets need a separate blocked-holdout report.

## Scope

Only `contrib/deepsignal/sounding_uncertainty/**`, `contrib/deepsignal/test/sounding_uncertainty/**`, `contrib/deepsignal/docs/sounding_uncertainty.md`, `contrib/deepsignal/configs/sounding_uncertainty_demo.yaml` and missing empty package markers. The requirements pins belong under the module. Check the config load path, old and current Transform imports, existing field consumers and logger output serialization. Consume upstream fields through schema adapters. A standalone demo can supply those same fields. Any integration with shared factors imports the versioned API when available.

## Trust boundaries and data integrity

D-SHIP1 is listen-only. Accept existing operator-distributed UDP through a core reader, complete public-format file tails when supported, or local archives. No module socket, vendor subscription, instrument query, configuration or triggering. Validate version, units, timestamps, frame, datum, finite numeric values, bounds and ancestry before estimation. Bound record counts and memory before allocation, count invalid/duplicate/partial inputs, report stale or unsupported inputs as missing. A short tail read waits for a complete record. A torn archive record is reported. No extrapolation across a file gap. Reject a prefix collision. A test must show the input bytes/fields and original timestamp survive unchanged.

Use the evidence graph: trace each fit to raw channels, calibration, clock, navigation and parent fits. Collapse duplicates and keep covariance for shared errors. Science feature scores have independent QC. Use GOOD/1, SUSPECT/3, FAULT_LIKELY/4, AMBIGUOUS/3, UNCORRECTABLE/4 and POSTHOC_REVIEW/2 as appropriate. An obscured cause is AMBIGUOUS. Score, support/persistence and a plain explanation accompany every flag. Only independent post-cruise evidence can qualify a CORRECTABLE proposal for #56. A named allowlisted reviewer approves any reversible ledger correction at a trusted checkpoint. This module produces derived observations only.

## Non-goals and banned

No survey-grade certification, automatic sounding rejection, new motion alignment service or use of crosslines as absolute depth truth. No core changes or global dependency changes. No loosened/skipped tests, silent errors or unrelated refactors. No writes outside module scope and its dedicated scratch during the build.

## Stop rule and result

If no change is needed, report the evidence. After two red fix rounds report the remaining failure to the lead. For an unverified format version, disable that version and continue with the documented input contract. Report within 30 lines.

- Head SHA and short diff:
- RED test names and actual output:
- Linux acceptance tails, gate receipt SHA256/verdict if run:
- Synthetic truth, baseline, achieved error/coverage, ambiguity and resource use:
- Real evidence checked, remaining inferred leads and limitations:
