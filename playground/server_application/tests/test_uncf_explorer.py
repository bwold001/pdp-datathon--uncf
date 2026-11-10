"""The UNCF Explorer API is mounted under /api/v1 and answers from the normalized data."""

import pytest

# app.uncf put the repository root on the import path when the app was built (see conftest.py).
from api import data, route
from measures.tests.explorer_fixture import here, make_database, student


@pytest.fixture
def explorer_data(tmp_path, monkeypatch):
    """A fixture database of 12 first-time Fall 2023 starters, in place of pdp.sqlite."""
    students = [student(f"s{n}") for n in range(12)]
    records = [here(f"s{n}", "2023-24", "SPRING") for n in range(12)]
    database = make_database(tmp_path / "pdp.sqlite", students, records)
    monkeypatch.setattr(data, "data_path", lambda: database)
    route.clear_cache()
    return database


def test_student_paths_is_mounted(client, explorer_data):
    response = client.get("/api/v1/uncf/student-paths", params={"cohort": "2023-24"})
    assert response.status_code == 200
    assert response.json()["students"] == 12


def test_cohort_options_is_mounted(client, explorer_data):
    response = client.get("/api/v1/uncf/cohort-options")
    assert response.status_code == 200
    assert response.json()["cohorts"]["2023-24"] == 12


def test_unknown_filter_value_is_a_422(client, explorer_data):
    response = client.get("/api/v1/uncf/student-paths", params={"pell": "Maybe"})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_filter"
