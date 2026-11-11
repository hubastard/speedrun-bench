# Compose Bench on Android

<!-- Written by results.py from history.jsonl: edits here are overwritten. -->

The latest full run of each tool:

- Speedrun v0.4.13, 2026-11-11: 10/10 passed, 26 s wall clock. Apple M1 Pro (16 GB), Api35 emulator (Android 15).

| Flow | Speedrun |
|---|---:|
| Agent tabs | 2.5 s |
| Authorize | 1.6 s |
| Consent | 4.6 s |
| Form | 3.0 s |
| Notes | 2.5 s |
| Notifications | 0.9 s |
| Sheet rows | 3.5 s |
| Skill back | 1.8 s |
| Tabs | 3.4 s |
| Tasks | 1.5 s |
| All flows | 25.4 s |
| Wall clock | 26.3 s |

Passed: Speedrun 10/10. ✗: failed (its time up to the failure).

Against Speedrun's run before (v0.4.12, 11-11 08:36):

| Flow | Before | Now | Change |
|---|---:|---:|---:|
| Agent tabs | 2.6 s | 2.5 s |  |
| Authorize | 1.6 s | 1.6 s |  |
| Consent | 2.5 s | 4.6 s | ▲ +85% |
| Form | 2.9 s | 3.0 s |  |
| Notes | 2.9 s | 2.5 s |  |
| Notifications | 1.1 s | 0.9 s |  |
| Sheet rows | 3.8 s | 3.5 s |  |
| Skill back | 1.9 s | 1.8 s |  |
| Tabs | 3.8 s | 3.4 s |  |
| Tasks | 1.6 s | 1.5 s |  |

## Speedrun's last runs

On Apple M1 Pro (16 GB), Api35 emulator (Android 15), newest first. ▲/▼: at least 15% (and 0.5 s) slower/faster than the run before it.

| Flow | v0.4.13<br>11-11 09:36 | v0.4.12<br>11-11 08:36 | v0.4.11<br>11-09 18:26 | v0.4.10<br>11-07 06:11 | v0.4.9<br>11-06 14:33 | v0.4.8<br>11-06 12:25 | v0.4.7-2-g180901f-dirty<br>11-06 12:24 | v0.4.7<br>11-06 11:04 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Agent tabs | 2.5 s | 2.6 s ▼ −20% | 3.3 s | 3.0 s | 2.8 s | 2.6 s | 2.9 s | – |
| Authorize | 1.6 s | 1.6 s ▼ −46% | 3.0 s ▲ +25% | 2.4 s | 2.1 s | 2.1 s | 2.1 s | 2.0 s |
| Consent | 4.6 s ▲ +85% | 2.5 s ▼ −29% | 3.5 s ▲ +31% | 2.6 s | – | – | – | – |
| Form | 3.0 s | 2.9 s ▼ −56% | 6.6 s ▲ +26% | 5.3 s | 4.6 s ▲ +21% | 3.8 s ▲ +25% | 3.1 s | 3.4 s |
| Notes | 2.5 s | 2.9 s ▼ −54% | 6.3 s | – | – | – | – | – |
| Notifications | 0.9 s | 1.1 s ▼ −51% | 2.2 s | – | – | – | – | – |
| Sheet rows | 3.5 s | 3.8 s ▼ −32% | 5.5 s ▲ +23% | 4.5 s | 4.3 s | 4.4 s | 4.4 s | 4.3 s |
| Skill back | 1.8 s | 1.9 s ▼ −33% | 2.9 s | 2.6 s | 2.4 s | – | – | – |
| Tabs | 3.4 s | 3.8 s ▼ −17% | 4.5 s | 4.3 s | 4.0 s | 4.0 s | 4.0 s | 3.8 s |
| Tasks | 1.5 s | 1.6 s ▼ −26% | 2.1 s | 1.7 s | – | – | – | – |
| **All flows** | 25.4 s | 24.6 s ▼ −38% | 39.9 s ▲ +51% | 26.4 s ▲ +30% | 20.3 s ▲ +19% | 17.0 s | 16.5 s ▲ +21% | 13.6 s |
| **Wall clock** | 26.3 s | 26.6 s ▼ −36% | 41.6 s ▲ +48% | 28.1 s ▲ +32% | 21.3 s ▲ +19% | 17.9 s | 17.5 s ▲ +22% | 14.4 s |
