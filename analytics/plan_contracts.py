"""Bounded provider-free catalog and execution envelopes around the shared v2 contracts."""

from typing import Annotated, Literal

from pydantic import AwareDatetime, Field, JsonValue, model_validator

from analytics.contracts_v2 import (
    AnalysisResponseV2,
    Choice,
    Cohort,
    Contract,
    Fingerprint,
    Identifier,
    Source,
    Text,
    VersionReference,
)
from analytics.provenance import ReplaySpec, SnapshotIdentity


class CatalogChoices(Contract):
    """Offer bounded public cohort/course choices without student identifiers or row counts."""

    cohorts: Annotated[tuple[Cohort, ...], Field(max_length=100)] = ()
    courses: Annotated[tuple[Text, ...], Field(max_length=200)] = ()
    more_courses: bool = False
    retention_types: tuple[Choice, ...] = (
        Choice(value="school", label="School/PDP retention"),
        Choice(value="federal", label="Next-fall federal retention"),
    )
    credentials: tuple[Choice, ...] = (
        Choice(value="B", label="Bachelor's degree"),
        Choice(value="A", label="Associate degree"),
        Choice(value="C", label="Certificate"),
    )
    programs: tuple[Choice, ...] = (
        Choice(value="chemistry_general", label="General chemistry"),
        Choice(value="chemistry_family", label="Chemistry family"),
    )


class CatalogOperation(Contract):
    """Expose semantic capabilities and a server-built JSON schema, without implementation paths."""

    id: Identifier
    version: Identifier
    kind: Literal["defined_measure", "legacy_analysis"]
    label: Text
    purpose: Text
    available: bool
    unavailable_reason: Literal["data_unavailable"] | None = None
    parameters_schema: dict[str, JsonValue]
    supported_filters: tuple[Identifier, ...]
    supported_breakdowns: tuple[Identifier, ...]
    grain: Text
    population: Text
    time_semantics: Text
    exclusions: Text
    required_coverage: tuple[Text, ...]
    units: tuple[Text, ...]
    component_denominators: tuple[Text, ...]
    limitations: tuple[Text, ...]
    disclosure_profile: VersionReference
    minimum_sample: int


class CohortFollowup(Contract):
    """Expose analyst-declared whole-cohort follow-up separately from observed records."""

    cohort: Cohort
    years: Annotated[int, Field(ge=0)]


class CoverageDeclaration(Contract):
    """Expose the declarations needed to interpret capability availability and unavailable results."""

    complete_academic_years: Annotated[tuple[Cohort, ...], Field(max_length=100)]
    cohort_followup: Annotated[tuple[CohortFollowup, ...], Field(max_length=100)]
    cutoff: Text | None
    provenance: Text
    provisional_retention_cohorts: Annotated[tuple[Cohort, ...], Field(max_length=100)]


class CatalogResponse(Contract):
    """Bind all choices and capability metadata to a real source and current computation versions."""

    protocol_version: Literal[2] = 2
    catalog_version: Identifier
    snapshot_ref: Fingerprint
    snapshot: SnapshotIdentity
    source: Source
    coverage: CoverageDeclaration
    operations: Annotated[tuple[CatalogOperation, ...], Field(max_length=14)]
    choices: CatalogChoices
    configuration_version: Fingerprint
    implementation_version: Fingerprint


class ExecutionInfo(Contract):
    """Identify this execution separately from stable computation fingerprints."""

    execution_id: Identifier
    started_at: AwareDatetime
    completed_at: AwareDatetime

    @model_validator(mode="after")
    def ordered(self):
        """Reject execution clocks that complete before they start."""
        if self.completed_at < self.started_at:
            raise ValueError("Execution completion precedes its start")
        return self


class PlanResponse(AnalysisResponseV2):
    """Export executed computation inputs and request execution stamps after cleanup/disclosure."""

    replay: ReplaySpec | None = None
    execution: ExecutionInfo | None = None
