"""Connect shared read snapshots to the database explicitly selected by Playground."""

from contextlib import contextmanager
from pathlib import Path

import psycopg
from analytics.data_access import connection_snapshot, sqlite_snapshot
from analytics.execution import check_cancelled, statement_timeout_ms
from analytics.service import AnalyticsService, DataUnavailable
from api.analyses import get_service as standalone_service
from sqlalchemy.engine import make_url

from app.core.config import settings


@contextmanager
def _configured_snapshot(*, require_identity):
    """Own one configured transaction without falling back to a standalone extract."""
    check_cancelled()
    try:
        url = make_url(settings.DATABASE_URL)
        if url.drivername.startswith("sqlite"):
            path = Path(url.database or "").resolve()
            with sqlite_snapshot(path, require_identity=require_identity) as snapshot:
                yield snapshot
        elif url.drivername.startswith("postgresql"):
            connection = psycopg.connect(
                url.set(drivername="postgresql").render_as_string(hide_password=False),
                connect_timeout=max(1, (statement_timeout_ms() + 999) // 1000),
            )
            with connection_snapshot(
                connection, postgres=True, require_identity=require_identity
            ) as snapshot:
                yield snapshot
        else:
            raise DataUnavailable("The configured database backend is unsupported.")
    except (psycopg.Error, OSError, ValueError) as error:
        check_cancelled()
        raise DataUnavailable("The configured Playground data is unavailable") from error


@contextmanager
def database():
    """Preserve the legacy named-row provider without requiring new build metadata."""
    with _configured_snapshot(require_identity=False) as snapshot:
        yield snapshot.named


@contextmanager
def database_snapshot():
    """Supply both row views and persisted identity for one v2 execution snapshot."""
    with _configured_snapshot(require_identity=True) as snapshot:
        yield snapshot


def get_service() -> AnalyticsService:
    """Share coverage with the standalone API while honoring the configured source."""
    return AnalyticsService(
        None,
        standalone_service().coverage,
        connection_factory=database,
        snapshot_factory=database_snapshot,
    )
