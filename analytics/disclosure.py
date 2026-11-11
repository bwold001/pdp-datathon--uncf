"""Versioned evidence projection without size-based or linked-result suppression."""

from dataclasses import dataclass
from typing import Literal

from analytics.contracts_v2 import (
    Contract,
    Identifier,
    Result,
    VersionReference,
    VisibleResult,
)
from analytics.execution import checked
from analytics.schemas import CalculationRow
from measures.disclosure import (
    DASHBOARD_V1,
    EXPLORATION_V1,
    LEGACY_ANALYTICS_V1,
    profile,
)


def has_small_cell(row: CalculationRow, threshold: int) -> bool:
    """Keep the old helper callable without applying a small-cell rule."""
    return False


def suppress_legacy(rows: list[CalculationRow], threshold: int) -> list[CalculationRow]:
    """Keep the old helper callable while returning all original evidence unchanged."""
    return rows


@dataclass(frozen=True)
class StagedEvidence:
    """Hold internal evidence and trusted executor/registry disclosure facts before serialization."""

    step_id: str
    profile_id: str
    result: Result
    distinct_units: int | None = None
    binary_counts: tuple[int, ...] = ()
    exclusion_counts: tuple[int, ...] = ()
    group_units: tuple[int, ...] = ()
    linked_family: str | None = None


def stage_defined(step_id, spec, evidence, *, linked_family=None):
    """Bind already-projected defined evidence to its registry policy without suppressing it again."""
    selected = profile(spec.disclosure_profile)
    if (
        selected not in (DASHBOARD_V1, LEGACY_ANALYTICS_V1)
        or evidence.operation_id != spec.id
        or evidence.operation_version != spec.version
    ):
        raise ValueError("Defined evidence does not match its registry entry")
    if evidence.disclosure_profile != VersionReference(
        id=selected.id, version=selected.version
    ):
        raise ValueError("Defined evidence has a different disclosure policy")
    return StagedEvidence(
        step_id=step_id,
        profile_id=selected.id,
        result=evidence.result,
        linked_family=linked_family,
    )


@dataclass(frozen=True)
class DisclosureRelation:
    """Declare a registry-established relationship; lack of a relation means unknown overlap."""

    left: str
    right: str
    kind: Literal["disjoint", "overlap", "partition", "unknown"]


class DisclosedStep(Contract):
    """Return projected evidence only, with permission for application-generated comparisons explicit."""

    step_id: Identifier
    profile: VersionReference
    result: Result
    comparisons_allowed: bool


def _validate_exploration(stage):
    """Reject inconsistent executor metadata without suppressing valid small populations."""
    result = stage.result
    if not isinstance(result, VisibleResult):
        return
    n = stage.distinct_units
    if type(n) is not int or n < 1:
        raise ValueError("Exploration requires a positive distinct-unit count")
    counts = (
        *stage.binary_counts,
        *stage.exclusion_counts,
        *(e.count for e in result.exclusions),
    )
    if any(type(count) is not int or count < 0 for count in counts):
        raise ValueError("Exploration counts must be nonnegative integers")
    if stage.binary_counts and (
        len(stage.binary_counts) != 2 or sum(stage.binary_counts) != n
    ):
        raise ValueError("Binary counts must partition the analysis population")
    if any(type(size) is not int or size < 1 for size in stage.group_units):
        raise ValueError("Exploration input groups must be nonempty")
    payload = result.payload
    if payload.kind in ("mean", "correlation") and payload.n != n:
        raise ValueError("Statistic sample does not match the analysis population")
    if payload.kind == "count" and payload.count > n:
        raise ValueError("Count exceeds the analysis population")
    if payload.kind == "rate" and payload.denominator != n:
        raise ValueError("Rate denominator does not match the analysis population")
    if payload.kind == "table" and (
        len(stage.group_units) != len(payload.rows) or not payload.rows
    ):
        raise ValueError("Tables require input-group evidence for every row")


def _has_hidden(result):
    """Detect hidden inputs inside a typed result before permitting derived comparison text."""
    if not isinstance(result, VisibleResult):
        return True
    if result.payload.kind == "rate":
        return any(
            row.status not in ("ok", "provisional") for row in result.payload.breakdowns
        )
    if result.payload.kind == "table":
        return any(
            row.status not in ("ok", "provisional") for row in result.payload.rows
        )
    return False


def disclose_plan(
    staged: tuple[StagedEvidence, ...], relations: tuple[DisclosureRelation, ...] = ()
) -> tuple[DisclosedStep, ...]:
    """Validate the completed response and preserve small, linked and overlapping results."""
    ids = [stage.step_id for stage in staged]
    if not 1 <= len(ids) <= 4 or len(ids) != len(set(ids)):
        raise ValueError("Disclosure requires one to four unique staged steps")
    policies = {stage.step_id: profile(stage.profile_id) for stage in staged}
    links = {}
    for relation in relations:
        key = frozenset((relation.left, relation.right))
        if (
            len(key) != 2
            or not key <= set(ids)
            or key in links
            or relation.kind not in ("disjoint", "overlap", "partition", "unknown")
        ):
            raise ValueError("Invalid disclosure relationship")
        links[key] = relation.kind
    output = []
    for stage in checked(staged):
        policy = policies[stage.step_id]
        if policy == EXPLORATION_V1:
            _validate_exploration(stage)
        result = stage.result
        allowed = not _has_hidden(result)
        output.append(
            DisclosedStep(
                step_id=stage.step_id,
                profile=VersionReference(id=policy.id, version=policy.version),
                result=result,
                comparisons_allowed=allowed,
            )
        )
    return tuple(output)
