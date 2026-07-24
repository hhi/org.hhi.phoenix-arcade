#!/bin/bash
# dump_pair.sh <script-pad-relatief-aan-c-phoenix> <loopframes> <naam>
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CPHX="${CPHX:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
JPHX="${JPHX:-$(cd "$CPHX/../jphoenix-emulator-port" && pwd)}"
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
cd "$JPHX"
if ! java -Dphoenix.inputclock=poll -Dphoenix.ramdump="$REF_DUMP" -Dphoenix.ramdump.frames=$JF \
     -cp build/classes PhoenixCoverageRunner "$SCRIPT_FOR_JPHX" /tmp/cov_$NAME $JF >"$JPHX_LOG" 2>&1; then
  echo "jphoenix-dump mislukt; zie $JPHX_LOG" >&2
  tail -n 40 "$JPHX_LOG" >&2
  exit 1
fi
cd "$CPHX"
SDL_VIDEODRIVER="${SDL_VIDEODRIVER:-dummy}" SDL_AUDIODRIVER="${SDL_AUDIODRIVER:-dummy}" \
  ./c-phoenix --run-frames=$LF --input-script="$SCRIPT" --ram-dump="$PORT_DUMP" --no-render >"$CPHX_LOG" 2>&1 || {
    echo "C-Phoenix-dump mislukt; zie $CPHX_LOG" >&2
    tail -n 40 "$CPHX_LOG" >&2
    exit 1
  }
echo "klaar: $NAME"
