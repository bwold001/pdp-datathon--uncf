"""Provider-enabled demonstration route, mounted only by the Playground runtime."""

import asyncio
from typing import Annotated

from analytics.execution import CalculationCancelled, execution_scope
from analytics.service import AnalyticsService
from api.analyses import get_service
from fastapi import APIRouter, Depends, HTTPException
from openrouter import OpenRouter

from app.chat.provider import OpenRouterClient, ProviderFailed
from app.chat.schemas import ChatRequest, ChatResponse
from app.chat.service import ChatFailed, answer

REQUEST_TIMEOUT_SECONDS = 75

router = APIRouter(tags=["chat"])


async def get_chat_client():
    """Close the server-side OpenRouter SDK after every request, including failures."""
    from app.core.config import settings

    try:
        _ = settings.chat_model
    except ValueError as error:
        raise HTTPException(503, str(error)) from error
    if not settings.OPENROUTER_API_KEY:
        yield None
        return
    async with OpenRouter(api_key=settings.OPENROUTER_API_KEY) as sdk:
        yield OpenRouterClient(sdk)


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
                answer(payload, client, settings.chat_model, service),
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
    except ProviderFailed as error:
        raise HTTPException(502, "The model provider failed. Please try again.") from error
