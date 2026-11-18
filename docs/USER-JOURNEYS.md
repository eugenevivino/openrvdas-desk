# User journeys

Status: quality contract for D-UX1, D-SETUP1, and D-MCP2. The named MCP tools are
`fields`, `values`, `status`, `analyze`, `calibrate`, `export`, `detect`,
`propose`, `diff`, `validate`, and `apply`. `apply` is the only write path.

## Rules shared by every journey

* An action is one click, command, or chat turn. Reading is not an action.
* No journey requires YAML entry. A tech may need to know the cable's port,
  instrument label, serial number, or calibration certificate. They need no parser,
  schema, database, or logger expertise.
* Remote MCP uses streamable HTTP on the ship LAN or VPN interface, never a public
  interface. It uses per-user tokens and compact replies on satellite links. The
  default role is `viewer`. `tech` can propose; `admin` can request a write.
* Every write requires `--enable-control` and human approval in an on-screen form
  or `deepsignal approve <code>`. `apply` saves a rollback proposal and verifies the
  result. Proposals expire after 24 hours. Remote writes require on-ship approval
  unless an explicit ship policy grants the caller's role that authority.
* `detect` sends no bytes and skips ports held by running loggers.
* Calibration changes apply going forward, link to correction ledger #56, and never
  rewrite past raw data. Flags never delete raw data.

## Persona and stage matrix

| Persona | Set up | Improve | Troubleshoot | Operate |
| --- | --- | --- | --- | --- |
| Shipboard tech | J-TECH-SETUP-1, J-TECH-SETUP-AI-1, J-TECH-SETUP-MCP-1 | J-TECH-CAL-2 | J-FAIL-DEAD-1 | J-TECH-CRUISE-1 |
| Scientist | J-SCI-DATA-1 | J-SCI-PLOT-1 | J-SCI-QUALITY-1 | J-SCI-EVENT-1 |
| Bridge watch | Skipped: bridge watch does not configure sensors. | J-BRIDGE-MODE-1 | J-FAIL-STALE-1 | J-BRIDGE-WATCH-1 |
| Shore support | J-SHORE-ACCESS-1 | J-SHORE-FIX-1 | J-SHORE-HEALTH-1 | J-SHORE-DATA-1 |

## Shipboard tech journeys

### J-TECH-SETUP-1: add an instrument

**Trigger:** "I just plugged in a new GPS." The tech knows the physical port and
instrument label. Role: local `tech`; `admin` for apply.

| Best path | MCP path |
| --- | --- |
| 1. **Console, Instruments page:** click **Add instrument**. 2. **Wizard, Detect:** select the port found without transmitting bytes. 3. **Wizard, Identify and Review:** confirm model and fields, then approve **Start logging**. `GAP: #125-#128 setup wizard.` | 1. **MCP:** ask to add the GPS; `detect`, `propose`, `validate` return an approval form. 2. **Console, Approval page** or **CLI:** `deepsignal approve <code>`. 3. **MCP:** `apply` writes, starts, and verifies. `GAP: #130 setup engine.` |

Targets: live data in **10 minutes or less**, **3 actions or fewer**, YAML typed
**0**, expert knowledge **none**, required knowledge **physical port and label**,
and correct fields visible on **Live page within 10 seconds**. Proven by E-08 and
usability test U-SETUP-10.

### J-TECH-SETUP-AI-1: set up outbound AI assist

**Trigger:** "Walk me through connecting an AI assistant without exposing ship
data." This is the outbound direction: DeepSignal sends a reviewed, redacted
request to the provider. Role: local `admin`.

1. **Wizard, AI Assist, Provider:** choose the provider. `GAP: #188 AI assist wizard.`
2. **Wizard, AI Assist, Credentials:** paste the provider key. The wizard says it
   is stored encrypted in the credential store, never in configuration files or
   git, and shows how to replace or revoke it. `GAP: #188.`
3. **Wizard, AI Assist, Limits:** enter daily and monthly spending caps. `GAP: #188.`
4. **Wizard, AI Assist, Preview:** inspect the redacted preview of exactly what the
   test will send, with secrets and sensitive fields removed. `GAP: #188.`
5. **Wizard, AI Assist, Test:** run one test call and read its plain result,
   latency, and cost. `GAP: #188.`

Targets: **under 5 minutes**, **5 actions**, YAML typed **0**, expert knowledge
**none**, required knowledge **provider account and key**, encrypted key storage
**yes**, config or git key copies **0**, preview shown before transmission **yes**.
Proven by E-21.

### J-TECH-SETUP-MCP-1: set up inbound MCP access

**Trigger:** "Walk me through connecting Claude to this ship safely." This is the
inbound direction: an MCP client connects to DeepSignal over the ship LAN or VPN.
Role: local `admin` for setup; the new user is `viewer` by default.

1. **Wizard, MCP Access, User:** create a named per-user token. `GAP: #64 MCP gateway.`
2. **Wizard, MCP Access, Role:** keep `viewer`, or explicitly choose `tech` or
   `admin`; read-only `viewer` is selected by default. `GAP: #64.`
3. **Wizard, MCP Access, Client:** choose Claude Desktop or Claude Code and copy
   its generated client configuration snippet. The snippet contains the LAN or VPN
   URL and handles the token without writing it to git. `GAP: #64.`
4. **MCP, client connection test:** connect from that client and call `status`; the
   wizard reports a plain pass or fix. `GAP: #64.`
5. **Wizard, MCP Access, Network check:** confirm the bind address is reachable
   only on the ship LAN or VPN; a public bind fails the check. `GAP: #64.`

Targets: **under 5 minutes**, **5 actions**, YAML typed **0**, expert knowledge
**none**, required knowledge **user name, client, and LAN or VPN address**,
per-user token **yes**, default read-only **yes**, public reachability **no**. Proven
by E-22.

### J-TECH-REPLACE-1: replace an instrument with a spare

**Trigger:** "The sensor failed; I have the same model with a new serial number and
calibration." Role: local `tech`; `admin` for apply.

1. **Console, Instrument detail:** choose **Replace**. `GAP: #126 replacement flow.`
2. **Wizard, Identity and Calibration:** enter serial, certificate date, and
   coefficients, then review the generated diff.
3. **Console, Approval page:** approve; the setup engine validates, applies, and
   verifies. MCP alternative: `status`, `propose`, `diff`, `validate`, approval,
   `apply` through the same engine. `GAP: #130.`

Targets: **8 minutes**, **3 actions**, YAML **0**, expertise **none**, knowledge
**label, serial, and certificate values**, raw history retained **yes**, new live
values within **10 seconds**. Proven by E-09.

### J-TECH-RETIRE-1: remove or retire an instrument

**Trigger:** "This temporary sensor is coming off the ship." Role: local `tech`;
`admin` for apply.

1. **Console, Instrument detail:** click **Retire** and select a reason.
2. **Wizard, Review:** confirm the logger stops but raw data and identity remain.
3. **Console, Approval page:** approve. MCP uses `status`, `propose`, `diff`,
   `validate`, and approved `apply`. `GAP: #126 retirement flow; #130 engine.`

Targets: **3 minutes**, **3 actions**, YAML **0**, expertise **none**, knowledge
**instrument label**, raw data deleted **no**, port released within **10 seconds**.
Proven by usability test U-RETIRE-03.

### J-TECH-CAL-1: enter a calibration

**Trigger:** "I have new coefficients and a calibration date." Role: local `tech`;
`admin` for apply.

1. **Console, Instrument detail, Calibration tab:** enter certificate date and
   coefficients. `GAP: #127 calibration form.`
2. **Wizard, Review:** show units, effective time, and `diff`; `validate` the change.
3. **Console, Approval page:** approve `apply`, verify live output, and open the
   linked correction ledger #56 entry.

Targets: **5 minutes**, **3 actions**, YAML **0**, expertise **none**, knowledge
**certificate values and units**, past raw records changed **no**, ledger link
created **yes**. Proven by E-11.

### J-TECH-CAL-2: propose calibration from reference samples

**Trigger:** "Compare these bottle samples and suggest a salinity correction."
Role: `tech`; `admin` for apply.

1. **Console, Instrument detail, Calibration tab:** upload or select reference
   samples. MCP alternative: `calibrate` computes fit and uncertainty.
2. **Wizard, Review:** `propose` creates a forward-only change and #56 ledger link;
   `diff` and `validate` expose exclusions and units. `GAP: #127.`
3. **Console, Approval page:** approve `apply`, or reject with no change.

Targets: **10 minutes**, **3 actions**, YAML **0**, expertise **none**, knowledge
**sample source and units**, uncertainty shown **yes**, past raw data changed **no**.
Proven by E-10.

### J-TECH-CRUISE-1: start a cruise

**Trigger:** "We sail today; is acquisition ready?" Role: local `tech`.

1. **Console, Checklist page:** open Cruise Start. `GAP: #128 checklists.`
2. **Wizard, Checks:** run `status` for sensors, clock, disk, cache, backup, and
   destination; show plain-language blockers.
3. **Console, Checklist page:** acknowledge warnings and record the signed result.

Targets: **8 minutes**, **3 actions**, YAML **0**, expertise **none**, knowledge
**cruise identifier and expected instruments**, all required checks recorded
**yes**. Proven by E-07.

### J-TECH-CRUISE-2: end a cruise and hand off data

**Trigger:** "The cruise is over; package and hand off the data." Role: local
`tech`.

1. **Console, Checklist page:** run Cruise End checks. `GAP: #128.`
2. **Console, Data page:** create checksummed science and R2R packages using
   `export`; include configs, calibration and correction ledger #56, flags, and
   provenance. `GAP: NEW R2R handoff receipt.`
3. **Console, Data page:** verify each recipient's receipt before stopping loggers.

Targets: **15 minutes** excluding transfer, **3 actions**, YAML **0**, expertise
**none**, knowledge **cruise identifier and recipients**, checksum verified **yes**,
science and R2R receipts **2**. Proven by E-14.

### J-TECH-PORT-1: port call

**Trigger:** "We are alongside; stop, secure, and restart cleanly." Role: local
`tech`; `admin` for apply.

1. **Console, Checklist page:** select Port Call Stop; `status` records state and
   approved `apply` stops designated loggers.
2. **Wizard, Secure:** confirm power and port exceptions. `GAP: #128.`
3. **Console, Checklist page:** select Restart; approved `apply` starts and verifies
   values and clock.

Targets: stop **5 minutes**, restart **5 minutes**, **3 actions per phase**, YAML
**0**, expertise **none**, knowledge **which sensors must remain on**, missing data
explicitly marked **yes**. Proven by usability test U-PORT-05.

### J-TECH-DAILY-1: daily clock and GPS check

**Trigger:** "Do the clocks and positions agree today?" Role: local `tech`.

1. **Console, Health page:** open Clock and Position; `status` compares sources.
2. **MCP:** optional `analyze` explains offsets and recommends the next check.
3. **Console, Checklist page:** record pass or escalate an alert.

Targets: **2 minutes**, **2 actions**, YAML **0**, expertise **none**, knowledge
**none**, a **2 second** lag shown within **10 seconds**, result recorded **yes**.
Proven by E-05.

### J-TECH-BACKUP-1: backups and restore test

**Trigger:** "Prove we can restore, not just that backup jobs ran." Role: local
`tech`.

1. **Console, Admin page, Backups:** select the latest snapshot. `GAP: #128 backup check.`
2. **Wizard, Restore Test:** restore into an isolated location and verify hashes.
3. **Console, Checklist page:** record elapsed time and result; production remains
   untouched.

Targets: **15 minutes**, **3 actions**, YAML **0**, expertise **none**, knowledge
**backup destination**, hash match **yes**, production writes **0**. Proven by
usability test U-BACKUP-15.

### J-TECH-UPGRADE-1: upgrade with rollback

**Trigger:** "Upgrade OpenRVDAS and DeepSignal without risking the watch." Role:
local `admin`.

1. **Console, Admin page, Updates:** review versions and compatibility.
2. **Wizard, Preflight:** save config and rollback proposal, then validate.
   `GAP: #129 safe upgrade flow.`
3. **Console, Approval page:** approve, verify live data, or choose rollback.

Targets: planned outage **10 minutes**, **3 actions**, YAML **0**, expertise **none**,
knowledge **approved version**, rollback available **yes**, verification within
**60 seconds**. Proven by usability test U-UPGRADE-10.

### J-TECH-MODE-1: change logging mode underway

**Trigger:** "We need high-rate logging for this transect." Role: local `tech`;
`admin` for apply.

1. **Console, Instrument detail:** select a named logging mode.
2. **Wizard, Review:** show storage impact and `diff`; `validate` it.
3. **Console, Approval page:** approve `apply`; verify rate on Live page.

Targets: **3 minutes**, **3 actions**, YAML **0**, expertise **none**, knowledge
**desired rate and duration**, discontinuity annotated **yes**. `GAP: #125 named
modes.` Proven by E-12.

## Science and bridge journeys

### J-SCI-QUALITY-1: ask what data quality is now

**Trigger:** "Can I trust temperature and salinity right now?" Role: `viewer`.
1. **Console, Live page, Quality panel:** read freshness, flags, and uncertainty.
2. **MCP:** `status`, `values`, and `analyze` give a plain-language answer with
   timestamps and evidence. `GAP: #114 quality summary.`

Targets: **1 minute**, **1 action**, YAML **0**, expertise **none**, knowledge
**field names**, stale status within **10 seconds**, evidence links **yes**. Proven
by E-01 and E-04.

### J-SCI-EVENT-1: log an event or station

**Trigger:** "Mark station 42 and the bottle cast." Role: `tech`.
1. **Console, Events page:** click **New event**, select type, and confirm the
   current ship time and position. `GAP: #114 event entry.`
2. **CLI:** optional `deepsignal event add --type station --name 42`; the Live and
   History pages show the marker.

Targets: **1 minute**, **2 actions**, YAML **0**, expertise **none**, knowledge
**event name and type**, timestamp error **1 second or less**. Proven by E-13.

### J-SCI-DATA-1: get data on and off the ship

**Trigger:** "Give me yesterday's CTD and met data." Role: `viewer`.
1. **Console, Data page:** choose fields and time range; `export` previews size.
2. **Console, Data page:** download CSV or NetCDF, use ERDDAP #104, or create an
   end-of-cruise package. `GAP: #104 ERDDAP; #114 guided export.`

Targets: first download **3 minutes**, **2 actions**, YAML **0**, expertise **none**,
knowledge **fields and dates**, checksum supplied **yes**. Proven by E-02 and E-14.

### J-SCI-PLOT-1: custom plot and derived field

**Trigger:** "Plot density from temperature and salinity." Role: `viewer` to plot,
`tech` to save a derived field.
1. **Console, History page:** select fields, range, and plot type.
2. **Wizard, Derived Field:** choose a documented formula and units, preview, then
   save after validation. MCP uses `fields`, `values`, and `analyze`. `GAP: #114
   plot builder; #125 derived-field wizard.`

Targets: plot **2 minutes**, saved field **5 minutes**, **3 actions**, YAML **0**,
expertise **none**, knowledge **desired variables and units**, provenance shown
**yes**. Proven by E-03.

### J-SCI-FLAG-1: mark contaminated data

**Trigger:** "The intake was contaminated from 14:10 to 14:25." Role: `tech`.
1. **Console, History page:** brush the interval and click **Add flag**.
2. **Wizard, Flag:** choose reason, preview affected fields, and confirm.

Targets: **2 minutes**, **2 actions**, YAML **0**, expertise **none**, knowledge
**interval, fields, and reason**, raw deletions **0**, flag reversible **yes**.
`GAP: #114 interval flags.` Proven by E-15.

### J-SCI-ASK-1: ask plain-language questions

**Trigger:** "When did salinity start drifting, and what else changed?" Role:
`viewer`.
1. **MCP:** `fields`, `values`, `status`, and `analyze` select bounded evidence.
2. **Console, History page:** follow links to the exact interval and fields.

Targets: **2 minutes**, **2 chat turns**, YAML **0**, expertise **none**, knowledge
**question only**, timestamps and evidence **yes**, writes **0**. Proven by E-06.

### J-BRIDGE-WATCH-1: monitor the watch

**Trigger:** "Show position, heading, wind, depth, and whether they are fresh."
Role: `viewer`.
1. **Console, Watch page:** use day, dusk, or night mode; freshness is visible
   without opening details. 2. **Console, Alerts page:** acknowledge an audible
   operational alert. `GAP: #114 watch page polish.`

Targets: answer **10 seconds**, **1 action**, YAML **0**, expertise **none**,
knowledge **none**, stale fields labeled within **10 seconds**. Proven by usability
test U-WATCH-10S.

### J-BRIDGE-MODE-1: improve night readability

**Trigger:** "This display is too bright for the bridge." Role: `viewer`.
1. **Console, Watch page:** select Night mode and density; the choice persists per
   user.

Targets: **10 seconds**, **1 action**, YAML **0**, expertise **none**, knowledge
**none**, accidental configuration writes **0**. Proven by usability test
U-NIGHT-10S.

## Shore and remote journeys

### J-SHORE-ACCESS-1: establish safe remote access

**Trigger:** "Let me support this ship over its VPN." Role: `viewer` by default.
1. **CLI:** an on-ship admin issues a per-user, expiring token bound to LAN/VPN.
2. **MCP:** connect over streamable HTTP and call `status`; compact mode is on for
   satellite. `GAP: #130 remote setup engine endpoint.`

Targets: **5 minutes**, **2 actions**, YAML **0**, expertise **none**, knowledge
**VPN address and token**, public bind **no**, shared token **no**. Proven by E-18.

### J-SHORE-HEALTH-1: check ship health

**Trigger:** "Is the ship collecting good data?" Role: remote `viewer`.
1. **MCP:** `status` returns compact freshness, logger, clock, disk, and cache state.
2. **Console, Health page:** open evidence for any alert.

Targets: **1 minute**, **1 chat turn**, YAML **0**, expertise **none**, knowledge
**ship name**, response **8 KiB or less** at **64 kbit/s**, writes **0**. Proven by
E-18.

### J-SHORE-FIX-1: diagnose a dead sensor and propose a fix

**Trigger:** "The GPS is dead; tell the ship what to do." Role: remote `tech` to
propose; on-ship `admin` to approve.
1. **MCP:** `status` and `analyze` identify last value, logger state, and likely fix.
2. **MCP:** `propose`, `diff`, and `validate` produce an approval code, but do not
   apply. 3. **Console, Approval page** on ship: a person approves; `apply` verifies.

Targets: diagnosis **2 minutes**, proposal **3 actions**, YAML **0**, expertise
**none**, knowledge **sensor label**, remote state stops at **waiting for on-ship
approval**, unapproved writes **0**. Proven by E-19.

### J-SHORE-DATA-1: pull one day of data

**Trigger:** "Download yesterday's data from shore." Role: remote `viewer`.
1. **MCP:** `fields` identifies names; `export` creates a bounded, checksummed file.
2. **Console, Data page:** resume the download if the link drops.

Targets: request **2 actions**, YAML **0**, expertise **none**, knowledge **fields
and day**, metadata reply **8 KiB or less**, byte transfer resumable **yes**. Proven
by E-20.

### J-SHORE-DROP-1: link drops mid-session

**Trigger:** "The satellite link dropped while I was checking the ship." Role:
remote `viewer`, or `tech` for an existing proposal.
1. **MCP:** show disconnected and last ship timestamp; never imply fresh data.
2. **MCP:** reconnect with the same per-user token and resume the idempotent read.
   A pending write remains unapplied and requires a new approval if expired.

Targets: stale indication **10 seconds**, reconnect **2 actions**, YAML **0**,
expertise **none**, knowledge **none**, duplicate writes **0**. Proven by E-20.

## Failure journeys

Each alert appears on **Alerts** and **Health** pages and in MCP `status`. The
surface uses plain words, links to evidence, and offers only validated fixes.

| Journey | Notice and guided fix | Fix steps | Targets | Proof |
| --- | --- | --- | --- | --- |
| J-FAIL-DEAD-1 sensor dead | No fresh record for 10 s; show "GPS stopped" and last timestamp. | Check cable and power; run read-only `detect`; restart via proposed, approved `apply`; verify. | Notice **15 s**; fix **5 min**, **3 actions**; YAML **0**; expertise **none**; know label and port. | E-04 |
| J-FAIL-PARSER-1 wrong parser | Parse error rate exceeds 5% over 60 s; show samples and "format does not match." | `analyze`; select suggested parser; `diff`; `validate`; approve `apply`; verify fields. | Notice **60 s**; fix **8 min**, **3 actions**; YAML **0**; expertise **none**; know instrument model. | E-03 |
| J-FAIL-CLOCK-1 clock drift | Sources differ by 2 s for 30 s; show which clock lags. | Check GPS lock; select clock source; propose and approve correction; verify. | Notice **40 s**; fix **5 min**, **3 actions**; YAML **0**; expertise **none**; know approved time source. | E-05 |
| J-FAIL-DISK-1 disk filling | Forecast less than 24 h free; show largest consumers and time remaining. | Confirm backup; choose safe retention proposal; approve; verify more than 72 h free. | Notice **60 s**; fix **10 min**, **3 actions**; YAML **0**; expertise **none**; know retention policy. | E-07 |
| J-FAIL-CRASH-1 logger crash loop | Three restarts in 5 min; show stderr summary with untrusted text labeled. | Keep stopped; inspect sanitized error; select last-good config; approve rollback; verify 5 min stable. | Notice **5 min**; fix **10 min**, **3 actions**; YAML **0**; expertise **none**; know logger label. | E-16 |
| J-FAIL-CACHE-1 cache down | Cache health fails twice in 20 s while raw logging state is shown separately. | Continue raw logging; restart cache through approved proposal; verify display catches up. | Notice **30 s**; fix **5 min**, **3 actions**; YAML **0**; expertise **none**; know none. | E-04 |
| J-FAIL-STALE-1 stale display, data fine | Watch page age exceeds 10 s but logger file grows; say "display stale, recording continues." | Refresh subscription; restart display/cache only; verify timestamps, never restart logger. | Notice **15 s**; fix **2 min**, **2 actions**; YAML **0**; expertise **none**; know none. | E-04 |
| J-FAIL-CAL-1 bad calibration applied | Range or reference check fails within 60 s; show applied proposal and rollback. | Open `diff`; approve saved rollback proposal; `apply`; verify; annotate #56 ledger. | Notice **60 s**; rollback **3 min**, **3 actions**; YAML **0**; expertise **none**; know expected range. | E-11 |
| J-FAIL-INIT-1 instrument init fails | Wizard shows failed command, redacted output, and no live values within 10 s. | Keep logger stopped; check cable/mode; retry safe step or choose previous proposal; approve and verify. | Notice **10 s**; fix **10 min**, **3 actions**; YAML **0**; expertise **none**; know model and port. | E-09 |
| J-FAIL-SAT-1 satellite link down | Shore header changes to "offline" within 10 s and shows last ship timestamp. | Do not change ship state; reconnect VPN; resume reads; obtain new approval for expired proposals. | Notice **10 s**; recover **2 actions** after link returns; YAML **0**; expertise **none**; stale labeled **yes**. | E-20 |

## Coverage

| Journey IDs | Surfaces | GAP items | Test |
| --- | --- | --- | --- |
| J-TECH-SETUP-1 | Console, Wizard, CLI, MCP | #125-#128, #130 | E-08, U-SETUP-10 |
| J-TECH-SETUP-AI-1 | Wizard | #188 | E-21 |
| J-TECH-SETUP-MCP-1 | Wizard, MCP | #64 | E-22 |
| J-TECH-REPLACE-1 | Console, Wizard, MCP | #126, #130 | E-09 |
| J-TECH-RETIRE-1 | Console, Wizard, MCP | #126, #130 | U-RETIRE-03 |
| J-TECH-CAL-1, J-TECH-CAL-2 | Console, Wizard, MCP | #127, #56 | E-10, E-11 |
| J-TECH-CRUISE-1, J-TECH-CRUISE-2 | Console, Wizard, MCP | #128, NEW R2R receipt | E-07, E-14 |
| J-TECH-PORT-1, J-TECH-DAILY-1 | Console, Wizard, MCP | #128 | U-PORT-05, E-05 |
| J-TECH-BACKUP-1, J-TECH-UPGRADE-1 | Console, Wizard | #128, #129 | U-BACKUP-15, U-UPGRADE-10 |
| J-TECH-MODE-1 | Console, Wizard, MCP | #125 | E-12 |
| J-SCI-QUALITY-1, J-SCI-ASK-1 | Console, MCP | #114 | E-01, E-04, E-06 |
| J-SCI-EVENT-1 | Console, CLI | #114 | E-13 |
| J-SCI-DATA-1 | Console, MCP | #104, #114 | E-02, E-14 |
| J-SCI-PLOT-1, J-SCI-FLAG-1 | Console, Wizard, MCP | #114, #125 | E-03, E-15 |
| J-BRIDGE-WATCH-1, J-BRIDGE-MODE-1 | Console | #114 | U-WATCH-10S, U-NIGHT-10S |
| J-SHORE-ACCESS-1, J-SHORE-HEALTH-1 | CLI, Console, MCP | #130 | E-18 |
| J-SHORE-FIX-1 | Console, MCP | #130 | E-19 |
| J-SHORE-DATA-1, J-SHORE-DROP-1 | Console, MCP | #114 | E-20 |
| J-FAIL-DEAD-1, J-FAIL-CACHE-1, J-FAIL-STALE-1 | Console, MCP | #114, #130 | E-04 |
| J-FAIL-PARSER-1 | Console, Wizard, MCP | #125, #130 | E-03 |
| J-FAIL-CLOCK-1 | Console, Wizard, MCP | #114, #130 | E-05 |
| J-FAIL-DISK-1 | Console, Wizard, MCP | #128, #130 | E-07 |
| J-FAIL-CRASH-1 | Console, Wizard, MCP | #114, #130 | E-16 |
| J-FAIL-CAL-1 | Console, Wizard, MCP | #56, #127, #130 | E-11 |
| J-FAIL-INIT-1 | Console, Wizard, MCP | #125-#127, #130 | E-09 |
| J-FAIL-SAT-1 | Console, MCP | #114, #130 | E-20 |
