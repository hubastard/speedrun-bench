#!/usr/bin/env bash
# Flutter Bench: builds and installs the app, and runs its flows (flows/) with speedrun.
#   ./bench.sh build ios|android     a build for the device (Android: release APK; iOS: a
#                                    simulator build), installed on it
#   ./bench.sh test ios|android      the flows with speedrun (pass/fail, per-flow times)
#   ./bench.sh maestro ios|android   the flows with Maestro
# Extra arguments go to `speedrun test` / `maestro test` (flow files instead of the folder).
# A run of every flow is recorded in the benchmarks' history (../results/, see ../results.py):
# NO_RECORD=1 to leave it out. Each run's report: results/<platform>-<tool>.xml.
# The device: DEVICE=<serial or simulator UDID>, else the first adb device (Android) or the
# booted simulator (iOS). Needs ../../speedrun (./build.sh) and Flutter.
set -euo pipefail
cd "$(dirname "$0")"

USAGE="usage: ./bench.sh build|test|maestro ios|android [args...]"
CMD="${1:?$USAGE}"
PLATFORM="${2:?$USAGE}"
shift 2
SPEEDRUN="${SPEEDRUN:-$(cd ../.. && pwd)/speedrun}"
APP_ID=dev.speedrun.flutterbench
now_ms() { perl -MTime::HiRes=time -e 'printf "%d\n", time*1000'; }

case "$PLATFORM" in
  ios)
    DEVICE="${DEVICE:-$(xcrun simctl list devices booted | sed -n 's/.*(\([0-9A-Fa-f-]\{36\}\)) (Booted).*/\1/p' | head -1)}"
    [ -n "$DEVICE" ] || { echo "No booted simulator: boot one (xcrun simctl boot <udid>)."; exit 1; }
    ;;
  android)
    DEVICE="${DEVICE:-$(adb devices | awk 'NR > 1 && $2 == "device" { print $1; exit }')}"
    [ -n "$DEVICE" ] || { echo "No Android device: start an emulator."; exit 1; }
    ;;
  *) echo "$USAGE"; exit 1 ;;
esac

case "$CMD" in
  build)
    if [ "$PLATFORM" = ios ]; then
      flutter build ios --simulator
      xcrun simctl install "$DEVICE" build/ios/iphonesimulator/Runner.app
    else
      flutter build apk --release
      # A Gradle daemon left running takes ~1 GB, enough to starve an emulator on a 16 GB Mac.
      (cd android && ./gradlew --stop > /dev/null 2>&1) || true
      adb -s "$DEVICE" install -r build/app/outputs/flutter-apk/app-release.apk > /dev/null
    fi
    echo "== Installed $APP_ID on $DEVICE"
    ;;
  test | maestro)
    tool=speedrun
    [ "$CMD" = maestro ] && tool=maestro
    # The flows folder, unless a flow file or folder is given.
    full=1
    run_args=
    for arg in "$@"; do
      if [ -e "$arg" ]; then full=0; else run_args="${run_args:+$run_args }$arg"; fi
    done
    [ "$full" = 0 ] || set -- "$@" flows
    mkdir -p results
    t0=$(now_ms)
    status=0
    if [ "$tool" = speedrun ]; then
      "$SPEEDRUN" test --device "$DEVICE" --format junit --output "results/$PLATFORM-$tool.xml" "$@" || status=$?
    else
      maestro --device "$DEVICE" test --format junit --output "results/$PLATFORM-$tool.xml" "$@" || status=$?
    fi
    echo "$(( $(now_ms) - t0 ))" > "results/$PLATFORM-$tool.wall"
    if [ "$full" = 1 ] && [ -z "${NO_RECORD:-}" ]; then
      python3 ../results.py record flutter "$PLATFORM" "$tool" --results results --device "$DEVICE" --args "$run_args" \
        || echo "== $tool's run was not recorded"
    fi
    exit "$status"
    ;;
  *) echo "$USAGE"; exit 1 ;;
esac
