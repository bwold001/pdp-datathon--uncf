"""Test settings for api/. Tests marked `slow` read the real normalized data; make check-fast skips them.

These tests check the hiding rules, so they run with groups under 10 hidden (UNCF_MIN_STUDENTS=10).
"""
import pytest


def pytest_configure(config):
    """Register the slow marker so pytest doesn't warn about it."""
    config.addinivalue_line("markers", "slow: reads the real normalized data; make check-fast leaves it out")


@pytest.fixture(autouse=True)
def hide_groups_under_ten(monkeypatch):
    """Run each test as a real-data deployment would. Tests of the default unset UNCF_MIN_STUDENTS themselves."""
    monkeypatch.setenv("UNCF_MIN_STUDENTS", "10")
