"""Runs the same checks on PostgreSQL when PDP_TEST_POSTGRES_URL points at a server.

With PDP_REQUIRE_POSTGRES=1 (CI sets it) a missing server or psycopg fails instead of skipping.
"""
import os
from pathlib import Path

import pytest

from measures.models import Cohort, GroupBy, GroupDimension, Measure, Status
from measures.run_measures import run_measure

FIXTURE = Path(__file__).parent / "fixture.sql"
SCHEMA = f"measures_test_{os.getpid()}"  # one per worker process, so parallel tests never share it or touch the data model's tables


def give_up(reason: str) -> None:
    """Skip the test, or fail it when PostgreSQL is required."""
    if os.environ.get("PDP_REQUIRE_POSTGRES") == "1":
        pytest.fail(f"PDP_REQUIRE_POSTGRES=1, but {reason}")
    pytest.skip(reason)


@pytest.fixture
def pg_database():
    """The tiny database in its own PostgreSQL schema, dropped afterwards."""
    url = os.environ.get("PDP_TEST_POSTGRES_URL")
    if not url:
        give_up("PDP_TEST_POSTGRES_URL is not set")
    try:
        import psycopg
    except ImportError:
        give_up("psycopg is not installed")
    connection = psycopg.connect(url, autocommit=True)
    connection.execute(f"DROP SCHEMA IF EXISTS {SCHEMA} CASCADE")
    connection.execute(f"CREATE SCHEMA {SCHEMA}")
    connection.execute(f"SET search_path TO {SCHEMA}")
    connection.execute(FIXTURE.read_text(encoding="utf-8"))
    yield connection
    connection.execute(f"DROP SCHEMA {SCHEMA} CASCADE")
    connection.close()


def find(results, label):
    """The one row whose group has this label."""
    rows = [r for r in results if r.group.label == label]
    assert len(rows) == 1, label
    return rows[0]


def test_retention_and_persistence_on_postgres(pg_database):
    cohort = Cohort.of("2022-23")
    retention = find(run_measure(Measure.RETENTION, [cohort], database=pg_database), "everyone")
    assert (retention.numerator, retention.denominator, retention.n_excluded) == (16, 20, 4)
    persistence = find(run_measure(Measure.PERSISTENCE, [cohort], database=pg_database), "everyone")
    assert (persistence.numerator, persistence.denominator) == (5, 20)


def test_groups_and_pooling_on_postgres(pg_database):
    by_term = run_measure(Measure.RETENTION, [Cohort.of("2022-23")], [GroupBy.of(GroupDimension.COHORT_TERM)], database=pg_database)
    assert (find(by_term, "cohort_term=Fall").numerator, find(by_term, "cohort_term=Fall").denominator) == (14, 14)

    by_age = run_measure(Measure.RETENTION, [Cohort.of("2022-23")], [GroupBy.of(GroupDimension.AGE_BAND)], database=pg_database)
    assert find(by_age, "age_band=> 20-24").denominator == 12

    pooled = run_measure(Measure.RETENTION, [Cohort.of("2022-23", "2023-24")], database=pg_database)
    assert (pooled[0].numerator, pooled[0].denominator) == (22, 32)

    unseen = run_measure(Measure.RETENTION, [Cohort.of("2024-25")], database=pg_database)
    assert unseen[0].status == Status.NOT_YET_OBSERVABLE

    # A pool that includes a year with no answers yet can't be read yet either.
    partly = run_measure(Measure.RETENTION, [Cohort.of("2023-24", "2024-25")], database=pg_database)
    assert partly[0].status == Status.NOT_YET_OBSERVABLE

    # Blank and unlisted values count as UNKNOWN: pell 'U' for students 45 to 48.
    by_pell = run_measure(Measure.RETENTION, [Cohort.of("2024-25")], [GroupBy.of(GroupDimension.PELL)], database=pg_database)
    assert find(by_pell, "pell=UNKNOWN").status == Status.NOT_YET_OBSERVABLE


def test_gateway_on_postgres(pg_database):
    cohort = Cohort.of("2022-23")
    math = find(run_measure(Measure.GATEWAY_MATH, [cohort], database=pg_database), "everyone")
    assert (math.numerator, math.denominator) == (12, 20)
    english = find(run_measure(Measure.GATEWAY_ENGLISH, [cohort], database=pg_database), "everyone")
    assert (english.numerator, english.denominator) == (10, 24)


def test_dfw_on_postgres(pg_database):
    row = find(run_measure(Measure.DFW_RATE, [Cohort.of("2022-23")], database=pg_database), "everyone")
    assert (row.numerator, row.denominator, row.n_excluded) == (9, 25, 2)  # the 1.7 is a C-, which passes


def test_credit_completion_on_postgres(pg_database):
    # PostgreSQL sums the ratios as decimals. They must come back as the same numbers as on SQLite.
    row = find(run_measure(Measure.CREDIT_COMPLETION, [Cohort.of("2022-23")], database=pg_database), "everyone")
    assert (row.numerator, row.denominator, row.metric_rate, row.n_excluded) == (11, 18, 0.6111, 4)


def test_dfw_by_course_on_postgres(pg_database):
    results = run_measure(Measure.DFW_RATE, [Cohort.of("2022-23")], [GroupBy.of(GroupDimension.COURSE)], database=pg_database)
    english = find(results, "course=ENGL 1302")
    assert (english.numerator, english.denominator) == (6, 22)  # the 1.7 is a C-, which passes
