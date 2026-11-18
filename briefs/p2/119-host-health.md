# Brief: p2-host-health (Host health reader)

- Decision: D-PARITY1, IDEAS #119 (Eugene approved building #104-#124, 2026-11-18)
- Risk tier: low
- Module: exactly one. Branch `deepsignal/p2-host-health` from `3b4b76e`
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: openrvdas_contrib tree, fork only for now
- Value (techs/science/shore): 4/1/4
- Depends on: display is the console `health` module: the build lead routes a small follow-up there; this task only publishes fields

## Goal
The acquisition computer reports its own health (disk, memory, load, clock offset, logger restarts) as
ordinary data fields, so the health page can warn before a full disk or a drifting clock costs data.

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

## Design (lead decisions; flag disagreement in the report)
Package `contrib/deepsignal/host_health/`, class `HostHealthReader` (an OpenRVDAS Reader).
- `read()` blocks until the next `interval` (default 30 s) and returns one DASRecord with
  `data_id='host'` and fields:
  `host_disk_free_pct` and `host_disk_free_gb` for each configured path (default `/` and the logfile
  root, field suffix from a configured short name), `host_mem_available_pct` (from `/proc/meminfo`
  MemAvailable / MemTotal), `host_load1` (os.getloadavg), `host_uptime_s`, `host_clock_offset_s` (from
  `chronyc -c tracking` if the command exists, field 4 "last offset" in seconds; else the field is absent
  and one info line is logged), `host_supervisor_restarts` (count of supervisord programs whose
  `supervisorctl status` uptime is under `restart_window` seconds; absent if supervisorctl is missing).
- Every probe is a small function taking injected readers (file text, command output), so tests need no
  real host. A probe that fails omits its field and logs once per failure type; it never raises out of
  `read()`.
- Commands run with a 5 s timeout, no shell (`subprocess.run([...], shell=False)`), fixed argument lists.
- Example logger config `contrib/deepsignal/configs/host_health_example.yaml` writes to `CachedDataWriter`.

## Failing test first
`contrib/deepsignal/test/host_health/test_reader.py`: each probe on canned text (meminfo, chronyc CSV line,
supervisorctl output with one recent restart); missing command; probe exception omits the field only;
interval honored with a fake clock; record shape.

## Module contract
Docs `contrib/deepsignal/docs/host_health.md` including suggested thresholds for the health page
(disk under 10% warn, under 5% alarm; clock offset over 0.5 s warn). Depends on no other module.

## Acceptance (exact commands, from repo root, Linux, no browser)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/host_health -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/host_health contrib/deepsignal/test/host_health
```

## Scope
Create or change only: `contrib/deepsignal/host_health/**`, `contrib/deepsignal/test/host_health/**`, `contrib/deepsignal/docs/host_health.md`, `contrib/deepsignal/configs/host_health_*.yaml`, and empty `__init__.py` files where missing. Everything else is read-only.

## Usability (anything a tech sees or edits)
Answer each line of desk `docs/USABILITY.md` in the report, or N/A with a reason. Every config error is one
plain-English line naming the setting, what it saw, what it expected, and a good example.

## Trust boundaries and data integrity
Config and input files are hand-edited and untrusted: `yaml.safe_load` only, no `eval`. Never change or
drop an incoming value; only add fields or write new files. Missing or stale inputs are shown as such,
never guessed.

## Non-goals and banned
No core changes. No new dependency. No network. No refactors, renames or formatting outside Scope. No
loosened, skipped or deleted tests, no swallowed errors, no sleeps for test ordering.

## Stop rule
No code change needed: stop and report. Two fix rounds still red: stop and report.

## Result (builder fills in)
- Head sha:
- RED receipt:
- Acceptance tails:
- Open questions:
