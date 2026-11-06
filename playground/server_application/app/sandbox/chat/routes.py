"""/sandbox/chat: ask a question; an LLM answers with the metadata-advisor skill and MCP tools."""

from functools import cache
from typing import Annotated

import anthropic
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import settings

from . import llm
from .schemas import SuggestRequest, SuggestResponse

router = APIRouter(prefix="/sandbox/chat", tags=["sandbox: chat"])


@cache
def _client(api_key: str) -> anthropic.AsyncAnthropic:
    """One Anthropic client per key, reused across requests."""
    return anthropic.AsyncAnthropic(api_key=api_key)


def get_chat_client() -> llm.ChatClient | None:
    """The Anthropic client, or None when no key is configured."""
    return _client(settings.ANTHROPIC_API_KEY) if settings.ANTHROPIC_API_KEY else None


# None instead of raising here: the 503 comes after FastAPI has validated the body.
ChatClientDep = Annotated[llm.ChatClient | None, Depends(get_chat_client)]


@router.post(
    "/suggest",
    responses={
        502: {"description": "The model provider failed or the assistant didn't finish"},
        503: {"description": "No ANTHROPIC_API_KEY is configured"},
    },
)
async def suggest(payload: SuggestRequest, client: ChatClientDep) -> SuggestResponse:
    """Answer one staff question, guided by the metadata-advisor skill and the definitions."""
    if client is None:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Sandbox chat needs ANTHROPIC_API_KEY. Set it in .env.development.local.",
        )
    try:
        return await llm.answer(client, settings.SANDBOX_CHAT_MODEL, payload.prompt)
    except anthropic.AnthropicError as exc:
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY, f"The model provider failed: {type(exc).__name__}."
        ) from None
    except llm.ChatFailed as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(exc)) from None
