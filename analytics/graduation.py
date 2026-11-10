"""Credential-specific completion and graduate composition without invented award dates."""

from analytics.execution import checked

from analytics.presentation import rate_row
from analytics.schemas import CalculationRow
from analytics.coverage import Coverage
from analytics.programs import normalize_program

CREDENTIAL_FIELDS = {
    "B": ("first_year_to_bachelors_at_coh", "years_to_ba_at_cohort_inst"),
    "A": ("first_year_to_associates_at_coho", "years_to_latest_associates_at_co"),
    "C": ("first_year_to_certificate_at_coh", "years_to_latest_certificate_at_c"),
}
HORIZONS = [("four_year", 4), ("six_year", 6), ("to_date", None)]
LABELS = [
    ("Entrants completing in any program", "rate"),
    ("Entrants completing in the selected program", "rate"),
    ("Program graduates who entered in the program", "composition"),
    ("Program graduates who switched in", "composition"),
    ("Program graduates with unknown entry program", "composition"),
]


def completion_year(student: dict, credential: str, observed: int) -> int | None:
    """Read first qualifying completion, rejecting contradictory or unobserved timing."""
    first_field, latest_field = CREDENTIAL_FIELDS[credential]
    first, latest = student.get(first_field), student.get(latest_field)
    if (
        first is None
        or latest is None
        or first < 0
        or latest < first
        or first > observed
        or latest > observed
    ):
        return None
    if first == 0 and latest > 0:
        return None
    return first


def calculate(
    students: list[dict],
    cohort: str,
    credential: str,
    programs: set[str],
    coverage: Coverage,
) -> list[CalculationRow]:
    """Return each completion horizon and distinguish rate from graduate composition."""
    result = []
    eligible = [s for s in checked(students) if s["credential_type_sought_year_1"] == credential]
    unknown_eligibility = sum(
        s["credential_type_sought_year_1"] in (None, "", "UNKNOWN") for s in checked(students)
    )
    observed = coverage.cohort_followup_years.get(cohort, 0)
    for horizon, years in HORIZONS:
        if years is not None and not coverage.observable(cohort, years):
            result.extend(
                CalculationRow(
                    label=label,
                    kind=kind,
                    horizon=horizon,
                    status="not_yet_observable",
                    note="Whole-cohort follow-up is not certified for this horizon.",
                )
                for label, kind in LABELS
            )
            continue
        if not coverage.cutoff or not observed:
            result.extend(
                CalculationRow(
                    label=label,
                    kind=kind,
                    horizon=horizon,
                    status="unavailable",
                    note="Extract cutoff and cohort follow-up must be declared.",
                )
                for label, kind in LABELS
            )
            continue
        limit = years if years is not None else observed
        known = [(s, completion_year(s, credential, observed)) for s in checked(eligible)]
        entrants = [
            (s, y)
            for s, y in checked(known)
            if normalize_program(s["program_of_study_term_1"]) in programs
        ]
        any_known = [(s, y) for s, y in checked(entrants) if y is not None]
        any_graduates = [(s, y) for s, y in checked(any_known) if 0 < y <= limit]
        program_known = [
            (s, y)
            for s, y in checked(any_known)
            if not 0 < y <= limit or s.get("graduation_program") is not None
        ]
        program_graduates = [
            (s, y)
            for s, y in checked(program_known)
            if 0 < y <= limit and s.get("graduation_program") in programs
        ]
        inferred = [
            s
            for s, y in checked(known)
            if y is not None
            and 0 < y <= limit
            and s.get("graduation_program") in programs
        ]
        exclusions = {
            "unknown_credential_eligibility": unknown_eligibility,
            "unknown_entry_program": sum(
                normalize_program(s["program_of_study_term_1"]) is None
                for s in checked(eligible)
            ),
            "unknown_completion_timing": sum(y is None for _, y in checked(entrants)),
        }
        result.append(
            rate_row(
                LABELS[0][0],
                len(any_graduates),
                len(any_known),
                horizon=horizon,
                exclusions=exclusions,
            )
        )
        result.append(
            rate_row(
                LABELS[1][0],
                len(program_graduates),
                len(program_known),
                horizon=horizon,
                exclusions={
                    **exclusions,
                    "unknown_completion_program": len(any_known) - len(program_known),
                },
                note="Completion program is inferred from a resolved final relevant semester; unresolved majors are excluded.",
            )
        )
        composition_exclusions = {
            "unknown_completion_program": sum(
                y is not None and 0 < y <= limit and s.get("graduation_program") is None
                for s, y in checked(known)
            )
        }
        for label, predicate in [
            (LABELS[2][0], lambda p: p in programs),
            (LABELS[3][0], lambda p: p is not None and p not in programs),
            (LABELS[4][0], lambda p: p is None),
        ]:
            count = sum(
                predicate(normalize_program(s["program_of_study_term_1"]))
                for s in checked(inferred)
            )
            result.append(
                rate_row(
                    label,
                    count,
                    len(inferred),
                    kind="composition",
                    horizon=horizon,
                    exclusions=composition_exclusions,
                    note="Composition among inferred program graduates, not a graduation rate.",
                )
            )
    return result
