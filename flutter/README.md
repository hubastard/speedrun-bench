# Flutter Bench

A Flutter app with the Flutter patterns UI test tools trip on, one screen each, and the
flows that test Speedrun on it (`flows/`). Speedrun Bench (`../app`) does the same for React
Native.

| Screen | What it has |
|---|---|
| Sign in | Fields tagged with `Semantics(identifier:)` (what `id:` selects), a validation error, a password field, a checkbox tile, a loading veil over the form |
| Feed | A lazy list whose rows merge their texts into one label, a pushed screen with a Hero, an icon button known by its tooltip, pull to refresh |
| Popups | A dialog, a modal bottom sheet with a long list, a snack bar's action, a popup menu, a dropdown menu |
| Controls | Switch, checkbox, slider, segmented button, a long press, a target that takes both taps and double taps |
| Pager | A `PageView` turned by a swipe and by its button, tabs that swipe (`TabBarView`) |
| Keyboard | A form longer than the screen: fields under the keyboard, a multiline field, a number field |
| Motion | A progress bar that never stops, a late result, items animated into a list, a tap that blocks the UI thread |
| Navigation | A bottom navigation bar, a drawer, a nested screen left with the system back |

## Run

```sh
./bench.sh build android   # flutter build apk --release, installed on the first adb device
./bench.sh test android    # the flows with ../../speedrun
./bench.sh build ios       # a simulator build, installed on the booted simulator
./bench.sh test ios
```

## Results

Each flow's time with Speedrun, from [`../results`](../results), written again on every full
run (where Speedrun's last runs are too); this README takes them when Speedrun ships a version.

<!-- results:flutter -->
<!-- /results:flutter -->

## What Flutter's tree looks like to a flow

- **A row's texts are one label.** A `ListTile` with a leading avatar, a title and a subtitle
  is one element whose text is `"2\nArticle 2\nBy author 2"`. Text matching is a full match
  (line breaks may stand for spaces), so `Article 2` does not match it: write `.*Article 2.*`.
- **A tab's label says where it is.** `Tab(text: 'Sent')` reads `"Sent\nTab 2 of 3"`: tap
  it with `"Sent.*"`.
- **`id:` is `Semantics(identifier:)`.** A `Key` does not reach accessibility.
- **`TabBarView` turns only past half its width.** A swipe from an element's center to the
  screen's edge (`swipe: from: ... direction: LEFT`) covers 40% of the screen and the tab
  springs back: swipe across the screen (`start: 90%, 75%` to `end: 10%, 75%`).
