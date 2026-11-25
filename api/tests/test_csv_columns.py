"""Each page's CSV has the same columns, in the same order, for every cohort and filter (issue #7).

A school imports these files into Power BI or a spreadsheet, so a column that comes and goes with the filters would
break its import. route.CSV_COLUMNS is the list; these tests fail when a page returns a field that isn't in it.
"""
from __future__ import annotations

import csv
import io

import pytest
from fastapi.testclient import TestClient

from api import data, route
from api.route import CSV_COLUMNS, create_app
from measures.tests.explorer_fixture import here, make_database, student

CONTEXT = ["cohort", "filters", "retention_type"]
PAGES = {
    "student-paths": ("student-paths", {}),
    "dfw": ("dfw", {}),
    "dfw-course": ("dfw/course", {"course": "ENG 101"}),
    "gateway": ("gateway", {}),
    "credit-momentum": ("credit-momentum", {}),
}


def header(client: TestClient, path: str, **params: str) -> list[str]:
    """The first row of one CSV download."""
    response = client.get(f"/api/v1/uncf/{path}", params={**params, "format": "csv"})
    assert response.status_code == 200, response.text
    return next(csv.reader(io.StringIO(response.text)))


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Twelve 2023-24 starters, half Pell, each with a gateway English course graded in the spring."""
    students = [student(f"s{n}", retention=1, pell="Y" if n % 2 else "N") for n in range(12)]
    records = [here(f"s{n}", "2023-24", "SPRING", gateway="E", grade="2.0" if n % 3 else "F", attempted="3", earned="3" if n % 3 else "0") for n in range(12)]
    database = make_database(tmp_path / "pdp.sqlite", students, records)
    monkeypatch.setattr(data, "data_path", lambda: database)
    route.clear_cache()
    yield TestClient(create_app())
    route.clear_cache()


@pytest.mark.parametrize("name", PAGES)
def test_every_page_has_exactly_its_columns(client, name) -> None:
    """With and without filters, and with nobody matching, the header is the page's fixed list."""
    path, extra = PAGES[name]
    expected = [*CONTEXT, *CSV_COLUMNS[name]]
    assert header(client, path, cohort="2023-24", **extra) == expected
    assert header(client, path, cohort="2023-24", pell="Y", retention_type="federal", **extra) == expected
    if name == "dfw-course":
        # A course nobody in the filters took is a 404, not an empty file.
        assert client.get(f"/api/v1/uncf/{path}", params={"cohort": "2023-24", "pell": "UNKNOWN", **extra}).status_code == 404
    else:
        assert header(client, path, cohort="2023-24", pell="UNKNOWN", **extra) == expected


def test_lists_have_no_repeats() -> None:
    """Each column appears once, and none repeats the three context columns."""
    for name, columns in CSV_COLUMNS.items():
        assert len(set(columns)) == len(columns), name
        assert not set(columns) & set(CONTEXT), name


def test_hidden_values_are_blank_not_zero(client) -> None:
    """A filter nobody matches leaves the numbers blank, so an import never reads them as 0."""
    response = client.get("/api/v1/uncf/credit-momentum", params={"cohort": "2023-24", "pell": "UNKNOWN", "format": "csv"})
    rows = list(csv.DictReader(io.StringIO(response.text)))
    assert all(value in ("", None) for row in rows for key, value in row.items() if key.endswith("rate"))


@pytest.mark.slow
@pytest.mark.parametrize("name", PAGES)
def test_real_data_columns_never_change(name) -> None:
    """On the loaded data, every cohort and a spread of filters give the page's fixed header."""
    if not data.data_path().exists():
        pytest.skip("Load the data first: python -m api load")
    client = TestClient(create_app())
    path, extra = PAGES[name]
    expected = [*CONTEXT, *CSV_COLUMNS[name]]
    queries = [{"cohort": cohort} for cohort in client.get("/api/v1/uncf/options").json()["cohorts"]]
    queries += [
        {"cohort": "2023-24", "pell": "Y"},
        {"cohort": "2023-24", "race": "Asian", "gender": "F"},
        {"cohort": "2022-23", "enrollment_intensity": "Part-time", "retention_type": "federal"},
        {"cohort": "2023-24", "age_band": "Older than 24", "cohort_term": "Spring"},
    ]
    for query in queries:
        assert header(client, path, **query, **extra) == expected, query
