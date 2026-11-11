"""The deterministic v2 API honors Playground's source with chat disabled."""

from analytics.tests.test_snapshots import add_identity
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import create_app
from tests.test_analytics_database import configured_data as configured_data


def test_v2_routes_work_with_chat_disabled_and_use_the_configured_source(
    configured_data, monkeypatch
):
    """Select the uploaded three-student source, independent of the standalone extract."""
    path, _ = configured_data
    add_identity(path)
    monkeypatch.setattr(settings, "UNCF_CHAT_ENABLED", False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    with TestClient(create_app()) as client:
        catalog = client.get("/api/v1/uncf/analysis-v2/catalog")
        assert catalog.status_code == 200
        metadata = catalog.json()
        assert metadata["choices"]["cohorts"] == ["2021-22", "2022-23"]
        plan = {
            "kind": "executable",
            "catalog_version": metadata["catalog_version"],
            "snapshot_ref": metadata["snapshot_ref"],
            "steps": [
                {
                    "step_id": "retention",
                    "kind": "legacy_analysis",
                    "operation_id": "legacy.entry_major_retention",
                    "parameters": {"cohort": "2022-23"},
                }
            ],
        }
        result = client.post("/api/v1/uncf/analysis-v2/execute", json=plan)
        assert result.status_code == 200 and result.json()["outcome"] == "complete"
        receipt = result.json()["receipts"][0]
        assert receipt["source"]["snapshot_ref"] == metadata["snapshot_ref"]
        columns = [c["id"] for c in receipt["result"]["payload"]["columns"]]
        rows = [
            dict(zip(columns, row["cells"], strict=True))
            for row in receipt["result"]["payload"]["rows"]
            if row["status"] == "ok"
        ]
        assert any(
            row["numerator"] == 1 and row["denominator"] == 2 and row["rate"] == 0.5 for row in rows
        )
