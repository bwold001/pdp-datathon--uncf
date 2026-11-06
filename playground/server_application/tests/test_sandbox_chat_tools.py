"""Sandbox chat's dictionary and aggregate query tools, called directly. No model is involved."""

import sqlite3
from pathlib import Path
from typing import Any

import pytest

from app.sandbox.chat import dictionary_tool, query_tool
from app.sandbox.chat.metadata_tools import ToolError

# 12 full-time students and 3 part-time ones: part-time is under the minimum group size.
STUDENTS = [(f"S{i:02d}", "Full-Time" if i < 12 else "Part-Time") for i in range(15)]


@pytest.fixture
def model_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A small SQLite data model that run_aggregate_query reads instead of the Playground's."""
    path = tmp_path / "model.db"
    with sqlite3.connect(path) as connection:
        connection.execute("CREATE TABLE student (student_id TEXT PRIMARY KEY)")
        connection.execute("CREATE TABLE cohort_membership (student_id TEXT, intensity TEXT)")
        connection.executemany("INSERT INTO student VALUES (?)", [(s,) for s, _ in STUDENTS])
        connection.executemany("INSERT INTO cohort_membership VALUES (?, ?)", STUDENTS)
    db, _, config = query_tool._mcp()
    backend = db.backend_for(config.Settings(backend="sqlite", sqlite_path=path))
    monkeypatch.setattr(query_tool, "backend", lambda: backend)
    return path


def run(sql: str) -> dict[str, Any]:
    """run_aggregate_query's result for one query."""
    return query_tool.call({"sql": sql})


def refusal(sql: str) -> dict[str, Any]:
    """run_aggregate_query's error for a query it must refuse."""
    with pytest.raises(ToolError) as caught:
        run(sql)
    return caught.value.body["error"]


GROUPS = "SELECT intensity, COUNT(DISTINCT student_id) AS n FROM cohort_membership GROUP BY 1"


def test_groups_under_ten_students_are_dropped(model_db: Path) -> None:
    result = run(GROUPS)

    assert result["columns"] == ["intensity", "n"]
    assert result["rows"] == [["Full-Time", 12]]
    assert result["suppressed_rows"] == 1
    assert result["source"] == "synthetic"


def test_a_case_mismatch_finds_nothing_and_says_why(model_db: Path) -> None:
    where = "FROM cohort_membership WHERE {} GROUP BY 1"
    select = "SELECT intensity, COUNT(DISTINCT student_id) AS n "

    exact = run(select + where.format("intensity = 'Full-time'"))
    lowered = run(select + where.format("LOWER(intensity) = LOWER('Full-time')"))

    assert exact["rows"] == []
    assert "LOWER" in exact["hint"]
    assert lowered["rows"] == [["Full-Time", 12]]
    assert "hint" not in lowered


def test_a_result_without_an_n_column_is_refused(model_db: Path) -> None:
    error = refusal("SELECT COUNT(*) AS total FROM student")

    assert error["code"] == "query_rejected"
    assert "named n" in error["message"]


def test_identifier_columns_are_refused(model_db: Path) -> None:
    error = refusal("SELECT student_id, 10 AS n FROM student")

    assert error["code"] == "query_rejected"
    assert "student_id" in error["message"]


def test_student_ids_under_another_name_are_refused(model_db: Path) -> None:
    error = refusal("SELECT student_id AS who, 10 AS n FROM student")

    assert error["code"] == "query_rejected"
    assert "student IDs" in error["message"]


@pytest.mark.parametrize("sql", ["DELETE FROM student", "WITH x AS (SELECT 1) DELETE FROM student"])
def test_writes_are_refused_and_change_nothing(model_db: Path, sql: str) -> None:
    assert refusal(sql)["code"] == "query_rejected"
    with sqlite3.connect(model_db) as connection:
        assert connection.execute("SELECT COUNT(*) FROM student").fetchone() == (len(STUDENTS),)


def test_a_missing_table_points_to_the_pipeline(model_db: Path) -> None:
    error = refusal("SELECT COUNT(*) AS n FROM course_enrollment")

    assert error["code"] == "query_failed"
    assert "pipeline" in error["message"]


def test_dictionary_returns_one_column() -> None:
    result = dictionary_tool.call({"table": "cohort_membership", "column": "retention"})

    assert (result["table"], result["column"]) == ("cohort_membership", "retention")
    assert result["stored"]["type"]


def test_dictionary_returns_every_column_of_a_table() -> None:
    result = dictionary_tool.call({"table": "cohort_membership"})

    assert {c["table"] for c in result["columns"]} == {"cohort_membership"}
    assert "retention" in {c["column"] for c in result["columns"]}


def test_dictionary_unknown_table_is_not_found() -> None:
    with pytest.raises(ToolError) as caught:
        dictionary_tool.call({"table": "nope"})

    assert caught.value.body["error"]["code"] == "not_found"
