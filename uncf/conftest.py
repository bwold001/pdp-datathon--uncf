"""Test settings for uncf/. Tests marked `slow` read the real normalized data; make check-fast skips them."""


def pytest_configure(config):
    """Register the slow marker so pytest doesn't warn about it."""
    config.addinivalue_line("markers", "slow: reads the real normalized data; make check-fast leaves it out")
