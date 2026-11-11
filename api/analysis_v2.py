"""Provider-free v2 HTTP adapters; validation, calculation and disclosure remain in analytics owners."""

import math
import os
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

from analytics.contracts_v2 import ExecutablePlan, ProposedPlan
from analytics.execution import CalculationCancelled, execution_scope, run_sync
from analytics.plan_contracts import CatalogResponse, PlanResponse
from analytics.plan_service import PlanService, refusal
from analytics.provenance import ReplaySpec
from api.analyses import get_service


def get_runtime_factory():
    """Return a source factory so coverage failures can be mapped inside the v2 boundary."""
    return get_service


def get_timeout():
    """Read a bounded server-only query budget without accepting request-level overrides."""
    try:
        value = float(os.environ.get("UNCF_ANALYSIS_V2_TIMEOUT_SECONDS", "10"))
        if not math.isfinite(value) or not 0 < value <= 60:
            raise ValueError("invalid budget")
        return value
    except ValueError as error:
        raise HTTPException(
            503, "Analysis execution configuration is unavailable."
        ) from error


def render(result):
    """Choose transport status without changing typed result or partial-execution semantics."""
    if isinstance(result, CatalogResponse) or result.status != "error":
        return result
    code = result.issues[0].code if result.issues else "data_unavailable"
    status = {
        "timeout": 504,
        "data_unavailable": 503,
        "version_unavailable": 409,
        "snapshot_unavailable": 409,
        "stale_plan": 409,
    }.get(code, 422)
    return JSONResponse(status_code=status, content=result.model_dump(mode="json"))


class AnalysisRoute(APIRoute):
    """Keep v2 structural/configuration errors typed without echoing raw request or driver details."""

    def get_route_handler(self):
        """Wrap FastAPI body validation only for these deterministic v2 endpoints."""
        original = super().get_route_handler()

        async def handler(request):
            """Map invalid HTTP input to bounded application-authored issues."""
            try:
                return await original(request)
            except RequestValidationError as error:
                code = (
                    "limit_exceeded"
                    if any(e["type"] == "too_long" for e in error.errors())
                    else "invalid_plan"
                )
                return JSONResponse(
                    status_code=422, content=refusal(code).model_dump(mode="json")
                )
            except HTTPException:
                return JSONResponse(
                    status_code=503,
                    content=refusal("version_unavailable").model_dump(mode="json"),
                )

        return handler


router = APIRouter(
    prefix="/api/v1/uncf/analysis-v2",
    tags=["uncf: analysis v2"],
    route_class=AnalysisRoute,
)


async def invoke(method, factory, seconds, payload=None):
    """Run the whole synchronous metadata/execution owner on one worker and await cleanup."""
    try:
        service = PlanService(factory())
        with execution_scope(seconds):
            if method == "catalog":
                result = await run_sync(service.catalog)
            elif method == "validate":
                result = await run_sync(service.validate, payload)
            else:
                replay = payload if isinstance(payload, ReplaySpec) else None
                plan = replay.plan if replay is not None else payload
                result = await run_sync(
                    service.execute_plan, plan, replay, check_completion=False
                )
        return render(result)
    except CalculationCancelled:
        plan = payload.plan if isinstance(payload, ReplaySpec) else payload
        return render(refusal("timeout", plan))
    except (HTTPException, OSError, ValueError):
        return render(refusal("version_unavailable"))


@router.get("/catalog", response_model=CatalogResponse | PlanResponse)
async def catalog(factory=Depends(get_runtime_factory), seconds=Depends(get_timeout)):
    """Return current source stamps, bounded choices and schema-based capability availability."""
    return await invoke("catalog", factory, seconds)


@router.post("/validate", response_model=PlanResponse)
async def validate(
    plan: Annotated[ProposedPlan | ExecutablePlan, Body(discriminator="kind")],
    factory=Depends(get_runtime_factory),
    seconds=Depends(get_timeout),
):
    """Validate a whole explicit/proposed plan and return clarification or canonical confirmation."""
    return await invoke("validate", factory, seconds, plan)


@router.post("/execute", response_model=PlanResponse)
async def execute(
    plan: ExecutablePlan | ReplaySpec,
    factory=Depends(get_runtime_factory),
    seconds=Depends(get_timeout),
):
    """Execute only a fully resolved plan, optionally bound to exported exact replay versions."""
    return await invoke("execute", factory, seconds, plan)
