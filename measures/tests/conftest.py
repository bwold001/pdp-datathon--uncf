"""Test settings for measures/: these tests check the hiding rules, so they run with groups under 10 hidden."""
import pytest


@pytest.fixture(autouse=True)
def hide_groups_under_ten(monkeypatch):
    """Run each test as a real-data deployment would: UNCF_MIN_STUDENTS=10. test_min_students.py checks the default."""
    monkeypatch.setenv("UNCF_MIN_STUDENTS", "10")
