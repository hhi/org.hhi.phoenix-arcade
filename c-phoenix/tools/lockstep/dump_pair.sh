#!/bin/bash
# dump_pair.sh <script-pad-relatief-aan-c-phoenix> <loopframes> <naam>
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CPHX="${CPHX:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
JPHX="${JPHX:-$(cd "$CPHX/../jphoenix-emulator-port" && pwd)}"
# Same default as jphoenix-emulator-port/Makefile (ROM_DIR ?= ../roms/assembled).
# This script starts Java directly instead of going through that Makefile, so
# it has to pass the ROM directory itself; without it JPhoenix falls back to
# its working directory and fails with "program.rom (No such file or directory)".
ROM_DIR="${ROM_DIR:-$(cd "$CPHX/../roms/assembled" 2>/dev/null && pwd)}"
SCRIPT="$1"; LF="$2"; NAME="$3"
REF_DUMP="${REF_DUMP:-/tmp/ref_$NAME.bin}"
PORT_DUMP="${PORT_DUMP:-/tmp/port_$NAME.bin}"
JPHX_LOG="/tmp/${NAME}-jphoenix.log"
CPHX_LOG="/tmp/${NAME}-c-phoenix.log"
case "$SCRIPT" in
  /*) SCRIPT_FOR_JPHX="$SCRIPT" ;;
  *) SCRIPT_FOR_JPHX="$CPHX/$SCRIPT" ;;
esac
JF=$(( LF * 5 / 4 + 400 ))
if [ ! -f "$ROM_DIR/program.rom" ]; then
  echo "geen program.rom in $ROM_DIR -- draai eerst 'make romprepare' vanuit de repository-root," >&2
  echo "of geef een andere map op met ROM_DIR=/pad/naar/roms" >&2
  exit 1
fi
cd "$JPHX"
if ! java -Dphoenix.inputclock=poll -Dphoenix.romdir="$ROM_DIR" \
     -Dphoenix.ramdump="$REF_DUMP" -Dphoenix.ramdump.frames=$JF \
     -cp build/classes PhoenixCoverageRunner "$SCRIPT_FOR_JPHX" /tmp/cov_$NAME $JF >"$JPHX_LOG" 2>&1; then
  echo "jphoenix-dump mislukt; zie $JPHX_LOG" >&2
  tail -n 40 "$JPHX_LOG" >&2
  exit 1
fi
cd "$CPHX"
SDL_VIDEODRIVER="${SDL_VIDEODRIVER:-dummy}" SDL_AUDIODRIVER="${SDL_AUDIODRIVER:-dummy}" \
  ./build/c-phoenix --run-frames=$LF --input-script="$SCRIPT" --ram-dump="$PORT_DUMP" --no-render >"$CPHX_LOG" 2>&1 || {
    echo "C-Phoenix-dump mislukt; zie $CPHX_LOG" >&2
    tail -n 40 "$CPHX_LOG" >&2
    exit 1
  }
echo "klaar: $NAME"
