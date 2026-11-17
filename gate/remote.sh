#!/usr/bin/env bash
# Run the gate on the Mac Mini from the MacBook, for one commit of the fork.
#   bash gate/remote.sh            (current HEAD of ~/openrvdas)
#   bash gate/remote.sh <branch or sha>
# The commit must already be pushed to eugenevivino/openrvdas.
# Exit codes pass through from gate.sh: 0 GREEN, 1 RED, 2 REFUSED.
set -u
ref=${1:-HEAD}
MINI=${ORV_MINI:-kalon-mini}
FORK=${ORV_FORK:-$HOME/openrvdas}

sha=$(git -C "$FORK" rev-parse --verify -q "$ref^{commit}") || { echo "REFUSED: cannot resolve '$ref' in $FORK"; exit 2; }
git -C "$FORK" fetch -q origin || echo "warning: fetch failed"
if ! git -C "$FORK" branch -r --contains "$sha" 2>/dev/null | grep -q 'origin/'; then
  echo "REFUSED: $sha is not on origin. Push the branch to eugenevivino/openrvdas first."
  exit 2
fi

echo "gate: $sha on $MINI"
ssh -o ConnectTimeout=10 -o BatchMode=yes "$MINI" \
  "git -C ~/OpenRVDAS-Work/openrvdas-desk pull -q --ff-only && bash ~/OpenRVDAS-Work/openrvdas-desk/gate/gate.sh $sha"
rc=$?
if [ "$rc" -eq 255 ]; then echo "REFUSED: could not reach $MINI over SSH"; exit 2; fi

mkdir -p "$HOME/OpenRVDAS-Work/receipts"
scp -q -r "$MINI:OpenRVDAS-Work/receipts/$sha" "$HOME/OpenRVDAS-Work/receipts/" 2>/dev/null \
  && echo "receipts copied to ~/OpenRVDAS-Work/receipts/$sha"
exit $rc
