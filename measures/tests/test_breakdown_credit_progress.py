"""Checks meaningful progress toward a degree (the Credit momentum design) against made-up students with known answers,
plus the design's own numbers on the real data."""
from __future__ import annotations

import pytest

from measures.breakdowns.credit_momentum import credit_momentum
from measures.run_measures import DEFAULT_DATABASE
from measures.tests.explorer_fixture import ask, here, make_database, student


def group(prefix: str, count: int, courses: list[dict], spring: bool = True, year_two: list[dict] = (), **values):
    """count students who took these year 1 Fall courses, a 3-credit course in Spring that doesn't count (unless
    spring=False), and these year 2 courses. A course is a dict of here()'s values: attempted, earned, grade, course_type."""
    students, records = [], []
    # The page needs the cohort file's year 1 credits too (its other sections), so every student has some.
    values = {"attempted": 12, "earned": 12, **values}
    for n in range(count):
        student_id = f"{prefix}{n}"
        students.append(student(student_id, **values))
        records += [here(student_id, "2023-24", "FALL", **course) for course in courses]
        if spring:
            # Passed, but not credit that counts, so it never decides a group or a reason.
            records.append(here(student_id, "2023-24", "SPRING", attempted=3, earned=3, grade="4", course_type="NC"))
        records += [here(student_id, "2024-25", "FALL", **course) for course in year_two]
    return students, records


def credits(attempted: float, earned: float | None = None, grade: str = "4", course_type: str = "CU") -> dict:
    """One course: credits attempted and earned (earned defaults to attempted), its grade and PDP course type."""
    return {"attempted": attempted, "earned": attempted if earned is None else earned, "grade": grade, "course_type": course_type}


def build(tmp_path, *groups):
    """A database from groups made by group()."""
    return make_database(tmp_path / "pdp.sqlite", [s for g in groups for s in g[0]], [r for g in groups for r in g[1]])


def progress_of(database, **filters) -> dict:
    """The progress section of the Credit momentum page for 2023-24."""
    return credit_momentum(**ask("2023-24", **filters), database=database)["progress"]


def test_year_one_groups(tmp_path):
    """30 or more credits that count is on pace, 24 to 29 the minimum; under 24 is below it, or stopped with no spring."""
    database = build(
        tmp_path,
        group("pace", 10, [credits(30)], retention=1),
        group("min", 10, [credits(26)], retention=1),
        group("below", 10, [credits(12)]),
        group("stop", 10, [credits(12)], spring=False, retention=0),
    )
    page = progress_of(database)
    assert page["settings"]["pace"] == 30 and page["settings"]["minimum"] == 24
    assert page["next_term"] == "Spring 2024"
    assert [(b["key"], b["students"], b["share"]) for b in page["bands"]] == [
        ("pace", 10, 0.25), ("minimum", 10, 0.25), ("below", 10, 0.25), ("stopped", 10, 0.25),
    ]
    assert page["minimum"] == {"students": 20, "share": 0.5}
    assert page["pace"] == {"students": 10, "share": 0.25}
    # Retention by group uses the chosen measure's answers: the PDP flag by default, unknown for the below group.
    assert [b["retention"]["retained"] for b in page["bands"]] == [10, 10, None, 0]


def test_only_college_level_and_applicable_developmental_credit_counts(tmp_path):
    """CU and CC count; developmental credit that doesn't apply (CD) or other types don't."""
    database = build(
        tmp_path,
        group("cu", 10, [credits(15), credits(15, course_type="CC")]),
        group("cd", 10, [credits(15), credits(15, course_type="CD")]),
    )
    page = progress_of(database)
    assert [(b["key"], b["students"]) for b in page["bands"]] == [("pace", 10), ("minimum", 0), ("below", 10), ("stopped", 0)]
    # Passed 30, but only 15 count toward a degree.
    assert {r["key"]: r["students"] for r in page["below"]["reasons"]}["not_counted"] == 10


def test_why_below_the_minimum(tmp_path):
    """Signed up for too few; else not all of it counts; else whichever cost more credits, F grades or withdrawals."""
    database = build(
        tmp_path,
        group("under", 10, [credits(12)]),
        group("failed", 10, [credits(12), credits(9, 0, "F"), credits(3, 0, "W")]),
        group("withdrew", 10, [credits(12), credits(3, 0, "F"), credits(9, 0, "W")]),
        group("notcounted", 10, [credits(12), credits(12, course_type="CD")]),
        group("even", 10, [credits(12), credits(6, 0, "F"), credits(6, 0, "W")]),
    )
    below = progress_of(database)["below"]
    assert below["students"] == 50
    assert [(r["key"], r["students"], r["share"]) for r in below["reasons"]] == [
        ("under", 10, 0.2), ("failed", 10, 0.2), ("withdrew", 10, 0.2), ("not_counted", 10, 0.2),
    ]
    # An even split explains nothing, so those students are counted apart.
    assert below["unexplained"] == 10


def test_failing_follows_the_dfw_grade_rule(tmp_path):
    """A 0.3 is an F, a 0.7 a D (the DFW measure's rule), so 0.7s don't count as failed."""
    database = build(
        tmp_path,
        group("low", 10, [credits(12), credits(12, 0, "0.3")]),
        group("d", 10, [credits(12), credits(12, 0, "0.7")]),
    )
    reasons = {r["key"]: r["students"] for r in progress_of(database)["below"]["reasons"]}
    assert reasons["failed"] == 10
    assert progress_of(database)["below"]["unexplained"] == 10


def test_higher_degree_total_and_two_year_pace(tmp_path):
    """125 credits means 31.25 a year, so 31 isn't on pace; two-year pace is 60 or more that count over years 1 and 2."""
    database = build(
        tmp_path,
        group("p31", 10, [credits(31)], year_two=[credits(29)]),
        group("p32", 10, [credits(32)], year_two=[credits(28)]),
        group("slow", 10, [credits(24)], year_two=[credits(12)]),
    )
    page = progress_of(database)
    assert page["higher_pace"] == {"students": 10, "share": 0.3333}
    assert page["two_year_pace"] == {"status": "ok", "students": 20, "share": 0.6667}


def test_year_two_follow_up(tmp_path):
    """Of those who did the minimum: again in year 2, kept taking courses but fell under it, or took none."""
    database = build(
        tmp_path,
        group("again", 10, [credits(24)], year_two=[credits(24)]),
        group("fell", 10, [credits(24)], year_two=[credits(12)]),
        group("left", 10, [credits(24)]),
        group("other", 10, [credits(12)], year_two=[credits(30)]),
    )
    page = progress_of(database)
    follow_up = page["year_two_follow_up"]
    assert follow_up["status"] == "ok" and follow_up["students"] == 30
    assert (follow_up["again"]["students"], follow_up["kept_taking_courses"]["students"], follow_up["no_courses"]["students"]) == (10, 10, 10)
    assert follow_up["again"]["share"] == 0.3333
    # Both years, of everyone: the "other" group did the minimum in year 2 only, so it doesn't count.
    assert page["both_years"] == {"students": 10, "share": 0.25}


def test_year_two_not_in_the_data_yet(tmp_path):
    """With no year 2 term in the data, the year 2 numbers are not yet observable, never 0."""
    database = build(tmp_path, group("min", 12, [credits(24)]))
    page = progress_of(database)
    assert page["year_two_follow_up"]["status"] == "not_yet_observable"
    assert page["year_two_follow_up"]["again"]["students"] is None
    assert page["two_year_pace"] == {"status": "not_yet_observable", "students": None, "share": None}
    assert page["both_years"]["students"] is None


def test_small_groups_are_hidden(tmp_path):
    """A group or reason of 1 to 9 students is None, and so is its share; the page still answers for the rest."""
    database = build(tmp_path, group("min", 15, [credits(24)]), group("stop", 4, [credits(6)], spring=False))
    page = progress_of(database)
    bands = {b["key"]: b for b in page["bands"]}
    assert (bands["stopped"]["students"], bands["stopped"]["share"]) == (None, None)
    assert bands["stopped"]["retention"]["rate"] is None
    assert (bands["below"]["students"], bands["minimum"]["students"]) == (0, 15)


def test_filters_narrow_every_number(tmp_path):
    """The cohort bar's filters pick the students first, so every count is among them."""
    database = build(tmp_path, group("y", 10, [credits(30)], pell="Y"), group("n", 10, [credits(12)], pell="N"))
    page = progress_of(database, pell="Y")
    assert page["pace"] == {"students": 10, "share": 1.0}
    assert [b["students"] for b in page["bands"]] == [10, 0, 0, 0]


def test_too_few_students(tmp_path):
    """Fewer than 10 students: the page is hidden, progress too."""
    database = build(tmp_path, group("few", 5, [credits(30)]))
    assert credit_momentum(**ask("2023-24"), database=database)["progress"] is None


@pytest.mark.slow
@pytest.mark.skipif(not DEFAULT_DATABASE.exists(), reason="the normalized data isn't loaded")
def test_real_data_matches_the_design():
    """Fall 2022 starters (synthetic data): the numbers in the Credit momentum design, which has one student fewer.

    The design counts 762 below the minimum (520 retained), 538 signed up for too few, 122 who did the minimum twice
    and 100 who kept taking courses; the one more student here lands in each of those.
    """
    page = credit_momentum(**ask("2022-23", cohort_term="Fall"))["progress"]
    assert page["next_term"] == "Spring 2023"
    assert [(b["key"], b["students"], b["retention"]["retained"]) for b in page["bands"]] == [
        ("pace", 133, 126), ("minimum", 172, 154), ("below", 763, 521), ("stopped", 521, 130),
    ]
    assert [r["students"] for r in page["below"]["reasons"]] == [539, 110, 66, 31]
    assert page["below"]["unexplained"] == 17
    assert (page["higher_pace"]["students"], page["two_year_pace"]["students"]) == (78, 70)
    follow_up = page["year_two_follow_up"]
    assert (follow_up["again"]["students"], follow_up["kept_taking_courses"]["students"], follow_up["no_courses"]["students"]) == (123, 99, 83)
