"""The UNCF API: the Explorer pages and one measure by group, on one router under /api/v1/uncf.

Every number comes from the measures package (run_measure and measures/breakdowns/), so the pages, CSV export
and chat agree.

Every page route and /measures/{measure} take the same cohort bar: cohort, the eight filters (cohort_term,
enrollment_intensity, enrollment_type, pell, gender, race, ethnicity, age_band) with the measures' value names,
retention_type (school, the default, or federal), and format (json, the default, or csv).
e.g. /api/v1/uncf/gateway?cohort=2022-23&pell=Y&retention_type=federal&format=csv

Run it with `python -m api` (port 8001). The Playground server mounts `router` with one line.
Errors: 422 for a value the API doesn't offer, 404 for a hidden course, 503 when the data isn't loaded.
Our bodies are {"error": {"code", "message"}}.
"""
from __future__ import annotations

import csv
import io
import os
from functools import lru_cache
from typing import Annotated, get_args

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from api import data
from api.analyses import router as analytics_router
from api.measure_by_group import clear_cache as clear_measure_cache
from api.measure_by_group import is_provisional, measure_by_group
from gap_finder.gateway import add_gateway_gaps
from measures.definitions import all_definitions, definition_for
from api.filters import (
    DEFAULT_RETENTION_TYPE,
    FILTER_LABELS,
    CohortQuery,
    InvalidFilter,
    cohort_options,
)
from api.schemas import (
    MAX_GROUP_BY,
    Cohort,
    CreditMomentumResponse,
    DfwCourseResponse,
    DfwResponse,
    Dimension,
    ErrorResponse,
    GatewayResponse,
    HealthResponse,
    Measure,
    MeasureByGroupMeta,
    MeasureByGroupResponse,
    MeasureDefinition,
    Option,
    OptionsResponse,
    StudentPathsResponse,
)
from measures.breakdowns.credit_momentum import credit_momentum
from measures.breakdowns.dfw_courses import UnknownCourse, dfw_course, dfw_courses
from measures.breakdowns.gateway_courses import gateway_courses
from measures.breakdowns.student_paths import DEFAULT_TERMS, student_paths
from measures.models import GroupDimension

PREFIX = "/api/v1/uncf"
DEFAULT_PORT = 8001
DEFAULT_CORS_ORIGINS = "http://localhost:3000"
ERRORS = {404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}, 503: {"model": ErrorResponse}}
# The lists each page's CSV holds, one row per item, with a section column naming the list.
CSV_SECTIONS = {
    "student-paths": ("path", "groups"),
    "dfw": ("courses",),
    "dfw-course": ("terms", "delivery", "groups"),
    "gateway": ("courses", "pairs"),
    "credit-momentum": ("milestones", "terms", "tiers"),
}

# The router answers under /uncf; both apps mount it under /api/v1, so every path is PREFIX + route.
router = APIRouter(prefix="/uncf", tags=["UNCF"])
Filter = Annotated[str | None, Query()]


def error(status_code: int, code: str, message: str) -> JSONResponse:
    """The error body every route shares."""
    return JSONResponse(status_code=status_code, content={"error": {"code": code, "message": message}})


class Bar:
    """The cohort bar's query values, checked into a CohortQuery (or a 422), plus the answer's format."""

    def __init__(
        self,
        cohort: str = data.DEFAULT_COHORT,
        cohort_term: Filter = None,
        enrollment_intensity: Filter = None,
        enrollment_type: Filter = None,
        pell: Filter = None,
        gender: Filter = None,
        race: Filter = None,
        ethnicity: Filter = None,
        age_band: Filter = None,
        retention_type: str = DEFAULT_RETENTION_TYPE,
        format: str = "json",
    ) -> None:
        self.format = format
        self.problem: JSONResponse | None = None
        self.query: CohortQuery | None = None
        if format not in ("json", "csv"):
            self.problem = error(422, "invalid_filter", f"format has no value {format!r}. Use json or csv.")
            return
        filters = {
            "cohort_term": cohort_term,
            "enrollment_intensity": enrollment_intensity,
            "enrollment_type": enrollment_type,
            "pell": pell,
            "gender": gender,
            "race": race,
            "ethnicity": ethnicity,
            "age_band": age_band,
        }
        try:
            self.query = CohortQuery.of(cohort, retention_type, **filters)
        except InvalidFilter as invalid:
            self.problem = error(422, "invalid_filter", str(invalid))


def run_page(name: str, query: CohortQuery, *extra) -> dict:
    """Ask measures/breakdowns for one page, then add what every answer says about its question (meta)."""
    cohort, filters, retention, database = query.cohort, query.as_group(), query.retention_measure, data.data_path()
    if name == "student-paths":
        terms, group_by = extra
        body = student_paths(cohort, filters, retention, terms, GroupDimension(group_by) if group_by else None, database)
    elif name == "dfw":
        body = dfw_courses(cohort, filters, database)
    elif name == "dfw-course":
        (course,) = extra
        body = dfw_course(cohort, course, filters, database)
    elif name == "gateway":
        body = add_gateway_gaps(gateway_courses(cohort, filters, retention, database))
    else:
        body = credit_momentum(cohort, filters, retention, database)
    context = body.pop("context")
    return {"meta": {**query.meta(), **context, "loaded_at": data.loaded_at()}, **body}


@lru_cache(maxsize=256)
def cached(name: str, query: CohortQuery, stamp: float, *extra) -> dict:
    """A page's answer for one query (plus any extra arguments) and one version of the data file."""
    return run_page(name, query, *extra)


def answer(bar: Bar, name: str, *extra):
    """Run a page for a checked query as JSON or CSV. A bad value is a 422 and missing data is a 503."""
    if bar.problem is not None:
        return bar.problem
    try:
        body = cached(name, bar.query, data.data_stamp(), *extra)
    except data.DataMissing as missing:
        return error(503, "data_missing", str(missing))
    except ValueError as invalid:
        # A value the page doesn't take, such as terms=9 or group_by=housing.
        return error(422, "invalid_filter", str(invalid))
    if bar.format == "csv":
        rows = [{"section": section, **flatten(item)} for section in CSV_SECTIONS[name] for item in body.get(section) or []]
        return csv_response(rows, bar.query, f"uncf-{name}-{bar.query.cohort}.csv")
    return body


def flatten(item: dict, prefix: str = "") -> dict:
    """One CSV row from a nested answer: {"split": {"D": 3}} becomes {"split.D": 3}. Lists are left out."""
    row = {}
    for key, value in item.items():
        name = f"{prefix}{key}"
        if isinstance(value, dict):
            row.update(flatten(value, f"{name}."))
        elif isinstance(value, (list, tuple, set)):
            if all(not isinstance(part, (dict, list)) for part in value):
                row[name] = " + ".join(str(part) for part in value)
        else:
            row[name] = value
    return row


def csv_response(rows: list[dict], query: CohortQuery, filename: str) -> Response:
    """Rows as a CSV download. Each row also says which cohort, filters and retention type it is for."""
    context = {
        "cohort": query.cohort,
        "filters": "; ".join(f"{key}={value}" for key, value in query.filters) or "all students",
        "retention_type": query.retention_type,
    }
    rows = [{**context, **row} for row in rows]
    columns: list[str] = list(context)
    for row in rows:
        columns.extend(key for key in row if key not in columns)
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)
    return Response(buffer.getvalue(), media_type="text/csv", headers={"Content-Disposition": f'attachment; filename="{filename}"'})


# Shared --------------------------------------------------------------------------------------------------------


@router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    """Whether the normalized data is loaded, and when."""
    try:
        data.data_stamp()
        return HealthResponse(data_available=True, loaded_at=data.loaded_at())
    except data.DataMissing:
        return HealthResponse(data_available=False, loaded_at=None)


@router.get("/definitions")
def get_definitions():
    """Every plain-language definition (measures/definitions.py), so every page and the chat use the same words."""
    return {"definitions": all_definitions()}


@router.get("/cohort-options", responses=ERRORS)
def get_cohort_options(cohort: str = data.DEFAULT_COHORT):
    """How many students entered in each cohort year, and how many in the chosen cohort have each filter value."""
    try:
        return cohort_options(cohort)
    except InvalidFilter as invalid:
        return error(422, "invalid_filter", str(invalid))
    except data.DataMissing as missing:
        return error(503, "data_missing", str(missing))


# One measure by group ------------------------------------------------------------------------------------------

GroupByQuery = Annotated[list[Dimension] | None, Query()]


@router.get("/measures/{measure}", response_model=MeasureByGroupResponse, responses=ERRORS)
def get_measure(measure: Measure, cohort: Cohort, bar: Annotated[Bar, Depends()], group_by: GroupByQuery = None):
    """One measure for one cohort, its filters and retention type: the everyone row, then one row per group."""
    return measure_answer(measure, cohort, bar, group_by or [])


@router.get("/results", response_model=MeasureByGroupResponse, responses=ERRORS, include_in_schema=False)
def get_results(measure: Measure, cohort: Cohort, bar: Annotated[Bar, Depends()], group_by: GroupByQuery = None):
    """The old URL for /measures/{measure} (measure as a query value), kept for the deployed API's callers."""
    return measure_answer(measure, cohort, bar, group_by or [])


def measure_answer(measure: str, cohort: str, bar: Bar, dimensions: list[str]):
    """One measure by group as JSON or CSV, with its definition. A bad group_by is a 422, missing data a 503."""
    if len(dimensions) > MAX_GROUP_BY:
        return error(422, "invalid_group_by", f"Pass group_by at most {MAX_GROUP_BY} times.")
    if len(set(dimensions)) != len(dimensions):
        return error(422, "invalid_group_by", "Each group_by dimension can be used once.")
    if bar.problem is not None:
        return bar.problem
    try:
        rows, loaded_at = measure_by_group(measure, bar.query, dimensions)
    except data.DataMissing as missing:
        return error(503, "data_missing", str(missing))

    if bar.format == "csv":
        table = [{**{d: row.group.get(d, "All") for d in dimensions}, **flatten(row.model_dump(exclude={"group"}))} for row in rows]
        return csv_response(table, bar.query, f"uncf-{measure}-{cohort}.csv")
    federal = measure == "retention" and bar.query.retention_type == "federal"
    meta = MeasureByGroupMeta(
        measure=measure,
        cohort=cohort,
        group_by=dimensions,
        filters=bar.query.as_dict(),
        retention_type=bar.query.retention_type,
        definition=MeasureDefinition(**definition_for("federal_retention" if federal else measure)),
        source=data.SOURCE,
        loaded_at=loaded_at,
        provisional=is_provisional(measure, cohort),
    )
    return MeasureByGroupResponse(meta=meta, rows=rows)


@router.get("/options", response_model=OptionsResponse)
def get_options() -> OptionsResponse:
    """The measures, classes, groupings and filters /measures/{measure} takes."""
    return OptionsResponse(
        measures=[Option(value=m, label=definition_for(m)["name"]) for m in get_args(Measure)],
        cohorts=list(get_args(Cohort)),
        dimensions=[Option(value=d, label=FILTER_LABELS[d]) for d in get_args(Dimension)],
        max_group_by=MAX_GROUP_BY,
    )


# Explorer pages ------------------------------------------------------------------------------------------------


@router.get("/student-paths", response_model=StudentPathsResponse, responses=ERRORS)
def get_student_paths(bar: Annotated[Bar, Depends()], terms: int = DEFAULT_TERMS, group_by: str | None = None):
    """Student paths: each entering student's status term by term, moves, transfers and retention."""
    return answer(bar, "student-paths", terms, group_by)


@router.get("/dfw", response_model=DfwResponse, responses=ERRORS)
def get_dfw(bar: Annotated[Bar, Depends()]):
    """DFW list: everyone's DFW rate with D, F and W apart, then each course with 10 or more students."""
    return answer(bar, "dfw")


@router.get("/dfw/course", response_model=DfwCourseResponse, responses=ERRORS)
def get_dfw_course(course: str, bar: Annotated[Bar, Depends()]):
    """One DFW course: its terms, delivery methods and groups, each next to everyone else in the course."""
    try:
        return answer(bar, "dfw-course", course)
    except UnknownCourse as unknown:
        return error(404, "unknown_course", str(unknown))


@router.get("/gateway", response_model=GatewayResponse, responses=ERRORS)
def get_gateway(bar: Annotated[Bar, Depends()]):
    """Gateway courses: each course's year 1 path (first try, in the end), retention, group gap and course pairs."""
    return answer(bar, "gateway")


@router.get("/credit-momentum", response_model=CreditMomentumResponse, responses=ERRORS)
def get_credit_momentum(bar: Annotated[Bar, Depends()]):
    """Credit momentum: year 1 credits, completion, milestones, the first two terms, credit tiers and retention."""
    return answer(bar, "credit-momentum")


def clear_cache() -> None:
    """Forget every cached answer: the pages' and the measure route's."""
    cached.cache_clear()
    clear_measure_cache()


def create_app() -> FastAPI:
    """The standalone app: the router plus CORS for the Playground client."""
    app = FastAPI(title="UNCF API", version="2")
    origins = os.environ.get("UNCF_CORS_ORIGINS", DEFAULT_CORS_ORIGINS).split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin.strip() for origin in origins if origin.strip()],
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    @app.exception_handler(HTTPException)
    async def analysis_error(_request, exception: HTTPException):
        """Keep the analytics routes' errors in the same error body as every other route."""
        codes = {404: "not_found", 422: "invalid_analysis", 503: "analytics_unavailable"}
        return error(exception.status_code, codes.get(exception.status_code, "http_error"), str(exception.detail))

    app.include_router(router, prefix="/api/v1")
    app.include_router(analytics_router)
    return app


app = create_app()
