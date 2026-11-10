"""Every named metric, defined once. Pages and both APIs get their numbers here and only reshape them.

- Retention, two types:
  - school (default): the PDP retention flag, read with the shared retention measure's own query.
  - federal: fall to fall. Enrolled here (took a course) in the fall term after the first academic year.
    FEDERAL_RETENTION holds the rules still open with stakeholders.
- DFW: the shared DFW measure's grade rules, split into D, F and W. F is an F or under 0.7, D is 0.7 to
  under 2.0, W is a W. D + F + W is the measure's numerator.
- Gateway course outcome: passed (2.0 or more, or a P), D, F or W, by the same grade rules.
- Credit completion: the shared credit_completion measure's own per student ratio, averaged.

Counting follows the measures (run_measures.build_result): a group is hidden when fewer than 10 students have an
answer, and a cohort with no answers at all is not yet observable. The tests check every metric here against
run_measure on the real data, so the Results API and the pages can't drift apart.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Iterable

from measures.calculations import credit_completion as completion_measure
from measures.calculations import gateway_english, gateway_math, persistence
from measures.calculations import retention as retention_measure
from measures.calculations.dfw import grade_outcomes
from uncf.cohort import FIRST_TIME, MIN_STUDENTS, share

# Open stakeholder questions for federal retention. Change them here only.
FEDERAL_RETENTION = {
    "first_time_only": False,  # IPEDS counts first time students only
    "credential_counts": False,  # a credential earned here before next fall counts as retained
}
FEDERAL_NOTE = "Students in the cohort who took a course here in the fall term after their first academic year (fall to fall)."
# The student measures the Results API serves, by name. DFW counts course grades, so it goes through dfw().
MEASURE_MODULES = {
    "retention": retention_measure,
    "persistence": persistence,
    "gateway_math": gateway_math,
    "gateway_english": gateway_english,
    "credit_completion": completion_measure,
}
F_BELOW = 0.7  # numeric grades under this are an F; from here to under 2.0 is a D
GRADES = grade_outcomes()
SEASONS = ("FALL", "WINTER", "SPRING", "SUMMER")


# Terms --------------------------------------------------------------------------------------------------------


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


# Counting -----------------------------------------------------------------------------------------------------


def rate(answers: dict[str, float | None], members: Iterable[str], observable: bool = True) -> dict:
    """A student metric for some students, counted the measures' way.

    answers holds each in scope student's answer: 1 or 0, a ratio from 0 to 1, or None when unknown.
    A member missing from answers is out of scope. Hidden numbers are None, never 0.
    """
    members = list(members)
    in_scope = [sid for sid in members if sid in answers]
    known = [answers[sid] for sid in in_scope if answers[sid] is not None]
    counts = {"n_excluded": len(in_scope) - len(known), "n_out_of_scope": len(members) - len(in_scope)}
    if not observable:
        return {"status": "not_yet_observable", "numerator": None, "denominator": None, "rate": None, "n_excluded": None, "n_out_of_scope": None}
    if len(known) < MIN_STUDENTS:
        return {"status": "suppressed", "numerator": None, "denominator": None, "rate": None, "n_excluded": None, "n_out_of_scope": None}
    total = sum(known)
    numerator = int(total) if float(total).is_integer() else round(total, 10)
    return {"status": "ok", "numerator": numerator, "denominator": len(known), "rate": round(total / len(known), 4), **counts}


# Retention ----------------------------------------------------------------------------------------------------


def retention_answers(connection: sqlite3.Connection, cohort: str, retention_type: str) -> tuple[dict[str, int | None], bool]:
    """Each in scope student's retention (1, 0 or None) for one cohort, and whether the cohort has answers yet."""
    if retention_type == "federal":
        return federal_answers(connection, cohort)
    rows = connection.execute(
        f"SELECT student_id, has_answer, achieved FROM ({retention_measure.STUDENT_SQL}) WHERE cohort = ?", [cohort]
    ).fetchall()
    answers = {row["student_id"]: (int(row["achieved"]) if row["has_answer"] else None) for row in rows}
    return answers, any(value is not None for value in answers.values())


def federal_answers(connection: sqlite3.Connection, cohort: str) -> tuple[dict[str, int | None], bool]:
    """Fall to fall: 1 for a student who took a course here the fall after year 1, 0 otherwise."""
    rules = FEDERAL_RETENTION
    rows = connection.execute(
        "SELECT student_id, UPPER(REPLACE(enrollment_type, ' ', '')) AS enrollment_type FROM cohort_membership WHERE cohort = ?",
        [cohort],
    ).fetchall()
    scope = [row["student_id"] for row in rows if not rules["first_time_only"] or row["enrollment_type"] == FIRST_TIME]
    year, season = retention_term(cohort)
    if (year, season) not in observed_terms(connection):
        return {sid: None for sid in scope}, False
    back = {
        row["student_id"]
        for row in connection.execute(
            "SELECT DISTINCT ce.student_id AS student_id FROM course_enrollment ce JOIN term t ON t.term_id = ce.term_id "
            "WHERE ce.cohort = ? AND t.academic_year = ? AND UPPER(t.academic_term) = ? AND ce.course_id IS NOT NULL",
            [cohort, year, season],
        )
    }
    if rules["credential_counts"]:
        back |= {sid for sid, first in credential_years(connection, cohort).items() if first == 1}
    return {sid: int(sid in back) for sid in scope}, True


def retention(answers: dict[str, int | None], observable: bool, students: Iterable[str], retention_type: str) -> dict:
    """Retention for some students: retained of students with an answer, with the type it was counted by."""
    counted = rate(answers, students, observable)
    return {"type": retention_type, **counted, "retained": counted["numerator"], "students": counted["denominator"]}


def retained_share(answers: dict[str, int | None], students: set[str]) -> dict:
    """How many of these students were retained, for a breakdown (a course, a tier, a pair). Hidden under 10."""
    known = [sid for sid in students if answers.get(sid) is not None]
    if len(known) < MIN_STUDENTS:
        return {"students": None, "retained": None, "rate": None}
    back = sum(answers[sid] for sid in known)
    return {"students": len(known), "retained": back, "rate": share(back, len(known))}


def credential_years(connection: sqlite3.Connection, cohort: str) -> dict[str, int]:
    """For each student with a credential here, the academic year (1 is the first) it was first earned."""
    rows = connection.execute(
        "SELECT student_id, first_year_to_bachelors_at_coh AS ba, first_year_to_a_or_c_at_cohort AS ac "
        "FROM cohort_membership WHERE cohort = ?",
        [cohort],
    ).fetchall()
    years = {}
    for row in rows:
        earned = [int(value) for value in (row["ba"], row["ac"]) if value]
        if earned:
            years[row["student_id"]] = min(earned)
    return years


# Grades: DFW and gateway outcomes ----------------------------------------------------------------------------


def grade_result(grade: str | None) -> str | None:
    """D, F, W or pass for a final grade, by the shared DFW measure's rules. None for a grade that isn't final."""
    code = (grade or "").strip().upper()
    is_dfw = GRADES.get(code)
    if is_dfw is None:
        return None
    if not is_dfw:
        return "pass"
    if code in ("W", "F"):
        return code
    return "F" if float(code) < F_BELOW else "D"


def course_rows(connection: sqlite3.Connection, cohort: str, students: dict) -> list[dict]:
    """Every course taken here by the given students in the cohort, with its grade result and the student's groups.

    The same enrollments as the shared DFW measure: rows with a course, for the cohort's own students.
    """
    rows = connection.execute(
        """
        SELECT ce.enrollment_id AS enrollment_id, ce.student_id AS student_id,
               UPPER(TRIM(c.course_prefix)) AS prefix,
               UPPER(TRIM(c.course_prefix)) || ' ' || UPPER(TRIM(c.course_number)) AS course,
               TRIM(ce.course_name) AS name, ce.grade AS grade,
               t.academic_year AS year, UPPER(t.academic_term) AS season, t.sort_order AS sort_order,
               UPPER(TRIM(ce.delivery_method)) AS delivery,
               UPPER(TRIM(ce.math_or_english_gateway)) AS gateway, UPPER(TRIM(ce.course_type)) AS course_type
        FROM course_enrollment ce
        JOIN course c ON c.course_id = ce.course_id
        JOIN term t ON t.term_id = ce.term_id
        WHERE ce.cohort = ?
        """,
        [cohort],
    ).fetchall()
    found = []
    for row in rows:
        student = students.get(row["student_id"])
        if student is None:
            continue
        found.append({**dict(row), "result": grade_result(row["grade"]), "student": student})
    return found


def dfw(rows: list[dict]) -> dict:
    """The DFW rate of some course rows, with D, F and W apart. Every number is None under 10 students."""
    graded = [row for row in rows if row["result"] is not None]
    students = len({row["student_id"] for row in graded})
    if students < MIN_STUDENTS:
        return {"students": None, "num": None, "den": None, "rate": None, "split": None}
    counts = {key: sum(1 for row in graded if row["result"] == key) for key in ("D", "F", "W")}
    num = counts["D"] + counts["F"] + counts["W"]
    total = len(graded)
    return {
        "students": students,
        "num": num,
        "den": total,
        "rate": share(num, total),
        "split": {**counts, "DF": counts["D"] + counts["F"], "total": total, "shares": {key: share(value, total) for key, value in counts.items()}},
    }


# Credits ------------------------------------------------------------------------------------------------------


def completion_answers(connection: sqlite3.Connection, cohort: str) -> dict[str, float | None]:
    """Each in scope student's year 1 credit completion ratio, from the shared measure's own query."""
    rows = connection.execute(
        f"SELECT student_id, in_scope, has_answer, achieved FROM ({completion_measure.STUDENT_SQL}) WHERE cohort = ?", [cohort]
    ).fetchall()
    return {row["student_id"]: (float(row["achieved"]) if row["has_answer"] else None) for row in rows if row["in_scope"]}


def credit_completion(answers: dict[str, float | None], students: Iterable[str]) -> dict:
    """The average credit completion ratio of some students, counted the measure's way."""
    counted = rate(answers, students)
    return {**counted, "counted": counted["denominator"], "ratio": counted["rate"]}


# Any shared measure, for the Results API -----------------------------------------------------------------------


def measure_answers(connection: sqlite3.Connection, measure: str, cohort: str, retention_type: str = "school") -> tuple[dict, bool, str]:
    """Each in scope student's answer to one student measure, whether the cohort has answers yet, and its note."""
    if measure == "retention":
        answers, observable = retention_answers(connection, cohort, retention_type)
        note = FEDERAL_NOTE if retention_type == "federal" else retention_measure.NOTE
        return answers, observable, note
    module = MEASURE_MODULES[measure]
    rows = connection.execute(f"SELECT student_id, in_scope, has_answer, achieved FROM ({module.STUDENT_SQL}) WHERE cohort = ?", [cohort]).fetchall()
    answers = {row["student_id"]: (row["achieved"] if row["has_answer"] else None) for row in rows if row["in_scope"]}
    return answers, any(value is not None for value in answers.values()), module.NOTE


def year_one_credits(connection: sqlite3.Connection, cohort: str) -> dict[str, tuple[float, float]]:
    """Credits attempted and earned in year 1 from the cohort file, for students with both known."""
    rows = connection.execute(
        "SELECT student_id, number_of_credits_attempted_yr_1 AS attempted, number_of_credits_earned_yr_1 AS earned "
        "FROM cohort_membership WHERE cohort = ?",
        [cohort],
    ).fetchall()
    return {row["student_id"]: (row["attempted"], row["earned"]) for row in rows if row["attempted"] is not None and row["earned"] is not None}
