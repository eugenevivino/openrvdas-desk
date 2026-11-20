# Independent Review

Target: `75a71c1f3c610119ee63c34280431fd7c15823ae`

## Observed

- The source preserves producer order, keeps OFF distinct from UNKNOWN, discovers independent streams, and renders root and stage freshness independently.
- Stale reports are displayed as UNKNOWN while retaining the latest producer observation as `Last reported`; failed-quality reports also distinguish `Last usable`.
- Missing and malformed current values render UNKNOWN. Recovery and null root reports update without rewriting the producer value.
- Review was static only, as required. I did not run tests, install tools, or make network calls. The supplied receipts report green macOS checks, while the regenerated bundle's separate Linux qualification remains pending.

## Finding

- **P1: `contrib/deepsignal/console/src/modules/stream-health/page.tsx:35` loses an existing producer observation once it ages from STALE to NO_DATA.** Valid input: a real `ds_chain:science:sensor` sample with value `FAILED`, accepted quality, and age greater than the store's NO_DATA threshold, such as the browser fixture's source-restart case. Expected: UNKNOWN current state plus accurate historical evidence such as `No data · Last reported: FAILED`, keeping an expired observation distinct from a field that never reported. Actual: `UNKNOWN / Missing`, because the unconditional NO_DATA return ignores both `report.value` and `report.lastGood`. The browser test codifies the same loss for an old root at `contrib/deepsignal/test/console/test_stream_health_view_browser.py:161-162`. This is misleading operator data and conflicts with the requirement that observations not be rewritten.

## Inferred

- A source outage lasting beyond the stale window will make previously reported FAILED, OFF, or root-cause observations indistinguishable from fields that never produced data, even though the store retains the latest value.

## Verdict

Verdict: HOLD at `75a71c1f3c610119ee63c34280431fd7c15823ae`.
