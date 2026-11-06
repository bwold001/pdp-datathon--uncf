"""Retention: students enrolled again in the next academic year, or who earned a credential by then."""
from __future__ import annotations

from .sql_counts import count_in_sql
from .students import student_rows_sql
from ..models import Cohort, Counts, Group

NOTE = (
    "Students in the cohort who were enrolled again in the next academic year, "
    "or earned a credential by then. Spring starters have less time to return than fall starters."
)

# One row per student per cohort, with whether they have an answer and whether they were retained.
STUDENT_SQL = student_rows_sql("cm.retention")


def count(connection, cohorts: list[Cohort], groups: list[Group]) -> dict[tuple[Cohort, Group], Counts]:
    """Count retained students in the database for every cohort and group."""
    return count_in_sql(connection, STUDENT_SQL, cohorts, groups)
