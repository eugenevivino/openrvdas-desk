# Brief: gate-linux-r4 (fix round 3, after the r3 Astra ultra review: HOLD)

- Decision: D-ARCH5 (Linux only). Parents: briefs/gate-linux.md, gate-linux-r2.md, gate-linux-r3.md
- Risk tier: HIGH (the gate itself is critical under D-REVIEW1; never auto-merged)
- Branch: continue `gate/linux-actions` in the desk repo, base = r3 head da72a75 or later
- Lane: `mac`. `-m gpt-6.2-sol` high via `~/bin/ds-codex`, fresh session, under 40 turns, 45 minute cap
- Scratch: `/private/tmp/deepsignal/gate-linux/` (rule 28). Pull the branch first.
- Review that produced this: `/private/tmp/deepsignal/gate-linux-r3-review/answer.md` (Astra ultra, HOLD, 4 new P1)

## Why a structural round
r2 and r3 each closed four findings and the review found four new ones. Patching line by line is whack-a-mole.
Make the script fail closed by construction, then fix the four findings as consequences.

## Design rule (do this first)
Verdict starts as REFUSED. It becomes GREEN only when every positive proof below has been recorded, and RED only
when proofs are complete and a real test or style failure exists. Any missing, malformed or interrupted evidence stays REFUSED.
Proofs: (a) sha reachable from a fork ref and checkout verified, (b) every changed path classified (regular file, deleted, or
refused), (c) suite output parsed and validated BEFORE any row is recorded, (d) flake8 finished with exit 0 or 1 and a
complete result, (e) tracked files byte-identical to the requested commit after install, tests and lint (git diff --quiet
plus git status --porcelain clean of tracked changes).

## Findings (each needs a test that FAILS first)
1. P1, gate-linux.sh:30/59, `record_suite` appends rows before validating, so a malformed suite ending in `__END__ PASS`
   can flip REFUSED to GREEN. Parse and validate the whole suite output into a temp structure, then record rows only if valid.
   Test: malformed rows then `__END__ PASS` stays REFUSED and records no rows.
2. P1, :91, a path `x.py` replaced by a directory `x.py/` appears as a delete plus children and the AMRT filter misses it.
   Classify by the commit's tree: for every path in the diff (including D), compare the old and new git object types
   (`git ls-tree`); any type change (file to tree, tree to file, symlink, submodule) is REFUSED with a plain message.
   Test: x.py to x.py/ never GREEN.
3. P1, :157, flake8 7.5.0 exits 1 on KeyboardInterrupt or interruption and that reads as RED with lint incomplete.
   Require the complete-run signal: run flake8 with `--exit-zero --format=...` plus `--statistics`/own sentinel and
   decide RED from parsed style codes only; non-zero exit with no parsed result, or any E902/E9xx, is REFUSED.
   Test: simulated interruption gives REFUSED, real E501 gives RED.
4. P1 (INFERRED), :148/165, in-place rewrite of a tracked .py during install or tests means lint checks different bytes.
   After install and after tests, and again before lint, verify `git diff --quiet` and no modified tracked files
   (record `git ls-files -s` hash before and after); lint a fresh `git archive` export of the sha, not the working tree.
   Test: a test that rewrites a tracked .py during the run is REFUSED.

## Constraints
- Do NOT change `.github/workflows/linux-gate.yml` or pinned action SHAs. Keep pins (flake8 7.5.0, pytest-timeout 2.4.0), the Ubuntu 22.04 check and evidence files.
- No loosened or deleted tests, no swallowed errors, no sleeps. Incomplete evidence is never GREEN or RED.
- No sub-agents. No git commit or push (the lead does).
- Also add one property-style test: random garbage in suite output, changed list and flake8 output never yields GREEN.

## Acceptance
```
python3.12 -m unittest discover gate/tests
```
Also run on python3.9 if available. flake8 on `gate/`, compare E501 count with the baseline of 30 in untouched files.

## Report format
Diff summary, test names, RED then GREEN output, verified vs inferred, under 40 lines.

## Stop rule
Red after this round: stop and report. Then Eugene decides in MORNING (the gate stays unmerged; module checks keep using the Mac and Mini gates).

## Result (builder fills in)
- Head sha:
- RED receipt:
- GREEN receipt:
- What changed, in three lines:
- Open questions:
