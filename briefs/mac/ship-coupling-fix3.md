# Brief: ship-coupling (#78) fix round 3 (FINAL; after the Astra ultra re-review of fix round 2: HOLD)

- Module: ship-coupling engine only. Branch `deepsignal/ship-coupling`, base cf7afd9 (fix round 2). Coordinator-approved final round.
- Lane: `mac`. `-m gpt-6.2-astra` high via `~/bin/ds-codex` with `KALON_ALLOW_ASTRA=1` (statistics), fresh session.
- Parent briefs: desk `briefs/deepsignal-ship-coupling.md`, `briefs/mac/ship-coupling-fix1.md`, `briefs/mac/ship-coupling-fix2.md`.
- If the ultra re-review still HOLDs: the branch stays unmerged and the work stops.

## Must close (each with a regression test that fails before the fix)
1. Independent noise can still reach `confirmed`.
2. An Earth-fixed field can be labelled ship contamination.
3. Live scoring can issue QC 1 from the wrong sector.
4. Missing tests: a non-perfect Pearson coefficient hand vector; an asymmetric Spearman tie case that distinguishes average
   from dense ranks; the 50-hypothesis null test run over several seeds (not one), with its expected false-confirm bound.

## Re-review text (verbatim, with file:line)
**1. Ranked findings**

- **P1 VERIFIED** A field equal to `1000 × latitude` received 200 `ship_artifact` votes and passed both time shifts because subtracting different rolling medians made identical readings at a shared position acquire opposite residuals. [controls.py:67](/private/tmp/deepsignal/ship-coupling-fix2/repo/contrib/deepsignal/coupling/controls.py:67)
- **P1 VERIFIED** Adding a 145-bin constant cruise turned independent noise from `rejected` into `confirmed` under default settings because 50 offset combinations reproduced the same shifted data, lowering both p-values from 1/2 to 1/51. [stats.py:150](/private/tmp/deepsignal/ship-coupling-fix2/repo/contrib/deepsignal/coupling/stats.py:150)
- **P1 VERIFIED** A field equal to `0.5 × cos(relative heading)` received 500 `environmental` votes because reciprocal legs with identical relative headings can vote environmental without testing a heading reversal. [controls.py:64](/private/tmp/deepsignal/ship-coupling-fix2/repo/contrib/deepsignal/coupling/controls.py:64)
- **P1 VERIFIED** Two headings of 320° and 40° in a completed bin calibrated to sector 0 offline, but live lag history retained only 40° and issued QC 1 from sector 1 instead of QC 3. [transform.py:132](/private/tmp/deepsignal/ship-coupling-fix2/repo/contrib/deepsignal/coupling/transform.py:132)
- **P1 VERIFIED** Scaling two identical 100-point ramps by `1e-200` underflowed the ACF denominator, raised `n_eff` from 4.729 to 100, and changed `insufficient` to `confirmed`. [stats.py:67](/private/tmp/deepsignal/ship-coupling-fix2/repo/contrib/deepsignal/coupling/stats.py:67)
- **P1 VERIFIED** Adding a two-bin cruise with the field and ship variable in separate bins changed `confirmed` to `insufficient` despite contributing zero pairs and leaving the effect and `n_eff` unchanged. [atlas.py:39](/private/tmp/deepsignal/ship-coupling-fix2/repo/contrib/deepsignal/coupling/atlas.py:39)
- **P1 VERIFIED** A measurement at time 30 caused the newest heading observation, arriving afterward with time 20, to be discarded, so the measurement at time 40 received QC 3 using the heading from time 10. [transform.py:123](/private/tmp/deepsignal/ship-coupling-fix2/repo/contrib/deepsignal/coupling/transform.py:123)
- **P1 VERIFIED** A malformed timestamp was silently accepted as untimed, allowing its heading to overwrite dated state and change the next valid measurement from QC 2 to QC 3. [transform.py:121](/private/tmp/deepsignal/ship-coupling-fix2/repo/contrib/deepsignal/coupling/transform.py:121)
- **P1 VERIFIED** A `transit` label overrode a measured 6 kn/min speed change live and issued QC 3 from a transit calibration, although offline preparation classified the same bin as `maneuver`. [transform.py:79](/private/tmp/deepsignal/ship-coupling-fix2/repo/contrib/deepsignal/coupling/transform.py:79)
- **P1 VERIFIED** When the configured relative-heading channel was null, offline preparation silently used a different column named `relative_heading` while live scoring correctly reported missing state. [prep.py:107](/private/tmp/deepsignal/ship-coupling-fix2/repo/contrib/deepsignal/coupling/prep.py:107)
- **P2 VERIFIED** A latitude offset of `1e-8` degrees, about 1 mm, erased every reciprocal match in the injected-bias fixture because the control requires exact coordinate equality in addition to the configured distance tolerance. [controls.py:159](/private/tmp/deepsignal/ship-coupling-fix2/repo/contrib/deepsignal/coupling/controls.py:159)
- **P2 INFERRED** An interrupted export can leave new Markdown and polar CSVs alongside the previous `atlas.json` because publication replaces each file separately. [archive.py:199](/private/tmp/deepsignal/ship-coupling-fix2/repo/contrib/deepsignal/coupling/archive.py:199)

**2. Brief and prior findings**

- **VERIFIED** I checked all 18 original findings and all 16 follow-up findings. Their specific regression cases are addressed, including raw-field preservation, input-alias checks, stale polar cleanup and injector truth intervals. The broader reciprocal, surrogate-support and live-state failures above remain open. The real NBP1406 split returned `insufficient` with effective sizes 20.81 and 17.87.
- **VERIFIED** On ordinary finite vectors, Pearson, average-tie Spearman, biased ACF, capped 1/e crossing, winning-lag `n_eff`, paired moving blocks, max-over-lags surrogate testing, and per-family BH/BY in both splits follow the brief. The implementation documents its realized shift denominator and unavailable CI after an undefined bootstrap replicate. The requested import-compatibility fallback is absent. [stats.py:17](/private/tmp/deepsignal/ship-coupling-fix2/repo/contrib/deepsignal/coupling/stats.py:17) [atlas.py:75](/private/tmp/deepsignal/ship-coupling-fix2/repo/contrib/deepsignal/coupling/atlas.py:75) [transform.py:8](/private/tmp/deepsignal/ship-coupling-fix2/repo/contrib/deepsignal/coupling/transform.py:8)

**3. Tests**

- **VERIFIED** All 44 test bodies passed with temporary I/O held in memory. They exercise production code and assert exact effective sizes, rejection sets, seeded resampling results, lag alignment, QC boundaries and raw bytes. Real filesystem publication and locking were unverified. Fault-bench integration remains pending because the bench is absent.
- **VERIFIED** The hand-vector coverage still lacks a nonperfect Pearson coefficient and an asymmetric Spearman tie case that distinguishes average from dense ranks. The 50-hypothesis null test uses one seed, and the suite misses the reproduced false verdicts above. [test_stats.py:8](/private/tmp/deepsignal/ship-coupling-fix2/repo/contrib/deepsignal/test/coupling/test_stats.py:8) [test_review.py:354](/private/tmp/deepsignal/ship-coupling-fix2/repo/contrib/deepsignal/test/coupling/test_review.py:354)

**4. HOLD (VERIFIED).** Independent noise can confirm, an Earth-fixed field can be labeled ship contamination, and live scoring can issue QC 1 from the wrong sector.## Acceptance (exact commands, from repo root)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/coupling -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal
```
```
python3.12 -m contrib.deepsignal.coupling atlas --config contrib/deepsignal/configs/ship_coupling_atlas.yaml
```

## Scope
Only `contrib/deepsignal/coupling/**`, `contrib/deepsignal/test/coupling/**`, `contrib/deepsignal/configs/ship_coupling_*`,
`contrib/deepsignal/docs/ship_coupling.md`.

## Stop rule
If a finding needs a change to a pinned formula in the parent brief, report it instead of changing the design.
