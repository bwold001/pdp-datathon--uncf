"""Timeout responses must never leave a calculation holding the upload database."""

import sqlite3
from threading import Event

import pytest
from analytics.tests.analytics_fixtures import build_database
from api.analyses import get_service

from app.chat import routes
from app.chat.routes import get_chat_client
from app.core.config import settings
from app.main import app
from app.services.analytics import database


@pytest.fixture
def cancellation_case(tmp_path, monkeypatch):
    """Use actual read-only connections against an isolated uploaded-data fixture."""
    path = build_database(tmp_path / "uploaded.sqlite")
    monkeypatch.setattr(settings, "DATABASE_URL", f"sqlite:///{path}")
    monkeypatch.setattr(routes, "REQUEST_TIMEOUT_SECONDS", 0.05)
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


def confirm(client):
    """Explicitly approve the exact scope; cancellation is independent of model behavior."""
    return client.post(
        "/api/v1/chat",
        json={
            "prompt": "Confirmed full cohort",
            "confirmed": [{"analysis": "retention", "cohort": "2022-23"}],
        },
    )


def test_timeout_waits_for_worker_transaction_cleanup(client, cancellation_case):
    """Even work between SQL statements must close its transaction before the 502."""
    started, finished = Event(), Event()

    class SlowService:
        """Hold a real read transaction during a bounded non-SQL calculation."""

        def clarify(self, request):
            """The complete confirmed scope needs no further choices."""
            return None

        def analyze(self, request):
            """Simulate Python-side processing that cannot be interrupted by SQLite."""
            try:
                with database() as db:
                    db.execute("SELECT * FROM cohort_membership").fetchall()
                    started.set()
                    Event().wait(0.15)
            finally:
                finished.set()

    app.dependency_overrides[get_service] = SlowService
    response = confirm(client)
    assert response.status_code == 502
    assert started.is_set() and finished.is_set()
    assert_writable(cancellation_case)


def test_deadline_interrupts_running_sql_and_releases_read_lock(client, cancellation_case):
    """VM cancellation aborts a long query rather than merely abandoning its future."""
    finished = Event()

    class LongQuery:
        """An intentionally expensive trusted query standing in for a slow calculation."""

        def clarify(self, request):
            """The test request is fully specified."""
            return None

        def analyze(self, request):
            """Acquire a snapshot, then run SQL that cannot finish before the deadline."""
            try:
                with database() as db:
                    db.execute("SELECT * FROM cohort_membership").fetchall()
                    db.execute("""
                        WITH RECURSIVE sequence(n) AS (
                            SELECT 1 UNION ALL SELECT n+1 FROM sequence WHERE n<1000000000
                        ) SELECT SUM(n) FROM sequence
                    """).fetchall()
            finally:
                finished.set()

    app.dependency_overrides[get_service] = LongQuery
    response = confirm(client)
    assert response.status_code == 502
    assert finished.is_set()
    assert_writable(cancellation_case)
