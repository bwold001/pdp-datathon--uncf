"""One measure split by group, for GET /measures/{measure}: the everyone row, then one row per group.

Every number is run_measure's row, with the cohort bar's filters applied, so this route, the Explorer pages,
CSV export and chat agree. This module only picks the measure and turns the rows into response rows. Answers are
cached in memory, keyed on the data file's modification time, so a reload is picked up without a restart.
"""
from __future__ import annotations

from functools import lru_cache

from api import data
from api.filters import CohortQuery
from api.schemas import GroupRow
from measures.models import Measure, MeasureResult
from measures import service as measures_service
from measures.breakdowns.common import page_source
from measures.disclosure import DASHBOARD_V1

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
    return DASHBOARD_V1.dashboard_status(measure, row.status.value)


def to_row(measure: str, row: MeasureResult) -> GroupRow:
    """One run_measure row as a response row."""
    return GroupRow(
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
def _calculate(measure: str, query: CohortQuery, dimensions: tuple[str, ...], stamp: float) -> tuple[tuple[GroupRow, ...], str]:
    """One measure for one class, its filters and grouping. stamp is only part of the cache key."""
    operation_id = measures_service.operation_for_measure(measure)
    parameters = {"cohort": query.cohort, "filters": query.as_dict(), "group_by": dimensions}
    if measure == "retention":
        parameters["retention_type"] = query.retention_type
    with page_source(data.data_path()) as snapshot:
        rows = measures_service.execute(operation_id, parameters, snapshot)
        loaded_at = data.loaded_at(snapshot.named)
    return tuple(to_row(measure, row) for row in rows), loaded_at


def measure_by_group(measure: str, query: CohortQuery, dimensions: list[str]) -> tuple[list[GroupRow], str]:
    """The everyone row, then one row per group, and when the data was loaded. Dimension order doesn't matter."""
    rows, loaded = _calculate(measure, query, tuple(sorted(dimensions)), data.data_stamp())
    return list(rows), loaded


def clear_cache() -> None:
    """Forget every cached answer."""
    _calculate.cache_clear()
