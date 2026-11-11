"""Small synthetic populations stay visible through owners, HTTP exports and v2 adapters."""

import csv
import io

import pytest
from fastapi.testclient import TestClient

from analytics.analysis_service import AnalysisService
from analytics.coverage import Coverage
from analytics.data_access import sqlite_snapshot
from analytics.tests.test_defined_operations import request
from analytics.tests.test_snapshots import add_identity
from api import data, route
from measures.tests.explorer_fixture import here, make_database, student


@pytest.mark.parametrize("size", range(1, 10))
def test_small_results_across_api_csv_and_v2(tmp_path, monkeypatch, size):
    """Each size from one to nine retains counts, fractional ratios and course-list membership."""
    monkeypatch.setenv("UNCF_MIN_STUDENTS", "100")
    students = [
        student(f"s{i}", retention=1, attempted=2, earned=1) for i in range(size)
    ]
    records = [
        here(
            f"s{i}",
            "2023-24",
            "FALL",
            prefix="ENG",
            number="101",
            grade="F",
            gateway="E",
        )
        for i in range(size)
    ]
    path = make_database(tmp_path / "small.sqlite", students, records)
    add_identity(path)
    monkeypatch.setattr(data, "data_path", lambda: path)
    route.clear_cache()
    try:
        with (
            TestClient(route.create_app()) as client,
            sqlite_snapshot(path) as snapshot,
        ):
            for measure, operation, numerator, extra in [
                ("retention", "retention.rate", size, {"retention_type": "school"}),
                ("credit_completion", "credit_completion.ratio", size / 2, {}),
                ("dfw_rate", "dfw.rate", size, {}),
            ]:
                url = f"/api/v1/uncf/measures/{measure}"
                params = {"cohort": "2023-24", **extra}
                response = client.get(url, params=params)
                assert response.status_code == 200
                body = response.json()
                assert body["meta"]["min_students"] == 1
                row = body["rows"][0]
                assert (row["status"], row["numerator"], row["denominator"]) == (
                    "ok",
                    numerator,
                    size,
                )
                exported = client.get(url, params={**params, "format": "csv"})
                assert exported.status_code == 200
                csv_row = next(csv.DictReader(io.StringIO(exported.text)))
                assert (float(csv_row["numerator"]), float(csv_row["denominator"])) == (
                    numerator,
                    size,
                )
                result = (
                    AnalysisService(Coverage())
                    .execute(request(operation, **extra), snapshot)
                    .result
                )
                assert result.status == "ok"
                assert (result.payload.numerator, result.payload.denominator) == (
                    numerator,
                    size,
                )
            dfw = client.get("/api/v1/uncf/dfw", params={"cohort": "2023-24"}).json()
            assert dfw["courses"][0]["course"] == "ENG 101"
            assert dfw["courses"][0]["den"] == size
            gateway = client.get(
                "/api/v1/uncf/gateway", params={"cohort": "2023-24"}
            ).json()
            assert gateway["courses"][0]["students"] == size
    finally:
        route.clear_cache()
