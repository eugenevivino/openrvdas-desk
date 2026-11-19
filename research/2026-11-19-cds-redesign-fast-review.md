# CDS gate redesign: fast review of the whole unit (D-FASTREV1), 2026-11-19

Head 814353a (slices 1 to 3 plus fix round 1), base 0fd4dee. Verdict: PASS. Linux nginx run 44452842829: both runtime probe tests passed (Django and React).

```
unit sec-cds-joint head 814353a base 0fd4dee
queue/setup 5s
logic 128s
install-security 189s
first pass wall 189s
escalation wall 0s
merge 0s
total 194s
self-check 222s
```

## Part: logic

## Blocking P1s

None.

## Tickets

TICKET: contrib/deepsignal/docs/security-cds.md:43 says each run publishes a nonce, but the documented `--site-only` run below it performs only a byte comparison and does not publish.

SCAN: not run (bandit and pip-audit are not installed)
ESCALATE: no
Verdict: PASS

## Part: install-security

## Blocking P1s

None.

## TICKETS

TICKET: contrib/deepsignal/security/cds_gateway.py:99 accumulates every prior subscription when enforcing MAX_FIELDS even though the CDS replaces a subscription, so a valid client that rotates through more than 200 distinct fields is disconnected.
TICKET: contrib/deepsignal/security/cds_gateway.py:90 forwards structurally invalid but allowed CDS requests such as a subscribe field with a null specification, letting an unauthenticated LAN client trigger an exception in the upstream CDS connection instead of receiving a refusal.
TICKET: contrib/deepsignal/console/install/install_site.py:96 busy-spins without a sleep while waiting up to five seconds for a worker generation, unnecessarily consuming a CPU during every nginx reload.
SCAN: not run (bandit and pip-audit are not installed)
ESCALATE: no
Verdict: PASS
