"""Test settings for api/. Tests marked `slow` read the real normalized data; make check-fast skips them.

The obsolete minimum is set to 10 to prove it cannot hide small results.
"""
import pytest


def pytest_configure(config):
    """Register the slow marker so pytest doesn't warn about it."""
    config.addinivalue_line("markers", "slow: reads the real normalized data; make check-fast leaves it out")


@pytest.fixture(autouse=True)
def legacy_threshold_is_ignored(monkeypatch):
    """Prove an old environment setting cannot reenable size-based suppression."""
    monkeypatch.setenv("UNCF_MIN_STUDENTS", "10")
