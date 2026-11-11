"""Legacy projection and conservative one-plan exploration disclosure, without changing dashboard policy."""

from dataclasses import dataclass
from typing import Literal

from analytics.contracts_v2 import (
    Contract,
    HiddenResult,
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
    """Reproduce the existing legacy count, numerator, denominator, complement and exclusion checks."""
    policy = LEGACY_ANALYTICS_V1
    return row.status in ("ok", "provisional") and (
        policy.small_cell(row.count, threshold=threshold)
        or (row.denominator is not None and row.denominator < threshold)
        or policy.small_cell(row.numerator, threshold=threshold)
        or (
            row.denominator is not None
            and row.numerator is not None
            and policy.small_cell(row.denominator - row.numerator, threshold=threshold)
        )
        or any(
            policy.small_cell(n, threshold=threshold) for n in row.exclusions.values()
        )
    )


def suppress_legacy(rows: list[CalculationRow], threshold: int) -> list[CalculationRow]:
    """Preserve legacy linked suppression and its existing safe-total exception exactly once."""
    if not any(has_small_cell(row, threshold) for row in checked(rows)):
        return rows
    totals = [row for row in checked(rows) if not row.group and row.horizon is None]
    safe_total = (
        totals[0]
        if len(totals) == 1
        and any(row.group for row in checked(rows))
        and not has_small_cell(totals[0], threshold)
        else None
    )
    return [
        CalculationRow(
            label=row.label,
            kind=row.kind,
            group=row.group,
            horizon=row.horizon,
            status="suppressed",
            note="Linked results hidden to prevent small-cell disclosure.",
        )
        if row is not safe_total and row.status in ("ok", "provisional")
        else row
        for row in checked(rows)
    ]


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


def _safe_exploration(stage):
    """Check distinct units, all visible inputs, binary complements and exclusions before statistics."""
    policy = EXPLORATION_V1
    n = stage.distinct_units
    if type(n) is not int or not policy.sample_visible(n):
        return False
    result = stage.result
    if not isinstance(result, VisibleResult):
        return False
    counts = (
        *stage.binary_counts,
        *stage.exclusion_counts,
        *(e.count for e in result.exclusions),
    )
    if any(
        type(count) is not int or count < 0 or policy.small_cell(count)
        for count in counts
    ):
        return False
    if stage.binary_counts and (
        len(stage.binary_counts) != 2 or sum(stage.binary_counts) != n
    ):
        return False
    if any(
        type(size) is not int or not policy.sample_visible(size)
        for size in stage.group_units
    ):
        return False
    payload = result.payload
    if payload.kind in ("mean", "correlation"):
        return payload.n == n
    if payload.kind == "count":
        return (
            payload.count <= n
            and not policy.small_cell(payload.count)
            and not policy.small_cell(n - payload.count)
        )
    if payload.kind == "rate":
        return (
            payload.denominator == n
            and not payload.breakdowns
            and not policy.small_cell(payload.numerator)
            and not policy.small_cell(n - payload.numerator)
        )
    if payload.kind == "mean_comparison":
        return all(policy.sample_visible(group.n) for group in payload.groups)
    if payload.kind == "table":
        if len(stage.group_units) != len(payload.rows) or not payload.rows:
            return False
        for row in payload.rows:
            if row.status not in ("ok", "provisional"):
                return False
            for column, cell in zip(payload.columns, row.cells):
                if (
                    column.type == "integer"
                    and cell is not None
                    and policy.small_cell(cell)
                ):
                    return False
        return True
    return False


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
    """Withhold unsafe exploratory families/overlaps while preserving already-disclosed defined evidence."""
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
    unsafe = {
        stage.step_id
        for stage in staged
        if policies[stage.step_id] == EXPLORATION_V1 and not _safe_exploration(stage)
    }
    unsafe_families = {
        stage.linked_family
        for stage in staged
        if stage.linked_family is not None
        and (stage.step_id in unsafe or _has_hidden(stage.result))
    }
    output = []
    for stage in checked(staged):
        policy = policies[stage.step_id]
        result = stage.result
        allowed = not _has_hidden(result)
        if policy == EXPLORATION_V1:
            overlapping = any(
                other.step_id != stage.step_id
                and links.get(frozenset((stage.step_id, other.step_id))) != "disjoint"
                for other in staged
            )
            family_unsafe = (
                stage.linked_family is not None
                and stage.linked_family in unsafe_families
            )
            if isinstance(result, VisibleResult) and (
                overlapping or family_unsafe or stage.step_id in unsafe
            ):
                reason = (
                    "linked_disclosure"
                    if overlapping or family_unsafe
                    else "small_group"
                )
                result = HiddenResult(status="suppressed", reason=reason)
                allowed = False
        output.append(
            DisclosedStep(
                step_id=stage.step_id,
                profile=VersionReference(id=policy.id, version=policy.version),
                result=result,
                comparisons_allowed=allowed,
            )
        )
    return tuple(output)
