"""Checks the Gateway page's comparisons: the breakdown's counts, compared by the gap finder."""
from __future__ import annotations

from gap_finder.gateway import add_gateway_gaps
from measures.breakdowns.gateway_courses import gateway_courses
from measures.tests.explorer_fixture import ask
from measures.tests.test_breakdown_gateway_courses import build, pairs_database, takers


def test_group_gap_against_everyone_else(tmp_path):
    """Pell recipients pass on the first try 25% of the time, everyone else in the course 75%: 50 points behind."""
    pell = takers("p", 20, ["F", "F", "F", "4"], back=0, pell="Y")
    other = takers("n", 20, ["4", "4", "4", "F"], back=0, pell="N")
    page = add_gateway_gaps(gateway_courses(**ask("2023-24", "federal", pell="Y"), database=build(tmp_path, pell, other)))
    (course,) = page["courses"]
    assert "all_takers" not in course
    assert course["group"] == {"status": "ok", "rate": 0.25, "others_rate": 0.75, "gap": -50.0, "likely_noise": False}


def test_no_filter_means_no_group(tmp_path):
    """Without a filter there's no group to compare, so each course's group is None."""
    page = add_gateway_gaps(gateway_courses(**ask("2023-24", "federal"), database=build(tmp_path, takers("s", 12, ["4"], back=0))))
    assert [course["group"] for course in page["courses"]] == [None]


def test_too_few_others_is_hidden(tmp_path):
    """12 Pell recipients and only 5 other students in the course: too few others to compare, so it's hidden."""
    pell = takers("p", 12, ["4"], back=0, pell="Y")
    other = takers("n", 5, ["F"], back=0, pell="N")
    page = add_gateway_gaps(gateway_courses(**ask("2023-24", "federal", pell="Y"), database=build(tmp_path, pell, other)))
    assert page["courses"][0]["group"] == {"status": "hidden", "rate": None, "others_rate": None, "gap": None, "likely_noise": None}


def test_pairs_behind_everyone_else(tmp_path):
    """A pair is compared with everyone else in the cohort: 1 of 10 came back, against 9 of 20 others."""
    page = add_gateway_gaps(gateway_courses(**ask("2023-24", "federal"), database=pairs_database(tmp_path)))
    assert "pair_counts" not in page
    (pair,) = page["pairs"]
    assert (pair["courses"], pair["students"], pair["retained"], pair["rate"], pair["others_rate"], pair["gap"]) == (["BIO 100", "ENG 101"], 10, 1, 0.1, 0.45, -35.0)
    assert pair["affected"] == -3.5
    assert isinstance(pair["likely_noise"], bool)
