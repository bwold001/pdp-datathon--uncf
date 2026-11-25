"""Shared test fixtures. Tests that need data point DATABASE_URL at their own SQLite file."""

import os

# Chat ships turned off. The tests exercise its routes, so turn it on before the app is built;
# tests of the switched-off behavior set it back to False themselves.
os.environ.setdefault("UNCF_CHAT_ENABLED", "true")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture
def client() -> TestClient:
    """An in-process client for the local API."""
    with TestClient(app) as test_client:
        yield test_client
