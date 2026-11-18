# DeepSignal Reanalysis: improve old cruise data, pass by pass

Plan only, nothing built. Status PROPOSED (D-REAN1, IDEAS #63). Written
2026-11-18 from Eugene's ask: "take these modules and work on a program that
can analyze and recursively improve old data."

## Answer first

Build a **reanalysis loop** (borrowing the meteorology term: re-run today's
best methods over old observations). Each pass reads the untouched raw
archive, adds QC flags and proposed corrections as separate reversible layers,
and is scored on a frozen scorecard. A pass is kept only if it beats the last
accepted pass on evidence it was not tuned on, and a person signs off every
value change. The loop stops when gains vanish or the residuals reach the
noise floor of the references.

"Recursive" means the **methods and the ledger** improve each pass. It never
means a pass fits itself to the previous pass's output. Every pass starts from
raw plus the human-approved ledger.

Mental model:

```
raw archive (read-only, hashed) ──► pass N ──► flags + proposed ledger entries
        ▲                              │
        │                              ▼
  approved ledger  ◄── sign-off ◄── scorecard vs pass N-1
  (reversible)                      (holdout refs, fault bench, consistency)
```

Why this is worth doing: the same DeepSignal transforms run live and offline,
so every pass over old data is also a test of the live modules on years of
real conditions. The bench becomes the proof behind the "bad sensor detected
under 1 hour" metric, and the ledger becomes the proof behind "under 1% of
values fixed on shore".

## 1. What "improves" means (the scorecard)

Evidence is ranked by how independent it is. Higher tiers decide; lower tiers
only guard.

| Tier | Evidence | Examples | Role |
|---|---|---|---|
| A | Independent references, split into fit and holdout | Pre and post cruise calibration certificates, CTD surface bins at stations, bottle salinities, discrete underway samples, reference thermometer checks | Decides whether a **correction** is kept |
| B | Synthetic truth from the fault-injection bench (#53) | Injected drift, step bias, lag, spikes, flat-lines, clock resets, plus real fronts as traps | Decides whether a **flagging method** is kept |
| C | Internal consistency | Redundant-sensor residuals (#10), physics referee (#25), hull SST vs TSG | Guard only: must not get worse on pairs not used for fitting. Never the sole reason to accept |

Metrics recorded every pass, per sensor and per cruise:

1. **Flag skill (Tier B, plus labeled real faults):** recall per fault type,
   false flags per 1000 good samples, median detection delay, and the
   UNDECIDED share. An UNDECIDED on an easy injected fault counts as a miss.
2. **Correction skill (Tier A holdout):** bias and RMSE of sensor minus
   reference, before and after the ledger. A gain counts only if it exceeds
   the combined uncertainty of the gain itself (paired bootstrap or paired
   t-test on holdout residuals, blocked by station so neighbours do not
   double-count).
3. **Uncertainty honesty (#57):** coverage, the share of holdout residuals
   inside the stated 95% interval. Band 90 to 98%. Below means
   overconfident; above means the error bars are uselessly wide.
4. **Consistency (Tier C):** residuals between sensor pairs that no
   correction was fitted against. Must not worsen beyond tolerance.
5. **Change budget:** share of values changed by the ledger, and the size of
   the largest change. Big changes need Tier A evidence, not just a fit.

## 2. Accept rule, stop rule, holdout budget

**Accept pass N only if all hold:**
- Tier A holdout skill improves beyond its own uncertainty, or the pass
  changes flags only.
- Bench scores do not regress on any fault type beyond a fixed tolerance
  (proposed: recall down at most 2 points, false flags up at most 10%).
- Coverage stays in the 90 to 98% band.
- Tier C consistency on unfitted pairs does not worsen.
- A named reviewer approved every ledger entry that changes values.

**Stop the loop for a sensor when any is true:**
- Two consecutive passes fail the accept rule (no real gain).
- **Uncertainty floor reached:** the holdout residual spread is consistent
  with the reference's own uncertainty plus sampling mismatch (for example
  TSG vs bottle salinity spread close to salinometer precision plus intake
  time and depth mismatch). Further "gains" are fitting noise.
- **Holdout budget spent:** each scoring of the holdout is a look, logged in
  the ledger. Proposed cap: 3 looks per sensor per cruise. After that, new
  claims need a fresh holdout, which means a new cruise.
- Pass cap reached (proposed: 5 per cruise). More passes than that means the
  method is being tuned, not the data improved.

## 3. Guards against the loop fooling itself

1. **Raw is immutable.** Raw files are hashed into a manifest at ingest. Every
   pass re-verifies the hashes and refuses to run if one changed. Nothing ever
   writes into the archive folder.
2. **Corrections are layers.** Each ledger entry stores inputs, method, code
   sha, parameters, uncertainty, evidence plot, reviewer, decision, and can be
   rolled back alone (#56, pairs with provenance hashes #32).
3. **Fit and score are separated by code, not by discipline.** The holdout
   split is made once, blocked by time and station (random points leak
   because neighbouring samples are correlated), frozen as a hashed manifest,
   and the fitting step receives a dataset the holdout rows were removed from.
   A test asserts the fitter cannot see them.
4. **No circular references.** A correction fitted to sensor B is never
   scored by agreement with B.
5. **No self-training.** Flags from pass N are never training labels for pass
   N+1. Labels come only from people (tech notes, watch verdicts #9) or Tier A.
6. **Simple, physical corrections first.** Ledger v1 allows offset, linear
   drift between calibration points, and characterized lag (#60). No
   free-form ML corrections until a simple method has been beaten on holdout
   across cruises.
7. **Cross-cruise validation.** Method settings are tuned on some cruises and
   scored on a cruise they never saw (leave-one-cruise-out). Settings are
   global unless evidence says a ship or sensor needs its own.
8. **Fresh bench seeds for the final score.** Faults used while tuning are not
   the faults used to score the release.
9. **Live and retrospective are different products.** Reanalysis may look
   ahead in time (#54). Any number quoted for live mode comes only from a
   causal replay run, where a guard reader proves no record after time t was
   read. Reports say which mode produced each number.
10. **AI suggests, people decide.** No ledger entry is ever auto-approved in
    v1. AI tools stay read-only (#62).

## 4. Failure modes, named plainly

| # | Failure | What it looks like | Mitigation |
|---|---|---|---|
| F1 | Circular validation | Score improves because the fit and the score used the same reference | Guards 3, 4 |
| F2 | Holdout erosion | Many looks at the holdout slowly turn it into training data | Look budget, stop rule |
| F3 | Bench overfit | Detectors tuned to synthetic faults that do not look like real ones | Real fronts as traps, real labeled faults from tech notes, fresh seeds |
| F4 | Hiding behind UNDECIDED | Detector looks precise by refusing to answer | UNDECIDED share reported; easy cases scored as misses |
| F5 | Erasing real ocean | A front or water-mass change "corrected" as drift | Drift corrections need Tier A; "cannot tell" verdict (#55); front traps on the bench |
| F6 | Bad references | CTD or bottle values themselves wrong, mislabeled or mistimed | Reference QC, robust statistics, outliers go to a person, never silently dropped |
| F7 | Clock errors posing as sensor errors | Lag or offset blamed on the sensor when the merge is wrong | Time base stage runs before any drift fit (#31, #38) |
| F8 | Wrong metadata | Wrong serial or calibration applied | Instrument history with contradiction checks (#52) before fitting |
| F9 | Irreproducible passes | Same pass gives different results later | Code sha, input hashes and parameters recorded per pass; replay must match |
| F10 | Rubber-stamp review | Reviewer approves 400 tiny entries without reading | Minimum effect size, entries grouped by evidence class, change budget |
| F11 | Format guessing | Old SCS or MetAcq files parsed with a wrong field, unit or time zone | Readers fail loudly on anything unknown; record counts reconciled against the source |
| F12 | Selective success | Only cruises with rich references improve, then the claim is generalized | Report coverage: which sensors and cruises had Tier A evidence |
| F13 | Goodhart on the change budget | Real fixes withheld to keep the "under 1%" number | Budget is reported, never a target the loop optimizes |

## 5. Pipeline stages and the modules each needs

| Stage | Does | Modules (IDEAS row) | Runs every pass? |
|---|---|---|---|
| S0 Ingest | Read old archives into normal OpenRVDAS records; hash manifest | Legacy readers (#59), archive manifest | No, only when readers change |
| S1 Context | Instrument history, events and stations, reference set, frozen holdout split | Instrument history (#52), reference loader, holdout splitter | No, only when metadata changes |
| S2 Time base | Measure clock offset and lag per instrument; propose time corrections to the ledger | Clock forensics (#31, #38) | Yes |
| S3 Flag | QARTOD flags with "cannot tell", redundant-pair CUSUM, later the physics referee | #8, #55, #10, #25 | Yes |
| S4 Diagnose | Drift and bias against references, two-sided lookahead smoother, response lag | #11, #54, #60 | Yes |
| S5 Propose | Write proposed ledger entries with uncertainty and evidence plots | Ledger (#56), uncertainty (#57) | Yes |
| S6 Score | Bench plus holdout scorecard, compare with the last accepted pass, apply accept and stop rules | Bench (#53), scorer, pass runner | Yes |
| S7 Review | Person approves or rolls back each entry, with a reason | Review tool | Yes |
| S8 Publish | Versioned release: raw, flags, ledger, history, manifest, changelog | R2R package (#58), provenance (#32) | On release |

S3 to S7 is the loop. Every stage is a standard OpenRVDAS piece where it can
be (Readers for S0, Transforms for S3 and for applying the ledger) so the
same code runs on the live ship. Batch-only parts (splitter, scorer, pass
runner, review tool) are small CLIs under `contrib/deepsignal/`.

## 6. Milestones (each ends with something a person can use)

| M | Name | Delivers | Done when |
|---|---|---|---|
| M0 | Load the past | One real cruise loads end to end from its original files; hashed manifest; reference set; frozen holdout | Record counts match the source, manifest replays identically, a tech can run it from a 5-minute guide |
| M1 | Flags-only reanalysis | QARTOD plus "cannot tell" over the archive; fault bench v1; scorecard v1 baseline | Bench report per fault type for one cruise; zero values changed |
| M2 | First correction class | Ledger plus TSG salinity and temperature offset and drift vs bottles and CTD, with uncertainty and coverage; review CLI | Holdout residual improves beyond uncertainty on at least one cruise, coverage in band, every entry signed |
| M3 | The loop | Pass runner with accept and stop rules, look budget, pass-to-pass diff report, leave-one-cruise-out | Three cruises, passes stop on their own by rule, reproducible from shas |
| M4 | Deeper diagnosis | Clock forensics, lookahead smoother, response-lag correction | Each beats M3 on holdout or is dropped |
| M5 | Release and screen | R2R-ready release builder; a console page with the review queue and ledger (USABILITY rules apply) | A tech reviews and approves a pass without the command line |

TSG salinity is the proposed first correction class because it usually has
the most independent references (bottles, CTD surface bins) and well-known
failure shapes (biofouling drift, intake lag, bubbles).

## 7. Codex-sized modules (one brief, one branch, one PR each)

Branch `deepsignal/<module>`, folder `contrib/deepsignal/`. Model tier per
`docs/CODEX.md` section 2: Astra for statistics, Sol for code, Luna for
mechanical work.

| # | Module | One line | Depends on | Model | M |
|---|---|---|---|---|---|
| 1 | `archive-manifest` | Hash every file in a cruise archive; verify later runs see identical bytes | none | Luna | M0 |
| 2 | `legacy-scs-reader` | Reader for SCS raw logs into standard records; fails loudly on unknown lines | samples from Eugene | Sol | M0 |
| 3 | `legacy-metacq-reader` | Same for MetAcq files | samples from Eugene | Sol | M0 |
| 4 | `reference-loader` | CTD surface bins, bottle salinities and cal certificates into one reference table with uncertainty | none | Sol | M0 |
| 5 | `holdout-splitter` | Time and station blocked split, frozen manifest, fitter-side filter with a test that it cannot see holdout | 4 | Astra | M0 |
| 6 | `instrument-history` | Dated serial, calibration, swap and mount records per sensor, with contradiction checks (#52) | none | Sol | M0 |
| 7 | `qartod-flags` | Already briefed and in flight | none | Astra | M1 |
| 8 | `cannot-tell-verdict` | UNDECIDED outcome for drift-vs-real-change tests, with its share reported (#55) | 7 | Astra | M1 |
| 9 | `fault-injector` | Inject known faults into clean segments from frozen distributions and seeds (#53 part 1) | 1 | Astra | M1 |
| 10 | `bench-scorer` | Recall, false flags, delay and UNDECIDED share per fault type (#53 part 2) | 9 | Astra | M1 |
| 11 | `correction-ledger` | Append-only ledger, apply and roll back layers as a Transform, test proves raw bytes unchanged (#56) | 1 | Sol | M2 |
| 12 | `reference-drift-fit` | Offset and linear drift between calibration points vs references, with uncertainty (#11) | 4, 5 | Astra | M2 |
| 13 | `uncertainty-coverage` | Coverage check of stated intervals on holdout (#57) | 5 | Astra | M2 |
| 14 | `review-cli` | List, approve and roll back ledger entries with reviewer and reason; plain messages | 11 | Sol | M2 |
| 15 | `pass-runner` | Runs S2 to S6, records shas, hashes and settings, applies accept and stop rules, counts holdout looks | 10, 11, 13 | Sol | M3 |
| 16 | `pass-diff-report` | Human-readable diff between two passes with evidence plots | 15 | Sol | M3 |
| 17 | `causal-replay-guard` | Reader wrapper that proves no future record was read; required for any live-mode number | none | Sol | M3 |
| 18 | `clock-offset-estimator` | Clock offset and lag per instrument from shared roll and heave (#38) | 1 | Astra | M4 |
| 19 | `lookahead-drift-smoother` | Two-sided state-space smoother for slow drift, retrospective only (#54) | 12 | Astra | M4 |
| 20 | `response-lag-correction` | Fit and undo characterized lags, output marked reconstructed (#60) | 18 | Astra | M4 |
| 21 | `r2r-release-builder` | Versioned, archive-ready release folder (#58) | 11, 1 | Sol | M5 |

Already briefed under D-SOII1 (do not re-brief): module 6 is
`briefs/deepsignal-instrument-history.md`, modules 9 and 10 are
`briefs/deepsignal-fault-bench.md`, module 11 is
`briefs/deepsignal-correction-ledger.md`, module 19 is
`briefs/deepsignal-post-cruise-drift.md`. Module 8 rides with the QARTOD
brief. Reconcile names when each is launched.

Modules 1, 4, 6 and 11 have no dependency on Eugene's data shape beyond
samples and can start first. The console page in M5 is planned with the
DeepSignal Console design, not as its own brief here.

## 8. What Eugene needs to provide

Minimum to start M0 and M1 (one cruise); M3 needs three.

1. **Raw archives exactly as recorded** for at least three cruises, ideally
   one ship and one sensor suite: SCS raw files, MetAcq files, or OpenRVDAS
   logs, with original timestamps and folder layout. Read-only copies; we
   never touch the originals.
2. **Format notes** for those files: SCS and MetAcq configuration files,
   sensor-to-file maps, units, the time base used (UTC or ship time).
3. **Instrument metadata:** serials, pre and post cruise calibration
   certificates with dates and coefficients, swap and repair notes, sensor
   heights and positions, TSG intake depth and any known plumbing lag.
4. **Independent references:** processed post-cruise CTD casts with station
   times, bottle salinity sheets, discrete underway samples, any reference
   thermometer or barometer checks.
5. **Event logs and tech notes:** stations, dock periods, and above all known
   bad periods. These become the real-fault test set that keeps the bench
   honest (F3).
6. **Rights:** whether each cruise's data and results may be published
   openly, and who may sign off corrections.

Proposed pilot set found 2026-11-18: three Revelle GO-SHIP cruises, see
`research/2026-11-18-r2r-pilot-cruises.md`.

If gathering these is slow, public R2R underway archives could bootstrap M0
and M1 for UNOLS ships (inferred, not verified: confirm what formats and
references R2R actually holds for a chosen cruise before relying on it). The
NBP1406 sample in the core repo is enough for unit tests, not for scoring.

## 9. Decisions for Eugene

1. **First cruises.** Three cruises from one ship with CTD and bottle
   salinity. Recommended. Alternative: start from public R2R data now.
2. **First correction class.** TSG salinity and temperature. Recommended
   (most references, known failure shapes).
3. **Who signs off.** Recommended: no auto-approval ever in v1; reviewer is a
   named tech or the PI for that cruise.
4. **numpy.** It is not a declared core dependency. Recommended: allow numpy
   (pinned, noted in each PR) for the Astra modules; no scipy, pandas or ML
   libraries until a module proves the need.
5. **Home.** Recommended: same `contrib/deepsignal/` umbrella, batch tools as
   small CLIs beside the transforms, so live and reanalysis share code.
6. **Default thresholds.** The numbers in sections 1 and 2 (tolerances,
   coverage band, 3 looks, 5 passes) are proposals; Eugene may change them
   before M3, never during a scored run.
