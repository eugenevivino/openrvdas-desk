# Nov 25 supervised pilot console review, November 20

The product candidate is `da4aa5ec9da9c59c000c0795981e0664bb5f483c`, based on `bff54ec722bd8bf2c0ee949c91528642e0140e26`. The release covers the ten console modules in the approved design. The tests serve the packaged browser app against an isolated replay. Ship deployment and the 24-hour soak are separate. [Fork PR #3](https://github.com/eugenevivino/openrvdas/pull/3)

## What the operator sees

In the tested cases, returning to the depth page preserves the last usable measurement even if the server has trimmed its copy. The tile displays `NO DATA` and `Last: 18 m at 12:00:00Z` after newer measurements fail quality checks. Revoking 18 m clears the line. A fresh usable reading restores the live display. Turning off graph history leaves these behaviors available.

| Regression on the production client | On b19dde0 | On da4aa5e |
| --- | --- | --- |
| Shorter backfill and two late failures | Failed | Passed |
| Shorter backfill and three late failures across batches | Failed | Passed |
| Zero graph history and three late failures after 24 nulls | Failed | Passed |
| Zero graph history, page return and five late failures after 30 nulls | Failed | Passed |
| A quality failure survives flag rollover until the measurement itself expires at the 10,000-point cap | Failed | Passed |

These five tests exercise the production client/store with a WebSocket test double. The four operator-display tests mount the production app. A separate Chromium suite serves the generated distribution and checks every module.

## Machine checks

- Mac passed all nine design commands and the static checklist. The full run passed 197 frontend tests in 24 files, 206 Python tests together, and 84 additional installer/server cases. The launcher recorded the results against da4aa5e.
- All three hosted jobs passed. Ubuntu passed 197 frontend cases, 207 console and replay cases, 204 installer/security cases and two real nginx configurations. Source loss and recovery passed on two fresh fixture starts. The workstation demo passed over HTTP and HTTPS. [Candidate Linux receipt](https://github.com/eugenevivino/openrvdas-desk/actions/runs/44695593537)
- The installed scanner policy matched all 188 raw Bandit findings to previously reviewed sites. The Mac Python dependency audit passed.
- Ten visible Chromium behaviors passed on each OS. Auto Pages built a bridge page, Bridge changed dial orientation, Chart plotted history and updated quality, and Example showed both configured weather readings. Health showed logger failure and recovery, Kiosk/Night required a held exit, Map recovered from unpaired coordinates, Number distinguished failed and missing quality, Self-Test showed logger and cruise mode, and Stale Banner named the sensor and cleared on recovery.

Mac evidence is under `/private/tmp/deepsignal/pilot-combination-20261120/` in `page-return/red-final.log`, `page-return/green.log`, `page-return/checks.log`, and `return-qualification/{self-check.xml,expanded.xml}`. The installed receipts are `/private/tmp/deepsignal/receipts/{self-check,pre-review}-da4aa5e.txt`.

## Independent reviews

Both cloud reviewers passed the candidate with zero blocking P1 findings. They reviewed the logic and UI separately. Their environments lacked the optional scanner tools. The official Mac and hosted Linux gates supplied the scanner results above.

The logic reviewer raised one portability follow-up for the replay fixture's POSIX file lock. The Mac run exercised the fixture successfully. Windows fixture support remains unverified and lies outside this pilot. The UI reviewer raised no follow-ups. Review records are in `return-review/cloud/`.

Astra Ultra issued HOLD on the same candidate. The following three outcomes were inferred by tracing stock CDS and production browser code. They have no failing runtime receipts in this round.

1. With zero graph history, leave after 18 m/PASS. While away, CDS receives 19 m/FAIL at +10 s and 20 m at +20 s. On return it can supply 20 m and the +10 s flag without the intervening 19 m reading. The browser assigns that flag to 18 m. A later failure of 20 m then clears the last-reading line.
2. Start with 18 m/PASS at noon and 19 m/FAIL at +1 s. Another FAIL arrives at +1.75 s, then a null at +2 s. A delayed 20 m reading stamped +1.5 s is first seen in backfill. After 84 minutes of 1 Hz null readings and 2 Hz MISSING flags, the browser can discard the +1 s FAIL. Inserting 20 m splits the old interval, moves the retained FAIL to 20 m and makes 19 m appear usable.
3. On a field with a learned 30-second cadence and 600 seconds of history, leave and return while the same CDS request is pending. An empty response can leave a ten-second-old 18 m/PASS reading showing NO DATA until the next update.

The release remains on fork integration bff54ec, with PR #3 in draft. The one extra correction round is complete and its claim is released. A further implementation needs a new scope decision. The proposed next brief should specify how to handle missing measurement intervals, retain explicit failures when backfill adds a timestamp, and restore freshness during quick navigation. Start with three red operator-display regressions and one valid variation for each. The full source-trace verdict is in `return-decision/answer.md`.
