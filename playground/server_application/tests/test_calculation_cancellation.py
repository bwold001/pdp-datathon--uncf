"""Timeout responses must never leave a calculation holding the upload database."""

import sqlite3
from threading import Event

import pytest
from analytics.analysis_service import AnalysisService
from analytics.execution import CURRENT, CalculationCancelled, check_cancelled
from analytics.plan_service import PlanService
from analytics.service import AnalyticsService
from analytics.tests.analytics_fixtures import build_database, fixture_coverage
from analytics.tests.test_snapshots import add_identity
from api.analyses import get_service

from app.chat.routes import get_chat_client
from app.core.config import settings
from app.main import app


@pytest.fixture
def cancellation_case(tmp_path, monkeypatch):
    """Use actual read-only connections against an isolated uploaded-data fixture."""
    path = build_database(tmp_path / "uploaded.sqlite")
    add_identity(path)
    monkeypatch.setattr(settings, "DATABASE_URL", f"sqlite:///{path}")
    previous = app.dependency_overrides.copy()
    app.dependency_overrides[get_chat_client] = lambda: None
    yield path
    app.dependency_overrides.clear()
    app.dependency_overrides.update(previous)


def assert_writable(path):
    """A separate writer must be able to commit immediately after the timeout."""
    connection = sqlite3.connect(path, timeout=0.02)
    try:
        connection.execute("UPDATE cohort_membership SET retention=1")
        connection.commit()
    finally:
        connection.close()


def confirm(client, path):
    """Confirm a current exact legacy-adapter scope through the v2 transport."""
    catalog = PlanService(AnalyticsService(path, fixture_coverage())).catalog()
    plan = {
        "kind": "executable",
        "catalog_version": catalog.catalog_version,
        "snapshot_ref": catalog.snapshot_ref,
        "steps": [
            {
                "kind": "legacy_analysis",
                "operation_id": "legacy.entry_major_retention",
                "step_id": "retention",
                "parameters": {"cohort": "2022-23"},
            }
        ],
    }
    return client.post(
        "/api/v1/chat", json={"protocol_version": 2, "prompt": "confirmed", "confirmed": plan}
    )


def test_timeout_waits_for_worker_transaction_cleanup(client, cancellation_case, monkeypatch):
    """Python-side cancellation waits for the borrowed snapshot to close before responding."""
    started, finished = Event(), Event()

    def slow(self, step, snapshot):
        """Expire the budget only after the worker acquires a real read lock."""
        try:
            snapshot.named.execute("SELECT * FROM cohort_membership").fetchall()
            started.set()
            CURRENT.get().deadline = 0
            check_cancelled()
        finally:
            finished.set()

    app.dependency_overrides[get_service] = lambda: AnalyticsService(
        cancellation_case, fixture_coverage()
    )
    monkeypatch.setattr(AnalysisService, "execute", slow)
    response = confirm(client, cancellation_case)
    assert response.status_code == 200 and response.json()["issues"][0]["code"] == "timeout"
    assert started.is_set() and finished.is_set()
    assert_writable(cancellation_case)


def test_deadline_interrupts_running_sql_and_releases_read_lock(
    client, cancellation_case, monkeypatch
):
    """VM cancellation stops a running statement before the response releases control."""
    finished = Event()

    def long_query(self, step, snapshot):
        """Expire the deadline inside SQL and require a real SQLite interruption."""

        def expire_deadline(value):
            """Exhaust the budget once SQLite has started evaluating the statement."""
            if value == 10:
                CURRENT.get().deadline = 0
            return value

        snapshot.named._session.raw.create_function("expire_deadline", 1, expire_deadline)
        try:
            with pytest.raises(CalculationCancelled) as interrupted:
                snapshot.named.execute("""
                    WITH RECURSIVE sequence(n) AS (
                        SELECT 1 UNION ALL SELECT n+1 FROM sequence WHERE n<1000
                    ) SELECT SUM(expire_deadline(n)) FROM sequence
                """).fetchall()
            assert isinstance(interrupted.value.__context__, sqlite3.OperationalError)
            assert str(interrupted.value.__context__) == "interrupted"
            raise interrupted.value
        finally:
            finished.set()

    app.dependency_overrides[get_service] = lambda: AnalyticsService(
        cancellation_case, fixture_coverage()
    )
    monkeypatch.setattr(AnalysisService, "execute", long_query)
    response = confirm(client, cancellation_case)
    assert response.status_code == 200 and response.json()["issues"][0]["code"] == "timeout"
    assert finished.is_set()
    assert_writable(cancellation_case)


def test_deadline_during_validation_does_not_start_calculation(
    client, cancellation_case, monkeypatch
):
    """A setup timeout closes its snapshot without dispatching an analysis."""
    original_catalog = PlanService._catalog
    validated = Event()

    def expire_during_validation(self, snapshot):
        """Expire only the request's catalog lookup, after its snapshot has opened."""
        if CURRENT.get() is not None:
            validated.set()
            CURRENT.get().deadline = 0
        return original_catalog(self, snapshot)

    def forbidden(*args, **kwargs):
        """Reject calculation dispatch after the validation deadline expires."""
        pytest.fail("Calculation started after validation timed out")

    app.dependency_overrides[get_service] = lambda: AnalyticsService(
        cancellation_case, fixture_coverage()
    )
    monkeypatch.setattr(PlanService, "_catalog", expire_during_validation)
    monkeypatch.setattr(AnalysisService, "execute", forbidden)
    response = confirm(client, cancellation_case)
    assert response.status_code == 200 and response.json()["issues"][0]["code"] == "timeout"
    assert validated.is_set()
    assert_writable(cancellation_case)
