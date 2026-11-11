"""Checks #35's promise: the same cohort, filters and retention type give the same numbers on every route."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api import route
from measures.run_measures import DEFAULT_DATABASE

needs_data = pytest.mark.skipif(not DEFAULT_DATABASE.exists(), reason="the normalized data isn't loaded")


@pytest.mark.slow
@needs_data
@pytest.mark.parametrize("retention_type", ["school", "federal"])
@pytest.mark.parametrize("filters", [{}, {"pell": "Y"}, {"cohort_term": "Fall", "race": "Black or African American"}, {"enrollment_type": "First-time"}])
def test_every_page_and_the_measure_route_agree_on_retention(retention_type, filters):
    """The issue's done criterion: the same cohort, filters and type give the same retention everywhere."""
    route.clear_cache()
    client = TestClient(route.create_app())
    params = {"cohort": "2022-23", "retention_type": retention_type, **filters}
    everyone = client.get("/api/v1/uncf/measures/retention", params=params).json()["rows"][0]
    expected = (everyone["numerator"], everyone["denominator"])
    paths = client.get("/api/v1/uncf/student-paths", params=params).json()["retention"]
    gateway = client.get("/api/v1/uncf/gateway", params=params).json()["cohort_retention"]
    credits = client.get("/api/v1/uncf/credit-momentum", params=params).json()["retention"]
    for page in (paths, gateway, credits):
        assert (page["retained"], page["students"]) == expected
        assert page["type"] == retention_type


@pytest.mark.slow
@needs_data
def test_dfw_page_and_measure_route_agree():
    """The DFW page's everyone tile and the measure route's dfw_rate row are the same numbers, filters included."""
    route.clear_cache()
    client = TestClient(route.create_app())
    for filters in [{}, {"pell": "Y"}, {"gender": "F", "age_band": "20 and younger"}]:
        params = {"cohort": "2023-24", **filters}
        page = client.get("/api/v1/uncf/dfw", params=params).json()["everyone"]
        row = client.get("/api/v1/uncf/measures/dfw_rate", params=params).json()["rows"][0]
        assert (page["num"], page["den"]) == (row["numerator"], row["denominator"])
        assert page["split"]["grades"] == row["split"]

