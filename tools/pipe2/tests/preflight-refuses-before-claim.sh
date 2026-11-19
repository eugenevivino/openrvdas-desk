#!/bin/bash
# A build job whose brief lacks a needs block, or whose needs are unmet, is refused (exit 8) and leaves no claim.
set -u; D=/private/tmp/deepsignal; T=$(mktemp -d $D/cds-redesign-pftest.XXXX); before=$(ls $D/claims | wc -l | tr -d ' ')
printf '# brief without needs\n' > $T/p.md
out=$(DS_POLL=1 $D/ds-launch-when-ok.sh $T $T/p.md $T/r.log 1 -- -m gpt-6.2-sol - 2>&1); rc=$?
after=$(ls $D/claims | wc -l | tr -d ' ')
[ $rc = 8 ] && [ "$before" = "$after" ] && echo "PASS refused with exit 8 before any claim: $out" || { echo "FAIL rc=$rc claims $before->$after: $out"; exit 1; }
printf -- '---\nneeds:\n  tools: nosuchtool-zz\n---\n' > $T/q.md
out=$(DS_POLL=1 $D/ds-launch-when-ok.sh $T $T/q.md $T/r.log 1 -- -m gpt-6.2-sol - 2>&1); rc=$?
[ $rc = 8 ] && echo "PASS unmet need refused: $out" || { echo "FAIL unmet need rc=$rc: $out"; exit 1; }
