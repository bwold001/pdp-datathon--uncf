"""Single-operation catalog and v2 result adapters; calculation formulas remain with their owners."""

import re
from typing import Annotated

from pydantic import Field, TypeAdapter, ValidationError

from analytics.contracts_v2 import (
    Contract,
    HiddenResult,
    HiddenTableRow,
    Identifier,
    RatePayload,
    Result,
    Step,
    TableColumn,
    TablePayload,
    Text,
    VisibleResult,
    VisibleTableRow,
)
from analytics.execution import check_cancelled
from analytics.legacy_operations import LEGACY_IDS
from analytics.legacy_operations import OPERATIONS as LEGACY_OPERATIONS
from analytics.schemas import AnalysisRequest
from analytics.service import AnalyticsService
from gap_finder.gateway import add_gateway_gaps
from measures import service as measures_service
from measures.breakdowns.dfw_courses import UnknownCourse
from measures.models import MeasureResult
from measures.registry import CATALOG_VERSION
from measures.registry import OPERATIONS as DEFINED_OPERATIONS
from measures.requests import Filters

_STEP = TypeAdapter(Step)
_HIDDEN_REASONS = {
    "suppressed": "small_group",
    "unknown": "no_evidence",
    "unavailable": "no_evidence",
    "not_yet_observable": "coverage_incomplete",
    "not_reported": "not_reported",
}


class OperationError(ValueError):
    """Carry a safe typed refusal before transport-specific response assembly."""

    def __init__(self, code, message):
        """Keep raw validation and database details out of public messages."""
        self.code = code
        super().__init__(message)


class OperationEvidence(Contract):
    """Stage typed result evidence for later plan-wide disclosure and receipt assembly."""

    operation_id: Identifier
    operation_version: Identifier
    result: Result
    context: Annotated[tuple[Text, ...], Field(max_length=32)] = ()


def _hidden(status):
    """Map an owner status to a payload with no numerical inputs or calculation text."""
    return HiddenResult(status=status, reason=_HIDDEN_REASONS[status])


def _rate_values(row: MeasureResult, spec):
    """Copy arithmetic and counting units from a disclosed owner row without recalculation."""
    return {
        "numerator": float(row.numerator),
        "denominator": float(row.denominator),
        "value": float(row.metric_rate),
        "numerator_unit": spec.units[0],
        "denominator_unit": spec.units[1],
        "n_students": row.n_students,
        "n_excluded": row.n_excluded,
        "n_out_of_scope": row.n_out_of_scope,
        "split": row.split,
    }


def _row_status(row, spec, provisional):
    """Keep dashboard gateway nonreporting distinct from an unobservable follow-up window."""
    if row.status.value == "not_yet_observable" and spec.id.startswith("gateway."):
        return "not_reported"
    if row.status.value == "ok" and provisional:
        return "provisional"
    return row.status.value


def _exclusions(row):
    """Copy only already-disclosed owner exclusion counts in deterministic order."""
    return tuple(
        {"reason": key.value, "count": value}
        for key, value in sorted(row.exclusions.items(), key=lambda pair: pair[0].value)
    )


def _scalar_result(rows, spec, provisional):
    """Project the overall and requested group rows without changing their populations."""
    first, *groups = rows
    status = _row_status(first, spec, provisional)
    if status not in ("ok", "provisional"):
        return _hidden(status)
    breakdowns = []
    for row in groups:
        check_cancelled()
        group = Filters.model_validate(
            {part.dimension.value: part.value for part in row.group.parts}
        )
        group_status = _row_status(row, spec, provisional)
        if group_status in ("ok", "provisional"):
            breakdowns.append(
                {
                    "status": group_status,
                    "group": group,
                    **_rate_values(row, spec),
                    "exclusions": _exclusions(row),
                }
            )
        else:
            breakdowns.append(
                {
                    "status": group_status,
                    "group": group,
                    "reason": _HIDDEN_REASONS[group_status],
                }
            )
    if len(breakdowns) > 200:
        raise OperationError(
            "limit_exceeded",
            "The requested breakdown exceeds the result limit; narrow the scope.",
        )
    return VisibleResult(
        status=status,
        payload=RatePayload(
            kind="rate", **_rate_values(first, spec), breakdowns=breakdowns
        ),
        exclusions=_exclusions(first),
    )


def _unit(operation, path):
    """Label copied page fields using their component context, never one shared denominator."""
    field = path.rsplit(".", 1)[-1]
    if (
        field in ("rate", "others_rate", "rest_rate", "ratio", "share", "shares")
        or ".shares." in path
    ):
        return "ratio"
    if field == "gap":
        return "percentage points"
    if field in (
        "credits",
        "avg_attempted",
        "avg_earned",
        "minimum",
        "degree_credits",
        "pace",
        "higher_degree_credits",
        "higher_pace",
    ) and ("settings" in path or field.startswith("avg_") or field == "credits"):
        return "credits"
    if field in ("position", "from_position", "to_position"):
        return "term position"
    if "settings.years" in path:
        return "years"
    if operation.startswith("dfw.") and (
        field in ("num", "den", "total", "D", "F", "W", "DF") or ".gateway." in path
    ):
        return "course enrollments"
    if field == "distinct" and ".names." in "." + path:
        return "course names"
    if field == "hidden_courses":
        return "courses"
    if field == "pairs_considered":
        return "course pairs"
    return "students"


def _page_result(page, operation, provisional):
    """Represent all aggregate page leaves as bounded typed cells; never embed arbitrary JSON."""
    status = page.get("status", "ok")
    if status not in ("ok", "provisional"):
        return _hidden(status)
    visible_status = "provisional" if provisional else "ok"
    rows = []

    def append(row):
        """Refuse oversized pages as a whole instead of silently dropping components."""
        if len(rows) >= 200:
            raise OperationError(
                "limit_exceeded", "The page exceeds the result limit; narrow the scope."
            )
        rows.append(row)

    def visit(value, path):
        """Copy the trusted aggregate owner tree, preserving order and explicit hidden states."""
        check_cancelled()
        if isinstance(value, (dict, list, tuple)) and not value:
            append(
                VisibleTableRow(
                    status=visible_status,
                    cells=(path, None, "no entries", "empty collection"),
                )
            )
            return
        if isinstance(value, dict):
            if "student_id" in value:
                raise OperationError(
                    "invalid_plan",
                    "The calculation returned an unsupported result shape.",
                )
            if value.get("status") in _HIDDEN_REASONS:
                append(HiddenTableRow(status=value["status"]))
                return
            if value.get("status") == "hidden":
                append(HiddenTableRow(status="suppressed"))
                return
            for key, child in value.items():
                if key != "status":
                    visit(child, f"{path}.{key}" if path else key)
        elif isinstance(value, (list, tuple)):
            for index, child in enumerate(value):
                visit(child, f"{path}[{index}]")
        elif value is None:
            append(HiddenTableRow(status="unknown"))
        else:
            number = value if type(value) in (int, float) else None
            text = None
            if isinstance(value, bool):
                text = str(value).lower()
            elif isinstance(value, str):
                text = value
            if number is None and text is None:
                raise OperationError(
                    "invalid_plan",
                    "The calculation returned an unsupported result shape.",
                )
            append(
                VisibleTableRow(
                    status=visible_status,
                    cells=(
                        path,
                        number,
                        text,
                        _unit(operation, path) if number is not None else "label",
                    ),
                )
            )

    visit(page, "")
    return VisibleResult(
        status=visible_status,
        payload=TablePayload(
            kind="table",
            columns=(
                TableColumn(id="component", type="text", unit="owner component path"),
                TableColumn(id="number", type="number", unit="specified by row unit"),
                TableColumn(id="text", type="text", unit="label"),
                TableColumn(id="unit", type="text", unit="counting unit"),
            ),
            rows=rows,
        ),
    )


def _legacy_result(receipt):
    """Keep legacy perspectives, horizons, group scopes, exclusions and hidden statuses explicit."""
    rows = []
    for row in receipt.rows:
        check_cancelled()
        if row.status not in ("ok", "provisional"):
            rows.append(HiddenTableRow(status=row.status))
            continue
        group = (
            ", ".join(f"{key}={value}" for key, value in sorted(row.group.items()))
            or "overall"
        )
        rows.append(
            VisibleTableRow(
                status=row.status,
                cells=(
                    row.label,
                    row.kind,
                    row.horizon,
                    group,
                    row.numerator,
                    row.denominator,
                    row.count,
                    row.rate,
                    row.note or None,
                ),
            )
        )
        for key, count in sorted(row.exclusions.items()):
            rows.append(
                VisibleTableRow(
                    status=row.status,
                    cells=(
                        row.label,
                        "exclusion",
                        row.horizon,
                        key,
                        None,
                        None,
                        count,
                        None,
                        None,
                    ),
                )
            )
    if len(rows) > 200:
        raise OperationError(
            "limit_exceeded",
            "The legacy analysis exceeds the result limit; narrow the scope.",
        )
    if not rows:
        return _hidden("unavailable")
    columns = [
        ("label", "text", "perspective"),
        ("kind", "text", "result kind"),
        ("horizon", "text", "follow-up window"),
        ("group", "text", "program/year/ethnicity or exclusion reason"),
        ("numerator", "integer", "students"),
        ("denominator", "integer", "eligible students for this perspective"),
        ("count", "integer", "students"),
        ("rate", "number", "ratio"),
        ("note", "text", "limitation"),
    ]
    status = (
        "provisional" if any(r.status == "provisional" for r in receipt.rows) else "ok"
    )
    return VisibleResult(
        status=status,
        payload=TablePayload(
            kind="table",
            columns=[
                TableColumn(id=id, type=type, unit=unit) for id, type, unit in columns
            ],
            rows=rows,
        ),
    )


def legacy_step(request: AnalysisRequest | dict, step_id="legacy"):
    """Map a fully resolved old request without changing its horizons, program or credential."""
    request = AnalysisRequest.model_validate(request)
    id = next(id for id, name in LEGACY_IDS.items() if name == request.analysis)
    parameters = request.model_dump(exclude_none=True, exclude={"analysis"})
    return _STEP.validate_python(
        {
            "kind": "legacy_analysis",
            "operation_id": id,
            "step_id": step_id,
            "parameters": parameters,
        }
    )


class AnalysisService:
    """Expose a small searchable catalog and execute one validated existing operation."""

    def __init__(self, coverage):
        """Use explicit coverage while borrowing all execution snapshots from the caller."""
        self.coverage = coverage
        self.operations = {**DEFINED_OPERATIONS, **LEGACY_OPERATIONS}

    def catalog(self, query=None):
        """Return compact candidates and distinctions without choosing a definition for the user."""
        tokens = set(re.findall(r"\w+", (query or "").lower()))
        candidates = []
        for spec in self.operations.values():
            words = set(
                re.findall(
                    r"\w+",
                    " ".join(
                        (spec.id, spec.label, spec.purpose, *spec.aliases)
                    ).lower(),
                )
            )
            if not tokens or tokens & words:
                candidates.append(spec.compact())
        return {"version": CATALOG_VERSION, "operations": candidates}

    def details(self, operation_id):
        """Return full metadata only for a registered candidate."""
        if not isinstance(operation_id, str) or operation_id not in self.operations:
            raise OperationError(
                "unsupported_operation", "The requested operation is not registered."
            )
        return self.operations[operation_id].details()

    def execute(self, step, snapshot):
        """Validate before reading, dispatch once and stage typed v2 evidence on the borrowed source."""
        raw = step.model_dump(mode="python") if isinstance(step, Contract) else step
        if (
            not isinstance(raw, dict)
            or not isinstance(raw.get("operation_id"), str)
            or raw["operation_id"] not in self.operations
        ):
            raise OperationError(
                "unsupported_operation", "The requested operation is not registered."
            )
        spec = self.operations[raw["operation_id"]]
        try:
            step = _STEP.validate_python(raw)
            if step.kind != spec.kind:
                raise ValueError("wrong operation kind")
            spec.parameters.model_validate(step.parameters.model_dump())
        except (ValidationError, ValueError) as error:
            raise OperationError(
                "unsupported_parameter",
                "The operation parameters are invalid or unsupported.",
            ) from error
        check_cancelled()
        if spec.kind == "defined_measure":
            try:
                owner_result = measures_service.execute(
                    spec.id, step.parameters, snapshot
                )
            except UnknownCourse:
                return OperationEvidence(
                    operation_id=spec.id,
                    operation_version=spec.version,
                    result=_hidden("unavailable"),
                    context=spec.component_denominators,
                )
            if spec.id == "gateway.course_outcomes":
                owner_result = add_gateway_gaps(owner_result)
            provisional = (
                step.parameters.cohort in self.coverage.provisional_retention_cohorts
            )
            if spec.measure is not None:
                provisional = provisional and spec.id in (
                    "retention.rate",
                    "persistence.rate",
                )
                result = _scalar_result(owner_result, spec, provisional)
            else:
                result = _page_result(owner_result, spec.id, provisional)
            context = spec.component_denominators
        else:
            request = AnalysisRequest(
                analysis=LEGACY_IDS[spec.id], **step.parameters.model_dump()
            )
            response = (
                AnalyticsService(None, self.coverage)
                .for_snapshot(snapshot)
                .analyze(request)
            )
            if response.clarification or len(response.receipts) != 1:
                raise OperationError(
                    "clarification_required",
                    "The legacy operation requires a resolved supported scope.",
                )
            receipt = response.receipts[0]
            result = _legacy_result(receipt)
            context = tuple(
                value
                for value in (
                    receipt.program_definition,
                    receipt.attribution,
                    receipt.cutoff,
                    receipt.coverage_provenance,
                    *receipt.academic_years,
                    *receipt.limitations,
                )
                if value
            )
        check_cancelled()
        return OperationEvidence(
            operation_id=spec.id,
            operation_version=spec.version,
            result=result,
            context=context,
        )
