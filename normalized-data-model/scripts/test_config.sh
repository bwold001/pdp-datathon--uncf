#!/usr/bin/env bash
# Runs the config tests from normalized-data-model/.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pytest tests/config -q "$@"
