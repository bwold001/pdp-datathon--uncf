"""Checks the DFW page's numbers against a tiny made-up database with known answers, plus the real data."""
from __future__ import annotations

import pytest

from measures.run_measures import DEFAULT_DATABASE
from uncf.cohort import CohortQuery
from uncf.dfw_courses import UnknownCourse, dfw_course, dfw_courses
from uncf.tests.explorer_fixture import here, make_database, student


def graded(prefix: str, count: int, grades: list[str], course=("ENG", "101"), **values) -> tuple[list[dict], list[dict]]:
    """count students, each with one final grade per entry in grades (cycled), in one course in Fall 2023."""
    students, records = [], []
    for n in range(count):
        student_id = f"{prefix}{n}"
        students.append(student(student_id, **values))
        record = {"prefix": course[0], "number": course[1], "name": "COMPOSITION I", "grade": grades[n % len(grades)]}
        records.append(here(student_id, "2023-24", "FALL", **record, **values.get("course_fields", {})))
    return students, records


def split(tally: dict) -> dict:
    """D, F, W, their D or F sum and the total, without the shares."""
    return {key: tally["split"][key] for key in ("D", "F", "W", "DF", "total")}


def build(tmp_path, *groups):
    """A database from groups made by graded()."""
    return make_database(tmp_path / "pdp.sqlite", [s for g in groups for s in g[0]], [r for g in groups for r in g[1]])


def test_grade_rules_follow_the_dfw_measure(tmp_path):
    """Under 2.0 (a C minus too), F and W count; 2.0 and P pass; I, audit, unknown and unlisted grades are left out."""
    database = build(tmp_path, graded("s", 20, ["1.7", "2.0", "F", "W", "P", "I", "A", "UNKNOWN", "UW", "4"]))
    everyone = dfw_courses(CohortQuery.of("2023-24"), database=database)["everyone"]
    # Final grades, twice each: 1.7, 2.0, F, W, P, 4. Of those, 1.7 is a D, F an F and W a withdrawal.
    assert everyone["den"] == 12
    assert everyone["students"] == 12
    assert split(everyone) == {"D": 2, "F": 2, "W": 2, "DF": 4, "total": 12}
    assert everyone["rate"] == 0.5


def test_courses_are_listed_by_dfw_count_and_small_ones_hidden(tmp_path):
    """Courses with 10 or more students are listed, most DFW grades first; one with 9 students is hidden."""
    database = build(
        tmp_path,
        graded("eng", 12, ["F", "4"], course=("ENG", "101")),
        graded("math", 20, ["F", "F", "4", "W"], course=("MATH", "111")),
        graded("art", 9, ["F"], course=("ART", "100")),
    )
    result = dfw_courses(CohortQuery.of("2023-24"), database=database)
    assert [c["course"] for c in result["courses"]] == ["MATH 111", "ENG 101"]
    assert result["hidden_courses"] == 1
    math = result["courses"][0]
    assert (math["num"], math["den"], split(math)) == (15, 20, {"D": 0, "F": 10, "W": 5, "DF": 10, "total": 20})
    assert math["names"] == {"top": ["COMPOSITION I"], "distinct": 1}


def test_course_detail_splits_by_term_delivery_and_group(tmp_path):
    """One course by term, by delivery method (blank shown as Blank) and by student group, small groups hidden."""
    students, records = graded("y", 12, ["F", "4", "4"], pell="Y")
    more_students, more_records = graded("n", 15, ["4"], pell="N")
    few_students, few_records = graded("u", 3, ["W"], pell="U")
    for n, record in enumerate(records):
        record["delivery"] = "O" if n % 2 else None
    database = make_database(tmp_path / "pdp.sqlite", students + more_students + few_students, records + more_records + few_records)
    detail = dfw_course(CohortQuery.of("2023-24"), "eng  101", database=database)
    assert detail["course"] == "ENG 101"
    assert (detail["num"], detail["den"]) == (7, 30)
    assert [term["value"] for term in detail["terms"]] == ["Fall"]
    delivery = {part["value"]: part["den"] for part in detail["delivery"]}
    assert delivery == {"Online": None, "Blank": 24}  # 6 online students: hidden
    pell = {group["value"]: (group["num"], group["den"]) for group in detail["groups"]["pell"]}
    assert pell == {"N": (0, 15), "UNKNOWN": (None, None), "Y": (4, 12)}
    intensity = {group["value"] for group in detail["groups"]["enrollment_intensity"]}
    assert intensity == {"Full-time"}  # stored as Full-Time, answered with the listed spelling


def test_numeric_f_and_d_follow_the_0_7_line(tmp_path):
    """F is an F or under 0.7, D is 0.7 to under 2.0, and D + F + W is the DFW numerator."""
    database = build(tmp_path, graded("s", 10, ["0.0", "0.67", "0.7", "1.99", "2.0", "W", "F", "3.3", "1.0", "0.69"]))
    everyone = dfw_courses(CohortQuery.of("2023-24"), database=database)["everyone"]
    assert split(everyone) == {"D": 3, "F": 4, "W": 1, "DF": 7, "total": 10}
    assert everyone["num"] == 8
    assert everyone["split"]["shares"] == {"D": 0.3, "F": 0.4, "W": 0.1}


def test_groups_are_compared_with_everyone_else_in_the_course(tmp_path):
    """Each group's rate next to the rest of the course, with the gap in points, computed by the API."""
    database = build(tmp_path, graded("y", 20, ["F", "4"], pell="Y"), graded("n", 20, ["4"], pell="N"))
    detail = dfw_course(CohortQuery.of("2023-24"), "ENG 101", database=database)
    pell = {group["value"]: group for group in detail["groups"]["pell"]}
    assert (pell["Y"]["rest_rate"], pell["Y"]["gap"]) == (0.0, 50.0)
    assert (pell["N"]["rest_rate"], pell["N"]["gap"]) == (0.5, -50.0)


def test_unknown_or_hidden_course_is_an_error(tmp_path):
    """Asking for a course that isn't there, or has under 10 students, raises UnknownCourse."""
    database = build(tmp_path, graded("s", 9, ["F"]))
    with pytest.raises(UnknownCourse):
        dfw_course(CohortQuery.of("2023-24"), "ENG 101", database=database)
    with pytest.raises(UnknownCourse):
        dfw_course(CohortQuery.of("2023-24"), "NOPE 1", database=database)


def test_cohort_filters_pick_the_students(tmp_path):
    """The cohort bar's filters decide whose grades count; under 10 students hides everything."""
    database = build(tmp_path, graded("y", 12, ["F"], pell="Y"), graded("n", 10, ["4"], pell="N"))
    assert dfw_courses(CohortQuery.of("2023-24", pell="Y"), database=database)["everyone"]["rate"] == 1.0
    assert dfw_courses(CohortQuery.of("2023-24", pell="N"), database=database)["everyone"]["rate"] == 0.0
    assert dfw_courses(CohortQuery.of("2023-24", pell="UNKNOWN"), database=database)["status"] == "suppressed"


@pytest.mark.slow
@pytest.mark.skipif(not DEFAULT_DATABASE.exists(), reason="the normalized data isn't loaded")
def test_real_data_known_answers():
    """2023-24, checked against the shared DFW measure's counts on pdp.sqlite (synthetic data)."""
    result = dfw_courses(CohortQuery.of("2023-24"))
    assert split(result["everyone"]) == {"D": 608, "F": 2262, "W": 1477, "DF": 2870, "total": 18883}
    assert result["everyone"]["num"] == 4347  # the shared dfw_rate measure's numerator
    eng = dfw_course(CohortQuery.of("2023-24"), "ENG 101")
    assert (eng["num"], eng["den"]) == (135, 492)
