"""Test settings shared by every test folder.

The PostgreSQL tests are marked `postgres`; a test that uses the `postgres` fixture is marked
for you. Without a server (PDP_TEST_POSTGRES_URL) or psycopg they skip, so the tests run on any
machine. With PDP_REQUIRE_POSTGRES=1, which `task check`, `task test:postgres` and CI set, a
PostgreSQL test that skips fails instead, so a missing database can't pass for a working one.
An expected failure (xfail) stays one.

Tests marked `slow` run on the full mock data. `make check-fast` leaves them out.
"""

import os

import pytest


def pytest_configure(config):
    config.addinivalue_line("markers", "postgres: needs a PostgreSQL server (PDP_TEST_POSTGRES_URL) and psycopg")
    config.addinivalue_line("markers", "slow: runs on the full mock data; make check-fast leaves it out")


@pytest.hookimpl(tryfirst=True)  # before `-m postgres` picks the tests to run
def pytest_collection_modifyitems(items):
    for item in items:
        if "postgres" in getattr(item, "fixturenames", ()):
            item.add_marker("postgres")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.skipped and not hasattr(report, "wasxfail") and item.get_closest_marker("postgres") \
            and os.environ.get("PDP_REQUIRE_POSTGRES") == "1":
        reason = report.longrepr[2] if isinstance(report.longrepr, tuple) else report.longrepr
        report.outcome = "failed"
        report.longrepr = f"PDP_REQUIRE_POSTGRES=1, but this PostgreSQL test skipped: {reason}"
