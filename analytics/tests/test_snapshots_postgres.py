"""Exercise real PostgreSQL row views and page/legacy readers when a test server is configured."""

import os
import sqlite3
from uuid import uuid4

import pytest

from analytics.coverage import Coverage
from analytics.data_access import connection_snapshot, sqlite_snapshot
from analytics.service import AnalyticsService
from analytics.tests.test_snapshots import database as database
from measures.breakdowns.credit_momentum import credit_momentum
from measures.models import Cohort, Measure
from measures.run_measures import run_measure


def test_postgres_mixed_readers_use_one_read_only_repeatable_read_transaction(database):
    """Real driver behavior must agree with SQLite; a skipped environment proves nothing."""
    url = os.getenv("PDP_TEST_POSTGRES_URL")
    if not url:
        if os.getenv("PDP_REQUIRE_POSTGRES") == "1":
            pytest.fail("PDP_REQUIRE_POSTGRES=1 needs PDP_TEST_POSTGRES_URL")
        pytest.skip("PDP_TEST_POSTGRES_URL is not configured")
    psycopg = pytest.importorskip("psycopg")
    schema = "snapshot_" + uuid4().hex
    with psycopg.connect(url, autocommit=True) as admin:
        admin.execute(f'CREATE SCHEMA "{schema}"')
        try:
            admin.execute(f'SET search_path TO "{schema}"')
            with sqlite3.connect(database) as source:
                tables = source.execute("SELECT name, sql FROM sqlite_master WHERE type='table'").fetchall()
                for name, sql in tables:
                    sql = sql.replace("retention INTEGER", "retention BOOLEAN").replace("persistence INTEGER", "persistence BOOLEAN")
                    admin.execute(sql)
                    columns = [r[1] for r in source.execute(f'PRAGMA table_info("{name}")')]
                    records = [tuple(bool(v) if c in ("retention", "persistence") and v is not None else v
                                     for c, v in zip(columns, row)) for row in source.execute(f'SELECT * FROM "{name}"')]
                    with admin.cursor() as cursor:
                        cursor.executemany(f'INSERT INTO "{name}" VALUES ({", ".join(["%s"] * len(columns))})', records)
            connection = psycopg.connect(url, options=f"-csearch_path={schema}")
            factory = connection.row_factory
            with connection_snapshot(connection, postgres=True) as snapshot:
                with sqlite_snapshot(database) as local:
                    assert snapshot.identity == local.identity
                assert snapshot.named.execute("SHOW transaction_read_only").fetchone()["transaction_read_only"] == "on"
                assert snapshot.positional.execute("SHOW transaction_isolation").fetchone() == ("repeatable read",)
                (measure,) = run_measure(Measure.RETENTION, [Cohort.of("2023-24")], database=snapshot.positional)
                legacy = AnalyticsService(None, Coverage(suppression_threshold=1)).for_snapshot(snapshot).analyze({"analysis": "retention", "cohort": "2023-24"})
                assert measure.metric_rate == legacy.receipts[0].rows[0].rate == .5
                assert credit_momentum("2023-24", snapshot=snapshot)["credits"]["avg_earned"] == 6.0
                assert connection.row_factory is factory
                assert snapshot.named.execute("SELECT '?' AS marker, ? AS chosen", (7,)).fetchone() == {"marker": "?", "chosen": 7}
            assert connection.closed
            from contextlib import contextmanager
            from analytics.contracts_v2 import ExecutablePlan
            from analytics.plan_service import PlanService

            @contextmanager
            def plan_source():
                """Give each full-plan request its own actual PostgreSQL transaction owner."""
                with connection_snapshot(psycopg.connect(url, options=f"-csearch_path={schema}"), postgres=True) as owned:
                    yield owned

            facade = PlanService(AnalyticsService(None, Coverage(), snapshot_factory=plan_source))
            catalog = facade.catalog()
            plan = ExecutablePlan.model_validate({"kind": "executable", "catalog_version": catalog.catalog_version,
                "snapshot_ref": catalog.snapshot_ref, "steps": [{"kind": "defined_measure", "step_id": "retention",
                "operation_id": "retention.rate", "parameters": {"cohort": "2023-24", "retention_type": "school"}}]})
            executed = facade.execute_plan(plan)
            assert executed.outcome == "complete" and executed.receipts[0].result.payload.value == .5
        finally:
            admin.execute(f'DROP SCHEMA "{schema}" CASCADE')
