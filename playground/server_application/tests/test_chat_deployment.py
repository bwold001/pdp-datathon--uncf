"""Check the actual Vercel entrypoint and chat-only application surface."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from analytics.tests.analytics_fixtures import build_database, fixture_coverage
from fastapi.testclient import TestClient

from app.chat.deployment import create_app
from app.chat.routes import get_chat_client
from app.core.config import settings
from tests.test_student_success_tools import ScriptedModel, call, finish


@pytest.mark.parametrize("path", ["/api/v1/chat", "/api/v1/uncf/chat"])
def test_deployed_chat_reads_configured_database(tmp_path, monkeypatch, path):
    """The hosted app calculates from the configured database and shares direct receipts."""
    import yaml
    from analytics.service import AnalyticsService

    database = build_database(tmp_path / "configured.sqlite")
    coverage = tmp_path / "coverage.yaml"
    coverage.write_text(yaml.safe_dump(fixture_coverage().model_dump(mode="json")))
    monkeypatch.setattr(settings, "DATABASE_URL", f"sqlite:///{database}")
    monkeypatch.setenv("UNCF_ANALYTICS_CONFIG", str(coverage))
    monkeypatch.setattr(settings, "UNCF_CHAT_ENABLED", True)
    app = create_app()
    model = ScriptedModel([call("retention", cohort="2022-23")], [finish()])
    app.dependency_overrides[get_chat_client] = lambda: model
    with TestClient(app) as client:
        proposal = client.post(path, json={"prompt": "Retention in 2022-23?"})
        assert proposal.status_code == 200
        reply = client.post(
            path, json={"prompt": "confirmed", "confirmed": proposal.json()["proposals"]}
        )
        assert reply.status_code == 200
        direct = AnalyticsService(database, fixture_coverage()).analyze(
            {"analysis": "retention", "cohort": "2022-23"}
        )
        assert reply.json()["receipts"] == direct.model_dump(mode="json")["receipts"]
        for forbidden in ["/docs", "/api/v1/documents", "/api/v1/sandbox/pipeline/runs"]:
            assert client.get(forbidden).status_code == 404


def test_deployment_switch_and_missing_key(monkeypatch):
    """The deployment supports explicit rollback and explains missing provider configuration."""
    monkeypatch.setattr(settings, "UNCF_CHAT_ENABLED", False)
    with TestClient(create_app()) as client:
        assert client.post("/api/v1/chat", json={"prompt": "hello"}).status_code == 404
    monkeypatch.setattr(settings, "UNCF_CHAT_ENABLED", True)
    monkeypatch.setattr(settings, "OPENAI_API_KEY", None)
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", None)
    with TestClient(create_app()) as client:
        reply = client.post("/api/v1/chat", json={"prompt": "Retention?"})
        assert reply.status_code == 503
        assert "provider API key" in reply.json()["error"]["message"]


def test_vercel_entrypoint_imports_without_playground_startup():
    """Production import defaults to the bundled extract and never loads Sandbox or DB sessions."""
    root = Path(__file__).resolve().parents[3]
    environment = {
        key: os.environ[key] for key in ("PATH", "TMPDIR", "SYSTEMROOT") if key in os.environ
    }
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import chat_app,sys,json; from app.core.config import settings; "
            "print(json.dumps({'database':settings.DATABASE_URL, "
            "'enabled':settings.UNCF_CHAT_ENABLED, 'environment':settings.APP_ENV, "
            "'sandbox': 'app.sandbox.router' in sys.modules, "
            "'sessions': 'app.db.session' in sys.modules, "
            "'routes':list(chat_app.app.openapi()['paths'])}))",
        ],
        cwd=root,
        env=environment,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    state = json.loads(result.stdout.strip().splitlines()[-1])
    assert state["environment"] == "production"
    assert state["enabled"]
    assert state["database"] == f"sqlite:///{root / 'normalized-data-model/output/pdp.sqlite'}"
    assert not state["sandbox"] and not state["sessions"]
    assert set(state["routes"]) == {"/api/v1/chat"}
