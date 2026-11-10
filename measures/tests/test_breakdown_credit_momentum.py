"""Checks the Credit momentum numbers against a tiny made-up database with known answers, plus the real data."""
from __future__ import annotations

import pytest

from measures.breakdowns.credit_momentum import credit_momentum
from measures.run_measures import DEFAULT_DATABASE
from measures.tests.explorer_fixture import ask, here, make_database, student


def group(prefix: str, count: int, attempted: float | None, earned: float | None, back: bool = False, terms=(), **values):
    """count students with these year-1 credits; back: they take a course in Fall 2024; terms: (season, att, earned)."""
    students, records = [], []
    for n in range(count):
        student_id = f"{prefix}{n}"
        students.append(student(student_id, attempted=attempted, earned=earned, **values))
        for season, term_attempted, term_earned in terms:
            year = "2023-24" if season != "NEXT_FALL" else "2024-25"
            records.append(here(student_id, year, "FALL" if season == "NEXT_FALL" else season, attempted=term_attempted, earned=term_earned, grade="4"))
        if back:
            records.append(here(student_id, "2024-25", "FALL", grade="4", attempted=3, earned=3))
    return students, records


def build(tmp_path, *groups):
    """A database from groups made by group()."""
    return make_database(tmp_path / "pdp.sqlite", [s for g in groups for s in g[0]], [r for g in groups for r in g[1]])


def test_tiles_milestones_and_tiers(tmp_path):
    """Averages over students with known credits, milestones at 12/24/30, and the design's three tiers."""
    database = build(
        tmp_path,
        group("low", 10, attempted=12, earned=6),
        group("mid", 10, attempted=24, earned=24, back=True),
        group("high", 10, attempted=30, earned=30, back=True),
        group("blank", 2, attempted=None, earned=None),
    )
    page = credit_momentum(**ask("2023-24", "federal"), database=database)
    assert page["status"] == "ok"
    assert page["credits"] == {"counted": 30, "left_out": None, "avg_attempted": 22.0, "avg_earned": 20.0}
    assert [(m["credits"], m["students"]) for m in page["milestones"]] == [(12, 20), (24, 20), (30, 10)]
    assert [(t["label"], t["students"], t["retained"]) for t in page["tiers"]] == [("Under 15", 10, 0), ("15–29", 10, 10), ("30 or more", 10, 10)]
    # The shared measure: the average of each student's own ratio (0.5 x 10, 1.0 x 20) -> 0.8333.
    assert page["completion"]["ratio"] == 0.8333
    assert (page["retention"]["type"], page["retention"]["retained"], page["retention"]["students"]) == ("federal", 20, 32)


def test_tiers_follow_the_retention_type(tmp_path):
    """School retention (the PDP flag) is the default, so tiers can differ from who came back next fall."""
    database = build(tmp_path, group("low", 10, attempted=12, earned=6, back=True, retention=0), group("mid", 10, attempted=24, earned=24, retention=1))
    school = credit_momentum(**ask("2023-24"), database=database)
    assert [t["retained"] for t in school["tiers"][:2]] == [0, 10]
    federal = credit_momentum(**ask("2023-24", "federal"), database=database)
    assert [t["retained"] for t in federal["tiers"][:2]] == [10, 0]


def test_first_two_terms(tmp_path):
    """Average credits in the starting term and the next fall or spring, over students enrolled each term."""
    database = build(
        tmp_path,
        group("a", 10, attempted=24, earned=20, terms=[("FALL", 12, 10), ("SPRING", 12, 10)]),
        group("b", 10, attempted=12, earned=6, terms=[("FALL", 12, 6)]),
    )
    terms = credit_momentum(**ask("2023-24"), database=database)["terms"]
    assert terms[0] == {"label": "Fall 2023", "enrolled": 20, "avg_attempted": 12.0, "avg_earned": 8.0}
    assert terms[1] == {"label": "Spring 2024", "enrolled": 10, "avg_attempted": 12.0, "avg_earned": 10.0}


def test_small_tiers_and_terms_are_hidden(tmp_path):
    """A tier or term with under 10 students has no numbers."""
    database = build(tmp_path, group("a", 12, attempted=12, earned=6, terms=[("FALL", 12, 6)]), group("b", 3, attempted=30, earned=30))
    page = credit_momentum(**ask("2023-24"), database=database)
    assert page["tiers"][2] == {"key": "30_plus", "label": "30 or more", "students": None, "share": None, "retained": None, "rate": None}
    assert page["terms"][1]["enrolled"] is None


def test_filters_and_suppression(tmp_path):
    """The cohort bar's filters pick students; under 10 with known credits hides everything."""
    database = build(tmp_path, group("y", 12, attempted=12, earned=12, pell="Y"), group("n", 9, attempted=12, earned=0, pell="N"))
    assert credit_momentum(**ask("2023-24", pell="Y"), database=database)["credits"]["avg_earned"] == 12.0
    assert credit_momentum(**ask("2023-24", pell="N"), database=database)["status"] == "suppressed"


@pytest.mark.slow
@pytest.mark.skipif(not DEFAULT_DATABASE.exists(), reason="the normalized data isn't loaded")
def test_real_data_known_answers():
    """2023-24 Fall starters, checked with SQL on pdp.sqlite (synthetic data): the credit plan's expected values."""
    page = credit_momentum(**ask("2023-24", cohort_term="Fall"))
    assert page["students"] == 1584
    assert (page["credits"]["avg_attempted"], page["credits"]["avg_earned"]) == (17.8, 13.1)
    assert [m["students"] for m in page["milestones"]] == [778, 316, 140]
    federal = credit_momentum(**ask("2023-24", "federal", cohort_term="Fall"))
    assert [t["rate"] for t in federal["tiers"]] == [0.2949, 0.6859, 0.7357]  # same as the Explorer before #35
