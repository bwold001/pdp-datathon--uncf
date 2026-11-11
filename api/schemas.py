"""Response shapes for GET /measures/{measure} and the Explorer pages.

The client has no generated types: when a shape here changes, update the client code that reads it.
"""
from __future__ import annotations

from typing import Literal, Union

from pydantic import BaseModel, ConfigDict

# The measures that have a definition (#3). Add one here once measures/definitions.py has it.
Measure = Literal["retention", "persistence", "gateway_math", "gateway_english", "dfw_rate", "credit_completion"]
# school: the PDP retention flag. federal: fall to fall, enrolled here the fall after year 1.
RetentionType = Literal["school", "federal"]
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


class GroupRow(BaseModel):
    """One group's result. A hidden or missing number is null with its status, never 0."""

    group: dict[str, str]  # {} is everyone; {"pell": "Y"}; {"pell": "Y", "race": "Asian"}
    numerator: Number | None
    denominator: Number | None
    rate: float | None
    status: Status
    n_excluded: int | None
    n_out_of_scope: int | None
    note: str
    split: dict[str, int] | None = None  # dfw_rate only: D+, D, D-, F and W counts


class MeasureByGroupMeta(BaseModel):
    """What the rows are, what they mean and where they came from."""

    measure: Measure
    cohort: Cohort
    group_by: list[Dimension]
    filters: dict[str, str]
    retention_type: RetentionType
    definition: MeasureDefinition
    source: str
    loaded_at: str  # when the source data was loaded, not when the numbers were calculated
    provisional: bool  # the class's second year is only partly in the data, so a year-2 rate can still change


class MeasureByGroupResponse(BaseModel):
    """GET /measures/{measure}: the everyone row first, then one row per group."""

    meta: MeasureByGroupMeta
    rows: list[GroupRow]


class ExplorerMeta(BaseModel):
    """What every Explorer page answer says about its question. Pages add their own fields."""

    model_config = ConfigDict(extra="allow")

    cohort: Cohort
    filters: dict[str, str]
    retention_type: RetentionType
    provisional: bool
    min_students: int
    source: str
    loaded_at: str


class Retention(BaseModel):
    """Retention for some students, by one type. Hidden numbers are null with their status, never 0."""

    type: RetentionType
    status: Status
    retained: Number | None
    students: int | None
    numerator: Number | None
    denominator: int | None
    rate: float | None
    n_excluded: int | None
    n_out_of_scope: int | None


class DfwSplit(BaseModel):
    """Each DFW grade apart (D+, D, D-, F, W), the D and F grades together (DF), W, every final grade, and shares."""

    grades: dict[str, int]
    DF: int
    W: int
    total: int
    shares: dict[str, float | None]


class DfwTally(BaseModel):
    """A DFW rate. Every number is null when under 10 students."""

    model_config = ConfigDict(extra="allow")

    students: int | None
    num: int | None
    den: int | None
    rate: float | None
    split: DfwSplit | None


class PageResponse(BaseModel):
    """An Explorer page's answer: the meta and status every page has, plus the page's own fields."""

    model_config = ConfigDict(extra="allow")

    meta: ExplorerMeta
    status: Literal["ok", "suppressed"]


class StudentPathsResponse(PageResponse):
    """GET /student-paths."""

    students: int | None
    retention: Retention | None


class DfwResponse(PageResponse):
    """GET /dfw."""

    everyone: DfwTally
    courses: list[DfwTally]
    hidden_courses: int


class DfwCourseResponse(DfwTally):
    """GET /dfw/course: one course, then each term, delivery method and group next to everyone else."""

    meta: ExplorerMeta
    course: str


class GatewayResponse(PageResponse):
    """GET /gateway."""

    students: int | None
    cohort_retention: Retention | None


class CreditMomentumResponse(PageResponse):
    """GET /credit-momentum."""

    students: int | None
    retention: Retention | None
    # Meaningful progress toward a degree (measures/breakdowns/credit_progress.py): settings, the minimum and pace,
    # year 1 groups with retention, why students fell below the minimum, and year 2. None when the page is hidden.
    progress: dict | None = None


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
