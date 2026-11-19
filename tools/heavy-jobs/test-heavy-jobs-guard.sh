#!/bin/bash
# Guard test (D-PIPE1a): the heavy-job counter never writes outside /private/tmp/deepsignal and never signals
# a process. It runs the counter under a macOS sandbox that denies every file write outside that folder (and
# /dev/null), and every signal to another process. A negative control proves the sandbox really blocks writes.
set -u
D=/private/tmp/deepsignal
PROFILE='(version 1)(allow default)(deny file-write* (require-not (require-any (subpath "/private/tmp/deepsignal") (literal "/dev/null") (literal "/dev/dtracehelper"))))(deny signal (target others))'
fail=0
# macOS sandboxes cannot exec setuid /bin/ps, so the counter reads a ps snapshot taken outside the sandbox.
snap=$D/.heavy-guard-snapshot; stub=$D/.heavy-guard-ps
ps -axo pid=,command= > "$snap"
printf '#!/bin/sh\ncase "$*" in *pid=*) cat "%s";; *) sed -E "s/^ *[0-9]+ //" "%s";; esac\n' "$snap" "$snap" > "$stub"; chmod +x "$stub"
export DS_HEAVY_PS=$stub
expect=$("$D/heavy-jobs.sh")
out=$(sandbox-exec -p "$PROFILE" "$D/heavy-jobs.sh" 2>&1); rc=$?
if [ $rc -eq 0 ] && [ "$out" = "$expect" ]; then echo "PASS counter runs inside the sandbox: $out heavy jobs"; else echo "FAIL counter under sandbox rc=$rc: $out"; fail=1; fi
out=$(sandbox-exec -p "$PROFILE" "$D/heavy-jobs.sh" --list 2>&1); rc=$?
[ $rc -eq 0 ] && [ "$(echo "$out" | grep -c .)" = "$expect" ] && echo "PASS --list runs inside the sandbox" || { echo "FAIL --list rc=$rc: $out"; fail=1; }
probe=/private/var/tmp/heavy-guard-probe.$$
if sandbox-exec -p "$PROFILE" /bin/sh -c "echo x > $probe" 2>/dev/null; then echo "FAIL negative control: the sandbox allowed a write outside the folder"; rm -f "$probe"; fail=1; else echo "PASS negative control: a write outside the folder is denied"; fi
if grep -nE '(kill|pkill|killall|open |rm |mv |cp |>>? *[^&/]|>>? */[^d])' "$D/heavy-jobs.sh" | grep -v '^[0-9]*:#' | grep -v '2>/dev/null' | grep -q .; then echo "FAIL static check: the counter contains a write, move or signal"; fail=1; else echo "PASS static check: no write, move or signal in the counter"; fi
rm -f "$snap" "$stub"
exit $fail
