"""Checks that nothing sent through the dormant execute_query path can change the database, on every backend.

execute_query isn't a tool in any access mode (test_contracts.py checks that), so these call it in
Python. They keep its read-only safeguards proven for a later student-level access decision.

Each attempt must come back as an error, and afterwards the database must be exactly what it was:
the same bytes for SQLite, the same tables and row counts for PostgreSQL.
"""

import hashlib

import pytest

from conftest import query, table_counts

# Refused before the database sees them, by the statement check.
NOT_A_QUERY = [
    "INSERT INTO institution VALUES (99, 'x', 0)",
    "UPDATE student SET gender = 'M'",
    "DELETE FROM student",
    "DROP TABLE student",
    "CREATE TABLE x (a INTEGER)",
    "ALTER TABLE student ADD COLUMN x TEXT",
    "TRUNCATE student",
    "ATTACH DATABASE 'other.sqlite' AS other",
    "PRAGMA writable_schema = 1",
    "VACUUM",
    "BEGIN",
    "COPY student TO STDOUT",
    "SET default_transaction_read_only = off",
    "/* SELECT */ DELETE FROM student",
    "-- SELECT\nDELETE FROM student",
    "   delete from student",
]

# Pass the statement check: the database itself must refuse them.
LOOKS_LIKE_A_QUERY = {
    "both": [
        "SELECT 1; DELETE FROM student",
        "SELECT 1; SELECT 2",
        "WITH gone AS (DELETE FROM student RETURNING student_id) SELECT COUNT(*) FROM gone",
        "WITH x AS (SELECT 1) DELETE FROM student",
        "WITH x AS (SELECT 1) INSERT INTO institution VALUES (99, 'x', false)",
        "WITH x AS (SELECT 1) UPDATE student SET gender = 'M'",
    ],
    "sqlite": [
        "SELECT load_extension('mod_spatialite')",
        "SELECT * FROM pragma_table_info('student')",
        "SELECT writefile('/tmp/pdp_mcp_should_not_exist', 'x')",
        "SELECT readfile('/etc/hosts')",
    ],
    "postgres": [
        "SELECT nextval(pg_get_serial_sequence('course', 'course_id'))",
        "SELECT * FROM student FOR UPDATE",
        "SELECT lo_from_bytea(0, 'x'::bytea)",
        "SELECT pg_advisory_xact_lock(1), * FROM student FOR SHARE",
    ],
}


def snapshot(settings):
    if settings.backend == "sqlite":
        return hashlib.sha256(settings.sqlite_path.read_bytes()).hexdigest()
    _, tables = query(settings, "SELECT table_name FROM information_schema.tables "
                                "WHERE table_schema = current_schema() ORDER BY 1")
    return tables["rows"], table_counts(settings)


@pytest.mark.parametrize("sql", NOT_A_QUERY)
def test_statements_that_are_not_queries_are_rejected(settings, sql):
    before = snapshot(settings)
    is_error, content = query(settings, sql)
    assert is_error and content["error"]["code"] == "query_rejected", content
    assert snapshot(settings) == before


def test_queries_that_would_write_are_refused_by_the_database(settings):
    attempts = LOOKS_LIKE_A_QUERY["both"] + LOOKS_LIKE_A_QUERY[settings.backend]
    before = snapshot(settings)
    for sql in attempts:
        is_error, content = query(settings, sql)
        assert is_error, f"ran: {sql}"
        assert content["error"]["code"] in {"query_rejected", "query_failed"}, (sql, content)
    assert snapshot(settings) == before


def test_more_than_one_statement_is_rejected_by_name(settings):
    is_error, content = query(settings, "SELECT 1; DELETE FROM student")
    assert content["error"]["code"] == "query_rejected" and "one statement" in content["error"]["message"]


def test_a_trailing_semicolon_or_comment_is_still_one_statement(settings):
    for sql in ("SELECT 1;", "SELECT 1; -- done", "SELECT 1 /* x */ ;  "):
        is_error, content = query(settings, sql)
        assert not is_error and content["rows"] == [[1]], (sql, content)


def test_a_session_setting_changed_by_one_query_does_not_reach_the_next(settings):
    if settings.backend != "postgres":
        pytest.skip("set_config is PostgreSQL's")
    query(settings, "SELECT set_config('default_transaction_read_only', 'off', false)")
    _, setting = query(settings, "SELECT current_setting('transaction_read_only')")
    is_error, content = query(settings, "SELECT nextval(pg_get_serial_sequence('course', 'course_id'))")
    assert setting["rows"] == [["on"]]
    assert is_error and content["error"]["details"] == {"sqlstate": "25006"}


def test_a_missing_sqlite_file_is_never_created(tmp_path):
    from pdp_mcp.config import Settings
    path = tmp_path / "missing.sqlite"
    is_error, content = query(Settings(backend="sqlite", sqlite_path=path), "SELECT 1")
    assert is_error and content["error"]["code"] == "database_unavailable"
    assert not path.exists()
