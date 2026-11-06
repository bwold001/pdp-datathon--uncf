"""Checks the comparison: it reproduces the stub's numbers, and planted gaps come out where they should."""
from dataclasses import replace

import pytest

from gap_finder.compare import CountRow, benjamini_hochberg, compare, newcombe_interval
from gap_finder.find_gaps import stub_gaps
from gap_finder.models import GapStatus
from gap_finder.stub import EVERYONE_DENOMINATOR, EVERYONE_NUMERATOR, NEWEST, POOLED, RACES
from gap_finder.tests.test_stub import AGREED

# The columns compare works out. The stub has them typed in, so the two must agree.
COMPUTED = (
    "numerator", "denominator", "metric_rate",
    "comparison_numerator", "comparison_denominator", "comparison_rate",
    "gap_pts", "students_affected", "ci_low", "ci_high", "p_value", "q_value", "likely_noise",
    "status", "suppressed", "n_excluded", "rank_by_affected", "rank_by_gap",
)


def count(cohort, values, numerator, denominator, status="ok", dimensions=None, measure="retention") -> CountRow:
    """A measure's row. No values means everyone."""
    if dimensions is None:
        dimensions = ("race",) * len(values)
    shown = status == "ok"
    return CountRow(
        measure, cohort, dimensions, values,
        numerator if shown else None, denominator if shown else None,
        status, 0 if shown else None, 0 if shown else None, None, "Test.", "test",
    )


def stub_counts() -> list[CountRow]:
    """The counts behind the stub, as the shared measures would hand them over."""
    rows = [count(POOLED, (), EVERYONE_NUMERATOR, EVERYONE_DENOMINATOR)]
    rows += [count(POOLED, (race,), x, n) for race, (x, n) in AGREED.items()]
    rows.append(count(POOLED, ("X", "Two or More Races"), None, None, "suppressed", ("gender", "race")))
    rows.append(count(NEWEST, (), None, None, "not_yet_observable"))
    rows += [count(NEWEST, (race,), None, None, "not_yet_observable") for race in RACES]
    return rows


def by_group(rows):
    """Rows by cohort and group values."""
    return {(r.cohort, r.group_values): r for r in rows}


def test_reproduces_the_stub():
    computed = by_group(compare(stub_counts()))
    stub = by_group(stub_gaps())
    assert computed.keys() == stub.keys()
    for key, row in stub.items():
        for name in COMPUTED:
            expected, actual = getattr(row, name), getattr(computed[key], name)
            if isinstance(expected, float):
                assert actual == pytest.approx(expected, rel=1e-12), (key, name)
            else:
                assert actual == expected, (key, name)


def test_order_matches_the_stub():
    assert [r.key for r in compare(stub_counts())] == [r.key for r in stub_gaps()]


def test_input_order_doesnt_matter():
    assert compare(stub_counts()) == compare(list(reversed(stub_counts())))


def planted() -> list[CountRow]:
    """Made-up counts for #26's completion tests 2 and 3: A is 15 points behind, B has a 2-point gap in 40 students."""
    return [
        count("2022-23", (), 480, 1000),
        count("2022-23", ("A",), 72, 200),  # 36% against 51% for everyone else
        count("2022-23", ("B",), 20, 40),  # 50% against 47.9%
        count("2022-23", ("C",), 388, 760),
    ]


def test_planted_gap_ranks_first_and_isnt_noise():
    a = by_group(compare(planted()))[("2022-23", ("A",))]
    assert (a.gap_pts, a.rank_by_affected, a.rank_by_gap, a.likely_noise) == (-15.0, 1, 1, False)


def test_two_point_gap_in_forty_students_is_noise():
    b = by_group(compare(planted()))[("2022-23", ("B",))]
    assert b.gap_pts == 2.08 and b.denominator == 40
    assert b.likely_noise is True and b.q_value >= 0.05


def test_group_under_thirty_is_tested_but_not_ranked_by_gap():
    rows = [count("2022-23", (), 50, 100), count("2022-23", ("A",), 5, 20), count("2022-23", ("B",), 45, 80)]
    a = by_group(compare(rows))[("2022-23", ("A",))]
    assert a.status == GapStatus.OK and a.p_value is not None
    assert a.rank_by_affected is not None and a.rank_by_gap is None


def test_unknown_group_is_shown_but_not_tested():
    without = by_group(compare(planted()))
    rows = compare(planted() + [count("2022-23", ("UNKNOWN",), 10, 20)])
    unknown = by_group(rows)[("2022-23", ("UNKNOWN",))]
    assert unknown.status == GapStatus.UNKNOWN_GROUP and unknown.denominator == 20 and unknown.gap_pts is None
    # It isn't one of the tests, so the others' q-values don't change.
    assert by_group(rows)[("2022-23", ("A",))].q_value == without[("2022-23", ("A",))].q_value


def test_small_group_is_hidden_even_if_the_measure_showed_it():
    rows = compare(planted() + [count("2022-23", ("D",), 3, 9)])
    d = by_group(rows)[("2022-23", ("D",))]
    assert d.status == GapStatus.SUPPRESSED and d.numerator is None


def test_too_new_wins_over_too_small_and_unknown():
    rows = [count(NEWEST, (), None, None, "not_yet_observable"), count(NEWEST, ("UNKNOWN",), None, None, "suppressed")]
    assert compare(rows)[0].status == GapStatus.NOT_YET_OBSERVABLE


def test_too_small_wins_over_unknown():
    rows = compare(planted() + [count("2022-23", ("UNKNOWN",), None, None, "suppressed")])
    assert by_group(rows)[("2022-23", ("UNKNOWN",))].status == GapStatus.SUPPRESSED


def test_everyone_with_the_same_outcome_has_no_gap():
    rows = [count("2022-23", (), 0, 100), count("2022-23", ("A",), 0, 40), count("2022-23", ("B",), 0, 60)]
    for row in compare(rows):
        assert (row.gap_pts, row.p_value, row.likely_noise) == (0.0, 1.0, True)


def test_ranks_and_q_values_start_again_for_each_cohort():
    later = [replace(r, cohort="2023-24") for r in planted()]
    rows = by_group(compare(planted() + later))
    assert rows[("2022-23", ("A",))].rank_by_affected == rows[("2023-24", ("A",))].rank_by_affected == 1
    assert rows[("2022-23", ("A",))].q_value == rows[("2023-24", ("A",))].q_value


def test_two_way_groups_are_tested_with_one_way_groups():
    rows = planted() + [count("2022-23", ("F", "A"), 30, 100, dimensions=("gender", "race"))]
    two_way = by_group(compare(rows))[("2022-23", ("F", "A"))]
    assert two_way.status == GapStatus.OK and two_way.rank_by_affected is not None


def test_needs_an_everyone_row():
    with pytest.raises(ValueError, match="no everyone row"):
        compare(planted()[1:])


def test_refuses_duplicate_rows():
    with pytest.raises(ValueError, match="only once"):
        compare(planted() + planted()[1:2])


def test_hidden_when_everyone_else_is_under_ten():
    # A has 96 of 100 students, so everyone else is B's 4. Showing A's comparison would print B's hidden counts.
    rows = by_group(compare([count("2022-23", (), 50, 100), count("2022-23", ("A",), 48, 96), count("2022-23", ("B",), None, None, "suppressed")]))
    a = rows[("2022-23", ("A",))]
    assert a.status == GapStatus.SUPPRESSED
    assert a.comparison_numerator is None and a.comparison_denominator is None and a.numerator is None


def test_a_group_that_is_everyone_is_hidden():
    rows = compare([count("2022-23", (), 50, 100), count("2022-23", ("A",), 50, 100)])
    assert [r.status for r in rows] == [GapStatus.SUPPRESSED]


def test_interval_matches_newcombes_worked_example():
    # Newcombe (1998), Statistics in Medicine 17:873-890, method 10: 56/70 against 48/80 gives 0.0524 to 0.3339.
    low, high = newcombe_interval(56, 70, 48, 80)
    assert (round(low, 4), round(high, 4)) == (0.0524, 0.3339)


def test_interval_is_honest_for_a_small_group_at_zero():
    # 0 of 12 could still be a true rate of about 24%, so the interval reaches well short of the -50 point gap.
    rows = [count("2022-23", (), 500, 1012), count("2022-23", ("A",), 0, 12), count("2022-23", ("B",), 500, 1000)]
    a = by_group(compare(rows))[("2022-23", ("A",))]
    assert (a.gap_pts, a.ci_low, a.ci_high) == (-50.0, -53.09, -25.55)
    assert a.ci_high > -30  # the old interval (rate +/- 1.96 standard errors) stopped at -46.9


def test_more_tests_can_lower_a_q_value():
    # With p-values 0.03 and 0.5, the 0.03 row has q = 0.06. Adding a p-value of 0.001 lowers it to 0.045.
    assert benjamini_hochberg({"a": 0.03, "b": 0.5})["a"] == pytest.approx(0.06)
    assert benjamini_hochberg({"a": 0.03, "b": 0.5, "c": 0.001})["a"] == pytest.approx(0.045)


def test_benjamini_hochberg_known_values():
    # Worked by hand: sorted p 0.01, 0.02, 0.03, 0.5 over 4 tests gives 0.04, 0.04, 0.04, 0.5.
    q = benjamini_hochberg({"a": 0.01, "b": 0.02, "c": 0.03, "d": 0.5})
    assert q == pytest.approx({"a": 0.04, "b": 0.04, "c": 0.04, "d": 0.5})
