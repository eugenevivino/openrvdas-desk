# Brief: p2-device-pack (UNOLS met device definitions (core contrib/devices))

- Decision: D-PARITY1, IDEAS #121 (Eugene approved building #104-#124, 2026-11-18)
- Risk tier: medium
- Module: exactly one. Branch `deepsignal/p2-device-pack` from `1a6f1ed`
- Lane: `mac`: `gpt-6.2-sol`, `model_reasoning_effort=high` (needs network for manuals; not math)
- Fresh session, under 40 turns
- Upstream home: core, fork only (D-ARCH6)
- Value (techs/science/shore): 4/2/1
- Depends on: none; needs manufacturer manuals, so it runs where the network allows reading them (Mac)
- Needs Eugene: Formats must come from manufacturer manuals or real captured lines. Any device whose output format cannot be cited is left out and listed, never guessed. Real lines from a Revelle MetAcq raw file (R2R pilot, RR2205) would settle the uncertain ones.
- Mac scratch path: `/private/tmp/deepsignal/p2-device-pack/` only (rule 28)

## Goal
The common UNOLS met and underway sensors parse out of the box in OpenRVDAS, so a tech adds them by
picking a device name instead of writing a parser.

## Background facts (do not re-derive)
- Device definitions are YAML in `contrib/devices/*.yaml` (see `misc_device_types.yaml` on fork `dev`):
  a device type has `category: "device_type"`, `description`, `format` (one or more patterns in Python
  `parse` syntax, keyed by message name) and `fields` with `units` and `description`.
- The MetAcq MetSpecs list (Rev 1.18, https://calcofi.org/downloads/underway/2021/2107SR/met/docs/MetSpecs.pdf)
  names the suite: RM Young 05103 and 85106 anemometers, Vaisala HMP155 (T/RH) and PTB barometers, Eppley
  PSP and PIR radiometers, Sea-Bird SBE45 thermosalinograph and SBE43 oxygen, Biospherical QSR PAR,
  LCI-90 winch display, and Advantech ADAM-4000 or DGH analog modules (ASCII protocol, polled).
- Many of these output analog or polled ASCII through a module; the device type is then the module's
  response format plus field scaling, not the sensor itself. Say which.

## Design
- New file `contrib/devices/UNOLS_met.yaml` only. One device type per output format actually documented.
- Each device type carries a comment with the manual title, revision and page the format comes from.
- For each, a test fixture line: from a real capture if one is in this repository, else built from the
  manual's own example output, marked `# from manual example, p. N`.
- ADAM-4000 ASCII: document how `PolledSerialReader` with a `pre_read_cmd` dict (fork `dev` supports
  round-robin polling with per-command timeout) polls several addresses, and the response pattern for
  the read-all-channels command, from the Advantech manual. Docs only plus the device type; no new reader.

## Failing test first
`test/contrib/test_unols_met_devices.py`: every device type loads with the repository's device-definition
loader; each fixture line parses to the documented field values and units; a corrupted line fails.

## Acceptance (exact commands, from repo root)
```
python3.12 -m pytest test/contrib/test_unols_met_devices.py -v
```
```
python3.12 -m pytest test/logger/transforms/test_parse_transform.py -q
```

## Scope
New files only: `contrib/devices/UNOLS_met.yaml`, `test/contrib/test_unols_met_devices.py` (and an
empty `test/contrib/__init__.py` if needed), `contrib/devices/UNOLS_met.md` (sources table, polling recipe,
devices left out and why).

## Trust boundaries and data integrity
Existing behavior and output bytes of every current config stay identical unless the new option is set.
Default values of existing classes do not change.

## Non-goals and banned
No upstream PR or issue (D-ARCH6, fork only). No refactors, renames or formatting outside the listed
files. No new dependency. No loosened, skipped or deleted tests, no swallowed errors, no sleeps for test
ordering.

## Stop rule
No code change needed: stop and report. Two fix rounds still red: stop and report.

## Result (builder fills in)
- Head sha:
- RED receipt:
- Acceptance tails:
- Open questions:
