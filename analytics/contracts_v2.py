"""Inactive v2 wire contracts; execution, catalog capabilities and disclosure live with their owners."""

from __future__ import annotations

import json
from typing import Annotated, ClassVar, Literal, Union

from pydantic import (
    AfterValidator, AwareDatetime, Field, StrictFloat,
    StrictInt, StrictStr, StringConstraints, TypeAdapter, create_model, model_validator,
)

from measures.requests import (
    Contract as Contract,
    Cohort as Cohort,
    CourseParameters as CourseParameters,
    Dimension as Dimension,
    Dimensions as Dimensions,
    Filters as Filters,
    PathsParameters as PathsParameters,
    RateParameters as RateParameters,
    RetentionParameters as RetentionParameters,
    RetentionScope as RetentionScope,
    RetentionType as RetentionType,
    Scope as Scope,
    check_cohort as check_cohort,
    unique_sorted as unique_sorted,
)

Text = Annotated[StrictStr, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]
Identifier = Annotated[StrictStr, StringConstraints(pattern=r"^[a-zA-Z0-9_.-]{1,128}$")]
Fingerprint = Annotated[StrictStr, StringConstraints(pattern=r"^[a-f0-9]{64}$")]
Number = Annotated[StrictFloat, Field(allow_inf_nan=False)]
Count = Annotated[StrictInt, Field(ge=0)]
SampleSize = Annotated[StrictInt, Field(ge=1)]
Precision = Annotated[StrictInt, Field(ge=0, le=10)]
Grouping = Literal["online_count_0_1to2_3plus", "retention_outcome_school", "retention_outcome_federal"]
Feature = Literal["credits_earned_y1", "credits_attempted_y1", "online_enrollment_count_y1", "online_enrollment_share_y1"]
ParameterKey = Literal["cohort", "retention_type", "course", "terms", "credential", "program", "x", "y", "grouping", "variant_id"]
ErrorCode = Literal[
    "invalid_plan", "unsupported_operation", "unsupported_parameter", "incompatible_features",
    "clarification_required", "stale_plan", "snapshot_unavailable", "data_unavailable",
    "limit_exceeded", "timeout", "dependency_unavailable", "version_unavailable", "provider_failed",
]
ConversationState = Literal["proposed", "needs_clarification", "ready_for_confirmation", "executing", "completed", "failed"]
HiddenStatus = Literal["suppressed", "unknown", "unavailable", "not_yet_observable", "not_reported"]
HiddenReason = Literal["small_group", "no_evidence", "zero_variance", "coverage_incomplete", "not_reported", "linked_disclosure", "unsupported_evidence"]


Dependencies = Annotated[tuple[Identifier, ...], Field(max_length=3), AfterValidator(unique_sorted)]


class GraduationParameters(Contract):
    """Retain the existing credential-specific and registered-program request."""

    cohort: Cohort
    credential: Literal["B", "A", "C"]
    program: Literal["chemistry_general", "chemistry_family"]


class LegacyRetentionParameters(Contract):
    """Do not advertise dashboard filters on the existing program-retention analysis."""

    cohort: Cohort


class EnrollmentParameters(Contract):
    """Annual enrollment uses certified years across entry cohorts and accepts no override."""


class GroupedParameters(Scope):
    """Select one registered grouping and conservative missing-value policy."""

    grouping: Grouping
    missing_policy: Literal["complete_cases"] = "complete_cases"


class CorrelationParameters(Scope):
    """Represent a fixed Pearson request without grouping or arbitrary transformations."""

    x: Feature
    y: Feature
    method: Literal["pearson"] = "pearson"
    missing_policy: Literal["complete_cases"] = "complete_cases"

    @model_validator(mode="after")
    def distinct_features(self):
        """Reject self-correlation; runtime catalog will validate approved feature pairs."""
        if self.x == self.y:
            raise ValueError("correlation requires distinct features")
        return self


class VariantParameters(Scope):
    """Name only a registered variant, whose evidence availability is checked later."""

    variant_id: Literal["gateway.cohort_completion_c_or_better"]


class StepBase(Contract):
    """Carry a stable ID and an explicit dependency set without exposing intermediate rows."""

    step_id: Identifier
    depends_on: Dependencies = ()


def request_model(name, kind, selector, operation, parameters):
    """Build explicit operation-discriminated schemas from their typed parameter owners."""
    fields = {"kind": (Literal[kind], ...), selector: (Literal[operation], ...), "parameters": (parameters, ...)}
    if kind == "exploratory_analysis":
        fields["dataset_id"] = (Literal["student_year1"], ...)
    return create_model(name, __base__=StepBase, __doc__=f"Typed {operation} request.", **fields)


DEFINED_REQUESTS = [
    request_model("RetentionStep", "defined_measure", "operation_id", "retention.rate", RetentionParameters),
    request_model("PersistenceStep", "defined_measure", "operation_id", "persistence.rate", RateParameters),
    request_model("DfwRateStep", "defined_measure", "operation_id", "dfw.rate", RateParameters),
    request_model("DfwListStep", "defined_measure", "operation_id", "dfw.course_list", Scope),
    request_model("DfwDetailStep", "defined_measure", "operation_id", "dfw.course_detail", CourseParameters),
    request_model("CreditCompletionStep", "defined_measure", "operation_id", "credit_completion.ratio", RateParameters),
    request_model("CreditMomentumStep", "defined_measure", "operation_id", "credit_momentum.summary", RetentionScope),
    request_model("GatewayMathStep", "defined_measure", "operation_id", "gateway.math_completion", RateParameters),
    request_model("GatewayEnglishStep", "defined_measure", "operation_id", "gateway.english_completion", RateParameters),
    request_model("GatewayCoursesStep", "defined_measure", "operation_id", "gateway.course_outcomes", RetentionScope),
    request_model("StudentPathsStep", "defined_measure", "operation_id", "student_paths.summary", PathsParameters),
]
LEGACY_REQUESTS = [
    request_model("GraduationStep", "legacy_analysis", "operation_id", "legacy.graduation", GraduationParameters),
    request_model("EntryMajorRetentionStep", "legacy_analysis", "operation_id", "legacy.entry_major_retention", LegacyRetentionParameters),
    request_model("AnnualEnrollmentStep", "legacy_analysis", "operation_id", "legacy.annual_enrollment", EnrollmentParameters),
]
EXPLORATORY_REQUESTS = [
    request_model("GroupedSummaryStep", "exploratory_analysis", "operation", "grouped_summary", GroupedParameters),
    request_model("MeanComparisonStep", "exploratory_analysis", "operation", "mean_comparison", GroupedParameters),
    request_model("CorrelationStep", "exploratory_analysis", "operation", "correlation", CorrelationParameters),
    request_model("VariantStep", "exploratory_analysis", "operation", "measure_variant", VariantParameters),
]


class _StepJsonSchema:
    """Keep nested operation unions valid in OpenAPI while runtime dispatch still discriminates by kind."""

    @classmethod
    def __get_pydantic_json_schema__(cls, schema, handler):
        """Remove Pydantic's inline-object kind mapping, which OpenAPI requires to contain string refs."""
        result = handler(schema)
        result.pop("discriminator", None)
        return result


def step_union(defined, legacy, exploration):
    """Keep path and operation discriminators visible in JSON Schema."""
    return Annotated[Union[
        Annotated[Union[tuple(defined)], Field(discriminator="operation_id")],
        Annotated[Union[tuple(legacy)], Field(discriminator="operation_id")],
        Annotated[Union[tuple(exploration)], Field(discriminator="operation")],
    ], Field(discriminator="kind"), _StepJsonSchema]


Step = step_union(DEFINED_REQUESTS, LEGACY_REQUESTS, EXPLORATORY_REQUESTS)


class Choice(Contract):
    """Bind an offered scalar value to a human-readable label."""

    value: StrictStr | StrictInt
    label: Text


class UnresolvedChoice(Contract):
    """Represent missing meaning explicitly, with a bounded set of server choices."""

    unresolved: Literal[True]
    question: Text
    choices: Annotated[tuple[Choice, ...], Field(min_length=1, max_length=100)]

    @model_validator(mode="after")
    def unique_choices(self):
        """Avoid ambiguous selection values even when labels differ."""
        if len({c.value for c in self.choices}) != len(self.choices):
            raise ValueError("choice values must be unique")
        return self


class ProposedParameters(Contract):
    """Validate proposed known values and choice options using the executable field types."""

    target: ClassVar[type[Contract]]

    @model_validator(mode="after")
    def valid_options(self):
        """A proposal cannot offer unsupported choices or bypass complete-request validation."""
        pending = False
        for key, field in self.target.model_fields.items():
            value = getattr(self, key)
            if isinstance(value, UnresolvedChoice):
                pending = True
                adapter = TypeAdapter(field.rebuild_annotation())
                for option in value.choices:
                    adapter.validate_python(option.value)
        if not pending:
            self.target.model_validate(self.model_dump(mode="python"))
        return self


def proposal_model(request):
    """Derive partial schemas once, retaining field constraints without weakening executable requests."""
    owner = request.model_fields["parameters"].annotation
    fields = {}
    for key, field in owner.model_fields.items():
        annotation = field.rebuild_annotation()
        if key in ParameterKey.__args__:
            annotation = Union[annotation, UnresolvedChoice]
        fields[key] = (annotation, Field(default=field.default, default_factory=field.default_factory))
    parameters = create_model("Proposed" + request.__name__ + "Parameters", __base__=ProposedParameters,
                              __doc__="Typed known parameters or explicit unresolved choices.", **fields)
    parameters.target = owner
    step_fields = {key: (field.rebuild_annotation(), Field(default=field.default, default_factory=field.default_factory))
                   for key, field in request.model_fields.items() if key != "parameters"}
    step_fields["parameters"] = (parameters, ...)
    return create_model("Proposed" + request.__name__, __base__=StepBase,
                        __doc__="Proposed operation scope; never executable.", **step_fields)


ProposedStep = step_union(*[[proposal_model(r) for r in group]
                           for group in (DEFINED_REQUESTS, LEGACY_REQUESTS, EXPLORATORY_REQUESTS)])


class PlanBase(Contract):
    """Anchor a bounded plan to explicit catalog and snapshot references."""

    catalog_version: Identifier
    snapshot_ref: Identifier

    @model_validator(mode="after")
    def valid_dependencies(self):
        """Require unique IDs and existing dependencies earlier in execution order."""
        ids = [s.step_id for s in self.steps]
        if len(ids) != len(set(ids)):
            raise ValueError("step IDs must be unique")
        seen = set()
        for step in self.steps:
            if not set(step.depends_on) <= seen:
                raise ValueError("dependencies must reference earlier steps; unknown references and cycles are invalid")
            seen.add(step.step_id)
        return self


class ExecutablePlan(PlanBase):
    """Accept only fully resolved operation contracts; catalog availability remains a service check."""

    kind: Literal["executable"]
    steps: Annotated[tuple[Step, ...], Field(min_length=1, max_length=4)]


class ProposedPlan(PlanBase):
    """Keep complete and unresolved steps together until deterministic resolution."""

    kind: Literal["proposed"]
    steps: Annotated[tuple[ProposedStep, ...], Field(min_length=1, max_length=4)]


def to_executable(plan: ProposedPlan) -> ExecutablePlan:
    """Convert only a fully resolved proposal, materializing every typed default."""
    if not isinstance(plan, ProposedPlan):
        raise ValueError("expected ProposedPlan")
    if any(isinstance(getattr(s.parameters, key), UnresolvedChoice)
           for s in plan.steps for key in type(s.parameters).model_fields):
        raise ValueError("plan contains unresolved choices")
    return ExecutablePlan.model_validate({**plan.model_dump(mode="python"), "kind": "executable"})


def resolve_choice(plan: ProposedPlan, step_id: str, parameter: ParameterKey, value: str | int) -> ProposedPlan:
    """Apply one offered choice through a whitelist and revalidate the entire preserved plan."""
    if parameter not in ParameterKey.__args__ or not isinstance(plan, ProposedPlan):
        raise ValueError("invalid clarification reference")
    selected = next((s for s in plan.steps if s.step_id == step_id), None)
    current = getattr(selected.parameters, parameter, None) if selected else None
    if not isinstance(current, UnresolvedChoice) or not any(type(value) is type(c.value) and value == c.value for c in current.choices):
        raise ValueError("select one current offered value for an unresolved parameter")
    raw = plan.model_dump(mode="python")
    for step in raw["steps"]:
        if step["step_id"] == step_id:
            step["parameters"][parameter] = value
    return ProposedPlan.model_validate(raw)


class Exclusion(Contract):
    """Carry one already-disclosed exclusion count with a fixed-form reason ID."""

    reason: Identifier
    count: Count


class CountPayload(Contract):
    """Represent a nonnegative count with its counting unit."""

    kind: Literal["count"]
    count: Count
    unit: Text


class DfwSplit(Contract):
    """Keep the owner's three grade counts immutable and separate from student counts."""

    D: Count
    F: Count
    W: Count


class RateValues(Contract):
    """Validate executed rates while allowing fractional student-ratio numerators."""

    numerator: Annotated[Number, Field(ge=0)]
    denominator: Annotated[Number, Field(gt=0)]
    value: Annotated[Number, Field(ge=0, le=1)]
    numerator_unit: Text
    denominator_unit: Text
    precision: Precision = 4
    n_students: Count | None = None
    n_excluded: Count | None = None
    n_out_of_scope: Count | None = None
    split: DfwSplit | None = None

    @model_validator(mode="after")
    def agrees(self):
        """Reject numerical values inconsistent with the disclosed formula inputs."""
        if self.numerator > self.denominator or self.value != round(self.numerator / self.denominator, self.precision):
            raise ValueError("rate must agree with numerator / denominator")
        if self.split is not None and sum(self.split.model_dump().values()) != self.numerator:
            raise ValueError("DFW split must agree with the numerator")
        return self


class VisibleRateBreakdown(RateValues):
    """Preserve an existing visible categorical row with its own denominator and exclusions."""

    status: Literal["ok", "provisional"]
    group: Filters
    exclusions: Annotated[tuple[Exclusion, ...], Field(max_length=32)] = ()


class HiddenRateBreakdown(Contract):
    """Name a categorical group without exposing any of its hidden numerical inputs."""

    status: HiddenStatus
    reason: HiddenReason
    group: Filters


class RatePayload(RateValues):
    """Carry an overall rate and the explicitly requested categorical breakdown rows."""

    kind: Literal["rate"]
    breakdowns: Annotated[tuple[Annotated[Union[VisibleRateBreakdown, HiddenRateBreakdown], Field(discriminator="status")], ...], Field(max_length=200)] = ()

    @model_validator(mode="after")
    def unique_groups(self):
        """Require distinct nonempty categorical groups rather than duplicating the overall rate."""
        groups = [tuple(sorted(row.group.model_dump(exclude_none=True).items())) for row in self.breakdowns]
        if any(not group for group in groups) or len(groups) != len(set(groups)):
            raise ValueError("breakdowns require unique nonempty groups")
        return self


class MeanPayload(Contract):
    """Represent an executed mean without restricting it to a percentage range."""

    kind: Literal["mean"]
    n: SampleSize
    value: Number
    unit: Text


class GroupMean(Contract):
    """Name one already-visible comparison group and its eligible sample."""

    id: Identifier
    n: SampleSize
    mean: Number


class Difference(Contract):
    """Declare subtraction direction explicitly rather than inferring it from a sign."""

    minuend: Identifier
    subtrahend: Identifier
    value: Number


class ComparisonPayload(Contract):
    """Return descriptive differences only when their visible group evidence is consistent."""

    kind: Literal["mean_comparison"]
    unit: Text
    groups: Annotated[tuple[GroupMean, ...], Field(min_length=2, max_length=20)]
    differences: Annotated[tuple[Difference, ...], Field(min_length=1, max_length=190)]
    precision: Precision = 4

    @model_validator(mode="after")
    def agrees(self):
        """Reject duplicate groups/pairs and differences with missing or reversed inputs."""
        groups = {g.id: g for g in self.groups}
        if len(groups) != len(self.groups):
            raise ValueError("comparison groups must be unique")
        pairs = set()
        for difference in self.differences:
            pair = (difference.minuend, difference.subtrahend)
            if pair in pairs or pair[0] == pair[1] or not set(pair) <= groups.keys():
                raise ValueError("difference needs a unique ordered pair of visible groups")
            pairs.add(pair)
            expected = groups[pair[0]].mean - groups[pair[1]].mean
            if difference.value != round(expected, self.precision):
                raise ValueError("difference must agree with the declared subtraction order")
        return self


class CorrelationPayload(Contract):
    """Carry paired-sample Pearson evidence; zero-variance execution returns unavailable instead."""

    kind: Literal["correlation"]
    method: Literal["pearson"]
    n: Annotated[StrictInt, Field(ge=2)]
    coefficient: Annotated[Number, Field(ge=-1, le=1)]
    x_unit: Text
    y_unit: Text


class TableColumn(Contract):
    """Declare the type and unit of one bounded table column."""

    id: Identifier
    type: Literal["integer", "number", "text"]
    unit: Text


class VisibleTableRow(Contract):
    """Contain typed, already-disclosed cells in declared column order."""

    status: Literal["ok", "provisional"]
    cells: Annotated[tuple[StrictInt | Number | Text | None, ...], Field(max_length=32)]


class HiddenTableRow(Contract):
    """Represent a hidden row with no cells, numerical inputs or formula text."""

    status: HiddenStatus
    path: Text | None = None


class TablePage(Contract):
    """Carry another immutable receipt page without requerying its source."""

    rows: Annotated[tuple[Annotated[Union[VisibleTableRow, HiddenTableRow], Field(discriminator="status")], ...], Field(min_length=1, max_length=200)]


class TablePayload(Contract):
    """Bound heterogeneous page tables and enforce their declared cell types."""

    kind: Literal["table"]
    columns: Annotated[tuple[TableColumn, ...], Field(min_length=1, max_length=32)]
    rows: Annotated[tuple[Annotated[Union[VisibleTableRow, HiddenTableRow], Field(discriminator="status")], ...], Field(max_length=200)]
    pages: Annotated[tuple[TablePage, ...], Field(max_length=63)] = ()

    @model_validator(mode="after")
    def typed_cells(self):
        """Refuse duplicate columns, private identifier columns and incorrectly typed rows."""
        names = [c.id for c in self.columns]
        if len(names) != len(set(names)) or "student_id" in names:
            raise ValueError("columns must be unique and cannot expose student_id")
        if self.pages and (len(self.rows) != 200 or any(len(p.rows) != 200 for p in self.pages[:-1])):
            raise ValueError("only the final receipt page may be shorter than 200 rows")
        for row in (*self.rows, *(row for page in self.pages for row in page.rows)):
            if isinstance(row, HiddenTableRow):
                continue
            if len(row.cells) != len(self.columns):
                raise ValueError("row width differs from columns")
            for column, value in zip(self.columns, row.cells):
                allowed = {"integer": (int,), "number": (int, float), "text": (str,)}[column.type]
                if value is not None and type(value) not in allowed:
                    raise ValueError("cell type differs from column")
        return self


Payload = Annotated[Union[CountPayload, RatePayload, MeanPayload, ComparisonPayload, CorrelationPayload, TablePayload], Field(discriminator="kind")]


class VisibleResult(Contract):
    """Contain only disclosed typed evidence and safe exclusion counts."""

    status: Literal["ok", "provisional"]
    payload: Payload
    exclusions: Annotated[tuple[Exclusion, ...], Field(max_length=32)] = ()


class HiddenResult(Contract):
    """Use a fixed reason code instead of carrying hidden values or unconstrained calculation text."""

    status: HiddenStatus
    reason: HiddenReason


Result = Annotated[Union[VisibleResult, HiddenResult], Field(discriminator="status")]


class VersionReference(Contract):
    """Name a versioned definition or feature without leaking implementation paths."""

    id: Identifier
    version: Identifier


class Source(Contract):
    """Declare synthetic snapshot identity and the coverage represented by its source."""

    label: Literal["synthetic"]
    snapshot_ref: Identifier
    fingerprint: Fingerprint
    loaded_at: AwareDatetime
    coverage: Text


class Versions(Contract):
    """Record computation inputs separately from the unique execution identity."""

    catalog: Identifier
    pipeline: Identifier
    configuration: Identifier
    coverage: Identifier
    implementation: Identifier
    disclosure: Identifier
    features: Annotated[tuple[VersionReference, ...], Field(max_length=16)] = ()
    method: VersionReference | None = None


def operation_id(request) -> str:
    """Read the operation selector for either a defined/legacy or exploratory step."""
    return request.operation if request.kind == "exploratory_analysis" else request.operation_id


RESULT_KINDS = {
    "retention.rate": "rate", "persistence.rate": "rate", "dfw.rate": "rate",
    "credit_completion.ratio": "rate", "gateway.math_completion": "rate", "gateway.english_completion": "rate",
    "dfw.course_list": "table", "dfw.course_detail": "table", "credit_momentum.summary": "table",
    "gateway.course_outcomes": "table", "student_paths.summary": "table",
    "legacy.graduation": "table", "legacy.entry_major_retention": "table", "legacy.annual_enrollment": "table",
    "grouped_summary": "table", "mean_comparison": "mean_comparison", "correlation": "correlation", "measure_variant": "rate",
}


class Receipt(Contract):
    """Bind one safely projected result to its canonical executed scope and provenance."""

    schema_version: Literal[2]
    step_id: Identifier
    request: Step
    operation_id: Identifier
    operation_version: Identifier
    disclosure_profile: VersionReference | None = None
    population: Text
    time_window: Text
    grain: Text
    definitions: Annotated[tuple[VersionReference, ...], Field(min_length=1, max_length=16)]
    baseline_changes: Annotated[tuple[Text, ...], Field(max_length=16)] = ()
    assumptions: Annotated[tuple[Text, ...], Field(max_length=16)] = ()
    limitations: Annotated[tuple[Text, ...], Field(max_length=16)] = ()
    source: Source
    versions: Versions
    computation_fingerprint: Fingerprint
    execution_id: Identifier
    started_at: AwareDatetime
    completed_at: AwareDatetime
    result: Result

    @model_validator(mode="after")
    def bound_evidence(self):
        """Reject receipt identity mismatches and impossible execution intervals."""
        if self.step_id != self.request.step_id or self.operation_id != operation_id(self.request):
            raise ValueError("receipt identity differs from executed request")
        if self.completed_at < self.started_at:
            raise ValueError("completion precedes execution start")
        if isinstance(self.result, VisibleResult) and self.result.payload.kind != RESULT_KINDS[self.operation_id]:
            raise ValueError("result payload kind differs from the requested operation")
        if isinstance(self.result, VisibleResult) and isinstance(self.result.payload, RatePayload):
            requested = set(getattr(self.request.parameters, "group_by", ()))
            for row in self.result.payload.breakdowns:
                if set(row.group.model_dump(exclude_none=True)) != requested:
                    raise ValueError("rate breakdown scope differs from the requested grouping")
        feature_ids = [v.id for v in self.versions.features]
        if len(feature_ids) != len(set(feature_ids)):
            raise ValueError("feature versions must be unique")
        if self.request.kind == "exploratory_analysis" and isinstance(self.result, VisibleResult):
            method = "pearson" if self.request.operation == "correlation" else self.request.operation
            if self.versions.method is None or self.versions.method.id != method:
                raise ValueError("visible exploration requires its executed method version")
            if self.request.operation == "correlation" and not {self.request.parameters.x, self.request.parameters.y} <= set(feature_ids):
                raise ValueError("correlation requires both feature versions")
        return self


class AnalysisIssue(Contract):
    """Return a bounded application-generated issue, never a raw provider/database exception."""

    code: ErrorCode
    step_id: Identifier | None = None
    message: Text


class StepOutcome(Contract):
    """Distinguish completed evidence, failed execution and work that never ran."""

    step_id: Identifier
    outcome: Literal["completed", "failed", "not_executed"]
    issue: AnalysisIssue | None = None

    @model_validator(mode="after")
    def issue_matches(self):
        """Require failure context for uncompleted steps and bind it to the same ID."""
        if self.outcome == "completed" and self.issue is not None:
            raise ValueError("completed step has no execution failure")
        if self.outcome != "completed" and (self.issue is None or self.issue.step_id != self.step_id):
            raise ValueError("uncompleted step needs its own issue")
        return self


class Clarification(Contract):
    """Reference one current unresolved parameter without arbitrary dotted paths."""

    step_id: Identifier
    parameter: ParameterKey
    question: Text
    choices: Annotated[tuple[Choice, ...], Field(min_length=1, max_length=100)]


class AnalysisResponseV2(Contract):
    """Keep transport status, per-step execution outcomes and evidence mutually consistent."""

    protocol_version: Literal[2]
    status: Literal["clarification", "confirmation", "answer", "unsupported", "error"]
    plan: Annotated[Union[ProposedPlan, ExecutablePlan], Field(discriminator="kind")] | None = None
    outcome: Literal["complete", "partial", "failed"] | None = None
    step_outcomes: Annotated[tuple[StepOutcome, ...], Field(max_length=4)] = ()
    clarification: Clarification | None = None
    receipts: Annotated[tuple[Receipt, ...], Field(max_length=4)] = ()
    issues: Annotated[tuple[AnalysisIssue, ...], Field(max_length=16)] = ()
    message: Text

    @model_validator(mode="after")
    def consistent_state(self):
        """Require the exact plan/evidence set and truthful partial-success status."""
        ids = [s.step_id for s in self.plan.steps] if self.plan else []
        if self.plan is not None and any(i.step_id is not None and i.step_id not in ids for i in self.issues):
            raise ValueError("issue references an unknown plan step")
        if self.outcome is None:
            if self.receipts or self.step_outcomes or self.status == "answer":
                raise ValueError("unexecuted response cannot contain execution evidence")
            if self.status == "confirmation" and not isinstance(self.plan, ExecutablePlan):
                raise ValueError("confirmation requires ExecutablePlan")
            if self.status == "error" and not self.issues:
                raise ValueError("pre-execution error requires a typed issue")
            if self.status == "clarification":
                if not isinstance(self.plan, ProposedPlan) or self.clarification is None:
                    raise ValueError("clarification requires a complete ProposedPlan and choice reference")
                ref = self.clarification
                step = next((s for s in self.plan.steps if s.step_id == ref.step_id), None)
                pending = getattr(step.parameters, ref.parameter, None) if step else None
                if not isinstance(pending, UnresolvedChoice) or (ref.question, ref.choices) != (pending.question, pending.choices):
                    raise ValueError("clarification differs from current plan choices")
            elif self.clarification is not None:
                raise ValueError("clarification belongs only to a clarification response")
            return self
        if not isinstance(self.plan, ExecutablePlan) or self.clarification is not None:
            raise ValueError("execution requires ExecutablePlan without clarification")
        if [s.step_id for s in self.step_outcomes] != ids:
            raise ValueError("ordered outcomes must cover every plan step")
        completed = [s.step_id for s in self.step_outcomes if s.outcome == "completed"]
        if [r.step_id for r in self.receipts] != completed:
            raise ValueError("receipts must cover exactly the completed steps in order")
        expected = "complete" if len(completed) == len(ids) else "partial" if completed else "failed"
        if self.outcome != expected or self.status != ("answer" if completed else "error"):
            raise ValueError("aggregate outcome/status disagrees with executed steps")
        steps = {s.step_id: s for s in self.plan.steps}
        for receipt in self.receipts:
            if (receipt.request != steps[receipt.step_id] or receipt.source.snapshot_ref != self.plan.snapshot_ref
                    or receipt.versions.catalog != self.plan.catalog_version):
                raise ValueError("receipt scope/source/catalog differs from confirmed plan")
        outcomes = {s.step_id: s for s in self.step_outcomes}
        receipts = {r.step_id: r for r in self.receipts}
        for step in self.plan.steps:
            unusable = any(outcomes[d].outcome != "completed" or isinstance(receipts[d].result, HiddenResult)
                           for d in step.depends_on)
            if unusable:
                state = outcomes[step.step_id]
                if state.outcome != "not_executed" or state.issue.code != "dependency_unavailable":
                    raise ValueError("a step without usable dependency evidence must not execute")
        return self


def canonical_json(model: Contract) -> str:
    """Serialize all resolved defaults with stable object-key order and meaningful array order."""
    return json.dumps(model.model_dump(mode="json"), sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
