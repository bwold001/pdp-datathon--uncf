"""Program adapter for the existing PDP retention outcome semantics."""

from collections import defaultdict

from analytics.presentation import rate_row
from analytics.programs import normalize_program


def calculate(students: list[dict], provisional: bool) -> list:
    """Count known outcomes overall and by first-term program, preserving unknowns."""
    groups = defaultdict(list)
    for student in students:
        groups[
            normalize_program(student["program_of_study_term_1"]) or "UNKNOWN"
        ].append(student)
    output = []
    for program, members in [("All majors", students), *sorted(groups.items())]:
        known = [s for s in members if s["retention"] is not None]
        retained = sum(bool(s["retention"]) for s in known)
        output.append(
            rate_row(
                f"Retention — {program}",
                retained,
                len(known),
                group={} if program == "All majors" else {"entry_program": program},
                exclusions={"unknown_outcome": len(members) - len(known)},
                provisional=provisional,
                note="Existing PDP retention flag; denominator includes known outcomes only.",
            )
        )
    return output
