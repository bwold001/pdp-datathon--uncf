"""Checks the Gateway courses numbers against a tiny made-up database with known answers, plus the real data."""
from __future__ import annotations

import pytest

from measures.run_measures import DEFAULT_DATABASE
from uncf.cohort import CohortQuery
from uncf.gateway_courses import gateway_courses
from uncf.tests.explorer_fixture import here, make_database, student

# These tests follow students back the next fall, so they count federal (fall to fall) retention.
FEDERAL = CohortQuery.of("2023-24", "federal")


def takers(prefix: str, count: int, grades: list[str], back: int, course=("ENG", "101"), gateway="E", **values):
    """count students who took one course in Fall 2023 (grades cycled); the first `back` return in Fall 2024."""
    students, records = [], []
    for n in range(count):
        student_id = f"{prefix}{n}"
        students.append(student(student_id, **values))
        records.append(here(student_id, "2023-24", "FALL", prefix=course[0], number=course[1], name="COMPOSITION I", grade=grades[n % len(grades)], gateway=gateway))
        if n < back:
            records.append(here(student_id, "2024-25", "FALL", prefix="HIS", number="101", grade="4"))
    return students, records


def build(tmp_path, *groups):
    """A database from groups made by takers()."""
    return make_database(tmp_path / "pdp.sqlite", [s for g in groups for s in g[0]], [r for g in groups for r in g[1]])


def test_outcomes_and_retention_by_course(tmp_path):
    """Passed (2.0 or more, or P), D or F, withdrew, other grades apart, and next-fall retention by outcome."""
    database = build(
        tmp_path,
        takers("pass", 12, ["4", "2.0", "P"], back=10),
        takers("fail", 10, ["1.7", "F"], back=2),
        takers("drop", 10, ["W"], back=1),
        takers("inc", 2, ["I"], back=0),
    )
    page = gateway_courses(FEDERAL, database=database)
    assert page["meta"]["flagged"] is True
    assert page["meta"]["retention_term"] == "Fall 2024"
    (course,) = page["courses"]
    assert course["course"] == "ENG 101"
    assert (course["students"], course["passed"], course["df"], course["w"]) == (32, 12, 10, 10)
    assert (course["d"], course["f"]) == (5, 5)
    assert page["left_out"] is None  # 2 incomplete across the listed courses: hidden
    assert course["other"] is None  # 2 incomplete: hidden
    assert course["retained_if_passed"] == {"students": 12, "retained": 10, "rate": 0.8333}
    assert course["retained_if_not_passed"] == {"students": 20, "retained": 3, "rate": 0.15}
    assert page["cohort_retention"]["retained"] == 13


def test_school_retention_is_the_pdp_flag(tmp_path):
    """The default retention type reads the PDP flag, so it can differ from who came back next fall."""
    flagged = takers("a", 12, ["4"], back=0, retention=1)
    unflagged = takers("b", 10, ["F"], back=10, retention=0)
    page = gateway_courses(CohortQuery.of("2023-24"), database=build(tmp_path, flagged, unflagged))
    assert page["meta"]["retention_type"] == "school"
    assert (page["cohort_retention"]["retained"], page["cohort_retention"]["students"]) == (12, 22)
    (course,) = page["courses"]
    assert course["retained_if_passed"]["rate"] == 1.0
    assert course["retained_if_not_passed"]["rate"] == 0.0


def test_first_attempt_counts_once(tmp_path):
    """A student who fails in fall and passes the same course in spring counts once, with the fall F."""
    students, records = takers("s", 10, ["F"], back=0)
    for s in students:
        records.append(here(s["student_id"], "2023-24", "SPRING", prefix="ENG", number="101", grade="4", gateway="E"))
    page = gateway_courses(FEDERAL, database=make_database(tmp_path / "pdp.sqlite", students, records))
    (course,) = page["courses"]
    assert (course["students"], course["passed"], course["df"]) == (10, 0, 10)


def test_unflagged_cohort_infers_math_and_english(tmp_path):
    """With no gateway flags at all, college-level math and English courses are inferred, and the page says so."""
    database = build(
        tmp_path,
        takers("e", 10, ["4"], back=5, gateway="N"),
        takers("m", 10, ["F"], back=5, course=("MATH", "111"), gateway="N"),
        takers("h", 10, ["4"], back=5, course=("HIS", "101"), gateway="N"),
    )
    page = gateway_courses(FEDERAL, database=database)
    assert page["meta"]["flagged"] is False
    assert [(c["course"], c["subject"]) for c in page["courses"]] == [("ENG 101", "E"), ("MATH 111", "M")]


def test_small_courses_are_hidden(tmp_path):
    """A gateway course with under 10 students isn't listed; it's counted as hidden."""
    database = build(tmp_path, takers("a", 12, ["4"], back=0), takers("b", 9, ["4"], back=0, course=("ENG", "102")))
    page = gateway_courses(FEDERAL, database=database)
    assert [c["course"] for c in page["courses"]] == ["ENG 101"]
    assert page["hidden_courses"] == 1


def test_pairs_below_the_cohort(tmp_path):
    """Two courses taken together in the first term by 10+ students, with retention under the cohort's."""
    students, records = takers("pair", 10, ["4"], back=1)
    for s in students:
        records.append(here(s["student_id"], "2023-24", "FALL", prefix="MATH", number="111", grade="4", gateway="M"))
    more_students, more_records = takers("solo", 10, ["4"], back=9, course=("BIO", "100"), gateway="N")
    page = gateway_courses(FEDERAL, database=make_database(tmp_path / "pdp.sqlite", students + more_students, records + more_records))
    assert page["meta"]["first_term"] == "Fall 2023"
    assert page["cohort_retention"]["rate"] == 0.5
    assert page["pairs"] == [{"courses": ["ENG 101", "MATH 111"], "students": 10, "retained": 1, "rate": 0.1, "gap": -40.0}]


def test_fewer_than_ten_students_hides_everything(tmp_path):
    """Nine students: no numbers at all."""
    page = gateway_courses(FEDERAL, build(tmp_path, takers("s", 9, ["4"], back=9)))
    assert page["status"] == "suppressed"
    assert page["courses"] == [] and page["pairs"] == []


@pytest.mark.slow
@pytest.mark.skipif(not DEFAULT_DATABASE.exists(), reason="the normalized data isn't loaded")
def test_real_data_known_answers():
    """2023-24, checked by hand with SQL on pdp.sqlite (synthetic data)."""
    page = gateway_courses(FEDERAL)
    assert page["meta"]["flagged"] is True
    retention = page["cohort_retention"]
    assert (retention["students"], retention["retained"], retention["rate"]) == (2580, 1074, 0.4163)
    school = gateway_courses(CohortQuery.of("2023-24"))["cohort_retention"]
    assert (school["students"], school["retained"]) == (2580, 1345)  # the PDP flag, as in the Results API
    eng = next(c for c in page["courses"] if c["course"] == "ENG 101")
    assert (eng["students"], eng["passed"], eng["df"], eng["w"]) == (380, 277, 76, 27)
