# Brief: gate-linux-r5 (rewrite, after three HOLD rounds r2, r3, r4)

- Decision: D-GATE1 (below). Parents: briefs/gate-linux.md, r2, r3, r4. Reviews: gate-linux-review, gate-linux-r3-review, gate-r4-review answers (Mac scratch).
- Risk tier: HIGH (the gate itself; never auto-merged under D-REVIEW1)
- Branch: new `gate/linux-actions-r5` off `gate/linux-actions` at the r4 head. Lane: Mac, `-m gpt-6.2-astra` HIGH (not Sol: this is logic that must be right), fresh session, 60 minute cap, scratch `/private/tmp/deepsignal/gate-linux/`
- Why rewrite: three rounds of patching a bash script each closed four findings and the next review found four more. The decision logic is spread across shell and Python, so evidence can be validated in one place and used in another.

## Design (the whole point)
1. One pure Python function `decide(evidence) -> Verdict` in `gate/gate_lib.py` is the ONLY place a verdict is made. The shell script only collects evidence into one immutable JSON file and calls the function once at the end. No verdict logic in shell. No re-reading files after validation: validate the in-memory evidence, decide from the same object.
2. Evidence is a closed schema: requested sha; checkout head sha; changed paths with git object type old and new; the exact pytest command line and the collected test count; JUnit results; deselect and exclude counts; flake8 file list actually passed, exit code and parsed findings; tracked-file hash before and after. Any missing field, wrong type, unknown field or inconsistency is REFUSED.
3. GREEN requires ALL positive proofs: sha reachable from a fork ref and equal to checkout head; collected == run + skipped-with-reason (no deselection from addopts or markers allowed unless the gate itself passed it and recorded the count); every JUnit testcase named, unique, with a classname; flake8 invoked with `--isolated` and an explicit file list, `--exclude=` empty, and every changed .py file appears in its results (lint count per file recorded, zero findings); no path type changes; tracked files byte-identical before and after; Python and OS versions as pinned. Anything else is REFUSED or RED (RED only when the evidence is complete and there is a real test or lint failure).
4. Fail-closed by construction: `decide` starts at REFUSED; there is exactly one code path to GREEN.
5. Closes by design the r4 findings: (1) flake8 exclusion hiding an explicit file; (2) pytest addopts selection with deselected tests; (3) unnamed JUnit testcase; (4) results truncated after validation. Add one regression test per finding PLUS a property test (hypothesis-free: seeded random mutation of a valid evidence object, 2000 mutations) asserting that no mutation of a valid RED or REFUSED evidence object ever produces GREEN, and that dropping or corrupting any single field never produces GREEN.

## Constraints
- Do NOT change `.github/workflows/linux-gate.yml` pins except to call the new entry point. Keep pins (flake8 7.5.0, pytest-timeout 2.4.0), Ubuntu 22.04 check, evidence files.
- Standard library only for the gate code. No sleeps, no swallowed errors, no loosened tests. No sub-agents. No git commit or push (the lead does).

## Acceptance
```
python3.12 -m unittest discover gate/tests
```
Also python3.9 if available. Report: diff summary, test names, RED then GREEN, verified vs inferred, under 40 lines.

## Stop rule (D-GATE1)
If the next Astra ultra review is not PASS, STOP gate work. The Linux gate then ships as ADVISORY only (it runs and prints raw pytest and flake8 results; no GREEN/RED label), and acceptance stays on the Mac and Mini gates. Eugene decides in MORNING whether to invest more.
