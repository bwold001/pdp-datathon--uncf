"""Test settings for the gap finder. Tests marked `slow` load the full mock data; make check-fast leaves them out.

The obsolete minimum is set to 10 to prove it cannot hide small results.
"""
import pytest


def pytest_configure(config):
    """Register the slow marker."""
    config.addinivalue_line("markers", "slow: loads the full mock data; make check-fast leaves it out")


@pytest.fixture(autouse=True)
def legacy_threshold_is_ignored(monkeypatch):
    """Prove an old environment setting cannot reenable size-based suppression."""
    monkeypatch.setenv("UNCF_MIN_STUDENTS", "10")
