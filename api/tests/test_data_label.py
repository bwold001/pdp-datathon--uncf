"""UNCF_DATA_LABEL: every answer, receipt and chat instruction says whether the data is synthetic or a school's own.

One setting decides it for the API, the analytics receipts and the chat, so the pages and the chat can't disagree.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from analytics.coverage import Coverage
from analytics.service import AnalyticsService
from analytics.tests.test_defined_operations import defined_data as defined_data  # noqa: PLC0414 - pytest fixture
from analytics.tests.test_defined_operations import request
from api import data, route
from api.analysis_v2 import get_runtime_factory
from api.route import create_app
from measures.run_measures import configured_data_label
from measures.tests.explorer_fixture import make_database, student

PREFIX = "/api/v1/uncf"


@pytest.fixture
def pages(tmp_path, monkeypatch):
    """The Explorer API over a small 2023-24 class."""
    path = make_database(tmp_path / "pdp.sqlite", [student(f"s{n}", retention=1) for n in range(4)])
    monkeypatch.setattr(data, "data_path", lambda: path)
    route.clear_cache()
    yield TestClient(create_app())
    route.clear_cache()


@pytest.fixture
def chat_api(defined_data, monkeypatch):
    """The chat's plan API over the analytics fixture, with no model provider."""
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    app = create_app()
    runtime = AnalyticsService(defined_data, Coverage())
    app.dependency_overrides[get_runtime_factory] = lambda: lambda: runtime
    with TestClient(app) as browser:
        yield browser


def run_plan(client: TestClient) -> dict:
    """Execute one school retention step through the chat's plan API."""
    catalog = client.get(f"{PREFIX}/analysis-v2/catalog").json()
    plan = {
        "kind": "executable",
        "catalog_version": catalog["catalog_version"],
        "snapshot_ref": catalog["snapshot_ref"],
        "steps": [request("retention.rate", retention_type="school")],
    }
    return client.post(f"{PREFIX}/analysis-v2/execute", json=plan).json()


def test_the_setting_defaults_to_synthetic(monkeypatch) -> None:
    """Unset, the data is the synthetic sample; "institution" names a school's files; anything else is refused."""
    monkeypatch.delenv("UNCF_DATA_LABEL", raising=False)
    assert configured_data_label() == "synthetic"
    monkeypatch.setenv("UNCF_DATA_LABEL", " Institution ")
    assert configured_data_label() == "institution"
    monkeypatch.setenv("UNCF_DATA_LABEL", "real")
    with pytest.raises(ValueError, match="UNCF_DATA_LABEL"):
        configured_data_label()


@pytest.mark.parametrize("label", ["synthetic", "institution"])
def test_every_explorer_answer_carries_the_label(pages, monkeypatch, label) -> None:
    """Page meta, a measure's meta, the cohort options and health all say what kind of data answered."""
    monkeypatch.setenv("UNCF_DATA_LABEL", label)
    assert pages.get(f"{PREFIX}/gateway", params={"cohort": "2023-24"}).json()["meta"]["data_label"] == label
    measure = pages.get(f"{PREFIX}/measures/retention", params={"cohort": "2023-24"}).json()
    assert measure["meta"]["data_label"] == label
    assert pages.get(f"{PREFIX}/cohort-options", params={"cohort": "2023-24"}).json()["data_label"] == label
    assert pages.get(f"{PREFIX}/health").json()["data_label"] == label


def test_an_unknown_label_is_a_503_not_a_wrong_label(pages, monkeypatch) -> None:
    """A mistyped setting stops the pages with config_invalid, and health shows no label, rather than guessing."""
    monkeypatch.setenv("UNCF_DATA_LABEL", "real")
    response = pages.get(f"{PREFIX}/gateway", params={"cohort": "2023-24"})
    assert response.status_code == 503 and response.json()["error"]["code"] == "config_invalid"
    measure = pages.get(f"{PREFIX}/measures/retention", params={"cohort": "2023-24"})
    assert measure.status_code == 503 and measure.json()["error"]["code"] == "config_invalid"
    assert pages.get(f"{PREFIX}/health").json()["data_label"] is None


def test_chat_receipts_say_synthetic_by_default(chat_api, monkeypatch) -> None:
    """On the sample, each receipt is labelled synthetic and says so, and so does the summary line."""
    monkeypatch.delenv("UNCF_DATA_LABEL", raising=False)
    body = run_plan(chat_api)
    receipt = body["receipts"][0]
    assert receipt["source"]["label"] == "synthetic"
    assert "All results are synthetic." in receipt["assumptions"]
    assert body["message"] == "Synthetic execution completed."


def test_chat_receipts_on_a_schools_data_drop_synthetic(chat_api, monkeypatch) -> None:
    """On a school's files, no receipt, limitation or summary line calls the results synthetic."""
    monkeypatch.setenv("UNCF_DATA_LABEL", "institution")
    body = run_plan(chat_api)
    receipt = body["receipts"][0]
    assert receipt["source"]["label"] == "institution"
    words = [*receipt["assumptions"], *receipt["limitations"], receipt["source"]["coverage"], body["message"]]
    assert not any("synthetic" in line.lower() for line in words), words
    assert body["message"] == "Execution completed."


def test_older_analysis_receipts_follow_the_setting(defined_data, monkeypatch) -> None:
    """The first chat's catalog and receipts (analytics/service.py) use the same setting."""
    monkeypatch.setenv("UNCF_DATA_LABEL", "institution")
    assert AnalyticsService(defined_data, Coverage()).catalog()["source"] == "institution"
