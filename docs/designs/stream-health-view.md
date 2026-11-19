# Stream Health console view

Slot 3 approved on November 19. This new view design awaits approval before implementation.

## Fixed target

Add a read-only Stream Health view reachable from the console. Discover streams from the field store. For each stream show the eight stage labels in producer order and display the state published in each ds_chain:<stream>:<stage> field. Display the producer's ds_chain:<stream>:root field as the reported root stage. Preserve OFF and UNKNOWN as distinct states. Missing, stale or unusable inputs must never look like healthy current readings. With no chain fields, explain that no stream health data is available. Keep the existing logger Health page usable.

## Acceptance tests

The first command exercises the registered view with the actual field-store contract. The browser command exercises navigation and visible updates against a served production bundle and an isolated CDS fixture. Include two independent streams, root recovery, stale or missing evidence, and a valid variation with fields arriving in a different order.

```sh
(cd contrib/deepsignal/console && npm test -- src/modules/stream-health/stream-health.test.tsx)
(cd contrib/deepsignal/console && npm run lint && npm run type-check && npm run build)
python3 -m pytest -q contrib/deepsignal/test/console/test_stream_health_view_browser.py
```

## Prerequisites and out of scope

Use a fresh fork topic cut from current integration (verified 1dc7a5e on November 19). The producer contract is in StreamHealthWriter.transform on the separately tested engine branch, 0f2137c. Integration of the engine and enabling its publisher on a vessel are separate work. Cloud builds the presentation. Deriving root causes, computing health, transition alerts, security changes and starting the soak are outside this view. Mark browser results with the tested commit and input source.
