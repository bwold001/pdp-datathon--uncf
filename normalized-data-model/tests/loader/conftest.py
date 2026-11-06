"""Fixtures the loader tests share."""

import os
import secrets

import pytest

POSTGRES_URL = os.environ.get("PDP_TEST_POSTGRES_URL")


@pytest.fixture
def postgres():
    """A connection URL whose search_path is a new, empty schema, dropped after the test."""
    psycopg = pytest.importorskip("psycopg")
    schema = f"pdp_test_{secrets.token_hex(4)}"
    with psycopg.connect(POSTGRES_URL, autocommit=True) as connection:
        connection.execute(f'CREATE SCHEMA "{schema}"')
    separator = "&" if "?" in POSTGRES_URL else "?"
    url = f"{POSTGRES_URL}{separator}options=-csearch_path%3D{schema}"
    yield url
    with psycopg.connect(POSTGRES_URL, autocommit=True) as connection:
        connection.execute(f'DROP SCHEMA "{schema}" CASCADE')
