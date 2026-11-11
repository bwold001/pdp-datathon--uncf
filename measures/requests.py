"""Pure dashboard request schemas and filter validation, independent of HTTP and orchestration."""

from typing import Annotated, Literal

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    StrictInt,
    StrictStr,
    StringConstraints,
)

from measures.models import ALLOWED_VALUES, Group, GroupDimension, Measure

Text = Annotated[
    StrictStr, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)
]
Dimension = Literal[
    "cohort_term",
    "enrollment_intensity",
    "enrollment_type",
    "pell",
    "gender",
    "race",
    "ethnicity",
    "age_band",
]
RetentionType = Literal["school", "federal"]
FILTER_DIMENSIONS = tuple(GroupDimension(name) for name in Dimension.__args__)
FILTER_NAMES = tuple(d.value for d in FILTER_DIMENSIONS)
RETENTION_MEASURES = {"school": Measure.RETENTION, "federal": Measure.FEDERAL_RETENTION}


class InvalidFilter(ValueError):
    """A cohort, filter or retention definition outside the supported domain."""


def check_cohort(value: str) -> str:
    """Require a consecutive academic year independently of the current catalog."""
    if int(value[-2:]) != (int(value[:4]) + 1) % 100:
        raise ValueError("cohort must name consecutive years")
    return value


def unique_sorted(values: tuple) -> tuple:
    """Canonicalize set-like request fields while refusing duplicates."""
    if len(values) != len(set(values)):
        raise ValueError("values must be unique")
    return tuple(sorted(values))


Cohort = Annotated[
    StrictStr, StringConstraints(pattern=r"^\d{4}-\d{2}$"), AfterValidator(check_cohort)
]
Dimensions = Annotated[
    tuple[Dimension, ...], Field(max_length=2), AfterValidator(unique_sorted)
]


class Contract(BaseModel):
    """Reject unknown properties and freeze all nested typed records."""

    model_config = ConfigDict(
        extra="forbid", frozen=True, allow_inf_nan=False, revalidate_instances="always"
    )


class Filters(Contract):
    """Expose exactly the eight categorical dimensions of the existing HTTP cohort bar."""

    cohort_term: Literal["Fall", "Winter", "Spring", "Summer", "UNKNOWN"] | None = None
    enrollment_intensity: Literal["Full-time", "Part-time", "UNKNOWN"] | None = None
    enrollment_type: (
        Literal["First-time", "Re-admit", "Transfer-in", "UNKNOWN"] | None
    ) = None
    pell: Literal["Y", "N", "UNKNOWN"] | None = None
    gender: Literal["M", "F", "P", "X", "UNKNOWN"] | None = None
    race: (
        Literal[
            "White",
            "Hispanic",
            "American Indian or Alaska Native",
            "Native Hawaiian or Other Pacific Islander",
            "Two or More Races",
            "Black or African American",
            "Nonresident alien",
            "Asian",
            "UNKNOWN",
        ]
        | None
    ) = None
    ethnicity: Literal["H", "N", "UNKNOWN"] | None = None
    age_band: (
        Literal["20 and younger", "> 20-24", "Older than 24", "UNKNOWN"] | None
    ) = None


class Scope(Contract):
    """Identify a cohort and explicit categorical filters."""

    cohort: Cohort
    filters: Filters = Field(default_factory=Filters)


class RateParameters(Scope):
    """Permit only supported categorical scalar breakdowns."""

    group_by: Dimensions = ()


class RetentionParameters(RateParameters):
    """Require a resolved retention definition rather than silently choosing one."""

    retention_type: RetentionType


class RetentionScope(Scope):
    """Name the retention definition for a fixed page breakdown."""

    retention_type: RetentionType


class CourseParameters(Scope):
    """Require a concrete course for the fixed DFW detail breakdown."""

    course: Text


class PathsParameters(RetentionScope):
    """Preserve the page's bounded term horizon and single optional grouping."""

    terms: Annotated[StrictInt, Field(ge=2, le=6)] = 3
    group_by: Dimension | None = None


def validate_cohort(cohort, allowed_cohorts):
    """Apply the caller's catalog cohort set without importing deployment configuration."""
    if cohort not in allowed_cohorts:
        raise InvalidFilter(f"Cohort has no value {cohort!r}.")


def validate_retention_type(retention_type):
    """Require the school or federal definition explicitly."""
    if retention_type not in RETENTION_MEASURES:
        raise InvalidFilter(
            f"retention_type has no value {retention_type!r}. Use school or federal."
        )


def validate_filters(filters):
    """Validate categorical names and values before building calculation-owner groups."""
    names = [name for name, _ in filters]
    if len(names) != len(set(names)):
        raise InvalidFilter("A filter can be selected only once.")
    for name, value in filters:
        if name not in FILTER_NAMES:
            raise InvalidFilter(f"There is no filter called {name!r}.")
        if value not in ALLOWED_VALUES[GroupDimension(name)]:
            raise InvalidFilter(f"{name} has no value {value!r}.")


def filter_group(filters: Filters) -> Group:
    """Convert the typed cohort-bar fields to the calculation owner's immutable group."""
    chosen = filters.model_dump(exclude_none=True)
    validate_filters(tuple(chosen.items()))
    return Group.of(*((GroupDimension(name), value) for name, value in chosen.items()))
