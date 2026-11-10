"""Calculates results per request with the measures package. Nothing is saved.

The API calls get_results(); the measures package reads the normalized data (pdp.sqlite) and does the counting.
Answers are cached in memory, keyed on the data file's modification time, so a reload is picked up on the
next request without a restart.
"""
from __future__ import annotations

import sqlite3
from functools import lru_cache
from pathlib import Path

from measures.models import Cohort, GroupBy, GroupDimension, Measure, MeasureResult
from measures.run_measures import DEFAULT_DATABASE, run_measure

from api.schemas import ResultRow

GATEWAY_MEASURES = {"gateway_math", "gateway_english"}
YEAR_TWO_MEASURES = {"retention", "persistence"}
# Classes whose second academic year is only partly in the course file. Matches the Explorer's own list;
# move it to config if a school's data needs a different one.
PROVISIONAL_COHORTS = {"2024-25"}


class DataMissing(Exception):
    """The normalized data isn't loaded yet: run `python -m api load`."""


def data_path() -> Path:
    """The normalized data file to read. A function, so tests can point it somewhere else."""
    return DEFAULT_DATABASE


def _data_stamp() -> float:
    """The data file's modification time, or raise DataMissing."""
    path = data_path()
    if not path.exists():
        raise DataMissing(f"{path} does not exist. Run: python -m api load")
    return path.stat().st_mtime


def loaded_at() -> str:
    """When the source data was loaded: the latest load time of the files in it."""
    _data_stamp()
    connection = sqlite3.connect(f"file:{data_path()}?mode=ro", uri=True)
    try:
        (value,) = connection.execute("SELECT MAX(loaded_at) FROM data_provider").fetchone()
    finally:
        connection.close()
    return value or "unknown"


def is_provisional(measure: str, cohort: str) -> bool:
    """True when a year-2 measure's class doesn't have its full second year in the data yet."""
    return measure in YEAR_TWO_MEASURES and cohort in PROVISIONAL_COHORTS


def _status(measure: str, result: MeasureResult) -> str:
    """The row's status. A gateway measure with no answers means the college doesn't report the requirement."""
    status = result.status.value
    if measure in GATEWAY_MEASURES and status == "not_yet_observable":
        return "not_reported"
    return status


def _to_row(measure: str, result: MeasureResult) -> ResultRow:
    """Turn one measures-package result into an API row."""
    parts = sorted(result.group.parts, key=lambda part: part.dimension.value)
    return ResultRow(
        group={part.dimension.value: part.value for part in parts},
        numerator=result.numerator,
        denominator=result.denominator,
        rate=result.metric_rate,
        status=_status(measure, result),
        n_excluded=result.n_excluded,
        n_out_of_scope=result.n_out_of_scope,
        note=result.note,
    )


@lru_cache(maxsize=1024)
def _calculate(measure: str, cohort: str, dimensions: tuple[str, ...], stamp: float) -> tuple[ResultRow, ...]:
    """Run one measure for one class and grouping. stamp is only part of the cache key."""
    group_by = [GroupBy.of(*(GroupDimension(d) for d in dimensions))] if dimensions else None
    results = run_measure(Measure(measure), [Cohort.of(cohort)], group_by, database=data_path())
    return tuple(_to_row(measure, result) for result in results)


def get_results(measure: str, cohort: str, dimensions: list[str]) -> list[ResultRow]:
    """The everyone row, then one row per group. Dimension order doesn't matter."""
    return list(_calculate(measure, cohort, tuple(sorted(dimensions)), _data_stamp()))


def clear_cache() -> None:
    """Forget every cached answer."""
    _calculate.cache_clear()
