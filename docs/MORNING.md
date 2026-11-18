# Morning queue for Eugene (newest first)

- #137 eez-mode (critical: controls logging): lead check with a real Marine Regions file and a recorded track. EEZ data never committed until the Marine Regions license is verified.
- Cloud env setup script fix (one edit, explains why cloud node tasks cannot run vitest or tsc): change the last line to `cd contrib/deepsignal/console && npm ci` with no `|| true`, so it fails loudly. Diagnostic showed node_modules is empty at task time (setup likely ran before the task branch checkout, or on the default branch with no console/package.json). Until fixed, console modules are built in the cloud and accepted on the Mac; core-v2 runs on the Mac.

- FYI no action: live checks of #131 against OpenVDM 2.17 sample data and #133 against a Sealog demo server come after merge.

- #121 device-pack: approve downloading the public manufacturer manuals named in briefs/mac/p2-device-pack.md (for example the MetSpecs PDF at calcofi.org) into /private/tmp/deepsignal/p2-device-pack/manuals/. Reply yes in the project thread. Until then #121 is held; everything else runs.

- #130 instrument-init: after merge, needs a real-hardware check with a tech present (it writes to instruments). Not run before then.

- #115 roles: pick the login layer (Django accounts, FastAPI JWT, or a reverse proxy). The role engine is built without login; #105 REST binds to localhost until you choose.
- #120 cruise metadata: do you have access to MFP or MOMS exports? v1 ships without that import.
- NCEI KAOU archive blocks robots: a person must download a real SAMOS file by hand if you want byte-exact tests (optional).

Rewritten as items are answered. Each line: what, why it needs you, what is already done around it.

- Mini login: you said the Mini is signed in, but the check on the Mini shows no `~/.codex-deepsignal` (only Kalon's
  `~/.codex`). The sign-in probably landed on the MacBook. On the Mini run:
  `mkdir -p ~/.codex-deepsignal && CODEX_HOME=$HOME/.codex-deepsignal /opt/homebrew/bin/codex login`
  then `resume/mini-finish.sh` runs from the MacBook. Meanwhile the #78 `ultra` review runs on the MacBook (no loss, only slower).
- Downloads for #121 device-pack, #139 kongsberg-tap and the app-ia reference (a saved text copy of https://impeccable.style/): the Mac lane needs Eugene's own yes to download the public manufacturer manuals and format documents named in briefs/mac/p2-device-pack.md and briefs/mac/p2-kongsberg-tap.md into /private/tmp/deepsignal/<module>/manuals/ (manifest with URL, size, SHA-256; never committed). Reply "yes, download the #121 and #139 documents" in the project thread; one yes unlocks all three.
