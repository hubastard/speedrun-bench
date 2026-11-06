#!/usr/bin/env bash
# Compose Bench: builds and installs the app, and runs its flows (flows/) with speedrun.
#   ./bench.sh build android     a release build (signed with the debug key), installed
#   ./bench.sh test android      the flows with speedrun (pass/fail, per-flow times)
#   ./bench.sh maestro android   the flows with Maestro
# Extra arguments go to `speedrun test` / `maestro test` (flow files instead of the folder).
# A run of every flow is recorded in the benchmarks' history (../results/, see ../results.py):
# NO_RECORD=1 to leave it out. Each run's report: results/<platform>-<tool>.xml.
# The device: DEVICE=<serial>, else the first adb device. BOM=<version> builds with that
# Compose BOM (app/build.gradle.kts has the default). Needs ../../speedrun (./build.sh) and
# the Android SDK (ANDROID_HOME, or local.properties' sdk.dir).
set -euo pipefail
cd "$(dirname "$0")"

USAGE="usage: ./bench.sh build|test|maestro android [args...]"
CMD="${1:?$USAGE}"
PLATFORM="${2:?$USAGE}"
shift 2
[ "$PLATFORM" = android ] || { echo "$USAGE (Compose Bench is an Android app)"; exit 1; }
SPEEDRUN="${SPEEDRUN:-$(cd ../.. && pwd)/speedrun}"
APP_ID=dev.speedrun.composebench
now_ms() { perl -MTime::HiRes=time -e 'printf "%d\n", time*1000'; }

DEVICE="${DEVICE:-$(adb devices | awk 'NR > 1 && $2 == "device" { print $1; exit }')}"
[ -n "$DEVICE" ] || { echo "No Android device: start an emulator."; exit 1; }

case "$CMD" in
  build)
    ./gradlew -q assembleRelease ${BOM:+-Pbom="$BOM"}
    # A Gradle daemon left running takes ~1 GB, enough to starve an emulator on a 16 GB Mac.
    ./gradlew --stop > /dev/null 2>&1 || true
    adb -s "$DEVICE" install -r app/build/outputs/apk/release/app-release.apk > /dev/null
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
      python3 ../results.py record compose "$PLATFORM" "$tool" --results results --device "$DEVICE" --args "$run_args" \
        || echo "== $tool's run was not recorded"
    fi
    exit "$status"
    ;;
  *) echo "$USAGE"; exit 1 ;;
esac
