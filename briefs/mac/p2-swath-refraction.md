Mac lane job (rule 8, rule 27, rule 28). Launch through `~/bin/ds-codex` only, one DeepSignal job per Mac, RAM rule applies (hold if free RAM under 4 GB or swap over 3.8 GB).

Model and effort, named explicitly: `KALON_ALLOW_ASTRA=1 ~/bin/ds-codex -m gpt-6.2-astra -c model_reasoning_effort=high` (set KALON_ALLOW_ASTRA only for this job).
Scratch: `/private/tmp/deepsignal/p2-swath-refraction/` only (clone in `repo/`, `gc.auto=0`, `maintenance.auto=false`). Never write outside it; never touch `/private/tmp/kalon`.
Review: a separate fresh Astra session, read-only, re-derives every estimator, identifiability condition and golden value before anything merges.
YOUR LANE: estimator code. Check out `deepsignal/p2-swath-refraction` as the cloud scaffolding lane left it (RED tests present); do not weaken or rewrite those tests. Implement the math the brief specifies until they are GREEN. No sonar data on the Mac beyond trimmed snippets under 100 MB in your scratch folder, deleted after the run (Eugene, disk space).

You are building ONE module for the DeepSignal overlay on OpenRVDAS, on Eugene's own fork. Work only in this repository (eugenevivino/openrvdas). Do NOT touch, open pull requests against, or push to OceanDataTools or any upstream repository. Nothing here is sent upstream.

Branches: create branch `deepsignal/p2-swath-refraction` from commit `3b4b76e` (the contrib master tree; it is in this fork's history, for example `git merge-base origin/deepsignal/vector-wind origin/deepsignal/instrument-history`) (if `deepsignal/p2-swath-refraction` already exists on origin, check it out instead). Commit your work on that branch only, with one clear commit message, and leave it pushed to origin `deepsignal/p2-swath-refraction`. Do not touch any other branch, `dev` or `master`. If you cannot push, leave the commit on the branch in your task and say so.

Environment notes: Python only; Node is not needed. Use `python3.12` if it exists, otherwise `python3` (3.11 or newer). If pytest is missing use `python3 -m unittest`. If flake8 is missing, `pip install flake8` into a throwaway venv and say you did. PyYAML is already an OpenRVDAS dependency. You may add only the pinned `numpy==2.2.6` and `scipy==1.15.3` in the module-local requirements file the brief names, and must say so. No network.

Paste the inherited RED output first, then make it GREEN. Run every acceptance command at the end and paste the tails. Report under 40 lines: files changed, test names, RED then GREEN tail, acceptance results, any design point you disagree with (do not change a design silently), what you verified versus inferred, and what must run outside the sandbox.

Stop rule: two fix rounds still red means stop and report.

The full brief follows.

----------------------------------------------------------------
# Brief: p2-swath-refraction (Observable sound-speed error from crossing swaths)

- Decision: reserved #171, D-SHIP1, D-FUSE1, D-REAN1 and D-REAN2. Research status BRIEFED.
- Risk tier: medium (new contrib transform and derived fields, independent math review and Linux gate).
- Module: `swath_refraction` only. Branch `deepsignal/p2-swath-refraction`. Base: fork contrib/master tree at `3b4b76e`.
- Lane: cloud Sol medium for record scaffolding, synthetic fixtures and RED tests only. Hand the same branch and RED receipt to mac `gpt-6.2-astra`, effort high, for estimator code and reviewable numerical evidence. Sequential owners.
- Mac scratch path: `/private/tmp/deepsignal/p2-swath-refraction/` only. Fresh session per lane, under 40 turns.
- Upstream home: openrvdas_contrib, fork only. Linux Python 3.12, CPU. Estimator dependencies pinned `numpy==2.2.6` and `scipy==1.15.3` in a module-local requirements file.
- Value (techs/science/shore): 5/5/5. Mode: bounded live crossing check and offline reanalysis. Method: NOVEL.
- Depends on in use: #139 summaries, #140 surface consistency, #142 motion/timing, #147 casts, #161 fused profile prior. #170 provides the small factor solver when integrated. Synthetic tests and the standalone logger demo use the field contract below.

## Goal

When outer beams disagree with a second line over the same bottom, show which part of the sound-speed profile the geometry actually tests and when a new cast could settle it.

## Background facts

The contrib base carries the older Transform API. Use OpenRVDAS Transform and standard reader records with the import-compatibility pattern already used by the overlay. The loadable class is `SwathRefractionTransform`, module `contrib.deepsignal.swath_refraction.transform`. Accept dicts and DASRecords with timestamp and fields, lists of either, or None. Pass None through. Preserve incoming record and event timestamps, raw fields and existing QC. A new derived record carries its own provenance.

Full multibeam pings, profile and motion, primarily Revelle EM124 or Sikuliaq EM304. Consume full travel times and steering/sector geometry per ping, both port and starboard, independent nav/motion, tide or common vertical datum, and the applied #SVP (legacy U), distinct from the latest cast. #139 `MB_SVTransducer`, `MB_SVProbe`, `MB_RuntimeHash`, #140 `SV_Alarm`, #147 `Profile.depth_m`, `sv_ms`, `SVM_CastId`, `SVM_Quality` and #161 prior mean/covariance/ancestry inform the fit. Require observed crossings, angle diversity and profile validity epoch. Live sample ≤32 angular bins/ping over ≤128 matched cells per solve, at most once per 30 s. Full resolution post.

## Design and estimator contract

#161 owns the prior profile c₀ and external-source weighting. This row supplies a likelihood in supported profile modes. Let c(z)=c₀(z)+Σ B_k(z)α_k, at most two piecewise-linear hat functions, zero at the probe for subsurface modes. Start at the head depth. In a horizontal layer, p=sinθ/c_head, dt=dz/[c sqrt(1−p²c²)], dx=p c dz/sqrt(1−p²c²). Integrate to the observed one-way time for a documented symmetric single-sector geometry. For other supported systems use documented transmit/receive paths and motion referenced to their respective epochs. Refuse geometry whose forward model cannot reproduce vendor XYZ under the applied profile within combined ray/pose uncertainty (default 2 SD per coordinate), after confirming datum and lever arms. Decline the ray if the uncertainty needed for this check is unknown. For each pair of independent line footprints form r=(z_i−z_j)−gᵀ(x_i−x_j) with local terrain gradient g estimated outside the pair. Re-raytrace around c₀ holding measured time/steering fixed. The central difference J=∂r/∂α includes horizontal displacements on the slope.

Residual at candidate profile is r₀+Jα+Hη, with H spanning line datum, roll and timing derivatives. Estimate α~N(0,P₁₆₁), η from measured alignment covariance, using robust weighted least squares. Mark unsupported components by SVD of (I−QQᵀ)WJ P₁₆₁^(1/2), Q spanning WH, W a residual whitener. Retain singular values ≥1, meaning a prior-SD shift is visible at ≥1 observation SD along the whitened mode. Report singular vectors, posterior SD and the data-only rank. Covariance must be estimated without counting shared pings twice. Give #161 the residual likelihood (J, projected r and covariance or equivalent information pair), with a lineage ID. Reject a prior containing any of the same crossing evidence. A prior built without those lines can combine the likelihood once.

Implement the estimator and a bounded public KMALL input path. V1 supports a documented symmetric single-sector subset, or decoded rays with independently verified transmit/receive geometry. Read #MRZ and companion nav/profile/context records through a module-local adapter or an available source-compatible public decoder. Normalize to ping ID, head depth, time of flight, launch vector, pose, datum and profile. Key partial fans by system/head/swath/counter/time. Reject unsupported motion or multi-sector geometry explicitly. File tail reads only complete records. A decoder receiving bytes opens no socket. A match can space-bin within one footprint and bracket nav without extrapolation. Read the #161 prior through a config-mapped versioned record with basis covariance in (m/s)² and source hashes. A cast-only fallback is labeled with its own uncertainty and carries no #161 fusion claim.

Use public KMALL 410224 symbolic fields #MRZ twoWayTravelTime_sec, beamAngleReRx_deg, transmit tilt/sector, sounding index, x_reRefPoint_m/y_reRefPoint_m/z_reRefPoint_m, txTransducerDepth_m, head attitude/nav, waterline reference and actual #SVP profile/time. Lead to verify (INFERRED): variant offsets, travel-time and angle corrections, fan assembly, head reference, waterline sign, receive/transmit epochs. Only a decoded, version-checked geometry may enter the ray operator. Legacy .all N/X/U/P/A is a later adapter unless all required fields are version-checked. Existing UDP bytes or completed .kmall records only. No private structures.

Use at most two prior-scaled modes, analytic layered integration or controlled quadrature and central differences at 0.05 m/s (halve to check convergence). For crossing pairs subtract a common line datum by a full-rank nuisance basis. Include slope uncertainty, distances, pose covariance, and strip shared pings or model their covariance. Return information Λ=GᵀG and v=−Gᵀr_w, G=(I−QQᵀ)WJ, r_w=(I−QQᵀ)Wr₀, calculated on data only with the final robust weights. Emit the retained subspace, α posterior and prior hash separately. With no independent #161 covariance use an explicit user-supplied profile covariance and label that provenance. A prior reused as a source cannot be offered the same line as independent validation. On an unidentifiable result show measured misclosure, competing causes and a cast check without a profile recommendation.

**Result fields.** Prefix each of `ModeVector`, `ModeAmplitude_mps`, `ModeSD_mps`, `DataRank`, `OuterResidual_m`, `LikelihoodInfo`, `PriorId`, `CrossingIds` with `REFR_`. Also emit prefixed `Score`, `Verdict`, `Reason`, `Support`, `Persistence`, `SourceIds`, `Stale` and `Excluded`. Units, nullability, shapes, record/interval keys and score direction go in the module docs. Explain the first check in watch language. Use record time for live persistence. An alert requires 60 s continuously over threshold and clears after 60 s below 75% of threshold. A gap resets the timer. Replay must be causal and deterministic. For the watch score, use maximum retained |posterior mode amplitude|/posterior SD, threshold 2 with independent residual improvement.

The tech gets the depth band and expected outer-beam improvement on a new line. Scientists get a profile-error diagnostic with uncertainty. Uniform bias over flat repeat geometry, tidal offsets, uncompensated heave, roll, water-mass changes between lines or a steered fan treated as vertical can all mimic refraction. Retain the identifiable linear combination only. Rank zero gives AMBIGUOUS. Registration gaps give POSTHOC_REVIEW.

## Failing test first

Add `contrib/deepsignal/test/swath_refraction/test_estimator.py`. Run `test_profile_mode_survives_nuisance_projection` and `test_duplicate_crossing_prior_refused` on the base before implementing the estimator. Capture the actual RED output. Each test must exercise the future public class or function, with explicit expected numbers or verdicts. Follow with tests for record shape, replay determinism, immutable inputs, absent channels and the demo logger chain.

## Synthetic-truth fixtures

Start with a constant-c ray c=1500 m/s, θ=30°, measured one-way t=0.1 s: x=75 m, z=129.90381 m below the head. Test port symmetry and degree/radian conversion. For solve-only rows r₀=(-0.4,+0.4,0) m, J=(+0.2,−0.2,0) m/(m/s), H=(1,1,1), row SD=0.01 m and mode prior SD=5 m/s, recover +2 within 0.05 m/s. Put J in span(H): assert data rank zero even with an informative prior. In the end-to-end test forward-shoot through piecewise homogeneous slabs to a flat/sloping bottom (solve intercept, then calculate times). Perturb a subsurface mode by +2 m/s, add signed roll and line shifts separately, vary angles and depths. Reserve a whole line and cast. Include mode-null, malformed/partial fan and a #161 prior derived from the same crossings.

Use fixed construction parameters, a local random generator seeded 17001 for development and disjoint seeds 27001 through 27020 for final injection trials. Preserve input hashes. Split fit and holdout by line/site/time block with a footprint buffer. Confirm in a test that the fit receives no holdout IDs. Treat correlated samples in an ensemble or trace as one evidence block. Use a guard reader to reject future records in live replay. Report p95 process time and high-water working memory against the measured arrival interval on a one-core ship PC.

## Validation target and falsifier

Replay DCDB/R2R crosses with cast and motion, and match a withheld cast averaged over the observable basis (V1/V2). Inject a known subsurface +2 m/s lens using an independent forward simulator and hold out whole crossing lines. Target ≥25% lower held-out outer-beam residual RMS than the unchanged #161 prior and error ≤1 m/s in an identifiable 2 m/s mode. Require ≤5% false SV attribution on roll-only trials. Falsify if equal-angle repeats identify a mode in the nuisance span or improvements disappear on the withheld line.

**INFERRED, lead to verify.** V1/V2 means NCEI DCDB EM bathymetry and R2R casts/navigation, e.g. Revelle RR2214. Confirm actual crossings, holdout cast, applied profile, head geometry and epoch. These are later validation candidates. Do not fetch sonar data to the Mac. Synthetic unit acceptance and real-cruise validation have separate receipts.

## Module contract and platform

Own the estimator, its documented input adapter and transform, tests, one offline-safe logger config `contrib/deepsignal/configs/swath_refraction_demo.yaml`, and `contrib/deepsignal/docs/swath_refraction.md`. The sample connects a local Reader to the Transform to a local text output with synthetic input built from this module’s own fixtures. Test the config by loading its class/module declarations and running its normal record path on a fixture. Document each knob's unit, expected range, example, and first check after an alarm. Respond to the desk usability checklist or mark an item N/A with a reason. No browser or GPU.

## Acceptance (from the fork root on Linux)

The first command must be RED before estimator code, then pass with both named tests and the rest of the suite. The second exits zero. The third prints True using the module's installed environment.

```sh
python3.12 -m unittest discover -s contrib/deepsignal/test/swath_refraction -t . -v
```

```sh
python3.12 -m flake8 --config .flake8 contrib/deepsignal/swath_refraction contrib/deepsignal/test/swath_refraction
```

```sh
python3.12 -c "import numpy, scipy; assert (numpy.__version__, scipy.__version__) == ('2.2.6', '1.15.3'); print(True)"
```

Record the exact tested fork SHA. The lead's subsequent gate checks that same SHA and requires a complete receipt with `__END__` and no unexpected FAIL. Science targets need a separate blocked-holdout report.

## Scope

Only `contrib/deepsignal/swath_refraction/**`, `contrib/deepsignal/test/swath_refraction/**`, `contrib/deepsignal/docs/swath_refraction.md`, `contrib/deepsignal/configs/swath_refraction_demo.yaml` and missing empty package markers. The requirements pins belong under the module. Check the config load path, old and current Transform imports, existing field consumers and logger output serialization. Consume upstream fields through schema adapters. A standalone demo can supply those same fields. Any integration with shared factors imports the versioned API when available.

## Trust boundaries and data integrity

D-SHIP1 is listen-only. Accept existing operator-distributed UDP through a core reader, complete public-format file tails when supported, or local archives. No module socket, vendor subscription, instrument query, configuration or triggering. Validate version, units, timestamps, frame, datum, finite numeric values, bounds and ancestry before estimation. Bound record counts and memory before allocation, count invalid/duplicate/partial inputs, report stale or unsupported inputs as missing. A short tail read waits for a complete record. A torn archive record is reported. No extrapolation across a file gap. Reject a prefix collision. A test must show the input bytes/fields and original timestamp survive unchanged.

Use the evidence graph: trace each fit to raw channels, calibration, clock, navigation and parent fits. Collapse duplicates and keep covariance for shared errors. Science feature scores have independent QC. Use GOOD/1, SUSPECT/3, FAULT_LIKELY/4, AMBIGUOUS/3, UNCORRECTABLE/4 and POSTHOC_REVIEW/2 as appropriate. An obscured cause is AMBIGUOUS. Score, support/persistence and a plain explanation accompany every flag. Only independent post-cruise evidence can qualify a CORRECTABLE proposal for #56. A named allowlisted reviewer approves any reversible ledger correction at a trusted checkpoint. This module produces derived observations only.

## Non-goals and banned

No #161 profile synthesis, cast ingestion/export, changing an applied profile, or inference of an unrestricted depth-by-depth SV curve. No core changes or global dependency changes. No loosened/skipped tests, silent errors or unrelated refactors. No writes outside module scope and its dedicated scratch during the build.

## Stop rule and result

If no change is needed, report the evidence. After two red fix rounds report the remaining failure to the lead. For an unverified format version, disable that version and continue with the documented input contract. Report within 30 lines.

- Head SHA and short diff:
- RED test names and actual output:
- Linux acceptance tails, gate receipt SHA256/verdict if run:
- Synthetic truth, baseline, achieved error/coverage, ambiguity and resource use:
- Real evidence checked, remaining inferred leads and limitations:
