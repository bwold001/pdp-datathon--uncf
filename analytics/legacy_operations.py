"""Catalog the three existing analyses as defined legacy adapters, never exploration."""

from types import MappingProxyType

from analytics.contracts_v2 import (
    EnrollmentParameters,
    GraduationParameters,
    LegacyRetentionParameters,
)
from analytics.definitions import DEFINITIONS
from measures.registry import OperationSpec

_PARAMETERS = {
    "graduation": GraduationParameters,
    "retention": LegacyRetentionParameters,
    "enrollment": EnrollmentParameters,
}
LEGACY_IDS = {
    "legacy.graduation": "graduation",
    "legacy.entry_major_retention": "retention",
    "legacy.annual_enrollment": "enrollment",
}


def _spec(id, name):
    """Retain the existing definition, population, horizons and coverage limitations."""
    definition = DEFINITIONS[name]
    coverage = {
        "graduation": (
            "Certified whole-cohort follow-up for four/six-year rates",
            "To-date descriptive outcomes",
            "Exact award semester required for completion-program attribution",
        ),
        "retention": (
            "Known PDP retention flag",
            "Provisional cohorts are declared in coverage configuration",
        ),
        "enrollment": (
            "Two explicitly certified complete academic years",
            "Actual course enrollments at the cohort institution",
        ),
    }
    time = {
        "graduation": "Four-year, six-year and completion-to-date horizons remain separate",
        "retention": "Next academic year, using the PDP flag",
        "enrollment": "Latest two certified complete academic years across entry cohorts",
    }
    return OperationSpec(
        id=id,
        version=definition.version,
        label=definition.name,
        aliases=(name, "entry major" if name == "retention" else name + " by program"),
        purpose=definition.name,
        parameters=_PARAMETERS[name],
        supported_filters=(),
        supported_breakdowns=(),
        grain=definition.grain,
        population=definition.population,
        time_semantics=time[name],
        exclusions=definition.exclusions,
        required_coverage=coverage[name],
        executor="analytics.service.AnalyticsService.analyze",
        disclosure_profile="legacy_v1",
        limitations=tuple(definition.limitations),
        units=("students", "ratio"),
        component_denominators=(definition.formula,),
        definitions=("legacy." + name,),
        kind="legacy_analysis",
    )


OPERATIONS = MappingProxyType({id: _spec(id, name) for id, name in LEGACY_IDS.items()})
