"""Runs the shared measures (#9) and hands their rows to compare() as CountRows.

This is the only file that runs the measures, so a change to their results is fixed here. compare.py takes
only their unknown value and status names.
"""
from __future__ import annotations

from pathlib import Path

from measures.models import Cohort, GroupBy, GroupDimension, Measure, MeasureResult
from measures.run_measures import latest_load, open_database, read_sources, run_measure

from .compare import CountRow

# The gap finder's statistics need a yes or no per student. These measures count something else.
NOT_YES_OR_NO = {Measure.DFW_RATE, Measure.CREDIT_COMPLETION}


def count_rows(
    measures: list[str],
    cohorts: list[list[str]],
    group_by: list[list[str]],
    database: str | Path | None = None,
) -> list[CountRow]:
    """Run each measure for every cohort and breakdown, everyone included, as CountRows."""
    measure_list = [Measure(name) for name in measures]
    refused = [measure.value for measure in measure_list if measure in NOT_YES_OR_NO]
    if refused:
        raise ValueError(f"the gap finder only compares yes-or-no measures, so it can't use {', '.join(refused)}")
    cohort_list = [Cohort.of(*years) for years in cohorts]
    group_by_list = [GroupBy.of(*(GroupDimension(name) for name in dimensions)) for dimensions in unique(group_by)]

    # One connection for every measure, so every row comes from the same load.
    connection, opened_here = open_database(database)
    try:
        check_cohorts_have_students(connection, cohort_list)
        data_loaded_at = latest_load(read_sources(connection))
        rows = []
        for measure in measure_list:
            results = run_measure(measure, cohort_list, group_by_list, database=connection)
            rows.extend(to_count_row(result, data_loaded_at) for result in results)
    finally:
        if opened_here:
            connection.close()
    return rows


def unique(group_by: list[list[str]]) -> list[list[str]]:
    """The breakdowns with repeats removed, in the order first asked for. race x gender and gender x race are one."""
    seen = set()
    breakdowns = []
    for dimensions in group_by:
        key = frozenset(dimensions)
        if key not in seen:
            seen.add(key)
            breakdowns.append(dimensions)
    return breakdowns


def check_cohorts_have_students(connection, cohorts: list[Cohort]) -> None:
    """Refuse a cohort year with no students, which is almost always a typo or the wrong data."""
    cursor = connection.cursor()
    cursor.execute("SELECT DISTINCT cohort FROM cohort_membership")
    loaded = {row[0] for row in cursor.fetchall()}
    missing = sorted({year for cohort in cohorts for year in cohort.years} - loaded)
    if missing:
        raise ValueError(f"no students in cohort {', '.join(missing)} in the loaded data (it has {', '.join(sorted(loaded))})")


def to_count_row(result: MeasureResult, data_loaded_at: str) -> CountRow:
    """One measure result as a CountRow: the group as sorted dimensions and values, as the measures save it."""
    parts = sorted(result.group.parts, key=lambda p: p.dimension.value)
    return CountRow(
        measure=result.measure.value,
        cohort=result.cohort.label,
        group_dimensions=tuple(p.dimension.value for p in parts),
        group_values=tuple(p.value for p in parts),
        numerator=result.numerator,
        denominator=result.denominator,
        status=result.status.value,
        n_excluded=result.n_excluded,
        n_out_of_scope=result.n_out_of_scope,
        exclusion_reason=result.exclusion_reason.value if result.exclusion_reason else None,
        note=result.note,
        data_loaded_at=data_loaded_at,
    )
