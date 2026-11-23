"""Shared test fixtures. Tests that need data point DATABASE_URL at their own SQLite file."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """An in-process client for the local API."""
    with TestClient(app) as test_client:
        yield test_client
