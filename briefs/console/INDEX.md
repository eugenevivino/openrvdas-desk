# Console MVP cloud tasks (2026-11-18)

| Task | Branch | Base | Attempts | Needs | Wave |
|---|---|---|---|---|---|
| auto-pages | `deepsignal/console-mod-auto-pages` | `deepsignal/console-contract` | 2 | node | 1 |
| bridge | `deepsignal/console-mod-bridge` | `deepsignal/console-contract` | 3 | node | 1 |
| charts | `deepsignal/console-mod-chart` | `deepsignal/console-contract` | 2 | node | 1 |
| core-v2 | `deepsignal/console-core-v2` | `deepsignal/console-core` | 3 | node | 2 (after Mac v2 push) |
| fixture | `deepsignal/console-harness-fixture` | `deepsignal/console-contract` | 2 | python | 1 |
| health | `deepsignal/console-mod-health` | `deepsignal/console-contract` | 2 | node | 1 |
| install | `deepsignal/console-install` | `deepsignal/console-contract` | 2 | node | 1 |
| kiosk-night | `deepsignal/console-mod-kiosk-night` | `deepsignal/console-contract` | 2 | node | 1 |
| soak | `deepsignal/console-harness-soak` | `deepsignal/console-harness-fixture` | 1 | python | 2 (after fixture) |
| source-loss | `deepsignal/console-harness-source-loss` | `deepsignal/console-harness-fixture` | 2 | python | 2 (after fixture) |
| map | `deepsignal/console-mod-map` | `deepsignal/console-contract` | 2 | node | 1 (MVP only if green by 11-21, else stretch) |
| stale-banner | `deepsignal/console-mod-stale-banner` | `deepsignal/console-contract` | 2 | node | 1 |

Prompt files: `briefs/cloud/console-<task>.md` (header + full brief). Briefs alone: `briefs/console/<task>.md`.

Wave 1 can go now, all in parallel (disjoint files): chart, health, bridge, auto-pages, stale-banner, kiosk-night, install, fixture.
Wave 2: core-v2 once the Mac v2 job has pushed deepsignal/console-core (or now on 5682671 if that job fails); soak and source-loss once fixture is pushed.

Environment: node tasks need Node >= 22 and `npm ci` run in `contrib/deepsignal/console` during setup (lockfile from the branch). Python tasks need OpenRVDAS requirements plus pytest and flake8.

Cannot run in cloud (lead runs outside the sandbox): every `@pytest.mark.lead_run` browser test (test_console_live extensions, test_bridge_browser, test_source_loss_browser), the real 24 h soak, Night luminance and onboard checks.

Integration (lead, after wave 2): merge module branches into core-v2 in any order (disjoint), rebuild dist once, run the full suite plus lead_run tests, Astra 6.2 review of the merged diff, Impeccable audit in all four lighting modes.

D-SETUP1 (first light in 10 minutes or less, 3 or fewer actions): the console's part is the install task (install.sh plus the self-test page). Its docs must show the 3 actions: run install.sh, open /console/, read the self-test page.
