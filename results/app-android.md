# Speedrun Bench on Android

<!-- Written by results.py from history.jsonl: edits here are overwritten. -->

The latest full run of each tool:

- Speedrun v0.4.12, 2026-11-11: 21/21 passed, 402 s wall clock. Apple M1 Pro (16 GB), Medium_Phone emulator (Android 17).
- Maestro 2.11, 2026-10-27: 16/19 passed, 2816 s wall clock. Apple M1 Pro (16 GB), Medium_Phone emulator (Android 17).

| Flow | Speedrun | Maestro | Speedup |
|---|---:|---:|---:|
| A JavaScript stack's screen closing while the JavaScript thread is busy | 7 s | – |  |
| A remembered account survives clearState on iOS, but not clearKeychain | 10 s | 34 s | 3.4x |
| Buy twice, with search, options, a promo code that fails once and the popups after | 54 s | 232 s | 4.3x |
| Cart lines, steppers and swipe to remove | 15 s | 75 s | 5.0x |
| Chat with the bot, long press and double tap a message, paste, quick replies | 17 s | 76 s | 4.5x |
| Confetti, a button that turns on late, a layout shift, a busy JavaScript thread | 12 s | 66 s | 5.5x |
| Dark mode, screenshots and a recording | 7 s | 48 s | 7.4x |
| Deep links to a product, a lab screen and the cart | 25 s | 36 s | 1.4x |
| Drag a slider and a card, scroll sideways, a long list with sticky headers | 17 s | 50 s ✗ (~60 s) | ~3.5x |
| Edit the profile, change settings, set a PIN, sign out | 22 s | 150 s | 6.9x |
| Elements told apart by place (index, relative, parent, child) and by state | 22 s | 62 s | 2.8x |
| Feed with a ticker, stories, likes, a double tap, more posts and pull to refresh | 30 s | 82 s ✗ (~125 s) | ~4.2x |
| Launch arguments, location, permissions, photos, orientation, app lifecycle, airplane mode | 24 s | 73 s | 3.1x |
| Native UI (Jetpack Compose, SwiftUI): texts that change, views that come and go, a spring, a loading overlay, a lazy list | 17 s | – |  |
| Onboarding pages, and no onboarding on the next launch | 5 s | 28 s ✗ (~24 s) | ~5.1x |
| Popups that come one after another (native modals, a sheet) | 29 s | 56 s | 1.9x |
| Scripts, env, conditions, repeat and retry | 12 s | 37 s | 3.2x |
| Sign in with a phone number and a code, a wrong one first | 8 s | 40 s | 4.8x |
| Swipes in four directions, taps at a point, single, double and long press | 7 s | 44 s | 6.0x |
| Taps on screens that never stop moving | 37 s | 1450 s | 39.1x |
| Typing, keys, erasing, copy and paste, random text, a draft kept across restarts | 25 s | 159 s | 6.3x |
| **All flows** | **401 s** | **2798 s** | **7.0x** |
| **Flows both passed (16)** | **326 s** | **2638 s** | **8.1x** |
| **All flows, Maestro's failures estimated** | **401 s** | **~2847 s** | **~7.1x** |
| **Wall clock** | **402 s** | **2816 s** | **7.0x** |

Passed: Speedrun 21/21, Maestro 16/19. ✗: failed (its time up to the failure); ~: estimated, had Maestro finished the flow.

Against Speedrun's run before (v0.4.11, 11-10 09:12):

| Flow | Before | Now | Change |
|---|---:|---:|---:|
| A JavaScript stack's screen closing while the JavaScript thread is busy | 7 s | 7 s |  |
| A remembered account survives clearState on iOS, but not clearKeychain | 10 s | 10 s |  |
| Buy twice, with search, options, a promo code that fails once and the popups after | 56 s | 54 s |  |
| Cart lines, steppers and swipe to remove | 16 s | 15 s |  |
| Chat with the bot, long press and double tap a message, paste, quick replies | 17 s | 17 s |  |
| Confetti, a button that turns on late, a layout shift, a busy JavaScript thread | 12 s | 12 s |  |
| Dark mode, screenshots and a recording | 7 s | 7 s |  |
| Deep links to a product, a lab screen and the cart | 25 s | 25 s |  |
| Drag a slider and a card, scroll sideways, a long list with sticky headers | 19 s | 17 s |  |
| Edit the profile, change settings, set a PIN, sign out | 22 s | 22 s |  |
| Elements told apart by place (index, relative, parent, child) and by state | 23 s | 22 s |  |
| Feed with a ticker, stories, likes, a double tap, more posts and pull to refresh | 31 s | 30 s |  |
| Launch arguments, location, permissions, photos, orientation, app lifecycle, airplane mode | 24 s | 24 s |  |
| Native UI (Jetpack Compose, SwiftUI): texts that change, views that come and go, a spring, a loading overlay, a lazy list | 17 s | 17 s |  |
| Onboarding pages, and no onboarding on the next launch | 4 s | 5 s |  |
| Popups that come one after another (native modals, a sheet) | 29 s | 29 s |  |
| Scripts, env, conditions, repeat and retry | 12 s | 12 s |  |
| Sign in with a phone number and a code, a wrong one first | 9 s | 8 s |  |
| Swipes in four directions, taps at a point, single, double and long press | 7 s | 7 s |  |
| Taps on screens that never stop moving | 36 s | 37 s |  |
| Typing, keys, erasing, copy and paste, random text, a draft kept across restarts | 26 s | 25 s |  |

## Speedrun's last runs

On Apple M1 Pro (16 GB), Medium_Phone emulator (Android 17), newest first. ▲/▼: at least 15% (and 1 s) slower/faster than the run before it.

| Flow | v0.4.12<br>11-11 08:31 | v0.4.11<br>11-10 09:12 | 10-29 12:00 |
|---|---:|---:|---:|
| A JavaScript stack's screen closing while the JavaScript thread is busy | 7 s | 7 s | – |
| A remembered account survives clearState on iOS, but not clearKeychain | 10 s | 10 s ▲ +20% | 8 s |
| Buy twice, with search, options, a promo code that fails once and the popups after | 54 s | 56 s | 52 s |
| Cart lines, steppers and swipe to remove | 15 s | 16 s | 15 s |
| Chat with the bot, long press and double tap a message, paste, quick replies | 17 s | 17 s | 17 s |
| Confetti, a button that turns on late, a layout shift, a busy JavaScript thread | 12 s | 12 s | 12 s |
| Dark mode, screenshots and a recording | 7 s | 7 s ▲ +24% | 6 s |
| Deep links to a product, a lab screen and the cart | 25 s | 25 s | 24 s |
| Drag a slider and a card, scroll sideways, a long list with sticky headers | 17 s | 19 s ▲ +18% | 16 s |
| Edit the profile, change settings, set a PIN, sign out | 22 s | 22 s | 21 s |
| Elements told apart by place (index, relative, parent, child) and by state | 22 s | 23 s | 20 s |
| Feed with a ticker, stories, likes, a double tap, more posts and pull to refresh | 30 s | 31 s | 29 s |
| Launch arguments, location, permissions, photos, orientation, app lifecycle, airplane mode | 24 s | 24 s | 22 s |
| Native UI (Jetpack Compose, SwiftUI): texts that change, views that come and go, a spring, a loading overlay, a lazy list | 17 s | 17 s | – |
| Onboarding pages, and no onboarding on the next launch | 5 s | 4 s | 5 s |
| Popups that come one after another (native modals, a sheet) | 29 s | 29 s ▲ +40% | 21 s |
| Scripts, env, conditions, repeat and retry | 12 s | 12 s | 11 s |
| Sign in with a phone number and a code, a wrong one first | 8 s | 9 s | 9 s |
| Swipes in four directions, taps at a point, single, double and long press | 7 s | 7 s | 7 s |
| Taps on screens that never stop moving | 37 s | 36 s | 35 s |
| Typing, keys, erasing, copy and paste, random text, a draft kept across restarts | 25 s | 26 s | 25 s |
| **All flows** | 401 s | 411 s ▲ +16% | 355 s |
| **Wall clock** | 402 s | 412 s ▲ +16% | 355 s |
