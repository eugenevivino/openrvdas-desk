# Launch-path race audit (D-PIPE2 rule 8, 2026-11-19)

Finding 1: `heartbeat.sh` had no single-instance guard; a second copy would double-start `autopilot.sh`.
Fix: it exits if the pid in `.heartbeat.pid` is a live heartbeat. Tested (second copy exits).

Finding 2: `autopilot.sh` had no single-instance guard. It runs `accept.sh` (acceptance only, no Codex), so a second
copy could accept the same cloud task twice. Fix: it exits if another autopilot is running. Tested.

Finding 3: two chain scripts for one unit ran at once on 2026-11-19 (`cds-redesign.sh` and `cds-redesign2.sh`). Claims
stop the same job (same workdir and prompt) launching twice, but not two different jobs for one unit. Fix: one chain
per unit; replacing a chain means stopping its parent first (done tonight), and mac-build now pins the branch head, so
a second writer's job refuses to launch or push once the head moves.

Finding 4: the keepalive does not launch jobs; only `ds-launch-when-ok.sh` launches Codex (claims, caps, preflight,
design check, routing). `hourly-sync.sh` pushes, it does not launch; its push risk is pitfall 1 in the handover.
