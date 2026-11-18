You are building ONE module for the DeepSignal overlay on OpenRVDAS, on Eugene's own fork. Work only in this repository (eugenevivino/openrvdas). Do NOT touch, open pull requests against, or push to OceanDataTools or any upstream repository. Nothing here is sent upstream.

Branches: create branch `deepsignal/p2-instrument-init` from commit `3b4b76e` (the contrib master tree; it is in this fork's history, for example `git merge-base origin/deepsignal/vector-wind origin/deepsignal/instrument-history`) (if `deepsignal/p2-instrument-init` already exists on origin, check it out instead). Commit your work on that branch only, with one clear commit message, and leave it pushed to origin `deepsignal/p2-instrument-init`. Do not touch any other branch, `dev` or `master`. If you cannot push, leave the commit on the branch in your task and say so.

Environment notes: Python only; Node is not needed. Use `python3.12` if it exists, otherwise `python3` (3.11 or newer). If pytest is missing use `python3 -m unittest`. If flake8 is missing, `pip install flake8` into a throwaway venv and say you did. PyYAML is already an OpenRVDAS dependency; add no other dependency. No network.

Write the failing test first and paste its RED output, then make it GREEN. Run every acceptance command at the end and paste the tails. Report under 40 lines: files changed, test names, RED then GREEN tail, acceptance results, any design point you disagree with (do not change a design silently), what you verified versus inferred, and what must run outside the sandbox.

Stop rule: two fix rounds still red means stop and report.

The full brief follows.

----------------------------------------------------------------
# Brief: p2-instrument-init (Instrument init profiles (sensor setup over the wire))

- Decision: D-PARITY1, IDEAS #130 (Eugene approved building #104-#124, 2026-11-18)
- Risk tier: high
- Module: exactly one. Branch `deepsignal/p2-instrument-init` from `3b4b76e`
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: openrvdas_contrib tree, fork only for now
- Value (techs/science/shore): 5/3/1
- Depends on: none; #121 device pack and #114 wizard will ship and propose profiles in this format

## Goal
An instrument that needs commands before it talks (wake, set mode, set output rate or units, start
sampling, optionally set its clock) is set up from a reviewed per-instrument profile. Each reply is checked.
The profile is re-run after a power loss or reconnect, and every byte sent and received is logged, so a tech
can see exactly what the system told each sensor and what it said back.

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
- What core already has (do not duplicate; reuse where it fits): `PolledSerialReader` takes `start_cmd`,
  `pre_read_cmd` and `stop_cmd`, with `__PAUSE__ <s>` and escape handling. `start_cmd` is sent once, when
  the reader is constructed. Its reply is never checked, a send failure is only logged, and it is not resent
  when the instrument power-cycles. Network readers send nothing. `SerialReader.read()` returns None on a
  `SerialException` and never reopens.
- MetAcq 2.15's manual documents only per-module poll commands (`CMD`, `CMD2`, `CMD3` in the .ACQ file,
  with `#` attention characters and escapes) and a 300 ms timeout. It says nothing about init or re-init.
  This module goes beyond it.

## Safety rules (non-negotiable; tests prove each one)
1. Only bytes written in a profile are ever sent. The module never builds, guesses or sweeps commands, and
   it never sends anything to a port or address that has no profile.
2. A profile is explicit, per instrument, and versioned (`profile_id`, `version`, `reviewed_by`,
   `reviewed_on`). A profile with no `reviewed_by` loads only with `allow_unreviewed: true` on the reader.
   The first send under that flag logs one warning per run.
3. Each step has a `class`: `query` (read-only, for example a status or ID request), `setup` (changes
   instrument settings), or `persist` (writes to instrument non-volatile memory or firmware). `persist`
   steps never run automatically on reconnect. They run only through the CLI with `--allow-persist --yes`.
4. Every send and every reply is appended to a JSONL audit log. Each record holds the UTC time, instrument
   id, profile id and version, trigger (`open`, `reconnect`, `silence`, `manual`), step name, bytes sent
   (as text plus hex), reply (as text plus hex), match result and elapsed ms. Never truncate or rewrite
   the log.
5. Secrets (for example a device password in a step) come only from an environment variable named in the
   profile. They show as `***` in logs and output.

## Design (lead decisions; flag disagreement in the report)
Package `contrib/deepsignal/instrument_init/`:
- Profile YAML (example `contrib/deepsignal/configs/instrument_init_example.yaml`, written for a
  generic ASCII instrument; do not invent real vendor commands):
  ```yaml
  profile_id: example-met-v1
  version: 3
  reviewed_by: "J. Tech"
  reviewed_on: 2026-11-01
  source: "Vendor manual rev C, p. 42"     # required free text
  line_ending: "\r\n"
  steps:
    - {name: wake, class: query, send: "\r", pause_s: 0.5, expect: null}
    - {name: id, class: query, send: "*ID?", expect: "^EX-MET .*", timeout_s: 1.0, retries: 2}
    - {name: rate_1hz, class: setup, send: "RATE 1", expect: "^OK$", timeout_s: 1.0, retries: 1}
    - {name: set_clock, class: setup, send: "TIME {utc:%H:%M:%S}", expect: "^OK$", optional: true}
    - {name: start, class: setup, send: "GO", expect: null}
  reinit:
    on_reconnect: true
    after_silence_s: 30        # no data for this long: re-run the non-persist steps (null disables)
    max_per_hour: 6            # back-off cap; past it, log an error and keep reading without re-init
  ```
  `{utc:FMT}` is the only template allowed: the current UTC time in strftime format. Anything else in
  braces is a load error. `expect` is a regex matched against each reply line until `timeout_s`. A
  required step that fails after its retries aborts the sequence and logs an error, and the reader keeps
  reading. Steps marked `optional: true` log a warning and continue.
- `profile.py`: load and validate with `yaml.safe_load`. Each error is one plain line naming the step and
  the setting.
- `runner.py`: `run(profile, transport, trigger, audit, classes={'query', 'setup'})`. `transport` is a
  small interface (`write(bytes)`, `readline(timeout) -> bytes|None`) so tests use fakes.
- `InitSerialReader` in `serial_reader.py`: subclass of core `SerialReader` (exists on both the contrib
  base and current core) with `profile_file`, `audit_log` and `allow_unreviewed`. It runs the profile after
  open, and its `read()` handles re-init:
  - Re-init after `after_silence_s` with no data.
  - Reopen on `SerialException`, with backoff of 1, 2, 4, up to 30 s, then re-init when `on_reconnect` is
    set.
  - Re-init respects `max_per_hour`.
- `InitTCPClientReader` in `tcp_client_reader.py`: for instruments that serve TCP (the module connects
  out to a named host and port, then runs the same profile and reads lines). It uses the same reconnect
  and re-init rules. No UDP sending in v1; the docs say why (no reply channel to check).
- CLI `python -m contrib.deepsignal.instrument_init`:
  - `check <profile>`: validate.
  - `plan <profile>`: print exactly what would be sent, with nothing opened.
  - `run <profile> --serial PORT --baud N | --tcp host:port [--allow-persist] --yes`: needs `--yes`.
  - `log <audit.jsonl> [--instrument id]`: readable view of what was sent and received.
- Profiles are meant to come from #121 (cited manuals) and be proposed by the #114 wizard. Document the
  file format so both can produce it. Do not import them.

## Failing test first
`contrib/deepsignal/test/instrument_init/test_init.py` with a fake transport and a fake serial module:
- the sequence is sent in order with line endings
- an `expect` match passes, and a mismatch retries and then aborts
- an optional step continues
- the `{utc:...}` template is filled from an injected clock
- any other template is rejected
- an unreviewed profile is refused without the flag
- a `persist` step is skipped on reconnect and on silence
- after a fake `SerialException` the port reopens with backoff and re-inits
- the silence re-init fires once, and the `max_per_hour` cap holds
- the audit log has one record per send and per reply, with hex
- a secret from an env var never appears in the log
- `plan` opens nothing
- `run` without `--yes` exits 2
- an instrument with no profile gets zero writes; assert the fake's write count

## Module contract
Docs `contrib/deepsignal/docs/instrument_init.md`: what core `start_cmd` already does and when to use it
instead, the profile format, the three step classes, the safety rules above, and a worked example. A
lead-run check on real hardware happens outside the sandbox, with a tech present. Depends on no other
module.

## Acceptance (exact commands, from repo root, Linux, no browser)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/instrument_init -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/instrument_init contrib/deepsignal/test/instrument_init
```
```
python3.12 -m contrib.deepsignal.instrument_init plan contrib/deepsignal/configs/instrument_init_example.yaml
```

## Scope
Create or change only: `contrib/deepsignal/instrument_init/**`, `contrib/deepsignal/test/instrument_init/**`, `contrib/deepsignal/docs/instrument_init.md`, `contrib/deepsignal/configs/instrument_init_*.yaml`, and empty `__init__.py` files where missing. Everything else is read-only.

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
