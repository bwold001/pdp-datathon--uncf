"""Checks the Results API (#5): the contract on a fixture database, and known answers on the real data when loaded."""
from __future__ import annotations

import os
import sqlite3
from typing import get_args

import pytest
from fastapi.testclient import TestClient

from measures.models import GroupDimension
from measures.run_measures import DEFAULT_DATABASE
from uncf import __main__ as entry
from uncf import api_results, api_route, data
from uncf.api_route import create_app
from uncf.definitions import DEFINITIONS
from uncf.schemas import Dimension
from uncf.schemas import Measure as ApiMeasure
from uncf.tests.explorer_fixture import LOADED_AT, here, make_database, student

URL = "/api/v1/uncf/results"


@pytest.fixture
def data_file(tmp_path, monkeypatch):
    """2022-23: 20 Pell students (12 retained), 10 non-Pell (5 retained), 3 unknown Pell; 15 back in Fall 2023."""
    students = (
        [student(f"y{n}", "2022-23", pell="Y", retention=int(n < 12)) for n in range(20)]
        + [student(f"n{n}", "2022-23", pell="N", retention=int(n < 5)) for n in range(10)]
        + [student(f"u{n}", "2022-23", pell="", retention=1) for n in range(3)]
    )
    back = [f"y{n}" for n in range(10)] + [f"n{n}" for n in range(5)]
    records = [here(sid, "2023-24", "FALL", cohort="2022-23", grade="3.0") for sid in back]
    path = make_database(tmp_path / "pdp.sqlite", students, records)
    monkeypatch.setattr(data, "data_path", lambda: path)
    api_route.clear_cache()
    yield path
    api_route.clear_cache()


@pytest.fixture
def client() -> TestClient:
    """A test client for the standalone app."""
    return TestClient(create_app())


def get(client: TestClient, **params):
    """GET /results with the given query parameters."""
    return client.get(URL, params=params)


def test_retention_by_pell_matches_the_explorer_contract(data_file, client) -> None:
    """#5's done criterion: rows, the definition and the load time, in the Explorer's shape."""
    response = get(client, measure="retention", cohort="2022-23", group_by="pell")
    assert response.status_code == 200
    body = response.json()
    assert body["meta"] == {
        "measure": "retention",
        "cohort": "2022-23",
        "group_by": ["pell"],
        "filters": {},
        "retention_type": "school",
        "definition": DEFINITIONS["retention"],
        "source": "PDP analysis-ready cohort and course files (synthetic sample)",
        "loaded_at": LOADED_AT,
        "provisional": False,
    }
    assert [row["group"] for row in body["rows"]] == [{}, {"pell": "N"}, {"pell": "UNKNOWN"}, {"pell": "Y"}]
    assert body["rows"][0] | {"note": None} == {
        "group": {}, "numerator": 20, "denominator": 33, "rate": 0.6061, "status": "ok",
        "n_excluded": 0, "n_out_of_scope": 0, "note": None, "split": None,
    }


def test_hidden_group_is_null_with_its_status_never_zero(data_file, client) -> None:
    """A suppressed group keeps null numbers and its status."""
    rows = get(client, measure="retention", cohort="2022-23", group_by="pell").json()["rows"]
    hidden = next(row for row in rows if row["group"] == {"pell": "UNKNOWN"})
    assert hidden["status"] == "suppressed"
    assert hidden["numerator"] is None and hidden["denominator"] is None and hidden["rate"] is None


def test_federal_retention_is_fall_to_fall(data_file, client) -> None:
    """retention_type=federal counts students back here the fall after year 1, with its own definition."""
    body = get(client, measure="retention", cohort="2022-23", group_by="pell", retention_type="federal").json()
    counts = {tuple(row["group"].values()): (row["numerator"], row["denominator"]) for row in body["rows"]}
    assert counts[()] == (15, 33)
    assert counts[("Y",)] == (10, 20)
    assert body["meta"]["retention_type"] == "federal"
    assert body["meta"]["definition"] == DEFINITIONS["federal_retention"]


def test_filters_narrow_every_row(data_file, client) -> None:
    """The cohort bar's filters pick the students before grouping, like on the Explorer pages."""
    body = get(client, measure="retention", cohort="2022-23", pell="Y").json()
    assert body["meta"]["filters"] == {"pell": "Y"}
    assert (body["rows"][0]["numerator"], body["rows"][0]["denominator"]) == (12, 20)


def test_dfw_rate_rows_split_d_f_and_w(tmp_path, monkeypatch, client) -> None:
    """dfw_rate counts final grades, with D, F and W apart."""
    students = [student(f"s{n}", "2022-23") for n in range(12)]
    grades = ["3.0"] * 6 + ["1.5", "0.5", "F", "W", "W", "I"]
    records = [here(f"s{n}", "2022-23", "FALL", cohort="2022-23", grade=grade) for n, grade in enumerate(grades)]
    path = make_database(tmp_path / "dfw.sqlite", students, records)
    monkeypatch.setattr(data, "data_path", lambda: path)
    api_route.clear_cache()
    row = get(client, measure="dfw_rate", cohort="2022-23").json()["rows"][0]
    assert row["status"] == "ok"
    assert (row["numerator"], row["denominator"], row["n_excluded"]) == (5, 11, 1)
    assert row["split"] == {"D": 1, "F": 2, "W": 2}


def test_no_group_by_returns_only_everyone(data_file, client) -> None:
    """Without group_by, the response is the everyone row alone."""
    body = get(client, measure="persistence", cohort="2022-23").json()
    assert body["meta"]["group_by"] == []
    assert [row["group"] for row in body["rows"]] == [{}]


def test_pair_order_does_not_matter_and_is_cached(data_file, client) -> None:
    """pell,race and race,pell return the same rows from one calculation."""
    first = client.get(URL, params={"measure": "retention", "cohort": "2022-23", "group_by": ["pell", "race"]})
    second = client.get(URL, params={"measure": "retention", "cohort": "2022-23", "group_by": ["race", "pell"]})
    assert first.json()["rows"] == second.json()["rows"]
    assert first.json()["rows"][1]["group"] == {"pell": "N", "race": "American Indian or Alaska Native"}
    assert api_results._calculate.cache_info().misses == 1


def test_new_data_clears_the_cache(data_file, client) -> None:
    """A reloaded data file is recalculated on the next request, without a restart."""
    get(client, measure="retention", cohort="2022-23", group_by="pell")
    stamp = data_file.stat().st_mtime + 10
    os.utime(data_file, (stamp, stamp))
    get(client, measure="retention", cohort="2022-23", group_by="pell")
    assert api_results._calculate.cache_info().misses == 2


def test_gateway_with_no_answers_is_not_reported(data_file, client) -> None:
    """A gateway class with no answers means the requirement isn't reported; retention for a later class is too new."""
    gateway = get(client, measure="gateway_math", cohort="2022-23").json()["rows"][0]
    assert gateway["status"] == "not_reported" and gateway["rate"] is None
    retention = get(client, measure="retention", cohort="2023-24", retention_type="federal").json()["rows"][0]
    assert retention["status"] == "not_yet_observable"


@pytest.mark.parametrize(
    ("measure", "cohort", "expected"),
    [("retention", "2024-25", True), ("persistence", "2024-25", True), ("gateway_math", "2024-25", False), ("retention", "2023-24", False)],
)
def test_provisional_for_year_two_measures_of_the_newest_class(data_file, client, measure, cohort, expected) -> None:
    """Only year 2 measures for a class missing part of its second year are provisional."""
    assert get(client, measure=measure, cohort=cohort).json()["meta"]["provisional"] is expected


@pytest.mark.parametrize(
    "params",
    [
        {"measure": "graduation", "cohort": "2022-23"},
        {"measure": "retention", "cohort": "2019-20"},
        {"measure": "retention", "cohort": "2022-23", "group_by": "first_gen"},
        {"measure": "retention", "cohort": "2022-23", "retention_type": "ipeds"},
        {"measure": "retention", "cohort": "2022-23", "pell": "Maybe"},
        {"cohort": "2022-23"},
    ],
)
def test_values_outside_the_lists_are_422(data_file, client, params) -> None:
    """Values the API doesn't offer are refused before anything is calculated."""
    assert client.get(URL, params=params).status_code == 422
    assert api_results._calculate.cache_info().misses == 0


@pytest.mark.parametrize("group_by", [["pell", "race", "gender"], ["pell", "pell"]])
def test_bad_group_by_is_422_with_our_error_body(data_file, client, group_by) -> None:
    """More than two dimensions, or the same one twice, gets a clear error."""
    response = client.get(URL, params={"measure": "retention", "cohort": "2022-23", "group_by": group_by})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_group_by"


def test_csv_export(data_file, client) -> None:
    """format=csv returns the same rows as a download, labelled with the cohort, filters and retention type."""
    response = get(client, measure="retention", cohort="2022-23", group_by="pell", format="csv")
    assert response.headers["content-type"].startswith("text/csv")
    lines = response.text.splitlines()
    assert lines[0].startswith("cohort,filters,retention_type,pell,numerator,denominator")
    assert lines[1].startswith("2022-23,all students,school,All,20,33")


def test_missing_data_is_503(tmp_path, monkeypatch, client) -> None:
    """Without the normalized data, the API says how to load it."""
    monkeypatch.setattr(data, "data_path", lambda: tmp_path / "missing.sqlite")
    api_route.clear_cache()
    response = get(client, measure="retention", cohort="2022-23", group_by="pell")
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "data_missing"
    assert client.get("/api/v1/uncf/health").json() == {"status": "ok", "data_available": False, "loaded_at": None}


def test_health_reports_the_load_time(data_file, client) -> None:
    """Health says the data is loaded, and when."""
    assert client.get("/api/v1/uncf/health").json() == {"status": "ok", "data_available": True, "loaded_at": LOADED_AT}


def test_options_offer_only_defined_measures(client) -> None:
    """Every measure offered has a definition, labelled with its on-screen name."""
    body = client.get("/api/v1/uncf/options").json()
    assert [m["value"] for m in body["measures"]] == list(get_args(ApiMeasure))
    assert all(m["label"] == DEFINITIONS[m["value"]]["name"] for m in body["measures"])
    assert [d["value"] for d in body["dimensions"]] == list(get_args(Dimension))
    assert body["max_group_by"] == 2


def test_cors_allows_the_playground_client(data_file, client) -> None:
    """The Explorer on localhost:3000 can call the API from the browser."""
    response = client.get(URL, params={"measure": "retention", "cohort": "2022-23"}, headers={"Origin": "http://localhost:3000"})
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_entry_point_commands(monkeypatch) -> None:
    """No argument loads then serves; each subcommand runs only itself."""
    calls: list[str] = []
    monkeypatch.setattr(entry.precompute, "ensure_data_loaded", lambda: calls.append("load"))
    monkeypatch.setattr(entry.precompute, "main", lambda: calls.append("precompute"))
    monkeypatch.setattr(entry, "serve", lambda host, port: calls.append(f"serve {port}"))
    entry.main([])
    entry.main(["load"])
    entry.main(["serve", "--port", "9000"])
    entry.main(["precompute"])
    assert calls == ["load", "serve 8001", "load", "serve 9000", "precompute"]


needs_data = pytest.mark.skipif(not DEFAULT_DATABASE.exists(), reason="run `python -m uncf load` first")


@pytest.mark.slow
@needs_data
def test_known_answer_on_the_real_data(client) -> None:
    """Retention for 2022-23 by Pell matches the measures package on the synthetic data."""
    api_route.clear_cache()
    rows = get(client, measure="retention", cohort="2022-23", group_by="pell").json()["rows"]
    counts = {tuple(row["group"].values()): (row["numerator"], row["denominator"], row["rate"]) for row in rows}
    assert counts[()] == (1414, 2617, 0.5403)
    assert counts[("N",)] == (848, 1578, 0.5374)
    assert counts[("Y",)] == (514, 873, 0.5888)
    assert counts[("UNKNOWN",)] == (52, 166, 0.3133)


# An independent recount: plain SQL on pdp.sqlite, without the measures package. Each measure is
# (who has an answer, who achieved it), from the measure definitions in measures/README.md.
RECOUNT_RULES = {
    "retention": ("cm.retention IS NOT NULL", "cm.retention = 1"),
    "persistence": ("cm.persistence IS NOT NULL", "cm.persistence = 1"),
    "gateway_math": (
        "cm.gateway_math_status = 'R' AND cm.completed_gateway_math_year1 IN ('C', 'D')",
        "cm.completed_gateway_math_year1 = 'C'",
    ),
    "gateway_english": (
        "cm.gateway_english_status = 'R' AND cm.completed_gateway_english_year1 IN ('C', 'D')",
        "cm.completed_gateway_english_year1 = 'C'",
    ),
}
RECOUNT_COLUMNS = {
    "race": "s.race",
    "ethnicity": "s.ethnicity",
    "gender": "s.gender",
    "age_band": "s.student_age",
    "pell": "cm.pell_status_first_year",
    "enrollment_type": "cm.enrollment_type",
    "enrollment_intensity": "cm.enrollment_intensity_first_term",
    "cohort_term": "cm.cohort_term",
}


def recount(connection, measure: str, cohort: str, dimensions: list[str]) -> dict[tuple, tuple[int, int]]:
    """(achieved, answered) per group, counted straight from pdp.sqlite. Keys are values in dimension order."""
    from measures.models import ALLOWED_VALUES

    answered, achieved = RECOUNT_RULES[measure]
    columns = ", ".join(RECOUNT_COLUMNS[d] for d in dimensions) or "NULL"
    rows = connection.execute(
        f"SELECT {columns}, {answered}, {achieved} FROM cohort_membership cm "
        "JOIN student s ON s.student_id = cm.student_id WHERE cm.cohort = ?",
        (cohort,),
    ).fetchall()

    def canonical(dimension: str, raw) -> str:
        """The official value, matching case and spaces loosely; anything else is UNKNOWN."""
        key = (raw or "").replace(" ", "").upper()
        for value in ALLOWED_VALUES[GroupDimension(dimension)]:
            if value.replace(" ", "").upper() == key:
                return value
        return "UNKNOWN"

    counts: dict[tuple, list[int]] = {}
    for row in rows:
        values = tuple(canonical(d, raw) for d, raw in zip(dimensions, row)) if dimensions else ()
        has_answer, did_achieve = row[-2], row[-1]
        for key in {(), values}:
            tally = counts.setdefault(key, [0, 0])
            tally[0] += int(bool(has_answer and did_achieve))
            tally[1] += int(bool(has_answer))
    return {key: (a, b) for key, (a, b) in counts.items()}


@pytest.mark.slow
@needs_data
def test_api_matches_an_independent_recount_of_the_normalized_data(client) -> None:
    """Every measure, class, single grouping and pair: the API's numbers equal plain SQL on pdp.sqlite."""
    from itertools import combinations

    api_route.clear_cache()
    connection = sqlite3.connect(f"file:{DEFAULT_DATABASE}?mode=ro", uri=True)
    groupings = [[]] + [[d] for d in get_args(Dimension)] + [sorted(p) for p in combinations(get_args(Dimension), 2)]
    checked = 0
    try:
        for measure in RECOUNT_RULES:
            for cohort in ["2021-22", "2022-23", "2023-24", "2024-25"]:
                for dimensions in groupings:
                    expected = recount(connection, measure, cohort, dimensions)
                    response = client.get(URL, params={"measure": measure, "cohort": cohort, "group_by": dimensions})
                    assert response.status_code == 200
                    for row in response.json()["rows"]:
                        key = tuple(row["group"][d] for d in dimensions) if row["group"] else ()
                        achieved, answered = expected.get(key, (0, 0))
                        where = (measure, cohort, dimensions, key)
                        if answered >= 10:
                            assert row["status"] == "ok", where
                            assert (row["numerator"], row["denominator"]) == (achieved, answered), where
                            assert row["rate"] == round(achieved / answered, 4), where
                        else:
                            assert row["status"] == "suppressed", where
                            assert row["numerator"] is None and row["rate"] is None, where
                        checked += 1
    finally:
        connection.close()
    assert checked > 5000


@pytest.mark.slow
@needs_data
def test_every_class_measure_and_grouping_answers_on_the_real_data(client) -> None:
    """Every offered measure, class and single grouping returns 200, and hidden rows have no numbers."""
    api_route.clear_cache()
    for measure in get_args(ApiMeasure):
        for cohort in ["2021-22", "2022-23", "2023-24", "2024-25"]:
            for dimension in get_args(Dimension):
                response = get(client, measure=measure, cohort=cohort, group_by=dimension)
                assert response.status_code == 200, (measure, cohort, dimension)
                for row in response.json()["rows"]:
                    if row["status"] != "ok":
                        assert row["rate"] is None and row["numerator"] is None
