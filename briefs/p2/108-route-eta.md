# Brief: p2-route-eta (Routes and waypoints (ETA, bearing, off-course))

- Decision: D-PARITY1, IDEAS #108 (Eugene approved building #104-#124, 2026-11-18)
- Risk tier: medium
- Module: exactly one. Branch `deepsignal/p2-route-eta` from `deepsignal/console-contract`
- Lane: `mac`: `gpt-6.2-astra`, `model_reasoning_effort=high`, `KALON_ALLOW_ASTRA=1` (math; Eugene rule 2026-11-18)
- Fresh session, under 40 turns
- Upstream home: console, fork only
- Value (techs/science/shore): 3/4/3
- Depends on: console contract; drawing routes on the map is a later change to #107 `map`, not this task
- Mac scratch path: `/private/tmp/deepsignal/p2-route-eta/` only (rule 28)

## Goal
The bridge and science watch see distance, bearing, time to go and ETA to the next station and to the end
of the route, and a plain "Check waypoint" warning when the ship is heading away from it.

## Build
- Pure math in `src/modules/route/geo.ts` (no imports from the rest of the console), used by the tile.
- Route source: `routes.json` next to the bundle (GeoJSON `LineString` or a list of
  `{name, lat, lon}`), loaded once with a plain message if missing or invalid; a setting `route` names
  the file. Tile `route` with settings `lat`, `lon`, `cog`, `sog` (knots) field names.
- Shows: next waypoint name, distance (nm, 1 decimal), bearing (degrees true, 0 decimals), cross-track
  distance (nm, "port" or "starboard"), time to go and ETA (UTC) to the next waypoint and to the route end.
- Waypoint arrival: within 0.1 nm the next waypoint becomes active. The active index never moves back.
- SOG under 0.5 knots: "No ETA: speed under 0.5 kn" instead of a time.
- Off-course: |bearing to next waypoint minus COG| (wrapped to 0..180) over 45 degrees for more than 60 s of
  record time gives "Check waypoint" (MetAcq CHK WPT rule). Uses `ctx.clock.now()` only.

## Pinned math (implement exactly; do not substitute another model)
Sphere radius R = 6371008.8 m. 1 nm = 1852 m. Angles in degrees at the API, radians inside.
- Distance (haversine): d = 2R asin( sqrt( sin^2((phi2-phi1)/2) + cos phi1 cos phi2 sin^2((lam2-lam1)/2) ) ).
- Initial bearing: theta = atan2( sin(dlam) cos phi2, cos phi1 sin phi2 - sin phi1 cos phi2 cos dlam ),
  normalized to [0, 360).
- Cross-track distance of point 3 from the leg 1 to 2: xt = asin( sin(d13/R) sin(theta13 - theta12) ) R.
  Negative means port (left of the leg in the direction of travel), positive means starboard.
- Remaining route distance = distance to the next waypoint + sum of the remaining leg lengths.
- ETA = now + remaining distance / (SOG x 1852 / 3600).

## Test vectors (from the pinned formulas; must match to the stated precision)
| From (lat, lon) | To (lat, lon) | Distance m (0.01) | Bearing deg (0.0001) |
|---|---|---|---|
| 0, 0 | 0, 1 | 111195.08 | 90.0000 |
| 50.0359, -5.4253 | 58.3838, -3.0412 | 940948.93 | 8.5220 |
| 32.7, -117.2 | 21.3, -157.9 | 4198112.76 | 262.8775 |
| 10, 179.5 | 10, -179.5 | 109505.74 | 89.9132 |

Cross-track, leg (0,0) to (0,1): point (0.01, 0.5) gives -1111.95 m (port); point (-0.01, 0.5) gives
+1111.95 m (starboard), to 0.01 m.

## Tests first
`geo.test.ts`: every vector above; bearing normalization; the antimeridian pair.
`route.test.tsx` with the fake feed and a fake clock: arrival advances the waypoint and never goes back;
ETA text; speed under 0.5 kn; off-course after exactly 60 s, not 59 s; missing routes file message; stale
position shows age and no ETA.

## Scope
`contrib/deepsignal/console/src/modules/route/**`, `contrib/deepsignal/console/docs/route.md`.

On the Mac: run `npm ci` in `contrib/deepsignal/console` before testing (network allowed there for npm only).

## Rules every console task follows

Read these files in the repository first: `contrib/deepsignal/console/CONTRACT.md`, `contrib/deepsignal/console/src/contract/index.ts`, `contrib/deepsignal/console/DESIGN.md` (the "Rulebook v2 additions" section wins over v1 where they differ). The contract is fixed: never edit `src/contract/**` or `CONTRACT.md`. If the contract blocks you, stop and say exactly what you need.

Ownership: you own ONLY the paths listed under Scope. Everything else is read-only, in particular `src/registry.ts`, `src/App.tsx`, `src/main.tsx`, `src/cds.ts`, `src/store.ts`, `src/lighting*.ts`, `src/pages.ts`, `src/index.css`, `index.html`, `package.json`, `package-lock.json`, `vite.config.ts`, `tsconfig*.json`, `.oxlintrc.json`, `DESIGN.md`, `README.md`, `public/**`, `dist/**`, `demo_cache.py`, `contrib/deepsignal/configs/**`, other modules' folders, and `contrib/deepsignal/test/console/test_console_live.py`. No new dependency of any kind.

Your module is `src/modules/<id>/index.ts` default-exporting a `ConsoleModule` (types in the contract). Core discovers it by glob; do not register it anywhere. If core's registry is not on your branch yet, that is expected: your tests import your module directly.

Tests: Vitest on jsdom, beside your code (`src/modules/<id>/*.test.ts(x)`). Build a minimal fake `ConsoleContext` inside your own folder (for example `src/modules/<id>/testkit.ts`) from `src/contract/fake-feed.json`, with a fake clock you step. Cover every behavior named in this brief. Use only `ctx.clock.now()` for time.

Screens: word + shape for every state, color third; tokens only (`--bg --panel --panel2 --line --fg --muted --accent --ok --check --stale --down --chart --grid` and fonts `--f-number --f-body --f-mono`), never literal colors; canvas/SVG read tokens at draw time and redraw on `ctx.lighting.subscribe`; Night must never paint a light surface (empty, loading and error states included); plain English, units always shown; touch targets at least 44 px; bridge sizes: primary value 48 px, labels at least 18 px, metadata at least 16 px; render all data as text (no `innerHTML`, no `dangerouslySetInnerHTML`, no `eval`).

Browser checks: Chromium does not run in this sandbox. If the brief asks for a browser test, write it as `contrib/deepsignal/test/console/test_<id>_browser.py`, mark it `@pytest.mark.lead_run`, make it skip with reason "browser test, run by lead outside the sandbox" when Playwright is not importable, and list it in your report.

`dist/` is rebuilt once at integration. Prove the build works, then restore it before committing.

Banned: loosening, skipping or deleting existing tests; swallowed errors; sleeps or timers for test ordering; refactors, renames or formatting outside your scope.

Docs: write `contrib/deepsignal/console/docs/<id>.md` for a ship tech: what it does in one sentence, how to turn it on or configure it (copy-paste example), how to see it working, what it does NOT do.

## Acceptance (run from `contrib/deepsignal/console`, paste the tails)
```
npx oxlint && npx tsc -b --noEmit
```
```
npx vitest run
```
```
npm run build && git checkout -- dist && git clean -fdq dist
```

## Result (builder fills in)
- Head sha:
- RED receipt:
- Acceptance tails:
- Open questions:
