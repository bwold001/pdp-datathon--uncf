"""Typed requests and calculation receipts shared by API and chat."""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic_core import PydanticCustomError

Analysis = Literal["graduation", "retention", "enrollment"]
ResultStatus = Literal[
    "ok", "suppressed", "unknown", "unavailable", "not_yet_observable", "provisional"
]


class Contract(BaseModel):
    """Reject undeclared parameters at every public boundary."""

    model_config = ConfigDict(extra="forbid")


class AnalysisRequest(Contract):
    """One supported analysis with explicit population choices."""

    analysis: Analysis
    cohort: str | None = None
    credential: Literal["B", "A", "C"] | None = None
    program: str | None = None

    @model_validator(mode="after")
    def compatible_parameters(self) -> AnalysisRequest:
        """Keep enrollment annual and program filters specific to graduation."""
        if self.cohort and not re.fullmatch(r"\d{4}-\d{2}", self.cohort):
            raise PydanticCustomError("invalid_parameters", "cohort must use YYYY-YY")
        if self.cohort and int(self.cohort[-2:]) != (int(self.cohort[:4]) + 1) % 100:
            raise PydanticCustomError(
                "invalid_parameters", "cohort must name consecutive years"
            )
        if self.analysis == "enrollment" and self.cohort is not None:
            raise PydanticCustomError(
                "invalid_parameters", "Annual enrollment includes all entry cohorts"
            )
        if self.analysis != "graduation" and (self.credential or self.program):
            raise PydanticCustomError(
                "invalid_parameters", "Only graduation accepts credential and program"
            )
        return self


class AnalysisDefinition(Contract):
    """Versioned numerical meaning, separate from the model prompt."""

    name: str
    version: str = "1"
    formula: str
    population: str
    grain: str
    exclusions: str
    limitations: list[str]


class CalculationRow(Contract):
    """One rate, composition share or headcount with its actual inputs."""

    label: str
    kind: Literal["rate", "composition", "count"]
    group: dict[str, str] = Field(default_factory=dict)
    horizon: Literal["four_year", "six_year", "to_date"] | None = None
    status: ResultStatus
    numerator: int | None = None
    denominator: int | None = None
    count: int | None = None
    rate: float | None = None
    exclusions: dict[str, int] = Field(default_factory=dict)
    calculation: str = ""
    note: str = ""

    @model_validator(mode="after")
    def consistent_values(self) -> CalculationRow:
        """A count is not a rate and hidden rows contain no numerical evidence."""
        if self.kind == "count" and any(
            v is not None for v in (self.numerator, self.denominator, self.rate)
        ):
            raise PydanticCustomError(
                "invalid_parameters", "Counts have no rate denominator"
            )
        if self.status not in ("ok", "provisional") and (
            any(
                v is not None
                for v in (self.numerator, self.denominator, self.count, self.rate)
            )
            or self.exclusions
        ):
            raise PydanticCustomError(
                "invalid_parameters", "Hidden rows cannot carry numerical inputs"
            )
        return self


class AnalysisReceipt(Contract):
    """A reproducible, already-redacted answer to one typed analysis."""

    analysis: Analysis
    parameters: AnalysisRequest
    definition: AnalysisDefinition
    rows: list[CalculationRow]
    source: Literal["synthetic"] = "synthetic"
    loaded_at: str | None = None
    source_stamp: str | None = None
    cutoff: str | None = None
    coverage_provenance: str = ""
    academic_years: list[str] = Field(default_factory=list)
    program_definition: str = ""
    attribution: str = "Entry major uses program_of_study_term_1; graduation major is inferred only with resolved award-semester evidence."
    limitations: list[str] = Field(default_factory=list)


class Clarification(Contract):
    """One unresolved parameter and the pending request needed to resume it."""

    field: Literal["cohort", "credential", "program"]
    message: str
    choices: list[dict[str, str]]
    pending: AnalysisRequest


class AnalysisResponse(Contract):
    """Either calculation receipts or a clarification, never a guessed interpretation."""

    receipts: list[AnalysisReceipt] = Field(default_factory=list)
    clarification: Clarification | None = None
