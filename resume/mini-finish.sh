#!/bin/bash
# Finish the DeepSignal setup on the Mac Mini, run FROM THE MACBOOK, after Eugene has logged in on the Mini himself:
#   (on the Mini)  mkdir -p ~/.codex-deepsignal && CODEX_HOME=$HOME/.codex-deepsignal /opt/homebrew/bin/codex login
# Then (on the MacBook):  bash resume/mini-finish.sh
# It copies the DeepSignal config.toml and ds-codex (desk tools/ds-codex.sh) to the Mini, creates the Mini's own scratch
# /private/tmp/deepsignal (never /private/tmp/kalon), installs the Mini launch gate with the lower Mini RAM floor, and runs
# dry-run tests only. No Codex job is started. No secrets: auth stays in the Mini's own ~/.codex-deepsignal/auth.json.
set -euo pipefail
MINI=${MINI:-kalon-mini}
DESK_RAW=https://raw.githubusercontent.com/eugenevivino/openrvdas-desk/tools/ds-codex/tools/ds-codex.sh
tmp=$(mktemp -d /private/tmp/deepsignal/mini-finish.XXXXXX); trap 'rm -rf "$tmp"' EXIT

echo "== 1. Mini preflight (read-only)"
ssh -o ConnectTimeout=10 "$MINI" 'set -e; [ "$(scutil --get LocalHostName)" = EugeneMacMini ] || { echo "not the Mini"; exit 1; }
  /opt/homebrew/bin/codex --version
  CODEX_HOME=$HOME/.codex-deepsignal /opt/homebrew/bin/codex login status | grep -q "Logged in" || { echo "NOT LOGGED IN: run the login first"; exit 1; }
  echo logged-in; [ ! -e $HOME/.codex-deepsignal/config.toml ] || echo "config.toml exists (kept)"'

echo "== 2. config.toml (only if missing; same keys as the MacBook DeepSignal home)"
printf 'service_tier = "default"\n\n[features]\njs_repl = false\nmemories = false\nhooks = false\n' > "$tmp/config.toml"
ssh "$MINI" '[ -e $HOME/.codex-deepsignal/config.toml ]' || scp -q "$tmp/config.toml" "$MINI:.codex-deepsignal/config.toml"

echo "== 3. ds-codex (atomic replace) and the Mini launch gate"
curl -fsSL "$DESK_RAW" -o "$tmp/ds-codex"; bash -n "$tmp/ds-codex"
cat > "$tmp/ds-mini-gate" <<'GATE'
#!/bin/bash
# Mini launch gate: lower RAM floor for the 8 GB Mini (lead decision 2026-11-18, pending Eugene's confirmation),
# pressure level must be 1, one DeepSignal job at a time (ds-codex lock), refuse during a Kalon gate.
export DS_MIN_FREE_MB=2048 DS_MAX_SWAP_MB=2457 DS_REQUIRE_PRESSURE1=1
for l in ~/KalonWork/lock-w0 ~/KalonWork/lock-w1 ~/KalonWork/lock-w2; do [ -e "$l" ] && { echo "ds-mini-gate: REFUSED: Kalon lock $l exists" >&2; exit 12; }; done
pgrep -f mini-gate-suite.sh >/dev/null && { echo "ds-mini-gate: REFUSED: Kalon mini-gate-suite is running" >&2; exit 12; }
exec "$HOME/bin/ds-codex" "$@"
GATE
ssh "$MINI" 'mkdir -p $HOME/bin /private/tmp/deepsignal'
scp -q "$tmp/ds-codex" "$MINI:bin/.ds-codex.new"; scp -q "$tmp/ds-mini-gate" "$MINI:bin/.ds-mini-gate.new"
ssh "$MINI" 'chmod +x $HOME/bin/.ds-codex.new $HOME/bin/.ds-mini-gate.new && mv -f $HOME/bin/.ds-codex.new $HOME/bin/ds-codex && mv -f $HOME/bin/.ds-mini-gate.new $HOME/bin/ds-mini-gate && ls -l $HOME/bin/ds-codex $HOME/bin/ds-mini-gate'

echo "== 4. dry-run tests on the Mini (no job is started)"
ssh "$MINI" 'cd /private/tmp/deepsignal
  t(){ d="$1"; shift; out=$("$@" 2>&1); rc=$?; echo "[$d] rc=$rc $(echo "$out" | grep -E "REFUSED|RAM gate" | head -1)"; }
  t "sol dry-run via mini gate" $HOME/bin/ds-mini-gate --dry-run -m gpt-6.2-sol -c model_reasoning_effort=high -
  t "no -m (expect 7)" $HOME/bin/ds-codex --dry-run -
  t "astra without opt-in (expect 3)" $HOME/bin/ds-codex --dry-run -m gpt-6.2-astra -
  t "multi_agent re-enable (expect 8)" $HOME/bin/ds-codex --dry-run -m gpt-6.2-sol -c features.multi_agent=true -
  (cd /private/tmp && t "cwd outside scratch (expect 9)" $HOME/bin/ds-codex --dry-run -m gpt-6.2-sol -)
  echo "CODEX_HOME in dry-run: $($HOME/bin/ds-codex --dry-run -m gpt-6.2-sol - 2>/dev/null | grep -oE "^CODEX_HOME=[^ ]+")"
  sysctl kern.memorystatus_vm_pressure_level vm.swapusage'
echo "== done. Clones on the Mini: after git clone, run git config gc.auto 0 && git config maintenance.auto false in each."
