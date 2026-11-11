"""Compares each group with everyone else in its cohort: the gap, a z-test, q-values and ranks.

It works on counts only, so it doesn't need a database: sources.py turns each of the shared measures'
result rows into a CountRow first. Standard library only.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from measures.models import UNKNOWN, Status

from .models import NOISE_Q, GapResult, GapStatus, check_table, min_students, sort_key

Z_95 = 1.96  # for the 95% interval
UNKNOWN_VALUES = frozenset({UNKNOWN, ""})  # the shared measures' unknown value, or a blank

# The statuses a measure's row can have, as the shared measures write them.
MEASURE_OK = Status.OK.value
MEASURE_NOT_YET_OBSERVABLE = Status.NOT_YET_OBSERVABLE.value

# Says who was compared and over which cohorts, as #26 asks of every note.
COMPARED_NOTE = "Compared with everyone else in the same cohort ({cohort}). A gap shows a difference, not its cause."


@dataclass(frozen=True)
class CountRow:
    """One measure result: a group's counts for one cohort. No dimensions means everyone."""

    measure: str
    cohort: str
    group_dimensions: tuple[str, ...]
    group_values: tuple[str, ...]
    numerator: int | None  # blank when the measure hid the group
    denominator: int | None
    status: str  # ok, suppressed or not_yet_observable, from the measure
    n_excluded: int | None
    n_out_of_scope: int | None
    exclusion_reason: str | None
    note: str
    data_loaded_at: str

    @property
    def is_everyone(self) -> bool:
        """True for the everyone row, which each group is compared with."""
        return not self.group_dimensions


@dataclass(frozen=True)
class Stats:
    """The comparison columns for one group, before q-values and ranks."""

    comparison_numerator: int
    comparison_denominator: int
    comparison_rate: float
    gap_pts: float
    students_affected: float
    ci_low: float
    ci_high: float
    p_value: float


def compare(rows: list[CountRow]) -> list[GapResult]:
    """Compare every group with everyone else, for each measure and cohort. Needs an everyone row for each."""
    keys = [(r.measure, r.cohort, r.group_dimensions, r.group_values) for r in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("each measure, cohort and group can appear only once")
    everyone = {(r.measure, r.cohort): r for r in rows if r.is_everyone}
    results = []
    for family, groups in group_rows(rows).items():
        if family not in everyone:
            raise ValueError(f"no everyone row for {family}")
        results.extend(compare_family(everyone[family], groups))
    results.sort(key=sort_key)
    check_table(results)
    return results


def group_rows(rows: list[CountRow]) -> dict[tuple[str, str], list[CountRow]]:
    """The group rows (not everyone), by measure and cohort."""
    families: dict[tuple[str, str], list[CountRow]] = {}
    for row in rows:
        if not row.is_everyone:
            families.setdefault((row.measure, row.cohort), []).append(row)
    return families


def compare_family(everyone: CountRow, groups: list[CountRow]) -> list[GapResult]:
    """Every group in one measure and cohort: compare, then correct for many tests, then rank."""
    statuses = {g: gap_status(everyone, g) for g in groups}
    stats = {g: group_stats(everyone, g) for g in groups if statuses[g] == GapStatus.OK}
    q_values = benjamini_hochberg({g: s.p_value for g, s in stats.items()})
    by_affected = ranks(stats, lambda g: stats[g].students_affected)
    by_gap = ranks(stats, lambda g: stats[g].gap_pts)
    return [
        build_result(g, statuses[g], stats.get(g), q_values.get(g), by_affected.get(g), by_gap.get(g))
        for g in groups
    ]


def gap_status(everyone: CountRow, group: CountRow) -> GapStatus:
    """The row's status. When more than one applies, too new wins, then too small, then unknown."""
    if MEASURE_NOT_YET_OBSERVABLE in (everyone.status, group.status):
        return GapStatus.NOT_YET_OBSERVABLE
    if group.status != MEASURE_OK or group.denominator is None or group.denominator < min_students():
        return GapStatus.SUPPRESSED
    # Everyone else is a group too: under the threshold, the comparison columns would print a hidden group's
    # counts. This also hides a group that is everyone, which has no one to compare with.
    if everyone.denominator - group.denominator < min_students():
        return GapStatus.SUPPRESSED
    if any(value in UNKNOWN_VALUES for value in group.group_values):
        return GapStatus.UNKNOWN_GROUP
    return GapStatus.OK


def group_stats(everyone: CountRow, group: CountRow) -> Stats:
    """The gap between a group and everyone minus the group, with its interval and p-value."""
    comparison_numerator = everyone.numerator - group.numerator
    comparison_denominator = everyone.denominator - group.denominator
    rate = group.numerator / group.denominator
    comparison_rate = comparison_numerator / comparison_denominator
    gap = rate - comparison_rate
    ci_low, ci_high = newcombe_interval(group.numerator, group.denominator, comparison_numerator, comparison_denominator)
    return Stats(
        comparison_numerator=comparison_numerator,
        comparison_denominator=comparison_denominator,
        comparison_rate=round(comparison_rate, 4),
        gap_pts=round(gap * 100, 2),
        students_affected=round(gap * group.denominator, 1),
        ci_low=round(ci_low * 100, 2),
        ci_high=round(ci_high * 100, 2),
        p_value=two_proportion_p_value(everyone, group, gap, comparison_denominator),
    )


def wilson_interval(successes: int, total: int) -> tuple[float, float]:
    """95% Wilson score interval for one rate. Unlike rate +/- 1.96 standard errors, it stays honest near 0% and 100%."""
    rate = successes / total
    z2 = Z_95 * Z_95
    centre = (rate + z2 / (2 * total)) / (1 + z2 / total)
    half = Z_95 * math.sqrt(rate * (1 - rate) / total + z2 / (4 * total * total)) / (1 + z2 / total)
    return centre - half, centre + half


def newcombe_interval(x1: int, n1: int, x2: int, n2: int) -> tuple[float, float]:
    """95% interval for rate 1 minus rate 2 (Newcombe's hybrid score method), built from each side's Wilson interval."""
    rate1, rate2 = x1 / n1, x2 / n2
    low1, high1 = wilson_interval(x1, n1)
    low2, high2 = wilson_interval(x2, n2)
    gap = rate1 - rate2
    low = gap - math.sqrt((rate1 - low1) ** 2 + (high2 - rate2) ** 2)
    high = gap + math.sqrt((high1 - rate1) ** 2 + (rate2 - low2) ** 2)
    return low, high


def two_proportion_p_value(everyone: CountRow, group: CountRow, gap: float, comparison_denominator: int) -> float:
    """Two-sided p-value of a two-proportion z-test, with the pooled rate (everyone's rate)."""
    pooled = everyone.numerator / everyone.denominator
    se = math.sqrt(pooled * (1 - pooled) * (1 / group.denominator + 1 / comparison_denominator))
    if se == 0:
        # Everyone has the same outcome, so there is no gap to test.
        return 1.0
    return math.erfc(abs(gap / se) / math.sqrt(2))


def benjamini_hochberg(p_values: dict) -> dict:
    """Benjamini-Hochberg q-values: each p-value corrected for how many were tested together."""
    ordered = sorted(p_values, key=lambda k: p_values[k])
    tests = len(ordered)
    q_values = {}
    smallest = 1.0
    # From the largest p-value down, so each q is the smallest of the corrected values at or above it.
    for position in range(tests, 0, -1):
        key = ordered[position - 1]
        smallest = min(smallest, p_values[key] * tests / position)
        # A q-value is never below its p-value; max() stops float rounding (p * 3 / 3 < p) from breaking that.
        q_values[key] = max(smallest, p_values[key])
    return q_values


def ranks(rows: dict, value) -> dict:
    """Rank 1 for the most behind (lowest value). Ties go to the larger group, then to the group's name."""
    ordered = sorted(rows, key=lambda g: (value(g), -g.denominator, g.group_dimensions, g.group_values))
    return {g: position for position, g in enumerate(ordered, start=1)}


def build_result(group: CountRow, status: GapStatus, stats: Stats | None, q_value, rank_by_affected, rank_by_gap) -> GapResult:
    """One GapResult: hidden rows are all blank, unknown groups show only their own counts."""
    hidden = status in (GapStatus.SUPPRESSED, GapStatus.NOT_YET_OBSERVABLE)
    shown = not hidden
    return GapResult(
        measure=group.measure,
        cohort=group.cohort,
        group_dimensions=group.group_dimensions,
        group_values=group.group_values,
        numerator=group.numerator if shown else None,
        denominator=group.denominator if shown else None,
        metric_rate=round(group.numerator / group.denominator, 4) if shown else None,
        comparison_numerator=stats.comparison_numerator if stats else None,
        comparison_denominator=stats.comparison_denominator if stats else None,
        comparison_rate=stats.comparison_rate if stats else None,
        gap_pts=stats.gap_pts if stats else None,
        students_affected=stats.students_affected if stats else None,
        ci_low=stats.ci_low if stats else None,
        ci_high=stats.ci_high if stats else None,
        p_value=stats.p_value if stats else None,
        q_value=q_value,
        likely_noise=q_value >= NOISE_Q if stats else None,
        status=status,
        suppressed=hidden,
        n_excluded=group.n_excluded if shown else None,
        n_out_of_scope=group.n_out_of_scope if shown else None,
        exclusion_reason=group.exclusion_reason if shown else None,
        rank_by_affected=rank_by_affected,
        rank_by_gap=rank_by_gap,
        note=f"{group.note} {COMPARED_NOTE.format(cohort=group.cohort)}".strip(),
        data_loaded_at=group.data_loaded_at,
    )
