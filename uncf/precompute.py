"""Runs the measures once at startup and saves the rows for the API to read."""
from __future__ import annotations

import logging
import subprocess
import sys
import time
from itertools import combinations
from pathlib import Path

from measures.models import Cohort, GroupBy, GroupDimension, Measure
from measures.run_measures import DEFAULT_DATABASE, run_measure

logger = logging.getLogger(__name__)

LOADER_FOLDER = Path(__file__).parent.parent / "normalized-data-model"
COHORT_YEARS = ["2021-22", "2022-23", "2023-24", "2024-25"]
MEASURES = [Measure.RETENTION, Measure.GATEWAY_MATH, Measure.GATEWAY_ENGLISH]
# First-gen is left out for now; COURSE is a DFW-only dimension.
SKIPPED_DIMENSIONS = {GroupDimension.FIRST_GEN, GroupDimension.COURSE}


def group_bys() -> list[GroupBy]:
    """Every single dimension, then every pair of dimensions."""
    dimensions = [d for d in GroupDimension if d not in SKIPPED_DIMENSIONS]
    return [GroupBy.of(*combo) for size in (1, 2) for combo in combinations(dimensions, size)]


def ensure_data_loaded() -> None:
    """Run the data model loader if the source database is missing."""
    if DEFAULT_DATABASE.exists():
        return
    logger.info("%s is missing, running the loader", DEFAULT_DATABASE)
    subprocess.run([sys.executable, "-m", "src.loader.load"], cwd=LOADER_FOLDER, check=True)




def precompute() -> None:
    """Run every measure once and save its rows; log how long it took."""
    started = time.perf_counter()
    cohorts = [Cohort.of(year) for year in COHORT_YEARS]
    groups = group_bys()
    for measure in MEASURES:
        # One call per measure with every cohort and group: a save replaces earlier rows for the
        # same measure and cohort, so splitting the groups across calls would wipe the first ones.
        # data_loaded_at is set by run_measure to when pdp.sqlite was built, so a restart never
        # makes old data look new.
        rows = run_measure(measure, cohorts, groups, save=True)
        logger.info("%s: %d rows", measure.value, len(rows))
    logger.info("precompute took %.1f seconds", time.perf_counter() - started)


def main() -> None:
    """Startup entry point: load the data if needed, then precompute."""
    logging.basicConfig(level=logging.INFO)
    ensure_data_loaded()
    precompute()
