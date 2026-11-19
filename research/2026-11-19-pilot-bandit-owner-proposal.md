# Pilot Bandit findings for the security and installer owner

The full scan of fork integration `1dc7a5e` and console candidate `8652862` produced 190 findings on each. The two security files account for five findings, four low and one medium. The other 185 are in the installer and its tests. This is a proposal for the owner. The four existing redesign tickets and critical merge have separate ownership.

| Location at the pinned base | What Bandit identified | Owner proposal |
|---|---|---|
| `security/check_cds.py:80`, B104, medium | The checker compares a reported listener address against wildcard representations. This expression rejects wildcards. It opens no listener. | Keep the rejection. Where addresses are numeric, use the standard IP parser's unspecified-address property. Preserve the existing semantics for the literal star and named interfaces. Exercise the checker's public UDP check with a valid named interface, wildcard IPv4 and wildcard IPv6. Verify that the existing IPv4 and IPv6 loopback TCP checks still pass. |
| `security/check_cds.py:9`, B404, low | The checker imports subprocess. Its runner calls the Linux listener-reporting utility with a fixed argument list. The utility name is resolved by the caller's environment. | Keep the injectable runner. Resolve the utility from a short list of deployment-verified absolute system locations. Bound execution time, check exit status before consuming output, and fail the check when the tool is missing, times out or fails. Preserve the configured-port versus no-feed distinction. |
| `security/probe_cds.py:18,37`, B404, B607 and B603, low | A fixed argument list requests the managed CDS PID from Supervisor. It already has a timeout, checks for nonzero exit, and avoids shell interpretation. The executable name is relative. | Verify the packaged Supervisor path on supported pilot images, including RHEL. Invoke an administrator-controlled executable by absolute path. If an approved venv layout is necessary, use an explicit trusted deployment setting and fail closed if unavailable. Preserve PID validation and the whitelist of environment keys. |

B404 and B603 can remain even after an appropriate subprocess call uses a verified absolute path. An import warning does not establish shell injection. The owner should document residual diagnostics and choose a supported API or submit a narrow policy decision through the gate owner. A broad exclusion, severity change or removal of the listener check would lose evidence. For a no-subprocess design, first validate that a replacement can inspect both IP families and every listener in the same namespace, and that the Supervisor API provides the same live-process identity under the existing deployment permissions. Do not assume that substituting service configuration for the running process is equivalent.

## Owner verification

Add D-FIX1 cases before changing the implementation. Exercise the checker with a successful IPv4 binding and a valid IPv6 variation, then the wildcard and failed-tool cases. Exercise the real PID lookup path with a controlled runner or fixture and two valid deployment layouts. Verify that unavailable tools, invalid PIDs and timeouts fail closed and that the actual supervisor-controlled configuration still works on the pilot Linux image. Submit checks via the desk launcher. Its acceptance commands should include the following, and the existing Linux runtime gate.

```sh
python3 -m pytest -q contrib/deepsignal/test/security/test_check_cds.py
python3 -m pytest -q contrib/deepsignal/test/security/test_probe_cds.py
python3 -m pytest -q contrib/deepsignal/test/security
```

## Remaining installer findings

Of the 185 findings outside these two files, five are in `console/install/install_site.py` and 180 in `console/install/test_nginx_site.py` and `test_owned_site.py`. Of those 180, 175 are pytest assertions. Preserve the test assertions and the live nginx coverage. Review each executable invocation and the deliberate wildcard fixture in their own contexts. Any scanner policy governing test-only assertions belongs to the gate owner. Re-run the full scanner on the resulting integrated revision, retain the raw output and record any outstanding findings before pilot release review.

Evidence for this handoff is in `/private/tmp/deepsignal/console-pilot-qualification/{base.json,candidate.json,comparison.txt}`. File paths in the table are relative to `contrib/deepsignal/`.
