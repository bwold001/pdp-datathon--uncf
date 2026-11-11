"""Checks the Explorer API's answers, errors and caching against the tiny fixture database."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api import data, route
from measures.definitions import DEFINITIONS
from api.route import create_app
from measures.tests.explorer_fixture import here, make_database, student


@pytest.fixture
def client(tmp_path, monkeypatch):
    """The standalone app reading a fixture database of 12 first-time Fall 2023 starters."""
    students = [student(f"s{n}", retention=1) for n in range(12)]
    records = [here(f"s{n}", "2023-24", "SPRING") for n in range(12)]
    database = make_database(tmp_path / "pdp.sqlite", students, records)
    monkeypatch.setattr(data, "data_path", lambda: database)
    route.clear_cache()
    return TestClient(create_app())


def test_student_paths_answer(client):
    """A plain request gets the page's numbers for the default cohort."""
    response = client.get("/api/v1/uncf/student-paths", params={"cohort": "2023-24", "pell": "Y"})
    assert response.status_code == 200
    body = response.json()
    assert body["students"] == 12
    assert body["meta"]["filters"] == {"pell": "Y"}
    assert body["columns"]["next"]["here"] == 12


def test_unknown_value_is_a_422(client):
    """A value the cohort bar doesn't offer names the problem."""
    response = client.get("/api/v1/uncf/student-paths", params={"race": "Martian"})
    assert response.status_code == 422
    assert response.json() == {"error": {"code": "invalid_filter", "message": "race has no value 'Martian'."}}


def test_cohort_options(client):
    """The bar's counts for the chosen cohort."""
    body = client.get("/api/v1/uncf/cohort-options", params={"cohort": "2023-24"}).json()
    assert body["cohorts"]["2023-24"] == 12
    assert body["filters"]["pell"] == {"Y": 12, "N": 0, "UNKNOWN": 0}


def test_missing_data_is_a_503(tmp_path, monkeypatch):
    """Before the data is loaded, every page says how to load it."""
    monkeypatch.setattr(data, "data_path", lambda: tmp_path / "missing.sqlite")
    route.clear_cache()
    response = TestClient(create_app()).get("/api/v1/uncf/student-paths")
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "data_missing"


def test_dfw_list_and_course(client):
    """The DFW list answers (the fixture has no final grades, so nothing to show); an unlisted course is a 404."""
    body = client.get("/api/v1/uncf/dfw", params={"cohort": "2023-24"}).json()
    assert body["status"] == "suppressed"
    assert body["courses"] == []
    response = client.get("/api/v1/uncf/dfw/course", params={"course": "ENG 101"})
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "unknown_course"


def test_gateway(client):
    """The Gateway page answers for the fixture: no gateway courses there, so no rows."""
    body = client.get("/api/v1/uncf/gateway", params={"cohort": "2023-24"}).json()
    assert body["status"] == "ok"
    assert body["courses"] == []
    assert body["cohort_retention"]["students"] == 12


def test_dfw_and_gateway_carry_each_grade_and_the_scale(tmp_path, monkeypatch):
    """The DFW split has each DFW grade, gateway courses have every grade, and both answers carry the grade scale."""
    students = [student(f"s{n}") for n in range(12)]
    grades = ["1.5", "1.0", "0.7", "0.3", "W", "1.7"] * 2
    records = [here(f"s{n}", "2023-24", "FALL", prefix="ENG", number="101", grade=grade, gateway="E") for n, grade in enumerate(grades)]
    database = make_database(tmp_path / "pdp.sqlite", students, records)
    monkeypatch.setattr(data, "data_path", lambda: database)
    route.clear_cache()
    client = TestClient(create_app())

    dfw = client.get("/api/v1/uncf/dfw", params={"cohort": "2023-24"}).json()
    assert dfw["everyone"]["split"]["grades"] == {"D+": 2, "D": 2, "D-": 2, "F": 2, "W": 2}  # the two C- pass
    assert (dfw["everyone"]["split"]["DF"], dfw["everyone"]["split"]["W"], dfw["everyone"]["num"]) == (8, 2, 10)
    scale = dfw["meta"]["grade_scale"]
    assert {row["grade"]: row["dfw"] for row in scale["grades"]}["C-"] is False

    gateway = client.get("/api/v1/uncf/gateway", params={"cohort": "2023-24"}).json()
    (course,) = gateway["courses"]
    assert {grade: count for grade, count in course["grades"].items() if count} == {"C-": 2, "D+": 2, "D": 2, "D-": 2, "F": 2, "W": 2}
    assert gateway["meta"]["grade_scale"] == scale

    # The CSV has one column per DFW grade.
    header = client.get("/api/v1/uncf/dfw", params={"cohort": "2023-24", "format": "csv"}).text.splitlines()[0]
    assert all(f"split.grades.{grade}" in header for grade in ("D+", "D", "D-", "F", "W"))


def test_credit_momentum(client):
    """The Credit momentum page answers; the fixture has no year-1 credits, so its numbers are hidden."""
    body = client.get("/api/v1/uncf/credit-momentum", params={"cohort": "2023-24"}).json()
    assert body["status"] == "suppressed"
    assert body["progress"] is None


def test_credit_momentum_progress(tmp_path, monkeypatch):
    """progress, the design's meaningful-progress page, comes through the API with its settings and groups."""
    students = [student(f"s{n}", attempted=30, earned=30) for n in range(12)]
    records = [here(f"s{n}", "2023-24", "FALL", attempted=30, earned=30, grade="4", course_type="CU") for n in range(12)]
    database = make_database(tmp_path / "pdp.sqlite", students, records)
    monkeypatch.setattr(data, "data_path", lambda: database)
    route.clear_cache()
    body = TestClient(create_app()).get("/api/v1/uncf/credit-momentum", params={"cohort": "2023-24"}).json()
    progress = body["progress"]
    assert progress["settings"] == {
        "minimum": 24, "degree_credits": 120, "years": 4, "pace": 30.0,
        "higher_degree_credits": 125, "higher_pace": 31.25, "counting_course_types": ["CU", "CC"],
    }
    assert progress["pace"] == {"students": 12, "share": 1.0}
    assert [band["key"] for band in progress["bands"]] == ["pace", "minimum", "below", "stopped"]
    assert progress["year_two_follow_up"]["status"] == "not_yet_observable"


def test_definitions_come_from_the_shared_dictionary(client):
    """The Explorer's key terms are api/definitions.py, word for word."""
    body = client.get("/api/v1/uncf/definitions").json()
    assert body["definitions"] == DEFINITIONS
    assert body["definitions"]["persistence"]["name"] == "At another college"


def test_every_page_takes_retention_type_and_the_new_filters(client):
    """retention_type and the two new filters (enrollment_type, ethnicity) work on every page route."""
    for page in ["student-paths", "dfw", "gateway", "credit-momentum"]:
        params = {"cohort": "2023-24", "retention_type": "federal", "enrollment_type": "First-time", "ethnicity": "UNKNOWN"}
        response = client.get(f"/api/v1/uncf/{page}", params=params)
        assert response.status_code == 200, page
        assert response.json()["meta"]["retention_type"] == "federal", page
        assert response.json()["meta"]["filters"] == {"enrollment_type": "First-time", "ethnicity": "UNKNOWN"}, page
    bad = client.get("/api/v1/uncf/gateway", params={"retention_type": "ipeds"})
    assert bad.status_code == 422
    assert bad.json()["error"]["code"] == "invalid_filter"


def test_page_csv_export(client):
    """format=csv gives the page's lists as a download, each row labelled with its section and the query."""
    response = client.get("/api/v1/uncf/student-paths", params={"cohort": "2023-24", "format": "csv"})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert 'filename="uncf-student-paths-2023-24.csv"' in response.headers["content-disposition"]
    header, first = response.text.splitlines()[:2]
    assert header.startswith("cohort,filters,retention_type,section,position")
    assert first.startswith("2023-24,all students,school,path,1")
    assert client.get("/api/v1/uncf/dfw", params={"format": "xml"}).status_code == 422


def test_student_paths_options_are_checked(client):
    """terms and group_by are checked like the filters."""
    assert client.get("/api/v1/uncf/student-paths", params={"terms": 9}).status_code == 422
    assert client.get("/api/v1/uncf/student-paths", params={"group_by": "housing"}).status_code == 422
    body = client.get("/api/v1/uncf/student-paths", params={"group_by": "pell", "terms": 4}).json()
    assert [group["value"] for group in body["groups"]] == ["Y"]
    assert len(body["path"]) == 3
