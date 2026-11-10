"""One provider boundary for the existing bounded analysis workflow."""

import json
from dataclasses import dataclass

import httpx
from openrouter import OpenRouter
from openrouter.errors import NoResponseError, OpenRouterError


class ProviderFailed(Exception):
    """A provider request failed without exposing its credentials or response body."""


@dataclass(frozen=True)
class ToolCall:
    """A provider-independent request for an approved application tool."""

    id: str
    name: str
    arguments: dict


@dataclass(frozen=True)
class ModelReply:
    """Keep tool requests and the assistant message needed for the next round."""

    calls: list[ToolCall]
    message: dict


class OpenRouterClient:
    """Normalize OpenRouter chat completions for the bounded analysis workflow."""

    def __init__(self, sdk: OpenRouter):
        """Use the request-scoped SDK owned and closed by the route dependency."""
        self.sdk = sdk

    async def complete(self, *, model: str, system: str, tools: list, messages: list):
        """Preserve assistant fields and tool IDs across asynchronous model rounds."""
        try:
            response = await self.sdk.chat.send_async(
                model=model,
                messages=[{"role": "system", "content": system}, *messages],
                tools=tools,
                stream=False,
                max_completion_tokens=1500,
                timeout_ms=45000,
                retries=None,
            )
            message = response.choices[0].message
            calls = []
            for call in message.tool_calls or []:
                arguments = json.loads(call.function.arguments)
                if not isinstance(arguments, dict):
                    raise ValueError("Tool arguments must be an object")
                if not call.id or not call.function.name:
                    raise ValueError("Tool calls need an ID and function name")
                calls.append(ToolCall(call.id, call.function.name, arguments))
            assistant = message.model_dump(mode="json", by_alias=True, exclude_unset=True)
            if not calls and not assistant.get("content") and not assistant.get("refusal"):
                raise ValueError("The model returned an empty message")
            return ModelReply(calls, assistant)
        except (
            OpenRouterError,
            NoResponseError,
            httpx.HTTPError,
            ValueError,
            TypeError,
            IndexError,
        ) as error:
            raise ProviderFailed("The model provider failed. Please try again.") from error
