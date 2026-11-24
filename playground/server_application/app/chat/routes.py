"""Provider-enabled v2 chat transport over the shared deterministic plan service."""

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
from app.chat.v2 import ChatRequestV2, answer_v2

REQUEST_TIMEOUT_SECONDS = 75


class ChatRoute(APIRoute):
    """Map rejected transport and runtime configuration to safe typed responses."""

    def get_route_handler(self):
        """Avoid echoing untrusted bodies or internal configuration details."""
        original = super().get_route_handler()

        async def handler(request):
            """Project validation failures before any provider or calculation executes."""
            try:
                return await original(request)
            except RequestValidationError:
                return JSONResponse(
                    status_code=422, content=refusal("invalid_plan").model_dump(mode="json")
                )
            except HTTPException:
                return JSONResponse(
                    status_code=503, content=refusal("version_unavailable").model_dump(mode="json")
                )

        return handler


router = APIRouter(tags=["chat"], route_class=ChatRoute)


async def get_chat_client(payload: ChatRequestV2 | None = None):
    """Avoid provider access for clarification/confirmation and always close an opened SDK."""
    from app.core.config import settings

    if payload is not None and (payload.plan is not None or payload.confirmed is not None):
        yield None
        return
    try:
        _ = settings.chat_model
    except ValueError:
        yield None
        return
    if not settings.OPENROUTER_API_KEY:
        yield None
        return
    async with OpenRouter(api_key=settings.OPENROUTER_API_KEY) as sdk:
        yield OpenRouterClient(sdk)


@router.post("/chat", response_model=PlanResponse)
async def chat(
    payload: ChatRequestV2,
    client: Annotated[object, Depends(get_chat_client)],
    service: Annotated[AnalyticsService, Depends(get_service)],
):
    """Execute only explicitly confirmed canonical v2 scopes within the existing deadline."""
    from app.core.config import settings

    try:
        with execution_scope(REQUEST_TIMEOUT_SECONDS):
            return await asyncio.wait_for(
                answer_v2(
                    payload, client, settings.chat_model if client is not None else "", service
                ),
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
    except TimeoutError, CalculationCancelled:
        return refusal("timeout", payload.confirmed or payload.plan)
    except ProviderFailed:
        return refusal("provider_failed")
