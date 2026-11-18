# DeepSignal Console design rulebook (DESIGN.md seed)

Source of truth for every console module. Copy into `contrib/deepsignal/console/DESIGN.md`
in console-core. Impeccable (`impeccable document`) may extend it; where Impeccable
advice conflicts with a rule here, this file wins.

Reference mockup: https://claude.ai/artifact/4vb6aXecBRQdT3k5XuXxGq (HTML copy in
project files `deepsignal-console/deepsignal-console.html`). Proposal:
https://claude.ai/artifact/XQFbM1ToqgwdbLha6Ek72z

## Lighting modes (all colors are tokens; components never use literal colors)
| Token | Day | Dusk | Night red (at dim 1.0; scale every channel by dim) |
|---|---|---|---|
| --bg | #e9eef0 | #081014 | #000000 (fixed) |
| --panel | #ffffff | #0e191f | #050000 (fixed) |
| --panel2 | #f3f6f7 | #132229 | #0a0000 (fixed) |
| --line | #c9d3d7 | #1f323b | rgb(70,8,4) |
| --fg | #0a151a | #dde8ec | rgb(255,38,16) |
| --muted | #4c5f68 | #8aa2ad | rgb(150,24,10) |
| --accent | #006a7c | #56c3d3 | rgb(255,38,16) |
| --ok / --check / --stale / --down | #1d7f50 / #a86a00 / #6b5bb5 / #b3261e | #4cc38a / #e5b440 / #a99cf0 / #ff6b5e | fg / fg / muted / rgb(255,60,30) |
| --chart / --grid | #006a7c / #d8e0e3 | #56c3d3 / #18282f | fg / rgb(40,4,2) |

Night red rules:
1. Every pixel has G and B at most 15% of R. Includes canvas charts, SVG, map, scrollbars
   (`color-scheme: dark`), inputs, focus rings, dialogs, toasts, loading states.
2. Dimmer 15-100%, default 60%, stored per screen (localStorage), applied by rewriting tokens.
3. Never a white or light frame: the first paint already uses the stored mode (inline boot
   script in index.html before CSS loads); no light default flash on load or route change.
4. One Night button in the top bar on every page, plus key N. Keys 1-9 switch pages.

## State
Four states, always word + shape + color: OK (filled circle), Check (filled triangle),
Stale (hollow square), Down (cross). Never color alone. Stale values are shown at 45%
opacity with a strike-through and "last seen <age> ago". Gaps in charts are gaps.

## Type
Numbers and labels: Barlow Semi Condensed 600. Body: Barlow. Ages and field names: IBM Plex Mono.
Fonts are bundled files (no Google Fonts at runtime). Big value 56px, medium 40px,
label 13px uppercase +0.08em tracking, tabular numerals everywhere digits appear.

## Layout
Sticky top bar: brand + ship name, page tabs, live/age pill, UTC and ship clock,
Day/Dusk, Night, dimmer (Night only). Tiles on a CSS grid, auto-fill minmax(220px,1fr),
wide = 2 columns, collapse to 1 column under 520px. Touch targets >= 44px.

## Words
Plain English, units always shown, sentence case labels, no unexplained acronyms
in UI copy (field names only in mono "source" lines).

---

# Rulebook v2 additions (2026-11-18, from Eugene's human-factors research report)

Source: Eugene's "Research-Vessel Monitoring Dashboard: Human-Factors Design Decision
Document" (project chat 2026-11-18 06:03Z). Its citations are leads, not verified facts.
Where v2 conflicts with v1 above, v2 wins.

## Identity
- Persistent low-salience label in the top bar: "Research system monitoring".
- Never claim or imitate ECDIS, radar or bridge alert management. Never use the words
  "navigation alarm", "safe" or "clear to proceed".
- The console is disposable relative to acquisition: a console crash or bad page file must
  never affect logging (it is read-only against the cache already).

## Four independent state axes (never one traffic light)
| Axis | States | Shape and word |
|---|---|---|
| Sensor health | OK, DEGRADED, FAILED, UNKNOWN | from logger status |
| Data quality (QARTOD flags 1,2,3,4,9) | PASS, NOT EVALUATED, SUSPECT, FAIL, MISSING | from `<field>_QC` when present, else NOT EVALUATED |
| Freshness | LIVE, AGING, STALE, NO DATA | computed in the console |
| AI | NONE, ANNOTATION, SUGGESTION, CONCERN | separate, subordinate |
A tile may show all four. UNKNOWN health never becomes FAIL quality. Each state has a word
and a shape; color is third. Normal states recede; exceptions stand out.

## Freshness (replaces v1 "stale after 30 s")
- Each field has an expected period T: from page file `period`, else learned as the median
  interval of the last 20 samples.
- LIVE: age <= 2T (age compact). AGING: 2T to 5T (age label "18 s old"). STALE: > 5T
  (value stays, marked STALE with age). NO DATA: past a hard timeout (default 60T, min 5 min):
  value replaced by "—", last good shown separately: "Last: 34.812 PSU at 03:14:22Z".
- Never show staleness by fading or strike-through alone. Word + age always.
- Keep source timestamp and receive time separately; shore views show both (source age vs link delay).

## Alerts
Tiers: A1 Critical, A2 Warning, A3 Caution, A4 Advisory, plus log-only. A1/A2 need ack and
must say what happened, source, consequence, age, first action. One root cause, one alert
(children grouped under it). Shelving is visible, time-limited and logged.
No browser audio by default anywhere; bridge audio only if the vessel's alarm philosophy allows.
Flashing only for unacknowledged A1. No other animation in Night.
(Alert engine is a later module; console-core only reserves the banner slot.)

## AI annotations
Visually subordinate to QC and alerts (smaller, dashed outline, labelled "AI suggestion").
Show model and version, time, data used, conclusion, confidence if meaningful, evidence link,
recommended action, and buttons Agree / Disagree / Not enough evidence. All dispositions logged.
AI confidence never sets severity.

## Night modes
Two palettes behind the one Night button; the ship sets which one the button uses
(Eugene's decision pending, see thread). Both: background #000000, no large luminous
surfaces, borders not filled cards, dimmer, persisted locally, and no bright frame on load,
refresh, route change, modal, loading skeleton, websocket disconnect, error page, tooltip or
login expiry.
- Night neutral (report table): surface #080808, secondary #111111, text #B8B8B8, critical
  value #E0E0E0, alarm #FF5A5A, warning #FFD45A, pass #72B486, unknown #A0A0A0, missing
  #8D8D8D, AI #8CA0B5.
- Night red: v1 table. Alarm vs normal is carried by shape, word, border weight and
  brightness only, since hue cannot carry it.
Hex is not luminance: acceptance needs a luminance meter on each bridge display class
(targets: surfaces <= 0.2-0.35 cd/m2, text about 1-2.5, nothing critical below about 0.1).

## Bridge sizes (CSS px, then verify physically at 1 to 1.5 m)
Primary value 32-48, alert title 24-32, section heading 22-28, label 18-22, metadata >= 16,
targets >= 44x44. Bridge page fits one screen with no scrolling.

## Personas (default pages)
Bridge: one-screen glance, highest abnormal state, freshness, trend direction.
Tech: health matrix, active alerts, root cause, logs, recovery.
Science: parameter groups, time series, QC filters, provenance.
Shore: fleet/cruise overview, source age vs link delay, event history.
Three density levels: glance, summary, diagnostics (behind a tap).

## Release gate
The bridge view is not "production-ready" until the onboard test in
`docs/ONBOARD-TEST.md` passes on real bridge hardware.

## Rulebook v3: visual gate

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
