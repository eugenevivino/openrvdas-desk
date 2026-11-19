# Brief: CDS gate redesign, fix round 1 (D-FASTREV1 pilot finding; CRITICAL, security)

- Branch `deepsignal/sec-cds-joint` (the checked-out branch, after slice 3). Design note: desk `docs/designs/security-redesign.md`. Lane: Mac, `gpt-6.2-sol` high. Push-only, never auto-merged.
- Finding (fast review pilot at 5fb327f, install-security part, INFERRED): `contrib/deepsignal/security/cds_gateway.py:57` connects UPSTREAM to the CDS with `max_size=None`. A valid subscribe for up to 200 high-rate fields with a large `seconds` or `back_records` request can make the real CDS return one very large frame that the gateway buffers whole, exhausting memory.

## Fix exactly this
1. Bound the upstream CDS frame size (a named constant, documented in `contrib/deepsignal/docs/security-cds.md`). An oversize upstream frame is refused: the gateway closes that client with a clear error message and does not buffer the frame; the gateway itself keeps serving other clients.
2. Only if each is a one-line change, also: (a) validate per-field subscribe option values at the gateway (types and ranges the CDS accepts; refuse anything else); (b) the installer refuses to keep an existing site file whose mode is group- or world-writable. If either is more than a one-line change, leave it and say so (it stays a ticket).
3. Every fix needs a production-path regression plus one variation that must keep the same answer (D-FIX1): for the frame bound, an oversize frame is refused AND a normal-size frame for the same subscription still passes.

## Acceptance (exact commands, from repo root)
```
python3.12 -m pytest -p no:cacheprovider contrib/deepsignal/test/security contrib/deepsignal/console/install contrib/deepsignal/test/console/test_install.py test/server/test_cached_data_server_host.py -v -k "not real_197"
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal
```

## Scope
`contrib/deepsignal/security/cds_gateway.py`, `contrib/deepsignal/test/security/**`, `contrib/deepsignal/docs/security-cds.md`, and for item 2b only `contrib/deepsignal/console/install/**` with its tests.

## Non-goals and banned
No new features, no deleted, skipped or loosened tests, no sleeps, no new dependencies, no sub-agents.

## Stop rule
Report any finding that needs a change to the design note instead of changing it.
