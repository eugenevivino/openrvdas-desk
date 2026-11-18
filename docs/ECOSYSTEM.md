# DeepSignal in the OceanDataTools ecosystem

Written 2026-11-18 by the parity thread, from the OceanDataTools source code read at the commits below.
All of this research was read-only. Under D-UPSTREAM0, nothing goes to OceanDataTools (no issues, PRs or
comments) until Eugene approves.

## The story in one paragraph

OpenRVDAS acquires the data, OpenVDM packages and ships it, Sealog records what people did, and Grafana
shows it. None of them says whether the data is any good. **DeepSignal is the quality and intelligence
layer that runs across all four.** It flags every value, notices when a stream goes stale, sets up
instruments safely, and explains problems. Each of those results then flows into the tool the person
already uses:

- QC results go into the OpenVDM cruise package and its dashboard.
- Quality changes go into the Sealog event log, and every event records the quality state at that moment.
- QC colors and alerts go into Grafana.
- Compressed, prioritized bundles go ashore through OpenVDM's ship-to-shore path.

Nothing in those tools has to change. DeepSignal plugs into each one through the extension point it
already publishes.

```
 instruments ──► OpenRVDAS ──► raw logs ─────────────► OpenVDM cruise package ──► shore (S2S, priority 1-5)
     ▲              │                                     ▲   ▲  Data Dashboard         ▲
     │ init (#130)  ▼                                     │   │  (#131 plugin)          │ bundles (#135)
     └──────── DeepSignal ── QC day files (#131) ─────────┘   └─ archive .zst (#135) ───┘
                    │  ├── quality events, aux data (#133) ──► Sealog (event log, science)
                    │  ├── QC fields, freshness (#134) ──────► InfluxDB ► Grafana dashboards and alerts
                    │  └── cruise id, dates (#132) ◄──────────  OpenVDM or Sealog cruise record
                    └── console, MCP, REST (#105) for people who use none of the above
```

## What each tool is, and its integration surface

### OpenVDM (vessel data management)

Source: github.com/OceanDataTools/openvdm, version 2.17.0, commit `5d163fc` (2026-11-12). MIT license. It
is very active: 2.17 adds vessel R2R ids, a File Naming Guide and README templates.

- **Collection System Transfers (CSTs)** copy files from acquisition systems into
  `<data root>/CruiseData/<cruiseID>/<destination>` with rsync. They support local, SMB, rsync, SSH and FTP
  sources (FTP via rclone), with include, exclude and ignore globs. A CST is registered in the web form.
  The File Naming Guide tells techs which file names each transfer accepts.
- **Data Dashboard plugins** are Python files at `server/plugins/<name>_plugin.py`, installed by copying a
  `.dist` file.
  - Each plugin has `fileTypeFilters` and a `PARSER_MAP`. Its parsers subclass `OpenVDMCSVParser`.
  - Output keys are `visualizerData`, `qualityTests` (`testName`, `results`: Passed, Warning or Failed) and
    `stats`.
  - **OpenVDM already ships `openrvdas_plugin.py.dist`** for OpenRVDAS raw logs (GGA, met, SSV, TSG, true
    wind), so raw data already flows. Quality does not.
- **Post hooks** (`openvdm.yaml` `postHookCommands`) run a command after a transfer, a dashboard update or
  a cruise setup or finalize, with `{cruiseID}`, `{newFiles}` and similar tokens.
- **Ship-to-shore** copies files matched by rules with priority 1 (highest) to 5 to the shoreside
  warehouse, under a bandwidth cap. I found no compression option in its transfer code. It keeps an MD5
  manifest.
- **API**: read endpoints such as `api/warehouse/getCruiseConfig`, `getLoweringID` and
  `api/dashboardData/getLatestQualityTestsByType`, a Gearman job queue, and a worker API key.

### Sealog (event logging)

Source: github.com/OceanDataTools/sealog-server, version 2.4.9, commit `46ccbf0`. MIT license. There are two
clients: vessel and vehicle (ROV, AUV, HOV).

- **REST** `/api/v1`: events, event aux data, event templates, cruises, lowerings and custom variables.
  Every route is behind a JWT.
- **Websocket**: pushes new, updated and deleted events live.
- **Event shape**: author, timestamp, `event_value`, options, free text. Aux data is
  `{event_id, data_source, data_array: [{data_name, data_value, data_uom}]}`.
- **Existing integrations**:
  - Aux-data inserters for InfluxDB (fed by OpenRVDAS) and for the CORIOLIX REST API.
  - `sealog_create_cruise_from_openvdm.py`, so OpenVDM and Sealog already share a cruise.
  - Auto-actions and responders.
- **OpenRVDAS core** already has `SealogReader` (websocket) and `SealogWriter`, which posts events through
  a field-map config.

### Grafana and InfluxDB tooling

- **OpenRVDAS core** has `InfluxDBWriter` and `GrafanaLiveWriter`, and `utils/install_influxdb.sh`
  installs InfluxDB and Grafana.
- **OceanDataTools panels**: `grafana-compass-panel` (on the Grafana marketplace, shows heading, true and
  apparent wind, set and drift) and `grafana-attitude-panel` (roll and pitch).
- **What's missing**: dashboards are built by hand, and nothing shows quality.

### QA processors (new in November 2026)

- `nav-qa-processing` ports R2R NavManager. It produces the R2R QA 2.0 navigation products and reports.
- `sbe-qa-processing` produces CTD QA reports and runs as an OpenVDM hook.
- `winch-data-processing` produces wire logs and RVSS Appendix A compliance reports.
- All three are marked "under heavy development" and validated on one or two cruises.
- **They overlap our plans.** #109's cast view should read winch-data-processing outputs rather than
  re-derive RVSS rules. The reanalysis plan should use nav-qa-processing for navigation QA. Adapters are
  backlog item #136.

### Other OceanDataTools repos (no integration planned)

- Ship-specific OpenRVDAS configs: Sikuliaq, RCRV, USAP, Stony Brook, Alucia. These are useful real
  configs for testing #126 and #127.
- `openvdm_sample_data`: use it for the #131 check.
- `openrvdas-ansible`.
- Templates: `fastapi-template` and `vite-react-template`, the same stack as the new OpenRVDAS web UI.
- Discord bots.

## Integration plan, ranked by value

| Rank | IDEAS | What | Plugs in through | Value (techs/science/shore) | Brief |
|---|---|---|---|---|---|
| 1 | #133 | Sealog bridge: quality events, plus quality aux data on every event | core `SealogWriter`, Sealog websocket and aux-data API | 4/5/3 | `briefs/p2/133-sealog-bridge.md` |
| 2 | #131 | OpenVDM bridge: QC day files, plus a Data Dashboard plugin with pass, warning and fail tests | CST plus `.dist` plugin and parser | 4/4/4 | `briefs/p2/131-openvdm-bridge.md` |
| 3 | #135 | Lossless archive (zstd or xz, manifest, verified) and prioritized shore bundles | files plus OpenVDM extra directory and S2S rule | 3/4/5 | `briefs/p2/135-archive-compress.md` |
| 4 | #134 | Grafana quality pack: flag colors, freshness, alerts, compass panel | core `InfluxDBWriter` plus provisioning files | 4/3/4 | `briefs/p2/134-grafana-quality.md` |
| 5 | #132 | Cruise context from OpenVDM or Sealog into DeepSignal cruise metadata | read-only GET of `getCruiseConfig` and `/api/v1/cruises` | 4/3/3 | `briefs/p2/132-cruise-context.md` |
| 6 | #136 | QA tool adapters (nav, CTD, winch verdicts into the console and Sealog) | OpenVDM post hooks | 3/4/3 | backlog |

All of these are DeepSignal modules, with fork-only branches and cloud lane builds. None of them changes
OpenRVDAS core, OpenVDM, Sealog or Grafana.

## Compression: what "industry standard" means here

- **Raw logs: lossless only.** zstd is the default where the `zstd` tool exists. It is fast, about as
  dense as xz, and used by Linux distributions. xz is the stdlib fallback, and gzip is offered for maximum
  compatibility. Every compressed file is decompressed and checked against the original's sha256 before
  anything else happens. Originals are kept unless someone explicitly asks for deletion. A manifest
  records the codec, version and level, and two runs produce identical bytes.
- **Science formats: NetCDF4/CF**, which is HDF5 with chunked zlib compression. ERDDAP (#104) already
  writes it on request from our datasets, so there is nothing to build now. An offline NetCDF or Parquet
  export would need an optional dependency, which is a later decision.
- **Over satellite:** OpenVDM's ship-to-shore path has priorities and a bandwidth cap but no compression.
  #135 makes small priority-tagged `.tar.zst` bundles that OpenVDM ships as ordinary files. Live values
  continue to use the #123 snapshot (a PNG plus compact JSON) and idea #18 (a buffered, compressed live
  stream).

## Risks and unknowns

- **Unverified field names.** The OpenVDM and Sealog field names come from source code, not from a live
  system. Each brief marks its fixtures "verify on a live system", and the lead runs that check outside
  the sandbox.
- **Plugin installs need a person.** OpenVDM plugins are installed by copying `.dist` files, which a person
  does on the OpenVDM host. The #131 docs give the exact steps, and the MCP setup engine can show them but
  never runs them.
- **Credentials.** Sealog needs a JWT and Grafana alerting needs a service account. Both are read from
  environment variables only and never logged.
