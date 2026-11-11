"""Independent examples and refusal cases for the inactive v2 boundary."""

import copy
import json
from pathlib import Path

import pytest
from pydantic import TypeAdapter, ValidationError

from analytics.contracts_v2 import (
    AnalysisResponseV2, ExecutablePlan, ProposedPlan, Receipt, Result, TablePayload,
    canonical_json, resolve_choice, to_executable,
)


def step(step_id="dfw", **changes):
    """Build a Pell-filtered defined request with independently stated scope."""
    return {"step_id": step_id, "kind": "defined_measure", "operation_id": "dfw.rate",
            "parameters": {"cohort": "2023-24", "filters": {"pell": "Y"}}, **changes}


def plan(*steps):
    """Build an executable plan with explicit catalog and source references."""
    return {"kind": "executable", "catalog_version": "1", "snapshot_ref": "fixture-1",
            "steps": list(steps or (step(),))}


def unresolved():
    """Offer two explicit cohort choices instead of an untyped missing value."""
    return {"unresolved": True, "question": "Which cohort?", "choices": [
        {"value": "2022-23", "label": "2022-23"}, {"value": "2023-24", "label": "2023-24"}]}


def receipt(request=None, result=None):
    """Supply explicit synthetic provenance without claiming a real data snapshot."""
    return {"schema_version": 2, "step_id": "dfw", "request": request or step(),
            "operation_id": "dfw.rate", "operation_version": "1",
            "population": "Pell recipients in the selected cohort", "time_window": "Observed course records",
            "grain": "course enrollment", "definitions": [{"id": "dfw.rate", "version": "1"}],
            "source": {"label": "synthetic", "snapshot_ref": "fixture-1", "fingerprint": "a" * 64,
                       "loaded_at": "2026-11-10T12:00:00Z", "coverage": "Hand-counted fixture"},
            "versions": {"catalog": "1", "pipeline": "1", "configuration": "1", "coverage": "1",
                         "implementation": "1", "disclosure": "dashboard_v1"},
            "computation_fingerprint": "b" * 64, "execution_id": "execution-1",
            "started_at": "2026-11-10T12:00:00Z", "completed_at": "2026-11-10T12:00:01Z",
            "result": result or {"status": "ok", "payload": {"kind": "rate", "numerator": 10,
                        "denominator": 20, "value": .5, "numerator_unit": "DFW enrollments",
                        "denominator_unit": "classifiable enrollments"}}}


def test_proposals_require_explicit_choices_and_cannot_execute():
    """Only a fully resolved proposal can be converted; null is not a choice."""
    pending = step(parameters={"cohort": unresolved(), "filters": {"pell": "Y"}})
    proposal = ProposedPlan.model_validate({**plan(pending), "kind": "proposed"})
    with pytest.raises(ValueError, match="unresolved"):
        to_executable(proposal)
    with pytest.raises(ValidationError):
        ExecutablePlan.model_validate(proposal.model_dump(mode="json"))
    with pytest.raises(ValidationError):
        ProposedPlan.model_validate({**plan(step(parameters={"cohort": None})), "kind": "proposed"})


def test_clarification_preserves_other_steps_and_is_deeply_immutable():
    """Resolving one parameter keeps a second pending step and all known filters."""
    pending = step(parameters={"cohort": unresolved(), "filters": {"pell": "Y"}})
    other = step("other", parameters={"cohort": unresolved(), "filters": {"gender": "F"}})
    proposal = ProposedPlan.model_validate({**plan(pending, other), "kind": "proposed"})
    resolved = resolve_choice(proposal, "dfw", "cohort", "2023-24")
    assert resolved.steps[1] == proposal.steps[1]
    assert resolved.steps[0].parameters.filters.pell == "Y"
    with pytest.raises(ValueError):
        resolve_choice(proposal, "dfw", "parameters.cohort", "2023-24")
    with pytest.raises(ValueError):
        resolve_choice(proposal, "dfw", "cohort", "2020-21")
    complete = resolve_choice(resolved, "other", "cohort", "2022-23")
    executed = to_executable(complete)
    assert isinstance(executed.steps, tuple)
    with pytest.raises(ValidationError):
        executed.steps[0].parameters.filters.pell = "N"
    assert proposal.steps[0].parameters.cohort.unresolved is True


@pytest.mark.parametrize("steps", [
    [step(), step()], [step(depends_on=["missing"])], [step(depends_on=["dfw"])],
    [step(depends_on=["later"]), step("later", depends_on=["dfw"])],
    [step(str(i)) for i in range(5)],
])
def test_plan_refuses_duplicates_unknown_dependencies_cycles_and_limits(steps):
    """A whole plan must be valid and dependency-ordered before execution."""
    with pytest.raises(ValidationError):
        ExecutablePlan.model_validate(plan(*steps))


@pytest.mark.parametrize("raw_request", [
    step(operation_id="arbitrary.sql"), step(sql="SELECT 1"),
    step(parameters={"cohort": "2023-25"}),
    step(parameters={"cohort": "2023-24", "filters": {"pell": "maybe"}}),
    step(parameters={"cohort": "2023-24", "group_by": ["pell", "pell"]}),
    step(operation_id="dfw.course_detail", parameters={"cohort": "2023-24"}),
    step(operation_id="credit_momentum.summary", parameters={"cohort": "2023-24", "group_by": ["pell"]}),
])
def test_defined_requests_refuse_unsupported_and_incomplete_scope(raw_request):
    """Operation contracts advertise only their own parameters and required choices."""
    with pytest.raises(ValidationError):
        ExecutablePlan.model_validate(plan(raw_request))


def test_exploration_schema_and_runtime_refuse_wrong_operation_parameters():
    """Correlation has neither grouping nor arbitrary methods; comparison needs a grouping."""
    request = {"step_id": "online", "kind": "exploratory_analysis", "dataset_id": "student_year1",
               "operation": "correlation", "parameters": {"cohort": "2023-24",
               "x": "online_enrollment_count_y1", "y": "credits_earned_y1"}}
    assert ExecutablePlan.model_validate(plan(request)).steps[0].parameters.method == "pearson"
    for changes in ({"grouping": "retention_outcome_school"}, {"method": "spearman"}, {"sql": "x"}):
        bad = copy.deepcopy(request)
        bad["parameters"].update(changes)
        with pytest.raises(ValidationError):
            ExecutablePlan.model_validate(plan(bad))
    bad = {**request, "operation": "mean_comparison", "parameters": {"cohort": "2023-24"}}
    with pytest.raises(ValidationError):
        ExecutablePlan.model_validate(plan(bad))
    schemas = ExecutablePlan.model_json_schema()["$defs"]
    assert schemas["CorrelationParameters"]["additionalProperties"] is False
    assert "grouping" not in schemas["CorrelationParameters"]["properties"]
    assert "grouping" in schemas["GroupedParameters"]["required"]


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf"), "0.5", True])
def test_results_refuse_nonfinite_or_coerced_numbers(value):
    """Numerical evidence must be finite numbers, not strings or booleans."""
    raw = receipt()
    raw["result"]["payload"]["value"] = value
    with pytest.raises(ValidationError):
        Receipt.model_validate(raw)


def test_visible_results_preserve_fractional_and_negative_evidence():
    """V2 arithmetic checks support credit ratios, negative means and correlations."""
    fractional = receipt(request=step(operation_id="credit_completion.ratio"), result={"status": "ok",
        "payload": {"kind": "rate", "numerator": 5.5, "denominator": 10, "value": .55,
                    "numerator_unit": "student ratios", "denominator_unit": "students"}})
    fractional.update(operation_id="credit_completion.ratio", grain="student/cohort")
    assert Receipt.model_validate(fractional).result.payload.numerator == 5.5
    for payload in (
        {"kind": "mean", "n": 10, "value": -12.5, "unit": "credits"},
        {"kind": "correlation", "method": "pearson", "n": 10, "coefficient": -1,
         "x_unit": "enrollments", "y_unit": "credits"},
    ):
        assert TypeAdapter(Result).validate_python({"status": "ok", "payload": payload}).payload
    raw = receipt()
    raw["result"]["payload"]["value"] = .56
    with pytest.raises(ValidationError):
        Receipt.model_validate(raw)


@pytest.mark.parametrize("status", ["suppressed", "unknown", "unavailable", "not_yet_observable", "not_reported"])
def test_hidden_results_cannot_carry_numbers_or_formula_text(status):
    """Hidden evidence has a fixed reason code and no payload or exclusions."""
    safe = {"status": status, "reason": "no_evidence"}
    assert TypeAdapter(Result).validate_python(safe).status == status
    for extra in ({"payload": {"kind": "count", "count": 1, "unit": "students"}},
                  {"exclusions": [{"reason": "missing", "count": 1}]}, {"calculation": "1/2"}):
        with pytest.raises(ValidationError):
            TypeAdapter(Result).validate_python({**safe, **extra})


def test_comparison_order_and_table_cells_are_checked():
    """A comparison must reference visible inputs in declared order; table cells have column types."""
    comparison = {"kind": "mean_comparison", "unit": "credits", "groups": [
        {"id": "retained", "n": 10, "mean": 30}, {"id": "not_retained", "n": 10, "mean": 10}],
        "differences": [{"minuend": "not_retained", "subtrahend": "retained", "value": -20}]}
    assert TypeAdapter(Result).validate_python({"status": "ok", "payload": comparison})
    comparison["differences"][0]["value"] = 20
    with pytest.raises(ValidationError):
        TypeAdapter(Result).validate_python({"status": "ok", "payload": comparison})
    table = {"kind": "table", "columns": [{"id": "count", "type": "integer", "unit": "students"}],
             "rows": [{"status": "ok", "cells": [10]}, {"status": "suppressed"}]}
    assert TablePayload.model_validate(table)
    for cells in (["10"], [True], [10, 20]):
        bad = copy.deepcopy(table)
        bad["rows"][0]["cells"] = cells
        with pytest.raises(ValidationError):
            TablePayload.model_validate(bad)
    table["rows"][1]["cells"] = [1]
    with pytest.raises(ValidationError):
        TablePayload.model_validate(table)


def test_response_outcomes_match_plan_receipts_and_failed_steps():
    """Partial success cannot masquerade as complete or lose a failed step."""
    raw = {"protocol_version": 2, "status": "answer", "plan": plan(step(), step("other")),
           "outcome": "partial", "step_outcomes": [{"step_id": "dfw", "outcome": "completed"},
               {"step_id": "other", "outcome": "failed", "issue": {"code": "timeout", "step_id": "other", "message": "Timed out"}}],
           "receipts": [receipt()], "message": "One step failed."}
    assert AnalysisResponseV2.model_validate(raw).outcome == "partial"
    for changes in ({"outcome": "complete"}, {"receipts": []}, {"step_outcomes": raw["step_outcomes"][:1]}):
        with pytest.raises(ValidationError):
            AnalysisResponseV2.model_validate({**raw, **changes})
    bad = copy.deepcopy(raw)
    bad["receipts"][0]["request"]["parameters"]["filters"]["pell"] = "N"
    with pytest.raises(ValidationError):
        AnalysisResponseV2.model_validate(bad)


def test_canonical_json_materializes_defaults_and_preserves_step_order():
    """Equivalent filter key order serializes identically without reordering steps."""
    a = ExecutablePlan.model_validate(plan(step(parameters={"cohort": "2023-24", "filters": {"pell": "Y", "gender": "F"}})))
    b = ExecutablePlan.model_validate(plan(step(parameters={"filters": {"gender": "F", "pell": "Y"}, "cohort": "2023-24"})))
    assert canonical_json(a) == canonical_json(b)
    assert "group_by" in json.loads(canonical_json(a))["steps"][0]["parameters"]
    both = ExecutablePlan.model_validate(plan(step(), step("other", depends_on=["dfw"])))
    assert [s["step_id"] for s in json.loads(canonical_json(both))["steps"]] == ["dfw", "other"]


def test_future_client_fixtures_round_trip():
    """Committed JSON examples can be consumed by a later TypeScript implementation."""
    examples = json.loads((Path(__file__).parent / "fixtures/contracts_v2.json").read_text())
    for raw in examples:
        parsed = AnalysisResponseV2.model_validate(raw)
        assert AnalysisResponseV2.model_validate_json(canonical_json(parsed)) == parsed


@pytest.mark.parametrize("operation,parameters", [
    ("retention.rate", {"retention_type": "federal"}), ("persistence.rate", {}), ("dfw.rate", {}),
    ("dfw.course_list", {}), ("dfw.course_detail", {"course": "ENG 101"}),
    ("credit_completion.ratio", {}), ("credit_momentum.summary", {"retention_type": "school"}),
    ("gateway.math_completion", {}), ("gateway.english_completion", {}),
    ("gateway.course_outcomes", {"retention_type": "school"}),
    ("student_paths.summary", {"retention_type": "federal", "terms": 6, "group_by": "pell"}),
])
def test_every_defined_contract_has_a_valid_request(operation, parameters):
    """Exercise every initial defined operation without executing a calculation."""
    parsed = ExecutablePlan.model_validate(plan(step(operation_id=operation, parameters={"cohort": "2023-24", **parameters})))
    assert parsed.steps[0].operation_id == operation


@pytest.mark.parametrize("operation,parameters", [
    ("legacy.graduation", {"cohort": "2023-24", "credential": "B", "program": "chemistry_general"}),
    ("legacy.entry_major_retention", {"cohort": "2023-24"}), ("legacy.annual_enrollment", {}),
])
def test_legacy_contracts_do_not_widen_v1_requests(operation, parameters):
    """Legacy adapters retain their distinct parameter domains."""
    raw = step(kind="legacy_analysis", operation_id=operation, parameters=parameters)
    assert ExecutablePlan.model_validate(plan(raw))
    raw["parameters"] = {**parameters, "filters": {"pell": "Y"}}
    with pytest.raises(ValidationError):
        ExecutablePlan.model_validate(plan(raw))


def test_proposed_options_must_match_the_operation_field_type():
    """Invalid cohort options and retention choices cannot be offered for confirmation."""
    choice = unresolved()
    choice["choices"][0]["value"] = "2023-25"
    with pytest.raises(ValidationError):
        ProposedPlan.model_validate({**plan(step(parameters={"cohort": choice})), "kind": "proposed"})
    raw = step(operation_id="retention.rate", parameters={"cohort": "2023-24", "retention_type": unresolved()})
    with pytest.raises(ValidationError):
        ProposedPlan.model_validate({**plan(raw), "kind": "proposed"})


def test_receipt_rejects_wrong_payload_identity_and_time_order():
    """Correct numbers alone do not make a receipt valid for another operation or run."""
    for update in ({"step_id": "other"}, {"operation_id": "retention.rate"},
                   {"completed_at": "2026-11-09T12:00:00Z"},
                   {"result": {"status": "ok", "payload": {"kind": "mean", "n": 10, "value": 20, "unit": "credits"}}}):
        with pytest.raises(ValidationError):
            Receipt.model_validate({**receipt(), **update})


def test_complete_unavailable_and_failed_execution_are_distinct():
    """Unavailable evidence is a completed receipt; a failed execution has no receipt."""
    unavailable = receipt(result={"status": "unavailable", "reason": "no_evidence"})
    completed = {"protocol_version": 2, "status": "answer", "plan": plan(), "outcome": "complete",
                 "step_outcomes": [{"step_id": "dfw", "outcome": "completed"}],
                 "receipts": [unavailable], "message": "No usable evidence."}
    assert AnalysisResponseV2.model_validate(completed).outcome == "complete"
    failed = {**completed, "status": "error", "outcome": "failed", "receipts": [],
              "step_outcomes": [{"step_id": "dfw", "outcome": "failed",
                "issue": {"step_id": "dfw", "code": "timeout", "message": "Timed out"}}]}
    assert AnalysisResponseV2.model_validate(failed).outcome == "failed"
    with pytest.raises(ValidationError):
        AnalysisResponseV2.model_validate({**failed, "status": "answer"})


def test_confirmation_and_clarification_are_bound_to_current_plan():
    """State responses cannot smuggle numerical execution or stale clarification options."""
    confirmation = {"protocol_version": 2, "status": "confirmation", "plan": plan(), "message": "Review scope."}
    assert AnalysisResponseV2.model_validate(confirmation)
    with pytest.raises(ValidationError):
        AnalysisResponseV2.model_validate({**confirmation, "receipts": [receipt()]})
    pending = step(parameters={"cohort": unresolved()})
    raw = {**confirmation, "status": "clarification", "plan": {**plan(pending), "kind": "proposed"},
           "clarification": {"step_id": "dfw", "parameter": "cohort", "question": "Which cohort?", "choices": unresolved()["choices"]}}
    assert AnalysisResponseV2.model_validate(raw)
    raw["clarification"]["parameter"] = "course"
    with pytest.raises(ValidationError):
        AnalysisResponseV2.model_validate(raw)


def test_bounded_results_and_invalid_result_tags_are_rejected():
    """Result schema bounds apply independently of orchestration limits."""
    for payload in ({"kind": "count", "count": -1, "unit": "students"},
                    {"kind": "mean", "n": 0, "value": 10, "unit": "credits"},
                    {"kind": "regression", "coefficient": .5},
                    {"kind": "correlation", "method": "pearson", "n": 10, "coefficient": 1.1, "x_unit": "credits", "y_unit": "credits"}):
        with pytest.raises(ValidationError):
            TypeAdapter(Result).validate_python({"status": "ok", "payload": payload})
    with pytest.raises(ValidationError):
        TablePayload.model_validate({"kind": "table", "columns": [{"id": "n", "type": "integer", "unit": "students"}],
                                     "rows": [{"status": "ok", "cells": [10]}] * 201})


def test_v1_remains_a_separate_integer_receipt_contract():
    """Adding v2 neither widens existing values nor injects new transport fields into v1."""
    from analytics.schemas import AnalysisRequest, CalculationRow

    assert AnalysisRequest(analysis="retention", cohort="2023-24").model_dump() == {
        "analysis": "retention", "cohort": "2023-24", "credential": None, "program": None}
    with pytest.raises(ValidationError):
        CalculationRow(label="Completion", kind="rate", status="ok", numerator=5.5, denominator=10, rate=.55)


def test_missing_dependency_evidence_prevents_a_completed_child():
    """A completed-but-unavailable parent cannot justify executing a dependent analysis."""
    raw = {"protocol_version": 2, "status": "answer", "plan": plan(step(), step("child", depends_on=["dfw"])),
           "outcome": "partial", "step_outcomes": [{"step_id": "dfw", "outcome": "completed"},
             {"step_id": "child", "outcome": "not_executed", "issue": {"step_id": "child", "code": "dependency_unavailable", "message": "No usable parent evidence."}}],
           "receipts": [receipt(result={"status": "unavailable", "reason": "no_evidence"})], "message": "Dependency unavailable."}
    assert AnalysisResponseV2.model_validate(raw)
    raw["step_outcomes"][1] = {"step_id": "child", "outcome": "completed"}
    child = receipt(request=step("child", depends_on=["dfw"]))
    child["step_id"] = "child"
    raw["receipts"].append(child)
    raw["outcome"] = "complete"
    with pytest.raises(ValidationError, match="dependency"):
        AnalysisResponseV2.model_validate(raw)


def test_visible_exploration_needs_matching_method_and_feature_versions():
    """A correlation cannot omit the versioned inputs needed to replay it."""
    examples = json.loads((Path(__file__).parent / "fixtures/contracts_v2.json").read_text())
    raw = next(e for e in examples if e.get("receipts") and e["receipts"][0]["operation_id"] == "correlation")
    for versions in ({"method": None}, {"features": []}, {"method": {"id": "spearman", "version": "1"}}):
        bad = copy.deepcopy(raw)
        bad["receipts"][0]["versions"].update(versions)
        with pytest.raises(ValidationError):
            AnalysisResponseV2.model_validate(bad)


@pytest.mark.parametrize("field,value", [("source", {"snapshot_ref": "different"}), ("versions", {"catalog": "different"})])
def test_receipts_cannot_silently_change_snapshot_or_catalog(field, value):
    """Response assembly validates source references as well as numerical scope."""
    raw = {"protocol_version": 2, "status": "answer", "plan": plan(), "outcome": "complete",
           "step_outcomes": [{"step_id": "dfw", "outcome": "completed"}], "receipts": [receipt()], "message": "Evidence."}
    raw["receipts"][0][field].update(value)
    with pytest.raises(ValidationError):
        AnalysisResponseV2.model_validate(raw)


def test_instance_revalidation_and_json_schema_preserve_strictness():
    """Pydantic model-copy helpers do not bypass explicit boundary revalidation."""
    parsed = ExecutablePlan.model_validate(plan())
    bad = parsed.model_copy(update={"steps": ()})
    with pytest.raises(ValidationError):
        ExecutablePlan.model_validate(bad)
    schema = AnalysisResponseV2.model_json_schema()
    assert schema["additionalProperties"] is False
    for name in ("ProposedPlan", "ExecutablePlan", "HiddenResult", "HiddenTableRow"):
        assert schema["$defs"][name]["additionalProperties"] is False


def test_v2_filter_values_stay_compatible_with_the_existing_cohort_bar():
    """Schema enums must not drift from the measure-owned categorical vocabulary."""
    from measures.breakdowns.common import STUDENT_DIMENSIONS
    from measures.models import ALLOWED_VALUES, GroupDimension

    properties = ExecutablePlan.model_json_schema()["$defs"]["Filters"]["properties"]
    assert set(properties) == {d.value for d in STUDENT_DIMENSIONS}
    for name, schema in properties.items():
        assert set(schema["anyOf"][0]["enum"]) == ALLOWED_VALUES[GroupDimension(name)]
