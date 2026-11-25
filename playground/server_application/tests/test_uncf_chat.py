"""V2-only transport rejects obsolete callers and keeps provider failures readable."""

import asyncio

import pytest
from analytics.coverage import Coverage
from analytics.service import AnalyticsService
from analytics.tests.test_defined_operations import defined_data as defined_data  # noqa: F401
from api.analyses import get_service

from app.chat.routes import get_chat_client
from app.core.config import settings
from app.main import app


@pytest.fixture
def analytics(defined_data):
    """Bind chat to one known synthetic snapshot without mutating a developer database."""
    app.dependency_overrides[get_service] = lambda: AnalyticsService(defined_data, Coverage())
    yield
    app.dependency_overrides.pop(get_service, None)
    app.dependency_overrides.pop(get_chat_client, None)


def test_missing_key_and_old_body(client, analytics, monkeypatch):
    """Missing credentials never fabricate evidence; obsolete v1 bodies fail validation."""
    monkeypatch.setattr(settings, "OPENROUTER_API_KEY", None)
    response = client.post(
        "/api/v1/uncf/chat", json={"protocol_version": 2, "prompt": "Retention?"}
    )
    assert response.status_code == 200
    assert response.json()["issues"][0]["code"] == "provider_failed"
    assert "credentials" in response.json()["issues"][0]["message"]
    obsolete = client.post("/api/v1/uncf/chat", json={"prompt": "Retention?"})
    assert obsolete.status_code == 422 and obsolete.json()["issues"][0]["code"] == "invalid_plan"


def test_provider_failure_and_deadline(client, analytics, monkeypatch):
    """Failures and cancellation use safe v2 errors before the browser deadline."""
    from app.chat import routes
    from app.chat.provider import ProviderFailed

    class Failed:
        """Simulate a provider error that includes an unsafe detail."""

        async def complete(self, **kwargs):
            """Fail before returning any proposed calculation."""
            raise ProviderFailed("private-provider-detail")

    app.dependency_overrides[get_chat_client] = lambda: Failed()
    payload = {"protocol_version": 2, "prompt": "School retention?"}
    response = client.post("/api/v1/uncf/chat", json=payload)
    assert response.json()["issues"][0]["code"] == "provider_failed"
    assert "private-provider-detail" not in response.text

    class Stalled:
        """Wait past the application request budget."""

        async def complete(self, **kwargs):
            """Allow cancellation to interrupt an in-flight provider call."""
            await asyncio.sleep(0.1)

    app.dependency_overrides[get_chat_client] = lambda: Stalled()
    monkeypatch.setattr(routes, "REQUEST_TIMEOUT_SECONDS", 0.01)
    response = client.post("/api/v1/uncf/chat", json=payload)
    assert response.json()["issues"][0]["code"] == "timeout"
    assert not response.json()["receipts"]
