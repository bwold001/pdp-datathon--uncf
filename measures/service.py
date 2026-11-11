"""Validate and dispatch defined requests to their existing calculation owners."""

from measures.breakdowns.credit_momentum import credit_momentum
from measures.breakdowns.dfw_courses import dfw_course, dfw_courses
from measures.breakdowns.gateway_courses import gateway_courses
from measures.breakdowns.student_paths import student_paths
from measures.models import Cohort, GroupBy, GroupDimension, Measure
from measures.registry import OPERATIONS
from measures.requests import RETENTION_MEASURES, filter_group
from measures.run_measures import run_measure

_PAGES = {
    "dfw.course_list": dfw_courses,
    "dfw.course_detail": dfw_course,
    "credit_momentum.summary": credit_momentum,
    "gateway.course_outcomes": gateway_courses,
    "student_paths.summary": student_paths,
}


def execute(operation_id, parameters, snapshot, *, include_evidence=False):
    """Borrow the supplied snapshot and return owner results without changing any formulas."""
    spec = OPERATIONS[operation_id]
    parameters = spec.parameters.model_validate(parameters)
    filters = filter_group(parameters.filters)
    if spec.measure is not None:
        measure = (
            RETENTION_MEASURES[parameters.retention_type]
            if operation_id == "retention.rate"
            else spec.measure
        )
        grouping = (
            [GroupBy.of(*(GroupDimension(d) for d in parameters.group_by))]
            if parameters.group_by
            else None
        )
        return run_measure(
            measure,
            [Cohort.of(parameters.cohort)],
            grouping,
            database=snapshot.positional,
            filters=filters,
        )
    options = {"cohort": parameters.cohort, "filters": filters, "snapshot": snapshot}
    if hasattr(parameters, "retention_type"):
        options["retention_measure"] = RETENTION_MEASURES[parameters.retention_type]
    if operation_id == "credit_momentum.summary" and include_evidence:
        options["include_evidence"] = True
    if operation_id == "dfw.course_detail":
        options["course"] = parameters.course
    if operation_id == "student_paths.summary":
        options.update(
            terms=parameters.terms,
            group_by=GroupDimension(parameters.group_by)
            if parameters.group_by
            else None,
        )
    return _PAGES[operation_id](**options)


def operation_for_measure(measure):
    """Resolve a dashboard scalar's existing name to its registered operation ID."""
    selected = Measure(measure)
    if selected == Measure.FEDERAL_RETENTION:
        return "retention.rate"
    return next(spec.id for spec in OPERATIONS.values() if spec.measure == selected)
