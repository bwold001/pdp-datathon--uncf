"""Checks that GapResult and check_table refuse rows that break the contract.

Run from the repo root: python -m pytest gap_finder/tests
"""
from dataclasses import replace

import pytest

from gap_finder.models import COLUMNS, GapResult, GapStatus, check_table, sort_key

# A valid ok row, made-up numbers. Each test breaks one rule.
OK = GapResult(
    "retention", "2022-23", ("race",), ("Asian",),
    numerator=20, denominator=40, metric_rate=0.5,
    comparison_numerator=300, comparison_denominator=500, comparison_rate=0.6,
    gap_pts=-10.0, students_affected=-4.0, ci_low=-25.0, ci_high=5.0, p_value=0.2, q_value=0.3,
    likely_noise=True, status=GapStatus.OK, suppressed=False, n_excluded=0, n_out_of_scope=0, exclusion_reason=None,
    rank_by_affected=1, rank_by_gap=1, note="test", data_loaded_at="test",
)

BLANK = dict(
    numerator=None, denominator=None, metric_rate=None,
    comparison_numerator=None, comparison_denominator=None, comparison_rate=None,
    gap_pts=None, students_affected=None, ci_low=None, ci_high=None, p_value=None, q_value=None,
    likely_noise=None, n_excluded=None, n_out_of_scope=None, rank_by_affected=None, rank_by_gap=None,
)
NO_COMPARISON = {name: value for name, value in BLANK.items() if name not in ("numerator", "denominator", "metric_rate", "n_excluded", "n_out_of_scope")}


def hidden(status=GapStatus.SUPPRESSED, **changes) -> GapResult:
    """A hidden row, with any changes."""
    return replace(OK, status=status, suppressed=True, **{**BLANK, **changes})


# The shared measures' table (#9), in its order: the gap table starts with these columns.
MEASURES_COLUMNS = (
    "measure", "cohort", "group_dimensions", "group_values", "numerator", "denominator", "metric_rate",
    "suppressed", "status", "n_excluded", "n_out_of_scope", "exclusion_reason", "note", "data_loaded_at",
)


def test_table_starts_with_the_measures_columns():
    assert COLUMNS[: len(MEASURES_COLUMNS)] == MEASURES_COLUMNS


def test_ok_row_builds():
    assert OK.status == GapStatus.OK


@pytest.mark.parametrize("status", [GapStatus.SUPPRESSED, GapStatus.NOT_YET_OBSERVABLE])
def test_hidden_row_builds_when_all_blank(status):
    assert hidden(status).suppressed


@pytest.mark.parametrize("name", ["numerator", "denominator", "metric_rate", "n_excluded", "n_out_of_scope", "gap_pts", "q_value", "rank_by_gap"])
def test_hidden_row_with_a_number_is_refused(name):
    with pytest.raises(ValueError, match="blank"):
        hidden(**{name: 0})


def test_hidden_row_must_say_suppressed():
    with pytest.raises(ValueError, match="suppressed"):
        replace(hidden(), suppressed=False)
    with pytest.raises(ValueError, match="suppressed"):
        replace(OK, suppressed=True)


def test_unknown_group_shows_counts_without_comparison():
    row = replace(OK, group_values=("UNKNOWN",), status=GapStatus.UNKNOWN_GROUP, **NO_COMPARISON)
    assert row.numerator == 20 and row.gap_pts is None
    with pytest.raises(ValueError, match="unknown_group"):
        replace(row, gap_pts=-10.0)


def test_status_must_be_a_gap_status():
    with pytest.raises(ValueError, match="GapStatus"):
        replace(OK, status="maybe")


def test_shown_row_accepts_small_nonempty_populations():
    assert replace(OK, numerator=5, denominator=9).denominator == 9
    with pytest.raises(ValueError, match="at least 1"):
        replace(OK, numerator=0, denominator=0)


def test_comparison_accepts_small_nonempty_populations():
    assert replace(OK, comparison_numerator=5, comparison_denominator=9).comparison_denominator == 9
    with pytest.raises(ValueError, match="everyone else needs at least 1"):
        replace(OK, comparison_numerator=0, comparison_denominator=0)


def test_rank_by_gap_is_required_for_small_groups():
    replace(OK, numerator=10, denominator=29)
    with pytest.raises(ValueError, match="rank_by_gap"):
        replace(OK, numerator=10, denominator=29, rank_by_gap=None)
    with pytest.raises(ValueError, match="rank_by_gap"):
        replace(OK, rank_by_gap=None)


def test_ok_row_needs_every_comparison_column():
    with pytest.raises(ValueError, match="every comparison column"):
        replace(OK, p_value=None)


def test_likely_noise_follows_q_value():
    with pytest.raises(ValueError, match="likely_noise"):
        replace(OK, likely_noise=False)
    replace(OK, p_value=0.01, q_value=0.04, likely_noise=False)


def test_q_value_cannot_be_below_p_value():
    with pytest.raises(ValueError, match="p <= q"):
        replace(OK, p_value=0.4, q_value=0.3)


def test_interval_must_contain_the_gap():
    with pytest.raises(ValueError, match="interval"):
        replace(OK, ci_low=-5.0)


def test_group_dimensions_and_values_line_up():
    with pytest.raises(ValueError, match="same length"):
        replace(OK, group_dimensions=("gender", "race"))
    with pytest.raises(ValueError, match="sorted"):
        replace(OK, group_dimensions=("race", "gender"), group_values=("Asian", "F"))
    with pytest.raises(ValueError, match="at least one"):
        replace(OK, group_dimensions=(), group_values=())
    with pytest.raises(ValueError, match="can't contain"):
        replace(OK, group_values=("A x B",))


def second(**changes) -> GapResult:
    """A second ok row in the same measure and cohort, ranked after OK."""
    values = dict(group_values=("White",), gap_pts=-5.0, students_affected=-2.0, ci_low=-20.0, ci_high=10.0,
                  rank_by_affected=2, rank_by_gap=2)
    return replace(OK, **{**values, **changes})


def test_check_table_accepts_a_good_table():
    check_table([OK, second(), hidden(group_values=("X",))])


def test_check_table_refuses_duplicates():
    with pytest.raises(ValueError, match="only once"):
        check_table([OK, OK])


def test_check_table_refuses_gaps_in_ranks():
    with pytest.raises(ValueError, match="1, 2, 3"):
        check_table([OK, second(rank_by_affected=3)])


def test_check_table_refuses_ranks_out_of_order():
    # White is ranked second but is further behind than Asian.
    with pytest.raises(ValueError, match="most behind first"):
        check_table([OK, second(students_affected=-9.0)])


def test_check_table_refuses_rows_out_of_order():
    with pytest.raises(ValueError, match="sort order"):
        check_table([second(), OK])


def test_ranks_start_again_for_each_cohort():
    other_cohort = replace(OK, cohort="2023-24")
    check_table(sorted([OK, second(), other_cohort], key=sort_key))
