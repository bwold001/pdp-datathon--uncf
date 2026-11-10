"""Configured-database parity for every preserved PR #24 analysis."""

import os
import sqlite3
from uuid import uuid4

import psycopg
import pytest
import yaml
from analytics.service import AnalyticsService
from analytics.tests.analytics_fixtures import build_database, fixture_coverage
from sqlalchemy.engine import make_url

from app.chat.routes import get_chat_client
from app.core.config import settings
from app.main import app
from app.services.analytics import database
from tests.test_student_success_tools import ScriptedModel, call, finish

REQUESTS = [
    {"analysis": "retention", "cohort": "2022-23"},
    {"analysis": "enrollment"},
    {
        "analysis": "graduation",
        "cohort": "2022-23",
        "credential": "B",
        "program": "chemistry_general",
    },
    {
        "analysis": "graduation",
        "cohort": "2022-23",
        "credential": "B",
        "program": "chemistry_family",
    },
]


@pytest.fixture
def configured_data(tmp_path, monkeypatch):
    """The selected Playground file is distinct from the standalone extract."""
    path = build_database(tmp_path / "uploaded.sqlite")
    coverage = fixture_coverage()
    config = tmp_path / "coverage.yaml"
    config.write_text(yaml.safe_dump(coverage.model_dump()))
    monkeypatch.setenv("UNCF_ANALYTICS_CONFIG", str(config))
    monkeypatch.setattr(settings, "DATABASE_URL", f"sqlite:///{path}")
    yield path, coverage
    app.dependency_overrides.pop(get_chat_client, None)


@pytest.mark.parametrize("analysis_request", REQUESTS)
@pytest.mark.parametrize(
    "url", ["/api/v1/chat", "/api/v1/uncf/chat", "/api/v1/sandbox/chat/suggest"]
)
def test_all_chat_paths_match_direct_service(client, configured_data, analysis_request, url):
    """Old URLs and the new URL execute the same rich, deterministic analyses."""
    path, coverage = configured_data
    analysis, parameters = (
        analysis_request["analysis"],
        {k: v for k, v in analysis_request.items() if k != "analysis"},
    )
    model = ScriptedModel([call(analysis, **parameters)], [finish()])
    app.dependency_overrides[get_chat_client] = lambda: model
    reply = client.post(url, json={"prompt": "Synthetic parity example"})
    assert reply.json()["status"] == "confirmation" and not reply.json()["receipts"]
    reply = client.post(url, json={"prompt": "confirmed", "confirmed": reply.json()["proposals"]})
    expected = AnalyticsService(path, coverage).analyze(analysis_request).model_dump(mode="json")
    assert reply.status_code == 200
    assert reply.json()["receipts"] == expected["receipts"]
    assert "99.9" not in reply.json()["message"]
    direct = client.post("/api/v1/uncf/analyses", json=analysis_request)
    assert direct.json()["receipts"] == expected["receipts"]


def test_reload_is_visible_without_restart(client, configured_data):
    """Upload replacement changes both counts and provenance without a cache reset."""
    path, _ = configured_data
    analysis_request = {"analysis": "retention", "cohort": "2022-23"}
    first = client.post("/api/v1/uncf/analyses", json=analysis_request).json()["receipts"][0]
    with sqlite3.connect(path) as db:
        db.execute("UPDATE cohort_membership SET retention=0 WHERE cohort='2022-23'")
        db.execute("UPDATE data_provider SET loaded_at='2026-07-01'")
    second = client.post("/api/v1/uncf/analyses", json=analysis_request).json()["receipts"][0]
    assert first["rows"][0]["rate"] == 0.5
    assert second["rows"][0]["rate"] == 0
    assert first["source_stamp"] != second["source_stamp"]


def test_missing_configured_data_never_falls_back(client, configured_data, monkeypatch, tmp_path):
    """Missing selected data cannot be replaced by the standalone sample."""
    missing = tmp_path / "missing.sqlite"
    monkeypatch.setattr(settings, "DATABASE_URL", f"sqlite:///{missing}")
    body = client.post("/api/v1/uncf/analyses", json={"analysis": "enrollment"}).json()
    assert body["receipts"][0]["rows"][0]["status"] == "unavailable"
    assert body["receipts"][0]["rows"][0]["count"] is None
    assert not missing.exists()


def test_sqlite_adapter_refuses_writes(configured_data):
    """The read-only snapshot cannot mutate uploaded data."""
    from analytics.service import DataUnavailable

    with pytest.raises(DataUnavailable), database() as connection:
        connection.execute("DELETE FROM cohort_membership")


@pytest.fixture
def postgres_data(configured_data, monkeypatch):
    """Use a disposable PostgreSQL schema containing the exact SQLite fixture."""
    path, coverage = configured_data
    url = os.getenv("PDP_TEST_POSTGRES_URL")
    if not url:
        if os.getenv("PDP_REQUIRE_POSTGRES") == "1":
            pytest.fail("PDP_REQUIRE_POSTGRES=1 needs PDP_TEST_POSTGRES_URL")
        pytest.skip("PDP_TEST_POSTGRES_URL is not configured")
    schema = f"analytics_test_{uuid4().hex}"
    with psycopg.connect(url, autocommit=True) as connection:
        connection.execute(f'CREATE SCHEMA "{schema}"')
        try:
            connection.execute(f'SET search_path TO "{schema}"')
            with sqlite3.connect(path) as source:
                for statement in source.iterdump():
                    if statement not in ("BEGIN TRANSACTION;", "COMMIT;"):
                        connection.execute(statement)
            connection.execute(
                "ALTER TABLE data_provider ALTER COLUMN loaded_at TYPE TIMESTAMP "
                "USING loaded_at::timestamp"
            )
            selected = make_url(url).update_query_dict({"options": f"-csearch_path={schema}"})
            monkeypatch.setattr(
                settings, "DATABASE_URL", selected.render_as_string(hide_password=False)
            )
            yield path, coverage
        finally:
            connection.execute(f'DROP SCHEMA "{schema}" CASCADE')


@pytest.mark.parametrize("analysis_request", REQUESTS)
def test_postgres_results_equal_sqlite_results(client, postgres_data, analysis_request):
    """Driver adaptation cannot change horizons, group attribution or formulas."""
    path, coverage = postgres_data
    expected = AnalyticsService(path, coverage).analyze(analysis_request).model_dump(mode="json")
    actual = client.post("/api/v1/uncf/analyses", json=analysis_request)
    assert actual.status_code == 200
    assert actual.json() == expected


def test_postgres_adapter_refuses_writes(postgres_data):
    """PostgreSQL enforces read-only access below the tools layer."""
    from analytics.service import DataUnavailable

    with pytest.raises(DataUnavailable), database() as connection:
        connection.execute("DELETE FROM cohort_membership")
