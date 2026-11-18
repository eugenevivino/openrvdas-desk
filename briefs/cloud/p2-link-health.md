You are building ONE module for the DeepSignal overlay on OpenRVDAS, on Eugene's own fork. Work only in this repository (eugenevivino/openrvdas). Do NOT touch, open pull requests against, or push to OceanDataTools or any upstream repository. Nothing here is sent upstream.

Branches: create branch `deepsignal/p2-link-health` from commit `3b4b76e` (the contrib master tree; it is in this fork's history, for example `git merge-base origin/deepsignal/vector-wind origin/deepsignal/instrument-history`) (if `deepsignal/p2-link-health` already exists on origin, check it out instead). Commit your work on that branch only, with one clear commit message, and leave it pushed to origin `deepsignal/p2-link-health`. Do not touch any other branch, `dev` or `master`. If you cannot push, leave the commit on the branch in your task and say so.

Environment notes: Python only; Node is not needed. Use `python3.12` if it exists, otherwise `python3` (3.11 or newer). If pytest is missing use `python3 -m unittest`. If flake8 is missing, `pip install flake8` into a throwaway venv and say you did. PyYAML is already an OpenRVDAS dependency; add no other dependency. No network.

Write the failing test first and paste its RED output, then make it GREEN. Run every acceptance command at the end and paste the tails. Report under 40 lines: files changed, test names, RED then GREEN tail, acceptance results, any design point you disagree with (do not change a design silently), what you verified versus inferred, and what must run outside the sandbox.

Stop rule: two fix rounds still red means stop and report.

The full brief follows.

----------------------------------------------------------------
# Brief: p2-link-health (Per-instrument link health, with NOC tool integration)

- Decision: IDEAS #156, D-SHIP1 and D-NOC1, from Eugene's 2026-11-18 ask for "intermapper-like network
  monitoring" (approved scope: link health in DeepSignal, integrate an existing NOC tool, no clone); build per D-NIGHT1
- Risk tier: medium (optional active probes on ship networks; an inbound webhook)
- Module: exactly one. Branch `deepsignal/p2-link-health` from `3b4b76e`
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: openrvdas_contrib tree, fork only for now
- Value (techs/science/shore): 5/2/4
- Depends on: none to build. Display is the console `health` module (a small follow-up the build lead
  routes there); host metrics stay in #119; the connection register is #151

## Goal
For every instrument link, a tech sees one verdict (OK, DEGRADED, FAILED, OFF) with the evidence: is the
device reachable, is data arriving at the expected rate, how many serial or parse errors, and since when.
The ship's existing network monitor (Uptime Kuma, Zabbix or LibreNMS) can poll that verdict, and its own
alerts show up next to it in DeepSignal.

## Background facts (do not re-derive)
- Base is the contrib `master` tree at `3b4b76e`: it carries a 2024 core tree (old Transform base class,
  no BaseModule). Copy the import-compatibility approach of
  `git show origin/deepsignal/vector-wind:contrib/deepsignal/logger/transforms/vector_wind_average_transform.py`
  so the module also works on current core. If that branch is unreadable, write plain absolute imports
  and say so.
- Create empty `__init__.py` files only where missing, byte-identical to the wind branch (empty), so
  parallel branches merge cleanly.
- OpenRVDAS loads classes from a config with `class:` plus `module:` (for example
  `module: contrib.deepsignal.<module>.<file>`). Records may arrive as a DASRecord, a dict with
  `timestamp` and `fields`, a list of either, or None; handle all, pass None through.
- File ownership is disjoint across phase 2 tasks: you own ONLY the paths under Scope.
- Design and safety context: desk `docs/SHIP-SYSTEMS.md` section 10 and decision D-SHIP1. Probes are opt-in per
  link and never touch a data port (see Design).


## What OpenRVDAS already has (reuse; do not rebuild)
Verified in OpenRVDAS v2.7.2 source:
- `server/logger_manager.py` publishes `status:logger_status` (`{logger: {config, status}}`, status
  RUNNING, STARTING, FAILED or EXITED) every manager loop, plus `status:cruise_mode`, and every logger
  stderr line as `stderr:logger:<logger>`; `server/logger_runner.py` tracks failed and restarted processes.
- `server/cached_data_server.py` keeps the latest timestamp and value of every field and serves
  `GET /fields` and `GET /latest/<f1>,<f2>` over HTTP on the cache port (8766 by default). Field age is
  `now - timestamp`: that is freshness, already.
- `logger/writers/timeout_writer.py` (`TimeoutWriter`) and `logger/readers/timeout_reader.py`
  (`TimeoutReader`) emit a message when a stream goes silent; `CountTransform` counts records.
- Desk console modules already planned or built: `health` (logger states, stderr, hints), `stale-banner`
  and `source-loss` (freshness on screen); #119 host health (disk, CPU, NTP).
The gaps this module fills: (1) reachability of the device itself, (2) record rate versus an expected rate,
(3) error counts per link classified from stderr, (4) one verdict per link joining all of it, (5) an endpoint
a NOC tool polls, (6) ingest of that NOC tool's alerts.

## Design (lead decisions; flag disagreement in the report)
Package `contrib/deepsignal/link_health/`:
- `links.yaml` (schema in docs): per link `name`, `logger`, `fields` (or a field prefix), `expected_rate_hz`,
  `max_age_s`, optional `probe` `{type: none|ping|tcp, host, port, interval_s}`, optional `register_id`
  (the #151 connection register entry). Default `probe: none`.
- `LinkHealthReader(Reader)`: every `interval_s` (default 10) reads `status:logger_status`, the link's
  fields and `stderr:logger:<logger>` from the cache over HTTP (`/latest`, stdlib `urllib`, read only), runs
  due probes, and returns one record with fields per link: `link:<name>:state`, `:age_s`, `:rate_hz`,
  `:expected_hz`, `:errors_5m` (stderr lines classified by regex into serial, parse, timeout, other, with
  per-class counts), `:reachable` (1, 0 or empty when no probe), `:evidence` (one plain sentence), and
  `link:summary` (counts per state). A normal `CachedDataWriter` publishes it; nothing new in core.
- Verdict rules: OFF if the logger is EXITED; FAILED if the logger FAILED, or age over `max_age_s`, or the
  probe fails 3 times in a row; DEGRADED if rate under 0.8 of expected, or errors over a threshold, or
  STARTING; else OK. Record time from the cache, not guesses.
- Probes, safety first: `ping` uses the system `ping -c 1 -W 1` (no raw sockets, no root); `tcp` only
  completes a connect and closes. **Never probe a data port**: many serial device servers accept one TCP
  client, so a probe can knock the logger off. The config check refuses a `tcp` probe whose host and port
  match any reader in the cruise definition, and the docs say to probe management ports only. No subnet
  scans, minimum interval 10 s, targets only from `links.yaml`.
- `endpoint.py`: stdlib HTTP server, bind `127.0.0.1` by default (science-LAN address opt-in), read only:
  `GET /health` (JSON of every link and the summary), `GET /health/<link>` (HTTP 200 for OK or OFF, 503
  for DEGRADED or FAILED, so Uptime Kuma, Zabbix web scenarios and LibreNMS `check_http` work with no
  plugin), `GET /metrics` (Prometheus text). No secrets in output.
- `noc_ingest.py`: `POST /noc/<source>` on the same server, disabled by default, requires a shared token
  header; accepts Uptime Kuma, Zabbix and LibreNMS webhook JSON through a small per-source mapping and
  publishes `noc:<source>:<monitor>` fields (state, message, time) to the cache via core `CachedDataWriter`.
  Body cap 64 KB, JSON only, never executes or forwards anything.
- `docs`: setup for each NOC tool (Uptime Kuma HTTP monitor with keyword or JSON query, Zabbix HTTP agent
  item plus webhook media type, LibreNMS service check plus API transport), and a table of what OpenRVDAS
  already provides versus what this adds.

## Failing test first
`contrib/deepsignal/test/link_health/test_link_health.py`: verdict rules for every state; rate and age
from a fake cache (a stdlib HTTP server in the test serving `/latest`); stderr classification; probe
refusal when the target is a reader's data port; ping and tcp probes against 127.0.0.1 only; endpoint
JSON, per-link HTTP codes, Prometheus text format; webhook token required, body cap, mapping for each of the
three tools from sample payloads written in the test; `None` handling; replay determinism of the verdict
function given fixed inputs.

## Module contract
Sample config `contrib/deepsignal/configs/link_health_demo.yaml` and `contrib/deepsignal/configs/link_health_links.yaml`
(NBP1406 loggers, no probes). Depends on no other module.

## Acceptance (exact commands, from repo root, Linux, no browser)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/link_health -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/link_health contrib/deepsignal/test/link_health
```

## Scope
Create or change only: `contrib/deepsignal/link_health/**`, `contrib/deepsignal/test/link_health/**`,
`contrib/deepsignal/docs/link_health.md`, `contrib/deepsignal/configs/link_health_*.yaml`, and empty
`__init__.py` files where missing. Everything else is read-only.

## Usability (anything a tech sees or edits)
Answer each line of desk `docs/USABILITY.md` in the report, or N/A with a reason. Every evidence line
names the link, what was seen, what was expected, and the first thing to check ("No data from gyro for
95 s (limit 30 s). Logger RUNNING, device answers ping: check the serial cable or the device output.").

## Trust boundaries and data integrity
Webhook bodies and cache values are untrusted: `json.loads` only, size caps, no `eval`, no shell
interpolation (probe commands are argument lists, host validated as an IP or hostname). Never change
incoming fields. Missing data is shown as missing, never as zero.

## Non-goals and banned
No Intermapper clone: no topology maps, no SNMP polling, no subnet discovery (the NOC tool does those). No
probes of data ports, OT networks outside the #151 register, or anything not in `links.yaml`. No core
changes, no new dependency. No loosened, skipped or deleted tests, no swallowed errors, no sleeps for
ordering (poll with a timeout).

## Stop rule
No code change needed: stop and report. Two fix rounds still red: stop and report.

## Result (builder fills in)
- Head sha:
- RED receipt:
- Acceptance tails:
- Open questions:
