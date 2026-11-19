---
needs:
  network: yes
  tools: git, node, npm
  disk_gb: 2
  ram_gb: 3
  required_files: contrib/deepsignal/console/package.json, contrib/deepsignal/console/package-lock.json, /private/tmp/deepsignal/desk-main/docs/designs/console.md
---

# Console pilot follow-up

Approval pending. Build only after approval and launcher admission. Use the
isolated checkout and pinned base in the design note. Scope is the console
production paths and tests for T-CON-1 through T-CON-3. Record red and green
D-FIX1 evidence, then run self-check against the note and D-P1DEF1.

## Acceptance
```sh
cd contrib/deepsignal/console && npm test -- src/cds.test.ts -t T-CON-1
cd contrib/deepsignal/console && npm test -- src/cds.test.ts -t T-CON-2
cd contrib/deepsignal/console && npm test -- src/modules/map/map.test.tsx -t T-CON-3
cd contrib/deepsignal/console && npm test
cd contrib/deepsignal/console && npm run lint
cd contrib/deepsignal/console && npm run type-check
cd contrib/deepsignal/console && npm run build
```
