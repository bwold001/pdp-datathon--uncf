"""The Results API's answers: one measure for one class, for everyone and each group, from uncf.metrics.

The numbers come from the same metrics every Explorer page uses, so the Results API, the pages, CSV export and chat
agree. This module only picks the students for each group and turns the metric into response rows. Answers are
cached in memory, keyed on the data file's modification time, so a reload is picked up without a restart.
"""
from __future__ import annotations

from functools import lru_cache
from itertools import product

from measures.models import ALLOWED_VALUES, GroupDimension
from uncf import data, metrics
from uncf.filters import CohortQuery, listed_value, select_students
from uncf.schemas import ResultRow

GATEWAY_MEASURES = {"gateway_math", "gateway_english"}
YEAR_TWO_MEASURES = {"retention", "persistence"}
DFW_NOTE = (
    "Course enrollments of the cohort's students that ended in a D, F or withdrawal, out of those with a final grade. "
    "A numeric grade under 2.0 counts. Incomplete, audit, missing and other grades are left out."
)


def is_provisional(measure: str, cohort: str) -> bool:
    """True when a year 2 measure's class doesn't have its full second year in the data yet."""
    return measure in YEAR_TWO_MEASURES and data.is_provisional(cohort)


def groups_for(dimensions: tuple[str, ...]) -> list[dict[str, str]]:
    """Everyone ({}), then every combination of the dimensions' listed values, as the measures order them."""
    groups: list[dict[str, str]] = [{}]
    ordered = sorted(dimensions)
    if ordered:
        for values in product(*(sorted(ALLOWED_VALUES[GroupDimension(d)]) for d in ordered)):
            groups.append(dict(zip(ordered, values)))
    return groups


def members(students: dict, group: dict[str, str]) -> list[str]:
    """The students in one group: every condition holds."""
    return [sid for sid, row in students.items() if all(listed_value(d, row[d]) == value for d, value in group.items())]


def status_of(measure: str, status: str) -> str:
    """A gateway measure with no answers means the college doesn't report the requirement."""
    return "not_reported" if measure in GATEWAY_MEASURES and status == "not_yet_observable" else status


def student_rows(connection, measure: str, query: CohortQuery, groups: list[dict], students: dict) -> list[ResultRow]:
    """Rows for a measure with one answer per student."""
    answers, observable, note = metrics.measure_answers(connection, measure, query.cohort, query.retention_type)
    rows = []
    for group in groups:
        counted = metrics.rate(answers, members(students, group), observable)
        rows.append(
            ResultRow(
                group=group,
                numerator=counted["numerator"],
                denominator=counted["denominator"],
                rate=counted["rate"],
                status=status_of(measure, counted["status"]),
                n_excluded=counted["n_excluded"],
                n_out_of_scope=counted["n_out_of_scope"],
                note=note,
            )
        )
    return rows


def dfw_rows(connection, query: CohortQuery, groups: list[dict], students: dict) -> list[ResultRow]:
    """Rows for the DFW rate, which counts final grades, not students."""
    enrollments = metrics.course_rows(connection, query.cohort, students)
    rows = []
    for group in groups:
        chosen = set(members(students, group))
        part = [row for row in enrollments if row["student_id"] in chosen]
        counted = metrics.dfw(part)
        hidden = counted["den"] is None
        rows.append(
            ResultRow(
                group=group,
                numerator=counted["num"],
                denominator=counted["den"],
                rate=counted["rate"],
                status="suppressed" if hidden else "ok",
                n_excluded=None if hidden else sum(1 for row in part if row["result"] is None),
                n_out_of_scope=None if hidden else 0,
                note=DFW_NOTE,
                split=None if hidden else {key: counted["split"][key] for key in ("D", "F", "W")},
            )
        )
    return rows


@lru_cache(maxsize=1024)
def _calculate(measure: str, query: CohortQuery, dimensions: tuple[str, ...], stamp: float) -> tuple[tuple[ResultRow, ...], str]:
    """One measure for one class, its filters and grouping. stamp is only part of the cache key."""
    connection = data.open_database()
    try:
        students = select_students(connection, query)
        groups = groups_for(dimensions)
        if measure == "dfw_rate":
            rows = dfw_rows(connection, query, groups, students)
        else:
            rows = student_rows(connection, measure, query, groups, students)
        return tuple(rows), data.loaded_at(connection)
    finally:
        connection.close()


def get_results(measure: str, query: CohortQuery, dimensions: list[str]) -> tuple[list[ResultRow], str]:
    """The everyone row, then one row per group, and when the data was loaded. Dimension order doesn't matter."""
    rows, loaded = _calculate(measure, query, tuple(sorted(dimensions)), data.data_stamp())
    return list(rows), loaded


def clear_cache() -> None:
    """Forget every cached answer."""
    _calculate.cache_clear()
