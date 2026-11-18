# Visual quality gate for the Console MVP (append to desk design/console-DESIGN.md as "Rulebook v3: visual gate")

Eugene, 2026-11-18 07:32Z: "I need this to be a gorgeous and functional piece of software." Visual quality is a merge gate for the MVP, not a goal. Every line below is checked, with a named test or review.

| # | Criterion | How it is checked | Pass |
|---|---|---|---|
| V1 | Design system match: tokens only | `test_style_lint.py` scans `src/modules/**` and `src/*.tsx` for hex, rgb() and named color literals outside `src/contract` and `lighting*` | zero hits |
| V2 | Type scale | the same lint: font sizes only from 48, 40, 32, 24, 22, 18, 16, 13, 12 px (or the matching tokens) | zero off-scale |
| V3 | Spacing | the same lint: gap, padding and margin values are multiples of 4 px | zero off-grid |
| V4 | Screenshot matrix reviewed side by side before the MVP merge | `test_visual_gate.py` (lead_run) captures every page and route in Day, Dusk, Night red and Night neutral, at 1920x1080 (bridge), 1366x768 (laptop) and 400x800 (phone), against the harness fixture, and writes `contact-sheet.html` | lead review plus an Astra 6.2 visual review, no open "ugly or broken" findings |
| V5 | WCAG AA contrast in Day and Dusk | the same test computes the contrast of every visible text node from computed styles | 4.5:1 for body text, 3:1 for text 24 px or larger and for UI glyphs |
| V6 | No layout shift | PerformanceObserver `layout-shift` over 60 s of live 1 Hz data on each page | CLS < 0.01 after first load |
| V7 | No jank at real data rates | over the same 60 s, with 4 charts on screen: long tasks > 50 ms, and rAF frame times | 0 long tasks; p95 frame time 16.7 ms or less |
| V8 | Smooth state transitions | state changes (LIVE, AGING, STALE, NO DATA, badges, banner rows) animate color and opacity over 150 ms or less; none under `prefers-reduced-motion`; in Night no transition passes through a light color | checked in code review plus a screenshot mid-transition |
| V9 | "Is any sensor bad right now?" answered in 5 s | (a) automatic: with the fixture's failed logger, the stale banner or a non-OK state is visible above the fold on every page at all three sizes; (b) human: 3 people who are not software experts each see Bridge and Health once with one injected fault | (a) passes on every page; (b) 3 of 3 answer correctly within 5 s |

Design-polish pass, 2026-11-22 to 11-24, after integration: one Codex job (Sol 6.2 high, on the Mac, build-side) runs the Impeccable `critique`, `typeset`, `polish` and `audit` steps on the integrated branch. It fixes findings inside DESIGN.md's rules and re-runs V1 to V9. DESIGN.md wins over Impeccable advice.

The Nov 25 MVP report attaches the V4 screenshot set (the contact sheet plus PNGs) and the V5 to V7 numbers.
