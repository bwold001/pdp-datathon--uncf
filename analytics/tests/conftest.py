"""Use ten for existing disclosure fixtures; display-default tests opt out explicitly."""
import pytest

@pytest.fixture(autouse=True)
def display_threshold(monkeypatch):
    """Keep arithmetic/privacy fixture expectations independent of the synthetic display default."""
    monkeypatch.setenv("UNCF_MIN_STUDENTS", "10")
