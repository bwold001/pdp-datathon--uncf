"""DFW rate: course enrollments that ended in a D, an F or a withdrawal.

Unlike the student measures, each row here is a course enrollment, not a student. The shared counting
in sql_counts.py works the same way: a row is in the denominator when its grade is one we can classify,
and it counts toward the numerator when that grade is a D (D+, D or D-), an F or a withdrawal. The letters come
from the shared grade scale (grades.py), so a C- (1.7) is a C and passes. Pages count D, F and W, not + and -.
"""
from __future__ import annotations

from ..models import (
    EVERYONE,
    UNKNOWN,
    Cohort,
    Counts,
    ExclusionReason,
    Group,
    GroupDimension,
)
from .grades import LETTER_SCALE, grade_letter, known_letters, lowest_points
from .sql_counts import cohort_values_sql, count_in_sql

# The letters that count as a DFW: every D, F and W. A C- is a C and passes.
DFW_GRADES = ("D+", "D", "D-", "F", "W")
# How the split counts them: every D letter is a D, so + and - aren't counted apart.
DFW_GROUPS = {"D+": "D", "D": "D", "D-": "D", "F": "F", "W": "W"}
SPLIT = ("D", "F", "W")
# A numeric grade under this many points is a DFW: the lowest points of the lowest letter that passes (C-, 1.7).
DFW_BELOW = min(lowest_points(letter) for letter, _ in LETTER_SCALE if letter not in DFW_GRADES)

NOTE = (
    "Course enrollments of the cohort's students that ended in a D, F or withdrawal, out of those with a final "
    f"grade. A numeric grade under {DFW_BELOW:.1f} counts, so a C- passes. Incomplete, audit, missing and other "
    "grades are left out."
)

# DFW can also be grouped by course (prefix and number, e.g. ENGL 1302), by the season the course was taken
# (FALL, SPRING, ...) and by delivery method (F, H, O or UNKNOWN). The data says which values exist.
SUPPORTED_OPEN_DIMENSIONS = frozenset({GroupDimension.COURSE, GroupDimension.TERM, GroupDimension.DELIVERY})

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


def grade_outcomes() -> dict[str, bool]:
    """Every grade we can classify (as written in the course file), mapped to whether it is a DFW."""
    return {grade: letter in DFW_GRADES for grade, letter in known_letters().items()}


def grade_result(grade: str | None) -> str | None:
    """A final grade's letter on the shared scale (A to D-, F), or P or W; None for one we can't classify."""
    return grade_letter(grade)


def grade_values_sql() -> str:
    """VALUES rows pairing each classifiable grade with 1 for a DFW (0 otherwise) and its split group (D, F, W or pass)."""
    # The grades come from the scale in grades.py, never from the data, so they are safe to write into the query.
    rows = []
    for grade, letter in known_letters().items():
        rows.append(f"('{grade}', {1 if letter in DFW_GRADES else 0}, '{DFW_GROUPS.get(letter, 'pass')}')")
    return ", ".join(rows)


def grade_reasons_sql() -> str:
    """VALUES rows pairing each grade we can explain with the reason it is left out."""
    # The grades and reasons come from the dictionary above, never from the data, so they are safe to write into the query.
    return ", ".join(f"('{grade}', '{reason.value}')" for grade, reason in GRADE_REASONS.items())


# One row per course enrollment with a class, with the student's group columns. The grade decides the answer.
# Grades and courses match ignoring case and spaces. Every enrollment is in scope. One with a grade we can't
# classify is left out of the denominator. The join to course drops enrollments with no class.
ENROLLMENT_SQL = f"""
WITH grade_outcomes(grade, is_dfw, outcome) AS (VALUES {grade_values_sql()}),
grade_reasons(grade, reason) AS (VALUES {grade_reasons_sql()})
SELECT ce.student_id AS student_id,
       ce.cohort AS cohort,
       1 AS in_scope,
       CASE WHEN g.grade IS NULL THEN 0 ELSE 1 END AS has_answer,
       CASE WHEN g.is_dfw = 1 THEN 1 ELSE 0 END AS achieved,
       COALESCE(r.reason, '{ExclusionReason.UNLISTED_GRADE.value}') AS exclusion_reason,
       g.outcome AS outcome,
       s.race AS race,
       s.ethnicity AS ethnicity,
       s.gender AS gender,
       s.first_gen AS first_gen,
       s.student_age AS age_band,
       cm.pell_status_first_year AS pell,
       cm.enrollment_type AS enrollment_type,
       cm.enrollment_intensity_first_term AS enrollment_intensity,
       cm.cohort_term AS cohort_term,
       UPPER(TRIM(c.course_prefix)) || ' ' || UPPER(TRIM(c.course_number)) AS course,
       UPPER(t.academic_term) AS term,
       UPPER(TRIM(ce.delivery_method)) AS delivery
FROM course_enrollment ce
JOIN cohort_membership cm ON cm.student_id = ce.student_id AND cm.cohort = ce.cohort
JOIN student s ON s.student_id = ce.student_id
JOIN course c ON c.course_id = ce.course_id
LEFT JOIN term t ON t.term_id = ce.term_id
LEFT JOIN grade_outcomes g ON g.grade = UPPER(TRIM(ce.grade))
LEFT JOIN grade_reasons r ON r.grade = UPPER(TRIM(ce.grade))
"""


def open_values(connection, dimension: GroupDimension, cohorts: list[Cohort]) -> list[str]:
    """The values in the requested cohorts' enrollments: courses ('ENGL 1302'), seasons (FALL) or delivery codes."""
    if dimension not in SUPPORTED_OPEN_DIMENSIONS:
        raise ValueError(f"dfw_rate has no values to find for {dimension.value}")
    # The column name comes from the GroupDimension enum, so it is safe to write into the query.
    column = f"COALESCE(NULLIF(e.{dimension.value}, ''), '{UNKNOWN}')"
    cursor = connection.cursor()
    cursor.execute(
        f"WITH cohort_numbers(cohort, cohort_no) AS (VALUES {cohort_values_sql(cohorts)}), "
        f"enrollments AS ({ENROLLMENT_SQL}) "
        f"SELECT DISTINCT {column} FROM enrollments e JOIN cohort_numbers c ON c.cohort = e.cohort ORDER BY 1"
    )
    return [row[0] for row in cursor.fetchall()]


def count(connection, cohorts: list[Cohort], groups: list[Group], filters: Group = EVERYONE) -> dict[tuple[Cohort, Group], Counts]:
    """Count DFW enrollments in the database for every cohort and group, with D, F and W apart."""
    return count_in_sql(connection, ENROLLMENT_SQL, cohorts, groups, filters, SPLIT)
