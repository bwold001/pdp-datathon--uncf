"""Serialized v1 responses and inactive v2 adapters share independently specified synthetic counts."""

import csv
import io

import pytest
from fastapi.testclient import TestClient

from analytics.analysis_service import AnalysisService
from analytics.coverage import Coverage
from analytics.data_access import sqlite_snapshot
from analytics.tests.test_defined_operations import defined_data as defined_data  # noqa: PLC0414 - register the shared pytest fixture
from analytics.tests.test_defined_operations import request
from api import data, route


@pytest.mark.parametrize(
    "operation,measure,numerator,denominator,extra",
    [
        ("dfw.rate", "dfw_rate", 12, 24, {}),
        ("credit_completion.ratio", "credit_completion", 35 / 6, 12, {}),
        ("retention.rate", "retention", 6, 12, {"retention_type": "school"}),
    ],
)
def test_api_json_csv_and_v2_preserve_the_same_arithmetic(
    defined_data, monkeypatch, operation, measure, numerator, denominator, extra
):
    """Fractional ratios and enrollment denominators survive each serialization boundary."""
    monkeypatch.setattr(data, "data_path", lambda: defined_data)
    route.clear_cache()
    with (
        TestClient(route.create_app()) as client,
        sqlite_snapshot(defined_data) as snapshot,
    ):
        v1 = client.get(
            f"/api/v1/uncf/measures/{measure}", params={"cohort": "2023-24", **extra}
        )
        assert v1.status_code == 200
        row = v1.json()["rows"][0]
        v2 = (
            AnalysisService(Coverage())
            .execute(request(operation, **extra), snapshot)
            .result.model_dump(mode="json")["payload"]
        )
        exported = client.get(
            f"/api/v1/uncf/measures/{measure}",
            params={"cohort": "2023-24", "format": "csv", **extra},
        )
        csv_row = next(csv.DictReader(io.StringIO(exported.text)))
        for actual in (row["numerator"], v2["numerator"], float(csv_row["numerator"])):
            assert actual == pytest.approx(numerator)
        assert (
            row["denominator"]
            == v2["denominator"]
            == float(csv_row["denominator"])
            == denominator
        )
    route.clear_cache()


def test_gateway_adapter_uses_the_same_gap_projection_as_the_api(
    defined_data, monkeypatch
):
    """Only the existing gap finder may replace pair counts and attach course comparisons."""
    monkeypatch.setattr(data, "data_path", lambda: defined_data)
    route.clear_cache()
    with (
        TestClient(route.create_app()) as client,
        sqlite_snapshot(defined_data) as snapshot,
    ):
        v1 = client.get("/api/v1/uncf/gateway", params={"cohort": "2023-24"}).json()
        evidence = AnalysisService(Coverage()).execute(
            request("gateway.course_outcomes", retention_type="school"), snapshot
        )
        paths = {
            row.cells[0]: row.cells[1]
            for row in evidence.result.payload.rows
            if row.status == "ok"
        }
        assert paths["courses[0].first_pass"] == v1["courses"][0]["first_pass"] == 12
        assert not any("pair_counts" in path or "all_takers" in path for path in paths)
        assert v1["pairs"] == []
    route.clear_cache()
