"""Results API (#5): the Explorer, CSV export, insight card and chat all get their numbers here.

Run it with `python -m uncf` (port 8001), or mount `router` in the Playground server with one line:
`app.include_router(uncf.api.router)`.

Assumptions (no issue decides them; change them in one place):
- Numbers are calculated per request by the measures package and cached; nothing is saved.
- group_by is optional and takes up to two dimensions. Order doesn't matter: pell,race equals race,pell.
- The everyone row always comes first ("group": {}).
- provisional is true for retention and persistence in 2024-25 (uncf/results.py, PROVISIONAL_COHORTS).
- A gateway measure with no answers for a class is not_reported: the college doesn't report the requirement.
- Port 8001; CORS allows http://localhost:3000 (override with UNCF_CORS_ORIGINS, comma separated).
- Errors: 422 for a value outside the lists (FastAPI's body) or a bad group_by (ours), 503 data_missing.
  Our bodies are {"error": {"code", "message"}}.
"""
from __future__ import annotations

import os
from typing import Annotated, get_args

from fastapi import APIRouter, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from uncf import results
from uncf.analytics.routes import router as analytics_router
from uncf.definitions import definition_for
from uncf.schemas import (
    DIMENSION_LABELS,
    MAX_GROUP_BY,
    SOURCE,
    Cohort,
    Dimension,
    ErrorResponse,
    HealthResponse,
    Measure,
    MeasureDefinition,
    Option,
    OptionsResponse,
    ResultsMeta,
    ResultsResponse,
)

PREFIX = "/api/v1/uncf"
DEFAULT_PORT = 8001
DEFAULT_CORS_ORIGINS = "http://localhost:3000"

router = APIRouter(prefix=PREFIX)


def _error(status_code: int, code: str, message: str) -> JSONResponse:
    """One error body shape for every error this API raises itself."""
    body = ErrorResponse.model_validate({"error": {"code": code, "message": message}})
    return JSONResponse(status_code=status_code, content=body.model_dump())


@router.get(
    "/results",
    response_model=ResultsResponse,
    responses={422: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
)
def get_results(
    measure: Measure,
    cohort: Cohort,
    group_by: Annotated[list[Dimension] | None, Query()] = None,
):
    """One measure for one class, for everyone and each group, with its definition."""
    dimensions = group_by or []
    if len(dimensions) > MAX_GROUP_BY:
        return _error(422, "invalid_group_by", f"Pass group_by at most {MAX_GROUP_BY} times.")
    if len(set(dimensions)) != len(dimensions):
        return _error(422, "invalid_group_by", "Each group_by dimension can be used once.")

    try:
        rows = results.get_results(measure, cohort, dimensions)
        loaded_at = results.loaded_at()
    except results.DataMissing as error:
        return _error(503, "data_missing", str(error))

    meta = ResultsMeta(
        measure=measure,
        cohort=cohort,
        group_by=dimensions,
        definition=MeasureDefinition(**definition_for(measure)),
        source=SOURCE,
        loaded_at=loaded_at,
        provisional=results.is_provisional(measure, cohort),
    )
    return ResultsResponse(meta=meta, rows=rows)


@router.get("/options", response_model=OptionsResponse)
def get_options() -> OptionsResponse:
    """The measures, classes and groupings a client can ask for."""
    return OptionsResponse(
        measures=[Option(value=m, label=definition_for(m)["name"]) for m in get_args(Measure)],
        cohorts=list(get_args(Cohort)),
        dimensions=[Option(value=d, label=DIMENSION_LABELS[d]) for d in get_args(Dimension)],
        max_group_by=MAX_GROUP_BY,
    )


@router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    """Whether the normalized data is loaded, and when."""
    try:
        return HealthResponse(data_available=True, loaded_at=results.loaded_at())
    except results.DataMissing:
        return HealthResponse(data_available=False, loaded_at=None)


def create_app() -> FastAPI:
    """The standalone app: the router plus CORS for the Playground client."""
    app = FastAPI(title="UNCF Results API", version="1")
    origins = os.environ.get("UNCF_CORS_ORIGINS", DEFAULT_CORS_ORIGINS).split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin.strip() for origin in origins if origin.strip()],
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )
    @app.exception_handler(HTTPException)
    async def analysis_error(_request, error: HTTPException):
        """Keep additive analytics errors in the existing standalone error envelope."""
        code = "invalid_analysis" if error.status_code == 422 else "analytics_unavailable"
        return _error(error.status_code, code, str(error.detail))

    app.include_router(router)
    app.include_router(analytics_router)
    return app


app = create_app()
