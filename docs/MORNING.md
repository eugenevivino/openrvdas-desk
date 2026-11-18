# Morning queue for Eugene (newest first)

- D-SEC1 adopt the security architecture and its MVP cut (docs/SECURITY-ARCHITECTURE.md section 12). Security code merges wait for you.
- D-SEC2 login layer: recommended Django accounts plus allauth MFA (this closes the #115 login item).
- D-SEC3 rename the #115 role "public" to "authenticated viewer".
- D-SEC4 one secrets vault; #188 AI stays off until #192 lands.
- D-SEC5 reference FIPS platform: RHEL 9.

- SECURITY (critical): upstream CachedDataServer binds all interfaces on 8766 and accepts unauthenticated publish, including via nginx /cds-ws. The console install must bind it to localhost and expose a read-only websocket only; closing publish is part of the security architecture block (#189-#198, trust zones plus CDS write lockdown). Do not expose the console beyond the ship LAN until that lands.


- #188 AI watch assistant: pick the API provider and put the key in the ship environment (never in git). A lead check against the real API runs outside the sandbox. Defaults: $2/day, $30/month caps; you can change them.

- CRITICAL security package, offline first: signed audit (#32), local identity, trust zones (#115, #151, #155). Needs your review before anything is enabled.
- #164 CalibrationTransform must NOT be enabled on any live config until you approve.

- #137 eez-mode (critical: controls logging): lead check with a real Marine Regions file and a recorded track. EEZ data never committed until the Marine Regions license is verified.
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
- Downloads for #121 device-pack and #139 kongsberg-tap: the Mac lane needs Eugene's own yes to download the public manufacturer manuals and format documents named in briefs/mac/p2-device-pack.md and briefs/mac/p2-kongsberg-tap.md into /private/tmp/deepsignal/<module>/manuals/ (manifest with URL, size, SHA-256; never committed). Reply "yes, download the #121 and #139 documents" in the project thread; one yes unlocks both.
