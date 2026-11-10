"""The Results API's answers: one measure for one class, for everyone and each group, from run_measure.

Every number is run_measure's row, with the cohort bar's filters applied, so the Results API, the Explorer pages,
CSV export and chat agree. This module only turns the rows into the response shape. Answers are cached in memory,
keyed on the data file's modification time, so a reload is picked up without a restart.
"""
from __future__ import annotations

from functools import lru_cache

from api import data
from api.filters import CohortQuery
from api.schemas import ResultRow
from measures.models import Cohort, GroupBy, GroupDimension, Measure, MeasureResult
from measures.run_measures import run_measure

GATEWAY_MEASURES = {"gateway_math", "gateway_english"}
YEAR_TWO_MEASURES = {"retention", "persistence"}


def is_provisional(measure: str, cohort: str) -> bool:
    """True when a year 2 measure's class doesn't have its full second year in the data yet."""
    return measure in YEAR_TWO_MEASURES and data.is_provisional(cohort)


def measure_for(measure: str, query: CohortQuery) -> Measure:
    """The measure to run: retention follows the query's retention type (school or federal)."""
    return query.retention_measure if measure == "retention" else Measure(measure)


def status_of(measure: str, row: MeasureResult) -> str:
    """A gateway measure with no answers means the college doesn't report the requirement."""
    if measure in GATEWAY_MEASURES and row.status.value == "not_yet_observable":
        return "not_reported"
    return row.status.value


def to_row(measure: str, row: MeasureResult) -> ResultRow:
    """One run_measure row as a response row."""
    return ResultRow(
        group={part.dimension.value: part.value for part in sorted(row.group.parts, key=lambda p: p.dimension.value)},
        numerator=row.numerator,
        denominator=row.denominator,
        rate=row.metric_rate,
        status=status_of(measure, row),
        n_excluded=row.n_excluded,
        n_out_of_scope=row.n_out_of_scope,
        note=row.note,
        split=row.split,
    )


@lru_cache(maxsize=1024)
def _calculate(measure: str, query: CohortQuery, dimensions: tuple[str, ...], stamp: float) -> tuple[tuple[ResultRow, ...], str]:
    """One measure for one class, its filters and grouping. stamp is only part of the cache key."""
    group_by = [GroupBy.of(*(GroupDimension(d) for d in dimensions))] if dimensions else None
    rows = run_measure(measure_for(measure, query), [Cohort.of(query.cohort)], group_by, database=data.data_path(), filters=query.as_group())
    return tuple(to_row(measure, row) for row in rows), data.loaded_at()


def get_results(measure: str, query: CohortQuery, dimensions: list[str]) -> tuple[list[ResultRow], str]:
    """The everyone row, then one row per group, and when the data was loaded. Dimension order doesn't matter."""
    rows, loaded = _calculate(measure, query, tuple(sorted(dimensions)), data.data_stamp())
    return list(rows), loaded


def clear_cache() -> None:
    """Forget every cached answer."""
    _calculate.cache_clear()
