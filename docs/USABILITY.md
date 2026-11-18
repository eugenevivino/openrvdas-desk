# Usability checklist (rule 26)

Audience: a ship tech or watch stander at 3 a.m. who can edit a text file but
is not a programmer. Every module and every screen must pass. A reviewer
answers each line with PASS, FAIL or N/A and a reason; any FAIL blocks the PR.

## Turning it on
1. A copy-paste sample logger config ships with the module and runs as is.
2. A README section titled "Turn it on in 5 minutes": what it does in one
   sentence, the three steps, how to see it working, how to turn it off.
3. Safe defaults: with only the required settings it works and cannot hurt
   other loggers or data. Every other setting has a stated default.
4. Time test: a person who has never seen the module enables it in under 15
   minutes from the README alone. Recorded once per module (who, how long).

## When something is wrong
5. Config is checked at start. A bad value names the setting, what it saw, what
   it expected, and an example of a good value.
6. Error and log messages say what went wrong and what to do next, in plain
   English. A stack trace goes to the debug log, never as the main message.
7. Missing, stale and bad data are shown as missing, stale and bad (never
   hidden, never invented). Say how old, since when, and what the sensor was
   last seen doing.
8. Nothing fails silently. Nothing needs a restart to recover unless the
   message says so and says how.

## Screens
9. Readable at a glance from across the room: large type, plain words, one clear
   state per item (OK, Check, Stale, Down) shown by words and shape as well as color.
10. Night-safe: dark mode that keeps the bridge dark, no bright flashes, sound
    only if the tech turns it on.
11. No hidden actions: every button says what it will do; anything that changes
    a running logger asks once, says what will happen, and can be undone.
12. Works on the screens ships actually have (a small laptop, a bridge display,
    a phone on the ship network).

## Words
13. Plain language, short sentences, units always shown, no unexplained
    acronyms. Terms match what crews already say.
14. Docs state what the module does NOT do.

Success metrics from `docs/IDEAS.md` apply: add a sensor in under 15 minutes, a
bad sensor noticed in under 1 hour.
