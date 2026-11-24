"""Catalog-driven question suggestions and coverage guidance without executing analyses."""

from analytics.contracts_v2 import operation_id
from analytics.plan_contracts import ScopeGuidance, SuggestedQuestion

# Wording belongs to analytics; catalog capabilities decide which templates can be offered.
QUESTION_TEMPLATES = {
    "retention.rate": "What is the school retention rate?",
    "dfw.rate": "What share of course enrollments received a D, F, or withdrawal?",
    "credit_momentum.summary": "How do first-year credits and school retention compare?",
    "gateway.course_outcomes": "What are the first-attempt outcomes in gateway courses?",
    "student_paths.summary": "What student paths appear over the first four terms using school retention?",
    "legacy.entry_major_retention": "What is the retention rate by entry major?",
    "legacy.graduation": "What is the graduation rate for chemistry majors?",
    "legacy.annual_enrollment": "What is enrollment by ethnicity and academic program in the latest two complete years?",
}


def suggested_questions(operations, coverage, cohorts):
    """Filter registered templates by schema capabilities and known coverage blockers."""
    available = {item.id for item in operations if item.available}
    questions = []
    for key, question in QUESTION_TEMPLATES.items():
        if key not in available or not cohorts:
            continue
        if key == "legacy.graduation" and not any(
            coverage.observable(cohort, 4) for cohort in cohorts
        ):
            continue
        if key == "legacy.annual_enrollment" and not coverage.latest_two_years():
            continue
        questions.append(SuggestedQuestion(operation_id=key, question=question))
    return tuple(questions)


def scope_guidance(plan, coverage):
    """Describe only known limitations; leave row-level eligibility for confirmed execution."""
    guidance = []
    for step in plan.steps:
        key = operation_id(step)
        messages = []
        if key == "legacy.graduation":
            cohort = step.parameters.cohort
            if isinstance(cohort, str):
                years = coverage.cohort_followup_years.get(cohort)
                if years is None:
                    messages.append(
                        "Graduation rates are unavailable because we haven't verified how long the data follows this entry cohort."
                    )
                elif years < 6:
                    if years < 4:
                        messages.append(
                            "Four-year and six-year graduation rates are unavailable because this cohort hasn't been followed long enough."
                        )
                    else:
                        messages.append(
                            "The six-year graduation rate is unavailable because this cohort hasn't been followed long enough."
                        )
                if not coverage.cutoff or not years:
                    messages.append(
                        "Completion to date requires a verified data cutoff and follow-up period."
                    )
            messages.append(
                "Graduation specifically in Chemistry cannot be established from this extract because exact award-semester information is missing."
            )
        elif key == "legacy.annual_enrollment" and not coverage.latest_two_years():
            messages.append(
                "Annual enrollment results require two verified complete academic years; these have not been declared for this dataset."
            )
        elif key == "measure_variant":
            messages.append(
                "The available gateway evidence does not support the C-or-better variant."
            )
        if messages:
            guidance.extend(
                ScopeGuidance(
                    step_id=step.step_id, state="known_limitation", message=message
                )
                for message in messages
            )
        else:
            guidance.append(
                ScopeGuidance(
                    step_id=step.step_id,
                    state="not_checked",
                    message="We'll check whether this selection has usable information when you calculate.",
                )
            )
    return tuple(guidance)
