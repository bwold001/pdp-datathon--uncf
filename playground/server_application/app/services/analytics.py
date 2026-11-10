"""Connect shared analytics to the database actually loaded in Playground."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path

import psycopg
from analytics.service import AnalyticsService, DataUnavailable
from api.analyses import get_service as standalone_service
from psycopg.rows import dict_row
from sqlalchemy.engine import make_url

from app.core.config import settings


class QueryConnection:
    """Adapt only the shared service's static parameterized queries to DB-API drivers."""

    def __init__(self, connection, postgres):
        """Keep values parameterized; tools cannot submit SQL to this adapter."""
        self.connection = connection
        self.postgres = postgres

    def execute(self, sql, parameters=()):
        """Shared queries use question-mark placeholders, never generated query text."""
        return self.connection.execute(sql.replace("?", "%s") if self.postgres else sql, parameters)


@contextmanager
def database():
    """Read a current snapshot and close it on success, failure or cancellation."""
    url = make_url(settings.DATABASE_URL)
    postgres = not url.drivername.startswith("sqlite")
    try:
        if postgres:
            connection = psycopg.connect(
                url.set(drivername="postgresql").render_as_string(hide_password=False),
                row_factory=dict_row,
                connect_timeout=10,
            )
        else:
            path = Path(url.database or "").resolve()
            connection = sqlite3.connect(f"{path.as_uri()}?mode=ro", uri=True, timeout=10)
            connection.row_factory = sqlite3.Row
        try:
            if postgres:
                connection.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
                connection.execute("SET LOCAL statement_timeout = '10s'")
            else:
                connection.execute("PRAGMA query_only = ON")
                connection.execute("BEGIN")
            yield QueryConnection(connection, postgres)
        finally:
            connection.rollback()
            connection.close()
    except (sqlite3.Error, psycopg.Error, OSError) as error:
        raise DataUnavailable("The configured Playground data is unavailable") from error


def get_service() -> AnalyticsService:
    """Share coverage declarations with the standalone API, never its database path."""
    return AnalyticsService(None, standalone_service().coverage, connection_factory=database)
