#!/usr/bin/env bash
# The benchmark app (Speedrun Bench): installs or builds it, runs its flows (flows/) as
# speedrun's regression suite, and compares speedrun with Maestro on the same flows.
#   ./bench.sh install ios|android    the prebuilt app for this checkout's sources (from the
#                                     bench-app release: no Node needed), installed on the device
#   ./bench.sh build ios|android      expo prebuild, a Release build, installed on the device
#   ./bench.sh fetch ios|android      the prebuilt app into prebuilt/, not installed (fails when
#                                     none matches these sources)
#   ./bench.sh compile ios|android    the Release build into prebuilt/, not installed
#   ./bench.sh publish ios|android    builds and uploads it to the bench-app release, unless
#                                     these sources are there already (needs gh)
#   ./bench.sh hash                   the sources' hash the prebuilt apps are named after
#   ./bench.sh test ios|android       the suite with speedrun (pass/fail, per-flow times)
#   ./bench.sh compare ios|android    the suite with speedrun, then with Maestro: a table per
#                                     flow in results/<platform>.md
#   ./bench.sh maestro ios|android    the suite with Maestro only (the table takes speedrun's
#                                     last results)
#   ./bench.sh table ios|android      the table again, from the last results (RESULTS=<dir>)
# Each tool's per-command times go to results/<platform>-<tool>-debug: a flow Maestro fails
# gets an estimate of its full time (see table). A run of the whole suite is also recorded in
# the benchmarks' history (../results/, see ../results.py): NO_RECORD=1 to leave it out.
# Extra arguments go to `speedrun test` / `maestro test` (flow files instead of the folder,
# --include-tags ...). The device: DEVICE=<serial or simulator UDID>, else the first adb device
# (Android) or the booted simulator (iOS). Needs ../../speedrun (./build.sh); compare needs
# maestro; build, compile and publish need Node, and Xcode or the Android SDK.
set -euo pipefail
cd "$(dirname "$0")"

USAGE="usage: ./bench.sh install|build|fetch|compile|publish|test|maestro|compare|table ios|android [args...], or ./bench.sh hash"
CMD="${1:?$USAGE}"
PLATFORM="${2:-}"
[ "$CMD" = hash ] || { [ -n "$PLATFORM" ] || { echo "$USAGE"; exit 1; }; }
shift $(($# < 2 ? $# : 2))
SPEEDRUN="${SPEEDRUN:-$(cd ../.. && pwd)/speedrun}"
APP_ID=dev.speedrun.bench
RESULTS="${RESULTS:-results}"
mkdir -p "$RESULTS"
# Prebuilt apps: assets of the bench-app release, named after the hash of the sources.
REPO="${BENCH_REPO:-hubastard/speedrun-bench}"
RELEASE=bench-app
PREBUILT=prebuilt

now_ms() { perl -MTime::HiRes=time -e 'printf "%d\n", time*1000'; }

case "$CMD:$PLATFORM" in
  hash:* | table:ios | table:android | fetch:ios | fetch:android | compile:ios | compile:android \
    | publish:ios | publish:android) ;;
  *:ios)
    DEVICE="${DEVICE:-$(xcrun simctl list devices booted | sed -n 's/.*(\([0-9A-Fa-f-]\{36\}\)) (Booted).*/\1/p' | head -1)}"
    [ -n "$DEVICE" ] || { echo "No booted simulator: boot one (xcrun simctl boot <udid>)."; exit 1; }
    ;;
  *:android)
    DEVICE="${DEVICE:-$(adb devices | awk 'NR > 1 && $2 == "device" { print $1; exit }')}"
    [ -n "$DEVICE" ] || { echo "No Android device: start an emulator."; exit 1; }
    ;;
  *) echo "platform: ios or android"; exit 1 ;;
esac

# What the app's build depends on, hashed (a prebuilt app is named after it): not the flows.
source_hash() {
  git ls-files -z -- app.json App.tsx index.ts tsconfig.json package.json package-lock.json \
    assets modules plugins src | xargs -0 shasum -a 256 | shasum -a 256 | cut -c1-12
}

# The release asset for these sources, and the app it unpacks to in prebuilt/.
asset() {
  if [ "$PLATFORM" = ios ]; then echo "speedrun-bench-$(source_hash)-ios-simulator.zip"; else echo "speedrun-bench-$(source_hash).apk"; fi
}
app_path() {
  if [ "$PLATFORM" = ios ]; then echo "$PREBUILT/SpeedrunBench.app"; else echo "$PREBUILT/speedrun-bench.apk"; fi
}

compile() {
  [ -d node_modules ] || npm ci --no-audit --no-fund
  mkdir -p "$PREBUILT"
  if [ "$PLATFORM" = ios ]; then
    CI=1 npx expo prebuild --platform ios
    # prebuild reuses ios/ and skips pod install unless package.json's dependencies changed:
    # a module added under modules/ would be missing.
    (cd ios && pod install --silent)
    xcodebuild -workspace ios/SpeedrunBench.xcworkspace -scheme SpeedrunBench -configuration Release \
      -sdk iphonesimulator -destination 'generic/platform=iOS Simulator' -derivedDataPath ios/build -quiet
    rm -rf "$(app_path)"
    cp -R ios/build/Build/Products/Release-iphonesimulator/SpeedrunBench.app "$(app_path)"
  else
    CI=1 npx expo prebuild --platform android
    (cd android && ./gradlew -q assembleRelease)
    cp android/app/build/outputs/apk/release/app-release.apk "$(app_path)"
  fi
  source_hash > "$PREBUILT/$PLATFORM.hash"
  echo "== Built $(app_path)"
}

fetch() {
  local name hash
  name=$(asset)
  hash=$(source_hash)
  if [ -e "$(app_path)" ] && [ "$(cat "$PREBUILT/$PLATFORM.hash" 2> /dev/null)" = "$hash" ]; then
    echo "== $(app_path) matches these sources ($hash)"
    return
  fi
  mkdir -p "$PREBUILT"
  echo "== Downloading $name"
  if ! curl -fsSL "https://github.com/$REPO/releases/download/$RELEASE/$name" -o "$PREBUILT/$name.part"; then
    rm -f "$PREBUILT/$name.part"
    echo "No prebuilt app for these sources ($hash) in https://github.com/$REPO/releases/tag/$RELEASE:"
    echo "build it with ./bench.sh build $PLATFORM."
    return 1
  fi
  if [ "$PLATFORM" = ios ]; then
    rm -rf "$(app_path)"
    unzip -q "$PREBUILT/$name.part" -d "$PREBUILT"
    rm "$PREBUILT/$name.part"
  else
    mv "$PREBUILT/$name.part" "$(app_path)"
  fi
  echo "$hash" > "$PREBUILT/$PLATFORM.hash"
}

install_app() {
  if [ "$PLATFORM" = ios ]; then
    xcrun simctl install "$DEVICE" "$(app_path)"
  elif ! adb -s "$DEVICE" install -r "$(app_path)" > /dev/null 2>&1; then
    # Signed by another build's key (a local build, then a prebuilt one): replace it.
    adb -s "$DEVICE" uninstall "$APP_ID" > /dev/null 2>&1 || true
    adb -s "$DEVICE" install "$(app_path)" > /dev/null
  fi
  echo "== Installed $APP_ID on $DEVICE"
}

publish() {
  local name
  name=$(asset)
  if gh release view "$RELEASE" --repo "$REPO" --json assets --jq '.assets[].name' 2> /dev/null | grep -qxF "$name"; then
    echo "== $name is published already"
    return
  fi
  compile
  gh release view "$RELEASE" --repo "$REPO" > /dev/null 2>&1 || gh release create "$RELEASE" --repo "$REPO" \
    --prerelease --target main --title "Speedrun Bench (prebuilt)" \
    --notes "Speedrun Bench, the benchmark app (bench/app), built for an Android emulator and an iOS simulator: one asset per platform and source hash (bench/app/bench.sh hash). \`./bench.sh install android|ios\` downloads and installs the one that matches your checkout."
  if [ "$PLATFORM" = ios ]; then
    (cd "$PREBUILT" && rm -f "$name" && zip -qry "$name" SpeedrunBench.app)
  else
    cp "$(app_path)" "$PREBUILT/$name"
  fi
  gh release upload "$RELEASE" "$PREBUILT/$name" --repo "$REPO" --clobber
  rm "$PREBUILT/$name"
  echo "== Published $name"
}

# Android's three animation scales, as `settings get` prints them.
animation_scales() {
  adb -s "$DEVICE" shell 'echo $(settings get global window_animation_scale) $(settings get global transition_animation_scale) $(settings get global animator_duration_scale)' | tr -d '\r'
}

# Runs the suite with one tool; prints its wall clock. $1: speedrun or maestro.
run() {
  local tool="$1" report="$RESULTS/$PLATFORM-$1.xml" debug="$RESULTS/$PLATFORM-$1-debug"; shift
  # Android: speedrun turns animations off for its run, and puts them back as it found them
  # (speedrun issue #12). Checked on a device that has them on, as a fresh emulator does.
  local scales=""
  if [ "$PLATFORM" = android ] && [ "$tool" = speedrun ]; then scales=$(animation_scales); fi
  rm -rf "$debug"
  # The flows folder, unless a flow file or folder is given.
  local flows=(flows) arg
  FULL=1
  RUN_ARGS=
  for arg in "$@"; do
    if [ -e "$arg" ]; then flows=(); FULL=0; else RUN_ARGS="${RUN_ARGS:+$RUN_ARGS }$arg"; fi
  done
  # On iOS speedrun keeps its agent between runs: stop it, so both tools start cold.
  [ "$PLATFORM" = ios ] && "$SPEEDRUN" --stop-agent >/dev/null 2>&1 || true
  local t0 t1 status=0
  t0=$(now_ms)
  if [ "$tool" = speedrun ]; then
    "$SPEEDRUN" test --device "$DEVICE" --format junit --output "$report" \
      --debug-output "$debug" --flatten-debug-output "$@" ${flows[@]+"${flows[@]}"} || status=$?
  else
    maestro --device "$DEVICE" test --format junit --output "$report" \
      --debug-output "$debug" --flatten-debug-output "$@" ${flows[@]+"${flows[@]}"} || status=$?
  fi
  t1=$(now_ms)
  [ "$PLATFORM" = ios ] && "$SPEEDRUN" --stop-agent >/dev/null 2>&1 || true
  if [ -n "$scales" ] && [ "$(animation_scales)" != "$scales" ]; then
    echo "== speedrun left the animation scales at $(animation_scales), not $scales as it found them"
    SCALES_CHANGED=1
  fi
  echo "$((t1 - t0))" > "$RESULTS/$PLATFORM-$tool.wall"
  echo "== $tool: $(( (t1 - t0) / 1000 )) s wall clock, exit $status"
}

# The table in results/<platform>.md (../results.py app-table): a flow Maestro fails gets an
# estimate of its full time too.
table() {
  python3 ../results.py app-table "$PLATFORM" "$RESULTS"
}

# A run of the whole suite (no flow file named) goes to the benchmarks' history, and its pages
# (../results/) are written again; a run of some flows prints its table only. NO_RECORD=1: no
# record (a comparison with an older build, say).
record() {
  [ "$FULL" = 1 ] && [ -z "${NO_RECORD:-}" ] || return 0
  python3 ../results.py record app "$PLATFORM" "$1" --results "$RESULTS" --device "$DEVICE" --args "$RUN_ARGS" \
    || echo "== $1's run was not recorded"
}

case "$CMD" in
  hash) source_hash ;;
  # Not `a && b`: bash ignores set -e in a function on the left of &&, so a failed build went
  # on to install the app it built before.
  install) fetch; install_app ;;
  build) compile; install_app ;;
  fetch) fetch ;;
  compile) compile ;;
  publish) publish ;;
  test) run speedrun "$@"; table; record speedrun; [ -z "${SCALES_CHANGED:-}" ] ;;
  maestro) run maestro "$@"; table; record maestro ;;
  table) table ;;
  compare)
    run speedrun "$@"
    # Maestro draws its live view over the screen: start it on a clear one.
    if [ -t 1 ]; then printf '\033[H\033[2J'; fi
    run maestro "$@"
    table
    record speedrun
    record maestro
    ;;
  *) echo "$USAGE"; exit 1 ;;
esac
