"""Independent disclosure expectations for synthetic dashboard, legacy and plan evidence."""

import json

import pytest

from analytics.contracts_v2 import HiddenResult, MeanPayload, VisibleResult
from analytics.disclosure import (
    DisclosureRelation,
    StagedEvidence,
    disclose_plan,
    suppress_legacy,
)
from analytics.presentation import rate_row
from measures.disclosure import (
    DASHBOARD_V1,
    EXPLORATION_V1,
    LEGACY_ANALYTICS_V1,
    profile,
)


def mean(value=17.5, n=12):
    """Specify a visible aggregate without deriving its expected policy outcome."""
    return VisibleResult(
        status="ok", payload=MeanPayload(kind="mean", n=n, value=value, unit="credits")
    )


def stage(
    id,
    *,
    policy=EXPLORATION_V1.id,
    result=None,
    units=12,
    family=None,
    binary=(),
    exclusions=(),
):
    """Declare trusted executor metadata separately from user request parameters."""
    return StagedEvidence(
        step_id=id,
        profile_id=policy,
        result=result or mean(),
        distinct_units=units,
        linked_family=family,
        binary_counts=binary,
        exclusion_counts=exclusions,
    )


def test_profiles_are_versioned_and_dashboard_does_not_adopt_legacy_complements():
    """A visible one-of-twelve dashboard result remains visible under the existing policy."""
    assert {p.id for p in (DASHBOARD_V1, LEGACY_ANALYTICS_V1, EXPLORATION_V1)} == {
        "dashboard_v1",
        "legacy_analytics_v1",
        "exploration_v1",
    }
    assert all(
        p.version in ("1", "2") and p.minimum == 10
        for p in (DASHBOARD_V1, LEGACY_ANALYTICS_V1, EXPLORATION_V1)
    )
    assert DASHBOARD_V1.sample_visible(12)
    assert DASHBOARD_V1.visible_count(0) == 0 and DASHBOARD_V1.visible_count(9) is None
    assert suppress_legacy([rate_row("one", 1, 12)], 10)[0].status == "suppressed"
    with pytest.raises(ValueError):
        profile("model_supplied_policy")


def test_legacy_profile_preserves_safe_total_and_hides_linked_groups():
    """A safe twenty-of-forty total stays visible while a small linked group masks its family."""
    rows = [
        rate_row("total", 20, 40),
        rate_row("small", 2, 10, group={"program": "a"}),
        rate_row("other", 18, 30, group={"program": "b"}),
    ]
    result = suppress_legacy(rows, 10)
    assert result[0] is rows[0]
    assert [row.status for row in result[1:]] == ["suppressed", "suppressed"]
    assert all(
        row.numerator is None and not row.exclusions and not row.calculation
        for row in result[1:]
    )


@pytest.mark.parametrize(
    "units,binary,exclusions",
    [(9, (), ()), (None, (), ()), (12, (2, 10), ()), (12, (), (1,))],
)
def test_exploration_requires_distinct_units_and_safe_exclusions(
    units, binary, exclusions
):
    """Sample size, binary complements and disclosed exclusions each independently gate statistics."""
    (result,) = disclose_plan(
        (stage("explore", units=units, binary=binary, exclusions=exclusions),)
    )
    assert result.result.status == "suppressed"
    assert set(json.loads(result.result.model_dump_json())) == {"status", "reason"}
    assert result.comparisons_allowed is False


def test_linked_partition_family_hides_totals_differences_and_exclusions():
    """A safe-looking sibling cannot reveal an unsafe partition by subtraction."""
    output = disclose_plan(
        (
            stage("small", units=3, family="partition"),
            stage("total", units=40, family="partition"),
        )
    )
    assert all(row.result.status == "suppressed" for row in output)
    assert all(not row.comparisons_allowed for row in output)


@pytest.mark.parametrize("relation", [None, "overlap", "partition", "unknown"])
def test_mixed_plan_withholds_exploration_when_overlap_is_recognized_or_uncertain(
    relation,
):
    """The guard protects exploratory evidence without changing an existing dashboard result."""
    defined = stage("official", policy=DASHBOARD_V1.id)
    exploratory = stage("relationship")
    links = (
        ()
        if relation is None
        else (DisclosureRelation("official", "relationship", relation),)
    )
    output = disclose_plan((defined, exploratory), links)
    assert output[0].result == defined.result
    assert output[1].result.model_dump() == {
        "status": "suppressed",
        "reason": "linked_disclosure",
    }
    assert not output[1].comparisons_allowed


def test_only_registry_proven_disjoint_results_can_pass_together():
    """A trusted disjointness relation permits independently safe evidence within this one response."""
    output = disclose_plan(
        (stage("a"), stage("b")), (DisclosureRelation("a", "b", "disjoint"),)
    )
    assert all(row.result.status == "ok" for row in output)
    assert all(row.comparisons_allowed for row in output)


def test_guard_preserves_already_hidden_defined_results_and_refuses_bad_plan_metadata():
    """Hidden input is never reconstructed, and relationship typos cannot bypass the guard."""
    hidden = HiddenResult(status="not_reported", reason="not_reported")
    (result,) = disclose_plan(
        (stage("official", policy=DASHBOARD_V1.id, result=hidden),)
    )
    assert result.result == hidden
    with pytest.raises(ValueError):
        disclose_plan((stage("a"), stage("a")))
    with pytest.raises(ValueError):
        disclose_plan((stage("a"),), (DisclosureRelation("a", "missing", "disjoint"),))


def test_hidden_defined_partition_protects_exploration_even_for_disjoint_cells():
    """Disjoint categories can still reveal a hidden partition through a shared total."""
    hidden = HiddenResult(status="suppressed", reason="small_group")
    output = disclose_plan(
        (
            stage("official", policy=DASHBOARD_V1.id, result=hidden, family="linked"),
            stage("explore", family="linked"),
        ),
        (DisclosureRelation("official", "explore", "disjoint"),),
    )
    assert output[0].result == hidden
    assert output[1].result.status == "suppressed"


def test_already_hidden_exploration_keeps_its_specific_unavailable_reason():
    """A missing or unobservable statistic cannot become an invented small-sample result."""
    hidden = HiddenResult(status="unavailable", reason="zero_variance")
    (output,) = disclose_plan((stage("explore", result=hidden),))
    assert output.result == hidden and not output.comparisons_allowed


def test_defined_policy_binding_refuses_a_second_policy():
    """The registry policy/version is attached once and cannot be switched during plan projection."""
    from analytics.analysis_service import OperationEvidence
    from analytics.contracts_v2 import VersionReference
    from analytics.disclosure import stage_defined
    from measures.registry import OPERATIONS

    evidence = OperationEvidence(
        operation_id="retention.rate",
        operation_version="1",
        result=mean(),
        disclosure_profile=VersionReference(id="legacy_analytics_v1", version="1"),
    )
    with pytest.raises(ValueError, match="different disclosure policy"):
        stage_defined("official", OPERATIONS["retention.rate"], evidence)


@pytest.mark.parametrize(
    "kind,count,expected",
    [
        ("count", 0, "ok"),
        ("count", 2, "suppressed"),
        ("count", 12, "ok"),
        ("rate", 2, "suppressed"),
        ("correlation", 12, "ok"),
        ("mean_comparison", 2, "suppressed"),
        ("mean_comparison", 10, "ok"),
    ],
)
def test_exploration_checks_each_payloads_counting_inputs(kind, count, expected):
    """A valid serialized statistic can still fail its distinct-unit or comparison-input policy."""
    from pydantic import TypeAdapter

    from analytics.contracts_v2 import Result

    n = 20 if kind == "mean_comparison" else 12
    if kind == "count":
        payload = {"kind": kind, "count": count, "unit": "students"}
    elif kind == "rate":
        payload = {
            "kind": kind,
            "numerator": count,
            "denominator": 12,
            "value": round(count / 12, 4),
            "numerator_unit": "students",
            "denominator_unit": "students",
        }
    elif kind == "correlation":
        payload = {
            "kind": kind,
            "method": "pearson",
            "n": n,
            "coefficient": 0.5,
            "x_unit": "credits",
            "y_unit": "credits",
        }
    else:
        payload = {
            "kind": kind,
            "unit": "credits",
            "groups": [
                {"id": "a", "n": count, "mean": 1.0},
                {"id": "b", "n": 10, "mean": 2.0},
            ],
            "differences": [{"minuend": "a", "subtrahend": "b", "value": -1.0}],
        }
    result = TypeAdapter(Result).validate_python({"status": "ok", "payload": payload})
    (output,) = disclose_plan((stage("statistic", result=result, units=n),))
    assert output.result.status == expected


def test_exploration_table_requires_registered_unit_counts_for_every_visible_input():
    """A table cannot bypass group-size checks or retain a difference sourced from a hidden row."""
    from analytics.contracts_v2 import TablePayload

    result = VisibleResult(
        status="ok",
        payload=TablePayload.model_validate(
            {
                "kind": "table",
                "columns": [{"id": "students", "type": "integer", "unit": "students"}],
                "rows": [{"status": "ok", "cells": [12]}],
            }
        ),
    )
    (unproven,) = disclose_plan((stage("table", result=result),))
    assert unproven.result.status == "suppressed"
    trusted = StagedEvidence(
        "table", EXPLORATION_V1.id, result, distinct_units=12, group_units=(12,)
    )
    assert disclose_plan((trusted,))[0].result.status == "ok"
