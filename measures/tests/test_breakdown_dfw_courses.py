"""Checks the DFW page's numbers against a tiny made-up database with known answers, plus the real data."""
from __future__ import annotations

import pytest

from measures.breakdowns.dfw_courses import UnknownCourse, dfw_course, dfw_courses
from measures.run_measures import DEFAULT_DATABASE
from measures.tests.explorer_fixture import here, make_database, pick, student


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
    """D, F and W, the D and F sum and the total, without the shares."""
    return {**tally["split"]["grades"], **{key: tally["split"][key] for key in ("DF", "W", "total")}}


def counts(d=0, f=0, w=0, total=0) -> dict:
    """What split() gives for these D, F and W counts."""
    return {"D": d, "F": f, "W": w, "DF": d + f, "total": total}


def build(tmp_path, *groups):
    """A database from groups made by graded()."""
    return make_database(tmp_path / "pdp.sqlite", [s for g in groups for s in g[0]], [r for g in groups for r in g[1]])


def test_grade_rules_follow_the_dfw_measure(tmp_path):
    """D+ and below, F and W count; a C- (1.7), 2.0 and P pass; I, audit, unknown and unlisted grades are left out."""
    database = build(tmp_path, graded("s", 20, ["1.7", "1.69", "F", "W", "P", "I", "A", "UNKNOWN", "UW", "4"]))
    everyone = dfw_courses(**pick("2023-24"), database=database)["everyone"]
    # Final grades, twice each: 1.7, 1.69, F, W, P, 4. Of those, 1.69 is a D+, F an F and W a withdrawal.
    assert everyone["den"] == 12
    assert everyone["students"] == 12
    assert split(everyone) == counts(d=2, f=2, w=2, total=12)
    assert everyone["rate"] == 0.5


def test_courses_are_listed_by_dfw_count_including_small_ones(tmp_path):
    """Every nonempty course is listed, most DFW grades first, including nine students."""
    database = build(
        tmp_path,
        graded("eng", 12, ["F", "4"], course=("ENG", "101")),
        graded("math", 20, ["F", "F", "4", "W"], course=("MATH", "111")),
        graded("art", 9, ["F"], course=("ART", "100")),
    )
    result = dfw_courses(**pick("2023-24"), database=database)
    assert [c["course"] for c in result["courses"]] == ["MATH 111", "ART 100", "ENG 101"]
    assert result["hidden_courses"] == 0
    math = result["courses"][0]
    assert (math["num"], math["den"], split(math)) == (15, 20, counts(f=10, w=5, total=20))
    assert math["names"] == {"top": ["COMPOSITION I"], "distinct": 1}


def test_course_detail_splits_by_term_delivery_and_group(tmp_path):
    """One course keeps term, delivery and student-group counts, including small groups."""
    students, records = graded("y", 12, ["F", "4", "4"], pell="Y")
    more_students, more_records = graded("n", 15, ["4"], pell="N")
    few_students, few_records = graded("u", 3, ["W"], pell="U")
    for n, record in enumerate(records):
        record["delivery"] = "O" if n % 2 else None
    database = make_database(tmp_path / "pdp.sqlite", students + more_students + few_students, records + more_records + few_records)
    detail = dfw_course(**pick("2023-24"), course="eng  101", database=database)
    assert detail["course"] == "ENG 101"
    assert (detail["num"], detail["den"]) == (7, 30)
    assert [term["value"] for term in detail["terms"]] == ["Fall"]
    delivery = {part["value"]: part["den"] for part in detail["delivery"]}
    assert delivery == {"Online": 6, "Blank": 24}
    pell = {group["value"]: (group["num"], group["den"]) for group in detail["groups"]["pell"]}
    assert pell == {"N": (0, 15), "UNKNOWN": (3, 3), "Y": (4, 12)}
    intensity = {group["value"] for group in detail["groups"]["enrollment_intensity"]}
    assert intensity == {"Full-time"}  # stored as Full-Time, answered with the listed spelling


def test_every_d_letter_is_a_d(tmp_path):
    """F is an F or under 0.7; D-, D and D+ are all a D; a 1.99 is a C- and passes. They add up to the numerator."""
    database = build(tmp_path, graded("s", 10, ["0.0", "0.67", "0.7", "1.99", "1.5", "W", "F", "3.3", "1.0", "0.69"]))
    everyone = dfw_courses(**pick("2023-24"), database=database)["everyone"]
    assert split(everyone) == counts(d=3, f=4, w=1, total=10)
    assert everyone["num"] == 8
    assert everyone["split"]["shares"] == {"D": 0.3, "F": 0.4, "W": 0.1}


def test_answers_carry_the_grade_scale(tmp_path):
    """The list and the course detail both say which grades count, so the page's table matches its numbers."""
    database = build(tmp_path, graded("s", 10, ["F", "4"]))
    scale = dfw_courses(**pick("2023-24"), database=database)["context"]["grade_scale"]
    assert dfw_course(**pick("2023-24"), course="ENG 101", database=database)["context"]["grade_scale"] == scale
    assert [row["grade"] for row in scale["grades"] if row["counted"]] == ["D", "F", "W"]


def test_groups_are_compared_with_everyone_else_in_the_course(tmp_path):
    """Each group's rate next to the rest of the course, with the gap in points, computed by the API."""
    database = build(tmp_path, graded("y", 20, ["F", "4"], pell="Y"), graded("n", 20, ["4"], pell="N"))
    detail = dfw_course(**pick("2023-24"), course="ENG 101", database=database)
    pell = {group["value"]: group for group in detail["groups"]["pell"]}
    assert (pell["Y"]["rest_rate"], pell["Y"]["gap"]) == (0.0, 50.0)
    assert (pell["N"]["rest_rate"], pell["N"]["gap"]) == (0.5, -50.0)


def test_small_course_is_visible_and_unknown_course_is_an_error(tmp_path):
    """Small courses remain available; a nonexistent course raises UnknownCourse."""
    database = build(tmp_path, graded("s", 9, ["F"]))
    assert dfw_course(**pick("2023-24"), course="ENG 101", database=database)["den"] == 9
    with pytest.raises(UnknownCourse):
        dfw_course(**pick("2023-24"), course="NOPE 1", database=database)


def test_cohort_filters_pick_the_students(tmp_path):
    """The cohort bar selects whose grades count; empty selections have no rate."""
    database = build(tmp_path, graded("y", 12, ["F"], pell="Y"), graded("n", 10, ["4"], pell="N"))
    assert dfw_courses(**pick("2023-24", pell="Y"), database=database)["everyone"]["rate"] == 1.0
    assert dfw_courses(**pick("2023-24", pell="N"), database=database)["everyone"]["rate"] == 0.0
    assert dfw_courses(**pick("2023-24", pell="UNKNOWN"), database=database)["status"] == "suppressed"


@pytest.mark.slow
@pytest.mark.skipif(not DEFAULT_DATABASE.exists(), reason="the normalized data isn't loaded")
def test_real_data_known_answers():
    """2023-24, checked against the shared DFW measure's counts on pdp.sqlite (synthetic data)."""
    result = dfw_courses(**pick("2023-24"))
    assert split(result["everyone"]) == counts(d=548, f=2262, w=1477, total=18883)
    assert result["everyone"]["num"] == 4287  # the shared dfw_rate measure's numerator
    eng = dfw_course(**pick("2023-24"), course="ENG 101")
    assert (eng["num"], eng["den"]) == (133, 492)  # 135 under the old 2.0 line: two C- grades now pass
