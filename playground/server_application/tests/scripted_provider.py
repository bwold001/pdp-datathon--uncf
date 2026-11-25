"""Reusable finite provider scripts for deterministic chat tests."""

import json

from app.chat.provider import ModelReply, ToolCall


class ScriptedModel:
    """Return SDK-shaped responses without contacting a provider."""

    def __init__(self, *responses):
        """Record calls and consume an explicitly bounded script."""
        self.responses = list(responses)
        self.requests = []

    async def complete(self, **request):
        """Preserve assistant tool messages for transport and state assertions."""
        self.requests.append(request)
        blocks = self.responses.pop(0)
        calls = [block for block in blocks if isinstance(block, ToolCall)]
        message = {"role": "assistant", "content": None}
        if calls:
            message["tool_calls"] = [
                {
                    "id": call.id,
                    "type": "function",
                    "function": {"name": call.name, "arguments": json.dumps(call.arguments)},
                }
                for call in calls
            ]
        return ModelReply(calls, message)
