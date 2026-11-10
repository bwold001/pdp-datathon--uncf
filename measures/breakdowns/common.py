"""What every page breakdown shares: the students a filter picks, small group hiding, terms and result rows.

Rates come from run_measure; this module only picks students and counts within sets of them (a course's takers,
a credit tier) with the same rule: fewer than 10 students is hidden, never shown as 0.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Iterable
from pathlib import Path

from ..calculations.dfw import grade_result
from ..calculations.sql_counts import SAFE_YEAR, filters_sql, group_value_sql, normalize
from ..models import (
    ALLOWED_VALUES,
    EVERYONE,
    SUPPRESSION_THRESHOLD,
    Cohort,
    Group,
    GroupDimension,
    Measure,
    MeasureResult,
)
from ..run_measures import DEFAULT_DATABASE, run_measure

MIN_STUDENTS = SUPPRESSION_THRESHOLD
SEASONS = ("FALL", "WINTER", "SPRING", "SUMMER")
# The student dimensions a page can filter or group by, in the cohort bar's order.
STUDENT_DIMENSIONS = (
    GroupDimension.COHORT_TERM,
    GroupDimension.ENROLLMENT_INTENSITY,
    GroupDimension.ENROLLMENT_TYPE,
    GroupDimension.PELL,
    GroupDimension.GENDER,
    GroupDimension.RACE,
    GroupDimension.ETHNICITY,
    GroupDimension.AGE_BAND,
)
# The two retention measures a page can report, by the name pages and the API use for them.
RETENTION_TYPES = {Measure.RETENTION: "school", Measure.FEDERAL_RETENTION: "federal"}
# Each dimension's values in matching form (upper case, no spaces), mapped back to the listed spelling.
LISTED = {dimension.value: {normalize(value): value for value in values} for dimension, values in ALLOWED_VALUES.items()}


def connect(database: str | Path | None = None) -> sqlite3.Connection:
    """A read-only connection with rows by column name."""
    path = Path(database) if database is not None else DEFAULT_DATABASE
    if not path.exists():
        raise FileNotFoundError(f"{path} not found. Run the loader first (see the README).")
    connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    return connection


def check_cohort(cohort: str) -> None:
    """Refuse a cohort year that isn't plain text like 2022-23, since it goes into query text."""
    if not SAFE_YEAR.match(cohort):
        raise ValueError(f"{cohort!r} is not a valid cohort year")


def students_sql() -> str:
    """One row per student per cohort, with each student dimension matched the measures' way (see sql_counts)."""
    columns = "".join(f",\n       {group_value_sql(dimension)} AS {dimension.value}" for dimension in STUDENT_DIMENSIONS)
    return f"""
SELECT s.student_id AS student_id, s.cohort AS cohort{columns}
FROM (
    SELECT cm.student_id AS student_id, cm.cohort AS cohort,
           cm.cohort_term AS cohort_term,
           cm.enrollment_intensity_first_term AS enrollment_intensity,
           cm.enrollment_type AS enrollment_type,
           cm.pell_status_first_year AS pell,
           st.gender AS gender, st.race AS race, st.ethnicity AS ethnicity, st.student_age AS age_band
    FROM cohort_membership cm
    JOIN student st ON st.student_id = cm.student_id
) s"""


def select_students(connection: sqlite3.Connection, cohort: str, filters: Group = EVERYONE) -> dict[str, sqlite3.Row]:
    """The students of one cohort year who match every filter, by id, with their (normalized) dimension values."""
    check_cohort(cohort)
    # The values are already normalized, and matching a normalized value again gives the same value, so the
    # measures' own filter clause (written against s) works on these rows too.
    where = filters_sql(filters)
    cohort_condition = f"s.cohort = '{cohort}'"
    where = f"{where} AND {cohort_condition}" if where else f"WHERE {cohort_condition}"
    rows = connection.execute(f"SELECT * FROM ({students_sql()}) s {where}").fetchall()
    return {row["student_id"]: row for row in rows}


def listed_value(dimension: str, normalized: str) -> str:
    """The listed spelling of a normalized value, e.g. FIRST-TIME -> First-time."""
    return LISTED[dimension][normalized]


def shown(count: int | None) -> int | None:
    """A count as a page may show it: groups of 1 to 9 students are hidden (None), never shown as 0."""
    if count is None or 0 < count < MIN_STUDENTS:
        return None
    return count


def share(count: int | None, total: int | None) -> float | None:
    """count / total to four places, or None when either is hidden or the total is 0."""
    if count is None or not total:
        return None
    return round(count / total, 4)


def retained_share(answers: dict[str, int | None], students: Iterable[str]) -> dict:
    """How many of these students were retained, for a breakdown (a course, a tier, a pair). Hidden under 10."""
    known = [sid for sid in students if answers.get(sid) is not None]
    if len(known) < MIN_STUDENTS:
        return {"students": None, "retained": None, "rate": None}
    back = sum(answers[sid] for sid in known)
    return {"students": len(known), "retained": back, "rate": share(back, len(known))}


def result_dict(row: MeasureResult) -> dict:
    """A run_measure row as a page shows it. Hidden numbers stay None with their status."""
    return {
        "status": row.status.value,
        "numerator": row.numerator,
        "denominator": row.denominator,
        "rate": row.metric_rate,
        "n_excluded": row.n_excluded,
        "n_out_of_scope": row.n_out_of_scope,
    }


def retention(measure: Measure, cohort: str, filters: Group, database: str | Path | None) -> dict:
    """The filtered cohort's retention by one retention measure, from run_measure, with the type it was counted by."""
    (row,) = run_measure(measure, [Cohort.of(cohort)], database=database, filters=filters)
    counted = result_dict(row)
    return {"type": RETENTION_TYPES[measure], **counted, "retained": counted["numerator"], "students": counted["denominator"]}


def check_retention(measure: Measure) -> None:
    """Refuse a measure that isn't one of the two retention measures."""
    if measure not in RETENTION_TYPES:
        raise ValueError(f"{measure.value} is not a retention measure")


# Terms -------------------------------------------------------------------------------------------------------


def next_year(year: str) -> str:
    """The academic year after this one: 2023-24 -> 2024-25."""
    start = int(year[:4]) + 1
    return f"{start}-{str(start + 1)[2:]}"


def next_main_term(term: tuple[str, str]) -> tuple[str, str]:
    """The next fall or spring term after a term. Fall and winter lead to spring; spring and summer to next fall."""
    year, season = term
    if season in ("FALL", "WINTER"):
        return (year, "SPRING")
    return (next_year(year), "FALL")


def term_label(term: tuple[str, str]) -> str:
    """A term's name: fall is in the academic year's first calendar year, the rest in its second. Fall 2023."""
    year, season = term
    calendar_year = int(year[:4]) if season == "FALL" else int(year[:4]) + 1
    return f"{season.title()} {calendar_year}"


def retention_term(cohort: str) -> tuple[str, str]:
    """The fall term federal retention looks at: the fall after the cohort's first academic year."""
    return (next_year(cohort), "FALL")


def observed_terms(connection: sqlite3.Connection) -> set[tuple[str, str]]:
    """The terms that have any course file rows at all. A later term isn't in the data yet."""
    rows = connection.execute(
        "SELECT DISTINCT t.academic_year AS year, UPPER(t.academic_term) AS season "
        "FROM course_enrollment ce JOIN term t ON t.term_id = ce.term_id"
    ).fetchall()
    return {(row["year"], row["season"]) for row in rows}


# Cohort file facts -------------------------------------------------------------------------------------------


def credential_years(connection: sqlite3.Connection, cohort: str) -> dict[str, int]:
    """For each student with a credential here, the academic year (1 is the first) it was first earned."""
    check_cohort(cohort)
    rows = connection.execute(
        "SELECT student_id, first_year_to_bachelors_at_coh AS ba, first_year_to_a_or_c_at_cohort AS ac "
        f"FROM cohort_membership WHERE cohort = '{cohort}'"
    ).fetchall()
    years = {}
    for row in rows:
        earned = [int(value) for value in (row["ba"], row["ac"]) if value]
        if earned:
            years[row["student_id"]] = min(earned)
    return years


def year_one_credits(connection: sqlite3.Connection, cohort: str) -> dict[str, tuple[float, float]]:
    """Credits attempted and earned in year 1 from the cohort file, for students with both known."""
    check_cohort(cohort)
    rows = connection.execute(
        "SELECT student_id, number_of_credits_attempted_yr_1 AS attempted, number_of_credits_earned_yr_1 AS earned "
        f"FROM cohort_membership WHERE cohort = '{cohort}'"
    ).fetchall()
    return {row["student_id"]: (row["attempted"], row["earned"]) for row in rows if row["attempted"] is not None and row["earned"] is not None}


def course_rows(connection: sqlite3.Connection, cohort: str, students: dict) -> list[dict]:
    """Every course these students took here in the cohort, with its grade result (dfw.grade_result) and the student.

    The same enrollments as the DFW measure: rows with a course, for the cohort's own students.
    """
    check_cohort(cohort)
    rows = connection.execute(
        f"""
        SELECT ce.enrollment_id AS enrollment_id, ce.student_id AS student_id,
               UPPER(TRIM(c.course_prefix)) AS prefix,
               UPPER(TRIM(c.course_prefix)) || ' ' || UPPER(TRIM(c.course_number)) AS course,
               TRIM(ce.course_name) AS name, ce.grade AS grade,
               t.academic_year AS year, UPPER(t.academic_term) AS season, t.sort_order AS sort_order,
               UPPER(TRIM(ce.math_or_english_gateway)) AS gateway, UPPER(TRIM(ce.course_type)) AS course_type
        FROM course_enrollment ce
        JOIN course c ON c.course_id = ce.course_id
        JOIN term t ON t.term_id = ce.term_id
        WHERE ce.cohort = '{cohort}'
        """
    ).fetchall()
    found = []
    for row in rows:
        student = students.get(row["student_id"])
        if student is not None:
            found.append({**dict(row), "result": grade_result(row["grade"]), "student": student})
    return found


def filter_options(cohorts: Iterable[str], cohort: str, database: str | Path | None = None) -> dict:
    """How many students entered in each cohort year, and in the chosen cohort, how many have each dimension value."""
    connection = connect(database)
    try:
        rows = connection.execute(f"SELECT * FROM ({students_sql()})").fetchall()
    finally:
        connection.close()
    per_cohort = {year: 0 for year in cohorts}
    per_value = {d.value: {value: 0 for value in ALLOWED_VALUES[d]} for d in STUDENT_DIMENSIONS}
    for row in rows:
        if row["cohort"] in per_cohort:
            per_cohort[row["cohort"]] += 1
        if row["cohort"] == cohort:
            for name, counts in per_value.items():
                counts[listed_value(name, row[name])] += 1
    return {
        "cohorts": {year: shown(count) for year, count in per_cohort.items()},
        "filters": {name: {value: shown(count) for value, count in counts.items()} for name, counts in per_value.items()},
    }
