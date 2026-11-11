"""Dashboard JSON/CSV and defined v2 evidence retain the original disclosure boundary."""

import csv
import io
import sqlite3

import pytest
from fastapi.testclient import TestClient

from analytics.analysis_service import AnalysisService
from analytics.coverage import Coverage
from analytics.data_access import sqlite_snapshot
from analytics.disclosure import disclose_plan, stage_defined
from analytics.tests.test_defined_operations import defined_data as defined_data  # noqa: PLC0414 - pytest fixture
from analytics.tests.test_defined_operations import request
from api import data, route
from measures import service as measures_service


def test_dashboard_single_success_remains_visible_in_api_csv_and_v2(
    defined_data, monkeypatch
):
    """One success of twelve is visible on the dashboard and must not receive legacy complement suppression."""
    with sqlite3.connect(defined_data) as db:
        db.execute(
            "UPDATE cohort_membership SET retention=CASE WHEN student_id='s0' THEN 1 ELSE 0 END"
        )
    monkeypatch.setattr(data, "data_path", lambda: defined_data)
    route.clear_cache()
    service = AnalysisService(Coverage())
    with (
        TestClient(route.create_app()) as client,
        sqlite_snapshot(defined_data) as snapshot,
    ):
        response = client.get(
            "/api/v1/uncf/measures/retention", params={"cohort": "2023-24"}
        )
        row = response.json()["rows"][0]
        exported = client.get(
            "/api/v1/uncf/results",
            params={"measure": "retention", "cohort": "2023-24", "format": "csv"},
        )
        csv_row = next(csv.DictReader(io.StringIO(exported.text)))
        evidence = service.execute(
            request("retention.rate", retention_type="school"), snapshot
        )
        (projected,) = disclose_plan(
            (stage_defined("official", service.operations["retention.rate"], evidence),)
        )
        assert row["status"] == csv_row["status"] == projected.result.status == "ok"
        assert (
            row["numerator"]
            == float(csv_row["numerator"])
            == projected.result.payload.numerator
            == 1
        )
        assert row["denominator"] == projected.result.payload.denominator == 12
        assert (
            projected.profile.id == "dashboard_v1" and projected.profile.version == "1"
        )
        serialized = disclosed_receipt(service, snapshot, projected.result)
        assert (
            serialized.result.payload.numerator == 1
            and serialized.result.payload.denominator == 12
        )
        assert serialized.versions.disclosure == "dashboard_v1"
    route.clear_cache()


def disclosed_receipt(service, snapshot, result):
    """Serialize the real executed synthetic scope/provenance to check the final v2 receipt boundary."""
    from datetime import datetime, timezone

    from analytics.contracts_v2 import (
        ExecutablePlan,
        Receipt,
        VersionReference,
        Versions,
    )
    from analytics.provenance import make_replay_spec, step_fingerprint

    plan = ExecutablePlan.model_validate(
        {
            "kind": "executable",
            "catalog_version": service.catalog()["version"],
            "snapshot_ref": snapshot.identity.snapshot_ref,
            "steps": [request("retention.rate", retention_type="school")],
        }
    )
    versions = Versions(
        catalog=plan.catalog_version,
        pipeline=snapshot.identity.pipeline_version,
        implementation="fixture-1",
        configuration="fixture-1",
        coverage="fixture-1",
        disclosure="dashboard_v1",
    )
    replay = make_replay_spec(
        plan,
        snapshot.identity,
        versions,
        (VersionReference(id="retention.rate", version="1"),),
        service.coverage,
    )
    stamp = datetime(2026, 11, 10, tzinfo=timezone.utc)
    receipt = Receipt(
        schema_version=2,
        step_id=plan.steps[0].step_id,
        request=plan.steps[0],
        operation_id="retention.rate",
        operation_version="1",
        population="Synthetic selected cohort",
        time_window="Next academic year",
        grain="student and entry cohort",
        definitions=(VersionReference(id="retention", version="1"),),
        source={
            "label": "synthetic",
            "snapshot_ref": snapshot.identity.snapshot_ref,
            "fingerprint": snapshot.identity.source_fingerprint,
            "loaded_at": snapshot.identity.loaded_at,
            "coverage": "Hand-counted synthetic fixture",
        },
        versions=versions,
        computation_fingerprint=step_fingerprint(replay, plan.steps[0].step_id),
        execution_id="fixture-execution",
        started_at=stamp,
        completed_at=stamp,
        result=result,
    )
    return Receipt.model_validate_json(receipt.model_dump_json())


@pytest.mark.parametrize(
    "path,operation,extra",
    [
        ("student-paths", "student_paths.summary", {}),
        ("dfw", "dfw.course_list", {}),
        ("dfw/course", "dfw.course_detail", {"course": "ENG 101"}),
        ("credit-momentum", "credit_momentum.summary", {}),
        ("gateway", "gateway.course_outcomes", {}),
        ("measures/dfw_rate", "dfw.rate", {}),
        ("results", "dfw.rate", {"measure": "dfw_rate"}),
    ],
)
def test_every_dashboard_and_results_route_uses_the_shared_execution_service(
    defined_data, monkeypatch, path, operation, extra
):
    """No JSON/CSV route retains a separate direct executor after migration."""
    monkeypatch.setattr(data, "data_path", lambda: defined_data)
    route.clear_cache()
    called = []
    owner = measures_service.execute

    def record(id, parameters, snapshot):
        """Observe the actual execution boundary while retaining real database behavior."""
        called.append(id)
        return owner(id, parameters, snapshot)

    monkeypatch.setattr(measures_service, "execute", record)
    with TestClient(route.create_app()) as client:
        for format in ("json", "csv"):
            response = client.get(
                "/api/v1/uncf/" + path,
                params={"cohort": "2023-24", "format": format, **extra},
            )
            assert response.status_code == 200
            if path == "dfw/course" and format == "csv":
                rows = list(csv.DictReader(io.StringIO(response.text)))
                gender = next(
                    row
                    for row in rows
                    if row["section"] == "groups" and row["dimension"] == "gender"
                )
                assert (
                    gender["value"] == "F"
                    and float(gender["num"]) == 12
                    and float(gender["den"]) == 24
                )
        assert called == [operation]
    route.clear_cache()


def test_gateway_unreported_and_hidden_group_statuses_survive_json_and_csv(
    defined_data, monkeypatch
):
    """Hidden values and missing reporting are null/blank with their original status, never zero."""
    with sqlite3.connect(defined_data) as db:
        db.execute(
            "UPDATE cohort_membership SET gateway_math_status=NULL, completed_gateway_math_year1=NULL"
        )
    monkeypatch.setattr(data, "data_path", lambda: defined_data)
    route.clear_cache()
    with (
        TestClient(route.create_app()) as client,
        sqlite_snapshot(defined_data) as snapshot,
    ):
        for measure, extra, hidden_status in (
            ("gateway_math", {}, "not_reported"),
            ("retention", {"pell": "N"}, "suppressed"),
        ):
            params = {"cohort": "2023-24", **extra}
            body = client.get(f"/api/v1/uncf/measures/{measure}", params=params).json()
            row = body["rows"][0]
            assert row["status"] == hidden_status and row["numerator"] is None
            exported = client.get(
                f"/api/v1/uncf/measures/{measure}", params={**params, "format": "csv"}
            )
            csv_row = next(csv.DictReader(io.StringIO(exported.text)))
            assert csv_row["status"] == hidden_status and csv_row["numerator"] == ""
        evidence = AnalysisService(Coverage()).execute(
            request("gateway.math_completion"), snapshot
        )
        assert evidence.result.status == "not_reported"
    route.clear_cache()
