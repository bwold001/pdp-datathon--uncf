"""Provider-enabled demonstration route, mounted only by the Playground runtime."""

import asyncio
from typing import Annotated

from analytics.execution import CalculationCancelled, execution_scope
from analytics.plan_contracts import PlanResponse
from analytics.plan_service import refusal
from analytics.service import AnalyticsService
from api.analyses import get_service
from fastapi import APIRouter, Depends, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from openrouter import OpenRouter

from app.chat.provider import OpenRouterClient, ProviderFailed
from app.chat.schemas import ChatRequest, ChatResponse
from app.chat.service import ChatFailed, answer
from app.chat.v2 import ChatRequestV2, answer_v2

REQUEST_TIMEOUT_SECONDS = 75


class ChatRoute(APIRoute):
    """Keep v2 invalid input errors typed and free of echoed unsafe values."""

    def get_route_handler(self):
        """Preserve v1 errors while mapping explicit v2 body validation failures."""
        original = super().get_route_handler()

        async def handler(request):
            """Project failed v2 transport validation into the shared safe response."""
            try:
                return await original(request)
            except RequestValidationError as error:
                if isinstance(error.body, dict) and error.body.get("protocol_version") == 2:
                    return JSONResponse(
                        status_code=422, content=refusal("invalid_plan").model_dump(mode="json")
                    )
                raise
            except HTTPException:
                body = await request.json()
                if isinstance(body, dict) and body.get("protocol_version") == 2:
                    return JSONResponse(
                        status_code=503,
                        content=refusal("version_unavailable").model_dump(mode="json"),
                    )
                raise

        return handler


router = APIRouter(tags=["chat"], route_class=ChatRoute)


async def get_chat_client(payload: ChatRequestV2 | ChatRequest | None = None):
    """Close the server-side OpenRouter SDK after every request, including failures."""
    from app.core.config import settings

    if isinstance(payload, ChatRequestV2) and (
        payload.plan is not None or payload.confirmed is not None
    ):
        yield None
        return

    try:
        _ = settings.chat_model
    except ValueError as error:
        if isinstance(payload, ChatRequestV2):
            yield None
            return
        raise HTTPException(503, str(error)) from error
    if not settings.OPENROUTER_API_KEY:
        yield None
        return
    async with OpenRouter(api_key=settings.OPENROUTER_API_KEY) as sdk:
        yield OpenRouterClient(sdk)


@router.post("/chat", response_model=ChatResponse | PlanResponse)
async def chat(
    payload: ChatRequestV2 | ChatRequest,
    client: Annotated[object, Depends(get_chat_client)],
    service: Annotated[AnalyticsService, Depends(get_service)],
):
    """Answer an approved question with structured calculation evidence."""
    from app.core.config import settings

    try:
        with execution_scope(REQUEST_TIMEOUT_SECONDS):
            return await asyncio.wait_for(
                (
                    answer_v2(
                        payload, client, settings.chat_model if client is not None else "", service
                    )
                    if isinstance(payload, ChatRequestV2)
                    else answer(payload, client, settings.chat_model, service)
                ),
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
    except (TimeoutError, CalculationCancelled) as error:
        if isinstance(payload, ChatRequestV2):
            return refusal("timeout", payload.confirmed or payload.plan)
        raise HTTPException(
            502, "The analysis request timed out. Try one supported question."
        ) from error
    except ValueError as error:
        raise HTTPException(422, str(error)) from error
    except ChatFailed as error:
        raise HTTPException(503 if client is None else 502, str(error)) from error
    except ProviderFailed as error:
        raise HTTPException(502, "The model provider failed. Please try again.") from error
