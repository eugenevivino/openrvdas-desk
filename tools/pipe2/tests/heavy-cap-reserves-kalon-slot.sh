#!/bin/bash
# With 2 heavy jobs already running machine-wide (any project), DeepSignal must not take the third slot (reserved
# for Kalon): ds-codex refuses with exit 12 before the lock. Uses a ps stand-in; the counter stays read-only.
set -u; D=/private/tmp/deepsignal; T=$(mktemp -d $D/cds-redesign-captest.XXXX)
printf '#!/bin/sh\ncase "$*" in *pid=*) printf "1 /x/bin/codex exec a\\n2 /x/bin/codex exec b\\n";; *) printf "/x/bin/codex exec a\\n/x/bin/codex exec b\\n";; esac\n' > $T/ps; chmod +x $T/ps
n=$(DS_HEAVY_PS=$T/ps $D/heavy-jobs.sh); [ "$n" = 2 ] || { echo "FAIL count $n"; exit 1; }
out=$(cd $T && DS_HEAVY_PS=$T/ps ~/bin/ds-codex -m gpt-6.2-sol - < /dev/null 2>&1); rc=$?
[ $rc = 12 ] && echo "PASS ds-codex refuses the third slot (exit 12): $out" || { echo "FAIL rc=$rc: $out"; exit 1; }
printf '#!/bin/sh\ncase "$*" in *pid=*) printf "1 /x/bin/codex exec a\\n";; *) printf "/x/bin/codex exec a\\n";; esac\n' > $T/ps1; chmod +x $T/ps1
out=$(cd $T && DS_HEAVY_PS=$T/ps1 ~/bin/ds-codex --dry-run -m gpt-6.2-sol - < /dev/null 2>&1 | grep 'heavy jobs'); echo "$out" | grep -q '1 of cap 2' && echo "PASS one running job leaves room: $out" || { echo "FAIL: $out"; exit 1; }
