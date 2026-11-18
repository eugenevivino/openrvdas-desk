You are building ONE module for the DeepSignal overlay on OpenRVDAS, on Eugene's own fork. Work only in this repository (eugenevivino/openrvdas). Do NOT touch, open pull requests against, or push to OceanDataTools or any upstream repository. Nothing here is sent upstream.

Branches: create branch `deepsignal/p2-archive-compress` from commit `3b4b76e` (the contrib master tree; it is in this fork's history, for example `git merge-base origin/deepsignal/vector-wind origin/deepsignal/instrument-history`) (if `deepsignal/p2-archive-compress` already exists on origin, check it out instead). Commit your work on that branch only, with one clear commit message, and leave it pushed to origin `deepsignal/p2-archive-compress`. Do not touch any other branch, `dev` or `master`. If you cannot push, leave the commit on the branch in your task and say so.

Environment notes: Python only; Node is not needed. Use `python3.12` if it exists, otherwise `python3` (3.11 or newer). If pytest is missing use `python3 -m unittest`. If flake8 is missing, `pip install flake8` into a throwaway venv and say you did. PyYAML is already an OpenRVDAS dependency; add no other dependency. No network.

Write the failing test first and paste its RED output, then make it GREEN. Run every acceptance command at the end and paste the tails. Report under 40 lines: files changed, test names, RED then GREEN tail, acceptance results, any design point you disagree with (do not change a design silently), what you verified versus inferred, and what must run outside the sandbox.

Stop rule: two fix rounds still red means stop and report.

The full brief follows.

----------------------------------------------------------------
# Brief: p2-archive-compress (Lossless archive compression and shore bundles)

- Decision: IDEAS #135, from Eugene's 2026-11-18 asks (config assist, sensor init, ecosystem and compression); build per D-NIGHT1
- Risk tier: high
- Module: exactly one. Branch `deepsignal/p2-archive-compress` from `3b4b76e`
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: openrvdas_contrib tree, fork only for now
- Value (techs/science/shore): 3/4/5
- Depends on: none; #123 shore snapshot and #131 manifests can be bundled

## Goal
Closed raw logs shrink several times with industry-standard lossless compression, verifiably identical when
decompressed, and the most important data reaches shore first in small compressed bundles over satellite.

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
- OpenRVDAS writes plain text logs (`LogfileWriter`, daily split by default) and compresses nothing.
  OpenVDM's ship-to-shore transfer has priorities 1 to 5 and a bandwidth cap, and keeps an MD5 manifest;
  no compression option was found in its transfer code.
- Python 3.12 stdlib has gzip, bz2 and lzma (xz). zstd is not in the 3.12 stdlib: use the `zstd` command
  line tool when `shutil.which('zstd')` finds it; otherwise fall back to xz and say so. No new Python
  dependency.

## Design (lead decisions; flag disagreement in the report)
Package `contrib/deepsignal/archive/`:
- `compress_closed(root, codec='auto', level=None, min_age_s=3600, delete_originals=False)`: only files
  whose mtime is older than `min_age_s` and that are not today's file (never the file being written).
  Codecs: `zstd` (level 19, `--long=27`), `xz` (preset 9), `gzip` (level 9, `mtime=0`, for maximum
  compatibility). Output `<name>.zst|.xz|.gz` beside, or in `--out DIR` mirroring the tree.
- Byte-reproducible: fixed levels, no embedded names or times (gzip `mtime=0` and no file name; zstd keeps its content checksum). The manifest records codec, tool version, level.
- Verify before anything else: decompress to memory or a temp file and compare sha256 to the original;
  any mismatch is an error and the original is untouched. `delete_originals` needs the flag AND a verified
  copy, and is off by default.
- `MANIFEST.sha256` per directory: original name, original sha256 and size, compressed name, sha256, size,
  codec. Appended, never rewritten; `verify DIR` re-checks everything.
- `bundle(spec, out)`: shore bundles for ship-to-shore. `spec` lists globs with priority 1 to 5 and a size
  budget per bundle; writes `bundle-<cruise>-<UTC>-p<priority>.tar.zst` (or `.tar.xz`) plus its manifest
  into a directory an OpenVDM Extra Directory and Ship-to-Shore rule can pick up (docs give the form values).
- CLI: `python -m contrib.deepsignal.archive compress|verify|bundle|plan` (`plan` lists what would happen,
  touching nothing).
- Non-goal now: offline NetCDF4/Parquet export (ERDDAP #104 serves netCDF on request; offline export is a
  later phase that may need an optional dependency, decided then).

## Failing test first
`contrib/deepsignal/test/archive/test_archive.py`: round trip for each codec available (xz and gzip always;
zstd only if the tool exists, otherwise the auto fallback is asserted); today's file and young files are
never touched; corrupt output is caught by verify and the original kept; delete only with flag and verify;
manifest append-only; two runs give identical bytes; bundle priority order and size budget; `plan` touches
nothing.

## Module contract
Docs `contrib/deepsignal/docs/archive.md` with measured ratios on `test/NBP1406` logs for each codec.

## Acceptance (exact commands, from repo root, Linux, no browser)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/archive -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/archive contrib/deepsignal/test/archive
```
```
python3.12 -m contrib.deepsignal.archive plan test/NBP1406
```

## Scope
Create or change only: `contrib/deepsignal/archive/**`, `contrib/deepsignal/test/archive/**`, `contrib/deepsignal/docs/archive.md`, `contrib/deepsignal/configs/archive_*.yaml`, and empty `__init__.py` files where missing. Everything else is read-only.

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
