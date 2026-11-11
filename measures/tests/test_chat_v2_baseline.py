"""Hand-counted synthetic cases that a v2 adapter must preserve."""

import sqlite3

import pytest

from measures.breakdowns.credit_momentum import credit_momentum
from measures.breakdowns.gateway_courses import gateway_courses
from measures.models import Cohort, Measure, Status
from measures.run_measures import run_measure
from measures.tests.explorer_fixture import here, make_database, student


def test_gateway_cohort_completion_and_course_outcomes_have_different_populations(tmp_path):
    """Ten gateway passes at 1.5 and ten non-attempters have different denominators."""
    students = [student(f"s{i}", retention=1) for i in range(20)]
    records = [
        here(f"s{i}", "2023-24", "FALL", prefix="MATH", number="101", grade="1.5", gateway="M")
        for i in range(10)
    ]
    path = make_database(tmp_path / "gateway.sqlite", students, records)
    with sqlite3.connect(path) as connection:
        connection.execute("UPDATE cohort_membership SET gateway_math_status = 'R', completed_gateway_math_year1 = 'D'")
        connection.executemany(
            "UPDATE cohort_membership SET completed_gateway_math_year1 = 'C' WHERE student_id = ?",
            [(f"s{i}",) for i in range(10)],
        )

    (completion,) = run_measure(Measure.GATEWAY_MATH, [Cohort.of("2023-24")], database=path)
    (course,) = gateway_courses("2023-24", database=path)["courses"]

    assert (completion.numerator, completion.denominator, completion.metric_rate) == (10, 20, 0.5)
    assert (course["students"], course["first_pass"], course["passed"]) == (10, 10, 10)
    assert course["path"] == {"first": 10, "retook_passed": 0, "retook_not": 0, "no_retake": 0}


def test_credit_completion_preserves_a_fractional_numerator(tmp_path):
    """Nine half-completions plus one full completion produce 5.5 over ten students."""
    students = [student(f"s{i}", attempted=2, earned=1) for i in range(9)]
    students.append(student("full", attempted=10, earned=10))
    path = make_database(tmp_path / "credits.sqlite", students)

    (result,) = run_measure(Measure.CREDIT_COMPLETION, [Cohort.of("2023-24")], database=path)

    assert (result.numerator, result.denominator, result.metric_rate) == (5.5, 10, 0.55)
    assert result.metric_rate != round(19 / 28, 4)


def test_tier_size_is_not_the_known_retention_denominator(tmp_path):
    """Twelve tier members include only ten retention answers, six of them retained."""
    students = [
        student(f"s{i}", attempted=12, earned=6, retention=1 if i < 6 else 0 if i < 10 else None)
        for i in range(12)
    ]
    path = make_database(tmp_path / "tiers.sqlite", students)

    tier = credit_momentum("2023-24", database=path)["tiers"][0]

    assert (tier["students"], tier["share"], tier["retained"], tier["rate"]) == (12, 1.0, 6, 0.6)


@pytest.mark.parametrize("size,status", [(9, Status.SUPPRESSED), (10, Status.OK)])
def test_dfw_threshold_counts_students_instead_of_enrollments(tmp_path, size, status):
    """Two grades per student do not let nine students clear the threshold of ten."""
    students = [student(f"s{i}") for i in range(size)]
    records = [
        here(f"s{i}", "2023-24", "FALL", grade=grade)
        for i in range(size)
        for grade in ("F", "P")
    ]
    path = make_database(tmp_path / "dfw.sqlite", students, records)

    (result,) = run_measure(Measure.DFW_RATE, [Cohort.of("2023-24")], database=path)

    assert result.status == status
    if size == 9:
        assert (result.numerator, result.denominator, result.n_students, result.metric_rate) == (None,) * 4
        assert result.exclusions == {} and result.split is None
    else:
        assert (result.numerator, result.denominator, result.n_students, result.metric_rate) == (10, 20, 10, 0.5)
