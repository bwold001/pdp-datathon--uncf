"""Small synthetic comparisons remain visible regardless of obsolete settings."""
from __future__ import annotations

import sqlite3

import pytest

from gap_finder.compare import compare
from gap_finder.gateway import count_row
from gap_finder.models import GapStatus
from gap_finder.save_results import CREATE_TABLE, save_gaps


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


def test_legacy_setting_cannot_hide_small_groups(monkeypatch):
    """An old threshold of ten cannot hide a three-student comparison."""
    monkeypatch.setenv("UNCF_MIN_STUDENTS", "10")
    (gap,) = [g for g in compare(three_against_twenty_seven()) if g.group_values]
    assert gap.status == GapStatus.OK and gap.denominator == 3
    assert gap.rank_by_gap == 1


def test_a_table_with_an_old_threshold_is_rebuilt(tmp_path):
    """A persisted threshold of ten cannot prevent saving newly visible small results."""
    database = tmp_path / "gaps.sqlite"
    with sqlite3.connect(database) as connection:
        connection.execute(CREATE_TABLE.format(min_students=10))
    save_gaps(compare(three_against_twenty_seven()), database)
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT status, denominator FROM equity_gaps WHERE group_values = 'small'").fetchone() == ("ok", 3)
