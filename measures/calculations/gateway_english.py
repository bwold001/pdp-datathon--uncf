"""Gateway English: students required to take it who completed it in their first academic year.

A required student who never took the course counts as not completed.
"""
from __future__ import annotations

from .sql_counts import count_in_sql
from .students import gateway_rows_sql
from ..models import Cohort, Counts, Group

NOTE = (
    "Students required to take gateway English who completed it in their first academic year "
    "(a grade of 1.0 or higher, or a pass). Students who never took it count as not completed. "
    "Students not required are outside the measure. Students whose requirement or outcome is unknown are left out."
)

# One row per student per cohort: out of scope if not required, counted if completed is C or D, achieved if C.
STUDENT_SQL = gateway_rows_sql("cm.completed_gateway_english_year1", "cm.gateway_english_status")


def count(connection, cohorts: list[Cohort], groups: list[Group]) -> dict[tuple[Cohort, Group], Counts]:
    """Count students who completed gateway English, for every cohort and group."""
    return count_in_sql(connection, STUDENT_SQL, cohorts, groups)
