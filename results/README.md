# Benchmark results

<!-- Written by results.py from history.jsonl: edits here are overwritten. -->

Every full run of a benchmark adds its times to [`history.jsonl`](history.jsonl) (`../results.py record`, which the benchmarks' scripts call after a full run), and these pages are written again from it: the latest run of each tool, and Speedrun's last runs, so a run that got slower shows. Speedrun's README and the benchmarks' own READMEs take their numbers from here only when Speedrun ships a version (`../results.py readme`).

## Speedrun Bench ([Android](app-android.md), [iOS](app-ios.md))

| Tool, all flows | Android | iOS |
|---|---|---|
| **Speedrun** | **355 s**, 19/19 passed · 2026-10-29 | **563 s**, 19/19 passed · 2026-10-29 |
| Maestro 2.11 | 2798 s, 16/19 passed · 2026-10-27 | 2408 s, 8/19 passed · 2026-10-27 |

Speedrun's speedup over Maestro on the flows both passed: 8.6x on Android (16 flows), 3.0x on iOS (8 flows).

## Compose Bench ([Android](compose-android.md))

| Tool, all flows | Android |
|---|---|
| **Speedrun** | **17.0 s**, 5/5 passed · 2026-11-06 |

## The journey ([Android](journey-android.md), [iOS](journey-ios.md))

| Tool | Android emulator | iOS simulator |
|---|---:|---:|
| **Speedrun** | **20.3 s**, 3/3 passed · 2026-10-29 | **25.5 s**, 3/3 passed · 2026-10-29 |
| Appium | 59.4 s, 3/3 passed · 2026-10-27 | 94.1 s, 3/3 passed · 2026-10-27 |
| maestro-runner | 65.9 s, 2/3 passed · 2026-10-28 | 49.6 s, 3/3 passed · 2026-10-28 |
| Argent | 81.5 s, 3/3 passed · 2026-10-29 | 72.2 s, 3/3 passed · 2026-10-29 |
| XCUITest |  | 81.2 s, 3/3 passed · 2026-10-27 |
| Maestro | 126.5 s, 2/3 passed · 2026-10-27 | 113.1 s, 2/3 passed · 2026-10-27 |

## The web ([details](web.md))

Apple M1 Pro (16 GB):

| Tool | TodoMVC | Real World App, 7 tests |
|---|---:|---:|
| **Speedrun** | **0.66 s**, passed · 2026-11-03 | **4.2 s**, 7/7 passed · 2026-11-03 |
| Playwright | 1.30 s, passed · 2026-11-03 | 5.9 s, 7/7 passed · 2026-11-03 |
| Cypress | 3.66 s, passed · 2026-11-03 | 11.3 s, 7/7 passed · 2026-11-03 |
| Maestro | failed · 2026-11-03 | 3/6 passed in 30 min, then stopped · 2026-11-03 |

GitHub Actions ubuntu-24.04 runner (4 vCPUs):

| Tool | TodoMVC | Real World App, 7 tests |
|---|---:|---:|
| **Speedrun**, Chrome | **0.62 s**, passed · 2026-11-03 | **6.9 s**, 7/7 passed · 2026-11-03 |
| Playwright, Chrome | 1.93 s, passed · 2026-11-03 | 9.3 s, 7/7 passed · 2026-11-03 |
| Cypress, Electron | 6.76 s, passed · 2026-11-03 | 16.8 s, 7/7 passed · 2026-11-03 |
| **Speedrun**, Firefox | **2.99 s**, passed · 2026-11-03 | **11.5 s**, 7/7 passed · 2026-11-03 |
| Playwright, Firefox | 3.88 s, passed · 2026-11-03 | 15.2 s, 7/7 passed · 2026-11-03 |
| Cypress, Firefox | 9.00 s, passed · 2026-11-03 | 21.8 s, 7/7 passed · 2026-11-03 |
