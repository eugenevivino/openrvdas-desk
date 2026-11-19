# Design note: 24-hour Console UI soak

Status: DRAFT, Eugene approval required. Launcher unit: `soak`. Decision: D-SOAK1.

## Fixed target

Qualify the Nov 25 supervised pilot on fork integration `1dc7a5e001f9535520ac8986922253c2ea20e01e`. Run 24 real hours on the Mini when idle, with the MacBook as fallback after normal admission. Run 5.5 hours on the same SHA in the desk Linux job. The harness starts a loopback replay fixture. Three persistent clients and one client that reconnects every ten minutes request all fixture fields with 300 seconds of history, then receive live records.

Sample every 60 seconds after starting, with a 30-minute warm-up. Require all six fixture processes (cache, manager and four loggers) to stay alive and measured. Each process's median RSS for its final ten post-warm-up samples must stay within 5% of its initial ten. Each client's median interval maximum receive lag must be at most five seconds. Every post-warm-up client interval must contain new records, including for the reconnecting client.

## Acceptance tests

Run from the root of the exact candidate checkout using the existing fixture environment. Run only the duration command for the selected host, in fresh scratch. Keep exit status and report with the candidate SHA and host.

```sh
test "$(git rev-parse HEAD)" = 1dc7a5e001f9535520ac8986922253c2ea20e01e
python3 -m pytest -v contrib/deepsignal/test/harness/test_soak.py
python3 -m flake8 contrib/deepsignal/test/harness/soak.py contrib/deepsignal/test/harness/test_soak.py
```

Mac:

```sh
test ! -e soak-mac.json && python3 -m contrib.deepsignal.test.harness.soak --hours 24 --warmup-min 30 --sample-s 60 --clients 3 --report soak-mac.json
```

Desk Linux:

```sh
test ! -e soak-linux.json && python3 -m contrib.deepsignal.test.harness.soak --hours 5.5 --warmup-min 30 --sample-s 60 --clients 3 --report soak-linux.json
```

Each host must record exit 0 and pass this independent check from the checkout root. The runner's median-rate verdict alone can miss individual empty intervals.

```sh
python3 -c 'import json,sys; from pathlib import Path; p,=Path(".").glob("soak-*.json"); r=json.loads(p.read_text()); s=[x for x in r["samples"] if x["after_warmup"]]; clients=("client-1","client-2","client-3","reconnecting-client"); empty=sum(x["clients"].get(c,{}).get("messages_per_s",0)<=0 for x in s for c in clients); print(p,r["verdict"],r["reasons"],"samples",len(s),"empty intervals",empty); sys.exit(r["verdict"]!="PASS" or len(s)<10 or empty!=0)'
```

## Out of scope

Deliberate source-loss drills, automatic logger restart, bridge cutover and changes to the security redesign or its tickets. An unplanned fixture-process death fails the soak.

## Prerequisites and gate

The fork merge was fetched and `814353a` is in the pinned tip's ancestry. The tip contains `fixture.py`, `soak.py`, `test_soak.py` and `SOAK.md`. Before launch, verify the SHA and claim again, confirm host admission, isolated fixture ports and processes, existing dependencies and a desk Linux job pinned to the same SHA. Obtain a new Linux run ID and retain both hosts' reports. Linux is the gate of record under D-SOAK1. Record a Mac-only failure separately. Stop for a new pin if integration changes before launch.
