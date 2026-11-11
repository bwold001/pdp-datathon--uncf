"""Explicit extract completeness; observed rows alone never prove follow-up."""

from pathlib import Path

import yaml
from pydantic import Field, model_validator

from analytics.schemas import Contract

DEFAULT_CONFIG = Path(__file__).parent / "config" / "analytics.yaml"


class Coverage(Contract):
    """Analyst-declared observation windows and their provenance."""

    complete_academic_years: list[str] = Field(default_factory=list)
    cohort_followup_years: dict[str, int] = Field(default_factory=dict)
    cutoff: str | None = None
    provenance: str = ""
    suppression_threshold: int = Field(default=1, ge=1)  # legacy config; no longer hides results
    provisional_retention_cohorts: list[str] = Field(
        default_factory=lambda: ["2024-25"]
    )

    @model_validator(mode="after")
    def declarations_need_provenance(self):
        """Do not enable numerical coverage from an undocumented declaration."""
        if (
            self.complete_academic_years or self.cohort_followup_years
        ) and not self.provenance.strip():
            raise ValueError("Coverage declarations require provenance")
        if self.cohort_followup_years and not self.cutoff:
            raise ValueError("Follow-up declarations require an extract cutoff")
        for year in self.complete_academic_years:
            if len(year) != 7 or not year[:4].isdigit() or not year[-2:].isdigit():
                raise ValueError("Complete years must use YYYY-YY")
            if (int(year[:4]) + 1) % 100 != int(year[-2:]):
                raise ValueError("Complete years must be consecutive")
        if any(years < 0 for years in self.cohort_followup_years.values()):
            raise ValueError("Follow-up cannot be negative")
        return self

    def latest_two_years(self) -> list[str]:
        """Select only the latest two explicitly complete years."""
        years = sorted(set(self.complete_academic_years))
        return years[-2:] if len(years) >= 2 else []

    def observable(self, cohort: str, horizon: int) -> bool:
        """Whether the whole cohort has the declared follow-up for a horizon."""
        return self.cohort_followup_years.get(cohort, 0) >= horizon


def load_coverage(path: Path = DEFAULT_CONFIG) -> Coverage:
    """Read the shared configuration on each request so corrections take effect."""
    return Coverage.model_validate(yaml.safe_load(path.read_text()) or {})
