"""Checks the shared letter grade scale, and that the table pages show follows the DFW and gateway rules."""
from __future__ import annotations

import pytest

from measures.breakdowns.grade_scale import grade_scale
from measures.calculations.dfw import DFW_BELOW, DFW_GRADES, grade_outcomes
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


def test_the_scale_table_follows_the_rules():
    """Every final grade appears once, in order, with points staff can read and the same rules the numbers use."""
    scale = grade_scale()
    rows = scale["grades"]
    assert [row["grade"] for row in rows] == list(GRADE_ORDER)
    assert [row["grade"] for row in rows if row["dfw"]] == list(DFW_GRADES)
    assert all(row["gateway_pass"] == letter_passes_gateway(row["grade"]) for row in rows)
    points = {row["grade"]: row["points"] for row in rows}
    assert (points["A"], points["C-"], points["D-"]) == ("4.0", "1.7 to under 2.0", "0.7 to under 1.0")
    assert points["F"] == "under 0.7, or the code F"
    assert "UW" in scale["left_out"]
    # The bands meet with no gap: each letter's lowest points are the next letter's upper end.
    for (_, lowest), (letter, _) in zip(LETTER_SCALE, LETTER_SCALE[1:]):
        assert points[letter].endswith(f"under {lowest:.1f}")
