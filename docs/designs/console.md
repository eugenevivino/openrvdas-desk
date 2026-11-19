# Design note: Console UI pilot follow-up

Status: approved for the Nov 25 supervised pilot. Launcher unit: `console`. Tickets: T-CON-1 to T-CON-3 and the T-CON-11 test prerequisite.

## Fixed target

For the Nov 25 supervised pilot, the console must display the latest defensible reading status on valid CDS data. A late FAIL for an older reading must preserve the newest usable reading. Returning to a page must retain its learned sample period and report freshness from that period and actual sample age. The Map must show NO DATA when valid coordinates yield no paired track points.

Prove one visible behavior in a real browser for each of the ten shipped console modules. Use the served distribution, production registry and an isolated CDS fixture. Record the exact SHA and the module-specific assertions.

## Acceptance tests

Run from the fork checkout. Name each regression and its valid variation with its ticket ID. Record the failing cases on the pinned base with the new tests applied, then record both passing cases per ticket on the fix.

```sh
cd contrib/deepsignal/console && npm test -- src/cds.test.ts -t T-CON-1
cd contrib/deepsignal/console && npm test -- src/cds.test.ts -t T-CON-2
cd contrib/deepsignal/console && npm test -- src/modules/map/map.test.tsx -t T-CON-3
cd contrib/deepsignal/console && npm test
cd contrib/deepsignal/console && npm run lint
cd contrib/deepsignal/console && npm run type-check
cd contrib/deepsignal/console && npm run build
python3 -m pytest -v contrib/deepsignal/test/console/test_pilot_modules_browser.py
python3 -m pytest -q contrib/deepsignal/test
```

- T-CON-1: feed a late FAIL for an evicted sample through the CDS ingestion path and assert the exposed last-good reading survives. Repeat at a different valid rollover offset.
- T-CON-2: exercise the subscription lifecycle with a learned cadence slower than one second. Switch away and return, then check the freshness calculation at a sample age that should still be healthy. Repeat with a second cadence.
- T-CON-3: render the production Map tile with valid coordinates at different timestamps and assert NO DATA when pairing yields zero points. Repeat with the latitude and longitude arrival order reversed.

## Out of scope

T-CON-4 through T-CON-10 remain tickets. Installer, relay, security redesign, the 24-hour soak and pilot cutover are separate work.

## Prerequisites on trunk

Fork integration was verified remotely at `1dc7a5e001f9535520ac8986922253c2ea20e01e`. Before starting, recheck the head and claims, verify the console source and lockfile, and create an isolated checkout from that integration commit. Keep the checkout detached to avoid the hourly sync. Use the pinned Node dependencies and normal launcher admission. Include the verified T-CON-11 test fix on the candidate. Cover Auto Pages, Bridge, Chart, Example, Health, Kiosk/Night, Map, Number, Self-Test and Stale Banner. Every module needs an assertion against its own observable behavior.

## Who judges

The builder self-checks against the commands, D-FIX1 and D-P1DEF1. Cloud reviewers judge the production diff under D-FASTREV1. The desk Linux job records the gate at the final SHA. The lead handles integration under D-REVIEW1.
