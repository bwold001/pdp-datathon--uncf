"""Gateway math: students required to take it who completed it in their first academic year.

A required student who never took the course counts as not completed.
"""
from __future__ import annotations

from ..models import EVERYONE, Cohort, Counts, Group
from .sql_counts import count_in_sql
from .students import gateway_rows_sql

NOTE = (
    "Students required to take gateway math who completed it in their first academic year "
    "(a grade of 1.0 or higher, or a pass). Students who never took it count as not completed. "
    "Students not required are outside the measure. Students whose requirement or outcome is unknown are left out."
)

# One row per student per cohort: out of scope if not required, counted if completed is C or D, achieved if C.
STUDENT_SQL = gateway_rows_sql("cm.completed_gateway_math_year1", "cm.gateway_math_status")


def count(connection, cohorts: list[Cohort], groups: list[Group], filters: Group = EVERYONE) -> dict[tuple[Cohort, Group], Counts]:
    """Count students who completed gateway math, for every cohort and group."""
    return count_in_sql(connection, STUDENT_SQL, cohorts, groups, filters)
