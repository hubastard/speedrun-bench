# The web benchmark

<!-- Written by results.py from history.jsonl: edits here are overwritten. -->

The latest runs of each tool: the median of its passed runs, the pass count, and each run's time.

## Apple M1 Pro (16 GB)

| Tool | TodoMVC | Real World App |
|---|---|---|
| Speedrun, Chrome | 0.66 s, 3/3 passed (0.68, 0.66, 0.66) · 2026-11-03 | 4.19 s, 3/3 passed (4.20, 4.19, 4.19) · 2026-11-03 |
| Playwright, Chrome | 1.30 s, 3/3 passed (1.29, 1.30, 1.30) · 2026-11-03 | 5.86 s, 3/3 passed (5.89, 5.86, 5.83) · 2026-11-03 |
| Cypress, Electron | 3.66 s, 3/3 passed (3.66, 3.66, 3.66) · 2026-11-03 | 11.32 s, 3/3 passed (11.33, 11.29, 11.32) · 2026-11-03 |
| Maestro, Chrome | failed in every run, after ~60 s · 2026-11-03 | stopped after 30 min: 6 of 7 tests run, 3 passed · 2026-11-03 |

## GitHub Actions ubuntu-24.04 runner (4 vCPUs)

| Tool | TodoMVC | Real World App |
|---|---|---|
| Speedrun, Chrome | 0.62 s, 3/3 passed (0.62, 0.69, 0.62) · 2026-11-03 | 6.87 s, 3/3 passed (7.10, 6.81, 6.87) · 2026-11-03 |
| Playwright, Chrome | 1.93 s, 3/3 passed (1.93, 1.92, 1.93) · 2026-11-03 | 9.33 s, 3/3 passed (9.91, 9.33, 9.29) · 2026-11-03 |
| Cypress, Electron | 6.76 s, 3/3 passed (6.42, 6.78, 6.76) · 2026-11-03 | 16.78 s, 3/3 passed (16.78, 17.15, 16.76) · 2026-11-03 |
| Speedrun, Firefox | 2.99 s, 3/3 passed (2.99, 2.99, 3.05) · 2026-11-03 | 11.51 s, 3/3 passed (11.44, 11.69, 11.51) · 2026-11-03 |
| Playwright, Firefox | 3.88 s, 3/3 passed (3.87, 3.88, 4.21) · 2026-11-03 | 15.16 s, 3/3 passed (15.08, 15.38, 15.16) · 2026-11-03 |
| Cypress, Firefox | 9.00 s, 3/3 passed (9.18, 9.00, 8.87) · 2026-11-03 | 21.75 s, 3/3 passed (21.88, 21.75, 21.74) · 2026-11-03 |
