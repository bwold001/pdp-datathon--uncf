"""Registered bounded statistical calculations over private student/cohort units."""

import time
from collections import Counter
from contextlib import contextmanager
from dataclasses import dataclass
from itertools import combinations
from math import isfinite
from statistics import StatisticsError, correlation, mean

from analytics.contracts_v2 import (
    ComparisonPayload, CorrelationPayload, HiddenResult, TableColumn, TablePayload,
    VisibleResult, VisibleTableRow,
)
from analytics.execution import CURRENT, CalculationCancelled, check_cancelled, execution_scope
from analytics.exploration.catalog import FEATURES, GROUPS, PAIRS, group_for
from analytics.exploration.datasets import ExplorationRefusal, build
from measures.registry import OperationSpec
from measures.requests import FILTER_NAMES
from analytics.contracts_v2 import CorrelationParameters, GroupedParameters, VariantParameters

MAX_GROUPS = 20
STEP_SECONDS = 10


@dataclass(frozen=True)
class Evidence:
    """Stage validated aggregates and private counting evidence for receipt projection."""

    result: object
    distinct_units: int
    group_units: tuple[int, ...] = ()
    context: tuple[str, ...] = ()


def bound_groups(groups):
    """Count all occupied groups and refuse rather than returning a truncated statistic."""
    if sum(bool(values) for values in groups.values()) > MAX_GROUPS:
        raise ExplorationRefusal("limit_exceeded")


def _check(deadline):
    """Enforce both the remaining request deadline and the ten-second step budget."""
    check_cancelled()
    if time.monotonic() >= deadline:
        raise CalculationCancelled("Exploration step deadline reached")


def _number(value):
    """Reject nonfinite executor inputs even when constructed outside the dataset builder."""
    if value is not None and (type(value) not in (int, float) or not isfinite(value)):
        raise ExplorationRefusal("data_unavailable")
    return value


def _stats(rows, feature):
    """Compute each metric on its own complete cases, preserving n=1 means."""
    values = [_number(getattr(row, feature)) for row in rows]
    known = [value for value in values if value is not None]
    return (mean(known) if known else None), len(known), len(values) - len(known)


def _scaled(values, deadline):
    """Bound Pearson intermediates without changing correlation under positive scaling."""
    _check(deadline)
    scale = max(map(abs, values))
    scaled = []
    for value in values:
        _check(deadline)
        scaled.append(value / scale)
    return scaled


def _grouped(data, parameters, comparison, deadline):
    """Preserve registered order, exclusion reasons and independent metric eligibility."""
    groups = {name: [] for name in GROUPS[parameters.grouping]}
    exclusions = Counter()
    for row in data.rows:
        _check(deadline)
        group, reasons = group_for(row, parameters.grouping)
        if group is None:
            exclusions.update(reasons)
        else:
            groups[group].append(row)
    bound_groups(groups)
    counts = tuple({"reason": reason, "count": n} for reason, n in sorted(exclusions.items()))
    context = (data.coverage, "Exclusion reasons may overlap; group membership counts student/cohort units.",
        *(f"Excluded {key}: {value} student/cohort units." for key, value in sorted(exclusions.items())))
    if not data.rows:
        return Evidence(HiddenResult(status="unavailable", reason="no_evidence"), 0, context=context)
    if not any(groups.values()):
        return Evidence(HiddenResult(status="unavailable", reason="no_evidence"), len(data.rows),
            context=(*context, "No units with known grouping membership."))
    if comparison:
        summaries = []
        for key, rows in groups.items():
            value, n, missing = _stats(rows, "credits_earned_y1")
            summaries.append({"id": key, "n": n, "mean": value, "count": len(rows), "missing_count": missing})
        differences = []
        for left, right in combinations(summaries, 2):
            available = left['mean'] is not None and right['mean'] is not None
            differences.append({"minuend": right['id'], "subtrahend": left['id'],
                "value": round(right['mean'] - left['mean'], 4) if available else None,
                "minuend_n": right['n'], "subtrahend_n": left['n'],
                "unavailable_reason": None if available else "missing_group_mean"})
        result = VisibleResult(status="ok", payload=ComparisonPayload(
            kind="mean_comparison", unit="credits", groups=summaries, differences=differences), exclusions=counts)
        return Evidence(result, len(data.rows), context=context)
    columns = (
        ("group", "text", "registered group"), ("count", "integer", "student/cohort units"),
        ("earned_mean", "number", "credits"), ("earned_n", "integer", "eligible student/cohort units"),
        ("earned_missing", "integer", "student/cohort units"),
        ("attempted_mean", "number", "credits"), ("attempted_n", "integer", "eligible student/cohort units"),
        ("attempted_missing", "integer", "student/cohort units"),
    )
    rows, sizes = [], []
    for key, members in groups.items():
        if not members:
            continue
        earned, en, em = _stats(members, "credits_earned_y1")
        attempted, an, am = _stats(members, "credits_attempted_y1")
        rows.append(VisibleTableRow(status="ok", cells=(key, len(members), earned, en, em, attempted, an, am)))
        sizes.append(len(members))
    return Evidence(VisibleResult(status="ok", payload=TablePayload(kind="table",
        columns=[TableColumn(id=key, type=kind, unit=unit) for key, kind, unit in columns], rows=rows), exclusions=counts),
        len(data.rows), tuple(sizes), context)


def _correlation(data, parameters, deadline):
    """Use only paired complete cases; unrelated missing features do not drop a pair."""
    if frozenset((parameters.x, parameters.y)) not in PAIRS:
        raise ExplorationRefusal("incompatible_features")
    x, y, missing = [], [], Counter()
    for row in data.rows:
        _check(deadline)
        a, b = _number(getattr(row, parameters.x)), _number(getattr(row, parameters.y))
        if a is None or b is None:
            for feature, value in ((parameters.x, a), (parameters.y, b)):
                if value is None:
                    if feature.startswith('online_'):
                        missing.update(row.online_reasons)
                    else:
                        missing.update((feature + "_missing",))
            continue
        x.append(a)
        y.append(b)
    context = (data.coverage, f"Paired n={len(x)}; excluded incomplete pairs={len(data.rows) - len(x)}.",
        *(f"Missing {key}: {value} student/cohort units." for key, value in sorted(missing.items())))
    if len(x) < 2 or len(set(x)) == 1 or len(set(y)) == 1:
        reason = "no_evidence" if len(x) < 2 else "zero_variance"
        return Evidence(HiddenResult(status="unavailable", reason=reason), len(x), context=context)
    try:
        coefficient = correlation(_scaled(x, deadline), _scaled(y, deadline))
    except (StatisticsError, ArithmeticError) as error:
        raise ExplorationRefusal("data_unavailable") from error
    _check(deadline)
    # Clamp only finite roundoff near the mathematical bounds, never failed arithmetic.
    if not isfinite(coefficient) or abs(coefficient) > 1.0 + 1e-12:
        raise ExplorationRefusal("data_unavailable")
    result = VisibleResult(status="ok", payload=CorrelationPayload(kind="correlation", method="pearson", n=len(x),
        coefficient=max(-1.0, min(1.0, coefficient)), x_unit=FEATURES[parameters.x].unit, y_unit=FEATURES[parameters.y].unit, missing_pairs=len(data.rows) - len(x)),
        exclusions=[{"reason": key, "count": value} for key, value in sorted(missing.items())])
    return Evidence(result, len(x), context=context)


@contextmanager
def step_budget():
    """Bound database statements and Python loops by the same remaining step deadline."""
    parent = CURRENT.get()
    if parent is None:
        with execution_scope(STEP_SECONDS) as budget:
            yield budget.deadline
        return
    previous = parent.deadline
    parent.deadline = min(previous, time.monotonic() + STEP_SECONDS)
    try:
        yield parent.deadline
    finally:
        parent.deadline = previous


def execute(operation, parameters, snapshot):
    """Scope all reads and arithmetic to the remaining ten-second execution budget."""
    with step_budget():
        return _execute(operation, parameters, snapshot)


def _execute(operation, parameters, snapshot):
    """Validate a registered request, then calculate within one borrowed snapshot and budget."""
    if operation not in OPERATIONS:
        raise ExplorationRefusal("unsupported_operation")
    parameters = OPERATIONS[operation].parameters.model_validate(parameters)
    deadline = time.monotonic() + STEP_SECONDS
    _check(deadline)
    if operation == "correlation" and frozenset((parameters.x, parameters.y)) not in PAIRS:
        raise ExplorationRefusal("incompatible_features")
    if operation == "measure_variant":
        return Evidence(HiddenResult(status="unavailable", reason="unsupported_evidence"), 0, context=(
            "Gateway variant unavailable: required students marked completed include missing or contradictory highest year-one grades; equivalent threshold-only classification is not established for the baseline denominator.",
            "Requires reconciled completion/highest-grade evidence and validated non-attempter eligibility for the same cohort-completion denominator. P would qualify; highest year-one attempt grade differs from first-attempt course outcomes.",
        ))
    data = build(snapshot, parameters.cohort, parameters.filters)
    _check(deadline)
    if operation == "correlation":
        result = _correlation(data, parameters, deadline)
    else:
        result = _grouped(data, parameters, operation == "mean_comparison", deadline)
    _check(deadline)
    return result


def _spec(operation, parameters):
    """Publish fixed feature/group contracts instead of model-selected transformations."""
    return OperationSpec(id=operation, version="1", kind="exploratory_analysis", label=operation.replace('_', ' '),
        aliases=("online enrollments", "year-one credits", "retained characteristics"),
        purpose="Descriptive registered exploration; no causal inference or significance tests.", parameters=parameters,
        supported_filters=FILTER_NAMES, supported_breakdowns=tuple(GROUPS) if operation in ('grouped_summary', 'mean_comparison') else (),
        grain="student and entry cohort", population="Selected cohort and dashboard filters; each feature has separate eligibility.",
        time_semantics="First academic year; school/PDP or observed next-fall federal outcomes as named by grouping.",
        exclusions="Complete cases for requested features only; unknown retention is not not-retained; safe reasons may overlap.",
        required_coverage=("Normalized cohort facts and observed course terms",), executor="analytics.exploration.operations.execute",
        disclosure_profile="exploration_v1", limitations=("Descriptive evidence; no causal claims.", "Exposure completeness is uncertified.",
            "Gateway variant is unavailable pending validated equivalent cohort eligibility; first-attempt outcomes are a different population."),
        units=("credits", "student/cohort units", "observed enrollments"), component_denominators=(
            "Earned and attempted means each use their own observed n; Pearson uses paired complete cases.",
            "Online groups ordered 0, 1–2, 3+; differences: 1–2 minus 0, 3+ minus 0, 3+ minus 1–2.",
            "Retention difference is not-retained minus retained; unknown and unobservable outcomes are exclusions."),
        definitions=("student_year1", "complete_cases"))


OPERATIONS = {name: _spec(name, parameters) for name, parameters in (
    ('grouped_summary', GroupedParameters), ('mean_comparison', GroupedParameters),
    ('correlation', CorrelationParameters), ('measure_variant', VariantParameters))}
