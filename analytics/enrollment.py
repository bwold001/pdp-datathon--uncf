"""Distinct annual program enrollments, with ethnicity kept separate from race."""

from collections import defaultdict

from analytics.schemas import CalculationRow
from analytics.programs import normalize_program


def calculate(enrollments: list[dict], years: list[str]) -> list[CalculationRow]:
    """Count a student once per year, program and ethnicity, regardless of course count."""
    groups = defaultdict(set)
    for row in enrollments:
        if row["academic_year"] not in years or row["course_id"] is None:
            continue
        program = normalize_program(row["term_program_of_study"]) or "UNKNOWN"
        groups[(row["academic_year"], program, row["ethnicity"] or "UNKNOWN")].add(
            row["student_id"]
        )
    return [
        CalculationRow(
            label="Enrollment",
            kind="count",
            status="ok",
            count=len(students),
            group={"academic_year": year, "program": program, "ethnicity": ethnicity},
            calculation=f"COUNT(DISTINCT student_id) = {len(students)}",
            note="Program totals overlap when a student changes programs.",
        )
        for (year, program, ethnicity), students in sorted(groups.items())
    ]
