"""Checks the dormant execute_query path on every backend available, called in Python.

No access mode registers execute_query as a tool (test_contracts.py checks that). These tests keep
the query path, its limits and its errors working for a later student-level access decision. The
read-only safeguards are in test_read_only.py.

The sample is the committed 10-student output of the data model: 10 students, 11 cohort rows (one
student is in two cohorts), 52 course rows. The data is synthetic.
"""

import pytest

from conftest import ph, query, query_error_code


def test_a_query_returns_columns_and_rows(settings):
    _, result = query(settings, "SELECT cohort, COUNT(*) AS n FROM cohort_membership GROUP BY cohort ORDER BY cohort")
    assert [c["name"] for c in result["columns"]] == ["cohort", "n"]
    assert result["rows"] == [["2021-22", 3], ["2022-23", 4], ["2023-24", 3], ["2024-25", 1]]
    assert result["row_count"] == 4 and not result["truncated"] and result["max_rows"] == 20


def test_params_use_the_backends_own_placeholder(settings):
    _, result = query(settings, f"SELECT COUNT(*) FROM cohort_membership WHERE cohort = {ph(settings)} "
                                f"AND retention = {ph(settings)}", ["2022-23", True])
    assert result["rows"][0][0] <= 4
    assert query_error_code(settings, f"SELECT {ph(settings)}", []) == "query_failed"


def test_a_literal_percent_works_without_params(settings):
    _, result = query(settings, "SELECT COUNT(*) FROM cohort_membership WHERE cohort LIKE '2022%'")
    assert result["rows"] == [[4]]


def test_values_become_json_scalars(settings):
    _, result = query(settings, "SELECT course_begin_date, number_of_credits_attempted, retention "
                                "FROM course_enrollment e JOIN cohort_membership m ON m.student_id = e.student_id "
                                "WHERE course_begin_date IS NOT NULL ORDER BY e.enrollment_id LIMIT 1")
    begin, credits, retention = result["rows"][0]
    assert isinstance(begin, str) and len(begin) == 10 and begin[4] == "-"
    assert isinstance(credits, float)
    assert retention in ((0, 1) if settings.backend == "sqlite" else (False, True))


def test_max_rows_truncates_and_says_so(settings):
    _, result = query(settings, "SELECT enrollment_id FROM course_enrollment ORDER BY 1")
    assert result["row_count"] == 20 and result["truncated"] and result["max_rows"] == 20
    _, result = query(settings, "SELECT enrollment_id FROM course_enrollment ORDER BY 1", max_rows=5)
    assert [r[0] for r in result["rows"]] == [1, 2, 3, 4, 5] and result["truncated"]
    _, result = query(settings, "SELECT student_id FROM student", max_rows=10)
    assert result["row_count"] == 10 and not result["truncated"]


def test_max_rows_above_the_server_limit_is_an_invalid_argument(settings):
    _, content = query(settings, "SELECT 1", max_rows=21)
    assert content["error"] == {"code": "invalid_argument", "message": content["error"]["message"],
                                "details": {"max_rows": 20}}


@pytest.mark.parametrize("sql", ["SELECT nope FROM student", "SELECT * FROM no_such_table", "SELEC 1 FROM student",
                                 "SELECT (1"])
def test_invalid_sql_fails_cleanly(settings, sql):
    assert query_error_code(settings, sql) == ("query_rejected" if sql.startswith("SELEC ") else "query_failed")


def test_a_runaway_query_times_out(settings):
    sql = ("WITH RECURSIVE c(x) AS (SELECT 1 UNION ALL SELECT x + 1 FROM c) SELECT COUNT(*) FROM c"
           if settings.backend == "sqlite" else "SELECT pg_sleep(10)")
    _, content = query(settings, sql)
    assert content["error"]["code"] == "timeout" and content["error"]["details"] == {"timeout_seconds": 1.0}
    _, after = query(settings, "SELECT COUNT(*) FROM student")
    assert after["rows"] == [[10]], "the query path keeps working after a timeout"


def test_explain_works_and_explain_analyze_is_refused(settings):
    plan = "EXPLAIN QUERY PLAN SELECT * FROM student" if settings.backend == "sqlite" else "EXPLAIN SELECT * FROM student"
    is_error, _ = query(settings, plan)
    assert not is_error
    assert query_error_code(settings, "EXPLAIN ANALYZE SELECT * FROM student") == "query_rejected"


def test_without_a_configured_database_the_query_path_is_unavailable():
    from pdp_mcp.config import Settings
    _, content = query(Settings(), "SELECT 1")
    assert content["error"]["code"] == "database_unavailable"
