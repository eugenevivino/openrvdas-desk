# Brief: p2-seep-repeatability (Seabed-anchored flares and repeat-pass strength)

- Decision: reserved #174, D-SHIP1, D-FUSE1, D-REAN1 and D-REAN2. Research status BRIEFED.
- Risk tier: medium (new contrib transform and derived fields, independent math review and Linux gate).
- Module: `seep_repeatability` only. Branch `deepsignal/p2-seep-repeatability`. Base: fork contrib/master tree at `3b4b76e`.
- Lane: cloud Sol medium for record scaffolding, synthetic fixtures and RED tests only. Hand the same branch and RED receipt to mac `gpt-6.2-astra`, effort high, for estimator code and reviewable numerical evidence. Sequential owners.
- Mac scratch path: `/private/tmp/deepsignal/p2-seep-repeatability/` only. Fresh session per lane, under 40 turns.
- Upstream home: openrvdas_contrib, fork only. Linux Python 3.12, CPU. Estimator dependencies pinned `numpy==2.2.6` and `scipy==1.15.3` in a module-local requirements file.
- Value (techs/science/shore): 4/5/5. Mode: offline water-column replay. Method: NOVEL.
- Depends on in use: #91 flare candidates, #139 ping and bottom reference, #142 timing/motion, #144 transmit timeline and #145 current-profiler context. Raw #MWC is essential. Synthetic tests and the standalone logger demo use the field contract below.

## Goal

Show whether repeat passes support a flare rising from the same seabed location, and whether its relative acoustic strength changed under comparable conditions.

## Background facts

The contrib base carries the older Transform API. Use OpenRVDAS Transform and standard reader records with the import-compatibility pattern already used by the overlay. The loadable class is `SeepRepeatabilityTransform`, module `contrib.deepsignal.seep_repeatability.transform`. Accept dicts and DASRecords with timestamp and fields, lists of either, or None. Pass None through. Preserve incoming record and event timestamps, raw fields and existing QC. A new derived record carries its own provenance.

Companion multibeam water-column and bathymetry pings are essential. Per georeferenced voxel retain time, height above bottom, footprint, range, beam angle, local median and noise variance, insonified volume, gain/TVG, runtime/head/frequency and coverage mask. Pair RR2214 or SKQ202217T files for geometry only (V1). Optional EK80 adds calibrated band volume backscatter where footprints overlap. Optional ADCP adds quality-screened earth-frame currents per height from PD0/UHDAS and relative echo/correlation. Distinct frequencies are measured, not inferred from instrument count. V5 supplies candidate labeled sites.

## Design and estimator contract

For bottom anchor a and rise speed w>0 define a tube center at height h as x(h)=a+∫₀ʰ u(s)/w ds, using quasi-steady measured horizontal current u. Without currents grid constant horizontal tilt v with a bounded prior. K_j is the fraction of voxel footprint inside a tube broadened by beamwidth, current/time and registration uncertainty. For local background-subtracted intensity y_j with variance s²_j compare earth-fixed K, ship/beam-fixed sidelobe K and broad layer K on the same observed voxels. Under model y_j=A K_j+ε_j, A≥0 with half-normal prior scale τ, Gaussian block-whitened errors, Â=max(0,Σ K y/s²)/(Σ K²/s²+τ⁻²). Improvement in penalized fit is ½Â²(Σ K²/s²+τ⁻²). Estimate one amplitude per pass/band, with the earth anchor shared across passes. Average powers in linear units.

Fit anchor, width and tilt on discovery line only, with uniform location prior over observed bottom and predeclared finite grids. Use a w grid of 0.1, 0.2 and 0.4 m/s for shape only. On a crossing line fix the predicted anchor/uncertainty tube and test improvement over the best null including the beam-fixed and layer alternatives. Set search-adjusted threshold from maximum scores on whole-line block shifts in depth-matched terrain. For repeat strength Q* integrate excess linear volume scattering over a covered horizontal slice at a fixed height, e.g. Σ (s_v−background) Δarea with overlap-deduplicated area weights, and give coverage and block-bootstrap interval. For EM counts without a verified calibration report a within-setting relative index (normalized linear power × area) only. A flux proxy can be Q* times an independently measured rise speed, with its units stated as an acoustic index. A rise speed selected by template search is inferred from shape and cannot supply an independent velocity. No conversion to gas mass or volume rate from these data alone.

Implement bounded streaming intake of archived #MWC plus companion #MRZ for one declared public KMALL version, as well as decoded voxel rows. Join by head/system, ping counter, swath, fan and event time, then compute sample range, footprint and terrain-relative height. Audit sample scale/TVG for that version. Process in tiles (≤256×256 horizontal cells, ≤128 heights per tile), stream sparse visited voxels and cap input/decompressed sizes. Never allocate a cruise cube. Optional EK/ADCP inputs arrive as local decoded fields with frequency/frame/calibration metadata. Segment by runtime hash, retain coverage, store only score/evidence records via normal logger return. Defaults: test a slice 10 to 15 m above bottom where visible, ≥80% common coverage to quote a matched repeat index, independent repeat heading difference ≥30° modulo 360° plus spatially distinct ray paths.

Public KMALL 410224 #MWC with beamPointAngReVertical_deg, startRangeSampleNum, detectedRangeInSamples, numSampleData, sampleFreq_Hz, soundVelocity_mPerSec, amplitudes, TVG function/offset and transmit sector geometry, plus #MRZ XYZ bottom, timing, sound speed, geolocation and orientation. Lead to verify (INFERRED): field names/offsets in supported version, amp scale (including signed dB coding), sample/TVG correction, partial fan and sidelobe exclusion limits. Echo-free/noise regions must be observable. Use earliest local bottom slant range for conservative sidelobe masking. The resulting near-bottom blind zone can preclude a root location. State when footprint extrapolation supplies the root and withhold a confirmed anchor in that case. Reject mixed signatures and density estimates from uneven insonification.

Default tube widths one/two beam footprints, anchor spacing one footprint over covered bottom, fallback tilt range ±0.5 horizontal m/vertical m on a stated grid. Penalize variable-width fits by threshold calibration on the entire search. Null beam template is fixed in receive beam/range coordinates, layer template follows a constant-depth band across beams. Fit template shapes on discovery data, compare amplitudes on the independent pass without relocating the anchor. Use ≥199 stratified circular shifts or matched negative lines with the entire search repeated, and report an empirical tail probability (1 + count of null maxima at least as large as the observed maximum)/(1 + number of shifts). Require p≤0.05, repeat support and gain over both competing templates to label a repeat. Treat one-line anchors as candidates. Fit each instrument's amplitude in its own units and covariance block. A PD0 plume return cannot serve as an independent current estimate without a clean water-velocity bin. Compute calibrated s_v in linear m⁻¹. Q* has units m and Q*w m²/s. Emit normalized EM index in labeled relative units and withhold cross-setting comparison. Insufficient independent blocks means no CI.

**Result fields.** Prefix each of `Anchor_EN_m`, `AnchorSD_m`, `FeatureScore`, `NullScore`, `RepeatLines`, `Coverage`, `RelativeIndex`, `IndexUnits`, `HeightBand_m` with `FLARE_`. Also emit prefixed `Score`, `Verdict`, `Reason`, `Support`, `Persistence`, `SourceIds`, `Stale` and `Excluded`. Units, nullability, shapes, record/interval keys and score direction go in the module docs. Explain the first check in watch language. Count independent trace/line support in Persistence, with its unit. Emit a result only for the documented processing window. Score is repeat gain over the best null. Include search-adjusted p and observable-root status.

Techs can check whether a promising feature survives the next crossing. Scientists get candidate coordinates, repeatability, detection footprint and a bounded comparison of strength. Needs intersecting independently navigated headings and a resolved base, calibrated coverage for quantitative comparisons, and background observations on both sides. Fish schools, turbidity plumes, bottom sidelobes, current variability, blind zones near bed and dependent EK/EM picks can defeat identification. One line is a candidate. An unobserved base remains unresolved.

## Math review fixes (binding; `research/2026-11-18-sonar-math-review.md`, cdb7efb)

These override anything above or below that conflicts. Each added test is part of "Failing test first".

1. **Heading wrap (P1).** Line heading difference is abs(((h2 - h1 + 180) mod 360) - 180). "Opposing or perpendicular" requires that difference >= 30 degrees. Test `test_heading_wrap`: 350 and 10 degrees differ by 20 degrees and do not qualify.
2. **Correlated voxels (P1).** With voxel covariance R: D = K^T R^-1 K + tau^-2, A_hat = max(0, K^T R^-1 y)/D, gain = A_hat^2 D / 2. Never use diagonal weighting when R has off-diagonal terms. Test `test_correlated_voxel_gain`: the review's correlation-0.5 fixture gives gain 8/3 (diagonal weighting would give 4).
3. **Null distribution.** Null shifts must preserve each line's spatial correlation while breaking cross-pass alignment. p = (1 + count(null max >= observed)) / (1 + n_shifts). Test `test_null_p_value`: 199 shifts with 9 ties-or-exceedances give p = 0.05; 10 give 0.055.
4. **Added tests.** `test_zero_template_support` (no support: missing value with reason) and `test_near_zero_first_pass` (relative index with a near-zero first-pass value is reported as undefined, never a huge ratio).

Simulation targets (fault recall, Monte Carlo covariance error, reflector recall, false-repeat rate) are acceptance claims only once the run's realized outputs are pasted in the report; the review could not verify them from the brief.

## Failing test first

Add `contrib/deepsignal/test/seep_repeatability/test_estimator.py`. Run `test_repeat_anchor_beats_beam_fixed_ghost` and `test_missing_coverage_is_missing_strength` on the base before implementing the estimator. Capture the actual RED output. Each test must exercise the future public class or function, with explicit expected numbers or verdicts. Follow with tests for record shape, replay determinism, immutable inputs, absent channels and the demo logger chain.

## Synthetic-truth fixtures

Use seabed at 100 m, anchor (0,0), opposing or perpendicular independent lines, beam footprint 5 m, current (0.05,0) m/s, rise 0.2 m/s. At 20 m above bed the center must be (5,0) m. For y=(2,2), K=(1,1), s=1 and τ⁻²=0 (fixture only) expect Â=2 and gain 4. Inject a beam-angle streak on both passes that georeferences to different bottom positions, and a layer covering the full transect. Mask bottom contamination and incomplete repeat coverage, inject two calibrated repeat strengths 1:2 and test the ratio. One line, incompatible gains, bad navigation, no base, fixed-current mismatch and shared EK/EM parents must carry explicit limitations.

Use fixed construction parameters, a local random generator seeded 17001 for development and disjoint seeds 27001 through 27020 for final injection trials. Preserve input hashes. Split fit and holdout by line/site/time block with a footprint buffer. Confirm in a test that the fit receives no holdout IDs. Treat correlated samples in an ensemble or trace as one evidence block. Compare blind feature scores by whole line and count easy abstentions as misses.

## Validation target and falsifier

Compare against #91 single-pass vertical coherence on blinded known-seep and searched negative transects (V5), using independent imagery/ROV evidence where available. Inject slant-sampled plumes, streaks fixed to beam, moving schools and unequal sampling. Gate ≥80% repeat-pass recovery within one effective footprint at ≤1 false repeat per 100 surveyed km, and ≤15% relative-index bias for known strength ratios on matched footprints. Reject if beam-fixed ghosts survive heading reversal or missing coverage appears as zero flux.

**INFERRED, lead to verify.** V1/V5 means NCEI WCSD+DCDB matched RR2214 EM124 ping file 0578 for plumbing, US Atlantic margin seep inventory with repeat water-column lines and independent ROV observations (e.g. Blake Ridge) for scoring. Confirm heading, base visibility, gain/beam calibration and searched negatives. These are later validation candidates. Do not fetch sonar data to the Mac. Synthetic unit acceptance and real-cruise validation have separate receipts.

## Module contract and platform

Own the estimator, its documented input adapter and transform, tests, one offline-safe logger config `contrib/deepsignal/configs/seep_repeatability_demo.yaml`, and `contrib/deepsignal/docs/seep_repeatability.md`. The sample connects a local Reader to the Transform to a local text output with synthetic input built from this module’s own fixtures. Test the config by loading its class/module declarations and running its normal record path on a fixture. Document each knob's unit, expected range, example, and first check after an alarm. Respond to the desk usability checklist or mark an item N/A with a reason. No browser or GPU.

## Acceptance (from the fork root on Linux)

The first command must be RED before estimator code, then pass with both named tests and the rest of the suite. The second exits zero. The third prints True using the module's installed environment.

```sh
python3.12 -m unittest discover -s contrib/deepsignal/test/seep_repeatability -t . -v
```

```sh
python3.12 -m flake8 --config .flake8 contrib/deepsignal/seep_repeatability contrib/deepsignal/test/seep_repeatability
```

```sh
python3.12 -c "import numpy, scipy; assert (numpy.__version__, scipy.__version__) == ('2.2.6', '1.15.3'); print(True)"
```

Record the exact tested fork SHA. The lead's subsequent gate checks that same SHA and requires a complete receipt with `__END__` and no unexpected FAIL. Science targets need a separate blocked-holdout report.

## Scope

Only `contrib/deepsignal/seep_repeatability/**`, `contrib/deepsignal/test/seep_repeatability/**`, `contrib/deepsignal/docs/seep_repeatability.md`, `contrib/deepsignal/configs/seep_repeatability_demo.yaml` and missing empty package markers. The requirements pins belong under the module. Check the config load path, old and current Transform imports, existing field consumers and logger output serialization. Consume upstream fields through schema adapters. A standalone demo can supply those same fields. Any integration with shared factors imports the versioned API when available.

## Trust boundaries and data integrity

D-SHIP1 is listen-only. Accept existing operator-distributed UDP through a core reader, complete public-format file tails when supported, or local archives. No module socket, vendor subscription, instrument query, configuration or triggering. Validate version, units, timestamps, frame, datum, finite numeric values, bounds and ancestry before estimation. Bound record counts and memory before allocation, count invalid/duplicate/partial inputs, report stale or unsupported inputs as missing. A short tail read waits for a complete record. A torn archive record is reported. No extrapolation across a file gap. Reject a prefix collision. A test must show the input bytes/fields and original timestamp survive unchanged.

Use the evidence graph: trace each fit to raw channels, calibration, clock, navigation and parent fits. Collapse duplicates and keep covariance for shared errors. Science feature scores have independent QC. Use GOOD/1, SUSPECT/3, FAULT_LIKELY/4, AMBIGUOUS/3, UNCORRECTABLE/4 and POSTHOC_REVIEW/2 as appropriate. An obscured cause is AMBIGUOUS. Score, support/persistence and a plain explanation accompany every flag. Only independent post-cruise evidence can qualify a CORRECTABLE proposal for #56. A named allowlisted reviewer approves any reversible ledger correction at a trusted checkpoint. This module produces derived observations only.

## Non-goals and banned

No methane identification, absolute gas discharge, commands for another survey pass or unrestricted whole-cruise cube. No core changes or global dependency changes. No loosened/skipped tests, silent errors or unrelated refactors. No writes outside module scope and its dedicated scratch during the build.

## Stop rule and result

If no change is needed, report the evidence. After two red fix rounds report the remaining failure to the lead. For an unverified format version, disable that version and continue with the documented input contract. Report within 30 lines.

- Head SHA and short diff:
- RED test names and actual output:
- Linux acceptance tails, gate receipt SHA256/verdict if run:
- Synthetic truth, baseline, achieved error/coverage, ambiguity and resource use:
- Real evidence checked, remaining inferred leads and limitations:
