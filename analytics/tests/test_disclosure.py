"""Independent disclosure expectations for synthetic dashboard, legacy and plan evidence."""

import pytest

from analytics.contracts_v2 import HiddenResult, MeanPayload, VisibleResult
from analytics.disclosure import (
    DisclosureRelation,
    StagedEvidence,
    disclose_plan,
    has_small_cell,
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
        result=result or mean(n=units if type(units) is int and units > 0 else 12),
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
        p.version == "2" and p.minimum == 1
        for p in (DASHBOARD_V1, LEGACY_ANALYTICS_V1, EXPLORATION_V1)
    )
    assert DASHBOARD_V1.sample_visible(12)
    assert DASHBOARD_V1.visible_count(0) == 0 and DASHBOARD_V1.visible_count(9) == 9
    assert suppress_legacy([rate_row("one", 1, 12)], 100)[0].status == "ok"
    with pytest.raises(ValueError):
        profile("model_supplied_policy")


@pytest.mark.parametrize("threshold", [1, 10, 100])
def test_legacy_profile_keeps_small_counts_complements_exclusions_and_linked_groups(
    threshold,
):
    """Old thresholds cannot hide a numerator, complement, exclusion or a related group."""
    rows = [
        rate_row("total", 20, 40),
        rate_row("small", 1, 2, group={"program": "a"}, exclusions={"missing": 1}),
        rate_row("complement", 11, 12, group={"program": "b"}),
    ]
    result = suppress_legacy(rows, threshold)
    assert result is rows
    assert [row.status for row in result] == ["ok", "ok", "ok"]
    assert result[1].exclusions == {"missing": 1}
    assert result[1].calculation == "1 / 2 = 50.00%"
    assert not any(has_small_cell(row, threshold) for row in rows)


@pytest.mark.parametrize("units", range(1, 10))
def test_exploration_keeps_small_populations_binary_complements_and_exclusions(units):
    """Every nonempty sample survives projection with one-unit exclusions and complements."""
    original = stage("explore", units=units, binary=(1, units - 1), exclusions=(1,))
    (result,) = disclose_plan((original,))
    assert result.result == original.result
    assert result.comparisons_allowed


@pytest.mark.parametrize(
    "units,binary,exclusions",
    [
        (None, (), ()),
        (0, (), ()),
        (12, (1, 2), ()),
        (12, (), (-1,)),
    ],
)
def test_invalid_exploration_metadata_is_rejected(units, binary, exclusions):
    """Malformed executor evidence raises an error instead of becoming size-suppressed output."""
    with pytest.raises(ValueError):
        disclose_plan(
            (stage("explore", units=units, binary=binary, exclusions=exclusions),)
        )


def test_linked_partition_family_keeps_small_groups_and_totals():
    """Linked small groups and totals remain visible without a subtraction rule."""
    output = disclose_plan(
        (
            stage("small", units=3, family="partition"),
            stage("total", units=40, family="partition"),
        )
    )
    assert all(row.result.status == "ok" for row in output)
    assert all(row.comparisons_allowed for row in output)


@pytest.mark.parametrize("relation", [None, "overlap", "partition", "unknown"])
def test_mixed_plan_keeps_exploration_when_overlap_is_recognized_or_uncertain(
    relation,
):
    """Overlapping or uncertain scopes do not hide valid exploratory or dashboard evidence."""
    defined = stage("official", policy=DASHBOARD_V1.id)
    exploratory = stage("relationship")
    links = (
        ()
        if relation is None
        else (DisclosureRelation("official", "relationship", relation),)
    )
    output = disclose_plan((defined, exploratory), links)
    assert output[0].result == defined.result
    assert output[1].result == exploratory.result
    assert all(row.comparisons_allowed for row in output)


def test_registry_proven_disjoint_results_remain_visible():
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


def test_hidden_defined_partition_does_not_hide_valid_exploration():
    """Historical hidden evidence stays hidden without hiding a valid sibling."""
    hidden = HiddenResult(status="suppressed", reason="small_group")
    output = disclose_plan(
        (
            stage("official", policy=DASHBOARD_V1.id, result=hidden, family="linked"),
            stage("explore", family="linked"),
        ),
        (DisclosureRelation("official", "explore", "disjoint"),),
    )
    assert output[0].result == hidden
    assert output[1].result.status == "ok"
    assert not output[0].comparisons_allowed and output[1].comparisons_allowed


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
        ("count", 1, "ok"),
        ("count", 2, "ok"),
        ("count", 11, "ok"),
        ("count", 12, "ok"),
        ("rate", 1, "ok"),
        ("rate", 2, "ok"),
        ("rate", 11, "ok"),
        ("correlation", 12, "ok"),
        ("mean_comparison", 1, "ok"),
        ("mean_comparison", 2, "ok"),
        ("mean_comparison", 10, "ok"),
    ],
)
def test_exploration_checks_each_payloads_counting_inputs(kind, count, expected):
    """Small counts, rates and comparison inputs survive the serialized result boundary."""
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
    """Tables require executor evidence but retain one-unit rows."""
    from analytics.contracts_v2 import TablePayload

    result = VisibleResult(
        status="ok",
        payload=TablePayload.model_validate(
            {
                "kind": "table",
                "columns": [{"id": "students", "type": "integer", "unit": "students"}],
                "rows": [{"status": "ok", "cells": [1]}],
            }
        ),
    )
    with pytest.raises(ValueError, match="input-group evidence"):
        disclose_plan((stage("table", result=result),))
    trusted = StagedEvidence(
        "table", EXPLORATION_V1.id, result, distinct_units=1, group_units=(1,)
    )
    assert disclose_plan((trusted,))[0].result.status == "ok"


@pytest.mark.parametrize("version", ["1", "unknown"])
def test_defined_policy_binding_rejects_old_policy_versions(version):
    """Evidence computed under earlier visibility rules cannot claim the new policy version."""
    from analytics.analysis_service import OperationEvidence
    from analytics.contracts_v2 import VersionReference
    from analytics.disclosure import stage_defined
    from measures.registry import OPERATIONS

    evidence = OperationEvidence(
        operation_id="retention.rate",
        operation_version="1",
        result=mean(),
        disclosure_profile=VersionReference(id="dashboard_v1", version=version),
    )
    with pytest.raises(ValueError, match="different disclosure policy"):
        stage_defined("official", OPERATIONS["retention.rate"], evidence)
