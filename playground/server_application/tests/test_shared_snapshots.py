"""Configured runtime snapshots reuse the same source as existing deterministic APIs."""

import pytest
from analytics.provenance import DataUnavailable, VersionUnavailable
from analytics.tests.test_snapshots import add_identity

from app.services.analytics import database_snapshot, get_service
from tests.test_analytics_database import configured_data as configured_data


def test_configured_snapshot_exposes_both_row_views_and_legacy_binding(configured_data):
    """The runtime never substitutes the standalone extract for the configured upload."""
    path, _ = configured_data
    add_identity(path)
    with database_snapshot() as snapshot:
        assert snapshot.named.execute("SELECT COUNT(*) AS n FROM student").fetchone() == {"n": 3}
        assert snapshot.positional.execute("SELECT COUNT(*) FROM student").fetchone() == (3,)
        reply = (
            get_service()
            .for_snapshot(snapshot)
            .analyze({"analysis": "retention", "cohort": "2022-23"})
        )
        assert reply.receipts[0].rows[0].rate == 0.5
    with pytest.raises(DataUnavailable, match="closed"):
        snapshot.named.execute("SELECT 1")


def test_configured_v2_snapshot_refuses_missing_build_identity(configured_data):
    """An old uploaded extract must be rebuilt for v2 rather than borrowing local metadata."""
    with pytest.raises(VersionUnavailable), database_snapshot():
        pass
