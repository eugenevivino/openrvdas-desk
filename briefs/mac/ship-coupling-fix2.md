# Brief: ship-coupling (#78) fix round 2 (final; after the Astra ultra re-review of fix round 1: HOLD)

- Module: ship-coupling engine only. Branch `deepsignal/ship-coupling`, base 9eb1b47 (fix round 1). Last fix round allowed.
- Lane: `mac`. `-m gpt-6.2-astra` high via `~/bin/ds-codex` with `KALON_ALLOW_ASTRA=1` (statistics), fresh session.
- Parent briefs: desk `briefs/deepsignal-ship-coupling.md` and `briefs/mac/ship-coupling-fix1.md`; pinned formulas hold.
- Re-review: fresh Astra ultra, read-only. If still HOLD, the branch stays unmerged and the lead reports; no third round.

## Re-review findings to close (verbatim; each needs code plus a regression test that fails before the fix)
**1. Ranked findings**

- **P1 VERIFIED** Reciprocal legs 0.89 km apart gave 532 ship-artifact votes for a temperature driven by latitude, background, and noise because the control treats nearby leg medians as observations of the same environment. [controls.py:73](/private/tmp/deepsignal/ship-coupling-fix1/repo/contrib/deepsignal/coupling/controls.py:73)
- **P1 VERIFIED** With 96 bins and default settings, the sole legal shift was drawn 500 times, giving independent noise `p = 1/501` in both splits and a `confirmed` verdict. [stats.py:139](/private/tmp/deepsignal/ship-coupling-fix1/repo/contrib/deepsignal/coupling/stats.py:139)
- **P1 VERIFIED** Headings of 90° and 270° have the same mathematical cosine, but Spearman ranked their floating-point rounding errors and reported a `ship_artifact` with effect 0.861. [prep.py:93](/private/tmp/deepsignal/ship-coupling-fix1/repo/contrib/deepsignal/coupling/prep.py:93)
- **P1 VERIFIED** Both sectors scored QC 1 for a confirmed 12-bin-delayed ship artifact because polar calibration pairs residuals with the contemporaneous heading. [atlas.py:97](/private/tmp/deepsignal/ship-coupling-fix1/repo/contrib/deepsignal/coupling/atlas.py:97)
- **P1 VERIFIED** Setting `min_n_eff: 2` bypasses the brief’s floor of 30 and produces `confirmed` at effective sizes 7.29 and 6.81 in the checked-in test. [atlas.py:62](/private/tmp/deepsignal/ship-coupling-fix1/repo/contrib/deepsignal/coupling/atlas.py:62)
- **P1 VERIFIED** One constant bootstrap replicate suppressed an otherwise computable shift p-value of 0.112 and labeled a fit with `n_eff = 100.42` insufficient. [stats.py:109](/private/tmp/deepsignal/ship-coupling-fix1/repo/contrib/deepsignal/coupling/stats.py:109) [atlas.py:62](/private/tmp/deepsignal/ship-coupling-fix1/repo/contrib/deepsignal/coupling/atlas.py:62)
- **P1 VERIFIED** Adding one empty bin from a second cruise changed `confirmed` to `insufficient` solely because that cruise had no legal shift, with effect and `n_eff` unchanged. [stats.py:124](/private/tmp/deepsignal/ship-coupling-fix1/repo/contrib/deepsignal/coupling/stats.py:124)
- **P1 VERIFIED** On the allowed lag grid `[0, 1, 4]`, adjacent winners 1 and 4 failed replication because the code uses the smallest numerical gap anywhere in the grid. [atlas.py:72](/private/tmp/deepsignal/ship-coupling-fix1/repo/contrib/deepsignal/coupling/atlas.py:72)
- **P1 VERIFIED** A heading packet at the same timestamp as a detected speed maneuver erased the speed-change evidence and changed live QC from 2 to 3. [transform.py:63](/private/tmp/deepsignal/ship-coupling-fix1/repo/contrib/deepsignal/coupling/transform.py:63)
- **P1 VERIFIED** A delayed heading observation overwrote newer ship state and caused the next measurement to receive QC 3 from the wrong sector. [transform.py:55](/private/tmp/deepsignal/ship-coupling-fix1/repo/contrib/deepsignal/coupling/transform.py:55)
- **P1 VERIFIED** Offline and live scoring assigned identical inputs to different sectors, including sectors 7 and 8 at exactly 240° and sectors 6 and 0 when direct and derived headings disagreed. [prep.py:85](/private/tmp/deepsignal/ship-coupling-fix1/repo/contrib/deepsignal/coupling/prep.py:85) [transform.py:56](/private/tmp/deepsignal/ship-coupling-fix1/repo/contrib/deepsignal/coupling/transform.py:56)
- **P1 VERIFIED** Supplying `lags=[0]` silently switched the requested Pearson surrogate statistic to Spearman and changed its p-value from 0.68 to 0.91. [stats.py:128](/private/tmp/deepsignal/ship-coupling-fix1/repo/contrib/deepsignal/coupling/stats.py:128)
- **P1 VERIFIED** Pearson returned 0 for identical vectors `[1e100, 2e100, 3e100]` because its denominator overflowed. [stats.py:28](/private/tmp/deepsignal/ship-coupling-fix1/repo/contrib/deepsignal/coupling/stats.py:28)
- **P1 VERIFIED** Two log timestamps 365 days apart require 3,153,601 row dictionaries at the default bin width, with no bound on the input span. [prep.py:73](/private/tmp/deepsignal/ship-coupling-fix1/repo/contrib/deepsignal/coupling/prep.py:73)
- **P2 VERIFIED** Reusing an output directory leaves the previous `polar_<field>.csv` available after the field loses confirmation. [archive.py:138](/private/tmp/deepsignal/ship-coupling-fix1/repo/contrib/deepsignal/coupling/archive.py:138)
- **P2 VERIFIED** The bench injector labeled an entire interval faulty at 90° to the configured sector even though every output value equaled its input. [bench_injectors.py:23](/private/tmp/deepsignal/ship-coupling-fix1/repo/contrib/deepsignal/coupling/bench_injectors.py:23)

**2. Brief and prior findings**

- **VERIFIED** Prior findings 3 through 15 and 17 are fixed for their reported cases, including gap preservation, winning-lag support, family-specific FDR, raw-field preservation, and input-alias protection. Finding 18’s scenario mapping and timestamped return are fixed in code. The fault bench is absent from this checkout, so integration remains unverified.
- **VERIFIED** For findings 1, 2, and 16, missing controls now withhold `ship_artifact`, the real NBP1406 sample returns `insufficient` at effective sizes 20.81 and 17.87, and the shift and bootstrap defaults match the brief. The spatial-gradient, threshold-override, and single-shift failures above remain.
- **VERIFIED** On ordinary finite inputs, average-tie Spearman, biased ACF, the capped 1/e search, the pinned `n_eff` formula, paired moving blocks, the plus-one count, max-over-lags Spearman, and per-family BH/BY follow the brief. Markdown and CSV still omit realized per-fit block and shift lengths, and Markdown gives no per-cruise replication count. [archive.py:117](/private/tmp/deepsignal/ship-coupling-fix1/repo/contrib/deepsignal/coupling/archive.py:117)

**3. Tests**

- **VERIFIED** I ran 25 of 26 test bodies successfully with temporary I/O held in memory or bypassed and inspected the hard-link test. The suite exercises production code and asserts exact `n_eff`, BH/BY sets, seeded CI and surrogate values, QC boundaries, and preserved raw bytes. [test_review.py:151](/private/tmp/deepsignal/ship-coupling-fix1/repo/contrib/deepsignal/test/coupling/test_review.py:151)
- **VERIFIED** Required coverage remains weak where it matters here. The reciprocal test misses a gradient between nearby tracks, the decorrelation vector never requires a later threshold crossing, and 99 surrogates over 50 hypotheses make 1 through 9 BH rejections impossible in the null test. [test_review.py:68](/private/tmp/deepsignal/ship-coupling-fix1/repo/contrib/deepsignal/test/coupling/test_review.py:68) [test_stats.py:12](/private/tmp/deepsignal/ship-coupling-fix1/repo/contrib/deepsignal/test/coupling/test_stats.py:12) [test_review.py:357](/private/tmp/deepsignal/ship-coupling-fix1/repo/contrib/deepsignal/test/coupling/test_review.py:357)

**4. HOLD (VERIFIED).** Independent noise can replicate, an Earth-fixed gradient can earn `ship_artifact`, and a reproduced delayed artifact receives live QC 1.
## Acceptance (exact commands, from repo root)
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
