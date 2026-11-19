# Design note: <unit> (D-DESIGN1)

One page. Written by Astra (read-only) before Sol builds; Sol builds against it; reviewers judge against it.
A review finding outside this note's scope is a ticket unless it meets D-P1DEF1 (a), (b) or (c).

- Unit: `<name>` on fork branch `deepsignal/<module>`; launcher unit name `<name in wip-units.txt>`.
- Author and date: Astra (<effort>), <date>. Status: DRAFT or FIXED.

## Fixed target
What the unit does when done, in a few sentences. One target; no "and also".

## Acceptance tests (commands)
Exact commands, each on its own line, macOS-safe (D-PIPE1 rule 7). Each names the behavior it proves.

## Out of scope
What this unit will not do, so reviewers file it as a ticket.

## Prerequisites on trunk
What must already be on `deepsignal/integration` (or named branches) before the build starts, and how that was checked.

## Who judges
Reviewer (model, effort, cloud or Mac per CODEX.md routing), the gate of record (D-PIPE1 rule 6), and who merges.
