# Compose Bench on Android

<!-- Written by results.py from history.jsonl: edits here are overwritten. -->

The latest full run of each tool:

- Speedrun v0.4.10, 2026-11-07: 8/8 passed, 28 s wall clock. Apple M1 Pro (16 GB), Api35 emulator (Android 15).

| Flow | Speedrun |
|---|---:|
| Agent tabs | 3.0 s |
| Authorize | 2.4 s |
| Consent | 2.6 s |
| Form | 5.3 s |
| Sheet rows | 4.5 s |
| Skill back | 2.6 s |
| Tabs | 4.3 s |
| Tasks | 1.7 s |
| All flows | 26.4 s |
| Wall clock | 28.1 s |

Passed: Speedrun 8/8. ✗: failed (its time up to the failure).

Against Speedrun's run before (v0.4.9, 11-06 14:33):

| Flow | Before | Now | Change |
|---|---:|---:|---:|
| Agent tabs | 2.8 s | 3.0 s |  |
| Authorize | 2.1 s | 2.4 s |  |
| Consent | – | 2.6 s |  |
| Form | 4.6 s | 5.3 s |  |
| Sheet rows | 4.3 s | 4.5 s |  |
| Skill back | 2.4 s | 2.6 s |  |
| Tabs | 4.0 s | 4.3 s |  |
| Tasks | – | 1.7 s |  |

## Speedrun's last runs

On Apple M1 Pro (16 GB), Api35 emulator (Android 15), newest first. ▲/▼: at least 15% (and 0.5 s) slower/faster than the run before it.

| Flow | v0.4.10<br>11-07 06:11 | v0.4.9<br>11-06 14:33 | v0.4.8<br>11-06 12:25 | v0.4.7-2-g180901f-dirty<br>11-06 12:24 | v0.4.7<br>11-06 11:04 |
|---|---:|---:|---:|---:|---:|
| Agent tabs | 3.0 s | 2.8 s | 2.6 s | 2.9 s | – |
| Authorize | 2.4 s | 2.1 s | 2.1 s | 2.1 s | 2.0 s |
| Consent | 2.6 s | – | – | – | – |
| Form | 5.3 s | 4.6 s ▲ +21% | 3.8 s ▲ +25% | 3.1 s | 3.4 s |
| Sheet rows | 4.5 s | 4.3 s | 4.4 s | 4.4 s | 4.3 s |
| Skill back | 2.6 s | 2.4 s | – | – | – |
| Tabs | 4.3 s | 4.0 s | 4.0 s | 4.0 s | 3.8 s |
| Tasks | 1.7 s | – | – | – | – |
| **All flows** | 26.4 s ▲ +30% | 20.3 s ▲ +19% | 17.0 s | 16.5 s ▲ +21% | 13.6 s |
| **Wall clock** | 28.1 s ▲ +32% | 21.3 s ▲ +19% | 17.9 s | 17.5 s ▲ +22% | 14.4 s |
