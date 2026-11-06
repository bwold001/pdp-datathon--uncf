#!/usr/bin/env bash
# Runs the table file tests (CSV and Parquet) from normalized-data-model/.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pytest tests/tables -q "$@"
