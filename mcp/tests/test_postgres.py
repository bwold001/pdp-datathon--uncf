"""PostgreSQL only: roles, warnings, types and connection failures. Needs PDP_TEST_POSTGRES_URL.

get_database_info is a tool; the query path is dormant and called in Python.
"""

import pytest

from conftest import call, query, query_error_code
from pdp_mcp.config import Settings


def pg(url, **settings):
    return Settings(backend="postgres", postgres_url=url, max_rows=20, **settings)


def test_a_select_only_role_reads_and_gets_no_warnings(postgres):
    if not postgres["reader_url"]:
        pytest.skip("the test user can't create roles")
    reader = pg(postgres["reader_url"])
    _, info = call(reader, "get_database_info")
    assert info["database"]["healthy"] and info["warnings"] == []
    assert info["database"]["database_schema"] == postgres["schema"]
    _, result = query(reader, "SELECT COUNT(*) FROM student")
    assert result["rows"] == [[10]]
    assert query_error_code(reader, "WITH x AS (SELECT 1) DELETE FROM student") == "query_failed"


def test_a_role_that_can_write_is_warned_about(postgres):
    _, info = call(pg(postgres["url"]), "get_database_info")
    assert info["warnings"], "the test user owns the tables, so it can write them"
    assert "superuser" in info["warnings"][0] or "can write" in info["warnings"][0]


def test_postgres_column_types_are_reported(postgres):
    _, result = query(pg(postgres["url"]), "SELECT cohort, retention, gpa_group_year_1, COUNT(*) OVER () "
                                           "FROM cohort_membership LIMIT 1")
    assert [c["data_type"] for c in result["columns"]] == ["text", "bool", "float8", "int8"]


def test_an_unreachable_server_is_unavailable_without_secrets():
    settings = pg("postgresql://someone:s3cret-password@127.0.0.1:1/pdp")
    is_error, content = query(settings, "SELECT 1")
    assert is_error and content["error"]["code"] == "database_unavailable"
    assert "s3cret" not in str(content) and "127.0.0.1" not in str(content)
    _, info = call(settings, "get_database_info")
    assert not info["database"]["healthy"] and info["database"]["error"]["code"] == "database_unavailable"
    assert info["metadata"]["healthy"] and "s3cret" not in str(info)
