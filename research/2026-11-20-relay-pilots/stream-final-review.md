# Independent Review

Target: `8e00f48f8c793ecd25468fcf59248c0d4ccb06cf`

## Observed

- HEAD and the worktree resolve to the exact candidate. Review was static only, as required. I did not run builds, tests, installs, or network operations.
- `presentReport` now separates an absent field from an expired observation: a NO_DATA report with stored source or usable history renders UNKNOWN plus `No data`, while a field with neither remains `Missing`.
- Expired FAILED, OFF, root-stage, and explicit null-root values remain historical `Last reported` evidence and are never rendered as current. Failed-quality history also remains rejected and separately identifies any `Last usable` value.
- The focused real-route cases cover initial expired history, missing evidence, stale evidence, QC rejection, independent streams, and recovery to current values after completing the CDS catalog-refresh handshake.
- The browser expectations retain expired root and time observations while keeping never-observed endpoint data distinct as missing.
- The supplied Linux receipts are reported green. Native same-head full self-check remains resource-pending and is not claimed here.

## Inferred

- During a prolonged source outage, operators retain the latest producer observation without mistaking it for current health, and a later valid publication restores current state.

## Prior HOLD Resolution

- The P1 at `75a71c1f3c610119ee63c34280431fd7c15823ae` is resolved: the unconditional NO_DATA-to-Missing path was replaced with an absence-only check, and regression coverage exercises expiry and recovery through the real store route.
- No new reachable operator-harm finding or other ticket was identified in the focused change.

## Verdict

Verdict: PASS at `8e00f48f8c793ecd25468fcf59248c0d4ccb06cf`.
