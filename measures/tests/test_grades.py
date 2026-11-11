"""Checks the shared letter grade scale, and that the table pages show follows the DFW and gateway rules."""
from __future__ import annotations

import pytest

from measures.breakdowns.grade_scale import GATEWAY_GROUPS, dfw_scale, gateway_group, gateway_scale
from measures.calculations.dfw import DFW_BELOW, DFW_GRADES, DFW_GROUPS, SPLIT, grade_outcomes
from measures.calculations.grades import GRADE_ORDER, LETTER_SCALE, grade_letter, letter_for, letter_passes_gateway


@pytest.mark.parametrize(
    ("points", "letter"),
    [(4.0, "A"), (3.7, "A-"), (3.69, "B+"), (3.6, "B+"), (3.5, "B+"), (3.0, "B"), (2.7, "B-"), (2.6, "C+"), (2.5, "C+"), (2.0, "C"),
     (1.7, "C-"), (1.69, "D+"), (1.5, "D+"), (1.3, "D+"), (1.0, "D"), (0.7, "D-"), (0.69, "F"), (0.3, "F"), (0.0, "F")],
)
def test_a_number_takes_the_highest_letter_it_reaches(points, letter):
    """Each letter covers its grade points up to the next letter's; anything under a D- is an F, whatever the number."""
    assert letter_for(points) == letter


def test_codes_and_spellings():
    """P, F and W are final codes; numbers match however they're written; codes that aren't final have no letter."""
    assert [grade_letter(g) for g in ("P", " f ", "w", "1", "1.0", "1.00", "4.00")] == ["P", "F", "W", "D", "D", "D", "A"]
    assert [grade_letter(g) for g in ("I", "A", "M", "MIS", "O", "OTH", "UW", "", None, "4.5", "-1")] == [None] * 11


def test_dfw_is_d_plus_and_below():
    """A C- passes, so the DFW line is 1.7; D+, D, D-, F and W count."""
    assert DFW_BELOW == 1.7
    assert DFW_GRADES == ("D+", "D", "D-", "F", "W")
    outcomes = grade_outcomes()
    assert not outcomes["1.7"] and outcomes["1.69"] and outcomes["F"] and outcomes["W"] and not outcomes["P"]


def test_gateway_pass_is_a_d_or_better():
    """The PDP's gateway line (1.0) falls on the D: D and up and P pass, D-, F and W don't."""
    passing = [grade for grade in GRADE_ORDER if letter_passes_gateway(grade)]
    assert passing == ["A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "P"]


def test_every_dfw_letter_has_a_group():
    """The split counts D, F and W: D+, D and D- are all a D."""
    assert set(DFW_GROUPS) == set(DFW_GRADES)
    assert SPLIT == ("D", "F", "W")
    assert [DFW_GROUPS[letter] for letter in ("D+", "D", "D-", "F", "W")] == ["D", "D", "D", "F", "W"]


def test_gateway_groups_follow_the_two_lines():
    """C or higher from the DFW line (1.7), D down to the pass line (1.0), and everything under it together."""
    groups = {letter: gateway_group(letter) for letter in GRADE_ORDER}
    assert {letter for letter, group in groups.items() if group == "C or higher"} == {"A", "A-", "B+", "B", "B-", "C+", "C", "C-"}
    assert {letter for letter, group in groups.items() if group == "D"} == {"D+", "D"}
    assert {letter for letter, group in groups.items() if group == "Under 1.0"} == {"D-", "F"}
    assert (groups["P"], groups["W"]) == ("P", "W")
    # Every group passes or fails as a whole, so its label is honest whatever grades the data holds.
    for group in GATEWAY_GROUPS:
        assert len({letter_passes_gateway(letter) for letter, g in groups.items() if g == group}) == 1


def test_the_tables_follow_the_rules():
    """Each page's table lists its groups in order, with points staff can read and the rule the numbers use."""
    dfw = {row["grade"]: row for row in dfw_scale()["grades"]}
    assert list(dfw) == ["C or higher", "D", "F", "P", "W"]
    assert [grade for grade, row in dfw.items() if row["counted"]] == ["D", "F", "W"]
    assert dfw["D"]["points"] == "0.7 to under 1.7 (D-, D, D+)"
    assert dfw["C or higher"]["points"] == "1.7 and up (C- and up)"
    assert dfw["F"]["points"] == "under 0.7, or the code F"

    gateway = {row["grade"]: row for row in gateway_scale()["grades"]}
    assert list(gateway) == list(GATEWAY_GROUPS)
    assert [grade for grade, row in gateway.items() if row["counted"]] == ["C or higher", "D", "P"]
    assert gateway["D"]["points"] == "1.0 to under 1.7 (D, D+)"
    assert gateway["Under 1.0"]["points"] == "under 1.0 (D- or F), or the code F"
    assert "UW" in dfw_scale()["left_out"]
