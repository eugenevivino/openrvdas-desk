# RVTEC interview and survey questions

Source: the 18 questions in `docs/PAIN-POINTS.md` (Deep Research, 2026-11-18), copied word for word. Each one is mapped to the DeepSignal items it validates or could kill. Use them in RVTEC sessions, onboard visits and the shadow pilot (#70). Record the answers in `research/interviews/` with the vessel, the role and the date. Never record names without consent.

| # | Question | Validates |
|---|---|---|
| 1 | “Tell me about the last three times you lost scientifically useful data even though the acquisition computer still looked healthy. When did you discover it, and what would have exposed it earlier?” | #162, #79, #8 |
| 2 | “At cruise start, what files, spreadsheets, scripts, dashboards and handwritten notes do you touch before you trust the ship’s systems?” | #114, #126, #163 |
| 3 | “Which configuration changes are dangerous enough that you personally double-check them? How do you know what changed between cruises?” | #163, #127 |
| 4 | “Which feeds can be stale or wrong while still displaying believable values?” | #162, #79, #164 |
| 5 | “What failure wakes you at 0300 most often?” | #162, #167, #168 |
| 6 | “What information do you need in the first 60 seconds of an alarm to decide whether to wake somebody else?” | #162 console chain, #167 |
| 7 | “Which faults require you to SSH/RDP into multiple machines before you understand the chain of failure?” | #162, #168 |
| 8 | “Where do calibration constants and sensor metadata actually live today? Which copy is authoritative?” | #164, #7, #52 |
| 9 | “What data do you routinely discover are missing only during end-of-cruise packaging?” | #166, #58 |
| 10 | “If a new technician joined tomorrow, what would they be unable to infer from the formal documentation?” | #167, #118 |
| 11 | “Which systems require vendor licenses, dongles, remote support or Windows-only tools that cause operational friction?” | #72, #138, #139 |
| 12 | “What do you deliberately avoid updating before a cruise because you fear breaking it?” | #163, #154 |
| 13 | “Which instrument systems are physically isolated for cybersecurity reasons, and what monitoring visibility do you lose because of that?” | #151, #162 |
| 14 | “What happens to your monitoring, authentication and data-transfer workflows when Internet access disappears for six hours?” | offline-first (MORNING), #123, #135 |
| 15 | “For deck/winch operations, what exact numbers need to be visible outdoors, at what update rate, and what failure or stale-data indication is acceptable?” | #5 scoreboard, #109, #13 |
| 16 | “For PSOs, which fields are still copied manually from navigation or seismic-control screens into mitigation records?” | #160 |
| 17 | “Which ship-to-shore data do you send immediately, which do you postpone, and who changes those priorities?” | #131, #135, #19 |
| 18 | “What would you refuse to let a centralized console control, even if it could technically do so?” | #64, #65, #154 (control limits) |

Priority interview groups the study flags as evidence gaps: winch and LCI-90i operators and deck scoreboards (Q15), PSOs on seismic cruises (Q16), seismic acquisition (hold #158 and #159 until answered), EEZ data-restriction workflows (#137 defaults), and fleets outside the US and UK (JAMSTEC, Ifremer, NIOZ, Canadian Coast Guard, NIWA).
