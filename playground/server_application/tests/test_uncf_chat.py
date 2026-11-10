"""Real normalized database to Playground chat/API transport tests."""

import pytest
from uncf.analytics.routes import get_service
from uncf.analytics.service import AnalyticsService
from uncf.chat.routes import get_chat_client
from uncf.tests.analytics_fixtures import build_database, fixture_coverage
from uncf.tests.test_chat_tools import ScriptedModel, call, finish

from app.core.config import settings
from app.main import app


@pytest.fixture
def analytics(tmp_path):
    """Use a real hand-counted fixture for this route, not a mocked calculation."""
    service = AnalyticsService(build_database(tmp_path / "analytics.sqlite"), fixture_coverage())
    app.dependency_overrides[get_service] = lambda: service
    yield service
    app.dependency_overrides.pop(get_service, None)
    app.dependency_overrides.pop(get_chat_client, None)


def test_chat_matches_direct_api(client, analytics):
    """Both transports serialize the same verified calculation receipts."""
    model = ScriptedModel([call("retention", cohort="2022-23")], [finish()])
    app.dependency_overrides[get_chat_client] = lambda: model
    chat = client.post("/api/v1/uncf/chat", json={"prompt": "Retention for all majors in 2022-23?"})
    assert chat.json()["status"] == "confirmation" and not chat.json()["receipts"]
    chat = client.post(
        "/api/v1/uncf/chat",
        json={"prompt": "Confirmed complete scope", "confirmed": chat.json()["proposals"]},
    )
    direct = client.post(
        "/api/v1/uncf/analyses", json={"analysis": "retention", "cohort": "2022-23"}
    )
    assert chat.status_code == 200
    assert chat.json()["receipts"] == direct.json()["receipts"]
    assert model.requests[0]["model"] == settings.UNCF_CHAT_MODEL
    assert "99.9" not in chat.json()["message"]


def test_missing_key_and_invalid_body(client, analytics, monkeypatch):
    """Input validation happens before provider configuration errors."""
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", None)
    assert client.post("/api/v1/uncf/chat", json={"prompt": "Retention?"}).status_code == 503
    assert client.post("/api/v1/uncf/chat", json={"prompt": " "}).status_code == 422


def test_typed_clarification_without_provider(client, analytics):
    """A selected cohort resumes the pending request without model memory."""
    app.dependency_overrides[get_chat_client] = lambda: None
    response = client.post(
        "/api/v1/uncf/chat",
        json={
            "prompt": "2022-23",
            "pending": {"analysis": "retention"},
            "selection": {"field": "cohort", "value": "2022-23"},
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "confirmation"
    response = client.post(
        "/api/v1/uncf/chat", json={"prompt": "confirmed", "confirmed": response.json()["proposals"]}
    )
    assert response.json()["receipts"][0]["rows"][0]["rate"] == 0.5


def test_provider_failure(client, analytics):
    """Provider errors produce a useful response without fabricated results."""
    import anthropic
    import httpx

    class FailingModel:
        """A provider that fails on its first request."""

        async def create(self, **kwargs):
            """Simulate a connection failure from the provider SDK."""
            raise anthropic.APIConnectionError(
                request=httpx.Request("POST", "https://example.test")
            )

    model = FailingModel()
    model.messages = model
    app.dependency_overrides[get_chat_client] = lambda: model
    response = client.post("/api/v1/uncf/chat", json={"prompt": "Retention?"})
    assert response.status_code == 502
    assert "provider failed" in response.json()["error"]["message"]


def test_total_request_deadline_is_shorter_than_the_browser_timeout(client, analytics, monkeypatch):
    """A stalled provider returns a readable timeout before the browser deadline."""
    import asyncio

    from uncf.chat import routes

    class StalledModel:
        """A provider that does not finish within the route deadline."""

        async def create(self, **kwargs):
            """Wait long enough for route cancellation to interrupt the request."""
            from types import SimpleNamespace

            await asyncio.sleep(0.05)
            return SimpleNamespace(content=[])

    model = StalledModel()
    model.messages = model
    app.dependency_overrides[get_chat_client] = lambda: model
    monkeypatch.setattr(routes, "REQUEST_TIMEOUT_SECONDS", 0.01)
    response = client.post("/api/v1/uncf/chat", json={"prompt": "Retention?"})
    assert response.status_code == 502
    assert "timed out" in response.json()["error"]["message"]


def test_chat_switch_is_independent_of_sandbox(monkeypatch):
    """Disabling example endpoints does not remove the explicitly enabled chat."""
    from fastapi.testclient import TestClient

    from app.main import create_app

    monkeypatch.setattr(settings, "SANDBOX_ENABLED", False)
    monkeypatch.setattr(settings, "UNCF_CHAT_ENABLED", True)
    with TestClient(create_app()) as client:
        assert client.post("/api/v1/uncf/chat", json={"prompt": " "}).status_code == 422
        assert client.get("/api/v1/sandbox/measures/by-group").status_code == 404
    monkeypatch.setattr(settings, "UNCF_CHAT_ENABLED", False)
    with TestClient(create_app()) as client:
        assert client.post("/api/v1/uncf/chat", json={"prompt": "hello"}).status_code == 404
