# Pilot Bandit remediation

Implementation owner: Codex. Security and installer review: owner of the critical merge. Fork branch: `deepsignal/pilot-bandit-remediation`. Base: `deepsignal/integration` at `1dc7a5e`. Design approved for implementation on 2026-11-19.

## Fixed target

Deliver a reviewable patch for the 190 inherited findings in the five files listed in the [owner proposal](../../research/2026-11-19-pilot-bandit-owner-proposal.md). Preserve listener detection, Supervisor PID verification, installer checks, and the existing live nginx tests. Keep the console candidate separate. Release acceptance requires the installed full-tree Bandit command to exit zero, with every residual diagnostic explicitly accounted for.

Harden executable selection on the real checker, probe and installer paths. Keep fixed argument lists, trusted executable locations, bounded execution, status validation and fail-closed behavior. Verify supported installation paths before pinning them. Preserve IPv4, IPv6 and named-interface behavior. The B104 in the checker is a wildcard rejection; the B104 in the nginx fixture is an actual bind. Evaluate each according to its function.

Keep all 175 pytest assertions and their collection. If hardening leaves a generic subprocess diagnostic, an intentional fixture diagnostic or the assertion diagnostics, deliver the hardening patch and a separate, exact proposed disposition for owner review. Record each affected rule and location and its rationale. Any change to scanner policy needs a distinct owner decision. Retain the raw diagnostic report and the red release status until the installed gate actually passes.

## Acceptance tests

Run from the pinned fork checkout through the desk launcher. For each behavior fix, first demonstrate the regression and one valid variation on the baseline, then both passing on the patch. Cover a valid supported alternate executable layout, unavailable tools and failed exit status, valid named bindings, and both IP families. Record collected test IDs before and after and retain the exact-head receipts.

```sh
/private/tmp/deepsignal/venv-scan/bin/python -m bandit -q -r contrib/deepsignal -x '*/test/*,*/node_modules/*'
python3.12 -m pytest -p no:cacheprovider -q contrib/deepsignal/test/security contrib/deepsignal/console/install contrib/deepsignal/test/console/test_install.py test/server/test_cached_data_server_host.py -k 'not real_197'
python3.12 -m flake8 --config .flake8 contrib/deepsignal
```

On the desk Linux runner with nginx, run both deployed site variants and retain the job URL:

```sh
python3 -m pytest -p no:cacheprovider -v contrib/deepsignal/console/install/test_nginx_site.py -k real_197
```

## Prerequisites and limits

Fetch integration and confirm the branch pin and claims before launch. Use the DeepSignal scan venv and an isolated Linux fixture. The four existing security tickets, ship deployment, the soak, gate waivers and critical merge are outside this implementation. Submit the patch to the security owner. After an approved change lands, re-cut and qualify the pilot console on the resulting integration SHA.
