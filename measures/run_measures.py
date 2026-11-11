"""Runs a measure and returns its result rows.

Each measure's calculation lives in its own file in calculations/ and counts in SQL or in Python. This file
builds the groups, asks the measure for its counts, hides small groups, works out the rate and checks the rows.

The equity gap finder (#26) will call run_measure, so keep its inputs and rows stable.
"""
from __future__ import annotations

import logging
import sqlite3
from itertools import product
from pathlib import Path

from .calculations import (
    credit_completion,
    dfw,
    federal_retention,
    gateway_english,
    gateway_math,
    persistence,
    retention,
)
from .calculations.sql_counts import SAFE_YEAR as SAFE_COHORT
from .calculations.sql_counts import as_number
from .models import (
    ALLOWED_VALUES,
    EVERYONE,
    OPEN_DIMENSIONS,
    SUPPRESSION_THRESHOLD as SUPPRESSION_THRESHOLD,
    Cohort,
    Counts,
    Group,
    GroupBy,
    GroupDimension,
    Measure,
    MeasureResult,
    Status,
    check_unique,
)
from .save_results import RESULTS_DATABASE, save_results
from .disclosure import DASHBOARD_V1

logger = logging.getLogger(__name__)

# Where the loader writes its SQLite database.
DEFAULT_DATABASE = Path(__file__).parent.parent / "normalized-data-model" / "output" / "pdp.sqlite"

# Add a measure by writing its file in calculations/ and listing it here.
MEASURES = {
    Measure.RETENTION: retention,
    Measure.FEDERAL_RETENTION: federal_retention,
    Measure.PERSISTENCE: persistence,
    Measure.GATEWAY_MATH: gateway_math,
    Measure.GATEWAY_ENGLISH: gateway_english,
    Measure.DFW_RATE: dfw,
    Measure.CREDIT_COMPLETION: credit_completion,
}


def run_measure(
    measure: Measure,
    cohorts: list[Cohort],
    group_by: list[GroupBy] | None = None,
    database: str | Path | None = None,
    save: bool = False,
    filters: Group = EVERYONE,
) -> list[MeasureResult]:
    """Return one row per cohort and group: everyone, plus every group asked for in group_by.

    database is the loaded SQLite file to read, or an open connection (for PostgreSQL). It defaults to
    the loader's file. save=True also writes the rows to the results database (see save_results.py).
    filters counts only the students who match every condition, e.g. Pell students; "everyone" then means
    everyone who matches. Filtered rows aren't saved, since the results table has no column for the filters.
    """
    if measure not in MEASURES:
        raise NotImplementedError(f"{measure.value} is not written yet")
    if not cohorts:
        raise ValueError("cohorts needs at least one Cohort")
    if save and filters.parts:
        raise ValueError("filtered results can't be saved: the results table has no column for the filters")
    calculation = MEASURES[measure]
    check_open_dimensions(measure, calculation, group_by or [])
    check_open_dimensions(measure, calculation, [GroupBy.of(part.dimension) for part in filters.parts])

    connection, opened_here = open_database(database)
    try:
        groups = groups_for(group_by or [], read_open_values(connection, calculation, cohorts, group_by or []))
        all_counts = calculation.count(connection, cohorts, groups, filters)
        sources = read_sources(connection)
    finally:
        if opened_here:
            connection.close()

    results = []
    for cohort in cohorts:
        for group in groups:
            results.append(build_result(measure, cohort, group, all_counts[(cohort, group)], calculation.NOTE))
    check_unique(results)
    loaded_at = latest_load(sources)
    log_run(measure, cohorts, group_by or [], results, sources, describe_database(database))
    if save:
        save_results(results, loaded_at)
        logger.info("%s: saved %d rows to %s", measure.value, len(results), RESULTS_DATABASE)
    return results


def read_answers(measure: Measure, cohort: str, database: str | Path | None = None) -> tuple[dict[str, int | float | None], bool]:
    """Each in scope student's answer to a student measure for one cohort year, and whether the cohort has answers yet.

    The answer is 1 or 0 (or a ratio, for credit completion), or None when the student can't be counted. A student
    missing from the result is outside the measure. The page breakdowns use this to count a measure among their
    own sets of students, such as the students who passed a course. DFW counts enrollments, so it has no answers.
    """
    if measure == Measure.DFW_RATE:
        raise ValueError("dfw_rate counts course enrollments, not students, so it has no per student answers")
    if not SAFE_COHORT.match(cohort):
        raise ValueError(f"{cohort!r} is not a valid cohort year")
    connection, opened_here = open_database(database)
    try:
        cursor = connection.cursor()
        cursor.execute(
            f"WITH students AS ({MEASURES[measure].STUDENT_SQL}) "
            f"SELECT student_id, in_scope, has_answer, achieved FROM students WHERE cohort = '{cohort}'"
        )
        rows = cursor.fetchall()
    finally:
        if opened_here:
            connection.close()
    answers = {}
    for student_id, in_scope, has_answer, achieved in rows:
        if int(in_scope):
            answers[student_id] = as_number(achieved) if int(has_answer) else None
    return answers, any(value is not None for value in answers.values())


def open_database(database: str | Path | None):
    """Return (connection, whether we opened it) for a SQLite file path, a connection, or the default file."""
    if database is not None and not isinstance(database, (str, Path)):
        return database, False
    path = Path(database) if database is not None else DEFAULT_DATABASE
    if not path.exists():
        raise FileNotFoundError(f"{path} not found. Run the loader first (see the README).")
    connection = sqlite3.connect(f"{path.resolve().as_uri()}?mode=ro", uri=True)
    connection.execute("BEGIN")
    return connection, True


def read_sources(connection) -> list[tuple]:
    """Which files the loaded data came from: source file, SHA-256 and load time."""
    cursor = connection.cursor()
    cursor.execute("SELECT source_file, file_sha256, loaded_at FROM data_provider ORDER BY provider_id")
    return cursor.fetchall()


def describe_database(database: str | Path | None) -> str:
    """Where the data came from, for the log."""
    if database is None:
        return DEFAULT_DATABASE.as_posix()
    if isinstance(database, (str, Path)):
        return Path(database).as_posix()
    return "an open connection"


def latest_load(sources: list[tuple]) -> str:
    """When the data was last loaded, or 'unknown' if nothing says."""
    return max((source[2] for source in sources), default="unknown")


def log_run(measure: Measure, cohorts: list[Cohort], group_by: list[GroupBy], results: list[MeasureResult], sources: list[tuple], database: str) -> None:
    """Log one summary of the run, and warn about what a reader of the numbers should know."""
    hidden = [r for r in results if r.suppressed]
    loaded_at = latest_load(sources)
    cohort_names = ", ".join(c.label for c in cohorts)
    group_names = ", ".join(" x ".join(sorted(d.value for d in g.dimensions)) for g in group_by) or "none"
    logger.info(
        "%s: read %s. cohorts [%s], grouped by [%s]: %d rows, %d shown, %d hidden. Data loaded %s from %d files.",
        measure.value, database, cohort_names, group_names, len(results), len(results) - len(hidden), len(hidden), loaded_at, len(sources),
    )
    for source_file, sha256, _ in sources:
        logger.debug("%s: data file %s sha256 %s", measure.value, source_file, sha256)

    too_new = sorted({r.cohort.label for r in results if r.status == Status.NOT_YET_OBSERVABLE})
    for label in too_new:
        logger.warning("%s: cohort %s has no answers yet, so all its rows are hidden.", measure.value, label)
    if results and len(hidden) == len(results):
        logger.warning("%s: every row is hidden. Check the cohorts and that the data is loaded.", measure.value)


def check_open_dimensions(measure: Measure, calculation, group_by: list[GroupBy]) -> None:
    """Refuse a dimension whose values come from the data when the measure doesn't support it."""
    supported = getattr(calculation, "SUPPORTED_OPEN_DIMENSIONS", frozenset())
    for entry in group_by:
        for dimension in entry.dimensions:
            if dimension in OPEN_DIMENSIONS and dimension not in supported:
                raise ValueError(f"{measure.value} can't be grouped by {dimension.value}")


def read_open_values(connection, calculation, cohorts: list[Cohort], group_by: list[GroupBy]) -> dict[GroupDimension, list[str]]:
    """The values in the data for each open dimension asked for, such as every course taught in the cohorts."""
    wanted = {d for entry in group_by for d in entry.dimensions if d in OPEN_DIMENSIONS}
    return {dimension: calculation.open_values(connection, dimension, cohorts) for dimension in wanted}


def groups_for(group_by: list[GroupBy], open_values: dict[GroupDimension, list[str]] | None = None) -> list[Group]:
    """Everyone, plus every combination of values for each GroupBy. open_values has the values found in the data."""
    open_values = open_values or {}
    groups = [EVERYONE]
    for entry in group_by:
        dimensions = sorted(entry.dimensions, key=lambda d: d.value)
        value_choices = [open_values[d] if d in OPEN_DIMENSIONS else sorted(ALLOWED_VALUES[d]) for d in dimensions]
        for values in product(*value_choices):
            groups.append(Group.of(*zip(dimensions, values)))
    return groups


def build_result(measure: Measure, cohort: Cohort, group: Group, counts: Counts, note: str) -> MeasureResult:
    """Turn counts into a result row, hiding the group if its cohort isn't observable yet or it has too few students."""
    if counts.not_yet_observable:
        return hidden_result(measure, cohort, group, Status.NOT_YET_OBSERVABLE, note)
    if not DASHBOARD_V1.sample_visible(counts.n_students):
        return hidden_result(measure, cohort, group, Status.SUPPRESSED, note)

    return MeasureResult(
        measure=measure,
        cohort=cohort,
        group=group,
        numerator=counts.numerator,
        denominator=counts.denominator,
        metric_rate=round(counts.numerator / counts.denominator, 4),
        status=Status.OK,
        n_excluded=counts.n_excluded,
        n_out_of_scope=counts.n_out_of_scope,
        exclusion_reason=counts.exclusion_reason,
        note=note,
        exclusions=dict(counts.exclusions),
        split=dict(counts.split) if counts.split is not None else None,
        n_students=counts.n_students,
    )


def hidden_result(measure: Measure, cohort: Cohort, group: Group, status: Status, note: str) -> MeasureResult:
    """A row with no numbers: the group is too small, or its cohort isn't observable yet."""
    return MeasureResult(
        measure=measure,
        cohort=cohort,
        group=group,
        numerator=None,
        denominator=None,
        metric_rate=None,
        status=status,
        n_excluded=None,
        n_out_of_scope=None,
        exclusion_reason=None,
        note=note,
    )
