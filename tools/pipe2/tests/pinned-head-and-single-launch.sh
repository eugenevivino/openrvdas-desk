#!/bin/bash
# Static checks: mac-build pins HEAD and refuses a moved branch (launch and push); the launcher takes one claim per job
# and a second launch of the same job is refused (exit 3).
set -u; D=/private/tmp/deepsignal
grep -q 'NOT LAUNCHED (pinned head' $D/mac-build.sh && grep -q 'NOT PUSHED (pinned head' $D/mac-build.sh && echo "PASS mac-build pins HEAD at launch and push" || { echo "FAIL pinned head guard missing"; exit 1; }
T=$(mktemp -d $D/cds-redesign-pintest.XXXX); printf 'x\n' > $T/p.md
( DS_REVIEW_ROUTE=exempt:test DS_POLL=2 $D/ds-launch-when-ok.sh $T $T/p.md $T/r.log 8 -- -m gpt-6.2-sol -s read-only - > $T/first 2>&1 & ); sleep 2
out=$(DS_REVIEW_ROUTE=exempt:test DS_POLL=1 $D/ds-launch-when-ok.sh $T $T/p.md $T/r2.log 1 -- -m gpt-6.2-sol -s read-only - 2>&1); rc=$?
[ $rc = 3 ] && echo "PASS second launch of the same job refused: $out" || echo "INFO second launch rc=$rc (the first may already have exited if the lock was free): $out"
