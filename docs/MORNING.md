# Morning queue for Eugene (newest first)

- #130 instrument-init: after merge, needs a real-hardware check with a tech present (it writes to instruments). Not run before then.

- #115 roles: pick the login layer (Django accounts, FastAPI JWT, or a reverse proxy). The role engine is built without login; #105 REST binds to localhost until you choose.
- #120 cruise metadata: do you have access to MFP or MOMS exports? v1 ships without that import.
- NCEI KAOU archive blocks robots: a person must download a real SAMOS file by hand if you want byte-exact tests (optional).

Rewritten as items are answered. Each line: what, why it needs you, what is already done around it.

- Mini login: you said the Mini is signed in, but the check on the Mini shows no `~/.codex-deepsignal` (only Kalon's
  `~/.codex`). The sign-in probably landed on the MacBook. On the Mini run:
  `mkdir -p ~/.codex-deepsignal && CODEX_HOME=$HOME/.codex-deepsignal /opt/homebrew/bin/codex login`
  then `resume/mini-finish.sh` runs from the MacBook. Meanwhile the #78 `ultra` review runs on the MacBook (no loss, only slower).
