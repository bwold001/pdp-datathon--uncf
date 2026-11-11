"""DFW: which courses an entering class doesn't pass, and which students that hits hardest.

Every rate comes from run_measure's dfw_rate (the course, term, delivery and student group splits included), so
the page, /measures/dfw_rate and the chat agree. This module adds what isn't a rate: each course's catalog names and
gateway flags, which values exist, and each group next to everyone else in the course. Fewer than min_students()
is hidden.
"""
from __future__ import annotations

import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

from ..calculations.dfw import grade_result
from ..calculations.sql_counts import normalize
from ..models import (
    ALLOWED_VALUES,
    EVERYONE,
    Cohort,
    Group,
    GroupBy,
    GroupDimension,
    GroupPart,
    Measure,
    MeasureResult,
    min_students,
)
from ..run_measures import run_measure
from .common import check_cohort, connect, select_students, share

# The student groups a course can be split by, besides delivery and the term it was taken.
GROUP_DIMENSIONS = (
    GroupDimension.PELL,
    GroupDimension.GENDER,
    GroupDimension.RACE,
    GroupDimension.ETHNICITY,
    GroupDimension.AGE_BAND,
    GroupDimension.ENROLLMENT_INTENSITY,
    GroupDimension.ENROLLMENT_TYPE,
    GroupDimension.COHORT_TERM,
)
SEASONS = {"FALL": "Fall", "WINTER": "Winter", "SPRING": "Spring", "SUMMER": "Summer"}
DELIVERY = {"F": "Face-to-face", "H": "Hybrid", "O": "Online", "UNKNOWN": "Blank"}
TOP_NAMES = 3
# The page's smallest cutoff is 10 final grades, so courses with fewer aren't sent: the list never shows them.
MIN_LISTED_GRADES = 10


class UnknownCourse(LookupError):
    """A course code with no listed final grades for these students."""


def tally(row: MeasureResult) -> dict:
    """A dfw_rate row as the page shows it, with D, F and W apart. Every number is None under min_students()."""
    if row.numerator is None:
        return {"students": None, "num": None, "den": None, "rate": None, "split": None}
    split = dict(row.split)
    return {
        "students": row.n_students,
        "num": row.numerator,
        "den": row.denominator,
        "rate": row.metric_rate,
        "split": {
            **split,
            "DF": split["D"] + split["F"],
            "total": row.denominator,
            "shares": {key: share(value, row.denominator) for key, value in split.items()},
        },
    }


def course_facts(connection: sqlite3.Connection, cohort: str, students: dict) -> dict[str, dict]:
    """For each course the students got a final grade in: its catalog names, gateway flags, and who took it."""
    check_cohort(cohort)
    rows = connection.execute(
        f"""
        SELECT ce.student_id AS student_id, ce.grade AS grade, TRIM(ce.course_name) AS name,
               UPPER(TRIM(c.course_prefix)) || ' ' || UPPER(TRIM(c.course_number)) AS course,
               UPPER(TRIM(ce.math_or_english_gateway)) AS gateway, UPPER(t.academic_term) AS season,
               COALESCE(NULLIF(UPPER(TRIM(ce.delivery_method)), ''), 'UNKNOWN') AS delivery
        FROM course_enrollment ce
        JOIN course c ON c.course_id = ce.course_id
        LEFT JOIN term t ON t.term_id = ce.term_id
        WHERE ce.cohort = '{cohort}'
        """
    ).fetchall()
    facts: dict[str, dict] = defaultdict(lambda: {"names": Counter(), "gateway": Counter(), "rows": []})
    for row in rows:
        if row["student_id"] not in students or grade_result(row["grade"]) is None:
            continue
        fact = facts[row["course"]]
        if row["name"]:
            fact["names"][row["name"]] += 1
        fact["gateway"][row["gateway"]] += 1
        fact["rows"].append(row)
    return facts


def names_of(fact: dict) -> dict:
    """The course's most used catalog names, and how many different names it has."""
    return {"top": [name for name, _ in fact["names"].most_common(TOP_NAMES)], "distinct": len(fact["names"])}


def dfw_courses(cohort: str, filters: Group = EVERYONE, database: str | Path | None = None) -> dict:
    """The DFW page's list: everyone's DFW rate, then each course with 10 or more final grades and min_students() students."""
    rows = run_measure(Measure.DFW_RATE, [Cohort.of(cohort)], [GroupBy.of(GroupDimension.COURSE)], database=database, filters=filters)
    connection = connect(database)
    try:
        facts = course_facts(connection, cohort, select_students(connection, cohort, filters))
    finally:
        connection.close()

    everyone = tally(rows[0])
    by_course = {row.group.label.split("=", 1)[1]: row for row in rows[1:]}
    courses = []
    for course, fact in facts.items():
        numbers = tally(by_course[course])
        if numbers["den"] is not None and numbers["den"] >= MIN_LISTED_GRADES:
            courses.append({"course": course, "names": names_of(fact), **numbers, "gateway": {"M": fact["gateway"]["M"], "E": fact["gateway"]["E"]}})
    courses.sort(key=lambda c: (-c["num"], -c["rate"], c["course"]))
    shown_any = everyone["den"] is not None
    return {
        "context": {},
        "status": "ok" if shown_any else "suppressed",
        "everyone": everyone,
        "courses": courses if shown_any else [],
        # Courses these students took that aren't listed: under 10 final grades, or hidden under min_students().
        "hidden_courses": len(facts) - len(courses),
    }


def compare(part: dict, course: dict) -> dict:
    """A group's numbers next to everyone else in the course: their rate and the gap in points."""
    if part["den"] is None or course["den"] is None:
        return {**part, "rest_rate": None, "gap": None}
    rest_grades = course["den"] - part["den"]
    if rest_grades < min_students():
        return {**part, "rest_rate": None, "gap": None}
    rest_rate = (course["num"] - part["num"]) / rest_grades
    return {**part, "rest_rate": round(rest_rate, 4), "gap": round((part["num"] / part["den"] - rest_rate) * 100, 1)}


def dfw_course(cohort: str, course: str, filters: Group = EVERYONE, database: str | Path | None = None) -> dict:
    """One course in detail: its numbers, then each term, delivery method and group next to everyone else."""
    code = " ".join(course.upper().split())
    connection = connect(database)
    try:
        students = select_students(connection, cohort, filters)
        fact = course_facts(connection, cohort, students).get(code)
    finally:
        connection.close()
    if fact is None:
        raise UnknownCourse(f"No course {code!r} with {min_students()} or more students for these filters.")

    # The course is one more filter, so every row below is about this course only.
    in_course = Group(filters.parts | {GroupPart(GroupDimension.COURSE, code)})
    splits = [GroupBy.of(GroupDimension.TERM), GroupBy.of(GroupDimension.DELIVERY), *(GroupBy.of(d) for d in GROUP_DIMENSIONS)]
    rows = run_measure(Measure.DFW_RATE, [Cohort.of(cohort)], splits, database=database, filters=in_course)
    numbers = tally(rows[0])
    if numbers["den"] is None:
        raise UnknownCourse(f"No course {code!r} with {min_students()} or more students for these filters.")

    by_group = {}
    for row in rows[1:]:
        (part,) = row.group.parts
        by_group[(part.dimension, normalize(part.value))] = row
    present = {
        GroupDimension.TERM: {normalize(row["season"] or "UNKNOWN") for row in fact["rows"]},
        GroupDimension.DELIVERY: {normalize(row["delivery"]) for row in fact["rows"]},
        **{d: {students[row["student_id"]][d.value] for row in fact["rows"]} for d in GROUP_DIMENSIONS},
    }

    def split_by(dimension: GroupDimension, values: dict[str, str]) -> list[dict]:
        """The course's numbers for each value of one dimension, in the given order; values nobody has are left out."""
        parts = []
        for value, label in values.items():
            key = normalize(value)
            if key in present[dimension] and (dimension, key) in by_group:
                parts.append(compare({"value": label, **tally(by_group[(dimension, key)])}, numbers))
        return parts

    return {
        "context": {},
        "course": code,
        "names": names_of(fact),
        **numbers,
        "terms": split_by(GroupDimension.TERM, SEASONS),
        "delivery": split_by(GroupDimension.DELIVERY, DELIVERY),
        "groups": {d.value: split_by(d, {value: value for value in sorted(ALLOWED_VALUES[d])}) for d in GROUP_DIMENSIONS},
    }
