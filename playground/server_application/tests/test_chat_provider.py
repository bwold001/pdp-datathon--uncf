"""Exercise the official OpenRouter SDK over mocked HTTP, without live credentials."""

import asyncio
import json

import httpx
import pytest
from analytics.coverage import Coverage
from analytics.plan_service import PlanService
from analytics.service import AnalyticsService
from analytics.tests.test_defined_operations import defined_data as defined_data  # noqa: F401
from openrouter import OpenRouter
from openrouter.components import ChatResult

from app.chat import routes
from app.chat.provider import OpenRouterClient, ProviderFailed
from app.chat.v2 import ChatRequestV2, answer_v2
from app.core.config import settings


def sdk_reply(name=None, arguments=None, **fields):
    """Build a typed SDK response with assistant fields needed in later rounds."""
    message = {"role": "assistant", "content": "Unsupported model prose: 99.9%", **fields}
    if name:
        message["tool_calls"] = [
            {
                "id": "call_1",
                "type": "function",
                "function": {"name": name, "arguments": arguments},
            }
        ]
    return ChatResult.model_validate(
        {
            "id": "chat-test",
            "object": "chat.completion",
            "created": 1,
            "model": "test/model",
            "system_fingerprint": None,
            "choices": [
                {"index": 0, "finish_reason": "tool_calls" if name else "stop", "message": message}
            ],
        }
    ).model_dump(mode="json", by_alias=True)


async def complete_over_http(handle):
    """Run one real SDK completion over a controlled HTTP transport."""
    async with (
        httpx.AsyncClient(transport=httpx.MockTransport(handle)) as http,
        OpenRouter(api_key="test-secret", async_client=http) as sdk,
    ):
        return await OpenRouterClient(sdk).complete(
            model="openai/gpt-4.1", system="rules", tools=[], messages=[]
        )


@pytest.mark.parametrize("model", ["openai/gpt-4.1", "anthropic/claude-sonnet-5.5"])
def test_provider_switch_preserves_confirmed_receipts(defined_data, model):
    """Model switching preserves tool messages, confirmation, and deterministic receipts."""
    requests = []
    first = sdk_reply(
        "search_catalog",
        json.dumps({"query": "retention"}),
        content=None,
        reasoning_details=[
            {
                "type": "reasoning.encrypted",
                "data": "opaque-signature",
                "format": "anthropic-claude-v1",
            }
        ],
    )
    service = AnalyticsService(defined_data, Coverage())
    catalog = PlanService(service).catalog()
    plan = {
        "kind": "proposed",
        "catalog_version": catalog.catalog_version,
        "snapshot_ref": catalog.snapshot_ref,
        "steps": [
            {
                "kind": "defined_measure",
                "operation_id": "retention.rate",
                "step_id": "retention",
                "parameters": {"cohort": "2023-24", "retention_type": "school"},
            }
        ],
    }
    replies = [first, sdk_reply("propose_plan", json.dumps(plan))]

    def handle(request):
        """Capture the actual SDK wire request and return a typed response as JSON."""
        requests.append(json.loads(request.content))
        assert request.headers["authorization"] == "Bearer test-secret"
        assert request.extensions["timeout"]["read"] == 45
        return httpx.Response(200, json=replies.pop(0))

    async def propose():
        """Use one SDK and transport for every round of this request."""
        async with (
            httpx.AsyncClient(transport=httpx.MockTransport(handle)) as http,
            OpenRouter(api_key="test-secret", async_client=http) as sdk,
        ):
            return await answer_v2(
                ChatRequestV2(protocol_version=2, prompt="School retention in 2023-24?"),
                OpenRouterClient(sdk),
                model,
                service,
            )

    reply = asyncio.run(propose())
    assert reply.status == "confirmation" and not reply.receipts
    confirmed = asyncio.run(
        answer_v2(
            ChatRequestV2(protocol_version=2, prompt="confirmed", confirmed=reply.plan),
            None,
            model,
            service,
        )
    )
    assert confirmed.receipts[0].result.payload.numerator == 6
    assert confirmed.receipts[0].result.payload.denominator == 12
    assert "99.9" not in confirmed.message
    assert requests[0]["model"] == model
    assert requests[0]["max_completion_tokens"] == 1500
    assert requests[0]["stream"] is False
    assert requests[0]["messages"][0]["role"] == "system"
    assert {tool["function"]["name"] for tool in requests[0]["tools"]} == {
        "search_catalog",
        "operation_details",
        "propose_plan",
    }
    assert requests[1]["messages"][-2] == first["choices"][0]["message"]
    assert requests[1]["messages"][-1]["role"] == "tool"
    assert requests[1]["messages"][-1]["tool_call_id"] == "call_1"
    assert "test-secret" not in confirmed.model_dump_json()


@pytest.mark.parametrize("arguments", ["not-json", "[]", "null", '"text"', "42"])
def test_malformed_provider_arguments_are_not_user_errors(arguments):
    """Malformed tool arguments fail before dispatching any tool."""
    with pytest.raises(ProviderFailed):
        asyncio.run(
            complete_over_http(
                lambda request: httpx.Response(200, json=sdk_reply("run_analysis", arguments))
            )
        )


@pytest.mark.parametrize("status", [401, 402, 429, 500, 502, 503])
def test_provider_http_failure_is_sanitized_and_never_retried(status):
    """Even retryable status codes make one request and expose no provider body."""
    requests = []

    def handle(request):
        """Include a credential in an upstream error to verify safe translation."""
        requests.append(request)
        return httpx.Response(
            status,
            json={"error": {"message": "test-secret", "code": status}},
            headers={"Retry-After": "0"},
        )

    with pytest.raises(ProviderFailed) as failure:
        asyncio.run(complete_over_http(handle))
    assert len(requests) == 1
    assert "test-secret" not in str(failure.value)


@pytest.mark.parametrize("error", [httpx.ReadTimeout, httpx.ConnectError])
def test_transport_failure_is_sanitized_and_never_retried(error):
    """Network failures retain the single-attempt timing contract."""
    requests = []

    def handle(request):
        """Fail at the transport boundary rather than mocking the SDK method."""
        requests.append(request)
        raise error("test-secret", request=request)

    with pytest.raises(ProviderFailed) as failure:
        asyncio.run(complete_over_http(handle))
    assert len(requests) == 1
    assert "test-secret" not in str(failure.value)


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"choices": []},
        {"error": {"message": "test-secret", "code": 502}},
        {"choices": [{"message": None}]},
        sdk_reply(content=None),
        sdk_reply(content=""),
    ],
)
def test_empty_or_malformed_response_fails_safely(body):
    """HTTP success cannot turn an invalid or empty model reply into a calculation."""
    with pytest.raises(ProviderFailed):
        asyncio.run(complete_over_http(lambda request: httpx.Response(200, json=body)))


def test_invalid_json_response_fails_safely():
    """Malformed JSON from an upstream gateway is sanitized at the provider boundary."""
    with pytest.raises(ProviderFailed):
        asyncio.run(
            complete_over_http(
                lambda request: httpx.Response(
                    200,
                    content="not-json test-secret",
                    headers={"Content-Type": "application/json"},
                )
            )
        )


def test_cancellation_propagates():
    """The application deadline can cancel an in-flight SDK call."""

    async def handle(request):
        """Simulate cancellation during network I/O."""
        raise asyncio.CancelledError

    with pytest.raises(asyncio.CancelledError):
        asyncio.run(complete_over_http(handle))


@pytest.mark.parametrize("failure", [None, ProviderFailed, asyncio.CancelledError])
def test_request_dependency_closes_sdk(monkeypatch, failure):
    """Close the actual SDK HTTP client on success, failure, and cancellation."""
    sdk = OpenRouter(api_key="test-secret")
    http = sdk.sdk_configuration.async_client
    monkeypatch.setattr(settings, "OPENROUTER_API_KEY", "test-secret")
    monkeypatch.setattr(routes, "OpenRouter", lambda **kwargs: sdk)

    async def request():
        """Enter and unwind the dependency as FastAPI does around a request."""
        dependency = routes.get_chat_client()
        assert isinstance(await anext(dependency), OpenRouterClient)
        if failure:
            with pytest.raises(failure):
                await dependency.athrow(failure())
        else:
            await dependency.aclose()
        assert http.is_closed

    asyncio.run(request())


def test_only_openrouter_key_enables_chat(monkeypatch):
    """Legacy provider environment keys cannot silently enable OpenRouter calls."""
    monkeypatch.setattr(settings, "OPENROUTER_API_KEY", None)
    monkeypatch.setenv("OPENAI_API_KEY", "legacy-secret")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "legacy-secret")

    async def request():
        """Read the missing-key dependency and close the generator."""
        dependency = routes.get_chat_client()
        assert await anext(dependency) is None
        await dependency.aclose()

    asyncio.run(request())


@pytest.mark.parametrize("model", ["google/gemini-test", "openai/gpt-4.1"])
def test_canonical_model_is_not_rewritten(monkeypatch, model):
    """Model configuration is independent of legacy provider selection."""
    monkeypatch.setattr(settings, "UNCF_CHAT_MODEL", model)
    assert settings.chat_model == model


@pytest.mark.parametrize("model", ["claude-sonnet-5-5", "", "openai/"])
def test_legacy_or_incomplete_model_is_rejected(monkeypatch, model):
    """Invalid model names fail explicitly instead of guessing a catalog mapping."""
    monkeypatch.setattr(settings, "UNCF_CHAT_MODEL", model)
    with pytest.raises(ValueError, match="canonical OpenRouter"):
        _ = settings.chat_model
