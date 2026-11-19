# Pilot Bandit policy proposal

**Owner decision pending. Active gate RED.** Bandit 1.9.4 exited 1 on hardening head
`8f0794ea62f935c9859ac8bc4c918dd6bfcd0a74`. The raw report has 188 findings
(187 low, one medium). This draft proposes an exact disposition for those
findings. The installed gate and release qualification still require owner action.

## Proposed dispositions

The manifest records each site's file, Bandit rule, severity, confidence, line,
and start and end columns as reported. These notes correspond to every rationale
identifier in [the manifest](bandit-policy.json). Paths below are relative to
`contrib/deepsignal/`.

| Rationale | Site | Why retain the reviewed source |
| --- | --- | --- |
| `installer-import` | `console/install/install_site.py:12` B404 | The installer imports subprocess for the four bounded commands below. |
| `installer-command` | `install_site.py:32` B603 | Callers pass structured argv for absolute systemctl and ps paths or the verified nginx executable. The wrapper requires a successful status and sets a 15-second timeout. |
| `installer-nginx-inspection` | `install_site.py:46` B603 | nginx configuration inspection uses verified service argv or the fixed preview executable paths. Status and conflicting-server diagnostics are checked before stdout is used. Timeout is 15 seconds. |
| `installer-listener-check` | `install_site.py:151` B603 | The release checker uses the installer interpreter with `-I -B`, explicit argv, checked status and a 45-second timeout. |
| `installer-release-probe` | `install_site.py:163` B603 | The release probe uses the installer interpreter with `-I -B`, explicit argv, checked status and a timeout based on configured ports and origins. |
| `listener-check-import` | `security/check_cds.py:11` B404 | The checker uses subprocess for fixed `ss -ltn` and `ss -lun` queries. It resolves the executable from fixed system directories and parses the output after a successful bounded run. |
| `supervisor-probe-import` | `security/probe_cds.py:19` B404 | The probe imports subprocess for the Supervisor PID query and its error handling. |
| `supervisor-pid-query` | `security/probe_cds.py:42` B603 | The probe uses supervisorctl from fixed system and administrator-local directories. The fixed query runs with cwd `/`, checked status and a 3-second timeout. The code validates the returned PID and reads only the two allowed CDS variables. |
| `nginx-fixture-import` | `console/install/test_nginx_site.py:10` B404 | The import supports the isolated Linux nginx fixture. |
| `nginx-fixture-launch` | `test_nginx_site.py:279` B603 | The fixture starts CI-installed nginx with a temporary prefix, config and inherited fixture socket. Teardown terminates and waits for the process. |
| `nginx-ci-wildcard-bind` | `test_nginx_site.py:331` B104 | This is an intentional IPv4 wildcard bind on an ephemeral port in isolated Linux CI. Its two cases exercise LAN-address and loopback access through fixture nginx. Review approval applies only to this fixture use. |
| `owned-site-fixture-import` | `console/install/test_owned_site.py:7` B404 | The import supports invoking the installer fixture below. |
| `owned-site-fixture-launch` | `test_owned_site.py:136` B603 | The fixture invokes `/bin/sh` with the private release copy and fixture argv, checks the returned status and sets a 60-second timeout. |
| `pytest-assertions` | 120 B101 sites in `test_nginx_site.py` and 55 in `test_owned_site.py` | These are the existing pytest test oracles. Each assertion's span is listed in the manifest, and the original remediation compared their expressions and order against the parent. Production assertions and additional test assertions still fail. |

## Evidence and checks

The manifest was reconciled against all 188 entries in the remediation
disposition and the pinned Git blobs. Its two per-file digests cover the full
source bytes and every field of the complete finding multiset. For the latter,
sort findings by their canonical JSON bytes, encode the sorted array as
ASCII JSON with keys sorted and compact separators, then hash it with SHA-256.
The helper pins the SHA-256 of the manifest itself. Every listed file present in
another candidate must still match exactly. All five must be present at the
reviewed SHA. A complete clean scan with none of these paths on another head
can pass.

The helper scans a private snapshot of the existing `contrib/deepsignal` scope,
including `.py` and `.pyw`, with the existing `test` and `node_modules`
exclusions. The snapshot inventory is checked against the report and rechecked
against the worktree before a pass. Python isolated mode and the helper's
explicit empty Bandit INI keep checkout configuration out of the scan. The
command checks for findings even at source suppression comments.

The atomic `bandit-raw-<full-sha>.json` receipt records the scanner process
status and byte-exact stdout and stderr in Base64. The separately published
`bandit-policy-<full-sha>.json` records the decision, count when available,
manifest digest and rationale. Match both receipts by their full head and run
ID, and verify the raw receipt SHA-256 against the verdict. The existing text
receipt prints the run ID for an installed scanner. A genuinely absent scanner
still reports D-SCAN1 SKIP. Treat that outcome as requiring the existing cloud
scanner review.

## Owner deployment requirements

1. Review and explicitly approve each site group and the exact desk revision.
   Confirm the Linux fixture isolation and the supported deployment executable
   paths. Use a fresh reviewer under the existing security review rules.
2. Authorize installation of `pre-review.sh`, `bandit-policy.py` and
   `bandit-policy.json` together in the trusted desk location. Keep the files,
   receipts, and Bandit 1.9.4 interpreter under gate control, outside the product
   checkout. Block candidate code from writing to them. Keep the active launcher
   paused during the change so it cannot see a partial installation.
3. Verify in scratch first. Then run the installed pre-review on the clean,
   pinned release candidate. Check the raw result and the linked policy verdict
   for that run, and complete the exact-head Linux gate, both isolated nginx
   cases and the independent release review. A future Bandit version or change
   to any approved site's source or finding requires renewed review of the policy.
