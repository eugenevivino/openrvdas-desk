You are building ONE module for the DeepSignal overlay on OpenRVDAS, on Eugene's own fork. Work only in this repository (eugenevivino/openrvdas). Do NOT touch, open pull requests against, or push to OceanDataTools or any upstream repository. Nothing here is sent upstream.

Branches: create branch `deepsignal/p2-weighted-depth` from commit `3b4b76e` (the contrib master tree; it is in this fork's history, for example `git merge-base origin/deepsignal/vector-wind origin/deepsignal/instrument-history`) (if `deepsignal/p2-weighted-depth` already exists on origin, check it out instead). Commit your work on that branch only, with one clear commit message, and leave it pushed to origin `deepsignal/p2-weighted-depth`. Do not touch any other branch, `dev` or `master`. If you cannot push, leave the commit on the branch in your task and say so.

Environment notes: Python only; Node is not needed. Use `python3.12` if it exists, otherwise `python3` (3.11 or newer). If pytest is missing use `python3 -m unittest`. If flake8 is missing, `pip install flake8` into a throwaway venv and say you did. PyYAML is already an OpenRVDAS dependency. You may add only the pinned `numpy==2.2.6` and `scipy==1.15.3` in the module-local requirements file the brief names, and must say so. No network.

YOUR LANE: cloud scaffolding only. Write the record contract, synthetic-truth fixtures and the failing tests the brief names, plus stubs that raise NotImplementedError for the estimator. Paste the RED output. Do NOT implement the estimator math: a Mac Astra session does that next on the same branch. Push the branch with the RED receipt in the commit message. Run every acceptance command at the end and paste the tails. Report under 40 lines: files changed, test names, RED then GREEN tail, acceptance results, any design point you disagree with (do not change a design silently), what you verified versus inferred, and what must run outside the sandbox.

Stop rule: two fix rounds still red means stop and report.

The full brief follows.

----------------------------------------------------------------
# Brief: p2-weighted-depth (Quality-weighted depth)

- Decision: reserved #170, D-SHIP1, D-FUSE1, D-REAN1 and D-REAN2. Research status BRIEFED.
- Risk tier: medium (new contrib transform and derived fields, independent math review and Linux gate).
- Module: `weighted_depth` only. Branch `deepsignal/p2-weighted-depth`. Base: fork contrib/master tree at `3b4b76e`.
- Lane: cloud Sol medium for record scaffolding, synthetic fixtures and RED tests only. Hand the same branch and RED receipt to mac `gpt-6.2-astra`, effort high, for estimator code and reviewable numerical evidence. Sequential owners.
- Mac scratch path: `/private/tmp/deepsignal/p2-weighted-depth/` only. Fresh session per lane, under 40 turns.
- Upstream home: openrvdas_contrib, fork only. Linux Python 3.12, CPU. Estimator dependencies pinned `numpy==2.2.6` and `scipy==1.15.3` in a module-local requirements file.
- Value (techs/science/shore): 5/5/4. Mode: live and causal replay. Method: NOVEL.
- Depends on in use: #113 geometry, #139 EM summaries, #141 consensus, #142 time alignment, #145 ADCP. #56 is downstream only. Synthetic tests and the standalone logger demo use the field contract below.

## Goal

When the bottom picks separate, show a depth with its uncertainty, each instrument’s contribution and whether the evidence can single out a cause.

## Background facts

The contrib base carries the older Transform API. Use OpenRVDAS Transform and standard reader records with the import-compatibility pattern already used by the overlay. The loadable class is `WeightedDepthTransform`, module `contrib.deepsignal.weighted_depth.transform`. Accept dicts and DASRecords with timestamp and fields, lists of either, or None. Pass None through. Preserve incoming record and event timestamps, raw fields and existing QC. A new derived record carries its own provenance.

At each 1 s epoch map #139 `MB_NadirDepth`, `MB_PingTime`, `MB_ValidBeamFraction`, HFDepth/LFDepth or EK/EA bottom, #145 `ADCP_BTDepth`, `ADCP_BTGood`, and an optional SBP first seabed return to metres below the waterline. For SBP use draft + c_water × TWT/2 only after trace delay, heave and water-path speed are known. Use H/L channels from one head as siblings. Read #141 `DEPTH_Consensus`, `DEPTH_OddOne`, `DEPTH_LostBottom` and `DEPTH_Stale` as baseline/context. Never ingest the median as an extra sonar. Configured age limits follow native ping/ensemble intervals. Revelle or Sikuliaq EM plus a concurrent echo or PD0 feed can pilot it. NBP1406 tests depth field mapping.

## Design and estimator contract

For epoch t, let y_it be waterline-referenced depth with chart datum/tide and the local slope displacement gᵀΔr_i accounted for when known. Use independent terrain to estimate g, otherwise add footprint slope uncertainty or withhold the pair. Write y_it = d_t + b_i + U_i a_t + e_it. Use a locally linear depth/rate process, b_i slowly varying by installation epoch, and R = UCUᵀ + diag(v_i + s²_geom,i). The proposed construction learns private noise from differences between independent families without using the fused depth as truth. Depth consensus #141 supplies a baseline alongside the new estimate. The three-corner variance identity is established. The proposed contribution is its footprint-matched, family-covariance-adjusted combination with attribution gates. On matched, stable overlaps form V_ij from squared robust scales of detrended pair differences. Fit v≥v_floor by weighted nonnegative least squares to V_ij − (U_i−U_j)C(U_i−U_j)ᵀ − s²_geom,ij = v_i + v_j. Weights are effective counts of overlap blocks, capped equally per family pair. For three families v_1=(V'12+V'13−V'23)/2 in the noiseless moment limit. Fit biases from robust means of the same contrasts, y_i−y_j ≈ b_i−b_j. With only two families retain prior private variances.

Estimate depth and rate with Huber loss (cutoff 1.5 standardized units). For positive-definite R minimize the sum of Huber losses of R^(-1/2)(y−Hx) (symmetric square root; see Math review fixes) plus half the Gaussian prior quadratic. Iterate QR weighted least squares up to 10 times or until relative state change <1e−6. The prior mean for depth/rate advances by a constant-velocity step using elapsed record time. Configure acceleration spectral density in m²/s³ and propagate with Q=q[[Δt³/3,Δt²/2],[Δt²/2,Δt]]. Calibration floors and process settings belong to the vessel profile, with explicit labeled demo values. Zero-centered Gaussian bias priors and variance floors come from declared calibration uncertainty. Learn only on previous independent clean blocks, freeze on alarms and runtime or datum changes. Use a rolling last 120 matched blocks, minimum 20 per edge, robust scale 1.4826 MAD and documented process variance per second. A connected comparison graph identifies relative offsets up to a constant. Private variances require full column rank of the pair-sum matrix (an odd cycle in each connected component). Fix a weighted zero-sum gauge for relative output. Absolute bias needs an independent depth reference. Grid priors may annotate suspicion and uncertainty but never decide which of two sonars is wrong. For a grid with independent survey lineage and datum use a capped weak depth prior only after sonar agreement, cap its precision at 0.1 of sonar-only precision. Flag a family on nonoverlapping 10 s mean contrasts, with their correlation-adjusted standard errors, at |leave-family-out innovation|/predicted SD >3 with two other independent families agreeing within 2 SD.

Own the small shared `factors.py` here. Expose `solve_linear(y,H,R,m,P,cutoff=1.5)` returning state, covariance, effective rank and residuals, and an observation record with source, event time, uncertainty, footprint and immutable parent IDs. Whiten by independent blocks, collapse exact ancestry duplicates, and return a reason on singular covariance. A callable family-contrast estimator is tested independently of logger wrapping. Process clocked events once, ignoring already-used samples for training counts. Use deterministic calibration/bias initialization from configuration and keep relative and anchored outputs distinct.

Configure each source as {field, time_field, role, family, raw_parent_fields, offset_m, datum, max_age_s, private_sd_m, shared_loadings, footprint_m}. Require an externally specified draft sign and reference surface. ADCP_BTDepth from #145 and MB_NadirDepth from #139 are already below waterline. Check single-beam DPT reference and any already applied offset. ADCP_BTGood is #145's fraction expressed as percent, not its individual-beam 0x0600 quality bytes. Do not derive a second ADCP source by averaging those bytes. A local chart grid must come with tide/datum, cell size, source IDs and vertical uncertainty. A live logger consumes the mapped products of existing UDP/file readers. Offline replay uses the same transform. No new binary decoder in this branch.

Estimate the covariance of the fused state from the weighted information matrix, inflate for outlier downweighting and validate coverage on independent fixtures. Bound the predictor across elapsed time and segment resets. Store learned weights once per epoch, never rebuild a noise estimate from the residual it just explained. For a held-out contrast, propagate the covariance of (y_i−d_without_i) including shared loadings. Write held-out score missing when the held-out families have no relevant support. The demo must print a common-depth estimate plus either evidence of a source-specific discrepancy or the plain reason attribution is ambiguous.

**Result fields.** Prefix each of `Depth_m`, `SD_m`, `RelativeBias_m`, `PrivateVariance_m2`, `FamilyWeights`, `HeldOutZ`, `Datum`, `AnchorId` with `WDEP_`. Also emit prefixed `Score`, `Verdict`, `Reason`, `Support`, `Persistence`, `SourceIds`, `Stale` and `Excluded`. Units, nullability, shapes, record/interval keys and score direction go in the module docs. Explain the first check in watch language. Use record time for live persistence. An alert requires 60 s continuously over threshold and clears after 60 s below 75% of threshold. A gap resets the timer. Replay must be causal and deterministic. Score is the largest supported absolute leave-one-family-out standardized residual.

The watch can distinguish a failing bottom lock from all heads seeing a real bank. Shore gets relative bias histories and measured weight changes. Common draft errors, shared heave, mobile bottom, nonsynchronous footprints and a grid made from this survey defeat absolute attribution. Return AMBIGUOUS on an unresolved two-family split. A single fresh family gives an explicitly single-source estimate with prior uncertainty.

## Math review fixes (binding; `research/2026-11-18-sonar-math-review.md`, cdb7efb)

These override anything above or below that conflicts. Each added test is part of "Failing test first".

1. **Whitening (P1).** Use the symmetric whitener R^(-1/2) (eigendecomposition of R), not the Cholesky factor L^(-1), before componentwise Huber loss, so the fit is invariant to row order. Test `test_row_permutation_invariance`: depths (4,0) m, unit variances, correlation 0.8, diffuse prior, cutoff 1.5; fused depth must be identical (to 1e-9) for both row orders. With Cholesky the two orders give 3.5 and 0.5 m.
2. **Pair-variance model (P1).** The pair equation is V'_ij = v_i + v_j - 2 Cov(e_i, e_j). Private variances are identified only when residual cross-covariances are known (zero by documented independence, or modelled). Otherwise mark private variances UNIDENTIFIED, keep prior variances and withhold attribution. When a residual cross-covariance is known (documented or modelled), carry it into the fusion as well: R = D + U C U^T + K, where K holds the known off-diagonal residual covariances. Test `test_known_residual_covariance_in_fusion`: two unit-variance sensors measuring one depth with known Cov 0.8 m^2, diffuse prior, residuals inside the Huber cutoff: fused depth variance must equal (1+0.8)/2 = 0.9 m^2 (diagonal R would give 0.5). Test `test_hidden_correlation_withholds`: unit private variances with Cov(e1,e2)=0.8 m^2 must not report the naive (0.2,0.2,1.8) m^2 as learned.
3. **Misfit gate (P1).** After the nonnegative pair fit, test its residual against block-bootstrap sampling uncertainty of the pair moments. Gate: B = 999 block-bootstrap resamples over at least 30 independent blocks per pair (fewer blocks: UNIDENTIFIED); misfit is material when the weighted pair-fit residual exceeds the 95th percentile of its bootstrap distribution. On material misfit keep prior variances, set attribution AMBIGUOUS and say why. A variance floor alone never counts as a fit. Tests: `test_inconsistent_moments_gate` gives the pair moments (1,1,4) m^2 (unconstrained hats (-1,2,2)) a bootstrap standard error of 0.1 m^2 per pair (fixture: 400 blocks) and must trip the gate; `test_noisy_moments_no_gate` gives the same moments a standard error of 2 m^2 per pair (fixture: 30 short blocks) and must not trip it, falling back to the nonnegative fit with wide intervals.
4. **Scale estimator (P2).** Recover variances from the plain second central moment of detrended pair differences after removing only points beyond 5 scaled MADs of the median (the outlier screen), not from squared scaled MADs (biased for non-Gaussian noise: Uniform(0,1) pairs give 0.18857 vs true 1/6). If a narrower trim is configured, divide by its consistency factor for the declared noise law, computed by simulation and stored with the config; an uncalibrated trim is refused (a |X-Y| <= 0.5 trim gives 5/72, not 1/6). Test `test_uniform_noise_variance`: independent Uniform(0,1) pairs, 20000 samples, estimate within 2 percent of 1/6 (the 5-MAD screen, about 2.17, removes nothing here). Test `test_uncalibrated_trim_refused`.
5. **Identifiability (added test).** `test_even_cycle_unidentified`: a connected four-family cycle overlap graph (1-2, 2-3, 3-4, 4-1) yields UNIDENTIFIED private variances, because the pair-sum matrix is rank deficient.

Simulation targets (fault recall, Monte Carlo covariance error, reflector recall, false-repeat rate) are acceptance claims only once the run's realized outputs are pasted in the report; the review could not verify them from the brief.

## Failing test first

Add `contrib/deepsignal/test/weighted_depth/test_estimator.py`. Run `test_pair_contrasts_recover_private_variances` and `test_duplicate_head_cannot_outvote_two_families` on the base before implementing the estimator. Capture the actual RED output. Each test must exercise the future public class or function, with explicit expected numbers or verdicts. Follow with tests for record shape, replay determinism, immutable inputs, absent channels and the demo logger chain.

## Synthetic-truth fixtures

Use identity U or explicit shared loading vectors. With corrected pair variances (5,10,13) m² for pairs (12,13,23), recover private variances (1,4,9) m². For independent unbiased y=(100,102,97) m and these variances, high-cutoff Gaussian mode gives d=(100+102/4+97/9)/(1+1/4+1/9)=100.122449 m (diffuse depth prior). Duplicate the first family with the same raw ID: assert identical answer and SD. For b=(0,+2,0) m add an independent anchor to test absolute bias, remove it to test relative-only. Simulate 6000 one-second epochs at 100 m, three family SDs (0.10,0.20,1.00) m, a 90 s +2 m fault in the second, a 10 m real bank seen by all, a stale interval, a 1 m shared draft error and a coarse grid sourced from the first. Separate learning, fault and score blocks. Test a two-family tie and prior-only startup.

Use fixed construction parameters, a local random generator seeded 17001 for development and disjoint seeds 27001 through 27020 for final injection trials. Preserve input hashes. Split fit and holdout by line/site/time block with a footprint buffer. Confirm in a test that the fit receives no holdout IDs. Treat correlated samples in an ensemble or trace as one evidence block. Use a guard reader to reject future records in live replay. Report p95 process time and high-water working memory against the measured arrival interval on a one-core ship PC.

## Validation target and falsifier

Use NBP1406 as a field-plumbing check, then independent surveyed check depths on held-out line blocks (V2/V3). Inject a +2 m step, unequal noise, a sloping bank and duplicate channels. Compare with #141 median at equal availability. Target ≥20% lower held-out RMSE on unequal-noise fixtures and ≥90% step recall after 60 s, with ≤1 false attribution per 10 h of clean causal replay. Falsify if a copied channel tightens the interval or grid agreement resolves an unanchored split.

**INFERRED, lead to verify.** V2/V3 means R2R cruise manifests and NBP1406 records, independent hydrographic check soundings and GMRT provenance. Confirm grid lineage, concurrent timestamped heads and datum. These are later validation candidates. Do not fetch sonar data to the Mac. Synthetic unit acceptance and real-cruise validation have separate receipts.

## Module contract and platform

Own the estimator, its mapped-field transform, tests, one offline-safe logger config `contrib/deepsignal/configs/weighted_depth_demo.yaml`, and `contrib/deepsignal/docs/weighted_depth.md`. The sample connects a local Reader to the Transform to a local text output with synthetic input built from this module’s own fixtures. Test the config by loading its class/module declarations and running its normal record path on a fixture. Document each knob's unit, expected range, example, and first check after an alarm. Respond to the desk usability checklist or mark an item N/A with a reason. No browser or GPU.

## Acceptance (from the fork root on Linux)

The first command must be RED before estimator code, then pass with both named tests and the rest of the suite. The second exits zero. The third prints True using the module's installed environment.

```sh
python3.12 -m unittest discover -s contrib/deepsignal/test/weighted_depth -t . -v
```

```sh
python3.12 -m flake8 --config .flake8 contrib/deepsignal/weighted_depth contrib/deepsignal/test/weighted_depth
```

```sh
python3.12 -c "import numpy, scipy; assert (numpy.__version__, scipy.__version__) == ('2.2.6', '1.15.3'); print(True)"
```

Record the exact tested fork SHA. The lead's subsequent gate checks that same SHA and requires a complete receipt with `__END__` and no unexpected FAIL. Science targets need a separate blocked-holdout report.

## Scope

Only `contrib/deepsignal/weighted_depth/**`, `contrib/deepsignal/test/weighted_depth/**`, `contrib/deepsignal/docs/weighted_depth.md`, `contrib/deepsignal/configs/weighted_depth_demo.yaml` and missing empty package markers. The requirements pins belong under the module. Check the config load path, old and current Transform imports, existing field consumers and logger output serialization. The reusable factors API resides inside this module.

## Trust boundaries and data integrity

D-SHIP1 is listen-only. Accept existing operator-distributed UDP through a core reader, complete public-format file tails when supported, or local archives. No module socket, vendor subscription, instrument query, configuration or triggering. Validate version, units, timestamps, frame, datum, finite numeric values, bounds and ancestry before estimation. Bound record counts and memory before allocation, count invalid/duplicate/partial inputs, report stale or unsupported inputs as missing. A short tail read waits for a complete record. A torn archive record is reported. No extrapolation across a file gap. Reject a prefix collision. A test must show the input bytes/fields and original timestamp survive unchanged.

Use the evidence graph: trace each fit to raw channels, calibration, clock, navigation and parent fits. Collapse duplicates and keep covariance for shared errors. Science feature scores have independent QC. Use GOOD/1, SUSPECT/3, FAULT_LIKELY/4, AMBIGUOUS/3, UNCORRECTABLE/4 and POSTHOC_REVIEW/2 as appropriate. An obscured cause is AMBIGUOUS. Score, support/persistence and a plain explanation accompany every flag. Only independent post-cruise evidence can qualify a CORRECTABLE proposal for #56. A named allowlisted reviewer approves any reversible ledger correction at a trusted checkpoint. This module produces derived observations only.

## Non-goals and banned

No replacement of #141, live bias correction to raw sounders, new grid service or seabed grid builder. No core changes or global dependency changes. No loosened/skipped tests, silent errors or unrelated refactors. No writes outside module scope and its dedicated scratch during the build.

## Stop rule and result

If no change is needed, report the evidence. After two red fix rounds report the remaining failure to the lead. For an unverified format version, disable that version and continue with the documented input contract. Report within 30 lines.

- Head SHA and short diff:
- RED test names and actual output:
- Linux acceptance tails, gate receipt SHA256/verdict if run:
- Synthetic truth, baseline, achieved error/coverage, ambiguity and resource use:
- Real evidence checked, remaining inferred leads and limitations:
