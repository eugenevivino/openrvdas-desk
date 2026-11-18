# Brief: gate-linux-r3 (fix round 2, after the r2 Astra review: HOLD)

- Decision: D-ARCH5 (Linux only). Parent briefs: briefs/gate-linux.md, briefs/gate-linux-r2.md
- Risk tier: medium
- Module: none (desk tooling). Branch: continue `gate/linux-actions` in the desk repo
- Lane: `mac`. `-m gpt-6.2-sol` high via `~/bin/ds-codex` (rule 27), fresh session, under 40 turns, 45 minute cap
- Mac scratch path: `/private/tmp/deepsignal/gate-linux/` (rule 28). `git pull` the branch there first.
- Base: `gate/linux-actions` at 6fe3aba or later (code last changed at 292117e)
- Review that produced this brief: `/private/tmp/deepsignal/gate-linux-review/answer.md` (Astra high, read-only, HOLD)

## Goal
Close the four review findings so the Linux gate can merge to `main` and run for real.
A gate that can be fooled into GREEN, or that gives RED where it should REFUSE, is worse than none.

## Findings to fix (each needs a test that FAILS first)
1. P1, gate/gate-linux.sh near line 81: the changed-file list uses `--diff-filter=AMR`, so a git
   type change (T), for example a symlink replaced by a real `.py` file or the reverse, escapes lint
   and can still end GREEN. Include T. Also: if a changed `.py` path is not a regular file in the
   checkout (symlink, directory, missing), the run is REFUSED with a plain-English message.
2. P1, near line 124: flake8 exiting with E902 (for example FileNotFoundError, unreadable file) is
   counted as a lint violation and gives RED. A flake8 that could not read the file must be REFUSED,
   never RED and never PASS. Only real style codes (not E902) become FAIL rows.
3. P1, near line 79: the check only proves the commit shares ancestry with `origin/dev`, so a
   fetchable outside commit can pass. Require that the sha is reachable from a ref of the fork
   checkout itself (`refs/remotes/origin/*` after the fork fetch), and that `verify_checkout` still
   passes. Refuse with a clear message otherwise. State in the report exactly which rule you chose and why.
4. P2, near line 127: filenames go into the TSV as is, so a tab or newline in a path corrupts a row
   and the verdict becomes REFUSED for the wrong reason. Either refuse up front with the message
   "unusual characters in a changed file name: <escaped path>" or escape the path consistently in
   every row and the changed.txt evidence. Pick one, say which.

## Failing test first
Add tests to `gate/tests/test_gate_linux.py` for each finding, run them against the current script,
paste the RED output, then fix. A test that already passes before the fix does not count as
coverage for that finding: say so.

## Constraints
- Do NOT change `.github/workflows/linux-gate.yml` or the pinned action SHAs.
- Keep the pins (flake8 7.5.0, pytest-timeout 2.4.0), the Ubuntu 22.04 check and the evidence files.
- No loosened or deleted tests, no swallowed errors, no sleeps. Incomplete evidence is never GREEN or RED.
- Do not spawn sub-agents. Do not run git commit or push (the lead does).

## Acceptance (exact commands)
```
python3.12 -m unittest discover gate/tests
```
Also run it on python3.9 if available (the MacBook default) and say so. Run flake8 on `gate/` if
installed and compare the E501 count with the baseline of 30 in untouched files.

## Scope
`gate/gate-linux.sh`, `gate/gate_lib.py` only if needed, `gate/tests/test_gate_linux.py`.

## Report format
Diff summary, test names, RED then GREEN output, verified separate from inferred, under 40 lines.

## Stop rule
Two fix rounds still red: stop and report.

## Result (builder fills in)
- Head sha:
- RED receipt:
- GREEN receipt:
- What changed, in three lines:
- Open questions:
