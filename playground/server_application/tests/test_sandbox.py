import time
from pathlib import Path

import pdp_model
import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import create_app
from app.sandbox.chart_examples.schemas import ChartName
from app.sandbox.pipeline import service, uploads

CHART_EXAMPLES = "/api/v1/sandbox/chart-examples"
ADD_A_SANDBOX_PAGE = "/api/v1/sandbox/add-a-sandbox-page"
KPI_EXAMPLES = "/api/v1/sandbox/kpi-examples"
ENDPOINTS = [
    CHART_EXAMPLES,
    ADD_A_SANDBOX_PAGE,
    "/api/v1/sandbox/measures/by-group",
    KPI_EXAMPLES,
]


@pytest.mark.parametrize("path", ENDPOINTS)
def test_sandbox_endpoints_return_labelled_data(client: TestClient, path: str) -> None:
    response = client.get(path)

    assert response.status_code == 200
    body = response.json()
    # An endpoint answers with one response, or with several by name.
    for chart in [body] if "meta" in body else body.values():
        assert chart["meta"]["source"] in {"mock", "synthetic"}
        assert chart["meta"]["title"]
        assert chart.get("rows") or chart.get("items")


def test_worked_example_answers_with_labelled_charts_by_name(client: TestClient) -> None:
    everything = client.get(ADD_A_SANDBOX_PAGE).json()
    one = client.get(ADD_A_SANDBOX_PAGE, params={"charts": "by-program"}).json()

    assert everything.keys() == {"by-modality", "by-program"}
    assert one.keys() == {"by-program"}
    for chart in everything.values():
        assert chart["meta"]["source"] == "mock"
        assert chart["meta"]["title"]
        assert chart["rows"]


def test_chart_examples_answers_with_every_labelled_chart_by_default(client: TestClient) -> None:
    response = client.get(CHART_EXAMPLES)

    assert response.status_code == 200
    charts = response.json()
    assert charts.keys() == {chart_name.value for chart_name in ChartName}
    for chart in charts.values():
        assert chart["meta"]["source"] == "mock"
        assert chart["meta"]["title"]
        assert chart["rows"]


def test_chart_examples_answers_with_only_the_charts_named(client: TestClient) -> None:
    one = client.get(CHART_EXAMPLES, params={"charts": "entry-status-share"}).json()
    several = client.get(CHART_EXAMPLES, params={"charts": ["gender-share", "headcount"]}).json()

    assert one.keys() == {"entry-status-share"}
    assert {"status", "share"} == one["entry-status-share"]["rows"][0].keys()
    assert several.keys() == {"gender-share", "headcount"}


def test_chart_examples_rejects_an_unknown_chart(client: TestClient) -> None:
    response = client.get(CHART_EXAMPLES, params={"charts": "not-a-chart"})

    assert response.status_code == 422


def test_gateway_completion_has_both_series_for_six_terms(client: TestClient) -> None:
    rows = client.get(CHART_EXAMPLES, params={"charts": "gateway-completion"}).json()[
        "gateway-completion"
    ]["rows"]

    assert len(rows) == 6
    assert all({"term", "english", "math"} <= row.keys() for row in rows)


def test_kpi_examples_include_percent_split_and_terms_cards(client: TestClient) -> None:
    groups = client.get(KPI_EXAMPLES).json()
    progress = {item["id"]: item for item in groups["student-progress"]["items"]}
    mix = {item["id"]: item for item in groups["student-mix"]["items"]}
    time_to_complete = {item["id"]: item for item in groups["time-to-complete"]["items"]}

    assert progress["first_year_credit_completion"] == {
        "id": "first_year_credit_completion",
        "label": "First-year credit completion",
        "unit": "percent",
        "value": 76.0,
        "secondary_value": None,
        "detail": "fall 2025 cohort",
    }
    assert (mix["female_male"]["value"], mix["female_male"]["secondary_value"]) == (64, 36)
    assert time_to_complete["time_to_complete"]["unit"] == "terms"


def test_kpi_examples_answers_with_only_the_groups_named(client: TestClient) -> None:
    one = client.get(KPI_EXAMPLES, params={"charts": "student-mix"}).json()

    assert one.keys() == {"student-mix"}
    assert client.get(KPI_EXAMPLES, params={"charts": "not-a-group"}).status_code == 422


def test_persistence_retention_carries_filters_and_definitions(client: TestClient) -> None:
    meta = client.get(CHART_EXAMPLES, params={"charts": "persistence-retention"}).json()[
        "persistence-retention"
    ]["meta"]

    assert meta["filters"] == ["Fall entry", "New + Transfer"]
    assert meta["definitions"]["Persistence"] == "Students continuing anywhere"


def test_sandbox_is_not_mounted_when_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "SANDBOX_ENABLED", False)

    with TestClient(create_app()) as client:
        assert client.get(CHART_EXAMPLES).status_code == 404
        assert client.get(ADD_A_SANDBOX_PAGE).status_code == 404
        assert client.get("/api/v1/health").status_code == 200


def test_measures_by_group_returns_exact_fixture_rates_and_counts(client: TestClient) -> None:
    body = client.get(
        "/api/v1/sandbox/measures/by-group?measure=gateway_math&cohort=2022-23&group_by=gender"
    ).json()

    assert body["meta"]["source"] == "synthetic"
    assert body["meta"]["filters"] == [
        "Measure: Gateway math completion",
        "Cohort: 2022-23",
        "Group by: Gender",
    ]
    assert body["rows"] == [
        {"group": "F", "rate": 26.1, "n": 620},
        {"group": "M", "rate": 25.4, "n": 456},
        {"group": "Unknown", "rate": 34.7, "n": 72},
        {"group": "X", "rate": None, "n": None},
    ]


def test_measures_by_group_rejects_unknown_cohort(client: TestClient) -> None:
    response = client.get("/api/v1/sandbox/measures/by-group?cohort=2020-21")

    assert response.status_code == 422


# --- /sandbox/pipeline: uploads, load runs and table previews -------------------------------

PIPELINE = "/api/v1/sandbox/pipeline"
SAMPLE = pdp_model.MODEL_DIR / "data/input/sample"  # the 10 sample students, as raw files


@pytest.fixture
def pipeline_dirs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Uploads and table files go to a temporary folder, not the repo's."""
    monkeypatch.setattr(uploads, "UPLOADS_DIR", tmp_path / "uploads")
    monkeypatch.setattr(service, "TABLES_DIR", tmp_path / "tables")
    return tmp_path


def _upload(client: TestClient, kind: str, content: bytes, filename: str = "file.csv"):
    return client.post(
        f"{PIPELINE}/uploads", data={"kind": kind}, files={"file": (filename, content, "text/csv")}
    )


def _wait_for(client: TestClient, run_id: str, seconds: float = 120) -> dict:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        run = client.get(f"{PIPELINE}/runs/{run_id}").json()
        if run["status"] != "running":
            return run
        time.sleep(0.2)
    raise AssertionError(f"run {run_id} was still running after {seconds}s")


def test_pipeline_loads_uploaded_sample_files(client: TestClient, pipeline_dirs: Path) -> None:
    cohort = _upload(client, "cohort", (SAMPLE / "pdp_cohort_data.csv").read_bytes())
    course = _upload(client, "course", (SAMPLE / "pdp_course_data.csv").read_bytes())
    assert (cohort.status_code, course.status_code) == (201, 201)
    assert cohort.json()["unexpected_columns"] == []
    listed = [u["upload_id"] for u in client.get(f"{PIPELINE}/uploads").json()["uploads"]]
    assert set(listed) == {cohort.json()["upload_id"], course.json()["upload_id"]}

    started = client.post(
        f"{PIPELINE}/runs",
        json={
            "cohort_upload_id": cohort.json()["upload_id"],
            "course_upload_id": course.json()["upload_id"],
        },
    )
    assert started.status_code == 202
    run = _wait_for(client, started.json()["run_id"])

    assert run["status"] == "succeeded", run["error"]
    assert run["progress"]
    # The sample's known counts: data/output/sample/ in the data model.
    assert run["summary"]["tables"]["student"] == 10
    assert run["summary"]["tables"]["course_enrollment"] == 52
    counts = {t["name"]: t["row_count"] for t in client.get(f"{PIPELINE}/tables").json()["tables"]}
    assert list(counts) == pdp_model.table_names()
    assert counts["student"] == 10
    preview = client.get(f"{PIPELINE}/tables/student?limit=3").json()
    assert len(preview["rows"]) == 3
    assert "student_id" in preview["columns"]
    first_page = client.get(f"{PIPELINE}/tables/student?limit=6").json()["rows"]
    last_page = client.get(f"{PIPELINE}/tables/student?limit=6&offset=6").json()
    assert last_page["offset"] == 6
    assert len(last_page["rows"]) == 4
    first_ids = {row["student_id"] for row in first_page}
    assert first_ids.isdisjoint(row["student_id"] for row in last_page["rows"])


def test_pipeline_upload_refuses_a_file_missing_a_column(
    client: TestClient, pipeline_dirs: Path
) -> None:
    lines = (SAMPLE / "pdp_cohort_data.csv").read_text().splitlines()
    header = lines[0].split(",")
    without_cohort = ",".join(c for c in header if c != "Cohort")

    response = _upload(client, "cohort", (without_cohort + "\n").encode())

    assert response.status_code == 422
    assert "Cohort" in response.json()["error"]["message"]
    assert not list((pipeline_dirs / "uploads").iterdir())


def test_pipeline_upload_refuses_a_non_csv_and_an_oversized_file(
    client: TestClient, pipeline_dirs: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = (SAMPLE / "pdp_cohort_data.csv").read_bytes()
    assert _upload(client, "cohort", content, filename="cohort.xlsx").status_code == 422

    monkeypatch.setattr(settings, "PIPELINE_UPLOAD_MAX_BYTES", 100)
    assert _upload(client, "cohort", content).status_code == 413


def test_pipeline_run_checks_its_upload_ids(client: TestClient, pipeline_dirs: Path) -> None:
    course = _upload(client, "course", (SAMPLE / "pdp_course_data.csv").read_bytes()).json()

    unknown = client.post(f"{PIPELINE}/runs", json={"cohort_upload_id": "0" * 32})
    wrong_kind = client.post(f"{PIPELINE}/runs", json={"cohort_upload_id": course["upload_id"]})

    assert unknown.status_code == 404
    assert wrong_kind.status_code == 422


def test_pipeline_run_without_uploads_loads_the_configured_files(
    client: TestClient, pipeline_dirs: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls = []

    def fake_load(database_url, run_id, **kwargs):
        calls.append(kwargs)
        validation = {
            "pdp_cohort_data.csv": {"run_id": run_id},
            "on_campus_housing.csv": {"run_id": f"{run_id}-on_campus_housing"},
        }
        held_back = [
            {"source_file": "pdp_cohort_data.csv"},
            {"source_file": "on_campus_housing.csv"},  # enrichment: not counted
        ]
        return {
            "run_id": run_id,
            "status": "loaded",
            "tables": {},
            "validation": validation,
            "held_back": held_back,
        }

    monkeypatch.setattr(pdp_model, "run_load", fake_load)

    run = _wait_for(client, client.post(f"{PIPELINE}/runs").json()["run_id"])

    assert run["status"] == "succeeded"
    assert (calls[0]["cohort"], calls[0]["course"]) == (None, None)
    assert calls[0]["tables_dir"] == pipeline_dirs / "tables"
    assert run["summary"]["held_back_rows"] == 1
    assert "held_back" not in run["summary"]


def test_pipeline_refuses_a_second_run_while_one_is_loading(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(service, "_active_run", "20260101T000000Z-abcdef")

    response = client.post(f"{PIPELINE}/runs")

    assert response.status_code == 409


def test_pipeline_unknown_table_and_run_are_404(client: TestClient) -> None:
    assert client.get(f"{PIPELINE}/tables/documents").status_code == 404
    assert client.get(f"{PIPELINE}/runs/no-such-run").status_code == 404


# --- /sandbox/dictionary: what each normalized column means --------------------------------

DICTIONARY = "/api/v1/sandbox/dictionary"


def test_dictionary_column_has_every_source_and_its_stored_codes(client: TestClient) -> None:
    response = client.get(f"{DICTIONARY}/columns/student/gender")

    assert response.status_code == 200
    body = response.json()
    assert body["description_source"] == "pdp_cohort_data.csv"
    assert [s["source_file"] for s in body["sources"]] == [
        "pdp_cohort_data.csv",
        "pdp_course_data.csv",
    ]
    assert {"code": "UK", "meaning": "Unknown"} in body["dictionary_values"]
    assert body["stored"]["allowed_values"] == ["M", "F", "P", "X"]
    assert body["stored"]["unknown_value"] == "UNKNOWN"


def test_dictionary_404_says_whether_the_model_has_the_column(client: TestClient) -> None:
    generated = client.get(f"{DICTIONARY}/columns/term/sort_order")
    unknown = client.get(f"{DICTIONARY}/columns/student/no_such_column")

    assert generated.status_code == 404
    assert "no dictionary entry" in generated.json()["error"]["message"]
    assert unknown.status_code == 404
    assert "isn't a column of the data model" in unknown.json()["error"]["message"]


def test_dictionary_list_filters_by_table_and_source_file(client: TestClient) -> None:
    every = client.get(f"{DICTIONARY}/columns").json()
    students = client.get(f"{DICTIONARY}/columns?table=student").json()["columns"]
    course = client.get(f"{DICTIONARY}/columns?source_file=pdp_course_data.csv").json()["columns"]

    assert len(every["columns"]) == len(pdp_model.column_dictionary())
    assert "synthetic" in every["note"]
    assert students and {c["table"] for c in students} == {"student"}
    assert course and all(
        "pdp_course_data.csv" in [s["source_file"] for s in c["sources"]] for c in course
    )
    assert "math_placement" not in [c["column"] for c in course]
