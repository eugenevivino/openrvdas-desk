# Design note: security-redesign (D-DESIGN1)

- Unit: `sec-cds-joint` on fork branch `deepsignal/sec-cds-joint`; launcher unit name `security-redesign`. CRITICAL.
- Status: FIXED (2026-11-19). The design is the existing redesign note; no new design work.

## Fixed target, acceptance tests, out of scope
See `research/2026-11-19-cds-gate-redesign.md` (the spec) and its three slice briefs, which carry the acceptance
commands, scope and non-goals: `briefs/mac/cds-redesign-1.md` (loopback-only CDS, gateway limits),
`briefs/mac/cds-redesign-2.md` (installer owns the nginx config), `briefs/mac/cds-redesign-3.md` (outside probe).
Out of scope: the side-effect-free probe design (IDEAS #200, T-SEC-2).

## Acceptance tests
Mac (nginx tests deselected; no nginx on the Mac):
```
python3.12 -m pytest -p no:cacheprovider contrib/deepsignal/test/security contrib/deepsignal/console/install contrib/deepsignal/test/console/test_install.py test/server/test_cached_data_server_host.py -q -k "not real_197"
python3.12 -m flake8 --config .flake8 contrib/deepsignal
```
Linux runner with nginx (desk branch `ci/sec-joint-nginx`): `test_real_197_*` must pass.

## Prerequisites on trunk
Console UI on `deepsignal/integration` 7c60dbf (D-PILOT1); the unit branch carries #197 (eadb0a2) itself.

## Who judges
Review in Codex cloud (non-math, D-WIP3) against this note and D-P1DEF1; the nginx probe on the desk Linux runner
(`ci/sec-joint-nginx`); merge only with Eugene's mark (critical).
