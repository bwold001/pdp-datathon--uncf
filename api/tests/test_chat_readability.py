"""The HTTP boundary preserves explanations and explicit scope without changing dashboard results."""

from fastapi.testclient import TestClient

from analytics.coverage import Coverage
from analytics.service import AnalyticsService
from analytics.tests.test_answer_presentation import database as database  # noqa: PLC0414 - pytest fixture
from analytics.tests.test_answer_presentation import graduation_step
from api.analysis_v2 import get_runtime_factory
from api.route import create_app


def test_chemistry_confirm_execute_and_replay_without_provider(database):
    """The exact selected scope gets early guidance and a meaningful answer after confirmation."""
    app = create_app()
    runtime = AnalyticsService(database, Coverage())
    app.dependency_overrides[get_runtime_factory] = lambda: lambda: runtime
    prefix = "/api/v1/uncf/analysis-v2"
    with TestClient(app) as client:
        catalog = client.get(prefix + "/catalog").json()
        assert all(
            item["operation_id"] != "legacy.graduation"
            for item in catalog["suggestions"]
        )
        raw = {
            "kind": "proposed",
            "catalog_version": catalog["catalog_version"],
            "snapshot_ref": catalog["snapshot_ref"],
            "steps": [graduation_step().model_dump(mode="json")],
        }
        reviewed = client.post(prefix + "/validate", json=raw).json()
        assert reviewed["status"] == "confirmation" and not reviewed["receipts"]
        assert any(
            "haven't verified" in item["message"] for item in reviewed["guidance"]
        )
        executed = client.post(prefix + "/execute", json=reviewed["plan"])
        assert executed.status_code == 200
        body = executed.json()
        receipt = body["receipts"][0]
        assert receipt["request"]["parameters"] == {
            "cohort": "2022-23",
            "credential": "B",
            "program": "chemistry_family",
        }
        assert (
            receipt["presentation"]["summary"]
            == "A graduation rate isn't available for this selection."
        )
        assert len(receipt["result"]["payload"]["rows"]) == 15
        assert all(
            row["explanation"]["reason"] == "followup_not_verified"
            for row in receipt["result"]["payload"]["rows"]
        )
        replayed = client.post(prefix + "/execute", json=body["replay"]).json()
        assert replayed["receipts"][0]["presentation"] == receipt["presentation"]
