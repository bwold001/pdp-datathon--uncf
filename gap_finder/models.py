"""One row of the equity gap table: the contract the gap finder's output follows.

Each row compares one group with everyone else in the same cohort, on one measure. The first columns
are the shared measures' table (#9), in its order, and the comparison columns come after them. It refuses rows
that break the rules, so a bad row fails when it is built.
"""
from __future__ import annotations

from dataclasses import dataclass, fields
from enum import Enum

# Compatibility metadata: every nonempty group is eligible for display.
from measures.models import min_students

NOISE_Q = 0.05  # a gap whose q-value is at or above this is likely noise
GROUP_JOIN = " x "  # how two-way groups are written in files, as in the shared measures' table


class GapStatus(str, Enum):
    """Whether a row's numbers are shown, and if not, why."""

    OK = "ok"
    SUPPRESSED = "suppressed"  # too few students, so the group is hidden
    NOT_YET_OBSERVABLE = "not_yet_observable"  # the cohort is too new for this measure
    UNKNOWN_GROUP = "unknown_group"  # an unknown value: shown and kept in everyone else, but not compared or ranked


# Hidden rows: no numbers at all.
HIDDEN = (GapStatus.SUPPRESSED, GapStatus.NOT_YET_OBSERVABLE)

# The columns that only a compared (ok) row has.
COMPARISON_FIELDS = (
    "comparison_numerator",
    "comparison_denominator",
    "comparison_rate",
    "gap_pts",
    "students_affected",
    "ci_low",
    "ci_high",
    "p_value",
    "q_value",
    "likely_noise",
    "rank_by_affected",
)


@dataclass(frozen=True)
class GapResult:
    """One group compared with everyone else in its cohort, on one measure. Gaps are the group minus everyone else."""

    measure: str
    cohort: str  # a cohort label, e.g. '2021-22 + 2022-23 + 2023-24' for pooled cohorts
    group_dimensions: tuple[str, ...]  # sorted, e.g. ('gender', 'race')
    group_values: tuple[str, ...]  # lined up with the dimensions
    numerator: int | None
    denominator: int | None
    metric_rate: float | None  # a fraction, 4 places
    suppressed: bool
    status: GapStatus
    n_excluded: int | None  # students the measure applies to but couldn't count
    n_out_of_scope: int | None  # students the measure doesn't apply to, e.g. not required to take a gateway course
    exclusion_reason: str | None
    note: str
    data_loaded_at: str
    # The columns above are the shared measures' table, in its order. The comparison columns follow.
    comparison_numerator: int | None  # everyone minus the group
    comparison_denominator: int | None
    comparison_rate: float | None
    gap_pts: float | None  # percentage points; negative means the group is behind
    students_affected: float | None  # gap_pts / 100 x denominator: how many students the gap is worth
    ci_low: float | None  # 95% Newcombe (Wilson score) interval for the gap, in points, not corrected for many tests
    ci_high: float | None
    p_value: float | None  # two-sided two-proportion z-test, with everyone's rate as the pooled rate
    q_value: float | None  # Benjamini-Hochberg, over the compared rows of the same measure and cohort in one call
    likely_noise: bool | None
    rank_by_affected: int | None  # 1 is the most students behind
    rank_by_gap: int | None  # 1 is the largest gap behind; every nonempty comparison is ranked

    def __post_init__(self) -> None:
        self.check_group()
        if not isinstance(self.status, GapStatus):
            raise ValueError("status must be a GapStatus")
        if self.suppressed != (self.status in HIDDEN):
            raise ValueError("suppressed must be true exactly for suppressed and not_yet_observable rows")
        if self.status in HIDDEN:
            self.check_hidden()
            return
        self.check_counts()
        if self.status == GapStatus.UNKNOWN_GROUP:
            if any(getattr(self, name) is not None for name in COMPARISON_FIELDS + ("rank_by_gap",)):
                raise ValueError("an unknown_group row is not compared, so its comparison columns must be blank")
            return
        self.check_comparison()

    def check_group(self) -> None:
        """A group has one value per dimension, sorted by dimension, with no join text inside a value."""
        if not self.group_dimensions:
            raise ValueError("a gap row needs at least one group dimension: everyone is the comparison, not a row")
        if len(self.group_dimensions) != len(self.group_values):
            raise ValueError("group_dimensions and group_values must be the same length")
        if list(self.group_dimensions) != sorted(self.group_dimensions):
            raise ValueError("group_dimensions must be sorted")
        if any(GROUP_JOIN in value for value in self.group_values):
            raise ValueError(f"a group value can't contain {GROUP_JOIN!r}")

    def check_hidden(self) -> None:
        """A hidden row is all blank, never 0."""
        numbers = ("numerator", "denominator", "metric_rate", "n_excluded", "n_out_of_scope", "rank_by_gap") + COMPARISON_FIELDS
        if any(getattr(self, name) is not None for name in numbers):
            raise ValueError("a hidden row must have every number blank")

    def check_counts(self) -> None:
        """A shown row has its own counts, from at least min_students() students."""
        if any(v is None for v in (self.numerator, self.denominator, self.metric_rate, self.n_excluded, self.n_out_of_scope)):
            raise ValueError("a shown row needs numerator, denominator, metric_rate, n_excluded and n_out_of_scope")
        if self.denominator < min_students():
            raise ValueError(f"a shown row needs at least {min_students()} students")
        if not 0 <= self.numerator <= self.denominator:
            raise ValueError("numerator must be between 0 and the denominator")

    def check_comparison(self) -> None:
        """An ok row has every comparison column, and they agree with each other."""
        if any(getattr(self, name) is None for name in COMPARISON_FIELDS):
            raise ValueError("an ok row needs every comparison column")
        if self.rank_by_gap is None:
            raise ValueError("rank_by_gap is required for every comparison")
        if self.comparison_denominator < min_students():
            raise ValueError(f"everyone else needs at least {min_students()} students")
        if not 0 <= self.p_value <= self.q_value <= 1:
            raise ValueError("p_value and q_value must satisfy 0 <= p <= q <= 1")
        if self.likely_noise != (self.q_value >= NOISE_Q):
            raise ValueError(f"likely_noise must be true exactly when q_value >= {NOISE_Q}")
        if not self.ci_low <= self.gap_pts <= self.ci_high:
            raise ValueError("the interval must contain the gap")

    @property
    def key(self) -> tuple:
        """What makes a row unique: measure, cohort and group."""
        return (self.measure, self.cohort, self.group_dimensions, self.group_values)


# The table's columns, in order: the same order as GapResult's fields.
COLUMNS = tuple(f.name for f in fields(GapResult))


def sort_key(row: GapResult) -> tuple:
    """Each measure and cohort together; within them by rank, unranked rows last, then by group."""
    unranked = row.rank_by_affected is None
    return (row.measure, row.cohort, unranked, row.rank_by_affected or 0, row.group_dimensions, row.group_values)


def check_table(rows: list[GapResult]) -> None:
    """One row per key, ranks that run 1, 2, 3 and follow the gaps, and rows in sort order."""
    keys = [row.key for row in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("each measure, cohort and group can appear only once")
    if rows != sorted(rows, key=sort_key):
        raise ValueError("rows must be in sort order: see sort_key")

    families: dict[tuple[str, str], list[GapResult]] = {}
    for row in rows:
        families.setdefault((row.measure, row.cohort), []).append(row)
    for family in families.values():
        check_ranks(family, "rank_by_affected", "students_affected")
        check_ranks(family, "rank_by_gap", "gap_pts")


def check_ranks(family: list[GapResult], rank: str, value: str) -> None:
    """Within one measure and cohort, a rank runs 1..k, and a lower rank never has a larger value."""
    ranked = sorted((r for r in family if getattr(r, rank) is not None), key=lambda r: getattr(r, rank))
    if [getattr(r, rank) for r in ranked] != list(range(1, len(ranked) + 1)):
        raise ValueError(f"{rank} must run 1, 2, 3 with no gaps or repeats")
    values = [getattr(r, value) for r in ranked]
    if values != sorted(values):
        raise ValueError(f"{rank} must put the most behind first, by {value}")
