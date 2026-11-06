"""Checks the stub rows against the agreed retention example (synthetic mock data)."""
from gap_finder.find_gaps import stub_gaps
from gap_finder.models import GapStatus
from gap_finder.stub import EVERYONE_DENOMINATOR, EVERYONE_NUMERATOR, POOLED

# Retention by race, cohorts 2021-22 to 2023-24 pooled, as the shared measures count it on the loaded mock data.
AGREED = {
    "American Indian or Alaska Native": (61, 148),
    "Asian": (341, 561),
    "Black or African American": (565, 1218),
    "Hispanic": (1082, 2014),
    "Native Hawaiian or Other Pacific Islander": (6, 23),
    "Nonresident alien": (97, 155),
    "Two or More Races": (104, 196),
    "White": (1704, 3068),
    "UNKNOWN": (165, 318),
}


def pooled_race_rows() -> dict[str, object]:
    """The pooled one-way race rows, by race."""
    return {r.group_values[0]: r for r in stub_gaps() if r.cohort == POOLED and r.group_dimensions == ("race",)}


def test_stub_passes_the_table_checks():
    # stub_gaps runs check_table, so this fails on any broken rule.
    assert len(stub_gaps()) == 19


def test_every_status_appears():
    assert {r.status for r in stub_gaps()} == set(GapStatus)


def test_counts_match_the_agreed_example():
    rows = pooled_race_rows()
    assert {race: (r.numerator, r.denominator) for race, r in rows.items()} == AGREED
    assert sum(n for _, n in AGREED.values()) == EVERYONE_DENOMINATOR
    assert sum(x for x, _ in AGREED.values()) == EVERYONE_NUMERATOR


def test_each_comparison_is_everyone_minus_the_group():
    for r in pooled_race_rows().values():
        if r.status == GapStatus.OK:
            assert r.numerator + r.comparison_numerator == EVERYONE_NUMERATOR
            assert r.denominator + r.comparison_denominator == EVERYONE_DENOMINATOR
            assert r.metric_rate == round(r.numerator / r.denominator, 4)
            assert r.comparison_rate == round(r.comparison_numerator / r.comparison_denominator, 4)


def test_black_students_are_furthest_behind():
    black = pooled_race_rows()["Black or African American"]
    assert (black.gap_pts, black.students_affected, black.rank_by_affected) == (-8.53, -103.8, 1)
    assert black.likely_noise is False


def test_small_group_is_compared_but_not_ranked_by_gap():
    nhpi = pooled_race_rows()["Native Hawaiian or Other Pacific Islander"]
    assert nhpi.status == GapStatus.OK and nhpi.rank_by_gap is None


def test_unknown_race_is_shown_but_not_ranked():
    unknown = pooled_race_rows()["UNKNOWN"]
    assert unknown.status == GapStatus.UNKNOWN_GROUP
    assert unknown.denominator == 318 and unknown.rank_by_affected is None


def test_every_note_says_stub_and_synthetic():
    assert all(r.note.startswith("STUB.") and "synthetic" in r.note for r in stub_gaps())
