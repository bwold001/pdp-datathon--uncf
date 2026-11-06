"""The run_aggregate_query tool: read-only SQL over the data model in the Playground database.

It runs through the MCP server's query path (mcp/pdp_mcp/db.py), so the database itself refuses
writes: SQLite opens the file read-only, PostgreSQL runs a read-only transaction and rolls it back.

Then only aggregates come back: the result needs an `n` column of students per group, groups under
MIN_GROUP_SIZE are dropped, and results with row-level identifier columns or student_id values are
refused. These checks catch accidental student-level output; they aren't a security boundary, since
a query can transform an ID or misstate n. The data is synthetic, and the sandbox is off in
production.
"""

from functools import cache
from pathlib import Path
from typing import Any

from sqlalchemy.engine import make_url

from app.core.config import settings

from .metadata_tools import ToolError, error_body
from .repo import import_path

NAME = "run_aggregate_query"
MIN_GROUP_SIZE = 10
MAX_ROWS = 200
TIMEOUT_SECONDS = 10.0
COUNT_COLUMN = "n"
# Each identifies one student, enrollment or attribute row, so no aggregate result needs one.
ROW_ID_COLUMNS = frozenset({"student_id", "enrollment_id", "attribute_id"})
EMPTY_RESULT_HINT = (
    "No rows matched. Text comparisons are case-sensitive and stored codes can differ in case from "
    "the dictionary's: filter with LOWER(column) = LOWER('code'), or group by the column to see "
    "the stored values."
)

TOOL = {
    "name": NAME,
    "description": (
        "Run one read-only query (SELECT or WITH) on the data model loaded into the Playground "
        "database, and get aggregate results. The result must have a column named n: the number of "
        "distinct students in each row's group, such as COUNT(DISTINCT student_id) AS n. Rows with "
        f"n under {MIN_GROUP_SIZE} are removed before you see them, and results with row-level "
        f"identifiers ({', '.join(sorted(ROW_ID_COLUMNS))}) are refused. At most {MAX_ROWS} rows. "
        "Write SQL that runs on both SQLite and PostgreSQL. Text comparisons are case-sensitive, "
        "so filter codes with LOWER(column) = LOWER('code'). The data is synthetic."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "sql": {"type": "string", "minLength": 1, "maxLength": 5000},
        },
        "required": ["sql"],
    },
}


@cache
def _mcp() -> tuple[Any, Any, Any]:
    """(db, query, config) from the MCP server's library, imported once."""
    import_path("mcp")
    from pdp_mcp import config, db, query  # type: ignore[import-not-found]

    return db, query, config


@cache
def backend() -> Any:
    """A read-only backend for the Playground database DATABASE_URL names."""
    db, _, config = _mcp()
    url = make_url(settings.DATABASE_URL)
    if settings.database_engine == "sqlite":
        # Relative paths resolve from the working directory, as SQLAlchemy resolves them.
        path = Path(url.database or "").resolve()
        return db.backend_for(config.Settings(backend="sqlite", sqlite_path=path))
    plain = url.set(drivername="postgresql").render_as_string(hide_password=False)
    return db.backend_for(config.Settings(backend="postgres", postgres_url=plain))


def call(arguments: dict[str, Any]) -> dict[str, Any]:
    """Run the query and return its groups of MIN_GROUP_SIZE or more. Raises ToolError."""
    db, query, _ = _mcp()
    try:
        statement = query.check_statement(arguments["sql"])
        result = backend().execute(statement, None, MAX_ROWS, TIMEOUT_SECONDS)
    except (query.QueryRejected, db.Rejected) as exc:
        raise ToolError(error_body("query_rejected", f"Query refused: {exc}.")) from None
    except db.TimedOut:
        message = f"The query ran longer than {TIMEOUT_SECONDS:g} seconds and was stopped."
        raise ToolError(error_body("timeout", message)) from None
    except db.Unavailable as exc:
        raise ToolError(error_body("database_unavailable", str(exc))) from None
    except db.Failed as exc:
        raise ToolError(error_body("query_failed", _failure_message(str(exc)))) from None

    columns = [column["name"] for column in result.columns]
    lowered = [name.lower() for name in columns]
    identifiers = sorted(ROW_ID_COLUMNS.intersection(lowered))
    if identifiers:
        message = (
            f"Results can't include row-level identifiers ({', '.join(identifiers)}). "
            "Group by other columns and count students instead."
        )
        raise ToolError(error_body("query_rejected", message))
    if COUNT_COLUMN not in lowered:
        message = (
            f"The result needs a column named {COUNT_COLUMN}: the number of distinct students in "
            "each group, such as COUNT(DISTINCT student_id) AS n."
        )
        raise ToolError(error_body("query_rejected", message))

    count_index = lowered.index(COUNT_COLUMN)
    kept = [row for row in result.rows if _group_size(row[count_index]) >= MIN_GROUP_SIZE]
    if _holds_student_ids(kept):
        message = (
            "Results can't include student IDs, even under another column name. "
            "Group by other columns and count students instead."
        )
        raise ToolError(error_body("query_rejected", message))
    output = {
        "columns": columns,
        "rows": kept,
        "row_count": len(kept),
        "suppressed_rows": len(result.rows) - len(kept),
        "min_group_size": MIN_GROUP_SIZE,
        "truncated": result.truncated,
        "max_rows": MAX_ROWS,
        "source": "synthetic",
    }
    if not result.rows:
        output["hint"] = EMPTY_RESULT_HINT
    return output


def _holds_student_ids(rows: list[list[Any]]) -> bool:
    """Whether any text value in the rows is a student_id, which the column-name check can miss."""
    values = sorted({value for row in rows for value in row if isinstance(value, str)})
    if not values:
        return False
    marker = "?" if backend().param_style == "qmark" else "%s"
    placeholders = ", ".join([marker] * len(values))
    sql = f"SELECT student_id FROM student WHERE student_id IN ({placeholders})"
    return bool(backend().execute(sql, values, 1, TIMEOUT_SECONDS).rows)


def _group_size(value: Any) -> float:
    """The n value as a number; anything that isn't one counts as 0, so its row is dropped."""
    if isinstance(value, bool) or not isinstance(value, int | float):
        return 0
    return value


def _failure_message(detail: str) -> str:
    """The database's error, with a hint when the model's tables haven't been loaded."""
    message = f"The database couldn't run the query: {detail}"
    if "no such table" in detail or "does not exist" in detail:
        message += " The data model may not be loaded yet: load it from the Sandbox pipeline page."
    return message
