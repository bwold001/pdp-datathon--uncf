"""How consumers get the gap table: computed from the shared measures, or the hand-written stub."""
from __future__ import annotations

from pathlib import Path

from .compare import compare
from .models import GapResult, check_table, sort_key
from .sources import count_rows
from .stub import stub_rows

# What find_gaps compares when it isn't told: each default dimension on its own, each measure, the three oldest cohorts pooled.
DEFAULT_MEASURES = ["retention", "persistence", "gateway_math", "gateway_english"]
DEFAULT_COHORTS = [["2021-22", "2022-23", "2023-24"]]
# first_gen is left out until #74's finding 1 is settled: Y reads as UNKNOWN. Ask for it by name.
DEFAULT_DIMENSIONS = ["race", "gender", "pell", "age_band", "enrollment_intensity"]


def default_group_by() -> list[list[str]]:
    """Each default dimension on its own. Pairs (e.g. race x gender) are asked for by name.

    Pairs overlap the groups they're built from, so in the default they repeat the same finding sliced
    several ways and bury the one-way ranks.
    """
    return [[name] for name in DEFAULT_DIMENSIONS]


def stub_gaps() -> list[GapResult]:
    """The hand-written stub rows, checked and in sort order. Synthetic mock data, not computed."""
    rows = sorted(stub_rows(), key=sort_key)
    check_table(rows)
    return rows


def find_gaps(
    measures: list[str] | None = None,
    cohorts: list[list[str]] | None = None,
    group_by: list[list[str]] | None = None,
    database: str | Path | None = None,
) -> list[GapResult]:
    """Compare every group with everyone else, e.g. find_gaps(["retention"], [["2021-22", "2022-23"]], [["race"]]).

    Each inner cohort list is counted together (pooled). Each inner group_by list is one breakdown: one dimension,
    or two for a two-way group. database is the loaded SQLite file, or an open connection, as for run_measure.
    """
    rows = count_rows(
        measures or DEFAULT_MEASURES,
        cohorts or DEFAULT_COHORTS,
        group_by or default_group_by(),
        database,
    )
    return compare(rows)
