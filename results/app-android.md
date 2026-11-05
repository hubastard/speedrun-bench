# Speedrun Bench on Android

<!-- Written by results.py from history.jsonl: edits here are overwritten. -->

The latest full run of each tool:

- Speedrun, 2026-10-29: 19/19 passed, 355 s wall clock. Apple M1 Pro (16 GB), Medium_Phone emulator (Android 17).
- Maestro 2.11, 2026-10-27: 16/19 passed, 2816 s wall clock. Apple M1 Pro (16 GB), Medium_Phone emulator (Android 17).

| Flow | Speedrun | Maestro | Speedup |
|---|---:|---:|---:|
| A remembered account survives clearState on iOS, but not clearKeychain | 8 s | 34 s | 4.2x |
| Buy twice, with search, options, a promo code that fails once and the popups after | 52 s | 232 s | 4.5x |
| Cart lines, steppers and swipe to remove | 15 s | 75 s | 5.0x |
| Chat with the bot, long press and double tap a message, paste, quick replies | 17 s | 76 s | 4.5x |
| Confetti, a button that turns on late, a layout shift, a busy JavaScript thread | 12 s | 66 s | 5.5x |
| Dark mode, screenshots and a recording | 6 s | 48 s | 8.0x |
| Deep links to a product, a lab screen and the cart | 24 s | 36 s | 1.5x |
| Drag a slider and a card, scroll sideways, a long list with sticky headers | 16 s | 50 s ✗ (~60 s) | ~3.8x |
| Edit the profile, change settings, set a PIN, sign out | 21 s | 150 s | 7.1x |
| Elements told apart by place (index, relative, parent, child) and by state | 20 s | 62 s | 3.1x |
| Feed with a ticker, stories, likes, a double tap, more posts and pull to refresh | 29 s | 82 s ✗ (~125 s) | ~4.3x |
| Launch arguments, location, permissions, photos, orientation, app lifecycle, airplane mode | 22 s | 73 s | 3.3x |
| Onboarding pages, and no onboarding on the next launch | 5 s | 28 s ✗ (~24 s) | ~4.8x |
| Popups that come one after another (native modals, a sheet) | 21 s | 56 s | 2.7x |
| Scripts, env, conditions, repeat and retry | 11 s | 37 s | 3.4x |
| Sign in with a phone number and a code, a wrong one first | 9 s | 40 s | 4.4x |
| Swipes in four directions, taps at a point, single, double and long press | 7 s | 44 s | 6.3x |
| Taps on screens that never stop moving | 35 s | 1450 s | 41.4x |
| Typing, keys, erasing, copy and paste, random text, a draft kept across restarts | 25 s | 159 s | 6.4x |
| **All flows** | **355 s** | **2798 s** | **7.9x** |
| **Flows both passed (16)** | **305 s** | **2638 s** | **8.6x** |
| **All flows, Maestro's failures estimated** | **355 s** | **~2847 s** | **~8.0x** |
| **Wall clock** | **355 s** | **2816 s** | **7.9x** |

Passed: Speedrun 19/19, Maestro 16/19. ✗: failed (its time up to the failure); ~: estimated, had Maestro finished the flow.

## Speedrun's last runs

On Apple M1 Pro (16 GB), Medium_Phone emulator (Android 17), newest first. ▲/▼: at least 15% (and 1 s) slower/faster than the run before it.

| Flow | 10-29 12:00 |
|---|---:|
| A remembered account survives clearState on iOS, but not clearKeychain | 8 s |
| Buy twice, with search, options, a promo code that fails once and the popups after | 52 s |
| Cart lines, steppers and swipe to remove | 15 s |
| Chat with the bot, long press and double tap a message, paste, quick replies | 17 s |
| Confetti, a button that turns on late, a layout shift, a busy JavaScript thread | 12 s |
| Dark mode, screenshots and a recording | 6 s |
| Deep links to a product, a lab screen and the cart | 24 s |
| Drag a slider and a card, scroll sideways, a long list with sticky headers | 16 s |
| Edit the profile, change settings, set a PIN, sign out | 21 s |
| Elements told apart by place (index, relative, parent, child) and by state | 20 s |
| Feed with a ticker, stories, likes, a double tap, more posts and pull to refresh | 29 s |
| Launch arguments, location, permissions, photos, orientation, app lifecycle, airplane mode | 22 s |
| Onboarding pages, and no onboarding on the next launch | 5 s |
| Popups that come one after another (native modals, a sheet) | 21 s |
| Scripts, env, conditions, repeat and retry | 11 s |
| Sign in with a phone number and a code, a wrong one first | 9 s |
| Swipes in four directions, taps at a point, single, double and long press | 7 s |
| Taps on screens that never stop moving | 35 s |
| Typing, keys, erasing, copy and paste, random text, a draft kept across restarts | 25 s |
| **All flows** | 355 s |
| **Wall clock** | 355 s |
