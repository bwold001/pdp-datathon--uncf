"""Stable response contracts for the deployed Results API."""
from __future__ import annotations

from typing import Literal, Union

from pydantic import BaseModel

# The measures that have a definition (#3). Add one here once measures/definitions.py has it.
Measure = Literal["retention", "persistence", "gateway_math", "gateway_english"]
Cohort = Literal["2021-22", "2022-23", "2023-24", "2024-25"]
# Every grouping the measures support except first_gen (unreliable in the mock data) and course (DFW only).
Dimension = Literal[
    "pell",
    "enrollment_intensity",
    "cohort_term",
    "enrollment_type",
    "age_band",
    "gender",
    "race",
    "ethnicity",
]
# not_reported: the college doesn't report what the measure needs, e.g. which students must take gateway math.
Status = Literal["ok", "suppressed", "not_yet_observable", "not_reported"]

DIMENSION_LABELS: dict[str, str] = {
    "pell": "Pell grant",
    "enrollment_intensity": "Full or part time",
    "cohort_term": "Starting term",
    "enrollment_type": "Enrollment type",
    "age_band": "Age",
    "gender": "Gender",
    "race": "Race",
    "ethnicity": "Ethnicity",
}
MAX_GROUP_BY = 2
SOURCE = "PDP analysis-ready cohort and course files (synthetic sample)"

# Counts stay whole numbers in JSON (1414, not 1414.0).
Number = Union[int, float]


class MeasureDefinition(BaseModel):
    """What a measure means, from measures/definitions.py."""

    name: str
    pdp_name: str
    what: str
    how: str
    who: str
    limits: list[str]


class ResultRow(BaseModel):
    """One group's result. A hidden or missing number is null with its status, never 0."""

    group: dict[str, str]  # {} is everyone; {"pell": "Y"}; {"pell": "Y", "race": "Asian"}
    numerator: Number | None
    denominator: Number | None
    rate: float | None
    status: Status
    n_excluded: int | None
    n_out_of_scope: int | None
    note: str


class ResultsMeta(BaseModel):
    """What the rows are, what they mean and where they came from."""

    measure: Measure
    cohort: Cohort
    group_by: list[Dimension]
    definition: MeasureDefinition
    source: str
    loaded_at: str  # when the source data was loaded, not when the numbers were calculated
    provisional: bool  # the class's second year is only partly in the data, so a year-2 rate can still change


class ResultsResponse(BaseModel):
    """GET /results: the everyone row first, then one row per group."""

    meta: ResultsMeta
    rows: list[ResultRow]


class Option(BaseModel):
    """A value a client can ask for, and its plain-language label."""

    value: str
    label: str


class OptionsResponse(BaseModel):
    """GET /options: what the Explorer and chat can ask for."""

    measures: list[Option]
    cohorts: list[str]
    dimensions: list[Option]
    max_group_by: int


class HealthResponse(BaseModel):
    """GET /health: whether the data is loaded, and when."""

    status: Literal["ok"] = "ok"
    data_available: bool
    loaded_at: str | None


class ErrorDetail(BaseModel):
    """A machine-readable code and a sentence for people."""

    code: str
    message: str


class ErrorResponse(BaseModel):
    """Body of every error this API returns itself: invalid_group_by (422), data_missing (503)."""

    error: ErrorDetail
