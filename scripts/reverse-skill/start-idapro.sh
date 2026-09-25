#!/usr/bin/env bash
# start-idapro.sh — launch IDA Pro so the idalib MCP plugin listens on the
# loopback service port declared in bootstrap-manifest.json (capability: idapro).
#
# Usage:
#   bash start-idapro.sh --target <file> [--port 13337] [--gui] [--timeout 60]
#
# Exit codes:
#   0  port already listening, or IDA launched and the port came up
#   1  IDA not found, or no target supplied
#   2  IDA launched but the service port never came up

set -euo pipefail

TARGET=""
PORT=13337
USE_GUI=false
TIMEOUT=60

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target)  TARGET="$2"; shift 2 ;;
    --port)    PORT="$2"; shift 2 ;;
    --timeout) TIMEOUT="$2"; shift 2 ;;
    --gui)     USE_GUI=true; shift ;;
    -*) echo "Unknown option: $1" >&2; exit 1 ;;
    *)  TARGET="$1"; shift ;;
  esac
done

port_open() {
  python3 - "$1" <<'PY' >/dev/null 2>&1
import socket, sys
s = socket.socket()
s.settimeout(1.0)
try:
    s.connect(('127.0.0.1', int(sys.argv[1])))
    sys.exit(0)
except Exception:
    sys.exit(1)
finally:
    s.close()
PY
}

if port_open "$PORT"; then
  echo "idapro service already listening on 127.0.0.1:$PORT"
  exit 0
fi

EXE_NAME="idat64"
$USE_GUI && EXE_NAME="ida64"

CANDIDATES=()
[[ -n "${IDA_HOME:-}" ]] && CANDIDATES+=("$IDA_HOME/$EXE_NAME")
CANDIDATES+=(
  "/c/Program Files/IDA Professional 9.0/$EXE_NAME"
  "/c/Program Files/IDA Professional 9.4/$EXE_NAME"
  "/c/Program Files/IDA Pro 9.4/$EXE_NAME"
  "/c/Program Files/IDA Pro 9.0/$EXE_NAME"
  "/opt/ida/$EXE_NAME"
  "$HOME/ida/$EXE_NAME"
)

EXE=""
for candidate in "${CANDIDATES[@]}"; do
  if [[ -f "$candidate" ]]; then EXE="$candidate"; break; fi
done

if [[ -z "$EXE" ]]; then
  echo "WARN: IDA not found. Looked for $EXE_NAME in: ${CANDIDATES[*]}" >&2
  echo "WARN: Set IDA_HOME to your IDA install directory." >&2
  exit 1
fi

if [[ -z "$TARGET" ]]; then
  echo "WARN: no target supplied. IDA needs a target open before the MCP plugin listens on port $PORT." >&2
  echo "WARN: re-run with: start-idapro.sh --target <path-to-binary>" >&2
  exit 1
fi

if [[ ! -f "$TARGET" ]]; then
  echo "WARN: target does not exist: $TARGET" >&2
  exit 1
fi

echo "Launching $EXE on $TARGET (expect MCP on 127.0.0.1:$PORT)"
if $USE_GUI; then
  "$EXE" "$TARGET" >/dev/null 2>&1 &
else
  # -A autonomous (no dialogs), -c discard any stale database.
  "$EXE" -A -c "$TARGET" >/dev/null 2>&1 &
fi

deadline=$(( $(date +%s) + TIMEOUT ))
while [[ $(date +%s) -lt $deadline ]]; do
  if port_open "$PORT"; then
    echo "idapro service is listening on 127.0.0.1:$PORT"
    exit 0
  fi
  sleep 2
done

echo "WARN: IDA started but nothing is listening on 127.0.0.1:$PORT after ${TIMEOUT}s." >&2
echo "WARN: Open a target in IDA and check its Output window for the [MCP] port= line." >&2
exit 2
