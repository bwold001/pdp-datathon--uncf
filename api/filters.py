"""One filter set for every page and both APIs: the cohort year, eight filters and the retention type.

This file only checks a request and turns it into what the measures take: a Group of filters and a retention
Measure. Picking the students and counting happen in measures/ (run_measure and measures/breakdowns).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from api import data
from measures.breakdowns.common import filter_options
from measures.requests import (
    FILTER_DIMENSIONS as FILTER_DIMENSIONS, FILTER_NAMES as FILTER_NAMES,
    RETENTION_MEASURES, InvalidFilter as InvalidFilter,
    validate_cohort, validate_filters, validate_retention_type,
)
from measures.models import (
    ALLOWED_VALUES as ALLOWED_VALUES,
    Group,
    GroupDimension,
    Measure,
    min_students,
)

# The cohort bar's filters after the cohort year, in the bar's order. /measures/{measure} groups by the same list.
FILTER_LABELS = {
    "cohort_term": "Starting term",
    "enrollment_intensity": "Full or part time",
    "enrollment_type": "Enrollment type",
    "pell": "Pell grant",
    "gender": "Gender",
    "race": "Race",
    "ethnicity": "Ethnicity",
    "age_band": "Age",
}
# school: the PDP retention flag. federal: fall to fall. Each is its own measure.
RETENTION_TYPES = tuple(RETENTION_MEASURES)
DEFAULT_RETENTION_TYPE = "school"


@dataclass(frozen=True)
class CohortQuery:
    """One cohort year, the filters set on it, and which retention to report. A filter left out means "All".

    A cohort left as None is the data's default cohort (data.default_cohort). The years allowed are the ones in
    the loaded data, so checking a query needs the data: it raises data.DataMissing when nothing is loaded.
    """

    cohort: str | None = None
    filters: tuple[tuple[str, str], ...] = field(default_factory=tuple)
    retention_type: str = DEFAULT_RETENTION_TYPE

    def __post_init__(self) -> None:
        """Apply the domain validators against the cohort years in the loaded data."""
        if self.cohort is None:
            object.__setattr__(self, "cohort", data.default_cohort())
        validate_cohort(self.cohort, data.cohorts())
        validate_retention_type(self.retention_type)
        validate_filters(self.filters)

    @classmethod
    def of(cls, cohort: str | None = None, retention_type: str = DEFAULT_RETENTION_TYPE, **filters: str | None) -> CohortQuery:
        """A query from keyword filters, skipping the ones left as None. Sorted, so equal queries are equal."""
        chosen = tuple(sorted((name, value) for name, value in filters.items() if value is not None))
        return cls(cohort, chosen, retention_type)

    def as_dict(self) -> dict[str, str]:
        """The filters that are set, by name."""
        return dict(self.filters)

    def as_group(self) -> Group:
        """The filters as the measures take them: a Group every counted student matches."""
        return Group.of(*((GroupDimension(name), value) for name, value in self.filters))

    @property
    def retention_measure(self) -> Measure:
        """The measure behind the retention type."""
        return RETENTION_MEASURES[self.retention_type]

    def meta(self) -> dict:
        """What every answer says about the question it answers."""
        return {
            "cohort": self.cohort,
            "filters": self.as_dict(),
            "retention_type": self.retention_type,
            "provisional": data.is_provisional(self.cohort),
            "min_students": min_students(),
            "source": data.source(),
        }


def cohort_options(cohort: str | None = None) -> dict:
    """How many students entered in each cohort year, and in the chosen cohort, how many have each filter value."""
    cohort = CohortQuery(cohort).cohort  # checks the cohort, or picks the default one
    counts = filter_options(data.cohorts(), cohort, data.data_path())
    return {
        "cohort": cohort,
        **counts,
        "labels": FILTER_LABELS,
        "retention_types": list(RETENTION_TYPES),
        "min_students": min_students(),
        "source": data.source(),
        "loaded_at": data.loaded_at(),
    }
