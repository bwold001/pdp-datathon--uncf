"""Checks the gap finder follows UNCF_MIN_STUDENTS: by default a group of 3 is compared; set to 10, it's hidden."""
from __future__ import annotations

import sqlite3

import pytest

from gap_finder.compare import compare
from gap_finder.gateway import count_row
from gap_finder.models import GapStatus
from gap_finder.save_results import save_gaps


@pytest.fixture
def default(monkeypatch):
    """The setting as a fresh deployment has it: not set."""
    monkeypatch.delenv("UNCF_MIN_STUDENTS", raising=False)


def three_against_twenty_seven():
    """Everyone: 30 students, 15 retained. The group: 3 students, 1 retained."""
    return [count_row("retention", "2023-24", None, 15, 30), count_row("retention", "2023-24", "small", 1, 3)]


def test_a_group_of_three_is_compared_by_default(default):
    """With nothing hidden, the 3 students get their rate, everyone else's and the gap."""
    (gap,) = [g for g in compare(three_against_twenty_seven()) if g.group_values]
    assert gap.status == GapStatus.OK
    assert (gap.numerator, gap.denominator, gap.comparison_numerator, gap.comparison_denominator) == (1, 3, 14, 27)


def test_the_same_group_hides_at_ten(monkeypatch):
    """Set to 10, as for real student data, the 3 students are hidden again."""
    monkeypatch.setenv("UNCF_MIN_STUDENTS", "10")
    (gap,) = [g for g in compare(three_against_twenty_seven()) if g.group_values]
    assert gap.status == GapStatus.SUPPRESSED and gap.denominator is None


def test_a_table_saved_at_ten_is_rebuilt_for_the_default(monkeypatch, tmp_path):
    """The saved table checks the minimum it was made with, so a change of setting rebuilds it instead of failing."""
    database = tmp_path / "gaps.sqlite"
    monkeypatch.setenv("UNCF_MIN_STUDENTS", "10")
    save_gaps(compare(three_against_twenty_seven()), database)
    monkeypatch.delenv("UNCF_MIN_STUDENTS")
    save_gaps(compare(three_against_twenty_seven()), database)
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT status, denominator FROM equity_gaps WHERE group_values = 'small'").fetchone() == ("ok", 3)
