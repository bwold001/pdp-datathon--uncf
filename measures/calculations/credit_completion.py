"""Credit completion: the average share of attempted credits that students earned in their first year."""
from __future__ import annotations

from .sql_counts import count_in_sql
from .students import rows_sql
from ..models import Cohort, Counts, ExclusionReason, Group

NOTE = (
    "Average of each student's year 1 credits earned / credits attempted, modeled on the Postsecondary Data "
    "Partnership's credit completion ratio. Counts first-time and transfer-in students who attempted at least "
    "one credit. Students with no credits attempted, or with unknown enrollment type or full- or part-time status, "
    "are left out. Re-admit and continuing students are outside the measure."
)


def credit_rows_sql(attempted_column: str, earned_column: str) -> str:
    """The query for one row per student per cohort, for credit completion.

    A student's answer is their own ratio, credits earned / credits attempted, and `achieved` holds it (0 to 1),
    so the numerator adds up the students' ratios. Counted: first-time and transfer-in students who attempted
    at least one credit and have a known full- or part-time status. Re-admit and continuing students are out of
    scope. A ratio above 1 (earned above attempted) is kept at 1, so one bad row can't stop the run or push the
    numerator past the denominator. Nothing flags such a row, so the README says it is capped.
    """
    # Both arguments are column names written in a measure's file, never user input.
    # COALESCE makes a blank enrollment type a value that matches nothing, so the tests below never come out blank.
    enrollment_type = "COALESCE(UPPER(REPLACE(cm.enrollment_type, ' ', '')), '')"
    out_of_scope = f"{enrollment_type} IN ('RE-ADMIT', 'CONTINUING')"
    unknown_enrollment_type = f"{enrollment_type} NOT IN ('FIRST-TIME', 'TRANSFER-IN', 'RE-ADMIT', 'CONTINUING')"
    unknown_value = f"{attempted_column} IS NULL OR {earned_column} IS NULL"
    no_credits = f"{attempted_column} < 1"
    unknown_attendance = (
        "COALESCE(UPPER(REPLACE(cm.enrollment_intensity_first_term, ' ', '')), '') NOT IN ('FULL-TIME', 'PART-TIME')"
    )
    counted = (
        f"NOT ({out_of_scope}) AND NOT ({unknown_enrollment_type}) AND NOT ({unknown_value}) "
        f"AND NOT ({no_credits}) AND NOT ({unknown_attendance})"
    )
    ratio = f"CASE WHEN {earned_column} > {attempted_column} THEN 1.0 ELSE {earned_column} * 1.0 / {attempted_column} END"
    return rows_sql(
        has_answer=f"CASE WHEN {counted} THEN 1 ELSE 0 END",
        achieved=f"CASE WHEN {counted} THEN {ratio} ELSE 0 END",
        in_scope=f"CASE WHEN {out_of_scope} THEN 0 ELSE 1 END",
        exclusion_reason=(
            f"CASE WHEN {unknown_enrollment_type} THEN '{ExclusionReason.UNKNOWN_ENROLLMENT_TYPE.value}' "
            f"WHEN {unknown_value} THEN '{ExclusionReason.UNKNOWN_OUTCOME.value}' "
            f"WHEN {no_credits} THEN '{ExclusionReason.NO_CREDITS_ATTEMPTED.value}' "
            f"ELSE '{ExclusionReason.UNKNOWN_ATTENDANCE_TYPE.value}' END"
        ),
    )


# One row per student per cohort: achieved holds the student's own ratio, and the numerator adds the ratios up.
STUDENT_SQL = credit_rows_sql("cm.number_of_credits_attempted_yr_1", "cm.number_of_credits_earned_yr_1")


def count(connection, cohorts: list[Cohort], groups: list[Group]) -> dict[tuple[Cohort, Group], Counts]:
    """Count students and add up their credit completion ratios for every cohort and group."""
    return count_in_sql(connection, STUDENT_SQL, cohorts, groups)
