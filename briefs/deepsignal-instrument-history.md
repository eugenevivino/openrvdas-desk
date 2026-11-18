# Brief: deepsignal-instrument-history

- Decision: D-SOII1 (IDEAS #52, extends #7; Eugene approved 2026-11-18)
- Risk tier: medium (metadata and calibration records; no data values change)
- Module: exactly one, instrument history registry plus checker. Branch `deepsignal/instrument-history`
- Base: `OceanDataTools/openrvdas_contrib` `master` at 3b4b76e
- Mac scratch path: `/private/tmp/deepsignal/instrument-history/` only (docs/CODEX.md rule 1b)
- Lane: `cloud` (Sol medium, fixed, so no `-m`; rules 8 and 27, D-TEAM7), fresh task, under 40 turns. Review: fresh `gpt-6.2-astra` high on a Mac, read-only.
- Upstream home: openrvdas_contrib (Eugene sends the PR)

## Goal
A tech keeps one plain YAML file that says, for every sensor, what was
installed where and when, its serial and firmware, every calibration and
repair; the ship can ask "what was true for this field at this time", and a
checker points out contradictions in plain English.

## Background facts (do not re-derive)
- contrib `master` carries a 2024 core tree. Copy the import-compatibility
  approach of `git show origin/deepsignal/vector-wind:contrib/deepsignal/logger/transforms/vector_wind_average_transform.py`.
- PyYAML is already an OpenRVDAS dependency. No other dependency.
- On the MacBook pytest is not installed; use `python3.12 -m unittest`.
- Applying calibration coefficients to data is a LATER module (#7). This
  module stores and answers questions only.

## Design (lead decisions; flag disagreement in the report, do not silently change)
Package `contrib/deepsignal/instruments/`:
- `history.py`: `InstrumentHistory.load(path)` and `from_dict(d)`.
- File shape:
  ```yaml
  instruments:
    - id: tsg1               # unique, short
      make: Sea-Bird
      model: SBE45
      serial: "0231"         # always a string
      fields: [TSG_Temp, TSG_Cond]   # data fields this instrument feeds
      events:
        - {time: 2026-03-01T00:00Z, type: install, position: "main lab intake"}
        - {time: 2026-03-01T00:00Z, type: calibration, cal_id: SBE45-0231-2026a,
           form: polynomial, coefficients: {TSG_Temp: [0.0021, 0.99987]},
           calibrated_on: 2026-02-10, valid_until: 2027-02-10, by: "Sea-Bird", certificate: "certs/0231-2026a.pdf"}
        - {time: 2026-06-12T14:30Z, type: firmware, version: "2.1b"}
        - {time: 2026-08-02T09:00Z, type: repair, note: "replaced pump"}
        - {time: 2026-09-30T00:00Z, type: remove}
  ```
- Event types: install, remove, calibration, firmware, repair, move,
  clock_source, software_version, note. Polynomial coefficients are lowest
  order first. Times are UTC ISO 8601; a bare date means 00:00Z.
- Queries (all take a UTC datetime or epoch seconds):
  `state_at(instrument_id, t)` returns serial, firmware, position, active
  calibration (latest calibration event at or before t), installed yes or no;
  `instrument_for_field(field, t)` returns the instrument installed and
  feeding that field at t, or None; `calibration_for_field(field, t)`.
- `check()` returns a list of findings, each `{level: error|warning, instrument, message}`:
  same serial installed in two places at once; a field fed by two installed
  instruments at once; events out of time order; calibration or firmware
  event while not installed; calibration expired (valid_until before now or
  before a given t); installed with no calibration; unknown event type;
  coefficients for a field the instrument does not list.
- CLI `python -m contrib.deepsignal.instruments check <file>` prints findings,
  exit 1 on any error; `... at <file> <field> <time>` prints the state.
- Load-time validation (usability rule 5): one plain-English line naming the
  instrument, the setting, what it saw, what it expected, and a good example.

## Failing test first
`contrib/deepsignal/test/instruments/test_history.py`. Write it first, paste RED.
Cover each query on boundary times (exactly at install, at remove, before
first event), each check finding, each validation message, serial kept as a
string, bare-date parsing, the CLI exit codes.

## Module contract
- Sample file `contrib/deepsignal/configs/instrument_history_example.yaml`
  for the NBP1406 sample fields, with at least one deliberate warning
  commented as such.
- Docs `contrib/deepsignal/docs/instrument_history.md`: one-sentence purpose,
  "Turn it on in 5 minutes", every event type with an example, how to read
  checker output, what it does NOT do (does not change data; applying
  calibrations is a later module).
- Empty `__init__.py` files as needed, identical to the wind branch.
- Depends on no other DeepSignal module.

## Acceptance (exact commands, from repo root)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/instruments -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal
```
```
python3.12 -m contrib.deepsignal.instruments check contrib/deepsignal/configs/instrument_history_example.yaml
```

## Scope
Create or change only files under `contrib/deepsignal/` listed above. Do not commit (sandbox blocks .git).

## Trust boundaries and data integrity
The YAML is hand-edited and untrusted: use `yaml.safe_load` only. Never
guess a missing time or serial. Never write back to the file.

## Non-goals and banned
No writes outside `/private/tmp/deepsignal/instrument-history/` (rule 28). No
core changes, no database, no GUI, no applying coefficients. docs/CODEX.md rule 13 applies.

## Report format
Under 40 lines: files, test names, RED then GREEN tail, flake8, design points you disagree with, verified vs inferred.

## Stop rule
Two fix rounds still red: stop and report.

## Result (builder fills in)
- Head sha:
- RED receipt:
- Linux check:
- What changed, in three lines:
- Open questions:
