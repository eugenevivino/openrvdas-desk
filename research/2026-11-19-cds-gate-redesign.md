# CDS gate redesign: own the config, test from outside (2026-11-19)

For Eugene. No code changes, no merges. Context: `deepsignal/sec-cds-joint` 82c8f3d closed every round-1 bypass, but the final review found 10 new P1s (desk `research/2026-11-19-sec-cds-joint-review-r2.md`). Each round finds more because the checker tries to prove that an arbitrary operator nginx config is safe by parsing it: includes, sibling hosts, stream upstreams, variables, SRV records, default vhosts. That problem has no end. More review rounds will not converge.

## Recommendation: three structural changes
1. **The installer owns the nginx config.** It renders one fixed template (console static files plus one `/cds-ws` location to the relay, with an explicit allowed-origin list, not a comparison with `Host`). It refuses to install next to unknown vhosts, includes or `stream` blocks that reference CDS ports (it lists them and stops; the operator resolves them). It always reloads nginx and confirms the reload.
2. **CDS binds loopback only. The read-filtered relay on 8767 is the only way in.** This is the #197 core change (`--host` and `--udp_interface`): TCP 8766 on 127.0.0.1, UDP on the named instrument interface only. The gateway listens on loopback (or a Unix socket) and only nginx reaches it.
3. **The check becomes a small runtime black-box test, not static parsing.** From a second address on the ship LAN (or the host's LAN IP), it checks four things:
   - 8766 is refused, and every configured CDS UDP port is unreachable;
   - a foreign Origin on `/cds-ws` gets 403;
   - a subscribe through `/cds-ws` returns a fresh value written for this run;
   - a publish through `/cds-ws` is refused and the cache is unchanged.

   The same test runs at install, in Self-test, and in the Linux CI gate.

## The 10 open findings under this design
| # | Finding | Outcome |
|---|---|---|
| 1 | 503 fallback skips TCP and UDP listener checks | Moot: loopback bind (2) plus the outside probe (3) check listeners on every path |
| 2 | Origin enforced only on recognized `/cds-ws` routes; a second 8767 route or the gateway listener is unchecked | Moot: the installer owns the only route (1); the gateway is loopback-only (2); the outside probe tests Origin (3) |
| 3 | Origin compared with `Host`; a default vhost satisfies it | Moot: the template uses an explicit allowed-origin list (1) |
| 4 | Only the last `--udp-port` kept | Mostly moot: UDP binds the instrument interface (2). Remains: the probe must read every UDP port from the CDS supervisor config |
| 5 | SRV upstream ports unchecked (inferred) | Moot: no operator upstreams in the owned template (1) |
| 6 | Idempotent install skips reload | Moot: the installer always reloads (1) |
| 7 | Subscribe probe trusts a stale field | Remains: the probe writes and reads a fresh nonce through a test-only loopback path. Tie this to IDEAS #200 (side-effect-free probe) |
| 8 | Gateway buffers the whole message before its 64 KiB check | Remains: gateway code fix (`max_size=65536` on the server) |
| 9 | Wildcard subscriptions bypass the 200-field cap | Remains: the gateway expands or refuses wildcards before counting |
| 10 | Source check passes against a stale `dist` (inferred) | Moot: drop source parsing; the outside probe loads the served bundle (3) |

Net result: 6 moot, 1 mostly moot, 3 remain (7, 8, 9). All 3 remaining items are small and local (the probe nonce and two gateway limits), not open-ended parsing.

## Cost and order
- One build job on `deepsignal/sec-cds-joint`: template plus installer refusal plus always-reload, the outside probe, and the two gateway limits. Then one Astra ultra review and the Linux nginx runner. This replaces `check_cds.py` static parsing; keep only a tiny guard that the rendered file matches the template.
- Requires: the #197 core bind change stays in the unit (critical, your merge mark). Operators with custom vhosts lose automatic install and get a clear refusal list. That is the tradeoff.
- Decision for you: adopt this redesign for #197 and the console install, or keep iterating on the parser. I recommend the redesign.
