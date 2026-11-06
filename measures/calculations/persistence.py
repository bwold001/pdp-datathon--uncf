"""Persistence: students enrolled at another institution, or who earned a credential there, by year 2."""
from __future__ import annotations

from .sql_counts import count_in_sql
from .students import student_rows_sql
from ..models import Cohort, Counts, Group

NOTE = (
    "Students in the cohort who were enrolled at another institution, "
    "or earned a credential there, by their second academic year."
)

# One row per student per cohort, with whether they have an answer and whether they persisted.
STUDENT_SQL = student_rows_sql("cm.persistence")


def count(connection, cohorts: list[Cohort], groups: list[Group]) -> dict[tuple[Cohort, Group], Counts]:
    """Count persisted students in the database for every cohort and group."""
    return count_in_sql(connection, STUDENT_SQL, cohorts, groups)
