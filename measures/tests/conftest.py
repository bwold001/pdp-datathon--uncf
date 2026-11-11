"""Test settings for measures/: an obsolete threshold must not hide small results."""
import pytest


@pytest.fixture(autouse=True)
def legacy_threshold_is_ignored(monkeypatch):
    """Prove an old environment setting cannot reenable size-based suppression."""
    monkeypatch.setenv("UNCF_MIN_STUDENTS", "10")
