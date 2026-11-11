"""Every nonempty synthetic group stays visible, even with obsolete threshold settings."""
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
    """Compatibility metadata stays at one regardless of obsolete settings."""
    assert min_students() == 1
    monkeypatch.setenv("UNCF_MIN_STUDENTS", " ")
    assert min_students() == 1
    monkeypatch.setenv("UNCF_MIN_STUDENTS", "10")
    assert min_students() == 1


@pytest.mark.parametrize("value", ["0", "-1", "ten", "2.5"])
def test_obsolete_setting_is_ignored(monkeypatch, value):
    """Obsolete configuration values cannot change visibility or stop calculations."""
    monkeypatch.setenv("UNCF_MIN_STUDENTS", value)
    assert min_students() == 1


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


def test_legacy_setting_cannot_hide_small_groups(monkeypatch, three_pell_students):
    """An old threshold of ten cannot hide the three Pell students."""
    monkeypatch.setenv("UNCF_MIN_STUDENTS", "10")
    rows = pell_rows(three_pell_students)
    assert (rows["Y"].status, rows["Y"].numerator, rows["Y"].denominator) == (Status.OK, 2, 3)
    assert rows["N"].status == Status.OK


def test_page_counts_follow_the_setting(default, monkeypatch):
    """Known counts remain visible, including zero, regardless of obsolete settings."""
    assert (shown(3), shown(0)) == (3, 0)
    monkeypatch.setenv("UNCF_MIN_STUDENTS", "10")
    assert (shown(3), shown(0)) == (3, 0)


@pytest.mark.parametrize("size", range(1, 10))
def test_small_course_pairs_are_compared(default, tmp_path, size):
    """Pairs of one to nine students remain eligible for comparison."""
    students, records = [], []
    for n in range(size + 12):
        sid = f"s{n}"
        students.append(student(sid))
        records.append(here(sid, "2023-24", "FALL", prefix="ENG", number="101", grade="3", gateway="E"))
        if n < size:  # The small pair never returns; twelve other students do.
            records.append(here(sid, "2023-24", "FALL", prefix="MAT", number="101", grade="3", gateway="M"))
        else:
            records.append(here(sid, "2024-25", "FALL", prefix="HIS", number="101", grade="4"))
    page = gateway_courses(**ask("2023-24", "federal"), database=make_database(tmp_path / "pdp.sqlite", students, records))
    assert {course["course"]: course["students"] for course in page["courses"]} == {"ENG 101": size + 12, "MAT 101": size}
    assert page["context"]["min_pair_students"] == 1
    assert page["pairs_considered"] == 1
    assert page["pair_counts"][0]["students"] == size

    from gap_finder.gateway import add_gateway_gaps

    compared = add_gateway_gaps(page)
    assert compared["pairs"][0]["students"] == size
    assert compared["pairs"][0]["rate"] == 0
    assert compared["pairs"][0]["others_rate"] == 1


def test_dfw_list_includes_courses_under_ten_grades(default, tmp_path):
    """Courses with three final grades appear alongside larger courses."""
    students = [student(f"s{n}") for n in range(15)]
    records = [here(f"s{n}", "2023-24", "FALL", prefix="ENG", number="101", grade="3") for n in range(15)]
    records += [here(f"s{n}", "2023-24", "FALL", prefix="ART", number="105", grade="W") for n in range(3)]
    page = dfw_courses("2023-24", database=make_database(tmp_path / "pdp.sqlite", students, records))
    assert [course["course"] for course in page["courses"]] == ["ART 105", "ENG 101"]
    assert page["hidden_courses"] == 0
    assert (page["everyone"]["num"], page["everyone"]["den"]) == (3, 18)  # ART 105's 3 grades still count


def test_the_dfw_definition_says_what_is_hidden(default, monkeypatch):
    """Definitions never claim that a minimum-size hiding policy applies."""
    from measures.definitions import definition_for

    assert not any("fewer than" in line for line in definition_for("dfw_rate")["limits"])
    monkeypatch.setenv("UNCF_MIN_STUDENTS", "10")
    assert not any("fewer than" in line for line in definition_for("dfw_rate")["limits"])
