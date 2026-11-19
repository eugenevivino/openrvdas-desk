# Units and superseded branches (D-PIPE1 rules 2 and 3)

Stamps and counts: `python3 tools/finish-line.py` (manifest `docs/units.json`). Regenerate the manifest
only from logged evidence at the exact head; never mark a stamp without evidence.

## SUPERSEDED-BY-UNIT

These branches never block a unit. Fold one in only if its unit needs the fix; retire after the unit lands.

| Branch | Head | Status | Unit |
|---|---|---|---|
| `deepsignal/console-contract` | 4bfd755 | SUPERSEDED-BY-UNIT | console-ui |
| `deepsignal/console-core` | 82ec7ca | SUPERSEDED-BY-UNIT | console-ui |
| `deepsignal/console-core-v2` | 2ebdf91 | SUPERSEDED-BY-UNIT | console-ui |
| `deepsignal/console-core-v2-a` | 82ec7ca | SUPERSEDED-BY-UNIT | console-ui |
| `deepsignal/console-core-v2-b` | 82ec7ca | SUPERSEDED-BY-UNIT | console-ui |
| `deepsignal/console-core-v2-c` | 82ec7ca | SUPERSEDED-BY-UNIT | console-ui |
| `deepsignal/console-harness-fixture` | 307ba2b | SUPERSEDED-BY-UNIT | console-ui |
| `deepsignal/console-harness-soak` | ca98149 | SUPERSEDED-BY-UNIT | console-ui |
| `deepsignal/console-harness-source-loss` | 307ba2b | SUPERSEDED-BY-UNIT | console-ui |
| `deepsignal/console-install` | c32b6c9 | SUPERSEDED-BY-UNIT | console-ui |
| `deepsignal/console-mod-auto-pages` | bc6c864 | SUPERSEDED-BY-UNIT | console-ui |
| `deepsignal/console-mod-bridge` | 585ca4c | SUPERSEDED-BY-UNIT | console-ui |
| `deepsignal/console-mod-chart` | f24f23b | SUPERSEDED-BY-UNIT | console-ui |
| `deepsignal/console-mod-health` | 991e456 | SUPERSEDED-BY-UNIT | console-ui |
| `deepsignal/console-mod-kiosk-night` | ed61d5f | SUPERSEDED-BY-UNIT | console-ui |
| `deepsignal/console-mod-map` | 8f6a226 | SUPERSEDED-BY-UNIT | console-ui |
| `deepsignal/console-mod-stale-banner` | 8e1c58b | SUPERSEDED-BY-UNIT | console-ui |
| `deepsignal/console-mvp` | f38b52e | SUPERSEDED-BY-UNIT | console-ui |
| `deepsignal/console-visual-gate` | 4bfd755 | SUPERSEDED-BY-UNIT | console-ui |
| `deepsignal/sec-cds-lockdown` | eadb0a2 | SUPERSEDED-BY-UNIT | sec-cds-joint |
