"""Versioned capabilities for existing dashboard calculations; no metric formulas live here."""

from dataclasses import dataclass
from types import MappingProxyType

from measures.definitions import definition_for
from measures.models import Measure
from measures.disclosure import profile
from measures.requests import (
    FILTER_NAMES,
    Contract,
    CourseParameters,
    PathsParameters,
    RateParameters,
    RetentionParameters,
    RetentionScope,
    Scope,
)

CATALOG_VERSION = "defined-2"


@dataclass(frozen=True)
class OperationSpec:
    """Describe exactly one executable definition and its supported request capabilities."""

    id: str
    version: str
    label: str
    aliases: tuple[str, ...]
    purpose: str
    parameters: type[Contract]
    supported_filters: tuple[str, ...]
    supported_breakdowns: tuple[str, ...]
    grain: str
    population: str
    time_semantics: str
    exclusions: str
    required_coverage: tuple[str, ...]
    executor: str
    disclosure_profile: str
    limitations: tuple[str, ...]
    units: tuple[str, ...]
    component_denominators: tuple[str, ...]
    definitions: tuple[str, ...]
    measure: Measure | None = None
    kind: str = "defined_measure"

    def compact(self):
        """Offer candidate meanings without claiming that matching aliases are interchangeable."""
        return {
            "id": self.id,
            "version": self.version,
            "kind": self.kind,
            "label": self.label,
            "aliases": self.aliases,
            "purpose": self.purpose,
            "distinctions": self.component_denominators,
        }

    def details(self):
        """Expose capabilities and executable parameter schemas for a selected candidate."""
        return {
            **self.compact(),
            "request_schema": self.parameters.model_json_schema(),
            "supported_filters": self.supported_filters,
            "supported_breakdowns": self.supported_breakdowns,
            "grain": self.grain,
            "population": self.population,
            "time_semantics": self.time_semantics,
            "exclusions": self.exclusions,
            "required_coverage": self.required_coverage,
            "executor": self.executor,
            "disclosure_profile": self.disclosure_profile,
            "disclosure_version": profile(self.disclosure_profile).version,
            "disclosure_scope": {
                "population": self.population,
                "analysis_unit": self.grain,
                "minimum_sample": profile(self.disclosure_profile).minimum,
                "partitions": self.supported_breakdowns,
                "measures": self.definitions,
                "known_overlap": "Selected cohort populations, filtered subsets and their totals may overlap; no disjointness is implied by different operation IDs or cohort labels.",
            },
            "limitations": self.limitations,
            "units": self.units,
            "definitions": self.definitions,
        }


def _scalar(id, measure, parameters=RateParameters, *, aliases=(), definitions=()):
    """Derive scalar catalog descriptions from the existing staff-facing definition owner."""
    definition = definition_for(measure.value)
    credits = measure == Measure.CREDIT_COMPLETION
    dfw = measure == Measure.DFW_RATE
    units = (
        ("sum of student credit ratios", "eligible students")
        if credits
        else (
            ("DFW course enrollments", "classifiable course enrollments")
            if dfw
            else ("successful students", "eligible students")
        )
    )
    if credits or measure in (Measure.GATEWAY_MATH, Measure.GATEWAY_ENGLISH):
        time = "First academic year"
    elif dfw:
        time = "All observed course terms for the entry cohort"
    else:
        time = "Second academic year; other-college PDP outcome"
    limits = tuple(definition["limits"])
    purpose = definition["what"]
    denominators = (definition["how"],)
    if id == "retention.rate":
        federal = definition_for("federal_retention")
        limits += tuple(federal["limits"])
        purpose = "Explicitly select school/PDP retention or the existing next-fall federal retention definition."
        time = "School: next academic year or credential; federal: observed next fall"
        denominators = ("school: " + definition["how"], "federal: " + federal["how"])
    return OperationSpec(
        id=id,
        version="1",
        label=definition["name"],
        aliases=aliases,
        purpose=purpose,
        parameters=parameters,
        supported_filters=FILTER_NAMES,
        supported_breakdowns=FILTER_NAMES,
        grain="course enrollment" if dfw else "student and entry cohort",
        population=definition["who"],
        time_semantics=time,
        exclusions="Existing measure exclusions and out-of-scope counts are preserved; see definitions.",
        required_coverage=(
            "Normalized cohort records",
            "Observed course terms"
            if dfw
            else "Known outcomes for the selected definition",
        ),
        executor="measures.run_measures.run_measure",
        disclosure_profile="dashboard_v1",
        limitations=limits,
        units=units,
        component_denominators=denominators,
        definitions=definitions or (measure.value,),
        measure=measure,
    )


def _page(
    id,
    label,
    aliases,
    purpose,
    parameters,
    executor,
    definitions,
    time,
    denominators,
    limitations=(),
):
    """Describe page-specific populations and denominators without inventing one universal rate."""
    return OperationSpec(
        id=id,
        version="1",
        label=label,
        aliases=aliases,
        purpose=purpose,
        parameters=parameters,
        supported_filters=FILTER_NAMES,
        supported_breakdowns=FILTER_NAMES if id == "student_paths.summary" else (),
        grain="aggregate page component",
        population="Selected entry cohort and explicitly selected cohort-bar filters",
        time_semantics=time,
        exclusions="Component-specific missing evidence and exclusions remain those of the existing page.",
        required_coverage=(
            "Normalized cohort and course records",
            "Observed term coverage; unavailable components remain hidden",
        ),
        executor=executor,
        disclosure_profile="dashboard_v1",
        limitations=limitations
        + (
            "Components have different counting units and denominators; do not combine them into one rate.",
            "All evidence is synthetic. Existing dashboard display suppression is not plan-level disclosure accounting.",
        ),
        units=(
            "students",
            "course enrollments",
            "credits",
            "ratio",
            "percentage points",
        ),
        component_denominators=denominators,
        definitions=definitions,
    )


_OPERATIONS = (
    _scalar(
        "retention.rate",
        Measure.RETENTION,
        RetentionParameters,
        aliases=("retention", "returned here", "back next fall"),
        definitions=("retention", "federal_retention"),
    ),
    _scalar(
        "persistence.rate",
        Measure.PERSISTENCE,
        aliases=("persistence", "at another college"),
    ),
    _scalar("dfw.rate", Measure.DFW_RATE, aliases=("DFW", "D F W grades")),
    _scalar(
        "credit_completion.ratio",
        Measure.CREDIT_COMPLETION,
        aliases=("credit completion", "average credit ratio"),
    ),
    _scalar(
        "gateway.math_completion",
        Measure.GATEWAY_MATH,
        aliases=("gateway math", "gateway success"),
    ),
    _scalar(
        "gateway.english_completion",
        Measure.GATEWAY_ENGLISH,
        aliases=("gateway English", "gateway success"),
    ),
    _page(
        "dfw.course_list",
        "DFW course list",
        ("DFW courses",),
        "Compare classifiable final grades by course.",
        Scope,
        "measures.breakdowns.dfw_courses.dfw_courses",
        ("dfw_rate",),
        "All observed terms for the entry cohort",
        (
            "Course rates count final-grade enrollments; suppression counts distinct students.",
        ),
    ),
    _page(
        "dfw.course_detail",
        "DFW course detail",
        ("course grades",),
        "Show one course by term, delivery and student groups.",
        CourseParameters,
        "measures.breakdowns.dfw_courses.dfw_course",
        ("dfw_rate",),
        "All observed terms for the entry cohort",
        (
            "Each course/term/delivery/group rate has its own classifiable-enrollment denominator.",
            "Distinct students determine suppression, not enrollment counts.",
        ),
    ),
    _page(
        "credit_momentum.summary",
        "Credit momentum",
        ("credit tiers", "credit milestones", "credit progress"),
        "Show first-year credits, milestones, tiers, progress and selected retention.",
        RetentionScope,
        "measures.breakdowns.credit_momentum.credit_momentum",
        ("credit_completion", "credit_milestones", "retention", "federal_retention"),
        "Year one plus the page's observed term and year-two progress windows",
        (
            "Credit means/milestones use students with known credits.",
            "Completion averages individual student ratios.",
            "Term means use students taking courses that term; tier retention uses known selected retention outcomes.",
        ),
    ),
    _page(
        "gateway.course_outcomes",
        "Gateway course outcomes",
        ("gateway success", "C or better", "gateway paths"),
        "Show first-attempt course outcomes, retakes, retention and course pairs; passing is at least 2.0 or P.",
        RetentionScope,
        "measures.breakdowns.gateway_courses.gateway_courses",
        ("gateway.course_outcomes", "retention", "federal_retention"),
        "First attempt per student/course in year one, with the existing page's retake path",
        (
            "Course outcomes count course takers, unlike requirement-based cohort gateway completion at 1.0 or pass.",
            "Outcome retention uses known school/federal outcomes; pairs use students taking both courses.",
        ),
    ),
    _page(
        "student_paths.summary",
        "Student paths",
        ("term paths", "stop out", "transfers"),
        "Show the existing term status paths, moves, transfers and selected retention.",
        PathsParameters,
        "measures.breakdowns.student_paths.student_paths",
        ("student_paths", "retention", "federal_retention"),
        "Two to six fall/spring terms from entry; observed terms remain explicit",
        (
            "Paths use students with a known entry term; moves count transition populations.",
            "Transfers and retention keep their own observable populations and denominators.",
        ),
    ),
)
OPERATIONS = MappingProxyType({spec.id: spec for spec in _OPERATIONS})
