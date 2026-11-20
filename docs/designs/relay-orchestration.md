# DeepSignal Relay orchestration

Requested directly by Eugene on November 20, 2026 in the attached implementation brief.

Fixed target: adapt supplied Relay 0.1.0 with Python scheduling into isolated DeepSignal
candidate verification. Pin source, adapters, environment, acceptance policy and evidence.
Pilot console-ui and stream-health-view; preserve valid evidence and all product gates.
Keep existing dispatch ownership until complete pilot qualification and independent review.
The subsequent user request authorizes actionable Console review fixes and finishing
both pilots. Existing scientific, security, independent-review and critical merge
requirements remain in force.

Acceptance (from tools/relay):

```
python3 -m unittest discover -s tests -v
python3 -m unittest discover -s ds_tests -v
python3 -m dsrelay pilot --root /private/tmp/deepsignal/relay-20261120/pilot
python3 -m dsrelay report --state /private/tmp/deepsignal/relay-20261120/pilot/state
```

Prove immutable artifacts, evidence reuse, actual candidate test execution, source/policy
invalidation, honest holds, independent advancement, restart without duplicate work,
bounded output and compatible test-only batching. Measure actual handoff latency.
A held pilot is fail-closed evidence, not a passed ownership-transfer pilot.

Out of scope: numerical changes, original observations, live ship operations, MCP writes,
installs, critical merges and replacement of existing supervisors. On November 20 the
user explicitly approved Stream Health source 61ba756 on the fork branch
deepsignal/relay-stream-health-20261120 and desk workflow 993fa40 on
ci/relay-stream-health-20261120, including the existing Linux checks. Those two
branches were pushed; this does not qualify either module for release.
Prerequisites: desk ac42575; console da4aa5e (independent HOLD); Stream Health 9f156fa
(fresh checks and independent review missing). Archive provenance: UPSTREAM.json.
Independent reviewer judges controller safety; existing product owners retain gate authority.

The Kalon lead owns the sole cross-project capacity authority. DeepSignal supplies a
small protocol client and keeps its own queues, policies and evidence. Shared
execution remains staged until trusted host observations, fencing, restart/network
loss and verified cleanup are qualified. Existing local resource guards remain final.
