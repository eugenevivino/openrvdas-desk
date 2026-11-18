# Shared header, prepend to every cloud prompt (D-UPSTREAM0)

- Work only on the fork eugenevivino/openrvdas, on your deepsignal/* branch. Never push to dev or master.
- gh and git may touch OceanDataTools only for a read-only fetch by URL. No pushes, PRs, issues or comments to any OceanDataTools repo, ever.
- Touch only the files your brief names. No secrets, no .env edits, no new dependencies unless the brief says so.
- No em dashes in any text you write.

You are building ONE module for the DeepSignal overlay on OpenRVDAS, on Eugene's own fork. Work only in this repository (eugenevivino/openrvdas). Do NOT touch, open pull requests against, or push to OceanDataTools or any upstream repository. Nothing here is sent upstream.

Branches: create branch `deepsignal/scoreboard-writer` from `deepsignal/scoreboard-integ` (the build lead's merge of #182 to #186; if it does not exist on origin, stop and report) (if `deepsignal/scoreboard-writer` already exists on origin, check it out instead). Commit your work on that branch only, with one clear commit message, and leave it pushed to origin `deepsignal/scoreboard-writer`. Do not touch any other branch, `dev` or `master`. If you cannot push, leave the commit on the branch in your task and say so.

Environment notes: Python only; Node is not needed. Use `python3.12` if it exists, otherwise `python3` (3.11 or newer). If pytest is missing use `python3 -m unittest`. If flake8 is missing, `pip install flake8` into a throwaway venv and say you did. PyYAML and pyserial are already OpenRVDAS dependencies; add no other dependency. No network beyond 127.0.0.1 test servers.

Write the failing test first and paste its RED output, then make it GREEN. Run every acceptance command at the end and paste the tails. Report under 40 lines: files changed, test names, RED then GREEN tail, acceptance results, any design point you disagree with (do not change a design silently), what you verified versus inferred, and what must run outside the sandbox.

Stop rule: two fix rounds still red means stop and report.

The full brief follows.

----------------------------------------------------------------
# Brief: deepsignal-scoreboard-writer (IDEAS #5: ScoreboardWriter, the OpenRVDAS writer that drives deck scoreboards)

- Decision: D-SCORE1, D-SCORE2, D-SCORE3 (stale defaults)
- Risk tier: medium (runs inside a logger, drives real boards; stale data on a deck board is a safety issue)
- Module: exactly one. Branch `deepsignal/scoreboard-writer` from `deepsignal/scoreboard-integ`
- Mac scratch path: `/private/tmp/deepsignal/scoreboard-writer/` only
- Lane: `cloud` (Sol medium, fixed)
- Wave: 2 (with #187 bench; disjoint files). Base `deepsignal/scoreboard-integ` = the build lead's merge
  of #182 to #186. If it does not exist on origin, stop and report; do not merge them yourself.
- Fresh session, under 40 turns
- Upstream home: fork only for now
- Depends on: #182 profiles, #183 transports, #184 to #186 codecs (imports them through `contract`)


## Shared scoreboard facts (identical in briefs #182 to #187 and the #5 writer brief; do not re-derive)

- Design: vendor-agnostic scoreboard output (D-SCORE2). Three layers: **transport** (how bytes or
  register writes leave), **codec** (`text`, `alpha`, `modbus`: how a board wants the data), **profile**
  (one YAML data file per board model). A new board needs a profile, never code. Design doc:
  https://claude.ai/artifact/XYUFNgc4nP67DBBS7RUviN
- Target hardware: outdoor deck LED scoreboards and large-digit displays (Eugene, 2026-11-18), not winch
  readouts. Brands vary by ship and are not known yet, so nothing may be hard-coded per vendor in Python.
- Package `contrib/deepsignal/scoreboard/` on the contrib tree `3b4b76e`. Layout (each brief owns only
  its listed files):
  ```
  contrib/deepsignal/__init__.py                  empty (create only if missing)
  contrib/deepsignal/scoreboard/__init__.py       empty
  contrib/deepsignal/scoreboard/contract.py       VERBATIM from the appendix, every branch
  contrib/deepsignal/scoreboard/profiles.py       #182
  contrib/deepsignal/scoreboard/profiles/*.yaml   #182
  contrib/deepsignal/scoreboard/transports/       #183 (__init__.py empty)
  contrib/deepsignal/scoreboard/codecs/__init__.py  empty
  contrib/deepsignal/scoreboard/codecs/text.py    #184
  contrib/deepsignal/scoreboard/codecs/alpha.py   #185
  contrib/deepsignal/scoreboard/codecs/modbus.py  #186
  contrib/deepsignal/scoreboard/bench.py          #187
  contrib/deepsignal/test/scoreboard/test_*.py    each brief its own test file
  ```
- **contract.py** (appendix) is the shared interface: `Profile`, `Page`, `Cell`, `RegisterWrite`,
  `Codec`, `Transport`, the error classes, `codec_class()`, `transport_class()`, `unescape()`,
  `checksum()`, `format_checksum()`. Copy it byte for byte (sha256 given in the appendix) and check the
  hash. Never edit it. If it blocks you, say so in the report; the build lead issues a new version.
- Registry by convention: `codecs/<name>.py` exports `CODEC = <class>`; `transports/<name>.py` exports
  `TRANSPORT = <class>`. `contract.codec_class('text')` imports it. No shared mutable registry file.
- Every empty `__init__.py` is zero bytes, so parallel branches merge cleanly.
- The ScoreboardWriter (IDEAS #5, brief `briefs/deepsignal-scoreboard-writer.md`, wave 2) is the only part that
  subclasses an OpenRVDAS Writer. Wave 1 briefs (#182 to #186) handle no records and subclass no
  OpenRVDAS class, so the old-core vs new-core import issue does not apply to them.
- Dependencies: standard library, PyYAML and pyserial only (both already OpenRVDAS requirements on
  `3b4b76e`). Add no dependency. Modbus is framed by hand (function code 16), not with pymodbus.
- Security: profiles are untrusted data. `yaml.safe_load` only. Templates use `str.format` on known keys
  only; reject any `{` field name that is not in the allowed set, and reject attribute or index access
  (`{a.b}`, `{a[0]}`). Never `eval`, `exec`, or `codecs.decode(..., 'unicode_escape')`; use
  `contract.unescape()`.
- Stale and missing values must never look fresh. A `Cell` with `stale=True` or `value=None` is shown as
  its `text` (the layout already put the stale marker there); the Modbus codec writes the profile's
  `stale_value`.
- Verified protocol facts available to this batch (cite these, do not add unverified ones):
  - Alpha Communications Protocol Rev D (Adaptive Micro Systems, 2002): frame is at least five `<NUL>`
    (00H) sync bytes (five `<SOH>` may substitute), `<SOH>`, type code, two-character sign address
    `00` to `FF` (`00` is broadcast), `<STX>`, command code, data, optionally `<ETX>` plus checksum, then
    `<EOT>`. Type code `Z` = "All signs". Command `A` = Write TEXT file; the data starts with a one-character
    File Label (power-up default `A`), then an optional Mode Field `<ESC>` + display position + mode code,
    then the message. Checksum: "Four ASCII digits that represent a 16-bit hexadecimal summation of all
    transmitted data from the previous <STX> through the previous <ETX> inclusive. The most significant
    digit is first." Checksum is used only when `<ETX>` precedes `<EOT>`. Bytes in a frame may not be more
    than 1 second apart. Baud for Alpha 2.0 signs: 1200 to 38400.
  - Modbus function code 16 (Write Multiple Registers), RTU: unit, `0x10`, start address (2 bytes, big
    endian), quantity (2), byte count (1), data (big-endian words), CRC-16/Modbus low byte first. Normal
    reply echoes unit, `0x10`, address, quantity, plus CRC. Exception reply: function `0x90` and one
    exception-code byte. TCP: 7-byte MBAP header (transaction id, protocol 0, length = bytes that follow,
    unit) then the same PDU without CRC.
  - Golden vectors computed with contract.py: CRC-16/Modbus of `b'123456789'` = `0x4B37`;
    CRC-16/CCITT-FALSE = `0x29B1`.

## Goal
A deck scoreboard shows the latest value of each chosen field, refreshed on its own clock, and shows
dashes (never the last good number) as soon as a field goes stale, whatever board model or link the
ship uses.

## Defaults decided by the lead (D-SCORE3, reversible; flag disagreement in the report)
- Stale threshold: per field, default 10 seconds (same as the console MVP source-loss test).
- Stale display: `stale_style: dash` (default) fills the cell width with `-`; `blank` fills it with
  spaces; `stale_text` overrides both. Never the last value.
- A value that has never arrived shows the same as stale.

## What to build
`contrib/deepsignal/scoreboard/scoreboard_writer.py`, class `ScoreboardWriter`, loadable from a logger
config with `class: ScoreboardWriter` and `module: contrib.deepsignal.scoreboard.scoreboard_writer`.

Base class: subclass OpenRVDAS `logger.writers.writer.Writer` and call `super().__init__()` with NO
arguments (works on both the old `3b4b76e` core and current core; see how
`git show origin/deepsignal/vector-wind:contrib/deepsignal/logger/transforms/vector_wind_average_transform.py`
does it). Do not call `can_process_record` or `digest_record` (not on the old core).

Constructor kwargs (all plain YAML values, so a logger config can set them):

| kwarg | Default | Meaning |
|---|---|---|
| `profile` | required | profile name or path, loaded with `profiles.load_profile` |
| `profile_overrides` | `{}` | deep-merged into the profile |
| `address` | profile default | board address or Modbus unit |
| `transport` | `{}` | merged over `profile.transport_defaults`; must contain `type` after merging |
| `pages` | required | list of pages; page = list of lines; line = list of cells (a single cell dict is accepted as a one-cell line) |
| `refresh_interval` | 1.0 | seconds between renders; raised to `1 / pacing.max_rate_hz` if that is slower |
| `page_dwell` | 5.0 | seconds per page when there is more than one |
| `stale_after` | 10.0 | default seconds before a field is stale |
| `stale_after_fields` | `{}` | per-field seconds, for example `{KnudDepthHF: 30}` |
| `stale_style` | `dash` | `dash` or `blank` |
| `stale_clock` | `arrival` | `arrival` (monotonic time the value arrived), or `both` (also stale when the record timestamp is older than the threshold by wall clock) |
| `send_on_change_only` | false | skip sending an identical frame set |
| `resend_interval` | 10.0 | with `send_on_change_only`, resend anyway at least this often so a rebooted board recovers |
| `max_backoff` | 30.0 | transport retry backoff cap, seconds |

Cell keys: `field` (source field name) or `text` (fixed label), `fmt` (Python format spec for numbers,
for example `6.1f`), `width` (required int), `align` (`right` default, `left`, `center`), `stale_after`
(overrides the field threshold), `stale_text`.

Validate everything at construction and raise `ValueError` naming the page, line and cell: unknown
keys, a line whose widths sum past `limits.chars_per_line`, more lines than `limits.lines`, a fixed
`text` longer than its width, bad `stale_style`. A ProfileError or TransportError from the lower layers
is re-raised as `ValueError` with the same message (listen.py reports ValueError cleanly).

Runtime:
1. `write(record)` only updates the cache and returns. Accept a DASRecord, a dict with `timestamp` and
   `fields`, a CDS field dict `{field: [[ts, value], ...]}` (latest timestamp wins), a list of any of
   these, or None (ignored). Normalize with a small local function; do not depend on
   `to_das_record_list` (its signature differs between cores). Store `(value, record_ts, arrival)`
   per field under a lock. A value of None counts as missing. Never raises on a bad record: log once
   per distinct problem at WARNING.
2. A daemon render thread starts in `__init__` (so a board shows dashes from the start), unless the
   private kwarg `_start_thread=False` is given (tests). `render_once()` is public for tests.
3. Each render builds a `contract.Page`: per cell, if stale or missing, text = stale text at `width`;
   else `format(value, fmt)` (or `str(value)` without `fmt`), aligned to `width`. If the formatted text
   is longer than `width`, show `#` repeated `width` times and log a warning once per field: never
   truncate a number. `Cell(field, text, value, stale)` with `value=None` when stale.
4. Encode with `contract.codec_class(profile.codec)(profile, address)`; send with
   `contract.transport_class(type)(**settings, inter_frame_delay=profile.pacing.get('inter_frame_delay', 0))`.
5. On TransportError: log once per outage (not per attempt), close, wait with exponential backoff (1,
   2, 4 ... `max_backoff` seconds), reopen, resend `codec.init()` frames, then continue. Log once on
   recovery. The logger never dies because a board is unplugged.
6. `close()` stops the thread, waits for it, closes the transport. Safe to call twice.
7. Private test hooks: `_clock` (monotonic), `_wall_clock`, `_sleep`, `_transport_factory`.

Sample config `contrib/deepsignal/configs/scoreboard_logger.yaml`: reads `CachedDataReader` fields
(server address as a variable comment), one ScoreboardWriter with `profile: generic_ascii`,
`transport: {type: udp, host: 127.0.0.1, port: 9999}`, two pages. It must run with `listen.py
--config_file` and print nothing alarming when no data arrives (the board shows dashes).

## Tests (at least these)
`contrib/deepsignal/test/scoreboard/test_scoreboard_writer.py` (fake clock and fake transport unless
stated):
- all record shapes update the cache; None and a malformed record do not raise
- a value shows formatted and right-aligned; at 10.0 s after arrival it still shows, at 10.1 s it is
  dashes; with `stale_style: blank` it is spaces; a per-field override of 30 s holds it longer
- a field that never arrived shows dashes; the last good value is never shown once stale (assert the
  digits of the old value do not appear in any frame after the threshold)
- `stale_clock: both`: a fresh arrival with an old record timestamp is stale
- overflow shows `#` x width
- layout wider than the board, too many lines, unknown cell key: ValueError at construction
- two pages alternate every `page_dwell`
- `send_on_change_only`: identical frames are skipped, then resent after `resend_interval`
- transport failure: one warning per outage, backoff 1 then 2 seconds, recovery resends `init()` frames
- `close()` twice is safe; the thread exits
- integration: `ListenerFromLoggerConfig` (or the old-core equivalent present on the base) builds the
  writer from the sample config shape with a UDP transport to a bound 127.0.0.1 socket; after one
  `render_once()` the socket receives the expected bytes from the `generic_ascii` profile

## Acceptance (exact commands)
```
python3 -m pytest contrib/deepsignal/test/scoreboard -q
```
```
python3 -m flake8 --max-line-length=100 contrib/deepsignal/scoreboard/scoreboard_writer.py contrib/deepsignal/test/scoreboard/test_scoreboard_writer.py
```
```
timeout 5 python3 logger/listener/listen.py --config_file contrib/deepsignal/configs/scoreboard_logger.yaml; test $? -eq 124
```

## Scope
Create: `scoreboard_writer.py`, the test file, `contrib/deepsignal/configs/scoreboard_logger.yaml`, and
`contrib/deepsignal/scoreboard/docs/writer.md` (a technician's page: pick a profile, set the transport,
lay out cells, what dashes mean, how to change the stale threshold). Read-only: everything else,
including `contract.py`, profiles, codecs and transports.

## Usability (a technician edits this config)
Answer each line of `docs/USABILITY.md` in the result, or mark N/A with a reason.

## Trust boundaries and data integrity
Records are untrusted. Stale or missing data is always visibly different from live data on the board.
The writer never alters, rounds or scales a value except through the cell's `fmt` and the profile's
codec rules.

## Non-goals and banned
No new codecs, transports or profiles. No CachedDataServer changes. No new dependencies.
No writes, deletes or moves in `/private/tmp` outside `/private/tmp/deepsignal/`; never `/private/tmp/kalon`.
No loosened, skipped or deleted tests, no swallowed errors, no sleeps for ordering (fake clock and
events).

## Report format
Under 40 lines: files, test names, RED then GREEN tails, acceptance tails, design disagreements,
verified versus inferred, and what must be checked with a real board and a live CachedDataServer.

## Stop rule
Two fix rounds still red: stop and report.

## Result (builder fills in)
- Head sha:
- RED receipt:
- Gate receipt sha256 and verdict:
- What changed, in three lines:
- Open questions:

## Appendix: contract.py (verbatim)
Canonical copy: desk `briefs/scoreboard/contract.py`, sha256 `d54e7183e0961744d7aa84ec5bae42e446982701d18f4ac3919a2837a5ea1196`. The cloud prompt
`briefs/cloud/scoreboard-writer.md` carries the full text. Wave 1 creates
`contrib/deepsignal/scoreboard/contract.py` byte for byte and checks the hash; wave 2 finds it in the base.
