#!/bin/bash
# Generic Python 3.11+ runner for greenbelt scripts
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT="$1"
shift
for py in python3.11 python3.12 python3.13; do
    if command -v "$py" &>/dev/null; then
        exec "$py" "$SCRIPT_DIR/$SCRIPT" "$@"
    fi
done
echo "[greenbelt] Python 3.11+ required. Install: brew install python@3.11" >&2
exit 1
