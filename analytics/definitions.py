"""Versioned calculation definitions for every consumer."""

from analytics.schemas import AnalysisDefinition

DEFINITIONS = {
    "graduation": AnalysisDefinition(
        name="Graduation by entry and inferred completion program",
        formula="qualifying completions / eligible entrants; graduate composition = entry-program graduates / inferred program graduates",
        population="Credential-seeking entrants in the selected entry cohort and credential population.",
        grain="Student and entry cohort, evaluated separately for each horizon and perspective.",
        exclusions="Unknown eligibility, entry program, outcome timing or inferred completion program are identified separately.",
        limitations=[
            "Four- and six-year horizons need whole-cohort follow-up certification.",
            "Completion to date is descriptive, not a mature graduation rate.",
            "Rounded earliest time to credential does not identify the relevant award semester.",
        ],
    ),
    "retention": AnalysisDefinition(
        name="Retention overall and by entry program",
        formula="retained students / students with known retention outcomes",
        population="All students in the selected entry cohort.",
        grain="Student and entry cohort.",
        exclusions="Unknown retention outcomes are excluded from the denominator.",
        limitations=[
            "Retention uses the existing PDP flag: enrolled again next academic year or credential earned by then.",
            "Spring starters have less time to return than fall starters.",
        ],
    ),
    "enrollment": AnalysisDefinition(
        name="Annual enrollment by ethnicity and program",
        formula="COUNT(DISTINCT student_id) within academic year, program and ethnicity",
        population="Actual cohort-institution course enrollments in the latest two certified complete academic years.",
        grain="Student, academic year and program.",
        exclusions="Other-institution-only rows without a course are excluded.",
        limitations=[
            "Students changing programs can appear in multiple programs; program totals overlap.",
            "Ethnicity is not race; unknown ethnicity remains a separate category.",
        ],
    ),
}
