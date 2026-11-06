#!/usr/bin/env bash
# Runs every step, from the source files to the database: map, fix, validate, load. Arguments pass
# through to python -m src.pipeline.run (try --help). Run from anywhere; it runs from
# normalized-data-model/, so give it paths from there, or absolute ones.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m src.pipeline.run "$@"
