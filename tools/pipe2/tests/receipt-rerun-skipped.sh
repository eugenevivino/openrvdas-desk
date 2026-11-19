#!/bin/bash
# mac-build --rerun-skipped keeps passed commands and reruns only failed ones (no Codex job, no push to GitHub).
set -u; D=/private/tmp/deepsignal; T=$(mktemp -d $D/p2-rrtest.XXXX); s=rrtest-$$
mkdir -p $T/repo && git -C $T/repo init -q && git -C $T/repo -c user.email=t@t -c user.name=t commit -q --allow-empty -m init
printf '# t\n\n## Acceptance (exact commands, from repo root)\n```\npython3 -c "print(1)"\n```\n```\npython3 -c "import os,sys; sys.exit(0 if os.path.exists(\x27ok.flag\x27) else 1)"\n```\n' > $T/brief.md
MB_DIR=$T MB_BRANCH=deepsignal/zz-$s $D/mac-build.sh $s x y --rerun-skipped > /dev/null 2>&1
grep -c '^failed' $D/receipts/job-$s.tsv | grep -q '^1$' || { echo "FAIL first run did not record one failure"; exit 1; }
touch $T/repo/ok.flag; MB_DIR=$T MB_BRANCH=deepsignal/zz-$s $D/mac-build.sh $s x y --rerun-skipped > /dev/null 2>&1
n=$(grep -c '^passed' $D/receipts/job-$s.tsv | tr -d ' '); kept=$(grep -c "kept passed\] python3 -c \"print(1)\"" $D/mac-builds.log | tr -d ' ')
[ "$n" = 2 ] && [ "$kept" -ge 1 ] && echo "PASS rerun kept the passed command and reran only the failed one" || { echo "FAIL passed=$n kept=$kept"; exit 1; }
