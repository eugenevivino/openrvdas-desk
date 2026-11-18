# Morning queue for Eugene (newest first)

Rewritten as items are answered. Each line: what, why it needs you, what is already done around it.

- Mini login: you said the Mini is signed in, but the check on the Mini shows no `~/.codex-deepsignal` (only Kalon's
  `~/.codex`). The sign-in probably landed on the MacBook. On the Mini run:
  `mkdir -p ~/.codex-deepsignal && CODEX_HOME=$HOME/.codex-deepsignal /opt/homebrew/bin/codex login`
  then `resume/mini-finish.sh` runs from the MacBook. Meanwhile the #78 `ultra` review runs on the MacBook (no loss, only slower).
