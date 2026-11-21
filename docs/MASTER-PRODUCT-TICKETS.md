# Master product implementation tickets

Created 2026-11-21 from Eugene's **Master Product and Implementation Directive**
(M sections 0–24) and **Mandatory Grafana and Visualization Integration**
(G sections 1–12 and final requirement). Both are implementation requirements.
This is the local work register, not a collection of published GitHub issues.
Grafana is mandatory product scope, while DeepSignal's own UI remains independent.

## Status, ownership and completion rules

- **IN PROGRESS** means implementation or discovery exists, not acceptance or release.
  **OPEN** means work remains; **DEFERRED** means explicitly outside first delivery.
  No ticket below is marked complete merely from a plan or passing isolated test.
- DeepSignal's lead is the sole integration owner and assigns one current worker
  per bounded unit after checking actual claims and prerequisites. Roles below
  identify responsibility, not a claim that a worker is running.
- Evidence for closure: exact candidate and dependency identities, commands and
  results, failure/repair history, reviewer disposition, applicable Linux gate,
  documented limitations, operator-facing demonstration and reproducible handoff.
  Preserve valid prior evidence; never turn HOLD or unrun checks into PASS.
- Distinguish fixture, real-upstream lab, SDK protocol, Codex interactive and
  live-vessel qualification. Production access, activation and upstream publication
  remain separately authorized. No ticket authorizes live scanning or writes.
- Reuse one catalog, evidence model, application services and existing Relay and
  Kalon resource authority. No competing scheduler, scientific metadata registry,
  AI-only computation, arbitrary command tool, or required cloud model.
- Dependencies are **stage-specific**: the M1 subset of a service can enable the
  fixture journey before its complete M2–M5 scope is finished. Do not wait for every
  later ticket before delivering the first runnable slice.
- Current verified baseline: Console and Stream Health **view fixture pilots** at
  `b67f3072daee63d0d307a16bc1d34e24b3c75002`; see
  [pilot evidence](../research/2026-11-20-relay-pilots/combined-astra-r9-pass.md).
  That does not qualify a Stream Health engine, this new M1 slice, Grafana or live control.
- New M1 work is in `/private/tmp/deepsignal/product-m1-20261121`. Evidence is still
  being collected; consult the lead's current handoff rather than infer completion.

## Milestone and requirement coverage

| Milestone | Deliverables and exit evidence | Tickets |
| --- | --- | --- |
| M0 | Verified inventory, compatibility, contracts, owners and bounded first profile | T-PROD-00, T-PROD-11, T-PROD-13 |
| M1 | Model-free fixture journey through Console/Health, data, draft/diff, validation, replay, handoff, Connections and actual SDK MCP | T-PROD-01; initial subsets of 03–11 |
| M2 | Real pinned OpenRVDAS profile and archive conformance in a disposable lab | T-PROD-02, T-PROD-03 |
| M3 | Usable configuration authoring, dependency-aware validation and isolated replay | T-PROD-07, T-PROD-08 |
| M4 | Real lab management adapter, independent approval, durable execution and recovery | T-PROD-11, T-PROD-12 |
| M5 | Complete promised workspaces, offline package, measured interference, usability and deployment review package | T-PROD-04–06, T-PROD-09–10, T-PROD-13–14; required Grafana gates |
| G1 | Real supported backend discovery and capability record | T-GRAF-01 |
| G2 | Verified-source dashboard drafts, queries, schema and diff | T-GRAF-02 |
| G3 | Same-service SDK MCP dashboard workflow | T-GRAF-03 |
| G4 | Independently approved lab publication, retrieval, panel queries and recovery | T-GRAF-04 |
| G5 | Ordinary DeepSignal dashboard management UI and safe navigation | T-GRAF-05 |
| G6 | Templates, portable remapping and operator change management | T-GRAF-06 |

| Requirement sections | Accountable tickets |
| --- | --- |
| M0–3: mandate, discovery, six workspaces, architecture | T-PROD-00, 01, 06, 10, 13, 14 |
| M4: domain and evidence contract | T-PROD-00, 03, 09, 11 |
| M5: upstream adapters, archives and compatibility | T-PROD-02, 03 |
| M6: Console and operator experience | T-PROD-06; existing T-CON tickets |
| M7: explainable health, events and alerts | T-PROD-05 |
| M8: Data Explorer, numerical/QC semantics | T-PROD-03, 04, 06 |
| M9: configuration workbench | T-PROD-07 |
| M10: isolated replay | T-PROD-08, 13 |
| M11: approval and controlled operations | T-PROD-11, 12 |
| M12: investigation, commissioning and handoff | T-PROD-09 |
| M13: MCP and ordinary-interface parity | T-PROD-10 |
| M14–15: AI behavior, data exposure, security and isolation | T-PROD-11; T-PROD-09, 10, 12 |
| M16: performance, reliability, storage and resource budgets | T-PROD-13 |
| M17–18: delivery order and reference demonstration | T-PROD-01, 02, 12, 14 |
| M19: concrete acceptance tests | Each ticket's acceptance; cross-cutting T-PROD-14 |
| M20–21: maintainability, documentation and engineering handoff | T-PROD-00, 14 |
| M22: open contribution and future research | T-PROD-14, 15 |
| M23–24: primary sources and executable delivery | T-PROD-00, 01, 02, 10, 14 |
| G1–3: shared service, versioned Grafana API and actual Influx dialect | T-GRAF-01, 02; T-PROD-03, 11 |
| G4–5: AI-assisted generation and scientific visualization | T-GRAF-02, 03 |
| G6–7: independent UI and MCP | T-GRAF-03, 05 |
| G8–9: templates, portability, ownership and conflicts | T-GRAF-04, 06 |
| G10: reliability, bounds and acquisition independence | T-GRAF-01, 02, 04; T-PROD-13 |
| G11–12 and final requirement: G1–G6 and reproducible lab demonstration | T-GRAF-01–06; T-PROD-14 |

## Core product tickets

### T-PROD-00 — Pin the first profile and shared contracts

**Status:** IN PROGRESS, M0. **Owner:** integration lead. **Depends on:** none.
**Reuse:** current Console/Stream Health, [REFERENCE](REFERENCE.md),
[units](units.json), [operating system](OPERATING-SYSTEM.md), existing design notes.

Deliver a concise capability inventory with code locations, dependencies and
implemented-and-verified / implemented-unverified / partial / absent / blocked
labels. Pin actual OpenRVDAS, client, SDK and dependency identities. Define typed,
versioned deployment/instrument/stream identities and compact result envelopes,
explicit result/error states, timestamps, provenance, limits and artifact scope.
Record consequential choices in short ADRs; preserve licenses and raw evidence.

**Acceptance:** reconcile source and current workloads with notes; demonstrate
fixture-vs-real profile and unsupported capabilities; preserve unknown metadata,
nonfinite classifications, original/source/derived flags and instrument replacement
identity; document schema migration policy. Reconcile historical T-CON statuses
against exact pilot evidence without deleting earlier findings. **Evidence:** M0
inventory/design exists in the active workspace; final manifest and review pending.

### T-PROD-01 — Complete the first cross-workspace fixture investigation

**Status:** IN PROGRESS, M1; not complete. **Owner:** integration lead.
**Depends on:** M1 subsets of T-PROD-00, 03–11; existing pilot Console/Stream Health.

Connect one clearly simulated, deterministic incident across all six workspaces:
stale plausible value, raw collection evidence, demonstrated parsing/configuration
failure, healthy streams and an intentionally inactive logger. Follow the selected
identity/interval through data and events, evidence-backed hypothesis, minimal draft,
source/behavior diff, static checks, identical-input baseline/candidate replay and
portable watch handoff. Connections shows real capability and limit information.

**Acceptance:** a model-free executable walkthrough and UI/CLI/SDK-client test use
the same services and snapshots; independent literal values/units/timestamps/counts
verify the corrected parser; include an evidence-insufficient or expected-inactivity
**no-change** outcome. Original raw input remains immutable. No mock-only control,
empty tools or screens count as implementation. **Evidence:** active workspace;
R5 and exact58fbde8c Linux workspace checks passed; Linux security policy failed. Full scenario and independent review remain pending.

### T-PROD-02 — Qualify one real OpenRVDAS lab adapter

**Status:** OPEN, M2. **Owner:** adapter maintainer, to be assigned.
**Depends on:** T-PROD-00; usable M1 services. **Reuse:** existing CDS and gateway,
fixture harness, stock Reader/Transform/Writer and actual manager APIs.

Implement configured discovery, metadata, bounded recent data, status, configuration
and supported events/snapshots against one pinned real upstream installation.
Detect capabilities and real backend semantics; do not treat lmcmd as universal.
Use an explicit endpoint identity and bounded shared subscriptions with local fanout.

**Acceptance:** reusable conformance suite runs against a disposable real installation,
not only mocks; prove timeout, backoff/reconnect and dropped/unknown coverage reporting;
missing journal/loaded state remains unknown; native acquisition/administration survive
DeepSignal termination. Record versions, side effects, authentication assumptions and
unsupported backend generations. **Evidence:** pending new-profile real lab receipts.

### T-PROD-03 — Deliver scoped catalog, immutable queries and archive coverage

**Status:** IN PROGRESS for fixture subset; OPEN for real archive, M1–M2.
**Owner:** data-service maintainer, to be assigned. **Depends on:** T-PROD-00;
T-PROD-02 for real profile. **Reuse:** catalog identity, existing CDS, TextFileReader.

Expose searchable streams/metadata and one real archive backend alongside fixtures.
Freeze bounded selections with stable IDs, source revisions and provenance. Implement
half-open UTC intervals, explicit original time basis and event/receipt/archive times,
once-resolved relative ranges, missing/nonfinite classification and separate QC flags.
Return requested/available intervals and known/partial/unknown completeness.

**Acceptance:** append, rotation and partial trailing-record tests preserve snapshot
boundaries; changed mutable input changes identity; future/invalid times, duplicate
and out-of-order records remain visible; unknown cadence never invents loss percent;
missing values never become zero. Artifact reads recheck scope/permissions; raw archives
stay authoritative; retention/expiry is visible. **Evidence:** fixture work only;
archive and lifecycle receipts pending.

### T-PROD-04 — Implement defensible analysis, QC and comparison

**Status:** IN PROGRESS for scalar fixture subset; OPEN for full scope, M1–M5.
**Owner:** analysis maintainer plus independent scientific reviewer, to be assigned.
**Depends on:** T-PROD-03. **Reuse:** established methods/IOOS QC where appropriate,
existing reviewed scientific units only when their exact evidence applies.

Deliver scalar counts/min/max/mean/median/quantiles/stddev, interval/gap diagnostics,
reviewed gross-range/spike/rate/flat-line profiles, and explicit unit/time-aligned
pairwise comparisons. Record method/version/parameters, filtering, counts, exclusions,
matched/unmatched data and limitations. Plot reduction is separate from analysis.

**Acceptance:** literal one-point/constant/missing/nonfinite and irregular-sampling
fixtures; declared observation/time weighting and population/sample deviation;
chunking preserves the chosen algorithm, never averages chunk medians; 1 Hz [0,6)
with 0,1,4,5 reports only 2,3 missing; circular/incompatible inputs are correctly
handled or rejected; flags stay separate and not-evaluated remains explicit. No
unsupported confidence, drift or physical-fault claim. **Evidence:** full scientific
validation and independent reference review pending; no raw corrections authorized.

### T-PROD-05 — Complete explainable health, event and alert lifecycle

**Status:** OPEN beyond existing qualified view, M1–M5.
**Owner:** health maintainer, to be assigned. **Depends on:** T-PROD-00, 02–03.
**Reuse:** existing Stream Health view; T-CON-12 delivery evidence.

Implement versioned mode-aware expectations, transparent cadence/parser/delivery
rules, dependency context and retained events. Separate process state, observation
freshness, observer connection, parsing, archival evidence and scientific quality.
Add deduplication, hysteresis, auditable acknowledgment and expiring suppression;
keep grouped child symptoms and label inferred relationships.

**Acceptance:** intentional inactivity is not a fault; backend outage does not label
all instruments broken; running with failed parsing is not globally healthy; unknown
archival stays unverified; acknowledgment never clears a condition; suppression
expires with history; historical health requires historical evidence/rule version.
Disk pressure bounds event retention without stopping acquisition. **Evidence:**
view pilot evidence reusable only for its scope; engine/lifecycle tests pending.

### T-PROD-06 — Finish coherent operator workflows and accessibility

**Status:** IN PROGRESS, M1–M5. **Owner:** Console maintainer, to be assigned.
**Depends on:** working service increments. **Reuse:** existing Console routes,
night palette, chart/map/number/status modules and [T-CON tickets](TICKETS.md).

Link Live Console, Stream Health, Data Explorer, Configuration Workbench,
Investigations and Connections with explicit deployment/cruise, live/recorded/replay
mode, time basis, interval, evidence age, permissions and draft context. Deliver
short plots/tables, saved layouts and meaningful groups; no dashboard-builder detour.

**Acceptance:** actual browser route tests preserve identity and frozen selection;
failed refresh cannot be hidden by a successful unrelated request; replay PASS cannot
be presented under a different interval. Verify day/night, keyboard/focus, narrow
screen and non-color cues; unknown/no-permission/no-data/unsupported states explain
why. Shared display routes expose no controls; essential tasks work with no model,
Grafana or shore connection. **Evidence:** existing pilot reusable; new-workspace
usability and browser receipts pending. T-CON-4–10 and other existing IDs remain
single-source follow-ups, not duplicated tickets here.

### T-PROD-07 — Complete configuration authoring, validation and proposal packets

**Status:** IN PROGRESS for narrow fixture draft; OPEN for M3 breadth.
**Owner:** configuration maintainer, to be assigned. **Depends on:** T-PROD-00,
02–03; T-PROD-08 for L5. **Reuse:** pinned upstream expansion/validation semantics.

Provide structured and source editors, guided logger creation from verified
components, immutable optimistic-concurrency revisions, source and behavioral diffs.
Keep disk, expanded, last-loaded and runtime states separate. Capture transitive
files/templates/variables/devices/calibrations, component and symlink identities,
known affected loggers/modes/destinations and unknown relationships.

**Acceptance:** report L1–L6 individually as passed/failed/not-run/unsupported;
bounded syntax/duplicate-key/type/depth checks; static checks never instantiate
components/import draft-selected modules/open devices; parity with pinned includes,
templates and modes; preserve unknown keys/comments/order or explicitly refuse
unsupported round-trip. Never write redacted secrets back. Dependency change
invalidates executable plan identity. Proposal records effects, interruptions/gaps,
assumptions, evidence, verification/recovery, expiry and stable plan hash; no approval
is implied. **Evidence:** full editing/parity/proposal review pending.

### T-PROD-08 — Qualify bounded isolated replay and job recovery

**Status:** IN PROGRESS for fixed fixture parser; OPEN for general supported replay,
M1–M3. **Owner:** replay maintainer, to be assigned. **Depends on:** T-PROD-03, 07,
11, 13. **Reuse:** existing parser and fixture components, Relay resource admission.

Compare baseline/candidate on the exact same immutable records and explicit clock
behavior. Use reviewed component contracts and substitute every supported I/O path,
including nested readers/writers, mirrors and diagnostics. Preserve event times apart
from scheduling time. Unsupported custom components must refuse qualification.

**Acceptance:** exact expected parsed fields/values/units/timestamps/counts/order/flags
and unchanged-field checks; no-change/bad draft remains failed. Demonstrate actual
network/device/credential/mount/process isolation, output/CPU/RAM/time bounds and
private workspaces. Long work returns durable IDs with cancellation, deadlines,
bounded queue and restart reconciliation; unsafe execution returns unavailable while
static validation remains useful. **Evidence:** fixed parser is not proof of general
sandboxing; isolation, asynchronous execution and recovery receipts pending.

### T-PROD-09 — Make investigations and watch handoffs durable and portable

**Status:** IN PROGRESS, M1–M5. **Owner:** evidence-service maintainer, to be assigned.
**Depends on:** T-PROD-03–08 increments and T-PROD-11 export policy.

Persist revisioned investigations with question, exact window, facts, calculations,
operator notes, attributed AI suggestions, hypotheses, decisions, proposals and next
actions. Link numeric claims to dataset/method/result fields; do not store private
model reasoning. Add versioned runbooks and commissioning expectation profiles.

**Acceptance:** concurrent edits conflict rather than overwrite; export a human report,
structured manifest, authorized config/diffs/results, optional bounded samples and
plots with omissions/unknowns and retention stated. Second person can resume without
chat or installed DeepSignal; export policy is rechecked and failed/full-disk exports
do not affect acquisition. Commissioning report distinguishes software replay from
instrument/site qualification. **Evidence:** fixture persistence/export under work;
portable resume, backup/restore and exposure checks pending.

### T-PROD-10 — Finish real MCP, CLI and API parity

**Status:** IN PROGRESS, M1–M5. **Owner:** interface maintainer, to be assigned.
**Depends on:** functional shared services and T-PROD-11.
**Reuse:** [existing MCP architecture](../research/2026-11-18-mcp-reference-architecture.md),
IDEAS #20/#64; this is the same engine, not a second MCP package/logic layer.

Pin the official SDK against actual runtime/client protocol compatibility; stdio first.
Expose only working typed tools across discovery/evidence, data/analysis/compare/plot,
configuration/drafts/validation/replay/proposals, investigation/artifacts/jobs and
operation status. Explicit qualified IDs carry scope; no hidden conversational state.

**Acceptance:** actual SDK client discovers schemas, calls the complete current
journey and verifies numerical/artifact parity with CLI/UI; protocol errors, result
bounds, cancellation and resource authorization tested through transport; stdout stays
protocol-only. Accurate annotations do not substitute for authorization. Supply verified
Codex registration instructions, tested prompt sequences and client compatibility;
label interactive verification pending if unrun. Execution tool appears only for a
qualified authorized principal/environment; never self-approval or arbitrary tools.
**Evidence:** actual13-tool SDK and CLI parity passed in Relay R5 and Linux44879804326 at58fbde8c. Complete catalog, interactive client and real backend conformance remain pending.

### T-PROD-11 — Enforce identity, data exposure and trusted boundaries

**Status:** IN PROGRESS for local fixture restrictions; OPEN for production boundary,
M0–M5. **Owner:** security maintainer plus independent reviewer, to be assigned.
**Depends on:** T-PROD-00. **Reuse:** existing security unit and T-SEC-1–6;
IDEAS #65 approval service. Do not weaken existing gateway or scanner gates.

Required boundary and acceptance evidence: [Security Architecture section17](SECURITY-ARCHITECTURE.md#17-mcp-access-and-ai-disclosure-required-production-boundary).
Read-only access is data disclosure; managed-provider egress and external-client
trust require separate enforcement and evidence. Current fixture is not qualified.
Eugene requires configurable selected MCP access: operator-managed versioned grants
by identity/client, deployment, sensor/stream/field, data class, time range and
operation. Test intersection, default denial of new fields, policy reload/revocation,
cached/queued/streaming access and prevention of client self-escalation. Provide an
ordinary authorized configuration interface and visible effective capabilities.

Use trusted transport/OS identity and distinct read/export/notes/draft/acknowledge/
propose/approve/execute/admin permissions. Enforce scoped handles and source roots,
resolved symlinks, configured endpoints, parsing/decompression/record/byte limits,
secret exclusion and data exposure profiles (synthetic/public, summaries, restricted,
local-only). Preserve untrusted text as data and escape UI output.

**Acceptance:** isolated local boundary tests refuse cross-deployment access,
unauthorized reads/exports, path escapes and unapproved endpoints; hostile fixture
text cannot change server policy. Review browser/terminal/SSH/file access as well as
MCP. Agent cannot alter privileged approvals/policy/executor/credentials; otherwise
mark approval boundary advisory and disable live execution. Audit principal/action/
revision/outcome without secret payloads; retention/full audit store fail safely.
Remote auth/transport/origin checks are required before remote use. No claim of
universal prompt-injection resistance or tamper-proof audit. **Evidence:** independent
security qualification and real isolation remain pending.

### T-PROD-12 — Implement independently approved operations in a disposable lab

**Status:** OPEN, M4. **Owner:** operations maintainer and separate approving operator,
to be assigned. **Depends on:** T-PROD-02, 07–08, 11, 13.
**Reuse:** IDEAS #65; approved narrow manager interface, not a generic command endpoint.

Support only proven allowlisted configuration/mode/start-stop-reload operations.
Bind approval to deployment/assets/base generation/dependencies/plan/actions/checks/
window/expiry/operator and bounded recovery. Durable operation intent precedes mutation;
serialize conflicts and atomically bind one approval to one operation independent of
client idempotency keys. Preserve all success, failure, partial and unknown states.

**Acceptance:** real lab success plus missing/expired/revoked/superseded approval,
stale native edit, duplicate/fresh-key reuse, cancellation/restart, post-submit timeout
and partial failure. Reconcile uncertain outcomes before retry; verify loaded state,
logger behavior, fresh expected data/errors/recording over a declared window. Record
backend transaction/race limits and irreversible gaps; only preauthorized recovery;
disabled executor/audit failure leaves acquisition operating. **Evidence:** real
management integration and protected approval boundary pending; mock-only is insufficient.

### T-PROD-13 — Measure resource budgets, reliability and acquisition interference

**Status:** OPEN for product qualification; existing Relay work is separate pilot
progress. **Owner:** runtime maintainer; Kalon lead retains shared allocator ownership.
**Depends on:** functioning service increments; approved resource mechanisms.
**Reuse:** [Relay handoff](CODEX-HANDOVER.md), existing claims/guards/lease protocol.

Set bounded rows/bytes/query cost/intervals/queues/concurrency/time/retention/disk
budgets; keep CPU-heavy work off request handling. Respect per-job memory headroom,
pressure/swap, protected jobs and machine reservations; no unverifiable new heavy
claim when coordinator is unavailable. Finish pending verified lease/fencing,
forced-retirement and owner-transfer gates before production Relay dispatch.

**Acceptance:** report measured p50/p95, peak process-tree memory, throughput and
sequence gaps on declared 2-core/4-GiB reference profile with 50 loggers/200 scalar
fields at 1 Hz plus specified higher rates. Evaluate <1 s warm request p95 and <2 s
visible update targets rather than assert them. Test bursts/reconnect/cancellation/
restart, full storage and bounded retries; compare acquisition with/without DeepSignal.
Preserve measured queued handoff evidence separately from end-to-end throughput.
**Evidence:** no new utilization improvement or Mini job claimed; product load and
shared production ownership qualification pending.

### T-PROD-14 — Qualify, package and hand off the whole operator product

**Status:** OPEN, M5. **Owner:** integration lead with independent science/security/
usability reviewers and operator pilot participant, to be assigned.
**Depends on:** required earlier milestone scope plus T-GRAF-01–06 acceptance.

Deliver Linux-first offline package/assets/dependency preparation and exact install,
run/test/demo, real-profile setup, CLI/MCP/Codex and operator commands. Document data/
science semantics, configuration/replay/approval/recovery, compatibility/conformance,
permissions/exposure/secrets, limits/performance, troubleshooting, backup/restore,
retention, disabling and contribution contracts. Preserve licenses and separate
institutional material; no upstream publication or licensing change without approval.

**Acceptance:** reproduce both ordinary and SDK-client incident/handoff journeys,
real upstream conformance and Grafana lab demo; verify offline startup and DeepSignal
termination leaves acquisition/native administration intact. Review all six promised
workspaces and explicit unsupported cases. Collect actual technician time-to-evidence,
context switches/errors, task completion and second-person resume observations before
percentage/fleet usability claims. Produce exact-source test/review matrix and separate
production deployment package; no live activation from ticket closure. **Evidence:**
M1, real-lab, client-interactive and production gates must remain individually labeled.

### T-PROD-15 — Preserve deferred research and scientific correction boundaries

**Status:** DEFERRED, outside first delivery. **Owner:** research/science lead,
unassigned. **Depends on:** completed core workflows and separately scoped research.
**Reuse:** existing correction ledger, instrument history and scientific backlog;
no automatic launch of held campaigns.

Track multi-vessel operation, richer commissioning, advanced inference/drift/predictive
faults/signals of opportunity, uncertainty propagation, specialized models and further
archives/exports as future extensions. Keep core contracts open and useful; no licensing
infrastructure or unsupported scientific/IP claims.

**Acceptance before any future activation:** raw data immutable; versioned reversible
correction layers name scope/method/parameters/uncertainty/evidence/author/reviewer/
approval; each pass starts from raw plus selected approved layers. Independently
validate against references not used for fitting; scientific correction approval stays
separate from configuration approval. **Evidence:** none claimed; does not block M1.

## Mandatory Grafana integration tickets

These extend existing [IDEAS #134 / Grafana quality pack](IDEAS.md) and
[its brief](../briefs/p2/134-grafana-quality.md), rather than create another catalog.
The older brief is useful history, but its offline-only output is not completion of
the new required discovery, UI/MCP, publication and real-lab scope.

### T-GRAF-01 — Discover and pin the Grafana/InfluxDB lab profile

**Status:** OPEN, G1. **Owner:** visualization adapter maintainer, to be assigned.
**Depends on:** T-PROD-00, 03, 11; an explicitly configured disposable lab backend.

Implement one shared Visualization Service and version/capability manifest. Inspect
actual Grafana API/dashboard schema, folders, dashboards, data sources, panel/plugin
capabilities and auth; detect/configure actual Influx generation and query language.
Use configured backend identities and least-privilege service accounts, not network
scans or admin credentials. Do not assume Flux or classic APIs are universal.

**Acceptance:** real authorized discovery receipts record Grafana/Influx versions,
source UIDs, folders and API revision; unsupported schema/plugin/rendering/auth cases
are explicit. Query timeouts/response/concurrency limits hold on backend loss.
No datasource/token/writer/bucket/retention mutation. **Evidence:** no installed
Grafana/Influx compatibility or discovery result claimed yet.

### T-GRAF-02 — Generate scientifically traceable dashboard drafts

**Status:** OPEN, G2. **Owner:** visualization service maintainer, to be assigned.
**Depends on:** T-GRAF-01, T-PROD-03–04, 11. **Reuse:** #134 and shared stream catalog.

Bind authorized OpenRVDAS logical stream roles to exact Influx measurement/field and
data-source UIDs. Create immutable manually/AI-authored drafts, validated bounded
query specifications, schema checks, previews, source/behavior diffs and provenance.
Support available time series/stat/table/gauge/bar gauge/state timeline/heatmap/geomap
and explicitly verified optional plugins such as the ODT compass.

**Acceptance:** no invented or similarly named substitute measurement/unit; explicit
coverage, ranges/aggregation/source labels; correct circular headings, compatible
units, latitude/longitude, salinity convention, missing intervals and QC overlays.
Query validation is separate from schema validation. Backend query results use bounded
allowlisted construction; expert query escape hatch, if added, has separate permissions
and cost limits. Preview works without claiming rendering service availability.
**Evidence:** hand-checked numeric/query fixtures and schema/lab receipts pending.

### T-GRAF-03 — Expose the same dashboard workflow through MCP and CLI

**Status:** OPEN, G3. **Owner:** interface maintainer, to be assigned.
**Depends on:** T-GRAF-01–02 and T-PROD-10–11.

Add working tools for visualization backend/data-source/dashboard discovery,
inspection, create/update/validate/preview drafts, propose publication and publication
status to the existing MCP server. Use shared services, bounded typed inputs, explicit
deployment/target/handles, proper mutation annotations and CLI equivalents.

**Acceptance:** actual SDK client requests the underway-science workflow, resolves
verified navigation/seawater/met fields, returns a complete validated draft and same
artifacts as CLI/UI; unsupported fields stay missing. No generic Grafana API,
datasource proxy, token admin, unrestricted query, or self-approval tool. Codex
interactive evidence is separate if available; model-free reproduction required.
**Evidence:** protocol workflow and interface-equivalence receipts pending.

### T-GRAF-04 — Publish approved dashboard revisions and reconcile conflicts

**Status:** OPEN, G4. **Owner:** visualization operations maintainer and independent
approving operator, to be assigned. **Depends on:** T-GRAF-02–03, T-PROD-11–13.

Distinguish DeepSignal-managed and operator-managed dashboards. Bind approved draft,
deployment, UID/folder/data-source mappings, base revision and exact material diff to
a narrow publication operation. Preserve operator edits/custom panels, detect conflicts,
record identity/validation/publication results and supported definition rollback.

**Acceptance:** independently approve a lab-folder publication; verify saved definition
by fetch, expected panel queries separately, and visual/operator acceptance separately.
Demonstrate stale revision rejection, unknown timeout reconciliation, duplicate-request
handling and approved rollback without overwriting unrelated dashboards. Rollback cannot
restore deleted observations or undo arbitrary side effects. No production publication
or infrastructure creation authorized. **Evidence:** approval, real API and recovery
receipts pending; advisory-only boundary cannot qualify production publication.

### T-GRAF-05 — Integrate ordinary dashboard management into DeepSignal

**Status:** OPEN, G5. **Owner:** Console maintainer, to be assigned.
**Depends on:** T-GRAF-01–04 increments and T-PROD-06, 11.

Provide backend capabilities/status, sources, dashboard inventory/templates,
manual/AI drafts, validation, preview/diff, authorized publication/export and open-in-
Grafana navigation. Embed only where verified auth/browser policy permits; otherwise
use explicit direct links. Maintain DeepSignal's own sensor/health/freshness/short-plot/
configuration/analysis/investigation workflows when Grafana or Influx is unavailable.

**Acceptance:** model-free browser workflow preserves deployment/time/ownership context;
day/night, keyboard/focus/narrow view and non-color cues work. Tokens remain server-side;
no weakened auth/origin/frame controls to enable embedding. Demonstrate a backend outage
with clear limitations and usable independent DeepSignal UI. **Evidence:** browser and
operator acceptance pending; API save alone does not qualify panel correctness.

### T-GRAF-06 — Deliver portable templates and the complete ecosystem demo

**Status:** OPEN, G6. **Owner:** visualization maintainer plus operator reviewer,
to be assigned. **Depends on:** T-GRAF-01–05 and T-PROD-09, 13–14.

Provide logical-role templates for underway science, navigation/motion, meteorology,
seawater/TSG, acoustic acquisition health, logger/stream health, science QC and
infrastructure monitoring where source data exists. Support compatible export/import,
explicit source remapping, revision-aware operator change management and versioned
provenance linked to investigations and evidence.

**Acceptance:** disposable OpenRVDAS + InfluxDB + Grafana demo performs actual field
discovery → validated appropriate panels/queries/units/coverage → usable preview →
independent approval → authorized lab publication → saved-definition and query
verification. Preserve existing dashboards; show no invented sensors, bounded database
load and measured acquisition interference. Replay the demonstration without a cloud
model; portable import reports incompatible schemas/plugins/mappings rather than guessing.
**Evidence:** complete lab demo, portability and operator acceptance pending.

## Verified discovery note, 2026-11-21 (T-GRAF-01)

No grafana or influx executable was found on the current PATH. Docker CLI is
present, but its read-only `docker ps` failed because /var/run/docker.sock is
absent; no daemon/container was started. This does not prove that no installation
exists elsewhere and is not network discovery.

The pinned upstream includes `logger/writers/influxdb_writer.py` using
`influxdb_client`, bucket and organization configuration. Its constructor can
create a missing bucket: do not instantiate it for visualization discovery or
replay. This source does not establish an installed InfluxDB version or query
language. Existing `contrib/niwa/grafana/cache-datasource/src/plugin.json` declares
Grafana >=10.3.3; its compose defaults to10.3.3. Those are historical source
metadata, not a tested target version or permission to launch that compose.
No compass panel was found at the inspected local path. Discover actual target
capabilities before claiming plugin support. G1 remains OPEN, real lab pending.

## Fake-cruise acceptance stories (Eugene, 2026-11-21)

Ten concrete stories are recorded in product
`contrib/deepsignal/workspace/DEMO-STORIES.md` at documentation commit1d601f39:
watch-start discovery, expected inactivity/staleness, parser investigation,
draft/validate/replay, justified no-change, second-person handoff, outage recovery,
Grafana draft, permission refusal and independently approved lab operation.
Each has a prompt, expected evidence/outcome, current status and existing ticket
mapping. T-PROD-01 owns fixture delivery, T-PROD-02 real pinned OpenRVDAS with fake
cruise/sensors and real archive, T-PROD-10 actual SDK plus interactive MCP stories,
and T-PROD-14 whole-demo operator acceptance. G1-G6 and M4 retain their own gates.
Current fixture is not a running upstream installation; no new ticket or PASS is
invented merely for writing stories. Test through Relay with preserved raw truth,
UI/CLI parity, safe acquisition independence and no live-vessel activation.
