# OpenRVDAS MCP for research vessels: reference architecture

Source: Eugene's Deep Research report, 2026-11-18. NOTE: truncated in transit (stops inside
the schema design section, before the example JSON). Only visible content is recorded.
Claims are the report's (inferred until checked). Re-send the full text to complete this note.

## Answer
Not an MCP server with broad OpenRVDAS access. A typed, provenance-preserving analytical
gateway in front of OpenRVDAS, with a separate control path for anything that changes state.
v1: every action is read-only or proposal-only. The model may inspect streams, fetch
metadata, compute stats, plot, validate logger configs, and propose config or dashboard
patches. It never starts or stops loggers, replaces configs, changes instrument settings,
or deploys dashboards. Those cross a separate approval boundary: deterministic validators,
a diff, authorization policy, a human decision, then a distinct apply service.
MCP readOnlyHint and destructiveHint are advisory, so enforcement lives in code and infrastructure.

## Numbers come from code, not the model
The LLM chooses the calculation; deterministic software computes it on a bounded, identified
slice. Every result carries query fingerprint, source ids, time bounds, sample counts, units,
quality flags and the exact computation. Benchmarks cited: TSAQA best zero-shot 65.08%,
ARFBench best frontier model 62.7%, so unaided LLM arithmetic is not authoritative.

## Architecture (from the report's diagram)
LLM host (cloud or local) -> trust boundary A -> MCP gateway and policy enforcement
(schema validation, authn/authz, per-tool scopes, query budgets, approval state, audit
correlation) -> read/analysis plane (OpenRVDAS adapters, archive/query, metadata catalog,
retrieval, deterministic stats, plot renderer) and proposal plane (patch generators,
validators, diff) -> human approval record -> trust boundary B -> apply service with its own
identity and postcondition tests -> OpenRVDAS control API, Grafana API. Append-only audit log
of all calls, data ids, diffs, approvals, hashes. Offline: local model, local MCP, local
metadata and archive, deferred sync queue to shore.

## Protocol and tool design
- Target MCP spec 2026-07-28 directly: stateless core, self-describing requests,
  Mcp-Method and Mcp-Name headers for gateway policy, cacheable lists, explicit handles
  instead of hidden sessions, 12-month deprecation window. Do not copy older SSE/session examples.
- Tools are domain operations with deterministic contracts: query_timeseries,
  summarize_timeseries, get_instrument_metadata, validate_logger_config, render_plot.
  No execute_python, execute_sql or run_shell. No hundreds of tiny tools. Two tools must not
  differ only by a filter option; put filtering, aggregation, field selection, resolution in typed params.
- JSON Schema 2020-12 as a real contract; validate inputs before tool code runs and outputs after.
- OWASP MCP risks: command execution, over-scoped credentials, tool poisoning, context injection, confused deputy.

## Models
Keep cloud and local inference behind one agent interface; do not hard-code a vendor.
Local baselines to qualify on our own MCP schemas per quantized build: Qwen3.5-9B
(constrained hardware), Qwen3.8-27B (single workstation). Vendor benchmarks do not substitute.

## Fit with current plan
Matches D-PA1/#62 (AI audit trail, read-only AI). Adds: proposal and apply split, query
budgets, provenance fingerprints, golden-cruise eval suite.
