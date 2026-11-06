# Speedrun's benchmarks and test apps

The apps, flows and scripts [Speedrun](https://github.com/hubastard/speedrun) is tested and
measured against. Speedrun's repository has this one as its `bench/` folder (a git submodule):
clone Speedrun with `git clone --recursive`, or run `git submodule update --init` in a
clone. The scripts find `speedrun` there (`../../speedrun`); outside a Speedrun checkout, set
`SPEEDRUN` to its path.

| Folder | |
|---|---|
| [`app/`](app) | **Speedrun Bench**, a React Native (Expo) app built to trip up UI test tools, and its 21 flows: Speedrun's regression suite on Android and iOS, and its benchmark against Maestro. |
| [`flutter/`](flutter) | **Flutter Bench**, a Flutter app with the Flutter patterns UI test tools trip on, and its 8 flows, on Android and iOS. |
| [`compose/`](compose) | **Compose Bench**, a Jetpack Compose app with the Compose patterns UI test tools trip on, and its 5 flows, on Android. |
| [`journey/`](journey) | One user journey on Speedrun Bench with each black-box test tool: Speedrun, Maestro, Appium, maestro-runner, Argent, XCUITest. |
| [`web/`](web) | The web benchmark: Speedrun, Playwright, Cypress and Maestro on TodoMVC and Cypress's Real World App, in Chrome and Firefox. |
| [`agents/`](agents) | AI agents trying out a feature through each tool's MCP server. |
| [`settings/`](settings) | A 15-step flow on Android's and iOS's own Settings app. |
| [`results/`](results) | **Every benchmark's latest results**, and Speedrun's last runs of each, written by [`results.py`](results.py). |

## Results

Every full run of a benchmark (`app/bench.sh test|maestro|compare`, `flutter/bench.sh
test|maestro` and `compose/bench.sh test|maestro` without flow files, `journey/run.sh`,
`web/run.sh`) adds its times to [`results/history.jsonl`](results/history.jsonl), and
`results.py` writes
[`results/`](results)'s pages again from it: a summary, and a page per benchmark with each
flow's time, the change since Speedrun's run before, and Speedrun's last runs side by side, so a
run that got slower shows. Commit `results/` with the rest. `NO_RECORD=1` leaves a run out (a
comparison with an older build, say); `BENCH_RESULTS=<folder>` records elsewhere.

The READMEs' numbers (this repository's and Speedrun's) are not written by a run: they take the
latest results when Speedrun ships a version (`./results.py readme`, which writes the tables
between `<!-- results:NAME -->` markers again). Speedrun's CI records its own runs, a row per
push to `main`, on Speedrun's
[`bench-history` branch](https://github.com/hubastard/speedrun/tree/bench-history).

Speedrun Bench's prebuilt builds (an Android emulator's APK, an iOS simulator's app) are on
this repository's [`bench-app` release](https://github.com/hubastard/speedrun-bench/releases/tag/bench-app),
named after their sources' hash (`app/bench.sh hash`). `.github/workflows/bench-app.yml`
publishes them when the sources change, and Speedrun's CI downloads them (`bench.sh fetch`)
instead of building the app.

These folders are kept apart from Speedrun's code: their dependencies (Expo and React Native,
Appium, Playwright, Cypress, the Real World App's) are only for testing and measuring, and none
of them ships in `speedrun`.
