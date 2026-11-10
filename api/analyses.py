"""Additive deterministic routes usable without an external model provider."""

import os
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from yaml import YAMLError

from api import results
from analytics.schemas import AnalysisRequest, AnalysisResponse
from analytics.service import AnalyticsService
from analytics.coverage import DEFAULT_CONFIG, load_coverage

router = APIRouter(prefix="/api/v1/uncf", tags=["uncf: analytics"])


def get_service() -> AnalyticsService:
    """Read the shared source path and optional server-only coverage configuration."""
    try:
        coverage = load_coverage(
            Path(os.environ.get("UNCF_ANALYTICS_CONFIG", DEFAULT_CONFIG))
        )
    except (OSError, ValueError, YAMLError) as error:
        raise HTTPException(
            503, "Analytics coverage configuration is missing or invalid."
        ) from error
    return AnalyticsService(results.data_path(), coverage)


@router.get("/analyses/catalog")
def catalog(service: Annotated[AnalyticsService, Depends(get_service)]) -> dict:
    """List definitions, choices and currently declared data coverage."""
    return service.catalog()


@router.post("/analyses", response_model=AnalysisResponse)
def analyze(
    request: AnalysisRequest, service: Annotated[AnalyticsService, Depends(get_service)]
):
    """Calculate an approved analysis or request a material clarification."""
    try:
        return service.analyze(request)
    except ValueError as error:
        raise HTTPException(422, str(error)) from error
