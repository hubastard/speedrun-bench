# Compose Bench on Android

<!-- Written by results.py from history.jsonl: edits here are overwritten. -->

The latest full run of each tool:

- Speedrun v0.4.8, 2026-11-06: 5/5 passed, 18 s wall clock. Apple M1 Pro (16 GB), Api35 emulator (Android 15).

| Flow | Speedrun |
|---|---:|
| Agent tabs | 2.6 s |
| Authorize | 2.1 s |
| Form | 3.8 s |
| Sheet rows | 4.4 s |
| Tabs | 4.0 s |
| All flows | 17.0 s |
| Wall clock | 17.9 s |

Passed: Speedrun 5/5. ✗: failed (its time up to the failure).

Against Speedrun's run before (v0.4.7-2-g180901f-dirty, 11-06 12:24):

| Flow | Before | Now | Change |
|---|---:|---:|---:|
| Agent tabs | 2.9 s | 2.6 s |  |
| Authorize | 2.1 s | 2.1 s |  |
| Form | 3.1 s | 3.8 s | ▲ +25% |
| Sheet rows | 4.4 s | 4.4 s |  |
| Tabs | 4.0 s | 4.0 s |  |

## Speedrun's last runs

On Apple M1 Pro (16 GB), Api35 emulator (Android 15), newest first. ▲/▼: at least 15% (and 0.5 s) slower/faster than the run before it.

| Flow | v0.4.8<br>11-06 12:25 | v0.4.7-2-g180901f-dirty<br>11-06 12:24 | v0.4.7<br>11-06 11:04 |
|---|---:|---:|---:|
| Agent tabs | 2.6 s | 2.9 s | – |
| Authorize | 2.1 s | 2.1 s | 2.0 s |
| Form | 3.8 s ▲ +25% | 3.1 s | 3.4 s |
| Sheet rows | 4.4 s | 4.4 s | 4.3 s |
| Tabs | 4.0 s | 4.0 s | 3.8 s |
| **All flows** | 17.0 s | 16.5 s ▲ +21% | 13.6 s |
| **Wall clock** | 17.9 s | 17.5 s ▲ +22% | 14.4 s |
