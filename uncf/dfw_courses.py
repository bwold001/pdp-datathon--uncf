"""DFW: which courses an entering class doesn't pass, and which students that hits hardest.

The numbers come from uncf.metrics (the shared DFW measure's grade rules, split into D, F and W). This module
only breaks them down by course, term, delivery method and student group, and compares each group with everyone
else in the course. Courses and groups with fewer than 10 students are hidden.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

from measures.models import ALLOWED_VALUES, GroupDimension
from uncf import data, metrics
from uncf.filters import MIN_STUDENTS, CohortQuery, listed_value, select_students

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
DELIVERY = {"F": "Face-to-face", "H": "Hybrid", "O": "Online"}
TOP_NAMES = 3


class UnknownCourse(LookupError):
    """A course code with no listed final grades for these students."""


def final_grades(query: CohortQuery, database: Path | None = None) -> tuple[list[dict], str]:
    """The query's students' final grades, each with its course, term, delivery method and the student's groups."""
    connection = data.open_database(database)
    try:
        students = select_students(connection, query)
        rows = metrics.course_rows(connection, query.cohort, students)
        stamp = data.loaded_at(connection)
    finally:
        connection.close()
    grades = []
    for row in rows:
        if row["result"] is None:
            continue
        student = row["student"]
        grades.append(
            {
                **row,
                "term": SEASONS.get(row["season"]),
                "delivery_label": DELIVERY.get(row["delivery"] or "", "Blank"),
                **{dimension.value: listed_value(dimension.value, student[dimension.value]) for dimension in GROUP_DIMENSIONS},
            }
        )
    return grades, stamp


def course_names(grades: list[dict]) -> dict:
    """The course's most used catalog names, and how many different names it has."""
    names = Counter(grade["name"] for grade in grades if grade["name"])
    return {"top": [name for name, _ in names.most_common(TOP_NAMES)], "distinct": len(names)}


def dfw_courses(query: CohortQuery, database: Path | None = None) -> dict:
    """The DFW page's list: everyone's DFW rate, then each course with 10 or more students."""
    grades, stamp = final_grades(query, database)
    by_course: dict[str, list[dict]] = defaultdict(list)
    for grade in grades:
        by_course[grade["course"]].append(grade)

    courses = []
    hidden = 0
    for course, rows in by_course.items():
        numbers = metrics.dfw(rows)
        if numbers["den"] is None:
            hidden += 1
            continue
        gateway = Counter(row["gateway"] for row in rows)
        courses.append({"course": course, "names": course_names(rows), **numbers, "gateway": {"M": gateway["M"], "E": gateway["E"]}})
    courses.sort(key=lambda c: (-c["num"], -c["rate"], c["course"]))

    everyone = metrics.dfw(grades)
    shown_any = everyone["den"] is not None
    return {
        "meta": {**query.meta(), "loaded_at": stamp},
        "status": "ok" if shown_any else "suppressed",
        "everyone": everyone,
        "courses": courses if shown_any else [],
        "hidden_courses": hidden,
    }


def compare(part: dict, course: dict) -> dict:
    """A group's numbers next to everyone else in the course: their rate and the gap in points."""
    if part["den"] is None or course["den"] is None:
        return {**part, "rest_rate": None, "gap": None}
    rest_grades = course["den"] - part["den"]
    if rest_grades < MIN_STUDENTS:
        return {**part, "rest_rate": None, "gap": None}
    rest_rate = (course["num"] - part["num"]) / rest_grades
    return {**part, "rest_rate": round(rest_rate, 4), "gap": round((part["num"] / part["den"] - rest_rate) * 100, 1)}


def dfw_course(query: CohortQuery, course: str, database: Path | None = None) -> dict:
    """One course in detail: its numbers, then each term, delivery method and group next to everyone else."""
    code = " ".join(course.upper().split())
    grades, stamp = final_grades(query, database)
    rows = [grade for grade in grades if grade["course"] == code]
    numbers = metrics.dfw(rows)
    if numbers["den"] is None:
        raise UnknownCourse(f"No course {code!r} with 10 or more students for these filters.")

    def split_by(key: str, values: list[str]) -> list[dict]:
        """The course's numbers for each value of one field, in the given order; values nobody has are left out."""
        parts = []
        for value in values:
            part = [row for row in rows if row[key] == value]
            if part:
                parts.append(compare({"value": value, **metrics.dfw(part)}, numbers))
        return parts

    return {
        "meta": {**query.meta(), "loaded_at": stamp},
        "course": code,
        "names": course_names(rows),
        **numbers,
        "terms": split_by("term", list(SEASONS.values())),
        "delivery": split_by("delivery_label", [*DELIVERY.values(), "Blank"]),
        "groups": {dimension.value: split_by(dimension.value, sorted(ALLOWED_VALUES[dimension])) for dimension in GROUP_DIMENSIONS},
    }
