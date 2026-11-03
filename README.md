# Speedrun's benchmarks and test apps

The apps, flows and scripts [Speedrun](https://github.com/hubastard/speedrun) is tested and
measured against. Speedrun's repository has this one as its `bench/` folder (a git submodule):
clone Speedrun with `git clone --recursive`, or run `git submodule update --init` in a
clone. The scripts find `speedrun` there (`../../speedrun`); outside a Speedrun checkout, set
`SPEEDRUN` to its path.

| Folder | |
|---|---|
| [`app/`](app) | **Speedrun Bench**, a React Native (Expo) app built to trip up UI test tools, and its 20 flows: Speedrun's regression suite on Android and iOS, and its benchmark against Maestro. |
| [`journey/`](journey) | One user journey on Speedrun Bench with each black-box test tool: Speedrun, Maestro, Appium, maestro-runner, Argent, XCUITest. |
| [`web/`](web) | The web benchmark: Speedrun, Playwright, Cypress and Maestro on TodoMVC and Cypress's Real World App, in Chrome and Firefox. |
| [`agents/`](agents) | AI agents trying out a feature through each tool's MCP server. |
| [`settings/`](settings) | A 15-step flow on Android's and iOS's own Settings app. |

Speedrun Bench's prebuilt builds (an Android emulator's APK, an iOS simulator's app) are on
this repository's [`bench-app` release](https://github.com/hubastard/speedrun-bench/releases/tag/bench-app),
named after their sources' hash (`app/bench.sh hash`). `.github/workflows/bench-app.yml`
publishes them when the sources change, and Speedrun's CI downloads them (`bench.sh fetch`)
instead of building the app.

These folders are kept apart from Speedrun's code: their dependencies (Expo and React Native,
Appium, Playwright, Cypress, the Real World App's) are only for testing and measuring, and none
of them ships in `speedrun`.
