"""Test settings for the gap finder. Tests marked `slow` load the full mock data; make check-fast leaves them out.

These tests check the hiding rules, so they run with groups under 10 hidden (UNCF_MIN_STUDENTS=10).
"""
import pytest


def pytest_configure(config):
    """Register the slow marker."""
    config.addinivalue_line("markers", "slow: loads the full mock data; make check-fast leaves it out")


@pytest.fixture(autouse=True)
def hide_groups_under_ten(monkeypatch):
    """Run each test as a real-data deployment would. Tests of the default unset UNCF_MIN_STUDENTS themselves."""
    monkeypatch.setenv("UNCF_MIN_STUDENTS", "10")
