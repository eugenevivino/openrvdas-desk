#!/bin/bash
# D-PIPE2 rule 9: never merge a trunk (main, dev, master, deepsignal/integration) INTO a unit branch.
# Usage: trunk-merge-check.sh <repo> <local-sha> <remote-ref> [remote-name]   exit 0 ok, 1 refused.
# Pushing TO a trunk is allowed (that is how units land). For any other ref, every new merge commit whose second or
# later parent is a trunk tip, or an ancestor of one, is refused. Remedy: re-cut the unit branch onto the trunk tip.
set -u
R=$1; L=$2; REF=$3; RM=${4:-origin}
case "$REF" in refs/heads/main|refs/heads/dev|refs/heads/master|refs/heads/deepsignal/integration) exit 0;; esac
[ "$L" = 0000000000000000000000000000000000000000 ] && exit 0
tips=$(git -C "$R" ls-remote "$RM" refs/heads/main refs/heads/dev refs/heads/master refs/heads/deepsignal/integration 2>/dev/null | cut -f1)
[ -n "$tips" ] || exit 0
for m in $(git -C "$R" rev-list --merges "$L" --not --remotes="$RM" 2>/dev/null); do
  for p in $(git -C "$R" rev-list --parents -n 1 "$m" | cut -d' ' -f3-); do
    for t in $tips; do
      if [ "$p" = "$t" ] || git -C "$R" merge-base --is-ancestor "$p" "$t" 2>/dev/null; then
        echo "REFUSED (D-PIPE2): merge commit ${m:0:7} merges trunk history (${p:0:7}) into $REF. Do not merge main, dev or integration into a unit branch; re-cut the unit branch onto the trunk tip instead." >&2; exit 1
      fi
    done
  done
done
exit 0
