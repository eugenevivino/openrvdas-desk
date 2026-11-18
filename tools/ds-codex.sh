#!/bin/bash
# ds-codex: DeepSignal-only Codex launcher (D-SEP, Eugene 2026-11-18: DeepSignal and Kalon/l2audio are fully separate).
# Never calls or edits ~/bin/codex-run and never touches ~/.codex. Usage, from a folder under /private/tmp/deepsignal/:
#   ds-codex [--dry-run] -m <gpt-6.2-sol|gpt-6.2-astra|gpt-6-luna> [-c model_reasoning_effort=<level>] [codex exec args...] [-]
# Exit codes: 2 bad usage, 3 Astra without KALON_ALLOW_ASTRA=1, 4 full-access/bypass/write-widening refused,
#             6 model not allowed, 7 no -m, 8 connector guard refused, 9 cwd outside scratch, 10 another DeepSignal job holds the lock.
set -u
DS_HOME="$HOME/.codex-deepsignal"
SCRATCH="/private/tmp/deepsignal"
LOCK="$SCRATCH/.ds-codex.lock"
CX="${DS_CODEX_BIN:-/opt/homebrew/bin/codex}"

# (a) Isolate the environment: our own Codex home, no Kalon or codex-run variables (KALON_ALLOW_ASTRA is the only opt-in honored).
astra_ok="${KALON_ALLOW_ASTRA:-0}"
for v in $(compgen -e); do case "$v" in KALON_*|CODEX_RUN_*|CODEX_HOME) unset "$v";; esac; done
export CODEX_HOME="$DS_HOME"
LOG="$DS_HOME/launch-log.txt"

die() { echo "ds-codex: REFUSED: $2" >&2; exit "$1"; }

# Parse our own flag and the model; copy everything else through.
dry=0; model=""; effort="default"; prev=""; args=(); cds=()
for a in "$@"; do
  if [ "$a" = "--dry-run" ]; then dry=1; prev="$a"; continue; fi
  case "$prev" in
    -m|--model) model="$a";;
    -C|--cd) cds+=("$a");;
    -c|--config)
      case "$a" in
        model=*) die 7 "set the model with -m, not -c model=";;
        model_reasoning_effort=*) effort="${a#model_reasoning_effort=}"; effort="${effort//\"/}";;
      esac;;
  esac
  case "$a" in --model=*) model="${a#--model=}";; --cd=*) cds+=("${a#--cd=}");; esac
  args+=("$a"); prev="$a"
done

# (b) Model: explicit, allow-listed, Astra only with the opt-in.
[ -n "$model" ] || die 7 "rule 2: name the model with -m (gpt-6.2-sol, gpt-6.2-astra or gpt-6-luna)"
case "$model" in gpt-6.2-sol|gpt-6.2-astra|gpt-6-luna) ;; *) die 6 "model '$model' is not allowed (gpt-6.2-sol, gpt-6.2-astra, gpt-6-luna)";; esac
if [[ "$model" == *astra* && "$astra_ok" != 1 ]]; then die 3 "$model needs KALON_ALLOW_ASTRA=1 for this one approved job"; fi

# (c) Working folder must resolve under the DeepSignal scratch root, including any -C/--cd.
in_scratch() { local r; r=$(cd "$1" 2>/dev/null && pwd -P) || return 1; case "$r/" in "$SCRATCH"/*) return 0;; esac; return 1; }
in_scratch "$PWD" || die 9 "cwd $(pwd -P) is not under $SCRATCH/"
for d in "${cds[@]+"${cds[@]}"}"; do in_scratch "$d" || die 9 "-C $d is not under $SCRATCH/"; done

# (e) Safety: no full access, no bypass, no widening of writable paths, no profiles, no connectors.
GUARD_FEATURES=(apps plugins remote_plugin plugin_sharing enable_mcp_apps codex_apps_mcp_2026_07_28 browser_use browser_use_external browser_use_full_cdp_access computer_use in_app_browser)
check_cfg() {
  local v="$1" k f g; k="${v%%=*}"; k="${k// /}"
  case "$k" in
    mcp_servers*|apps|apps.*|profile|profiles*|features) die 8 "config key '$k' is not allowed";;
    sandbox_workspace_write*|sandbox_mode|approval_policy) die 4 "config key '$k' is set by ds-codex, not the caller";;
  esac
  if [[ "$k" == features.* ]]; then
    f="${k#features.}"
    for g in "${GUARD_FEATURES[@]}"; do [ "$f" = "$g" ] && [[ "${v#*=}" != *false* ]] && die 8 "re-enabling $g is not allowed"; done
  fi
}
sandbox="workspace-write"; prev=""
for a in "${args[@]+"${args[@]}"}"; do
  case "$prev" in
    -c|--config) check_cfg "$a";;
    --enable) for g in "${GUARD_FEATURES[@]}"; do [ "$a" = "$g" ] && die 8 "--enable $g"; done;;
    -s|--sandbox) case "$a" in workspace-write|read-only) sandbox="$a";; *) die 4 "sandbox '$a' is not allowed";; esac;;
  esac
  case "$a" in
    --config=*) check_cfg "${a#--config=}";;
    -c?*) check_cfg "${a#-c}";;
    --enable=*) for g in "${GUARD_FEATURES[@]}"; do [ "${a#--enable=}" = "$g" ] && die 8 "--enable=$g"; done;;
    --sandbox=*) case "${a#--sandbox=}" in workspace-write|read-only) sandbox="${a#--sandbox=}";; *) die 4 "sandbox '${a#--sandbox=}' is not allowed";; esac;;
    -p|--profile|--profile=*|-p?*) die 8 "profiles are not allowed ($a)";;
    --add-dir|--add-dir=*) die 4 "--add-dir is not allowed";;
    --dangerously-bypass-approvals-and-sandbox|--dangerously-bypass-hook-trust|--full-auto|*danger-full-access*) die 4 "full-access or bypass flag $a";;
  esac
  prev="$a"
done

# (e) Connector guard, fail closed (logic copied from Kalon's codex-run, run against our own home).
feats=$("$CX" features list 2>/dev/null | awk '{print $1}')
for need in apps plugins; do printf '%s\n' "$feats" | grep -qx "$need" || die 8 "the installed CLI has no '$need' switch, so the connector guard cannot be applied"; done
dis=(); for f in "${GUARD_FEATURES[@]}"; do printf '%s\n' "$feats" | grep -qx "$f" && dis+=(--disable "$f"); done
mcp_names() { "$CX" "$@" mcp list --json 2>/dev/null | python3 -I -c 'import sys,json; print("\n".join(s["name"] for s in json.load(sys.stdin) if s.get("enabled")))'; }
servers=$(mcp_names "${dis[@]}") || die 8 "MCP server list unreadable (fail closed)"
off=(); while IFS= read -r n; do [ -n "$n" ] && off+=(-c "mcp_servers.$n.enabled=false"); done <<< "$servers"
still=$(mcp_names "${dis[@]}" "${off[@]+"${off[@]}"}") || die 8 "MCP server list unreadable after overrides (fail closed)"
[ -z "$still" ] || die 8 "MCP servers still enabled after overrides: $still"

sb=(); [[ " ${args[*]+"${args[*]}"} " == *" -s "* || " ${args[*]+"${args[*]}"} " == *" --sandbox "* || " ${args[*]+"${args[*]}"} " == *"--sandbox="* ]] || sb=(--sandbox workspace-write)
cmd=("$CX" exec "${dis[@]}" "${off[@]+"${off[@]}"}" -c 'approval_policy="never"' -c 'sandbox_workspace_write.writable_roots=[]' "${sb[@]+"${sb[@]}"}" "${args[@]+"${args[@]}"}")

# (d) One DeepSignal job at a time: lock dir holding the owner PID; a lock whose PID is gone is stale and removed.
lock_held() { [ -d "$LOCK" ] || return 1; local p; p=$(cat "$LOCK/pid" 2>/dev/null); [ -n "$p" ] && kill -0 "$p" 2>/dev/null && { echo "$p"; return 0; }; return 1; }
if holder=$(lock_held); then die 10 "another DeepSignal Codex job holds $LOCK (pid $holder)"; fi
[ -d "$LOCK" ] && { echo "ds-codex: removing stale lock (pid $(cat "$LOCK/pid" 2>/dev/null || echo none) is gone)" >&2; rm -rf "$LOCK"; }

# (g) Dry run: print the exact command and stop (the lock is checked but not taken).
if [ "$dry" = 1 ]; then printf 'CODEX_HOME=%q' "$CODEX_HOME"; printf ' %q' "${cmd[@]}"; printf '\n'; exit 0; fi

mkdir "$LOCK" 2>/dev/null || die 10 "another DeepSignal Codex job took $LOCK just now"
echo $$ > "$LOCK/pid"
child=""
cleanup() { rm -rf "$LOCK"; }
on_signal() { [ -n "$child" ] && kill -TERM "$child" 2>/dev/null; wait "$child" 2>/dev/null; rc=$((128 + $1)); log_line "$rc"; cleanup; exit "$rc"; }
log_line() { printf '%s\tmodel=%s\teffort=%s\tsandbox=%s\tcwd=%s\texit=%s\n' "$(date -u +%FT%TZ)" "$model" "$effort" "$sandbox" "$(pwd -P)" "$1" >> "$LOG"; }
trap 'on_signal 14' ALRM; trap 'on_signal 15' TERM; trap 'on_signal 2' INT; trap 'on_signal 1' HUP

# (h) Run codex exec as a child (not exec) so the exit code is logged (f) and the lock is released.
"${cmd[@]}" &
child=$!
wait "$child"; rc=$?
log_line "$rc"; cleanup
exit "$rc"
