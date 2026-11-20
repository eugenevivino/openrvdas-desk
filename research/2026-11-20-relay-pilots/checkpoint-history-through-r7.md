# Historical checkpoints, superseded by current handover

Latest update: R2 at9935ed82 returned HOLD on sparse-cadence, QC-only-history and
catalog-collision variations. Its original answer is preserved as
`research/2026-11-20-relay-pilots/combined-astra-r2-hold.md`. No integration occurred.
All six variations reproduced atf09ff838, then repaired sourcee388d666 passed229
frontend tests, lint and type checks. Two timestamp-correction replay variants
reproduced at39062221;2eaaf01a fixes their observation-epoch retention.
Final generated bundle `4f28b56d58c562ae7419475c05da7794a403c973` is published on
`deepsignal/relay-combined-pilot-20261120`. `combined-final-release-state` completed both unchanged full Mac design checks,
PASS. Linux44720535508 (workflow58ae2a9) all3 jobs PASS,231frontend tests.
R3 is terminal HOLD; answer preserved in `research/2026-11-20-relay-pilots/combined-astra-r3-hold.md`.
Eight new regressions at80dd74db reproduced cached-return cadence, historical QC
alignment, configured suffix collisions and stderr replay ordering. Source80abbf83
repairs these; `integration-r3-green-state` completed239frontend/lint/type PASS.
Generateda284c1c7 is published on the existing pilot topic. Both full native checks in
`combined-r4-release-state` PASS (151.8s and31.1s). Exact Linux44723265628
(workflowc9db041) all3 jobs PASS. Fresh independent R4 review owns
`native-review-r4/state`, job88fcbdb8f725e0f4988077f6, session
01a1f89a-ba02-7512-b351-9ba4932af994. Read-only Astra Ultra headers verified.
R4 terminal HOLD (five valid-input cases), preserved in combined-astra-r4-hold.md.
No integration. Ten corrected production-mode variants atd6253b3a reproduced
all five cases (10RED). Two complete per-test catalog variants at1490e537 also
reproduced the missing bound. Source01e83671 passes251frontend/lint/type checks.
Generated3db4e630c0415a3462607a6c3587f62883f57620 is published on the existing
pilot topic. `combined-r5-release-state` completed both full native checks PASS.
Linux44725528266 (workflowa50fd9e) all3 jobs PASS.
R5 is terminal HOLD (combined cache history and QC namespace prefix). Its answer
is preserved as combined-astra-r5-hold.md. Four new regressions atbd6cd242
reproduced both cases; source85e9307e repairs them. Full frontend255tests/lint/types in
`integration-r5-green-state` PASS. Generated9b344665 is published on the existing
pilot topic. `combined-r6-release-state` completed both full native checks PASS.
Linux44726875102 (workflow07e7d4c) frontend/hardening PASS, pilot active.
R6 is terminal HOLD3cases; answer preserved as combined-astra-r6-hold.md.
Source8bb74806/5c8398f2 replaces QC name guessing with explicit raw diagnostic
requests and derives cadence from bounded interval endpoints (max41points).
Two quick-return fixtures initially failed before cadence assertions. Corrected
production-protocol tests atc5a68e2a reproduced all6 real errors on held9b344665;
`integration-r6-valid-red-state` is terminal RED. All original fixture failures remain.
Source5c8398f2 passes266frontend tests, lint/types and100subscription cadence-bound
checks. Generateda9285257 is published on the pilot topic. `combined-r7-release-state`
completed both full native checks PASS; Linux44729381940 (workflow6d8074f)
all3 jobs PASS. `native-review-r7/state` now owns the fresh
standalone Astra Ultra review. Read its explicit terminal verdict and exact Linux
results before integration. Prior R6 HOLD remains. Quota verified3%.
Never duplicate active workers or clear uncertain claims. Codex3%
remaining, preserve1%; no new duplicate worker. Existing R4 HOLD retained.
Do not integrate while HOLD remains. Codex remains4%, with1% reserved.
All older observations below are historical evidence.

