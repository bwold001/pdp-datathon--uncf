"""Existing analyses retain their own definitions, perspectives, horizons and coverage."""

import json

import pytest

from analytics.analysis_service import AnalysisService, OperationError, legacy_step
from analytics.data_access import sqlite_snapshot
from analytics.tests.analytics_fixtures import build_database, fixture_coverage
from analytics.tests.test_snapshots import add_identity


@pytest.fixture
def legacy_data(tmp_path):
    """Three hand-counted students with separate entry/completion and annual populations."""
    path = build_database(tmp_path / "legacy.sqlite")
    add_identity(path)
    return path


def execute(path, request, coverage=None):
    """Exercise the typed old-request adapter on a real borrowed source."""
    with sqlite_snapshot(path) as snapshot:
        return AnalysisService(coverage or fixture_coverage()).execute(
            legacy_step(request), snapshot
        )


def visible(evidence):
    """Read the typed legacy columns without calculating any expected values from the owner."""
    columns = [column.id for column in evidence.result.payload.columns]
    return [
        dict(zip(columns, row.cells))
        for row in evidence.result.payload.rows
        if row.status in ("ok", "provisional")
    ]


def test_entry_major_retention_preserves_known_outcome_denominator(legacy_data):
    """Two known outcomes, one retained, and one unknown outcome remain separate evidence."""
    evidence = execute(legacy_data, {"analysis": "retention", "cohort": "2022-23"})
    rows = visible(evidence)
    overall = next(
        row for row in rows if row["kind"] == "rate" and row["group"] == "overall"
    )
    assert (overall["numerator"], overall["denominator"], overall["rate"]) == (
        1,
        2,
        0.5,
    )
    assert any(row["kind"] == "exclusion" and row["count"] == 1 for row in rows)
    assert evidence.operation_id == "legacy.entry_major_retention"


def test_graduation_keeps_separate_horizons_and_unknown_completion_program(legacy_data):
    """A mature four-year result does not make six-year or inferred-program evidence observable."""
    evidence = execute(
        legacy_data,
        {
            "analysis": "graduation",
            "cohort": "2022-23",
            "credential": "B",
            "program": "chemistry_general",
        },
    )
    rows = visible(evidence)
    four = next(
        row for row in rows if row["horizon"] == "four_year" and row["kind"] == "rate"
    )
    assert (four["numerator"], four["denominator"], four["rate"]) == (1, 2, 0.5)
    assert any(
        row.status == "not_yet_observable" for row in evidence.result.payload.rows
    )
    assert any(row.status == "unknown" for row in evidence.result.payload.rows)
    assert any("exact award semester" in value.lower() for value in evidence.context)


def test_annual_enrollment_keeps_actual_enrollments_and_latest_certified_years(
    legacy_data,
):
    """Duplicate course rows cannot multiply annual distinct students."""
    evidence = execute(legacy_data, {"analysis": "enrollment"})
    rows = visible(evidence)
    assert any(row["count"] == 1 and "2022-23" in row["group"] for row in rows)
    assert "2022-23" in evidence.context and "2023-24" in evidence.context
    assert all(row["kind"] == "count" for row in rows)
    from analytics.coverage import Coverage

    unavailable = execute(legacy_data, {"analysis": "enrollment"}, Coverage())
    assert all(row.status == "unavailable" for row in unavailable.result.payload.rows)
    assert "numerator" not in json.dumps(
        [row.model_dump() for row in unavailable.result.payload.rows]
    )


def test_catalog_search_returns_distinct_gateway_candidates_and_defined_legacy_entries():
    """Candidate search offers distinctions without deciding which gateway population was meant."""
    service = AnalysisService(fixture_coverage())
    candidates = service.catalog("gateway success")["operations"]
    assert {row["id"] for row in candidates} >= {
        "gateway.math_completion",
        "gateway.english_completion",
        "gateway.course_outcomes",
    }
    assert all(row["distinctions"] for row in candidates)
    assert len(service.catalog()["operations"]) == 14
    for id in (
        "legacy.graduation",
        "legacy.entry_major_retention",
        "legacy.annual_enrollment",
    ):
        spec = service.details(id)
        assert spec["kind"] == "legacy_analysis" and not spec["supported_filters"]
    with pytest.raises(OperationError):
        service.details("unregistered")
