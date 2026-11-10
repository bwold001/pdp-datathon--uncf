"""Federal (fall to fall) retention: students who took a course here in the fall term after their first academic year.

This is the IPEDS style retention rate. It reads lower than the PDP retention flag (retention.py), which counts
enrollment in any term of the next year and credentials. Two rules are still open with stakeholders, so they are
settings here: whether only first time students count, and whether a credential earned by then counts as retained.

A cohort has no answers until its next fall is in the course file, so it is not yet observable until then.
"""
from __future__ import annotations

from ..models import EVERYONE, Cohort, Counts, Group
from .sql_counts import count_in_sql
from .students import rows_sql

# Open stakeholder questions. Change them here only.
FIRST_TIME_ONLY = False  # IPEDS counts first time students only
CREDENTIAL_COUNTS = False  # a credential earned here in year 1 counts as retained

NOTE = (
    "Students in the cohort who took a course here in the fall term after their first academic year (fall to fall). "
    "Every enrollment type is counted, and a credential doesn't count as retained, until stakeholders decide."
)


def next_year_sql(year_column: str) -> str:
    """The academic year after a cohort year, in SQL: 2022-23 -> 2023-24. Runs on SQLite and PostgreSQL."""
    start = f"CAST(SUBSTR({year_column}, 1, 4) AS INTEGER)"
    return f"CAST({start} + 1 AS TEXT) || '-' || SUBSTR(CAST({start} + 2 AS TEXT), 3, 2)"


def federal_rows_sql() -> str:
    """One row per student per cohort: in scope, whether the next fall is in the data, and whether they took a course then."""
    # Students who took a course here the fall after the cohort year.
    back = f"""
LEFT JOIN (
    SELECT DISTINCT ce.student_id AS student_id, ce.cohort AS cohort
    FROM course_enrollment ce
    JOIN term t ON t.term_id = ce.term_id
    WHERE ce.course_id IS NOT NULL AND UPPER(t.academic_term) = 'FALL' AND t.academic_year = {next_year_sql('ce.cohort')}
) back ON back.student_id = cm.student_id AND back.cohort = cm.cohort"""
    # The fall terms the course file has any row for. A later fall isn't in the data yet.
    seen = """
LEFT JOIN (
    SELECT DISTINCT t.academic_year AS academic_year
    FROM course_enrollment ce
    JOIN term t ON t.term_id = ce.term_id
    WHERE UPPER(t.academic_term) = 'FALL'
) seen ON seen.academic_year = """ + next_year_sql("cm.cohort")
    in_scope = "CASE WHEN UPPER(REPLACE(cm.enrollment_type, ' ', '')) = 'FIRST-TIME' THEN 1 ELSE 0 END" if FIRST_TIME_ONLY else "1"
    retained = "back.student_id IS NOT NULL"
    if CREDENTIAL_COUNTS:
        retained += " OR cm.first_year_to_bachelors_at_coh = 1 OR cm.first_year_to_a_or_c_at_cohort = 1"
    return rows_sql(
        in_scope=in_scope,
        has_answer=f"CASE WHEN {in_scope} = 1 AND seen.academic_year IS NOT NULL THEN 1 ELSE 0 END",
        achieved=f"CASE WHEN {in_scope} = 1 AND seen.academic_year IS NOT NULL AND ({retained}) THEN 1 ELSE 0 END",
        joins=back + seen,
    )


# One row per student per cohort, with whether they have an answer and whether they were back next fall.
STUDENT_SQL = federal_rows_sql()


def count(connection, cohorts: list[Cohort], groups: list[Group], filters: Group = EVERYONE) -> dict[tuple[Cohort, Group], Counts]:
    """Count students back here next fall in the database for every cohort and group."""
    return count_in_sql(connection, STUDENT_SQL, cohorts, groups, filters)
