"""One provider boundary for the existing bounded analysis workflow."""

import json
from dataclasses import dataclass

import litellm
from openai import OpenAIError


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


class LiteLLMClient:
    """Call supported providers through LiteLLM's asynchronous chat interface."""

    def __init__(self, api_key: str):
        """Keep the selected provider's credential on this server-side client."""
        self.api_key = api_key

    async def complete(self, *, model: str, system: str, tools: list, messages: list):
        """Normalize tool calls while preserving the application's tool-loop limits."""
        try:
            response = await litellm.acompletion(
                model=model,
                api_key=self.api_key,
                messages=[{"role": "system", "content": system}, *messages],
                tools=tools,
                max_tokens=1500,
                timeout=45,
                num_retries=0,
            )
            message = response.choices[0].message
            calls = []
            for call in message.tool_calls or []:
                arguments = json.loads(call.function.arguments)
                if not isinstance(arguments, dict):
                    raise ValueError("Tool arguments must be an object")
                calls.append(ToolCall(call.id, call.function.name, arguments))
            return ModelReply(calls, message.model_dump(exclude_none=True))
        except (
            OpenAIError,
            litellm.exceptions.OpenAIError,
            ValueError,
            TypeError,
            IndexError,
        ) as error:
            raise ProviderFailed("The model provider failed. Please try again.") from error
