#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
for py in python3.11 python3.12 python3.13; do
    if command -v "$py" &>/dev/null; then
        exec "$py" "$SCRIPT_DIR/session_hook.py" "$@"
    fi
done
echo "[greenbelt] Python 3.11+ is required. Install: brew install python@3.11" >&2
exit 1
