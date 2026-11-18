You are building ONE piece of the DeepSignal Console, a display overlay on OpenRVDAS, on Eugene's own fork. Work only in this repository (eugenevivino/openrvdas). Do NOT touch, open pull requests against, or push to OceanDataTools or any upstream repository. Nothing here is sent upstream.

Branches: create branch `deepsignal/console-visual-gate` from `origin/deepsignal/console-contract` (if `deepsignal/console-visual-gate` already exists on origin, check it out instead). Commit your work on that branch only, with one clear commit message, and leave it pushed to origin `deepsignal/console-visual-gate`. Do not touch any other branch, `dev` or `master`. If you cannot push, leave the commit on the branch in your task and say so.

Environment notes: Python only; Node is not needed. Use `python3.12` if it exists, otherwise `python3` (3.11 or newer). If pytest is missing use `python3 -m unittest`. If flake8 is missing, `pip install flake8` into a throwaway venv and say you did. Add no dependency of any kind. No network.

Write the failing test first and paste its RED output, then make it GREEN. Run every acceptance command at the end and paste the tails. Report under 40 lines: files changed, test names, RED then GREEN tail, acceptance results, any design point you disagree with (do not change a design silently), what you verified versus inferred, and what must run outside the sandbox.

Stop rule: two fix rounds still red means stop and report.

The full brief follows.

----------------------------------------------------------------

# Brief: console `visual-gate` (style lint, screenshot matrix, contrast, layout shift and jank checks)

- Decision: D-CONSOLE1, Eugene 2026-11-18 07:32Z: "gorgeous and functional". Visual quality is a merge gate. Risk tier: low (test tooling only). Python only; no Node changes.

## Goal
Every page can be proven to match the design system and to stay smooth at real data rates, with a screenshot set a person can review in one sitting.

## Build
1. `contrib/deepsignal/test/console/test_style_lint.py` runs in the cloud and needs no browser. It scans `contrib/deepsignal/console/src/**/*.{ts,tsx,css}`, excluding `src/contract/**`, `src/lighting*`, `src/index.css` and test files, and fails on:
   - Color literals: `#rgb`, `#rrggbb`, `#rrggbbaa`, `rgb(`, `rgba(`, `hsl(`, and CSS named colors used as values.
   - Font sizes not in {48, 40, 32, 24, 22, 18, 16, 13, 12} px.
   - gap, padding or margin px values that are not multiples of 4.
   Each failure is printed as `file:line: what, why, the token to use instead`. An allow-list file is supported, `contrib/deepsignal/console/style-lint-allow.txt`, with one `file:line reason` per line. It is empty by default.
2. `contrib/deepsignal/test/console/test_visual_gate.py`, `@pytest.mark.lead_run` (it skips with the reason "browser test, run by lead outside the sandbox" when Playwright is not importable). It uses the harness fixture if `contrib.deepsignal.test.harness.fixture` exists on the branch under test, else `contrib/deepsignal/console/demo_cache.py`. It serves `dist/` on a loopback port.
   - Screenshots of every page and route listed by the app (read the tab bar) in Day, Dusk, Night red and Night neutral, at 1920x1080, 1366x768 and 400x800. Saved to `--visual-out` (default `./visual-gate-out/`) as `<page>__<mode>__<w>x<h>.png`.
   - `contact-sheet.html` in the same folder. It is one grid per page: modes across, sizes down, image-relative links, no external assets.
   - Contrast: Day and Dusk only. For every visible text node, compute the contrast from computed color and background, walking up to the first opaque background. Rule: 4.5:1, or 3:1 at 24 px and above. Write a `contrast.json` listing failures, and fail the test if there are any.
   - Layout shift and jank: on each page, run 60 s of live data and collect `layout-shift` entries (CLS) and `longtask` entries, plus rAF frame times. Write `motion.json`. Fail if CLS >= 0.01, if there is any long task over 50 ms, or if p95 frame time > 16.7 ms.
   - Above-the-fold fault check (V9a): with the fixture's failed or stale logger, assert a banner row or a non-OK state badge lies inside the viewport on every page at all three sizes.
   - A `summary.json` with pass/fail per criterion (V4 captured, V5, V6, V7, V9a).
3. `contrib/deepsignal/test/console/VISUAL-GATE.md`: what each check proves, how to run it (`python3 -m pytest contrib/deepsignal/test/console/test_visual_gate.py -m lead_run --visual-out <dir>`), and how to read the contact sheet.

## Tests first
- `test_style_lint.py` has unit tests for its own scanner on inline sample strings: it catches a hex color, `rgba()`, a 15 px font, and a 10 px gap, and it allows `var(--fg)`, 16 px, 12 px gaps and allow-list entries. Then it runs on the real tree. On the contract base the real-tree scan must pass; if it does not, list the hits in your report and do not edit files outside your scope.
- `test_visual_gate.py`: unit-test the pure helpers (contrast ratio math against WCAG reference pairs, CLS summation, p95) without a browser. The browser part is lead_run.

## Scope
`contrib/deepsignal/test/console/test_style_lint.py`, `contrib/deepsignal/test/console/test_visual_gate.py`, `contrib/deepsignal/test/console/VISUAL-GATE.md`, `contrib/deepsignal/console/style-lint-allow.txt`. Add a `--visual-out` option via `pytest_addoption` in a new `contrib/deepsignal/test/console/conftest_visual.py` loaded with `pytest_plugins` from your test file. Do not edit any existing conftest.

## Acceptance (repo root)
```
python3 -m pytest contrib/deepsignal/test/console/test_style_lint.py contrib/deepsignal/test/console/test_visual_gate.py -v
```
```
flake8 contrib/deepsignal/test/console/test_style_lint.py contrib/deepsignal/test/console/test_visual_gate.py contrib/deepsignal/test/console/conftest_visual.py
```
