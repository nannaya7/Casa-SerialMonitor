#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

PYTHON_EXE="python3"
if [ -x ".venv/bin/python" ]; then
  PYTHON_EXE=".venv/bin/python"
fi

if [ "${1:-}" = "--check" ]; then
  echo "Python command: \"$PYTHON_EXE\""
  exit 0
fi

"$PYTHON_EXE" main.py
