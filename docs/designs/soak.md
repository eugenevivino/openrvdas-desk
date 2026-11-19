# Design note: soak (D-DESIGN1)

- Unit: `soak` on fork branch `deepsignal/integration` at `7c60dbf`. Launcher unit: `soak`.
- Author: Astra, 2026-11-18. Status: DRAFT.

## Fixed target

The console pilot candidate at `7c60dbf` sustains 24 real hours on the Mini when Kalon is idle, with the MacBook as fallback under the memory gate. Both Macs observe the heavy-job gate. D-SOAK1 assigns the same head a 5.5 h run in the desk Linux Actions job. Three persistent WebSocket clients and one client reconnecting every 10 min each request all fields with 300 s of history, then consume live records.

Sample every 60 s with a 30 min warm-up. A completed run passes when all of the following hold:

- Zero crashes. The cache, logger manager and all four loggers survive. Every post-warm-up sample contains positive RSS for all six processes, with zero unmeasured loggers. Each process’s last 10-sample median RSS is at most 5% above its first 10-sample median after warm-up.
- Every client’s median interval maximum receive lag is at most 5 s. Lag is receipt time minus record timestamp. The median uses intervals with new records.
- Post-warm-up samples exist, with zero empty intervals for each client, including the reconnecting client. `soak.py` can return `PASS` despite individual empty intervals because it tests median record rate. Acceptance therefore also requires the sample check below.

## Acceptance tests (commands)

From the candidate checkout root, check verdict behavior and lint:

```sh
python3 -m pytest contrib/deepsignal/test/harness/test_soak.py -v
flake8 contrib/deepsignal/test/harness/soak.py contrib/deepsignal/test/harness/test_soak.py
```

On the selected Mac, start the run, inspect liveness and elapsed time with `ps` as needed, then collect its exit status in the same shell:

```sh
python3 -m contrib.deepsignal.test.harness.soak --hours 24 --warmup-min 30 --sample-s 60 --clients 3 --report soak.json &
soak_pid=$!
ps -p "$soak_pid" -o pid=,etime=,command=
wait "$soak_pid"
```

In the desk Linux job, run:

```sh
python3 -m contrib.deepsignal.test.harness.soak --hours 5.5 --warmup-min 30 --sample-s 60 --clients 3 --report soak.json
```

On either host, read the completed report and check every expected client. The command prints the runner verdict and reasons, counts empty client intervals, and exits nonzero on either failure. Runner exit codes are 0 for `PASS`, 1 for `FAIL` and 2 for `COULD_NOT_RUN`. A crash or missing report leaves the run without a pass.

```sh
python3 -c 'import json,sys; r=json.load(open("soak.json")); samples=[s for s in r["samples"] if s["after_warmup"]]; clients=("client-1","client-2","client-3","reconnecting-client"); empty=sum(s["clients"].get(c,{}).get("messages_per_s",0)<=0 for s in samples for c in clients); print(r["verdict"],r["reasons"],"empty client intervals:",empty); sys.exit(r["verdict"]!="PASS" or not samples or empty!=0)'
```

## Out of scope

Deliberate source loss and recovery belong to D-RECOVER1. Restarting a killed logger is an operator action, or a production `supervisord` action. Automatic restart is outside MVP acceptance. An unplanned logger death still fails the soak. Other out-of-scope findings become tickets unless they meet D-P1DEF1(a), (b) or (c).

## Prerequisites on trunk

Verified by inspection in this checkout: `fixture.py` starts the replay cache and manager and discovers PIDs for `mwx1`, `s330`, `knud1` and `true_winds`. `soak.py`, `test_soak.py` and `SOAK.md` are present. This design review did not execute a soak.

## Who judges

The desk Linux job is the gate of record. A Mac-only failure is recorded against the 24 h run and does not block that gate under D-SOAK1. Review takes place in Codex cloud. The soak reviewer model, review effort and merge owner are not specified in the sources.