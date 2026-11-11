"""Checks the UNCF_MIN_STUDENTS setting: by default every group with students is shown; set to 10, small ones hide."""
from __future__ import annotations

import pytest

from measures.breakdowns.common import shown
from measures.breakdowns.dfw_courses import dfw_courses
from measures.breakdowns.gateway_courses import gateway_courses
from measures.models import Cohort, GroupBy, GroupDimension, Measure, Status, min_students
from measures.run_measures import run_measure
from measures.tests.explorer_fixture import ask, here, make_database, student


@pytest.fixture
def default(monkeypatch):
    """The setting as a fresh deployment has it: not set."""
    monkeypatch.delenv("UNCF_MIN_STUDENTS", raising=False)


def test_default_shows_every_group_with_students(default, monkeypatch):
    """Unset (or blank) is 1; a number sets the smallest group shown."""
    assert min_students() == 1
    monkeypatch.setenv("UNCF_MIN_STUDENTS", " ")
    assert min_students() == 1
    monkeypatch.setenv("UNCF_MIN_STUDENTS", "10")
    assert min_students() == 10


@pytest.mark.parametrize("value", ["0", "-1", "ten", "2.5"])
def test_a_bad_setting_is_refused(monkeypatch, value):
    """A value that isn't a whole number of 1 or more stops with a clear message instead of guessing."""
    monkeypatch.setenv("UNCF_MIN_STUDENTS", value)
    with pytest.raises(ValueError, match="UNCF_MIN_STUDENTS"):
        min_students()


@pytest.fixture
def three_pell_students(tmp_path):
    """2022-23: 3 Pell students (2 retained) and 12 non-Pell (6 retained); nobody with an unknown Pell status."""
    students = [student(f"y{n}", "2022-23", pell="Y", retention=int(n < 2)) for n in range(3)]
    students += [student(f"n{n}", "2022-23", pell="N", retention=int(n < 6)) for n in range(12)]
    return make_database(tmp_path / "pdp.sqlite", students, [])


def pell_rows(database) -> dict[str, object]:
    """Retention for 2022-23 by Pell, keyed by Pell value."""
    rows = run_measure(Measure.RETENTION, [Cohort.of("2022-23")], [GroupBy.of(GroupDimension.PELL)], database=database)
    return {next(iter(row.group.parts)).value: row for row in rows[1:]}


def test_a_group_of_three_is_shown_by_default(default, three_pell_students):
    """The 3 Pell students get their own numbers; a group with nobody in it still has none."""
    rows = pell_rows(three_pell_students)
    assert (rows["Y"].status, rows["Y"].numerator, rows["Y"].denominator) == (Status.OK, 2, 3)
    assert rows["UNKNOWN"].status == Status.SUPPRESSED and rows["UNKNOWN"].numerator is None


def test_the_same_group_hides_at_ten(monkeypatch, three_pell_students):
    """Set to 10, as for real student data, the 3 Pell students are hidden again."""
    monkeypatch.setenv("UNCF_MIN_STUDENTS", "10")
    rows = pell_rows(three_pell_students)
    assert rows["Y"].status == Status.SUPPRESSED and rows["Y"].numerator is None
    assert rows["N"].status == Status.OK


def test_page_counts_follow_the_setting(default, monkeypatch):
    """A page shows a count of 3 by default, and hides it at 10. 0 is always shown as 0."""
    assert (shown(3), shown(0)) == (3, 0)
    monkeypatch.setenv("UNCF_MIN_STUDENTS", "10")
    assert (shown(3), shown(0)) == (None, 0)


def test_course_pairs_are_ranked_only_with_ten_students(default, tmp_path):
    """Small courses are shown by default, but a pair of courses needs 10 students to be ranked as risky."""
    students, records = [], []
    for n in range(15):
        sid = f"s{n}"
        students.append(student(sid))
        records.append(here(sid, "2023-24", "FALL", prefix="ENG", number="101", grade="3", gateway="E"))
        if n < 3:  # 3 students also took MAT 101, and none came back
            records.append(here(sid, "2023-24", "FALL", prefix="MAT", number="101", grade="3", gateway="M"))
        else:
            records.append(here(sid, "2024-25", "FALL", prefix="HIS", number="101", grade="4"))
    page = gateway_courses(**ask("2023-24", "federal"), database=make_database(tmp_path / "pdp.sqlite", students, records))
    assert {course["course"]: course["students"] for course in page["courses"]} == {"ENG 101": 15, "MAT 101": 3}
    assert page["context"]["min_pair_students"] == 10
    assert (page["pairs"], page["pairs_considered"]) == ([], 0)


def test_dfw_list_leaves_out_courses_under_ten_grades(default, tmp_path):
    """By default every course has its numbers, but the list only sends courses with 10 or more final grades."""
    students = [student(f"s{n}") for n in range(15)]
    records = [here(f"s{n}", "2023-24", "FALL", prefix="ENG", number="101", grade="3") for n in range(15)]
    records += [here(f"s{n}", "2023-24", "FALL", prefix="ART", number="105", grade="W") for n in range(3)]
    page = dfw_courses("2023-24", database=make_database(tmp_path / "pdp.sqlite", students, records))
    assert [course["course"] for course in page["courses"]] == ["ENG 101"]
    assert page["hidden_courses"] == 1
    assert (page["everyone"]["num"], page["everyone"]["den"]) == (3, 18)  # ART 105's 3 grades still count
