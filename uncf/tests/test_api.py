"""Checks the Results API (#5) with a fake measures call, plus known answers on the real data when it's loaded."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import get_args

import pytest
from fastapi.testclient import TestClient

from measures.models import Cohort, Group, GroupDimension, Measure, MeasureResult, Status
from measures.run_measures import DEFAULT_DATABASE
from uncf import __main__ as entry
from uncf import results
from uncf.api import create_app
from uncf.definitions import DEFINITIONS
from uncf.schemas import Dimension
from uncf.schemas import Measure as ApiMeasure

URL = "/api/v1/uncf/results"
LOADED = "2026-11-06T18:40:02"
VALUES = {GroupDimension.PELL: ["N", "Y", "UNKNOWN"], GroupDimension.RACE: ["Asian"]}


def result(measure: Measure, cohort: str, group: Group, counts: tuple | None, status: Status = Status.OK) -> MeasureResult:
    """A measures-package row: counts (numerator, denominator) when shown, None when hidden."""
    shown = counts is not None
    return MeasureResult(
        measure=measure,
        cohort=Cohort.of(cohort),
        group=group,
        numerator=counts[0] if shown else None,
        denominator=counts[1] if shown else None,
        metric_rate=round(counts[0] / counts[1], 4) if shown else None,
        status=status if not shown else Status.OK,
        n_excluded=0 if shown else None,
        n_out_of_scope=0 if shown else None,
        exclusion_reason=None,
        note="A note.",
    )


class FakeMeasures:
    """Stands in for run_measure: everyone shown, Pell UNKNOWN hidden, and records each call."""

    def __init__(self, everyone_status: Status = Status.OK) -> None:
        self.calls: list[tuple] = []
        self.everyone_status = everyone_status

    def __call__(self, measure, cohorts, group_by=None, database=None):
        """Return the everyone row, then a row for each combination of the asked dimensions."""
        cohort = next(iter(cohorts[0].years))
        dimensions = sorted(next(iter(group_by)).dimensions, key=lambda d: d.value) if group_by else []
        self.calls.append((measure.value, cohort, tuple(d.value for d in dimensions)))
        if self.everyone_status != Status.OK:
            return [result(measure, cohort, Group(), None, self.everyone_status)]
        rows = [result(measure, cohort, Group(), (100, 200))]
        if not dimensions:
            return rows
        combos = [[]]
        for dimension in dimensions:
            combos = [c + [(dimension, v)] for c in combos for v in VALUES[dimension]]
        for combo in combos:
            hidden = any(value == "UNKNOWN" for _, value in combo)
            rows.append(result(measure, cohort, Group.of(*combo), None if hidden else (40, 80), Status.SUPPRESSED))
        return rows


@pytest.fixture
def data_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A tiny stand-in for pdp.sqlite: only the data_provider table the load time comes from."""
    path = tmp_path / "pdp.sqlite"
    connection = sqlite3.connect(path)
    connection.execute("CREATE TABLE data_provider (provider_id INTEGER, loaded_at TEXT)")
    connection.executemany("INSERT INTO data_provider VALUES (?, ?)", [(1, "2026-11-01T10:00:00"), (2, LOADED)])
    connection.commit()
    connection.close()
    monkeypatch.setattr(results, "data_path", lambda: path)
    results.clear_cache()
    yield path
    results.clear_cache()


@pytest.fixture
def fake(data_file, monkeypatch: pytest.MonkeyPatch) -> FakeMeasures:
    """Replace the measures call with FakeMeasures."""
    fake = FakeMeasures()
    monkeypatch.setattr(results, "run_measure", fake)
    return fake


@pytest.fixture
def client() -> TestClient:
    """A test client for the standalone app."""
    return TestClient(create_app())


def get(client: TestClient, **params):
    """GET /results with the given query parameters."""
    return client.get(URL, params=params)


def test_retention_by_pell_matches_the_explorer_contract(fake, client) -> None:
    """#5's done criterion: rows, the definition and the load time, in the Explorer's shape."""
    response = get(client, measure="retention", cohort="2022-23", group_by="pell")
    assert response.status_code == 200
    body = response.json()
    assert body["meta"] == {
        "measure": "retention",
        "cohort": "2022-23",
        "group_by": ["pell"],
        "definition": DEFINITIONS["retention"],
        "source": "PDP analysis-ready cohort and course files (synthetic sample)",
        "loaded_at": LOADED,
        "provisional": False,
    }
    assert [row["group"] for row in body["rows"]] == [{}, {"pell": "N"}, {"pell": "Y"}, {"pell": "UNKNOWN"}]
    assert body["rows"][0] | {"note": None} == {
        "group": {}, "numerator": 100, "denominator": 200, "rate": 0.5, "status": "ok",
        "n_excluded": 0, "n_out_of_scope": 0, "note": None,
    }
    assert fake.calls == [("retention", "2022-23", ("pell",))]


def test_hidden_group_is_null_with_its_status_never_zero(fake, client) -> None:
    """A suppressed group keeps null numbers and its status."""
    rows = get(client, measure="retention", cohort="2022-23", group_by="pell").json()["rows"]
    hidden = next(row for row in rows if row["group"] == {"pell": "UNKNOWN"})
    assert hidden["status"] == "suppressed"
    assert hidden["numerator"] is None and hidden["denominator"] is None and hidden["rate"] is None


def test_no_group_by_returns_only_everyone(fake, client) -> None:
    """Without group_by, the response is the everyone row alone."""
    body = get(client, measure="persistence", cohort="2022-23").json()
    assert body["meta"]["group_by"] == []
    assert [row["group"] for row in body["rows"]] == [{}]


def test_pair_order_does_not_matter_and_is_cached(fake, client) -> None:
    """pell,race and race,pell return the same rows from one calculation."""
    first = client.get(URL, params={"measure": "retention", "cohort": "2022-23", "group_by": ["pell", "race"]})
    second = client.get(URL, params={"measure": "retention", "cohort": "2022-23", "group_by": ["race", "pell"]})
    assert first.json()["rows"] == second.json()["rows"]
    assert first.json()["rows"][1]["group"] == {"pell": "N", "race": "Asian"}
    assert len(fake.calls) == 1


def test_new_data_clears_the_cache(fake, client, data_file) -> None:
    """A reloaded data file is recalculated on the next request, without a restart."""
    get(client, measure="retention", cohort="2022-23", group_by="pell")
    stamp = data_file.stat().st_mtime + 10
    import os

    os.utime(data_file, (stamp, stamp))
    get(client, measure="retention", cohort="2022-23", group_by="pell")
    assert len(fake.calls) == 2


def test_gateway_with_no_answers_is_not_reported(data_file, monkeypatch, client) -> None:
    """A gateway class with no answers means the requirement isn't reported; retention stays too new."""
    monkeypatch.setattr(results, "run_measure", FakeMeasures(everyone_status=Status.NOT_YET_OBSERVABLE))
    gateway = get(client, measure="gateway_math", cohort="2022-23").json()["rows"][0]
    retention = get(client, measure="retention", cohort="2022-23").json()["rows"][0]
    assert gateway["status"] == "not_reported" and gateway["rate"] is None
    assert retention["status"] == "not_yet_observable"


@pytest.mark.parametrize(
    ("measure", "cohort", "expected"),
    [("retention", "2024-25", True), ("persistence", "2024-25", True), ("gateway_math", "2024-25", False), ("retention", "2023-24", False)],
)
def test_provisional_for_year_two_measures_of_the_newest_class(fake, client, measure, cohort, expected) -> None:
    """Only year-2 measures for a class missing part of its second year are provisional."""
    assert get(client, measure=measure, cohort=cohort).json()["meta"]["provisional"] is expected


@pytest.mark.parametrize(
    "params",
    [
        {"measure": "dfw_rate", "cohort": "2022-23"},
        {"measure": "retention", "cohort": "2019-20"},
        {"measure": "retention", "cohort": "2022-23", "group_by": "first_gen"},
        {"cohort": "2022-23"},
    ],
)
def test_values_outside_the_lists_are_422(fake, client, params) -> None:
    """Values the API doesn't offer are refused before anything is calculated."""
    assert client.get(URL, params=params).status_code == 422
    assert fake.calls == []


@pytest.mark.parametrize("group_by", [["pell", "race", "gender"], ["pell", "pell"]])
def test_bad_group_by_is_422_with_our_error_body(fake, client, group_by) -> None:
    """More than two dimensions, or the same one twice, gets a clear error."""
    response = client.get(URL, params={"measure": "retention", "cohort": "2022-23", "group_by": group_by})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_group_by"


def test_missing_data_is_503(tmp_path, monkeypatch, client) -> None:
    """Without the normalized data, the API says how to load it."""
    monkeypatch.setattr(results, "data_path", lambda: tmp_path / "missing.sqlite")
    response = get(client, measure="retention", cohort="2022-23", group_by="pell")
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "data_missing"
    assert client.get("/api/v1/uncf/health").json() == {"status": "ok", "data_available": False, "loaded_at": None}


def test_health_reports_the_load_time(data_file, client) -> None:
    """Health says the data is loaded, and when."""
    assert client.get("/api/v1/uncf/health").json() == {"status": "ok", "data_available": True, "loaded_at": LOADED}


def test_options_offer_only_defined_measures(client) -> None:
    """Every measure offered has a definition, labelled with its on-screen name."""
    body = client.get("/api/v1/uncf/options").json()
    assert [m["value"] for m in body["measures"]] == list(get_args(ApiMeasure))
    assert all(m["label"] == DEFINITIONS[m["value"]]["name"] for m in body["measures"])
    assert [d["value"] for d in body["dimensions"]] == list(get_args(Dimension))
    assert body["max_group_by"] == 2


def test_cors_allows_the_playground_client(fake, client) -> None:
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
    results.clear_cache()
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

    results.clear_cache()
    connection = sqlite3.connect(f"file:{DEFAULT_DATABASE}?mode=ro", uri=True)
    groupings = [[]] + [[d] for d in get_args(Dimension)] + [sorted(p) for p in combinations(get_args(Dimension), 2)]
    checked = 0
    try:
        for measure in get_args(ApiMeasure):
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
    results.clear_cache()
    for measure in get_args(ApiMeasure):
        for cohort in ["2021-22", "2022-23", "2023-24", "2024-25"]:
            for dimension in get_args(Dimension):
                response = get(client, measure=measure, cohort=cohort, group_by=dimension)
                assert response.status_code == 200, (measure, cohort, dimension)
                for row in response.json()["rows"]:
                    if row["status"] != "ok":
                        assert row["rate"] is None and row["numerator"] is None
