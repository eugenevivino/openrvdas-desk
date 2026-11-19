# Brief: joint #197 CDS lockdown plus console installer gate, round 2 (final; CRITICAL, security)

- Branch `deepsignal/sec-cds-joint` at f38b52e (the checked-out branch). Round 1 review: desk `research/2026-11-19-sec-cds-joint-review.md` (HOLD, 5 verified P1 bypasses). Round 1 brief: `briefs/mac/sec-cds-joint.md`; its rules hold. Lane: Mac, `gpt-6.2-sol` high. Push-only, never auto-merged; Eugene decides.
- The live nginx test `test_real_197_gate_through_django_and_react_nginx` passed on a Linux runner at f38b52e. The Mac has no nginx, so the Mac acceptance below deselects it; the lead reruns it on a Linux runner at the fix head. It must keep passing.

## Close each of these with code plus a regression test that fails at f38b52e (verbatim from the review)
- **P1 blocking, VERIFIED by inspection.** A valid `/cds-ws` relay can pass while another route exposes port 8766. The checker leaves nginx includes unread, and the installer passes it only the selected virtual host. A direct route in an included file or a sibling host survives installation. [check_cds.py](/private/tmp/deepsignal/sec-joint-rr/contrib/deepsignal/security/check_cds.py:138) · [nginx-site.awk](/private/tmp/deepsignal/sec-joint-rr/contrib/deepsignal/console/install/nginx-site.awk:175)
- **P1 blocking, VERIFIED by inspection.** The installer tracks named upstreams inside `http` but misses them inside `stream`. A UDP listener on a different public port can forward through a named upstream to the configured CDS UDP bind, even when the operator supplies both UDP flags. [nginx-site.awk](/private/tmp/deepsignal/sec-joint-rr/contrib/deepsignal/console/install/nginx-site.awk:51)
- **P1 blocking, VERIFIED by inspection.** When `/cds-ws` is absent, the installer treats a variable-based proxy destination as safe and skips the real checker. It can write the fallback 503 while another location still resolves to publish-capable CDS. [nginx-site.awk](/private/tmp/deepsignal/sec-joint-rr/contrib/deepsignal/console/install/nginx-site.awk:35) · [install.sh](/private/tmp/deepsignal/sec-joint-rr/contrib/deepsignal/console/install/install.sh:197)
- **P1 blocking, VERIFIED by inspection.** The gate accepts a relay without an Origin guard. Its live probe sends only the expected Origin, so a relay that also allows foreign browser origins to subscribe can pass. [check_cds.py](/private/tmp/deepsignal/sec-joint-rr/contrib/deepsignal/security/check_cds.py:127) · [install.sh](/private/tmp/deepsignal/sec-joint-rr/contrib/deepsignal/console/install/install.sh:182)
- **P1 blocking, VERIFIED by inspection.** The source check stops partway through the `config` initializer. It reports that the console uses the same-origin URL even if `loadConsole` later reassigns `config.websocket` before returning it. [check_cds.py](/private/tmp/deepsignal/sec-joint-rr/contrib/deepsignal/security/check_cds.py:181)

## Also fix (ticket from the review, verbatim)
- **Ticket, VERIFIED.** The UDP regression combines HTTP `server` and `stream` blocks at the same level, which real nginx cannot load. The Django direct-8766 case already rejects at `edec001`, and the React template is absent there. [test_nginx_site.py](/private/tmp/deepsignal/sec-joint-rr/contrib/deepsignal/console/install/test_nginx_site.py:127)
Make the UDP regression use a configuration real nginx would load (http `server` blocks inside `http`, `stream` blocks at top level), and keep the case it was meant to cover.

## Required behavior
- The checker evaluates the whole effective nginx configuration the installer will load: follow `include` directives (relative to the nginx prefix), and every `server` block in `http` and every block in `stream`, not only the selected virtual host. Any route anywhere that reaches publish-capable CDS (TCP 8766 or the configured CDS UDP bind), directly or through a named upstream (in `http` or `stream`) or a variable target, is unsafe.
- A proxy target the checker cannot resolve statically (variables) is unsafe unless it is the allowed relay itself; never skip the checker.
- The allowed `/cds-ws` relay must require an Origin guard that admits only the console's own origin; the live probe also sends a foreign Origin and requires refusal.
- The console source check parses the whole `config` construction in `src/pages.ts` (including later reassignments of `config.websocket` before return) and fails closed if it cannot prove same-origin `/cds-ws`.
- Fail closed on anything unparseable. Do not weaken any existing fail-closed path.

## Acceptance (exact commands, from repo root)
```
python3.12 -m pytest -p no:cacheprovider contrib/deepsignal/test/security contrib/deepsignal/console/install contrib/deepsignal/test/console/test_install.py test/server/test_cached_data_server_host.py -v -k "not real_197"
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal
```

## Scope
Only `contrib/deepsignal/security/**`, `contrib/deepsignal/test/security/**`, `contrib/deepsignal/docs/security-cds.md`, `contrib/deepsignal/console/install/**`, `contrib/deepsignal/test/console/test_install.py`, `contrib/deepsignal/console/docs/install.md`. No core or console UI changes. The side-effect-free probe is IDEAS #200, not this round.

## Non-goals and banned
No new features, no deleted, skipped or loosened tests, no sleeps, no new dependencies, no sub-agents.

## Stop rule
Report any finding that needs a change to the #197 or console design instead of changing it.
