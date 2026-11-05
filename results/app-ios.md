# Speedrun Bench on iOS

<!-- Written by results.py from history.jsonl: edits here are overwritten. -->

The latest full run of each tool:

- Speedrun, 2026-10-29 (`--animations off`): 19/19 passed, 573 s wall clock. Apple M1 Pro (16 GB), iPhone 17 Pro simulator (iOS 26.2).
- Maestro 2.11, 2026-10-27: 8/19 passed, 2419 s wall clock. Apple M1 Pro (16 GB), iPhone 17 Pro simulator (iOS 26.2).

| Flow | Speedrun | Maestro | Speedup |
|---|---:|---:|---:|
| A remembered account survives clearState on iOS, but not clearKeychain | 18 s | 78 s | 4.3x |
| Buy twice, with search, options, a promo code that fails once and the popups after | 70 s | 73 s ✗ (~270 s) | ~3.9x |
| Cart lines, steppers and swipe to remove | 19 s | 51 s ✗ (~98 s) | ~5.2x |
| Chat with the bot, long press and double tap a message, paste, quick replies | 23 s | 59 s ✗ (~81 s) | ~3.5x |
| Confetti, a button that turns on late, a layout shift, a busy JavaScript thread | 15 s | 70 s ✗ (~68 s) | ~4.5x |
| Dark mode, screenshots and a recording | 9 s | 45 s | 5.0x |
| Deep links to a product, a lab screen and the cart | 27 s | 43 s | 1.6x |
| Drag a slider and a card, scroll sideways, a long list with sticky headers | 39 s | 60 s ✗ (~160 s) | ~4.1x |
| Edit the profile, change settings, set a PIN, sign out | 30 s | 86 s ✗ (~137 s) | ~4.6x |
| Elements told apart by place (index, relative, parent, child) and by state | 28 s | 62 s ✗ (~105 s) | ~3.8x |
| Feed with a ticker, stories, likes, a double tap, more posts and pull to refresh | 63 s | 96 s ✗ (~338 s) | ~5.4x |
| Launch arguments, location, permissions, photos, orientation, app lifecycle, airplane mode | 28 s | 96 s | 3.4x |
| Onboarding pages, and no onboarding on the next launch | 12 s | 51 s ✗ (~50 s) | ~4.2x |
| Popups that come one after another (native modals, a sheet) | 26 s | 60 s | 2.3x |
| Scripts, env, conditions, repeat and retry | 15 s | 44 s | 2.9x |
| Sign in with a phone number and a code, a wrong one first | 20 s | 48 s | 2.4x |
| Swipes in four directions, taps at a point, single, double and long press | 12 s | 48 s | 4.0x |
| Taps on screens that never stop moving | 63 s | 1231 s ✗ (~724 s) | ~11.5x |
| Typing, keys, erasing, copy and paste, random text, a draft kept across restarts | 46 s | 107 s ✗ (~201 s) | ~4.4x |
| **All flows** | **563 s** | **2408 s** | **4.3x** |
| **Flows both passed (8)** | **155 s** | **462 s** | **3.0x** |
| **All flows, Maestro's failures estimated** | **563 s** | **~2694 s** | **~4.8x** |
| **Wall clock** | **573 s** | **2419 s** | **4.2x** |

Passed: Speedrun 19/19, Maestro 8/19. ✗: failed (its time up to the failure); ~: estimated, had Maestro finished the flow.

## Speedrun's last runs

On Apple M1 Pro (16 GB), iPhone 17 Pro simulator (iOS 26.2), `--animations off`, newest first. ▲/▼: at least 15% (and 1 s) slower/faster than the run before it.

| Flow | 10-29 12:00 |
|---|---:|
| A remembered account survives clearState on iOS, but not clearKeychain | 18 s |
| Buy twice, with search, options, a promo code that fails once and the popups after | 70 s |
| Cart lines, steppers and swipe to remove | 19 s |
| Chat with the bot, long press and double tap a message, paste, quick replies | 23 s |
| Confetti, a button that turns on late, a layout shift, a busy JavaScript thread | 15 s |
| Dark mode, screenshots and a recording | 9 s |
| Deep links to a product, a lab screen and the cart | 27 s |
| Drag a slider and a card, scroll sideways, a long list with sticky headers | 39 s |
| Edit the profile, change settings, set a PIN, sign out | 30 s |
| Elements told apart by place (index, relative, parent, child) and by state | 28 s |
| Feed with a ticker, stories, likes, a double tap, more posts and pull to refresh | 63 s |
| Launch arguments, location, permissions, photos, orientation, app lifecycle, airplane mode | 28 s |
| Onboarding pages, and no onboarding on the next launch | 12 s |
| Popups that come one after another (native modals, a sheet) | 26 s |
| Scripts, env, conditions, repeat and retry | 15 s |
| Sign in with a phone number and a code, a wrong one first | 20 s |
| Swipes in four directions, taps at a point, single, double and long press | 12 s |
| Taps on screens that never stop moving | 63 s |
| Typing, keys, erasing, copy and paste, random text, a draft kept across restarts | 46 s |
| **All flows** | 563 s |
| **Wall clock** | 573 s |
