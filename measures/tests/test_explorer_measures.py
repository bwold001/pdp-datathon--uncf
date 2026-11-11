"""Checks what the Explorer added to the measures: filters, federal retention, the D/F/W split, DFW's term and
delivery groups, and per student answers."""
from __future__ import annotations

import pytest

from measures.calculations.dfw import grade_result
from measures.models import (
    EVERYONE,
    Cohort,
    Group,
    GroupBy,
    GroupDimension,
    Measure,
    MeasureResult,
    Status,
)
from measures.run_measures import DEFAULT_DATABASE, read_answers, run_measure
from measures.tests.explorer_fixture import here, make_database, student

COHORTS = ["2021-22", "2022-23", "2023-24", "2024-25"]
needs_data = pytest.mark.skipif(not DEFAULT_DATABASE.exists(), reason="the normalized data isn't loaded")


@pytest.mark.parametrize(
    ("grade", "result"),
    [("F", "F"), ("0", "F"), ("0.3", "F"), ("0.69", "F"), ("0.7", "D-"), ("0.99", "D-"), ("1", "D"), ("1.3", "D+"),
     ("1.5", "D+"), ("1.69", "D+"), ("1.7", "C-"), ("1.99", "C-"), ("2.0", "C"), ("2.5", "C+"), ("3.6", "B+"),
     ("3.67", "B+"), ("4", "A"), ("4.00", "A"), ("P", "P"), ("W", "W"), (" w ", "W"), ("I", None), ("A", None),
     ("UNKNOWN", None), (None, None), ("UW", None)],
)
def test_grade_result_gives_each_grade_its_letter(grade, result):
    """A number takes the highest letter it reaches (1.5 is a D+), under 0.7 is an F; grades that aren't final are None."""
    assert grade_result(grade) == result


@pytest.fixture
def database(tmp_path):
    """2022-23: 12 Pell and 12 non-Pell students; 8 Pell and 3 non-Pell back in Fall 2023, each with a grade."""
    students = [student(f"y{n}", "2022-23", pell="Y", retention=1) for n in range(12)]
    students += [student(f"n{n}", "2022-23", pell="N", retention=int(n < 6)) for n in range(12)]
    grades = ["0.5", "1.5", "W", "4"]
    records = [here(f"y{n}", "2022-23", "FALL", cohort="2022-23", grade=grades[n % 4]) for n in range(12)]
    records += [here(f"n{n}", "2022-23", "SPRING", cohort="2022-23", grade="3") for n in range(12)]
    records += [here(f"y{n}", "2023-24", "FALL", cohort="2022-23", grade="3") for n in range(8)]
    records += [here(f"n{n}", "2023-24", "FALL", cohort="2022-23", grade="3") for n in range(3)]
    return make_database(tmp_path / "pdp.sqlite", students, records)


def everyone(measure: Measure, database, filters: Group = EVERYONE) -> MeasureResult:
    """The everyone row of one measure for 2022-23."""
    return run_measure(measure, [Cohort.of("2022-23")], database=database, filters=filters)[0]


def test_filters_count_only_matching_students(database):
    """A filter narrows everyone to the students who match it."""
    pell = Group.of((GroupDimension.PELL, "Y"))
    row = everyone(Measure.RETENTION, database, pell)
    assert (row.numerator, row.denominator) == (12, 12)
    assert (everyone(Measure.RETENTION, database).numerator, everyone(Measure.RETENTION, database).denominator) == (18, 24)


def test_filtered_rows_are_not_saved(database):
    """The results table has no column for filters, so saving a filtered run is refused."""
    with pytest.raises(ValueError, match="filtered"):
        run_measure(Measure.RETENTION, [Cohort.of("2022-23")], database=database, filters=Group.of((GroupDimension.PELL, "Y")), save=True)


def test_federal_retention_is_fall_to_fall(database):
    """Federal retention counts students who took a course here the fall after year 1."""
    row = everyone(Measure.FEDERAL_RETENTION, database)
    assert (row.numerator, row.denominator, row.status) == (11, 24, Status.OK)
    pell = run_measure(Measure.FEDERAL_RETENTION, [Cohort.of("2022-23")], [GroupBy.of(GroupDimension.PELL)], database=database)
    assert {r.group.label: r.numerator for r in pell[1:] if r.numerator is not None} == {"pell=N": 3, "pell=Y": 8}


def test_federal_retention_waits_for_the_next_fall(tmp_path):
    """A cohort whose next fall isn't in the course file has no answers yet."""
    students = [student(f"s{n}", "2023-24") for n in range(12)]
    records = [here(f"s{n}", "2023-24", "FALL", cohort="2023-24", grade="3") for n in range(12)]
    database = make_database(tmp_path / "pdp.sqlite", students, records)
    (row,) = run_measure(Measure.FEDERAL_RETENTION, [Cohort.of("2023-24")], database=database)
    assert row.status == Status.NOT_YET_OBSERVABLE


def test_dfw_rows_split_each_dfw_grade(database):
    """D+, D, D-, F and W add up to the DFW numerator, and the term and delivery groups add up to everyone."""
    rows = run_measure(Measure.DFW_RATE, [Cohort.of("2022-23")], [GroupBy.of(GroupDimension.TERM), GroupBy.of(GroupDimension.DELIVERY)], database=database)
    total = rows[0]
    # The fixture's 1.5s are D+ and its 0.5s are F.
    assert total.split == {"D+": 3, "D": 0, "D-": 0, "F": 3, "W": 3}
    assert (total.numerator, total.denominator, total.n_students) == (9, 35, 24)
    terms = {r.group.label: r.denominator for r in rows[1:] if r.group.parts and next(iter(r.group.parts)).dimension == GroupDimension.TERM}
    assert terms == {"term=FALL": 23, "term=SPRING": 12}


def test_dfw_course_filter(database):
    """A course is a filter too: one course's rows only."""
    course = Group.of((GroupDimension.COURSE, "ENG 101"))
    row = everyone(Measure.DFW_RATE, database, course)
    assert row.denominator == 35  # every record above is ENG 101


def test_read_answers_match_run_measure(database):
    """Per student answers count up to run_measure's numbers."""
    answers, observable = read_answers(Measure.FEDERAL_RETENTION, "2022-23", database)
    assert observable is True
    assert (sum(answers.values()), len(answers)) == (11, 24)
    with pytest.raises(ValueError):
        read_answers(Measure.DFW_RATE, "2022-23", database)


@pytest.mark.slow
@needs_data
def test_known_answers_on_the_real_data():
    """Synthetic data: retention 2022-23 school 1,414/2,617, federal 926/2,617; DFW 2023-24 4,287 of 18,883."""
    school = run_measure(Measure.RETENTION, [Cohort.of("2022-23")])[0]
    federal = run_measure(Measure.FEDERAL_RETENTION, [Cohort.of("2022-23")])[0]
    dfw = run_measure(Measure.DFW_RATE, [Cohort.of("2023-24")])[0]
    assert (school.numerator, school.denominator) == (1414, 2617)
    assert (federal.numerator, federal.denominator) == (926, 2617)
    # A C- passes, so the 60 C- grades that counted under the old 2.0 line (4,347) don't.
    assert (dfw.numerator, dfw.denominator) == (4287, 18883)
    assert dfw.split == {"D+": 38, "D": 486, "D-": 24, "F": 2262, "W": 1477}


@pytest.mark.slow
@needs_data
@pytest.mark.parametrize("measure", [Measure.RETENTION, Measure.FEDERAL_RETENTION, Measure.PERSISTENCE, Measure.CREDIT_COMPLETION, Measure.DFW_RATE])
def test_a_filter_equals_its_group_row(measure):
    """Filtering by pell=Y gives the same numbers as the pell=Y row of a pell grouping, for every class."""
    for cohort in COHORTS:
        grouped = run_measure(measure, [Cohort.of(cohort)], [GroupBy.of(GroupDimension.PELL)])
        (pell_row,) = [r for r in grouped if r.group.label == "pell=Y"]
        (filtered,) = run_measure(measure, [Cohort.of(cohort)], filters=Group.of((GroupDimension.PELL, "Y")))
        assert (filtered.numerator, filtered.denominator, filtered.status) == (pell_row.numerator, pell_row.denominator, pell_row.status), cohort
