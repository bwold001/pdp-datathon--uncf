"""Checks the Gateway courses numbers against a tiny made-up database with known answers, plus the real data."""
from __future__ import annotations

import pytest

from measures.breakdowns.gateway_courses import best_grade, gateway_courses, gateway_passed
from measures.run_measures import DEFAULT_DATABASE
from measures.tests.explorer_fixture import ask, here, make_database, student

# These tests follow students back the next fall, so they count federal (fall to fall) retention.
FEDERAL = ask("2023-24", "federal")


def takers(prefix: str, count: int, grades: list[str], back: int, course=("ENG", "101"), gateway="E", season="FALL", **values):
    """count students who took one course in year 1 (grades cycled); the first `back` return in Fall 2024."""
    students, records = [], []
    for n in range(count):
        student_id = f"{prefix}{n}"
        students.append(student(student_id, **values))
        records.append(here(student_id, "2023-24", season, prefix=course[0], number=course[1], name="COMPOSITION I", grade=grades[n % len(grades)], gateway=gateway))
        if n < back:
            records.append(here(student_id, "2024-25", "FALL", prefix="HIS", number="101", grade="4"))
    return students, records


def build(tmp_path, *groups):
    """A database from groups made by takers()."""
    return make_database(tmp_path / "pdp.sqlite", [s for g in groups for s in g[0]], [r for g in groups for r in g[1]])


def retake(students: list[dict], records: list[dict], grade: str, year="2023-24", season="SPRING") -> None:
    """Add a second try at ENG 101 for every student, in a later term."""
    for s in students:
        records.append(here(s["student_id"], year, season, prefix="ENG", number="101", grade=grade, gateway="E"))


def test_gateway_pass_line_is_one_point_zero():
    """The PDP's gateway line: 1.0 or higher, or P, passes; F, W and under 1.0 don't; non-final grades are None."""
    assert [gateway_passed(g) for g in ("4", "2.0", "1.7", "1.0", "1", "P")] == [True] * 6
    assert [gateway_passed(g) for g in ("0.7", "0", "F", "W")] == [False] * 4
    assert [gateway_passed(g) for g in ("I", "A", "MIS", None)] == [None] * 4


def test_first_try_path_and_retention(tmp_path):
    """Passed first try, retook and passed, retook and didn't, didn't retake; and retention by passing in the end."""
    first = takers("first", 12, ["4", "1.3", "P"], back=10)
    later = takers("later", 10, ["F"], back=6)
    retake(*later, grade="2.0")
    again = takers("again", 10, ["0.7"], back=1)
    retake(*again, grade="W")
    once = takers("once", 10, ["W"], back=0)
    page = gateway_courses(**FEDERAL, database=build(tmp_path, first, later, again, once))
    assert page["context"]["flagged"] is True
    (course,) = page["courses"]
    assert (course["course"], course["subject"], course["students"]) == ("ENG 101", "E", 42)
    assert (course["first_pass"], course["passed"]) == (12, 22)
    assert course["path"] == {"first": 12, "retook_passed": 10, "retook_not": 10, "no_retake": 10}
    assert course["retained_if_passed"] == {"students": 22, "retained": 16, "rate": 0.7273}
    assert course["retained_if_not_passed"] == {"students": 20, "retained": 1, "rate": 0.05}
    assert course["all_takers"] is None  # no filters, so nothing to compare


def test_every_grade_is_counted_apart(tmp_path):
    """Each try's letter, one per student per term: all letters from A to W, zeros included, adding up to the tries."""
    first = takers("first", 12, ["4", "1.5", "P", "0.3"], back=0)
    retake(*first, grade="2.0")
    page = gateway_courses(**FEDERAL, database=build(tmp_path, first))
    (course,) = page["courses"]
    grades = course["grades"]
    assert list(grades) == ["A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "D-", "F", "P", "W"]
    # First tries: 3 each of A, D+ (1.5), P and F (0.3); then a C for all 12 on the retake.
    assert {grade: count for grade, count in grades.items() if count} == {"A": 3, "D+": 3, "P": 3, "F": 3, "C": 12}
    assert sum(grades.values()) == 24
    assert page["context"]["grade_scale"]["grades"][-1] == {"grade": "W", "points": "the code W (withdrew)", "dfw": True, "gateway_pass": False}


def test_a_term_listed_twice_keeps_the_better_grade():
    """Duplicate class rows in one term are one try: a passing grade wins, then the higher letter."""
    assert best_grade(["F", "C"]) == "C"
    assert best_grade(["W", "F"]) == "F"
    assert best_grade(["D-", "P"]) == "P"
    assert best_grade(["B", "A-"]) == "A-"


def test_one_try_per_term(tmp_path):
    """Two rows in one term (duplicate class rows) are one try, passed if either passed."""
    students, records = takers("s", 10, ["F"], back=0)
    retake(students, records, grade="3", season="FALL")
    page = gateway_courses(**FEDERAL, database=make_database(tmp_path / "pdp.sqlite", students, records))
    (course,) = page["courses"]
    assert (course["first_pass"], course["path"]["first"], course["path"]["retook_passed"]) == (10, 10, 0)
    assert (course["grades"]["B"], course["grades"]["F"]) == (10, 0)  # the B wins over the F in the same term


def test_only_year_one_counts(tmp_path):
    """A pass in year 2 doesn't count: like the PDP measure, the page looks at the first academic year only."""
    students, records = takers("s", 10, ["F"], back=0)
    retake(students, records, grade="4", year="2024-25", season="FALL")
    page = gateway_courses(**FEDERAL, database=make_database(tmp_path / "pdp.sqlite", students, records))
    (course,) = page["courses"]
    assert (course["passed"], course["path"]["no_retake"]) == (0, 10)
    assert page["context"]["year_one"] == "2023-24"


def test_only_flagged_grades_count_and_nothing_is_guessed(tmp_path):
    """Unflagged math and English courses aren't gateway courses; with no flags the page lists none."""
    database = build(
        tmp_path,
        takers("e", 10, ["4"], back=5, gateway="N"),
        takers("m", 10, ["F"], back=5, course=("MATH", "111"), gateway="N"),
    )
    page = gateway_courses(**FEDERAL, database=database)
    assert page["context"]["flagged"] is False
    assert page["courses"] == []


def test_filtered_students_and_everyone_who_took_the_course(tmp_path):
    """With a filter, a course counts the filtered students and everyone who took it, for the API to compare."""
    pell = takers("p", 20, ["F", "F", "F", "4"], back=0, pell="Y")
    other = takers("n", 20, ["4", "4", "4", "F"], back=0, pell="N")
    page = gateway_courses(**ask("2023-24", "federal", pell="Y"), database=build(tmp_path, pell, other))
    assert page["context"]["compared"] is True
    (course,) = page["courses"]
    assert (course["students"], course["first_pass"]) == (20, 5)
    assert course["all_takers"] == {"students": 40, "first_pass": 20}


def test_small_courses_are_hidden(tmp_path):
    """A gateway course with under 10 students isn't listed; it's counted as hidden."""
    database = build(tmp_path, takers("a", 12, ["4"], back=0), takers("b", 9, ["4"], back=0, course=("ENG", "102")))
    page = gateway_courses(**FEDERAL, database=database)
    assert [c["course"] for c in page["courses"]] == ["ENG 101"]
    assert page["hidden_courses"] == 1


def pairs_database(tmp_path):
    """ENG 101 + BIO 100 taken together by 10 who mostly left; HIS 100 alone by 10 who stayed; ART + MUS by 10."""
    students, records = takers("pair", 10, ["4"], back=1)
    for s in students:
        records.append(here(s["student_id"], "2023-24", "FALL", prefix="BIO", number="100", grade="4"))
    solo_students, solo_records = takers("solo", 10, ["4"], back=9, course=("HIS", "100"), gateway="N")
    plain_students, plain_records = takers("plain", 10, ["4"], back=0, course=("ART", "100"), gateway="N")
    for s in plain_students:
        plain_records.append(here(s["student_id"], "2023-24", "FALL", prefix="MUS", number="100", grade="4"))
    return make_database(tmp_path / "pdp.sqlite", students + solo_students + plain_students, records + solo_records + plain_records)


def test_pairs_need_a_gateway_course(tmp_path):
    """Pairs are counted in the first term, and only when one of the two courses is a gateway course."""
    page = gateway_courses(**FEDERAL, database=pairs_database(tmp_path))
    assert page["context"]["first_term"] == "Fall 2023"
    assert page["pair_counts"] == [{"courses": ["BIO 100", "ENG 101"], "students": 10, "retained": 1}]
    assert page["pairs_considered"] == 1  # ART + MUS has no gateway course


def test_fewer_than_ten_students_hides_everything(tmp_path):
    """Nine students: no numbers at all."""
    page = gateway_courses(**FEDERAL, database=build(tmp_path, takers("s", 9, ["4"], back=9)))
    assert page["status"] == "suppressed"
    assert page["courses"] == [] and page["pair_counts"] == []


@pytest.mark.slow
@pytest.mark.skipif(not DEFAULT_DATABASE.exists(), reason="the normalized data isn't loaded")
def test_real_data_known_answers():
    """2023-24 on pdp.sqlite (synthetic data): cohort retention as before, and ENG 101's path adds up."""
    page = gateway_courses(**FEDERAL)
    assert page["context"]["flagged"] is True
    retention = page["cohort_retention"]
    assert (retention["students"], retention["retained"], retention["rate"]) == (2580, 1074, 0.4163)
    school = gateway_courses(**ask("2023-24"))["cohort_retention"]
    assert (school["students"], school["retained"]) == (2580, 1345)  # the PDP flag, as on /measures/retention
    eng = next(c for c in page["courses"] if c["course"] == "ENG 101")
    steps = [eng["path"][step] or 0 for step in ("first", "retook_passed", "retook_not", "no_retake")]
    assert eng["path"]["first"] == eng["first_pass"]
    assert sum(steps) <= eng["students"] and eng["passed"] >= eng["first_pass"]
