"""DFW rate: course enrollments that ended in a D, an F or a withdrawal.

Unlike the student measures, each row here is a course enrollment, not a student. The shared counting
in sql_counts.py works the same way: a row is in the denominator when its grade is one we can classify,
and it counts toward the numerator when that grade is a D, F or withdrawal.
"""
from __future__ import annotations

from .sql_counts import cohort_values_sql, count_in_sql
from ..models import Cohort, Counts, ExclusionReason, Group, GroupDimension

# A grade counts as D or F below this many grade points (2.0 is a C).
DFW_BELOW = 2.0

NOTE = (
    "Course enrollments of the cohort's students that ended in a D, F or withdrawal, out of those with a final "
    f"grade. A numeric grade under {DFW_BELOW:.1f} counts. Incomplete, audit, missing and other grades are left out."
)

# DFW can also be grouped by course. A course is its prefix and number, e.g. ENGL 1302. The data says which exist.
SUPPORTED_OPEN_DIMENSIONS = frozenset({GroupDimension.COURSE})

# The grades in the course file that are not numbers, in capitals. Anything not listed here or numeric is left out.
DFW_CODES = ["F", "W"]
PASS_CODES = ["P"]

# Why a grade that isn't classified is left out. A code that isn't here is an unlisted grade.
# The loader turns M and UK into UNKNOWN, so they show up as unknown_grade.
GRADE_REASONS = {
    "I": ExclusionReason.INCOMPLETE,
    "A": ExclusionReason.AUDIT,
    "MIS": ExclusionReason.MISSING_GRADE,
    "O": ExclusionReason.OTHER_GRADE,
    "OTH": ExclusionReason.OTHER_GRADE,
    "UNKNOWN": ExclusionReason.UNKNOWN_GRADE,
}


def numeric_grades() -> dict[str, bool]:
    """Every grade point from 0 to 4 in hundredths, written each way it appears ('1', '1.0', '1.00', '3.67'), mapped to is-it-a-DFW."""
    grades = {}
    for hundredths in range(0, 401):
        points = hundredths / 100
        spellings = {f"{points:g}", f"{points:.2f}"}
        if hundredths % 10 == 0:
            spellings.add(f"{points:.1f}")
        for spelling in spellings:
            grades[spelling] = points < DFW_BELOW
    return grades


def grade_outcomes() -> dict[str, bool]:
    """Every grade we can classify, mapped to whether it is a D, F or withdrawal."""
    outcomes = numeric_grades()
    outcomes.update({code: True for code in DFW_CODES})
    outcomes.update({code: False for code in PASS_CODES})
    return outcomes


def grade_values_sql() -> str:
    """VALUES rows pairing each classifiable grade with 1 for a D, F or withdrawal, 0 otherwise."""
    # The grades come from the lists above, never from the data, so they are safe to write into the query.
    return ", ".join(f"('{grade}', {1 if is_dfw else 0})" for grade, is_dfw in grade_outcomes().items())


def grade_reasons_sql() -> str:
    """VALUES rows pairing each grade we can explain with the reason it is left out."""
    # The grades and reasons come from the dictionary above, never from the data, so they are safe to write into the query.
    return ", ".join(f"('{grade}', '{reason.value}')" for grade, reason in GRADE_REASONS.items())


# One row per course enrollment with a class, with the student's group columns. The grade decides the answer.
# Grades and courses match ignoring case and spaces. Every enrollment is in scope. One with a grade we can't
# classify is left out of the denominator. The join to course drops enrollments with no class.
ENROLLMENT_SQL = f"""
WITH grade_outcomes(grade, is_dfw) AS (VALUES {grade_values_sql()}),
grade_reasons(grade, reason) AS (VALUES {grade_reasons_sql()})
SELECT ce.student_id AS student_id,
       ce.cohort AS cohort,
       1 AS in_scope,
       CASE WHEN g.grade IS NULL THEN 0 ELSE 1 END AS has_answer,
       CASE WHEN g.is_dfw = 1 THEN 1 ELSE 0 END AS achieved,
       COALESCE(r.reason, '{ExclusionReason.UNLISTED_GRADE.value}') AS exclusion_reason,
       s.race AS race,
       s.ethnicity AS ethnicity,
       s.gender AS gender,
       s.first_gen AS first_gen,
       s.student_age AS age_band,
       cm.pell_status_first_year AS pell,
       cm.enrollment_type AS enrollment_type,
       cm.enrollment_intensity_first_term AS enrollment_intensity,
       cm.cohort_term AS cohort_term,
       UPPER(TRIM(c.course_prefix)) || ' ' || UPPER(TRIM(c.course_number)) AS course
FROM course_enrollment ce
JOIN cohort_membership cm ON cm.student_id = ce.student_id AND cm.cohort = ce.cohort
JOIN student s ON s.student_id = ce.student_id
JOIN course c ON c.course_id = ce.course_id
LEFT JOIN grade_outcomes g ON g.grade = UPPER(TRIM(ce.grade))
LEFT JOIN grade_reasons r ON r.grade = UPPER(TRIM(ce.grade))
"""


def open_values(connection, dimension: GroupDimension, cohorts: list[Cohort]) -> list[str]:
    """The courses with an enrollment in the requested cohorts, such as 'ENGL 1302'."""
    if dimension != GroupDimension.COURSE:
        raise ValueError(f"dfw_rate has no values to find for {dimension.value}")
    cursor = connection.cursor()
    cursor.execute(
        f"WITH cohort_numbers(cohort, cohort_no) AS (VALUES {cohort_values_sql(cohorts)}), "
        f"enrollments AS ({ENROLLMENT_SQL}) "
        "SELECT DISTINCT e.course FROM enrollments e JOIN cohort_numbers c ON c.cohort = e.cohort ORDER BY e.course"
    )
    return [row[0] for row in cursor.fetchall()]


def count(connection, cohorts: list[Cohort], groups: list[Group]) -> dict[tuple[Cohort, Group], Counts]:
    """Count D, F and withdrawal enrollments in the database for every cohort and group."""
    return count_in_sql(connection, ENROLLMENT_SQL, cohorts, groups)
