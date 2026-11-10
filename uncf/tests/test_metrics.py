"""Checks the shared metrics: the grade and counting rules, and that every metric equals the measures package."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from measures.models import Cohort, GroupBy, GroupDimension, Measure
from measures.run_measures import DEFAULT_DATABASE, run_measure
from uncf import api_route, data, metrics
from uncf.cohort import CohortQuery, select_students

COHORTS = ["2021-22", "2022-23", "2023-24", "2024-25"]
needs_data = pytest.mark.skipif(not DEFAULT_DATABASE.exists(), reason="the normalized data isn't loaded")


@pytest.mark.parametrize(
    ("grade", "result"),
    [("F", "F"), ("0", "F"), ("0.69", "F"), ("0.7", "D"), ("1.99", "D"), ("2.0", "pass"), ("4", "pass"), ("P", "pass"),
     ("W", "W"), (" w ", "W"), ("I", None), ("A", None), ("UNKNOWN", None), (None, None), ("UW", None)],
)
def test_grade_result_splits_d_f_and_w(grade, result):
    """F is an F or under 0.7, D is 0.7 to under 2.0, W is a W; grades that aren't final are None."""
    assert metrics.grade_result(grade) == result


def test_rate_counts_the_measures_way():
    """Unknown answers are excluded, out of scope members counted apart, under 10 hidden, no answers not observable."""
    answers = {f"s{n}": int(n < 6) for n in range(12)} | {"unknown": None}
    counted = metrics.rate(answers, [*answers, "outside"])
    assert (counted["numerator"], counted["denominator"], counted["rate"]) == (6, 12, 0.5)
    assert (counted["n_excluded"], counted["n_out_of_scope"]) == (1, 1)
    assert metrics.rate(answers, ["s1", "s2"])["status"] == "suppressed"
    assert metrics.rate(answers, answers, observable=False)["status"] == "not_yet_observable"


@pytest.mark.slow
@needs_data
@pytest.mark.parametrize("measure", ["retention", "persistence", "gateway_math", "gateway_english", "credit_completion"])
def test_student_metrics_equal_run_measure(measure):
    """Every class, single grouping and a pair: the shared metric equals run_measure's numbers."""
    connection = data.open_database()
    try:
        for cohort in COHORTS:
            answers, observable, _ = metrics.measure_answers(connection, measure, cohort)
            group_bys = [[]] + [[GroupDimension.PELL], [GroupDimension.RACE], [GroupDimension.ENROLLMENT_TYPE, GroupDimension.COHORT_TERM]]
            for dimensions in group_bys:
                rows = run_measure(Measure(measure), [Cohort.of(cohort)], [GroupBy.of(*dimensions)] if dimensions else None)
                for row in rows:
                    query = CohortQuery.of(cohort, **{part.dimension.value: part.value for part in row.group.parts})
                    counted = metrics.rate(answers, select_students(connection, query), observable)
                    where = (measure, cohort, row.group.label)
                    assert counted["status"] == row.status.value, where
                    assert (counted["numerator"], counted["denominator"], counted["rate"]) == (row.numerator, row.denominator, row.metric_rate), where
    finally:
        connection.close()


@pytest.mark.slow
@needs_data
def test_dfw_equals_the_measure_and_d_f_w_add_up():
    """D + F + W is the dfw_rate measure's numerator and every final grade its denominator, for every class."""
    connection = data.open_database()
    try:
        for cohort in COHORTS:
            (row,) = run_measure(Measure.DFW_RATE, [Cohort.of(cohort)])
            tally = metrics.dfw(metrics.course_rows(connection, cohort, select_students(connection, CohortQuery(cohort))))
            split = tally["split"]
            assert split["D"] + split["F"] + split["W"] == tally["num"] == row.numerator, cohort
            assert tally["den"] == row.denominator, cohort
    finally:
        connection.close()


@pytest.mark.slow
@needs_data
def test_known_retention_by_type():
    """2022-23 (synthetic data): school 1,414 of 2,617 (the PDP flag), federal 926 of 2,617 (fall to fall)."""
    connection = data.open_database()
    try:
        students = select_students(connection, CohortQuery("2022-23"))
        for retention_type, expected in [("school", (1414, 2617)), ("federal", (926, 2617))]:
            answers, observable = metrics.retention_answers(connection, "2022-23", retention_type)
            counted = metrics.retention(answers, observable, students, retention_type)
            assert (counted["retained"], counted["students"]) == expected
    finally:
        connection.close()


@pytest.mark.slow
@needs_data
@pytest.mark.parametrize("retention_type", ["school", "federal"])
@pytest.mark.parametrize("filters", [{}, {"pell": "Y"}, {"cohort_term": "Fall", "race": "Black or African American"}, {"enrollment_type": "First-time"}])
def test_every_page_and_the_results_api_agree_on_retention(retention_type, filters):
    """The issue's done criterion: the same cohort, filters and type give the same retention everywhere."""
    api_route.clear_cache()
    client = TestClient(api_route.create_app())
    params = {"cohort": "2022-23", "retention_type": retention_type, **filters}
    results = client.get("/api/v1/uncf/results", params={"measure": "retention", **params}).json()["rows"][0]
    expected = (results["numerator"], results["denominator"])
    paths = client.get("/api/v1/uncf/student-paths", params=params).json()["retention"]
    gateway = client.get("/api/v1/uncf/gateway", params=params).json()["cohort_retention"]
    credits = client.get("/api/v1/uncf/credit-momentum", params=params).json()["retention"]
    for page in (paths, gateway, credits):
        assert (page["retained"], page["students"]) == expected
        assert page["type"] == retention_type


@pytest.mark.slow
@needs_data
def test_dfw_page_and_results_api_agree():
    """The DFW page's everyone tile and the Results API's dfw_rate row are the same numbers, filters included."""
    api_route.clear_cache()
    client = TestClient(api_route.create_app())
    for filters in [{}, {"pell": "Y"}, {"gender": "F", "age_band": "20 and younger"}]:
        params = {"cohort": "2023-24", **filters}
        page = client.get("/api/v1/uncf/dfw", params=params).json()["everyone"]
        row = client.get("/api/v1/uncf/results", params={"measure": "dfw_rate", **params}).json()["rows"][0]
        assert (page["num"], page["den"]) == (row["numerator"], row["denominator"])
        assert {key: page["split"][key] for key in ("D", "F", "W")} == row["split"]

