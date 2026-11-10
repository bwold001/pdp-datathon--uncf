"""Exercise the LiteLLM boundary with SDK responses and no live provider credentials."""

import asyncio
import json

import litellm
import pytest
from analytics.service import AnalyticsService
from analytics.tests.analytics_fixtures import build_database, fixture_coverage

from app.chat.provider import LiteLLMClient, ProviderFailed
from app.chat.routes import get_chat_client
from app.chat.schemas import ChatRequest
from app.chat.service import answer
from app.core.config import settings


def sdk_reply(name=None, arguments=None):
    """Build an actual LiteLLM response, including its typed tool-call objects."""
    message = {"role": "assistant", "content": "Unsupported model prose: 99.9%"}
    if name:
        message["tool_calls"] = [
            {
                "id": "call_1",
                "type": "function",
                "function": {"name": name, "arguments": arguments},
            }
        ]
    return litellm.ModelResponse(choices=[{"message": message}])


@pytest.mark.parametrize("model", ["openai/gpt-4.1", "anthropic/claude-sonnet-5-5"])
def test_provider_switch_preserves_confirmed_receipts(tmp_path, monkeypatch, model):
    """Both model configurations use the same tools and real deterministic calculation."""
    requests = []
    replies = [
        sdk_reply("run_analysis", json.dumps({"analysis": "retention", "cohort": "2022-23"})),
        sdk_reply(),
    ]

    async def completion(**kwargs):
        """Capture requests at the SDK boundary without contacting a provider."""
        requests.append(kwargs)
        return replies.pop(0)

    monkeypatch.setattr(litellm, "acompletion", completion)
    service = AnalyticsService(build_database(tmp_path / "data.sqlite"), fixture_coverage())
    reply = asyncio.run(
        answer(
            ChatRequest(prompt="Retention in 2022-23?"),
            LiteLLMClient("test-secret"),
            model,
            service,
        )
    )
    assert reply.status == "confirmation" and not reply.receipts
    confirmed = asyncio.run(
        answer(ChatRequest(prompt="confirmed", confirmed=reply.proposals), None, model, service)
    )
    assert (
        confirmed.receipts
        == service.analyze({"analysis": "retention", "cohort": "2022-23"}).receipts
    )
    assert "99.9" not in confirmed.message
    assert requests[0]["model"] == model
    assert requests[0]["timeout"] == 45
    assert requests[0]["num_retries"] == 0
    assert requests[0]["messages"][0]["role"] == "system"
    assert {tool["function"]["name"] for tool in requests[0]["tools"]} == {
        "get_analysis_catalog",
        "get_analysis_definition",
        "run_analysis",
    }
    assert requests[1]["messages"][-1]["role"] == "tool"
    assert requests[1]["messages"][-1]["tool_call_id"] == "call_1"
    assert "test-secret" not in confirmed.model_dump_json()


@pytest.mark.parametrize("arguments", ["not-json", "[]", "null"])
def test_malformed_provider_arguments_are_not_user_errors(monkeypatch, arguments):
    """Malformed model output becomes a provider failure, never a calculation."""

    async def completion(**kwargs):
        """Return invalid arguments in an otherwise valid SDK response."""
        return sdk_reply("run_analysis", arguments)

    monkeypatch.setattr(litellm, "acompletion", completion)
    with pytest.raises(ProviderFailed):
        asyncio.run(
            LiteLLMClient("test-secret").complete(
                model="openai/gpt-4.1", system="rules", tools=[], messages=[]
            )
        )


def test_provider_exception_is_sanitized(monkeypatch):
    """Provider error bodies and credential values never reach the route error message."""

    async def completion(**kwargs):
        """Simulate a provider including a credential in its exception text."""
        raise litellm.AuthenticationError("test-secret", llm_provider="openai", model="test")

    monkeypatch.setattr(litellm, "acompletion", completion)
    with pytest.raises(ProviderFailed) as failure:
        asyncio.run(
            LiteLLMClient("test-secret").complete(
                model="openai/gpt-4.1", system="rules", tools=[], messages=[]
            )
        )
    assert "test-secret" not in str(failure.value)


@pytest.mark.parametrize(
    "provider,key_name", [("openai", "OPENAI_API_KEY"), ("anthropic", "ANTHROPIC_API_KEY")]
)
def test_selects_only_the_configured_provider_key(monkeypatch, provider, key_name):
    """A key for the other provider cannot silently enable the selected provider."""
    monkeypatch.setattr(settings, "UNCF_CHAT_MODEL", f"{provider}/test-model")
    monkeypatch.setattr(settings, "OPENAI_API_KEY", None)
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", None)
    assert get_chat_client() is None
    monkeypatch.setattr(settings, key_name, "test-secret")
    assert get_chat_client().api_key == "test-secret"


def test_legacy_claude_model_setting_is_preserved(monkeypatch):
    """Existing local configuration acquires a provider prefix automatically."""
    monkeypatch.setattr(settings, "UNCF_CHAT_MODEL", "claude-sonnet-5-5")
    assert settings.chat_model == "anthropic/claude-sonnet-5-5"
