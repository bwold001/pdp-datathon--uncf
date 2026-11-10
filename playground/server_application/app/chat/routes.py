"""Provider-enabled demonstration route, mounted only by the Playground runtime."""

import asyncio
from functools import cache
from typing import Annotated

import anthropic
from analytics.execution import CalculationCancelled, execution_scope
from analytics.service import AnalyticsService
from api.analyses import get_service
from fastapi import APIRouter, Depends, HTTPException

from app.chat.schemas import ChatRequest, ChatResponse
from app.chat.service import ChatFailed, answer

REQUEST_TIMEOUT_SECONDS = 75

router = APIRouter(tags=["chat"])


@cache
def provider_client(key: str):
    """Reuse a server-side provider client with an explicit request timeout."""
    return anthropic.AsyncAnthropic(api_key=key, timeout=45.0, max_retries=0)


def get_chat_client():
    """Resolve the existing Playground credential without exposing it to the browser."""
    from app.core.config import settings

    return provider_client(settings.ANTHROPIC_API_KEY) if settings.ANTHROPIC_API_KEY else None


@router.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    client: Annotated[object, Depends(get_chat_client)],
    service: Annotated[AnalyticsService, Depends(get_service)],
):
    """Answer an approved question with structured calculation evidence."""
    from app.core.config import settings

    try:
        with execution_scope(REQUEST_TIMEOUT_SECONDS):
            return await asyncio.wait_for(
                answer(payload, client, settings.UNCF_CHAT_MODEL, service),
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
    except (TimeoutError, CalculationCancelled) as error:
        raise HTTPException(
            502, "The analysis request timed out. Try one supported question."
        ) from error
    except ValueError as error:
        raise HTTPException(422, str(error)) from error
    except ChatFailed as error:
        raise HTTPException(503 if client is None else 502, str(error)) from error
    except anthropic.AnthropicError as error:
        raise HTTPException(502, "The model provider failed. Please try again.") from error
