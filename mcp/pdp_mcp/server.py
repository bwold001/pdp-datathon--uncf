"""The MCP server: registers the tools its access mode allows, against the contracts in contracts.py.

The access mode comes from trusted configuration at startup (config.py). Definitions mode, the only
mode today, registers four metadata tools. They read the repo's metadata files, never a database,
and return no student-level values.

execute_query is kept, tested and dormant: Tools.execute_query and the SQLite and PostgreSQL
safeguards in db.py and query.py still work, but no access mode registers it as a tool. Exposing it
waits on a student-level access decision.

Each tool returns a CallToolResult. On success, structuredContent is the tool's result model and
the text content is the same JSON. On failure, isError is true and structuredContent is an
ErrorResult. Arguments that don't match a tool's input schema are rejected by the SDK before the
tool runs, with a text message only.
"""

import json
import logging
import time
from typing import Annotated

from mcp.server.mcpserver import MCPServer
from mcp_types import CallToolResult, TextContent, ToolAnnotations
from pydantic import BaseModel, Field

from . import db
from .config import Settings, from_env
from .contracts import (TOOL_DESCRIPTIONS, ColumnDefinitionResult, DatabaseInfoResult, DescribeTableResult,
                        ErrorCode, ErrorInfo, ErrorResult, ExecuteQueryResult, ListTablesResult)
from .metadata import Metadata, NotFound
from .query import QueryRejected, check_statement

__all__ = ["TOOLS_BY_MODE", "ToolFailure", "Tools", "build_server"]

log = logging.getLogger(__name__)

SERVER_NAME = "pdp-datathon"
# The tools each access mode registers. Nothing else is registered, so nothing else can be called.
TOOLS_BY_MODE = {"definitions": ("list_tables", "describe_table", "get_column_definition", "get_database_info")}
_READ_ONLY = ToolAnnotations(read_only_hint=True, destructive_hint=False, idempotent_hint=True, open_world_hint=False)


class ToolFailure(Exception):
    """Raised inside a tool to return an ErrorResult with this code."""

    def __init__(self, code: ErrorCode, message: str, details: dict | None = None):
        super().__init__(message)
        self.info = ErrorInfo(code=code, message=message, details=details)


def ok(result: BaseModel) -> CallToolResult:
    data = result.model_dump(mode="json")
    return CallToolResult(content=[TextContent(text=json.dumps(data))], structured_content=data)


def failed(info: ErrorInfo) -> CallToolResult:
    data = ErrorResult(error=info).model_dump(mode="json")
    return CallToolResult(content=[TextContent(text=json.dumps(data))], structured_content=data, is_error=True)


def _guarded(tool):
    """Run a tool body, turning each expected failure into its error result."""
    try:
        return ok(tool())
    except ToolFailure as exc:
        return failed(exc.info)
    except db.Unavailable as exc:
        return failed(ErrorInfo(code="database_unavailable", message=str(exc)))
    except Exception:
        log.exception("tool failed")   # the detail stays on the server, in stderr
        return failed(ErrorInfo(code="internal_error", message="The server hit an unexpected error. Its log (stderr) "
                                                               "has the details."))


class Tools:
    """The tool bodies. The metadata tools read repo files once; the dormant query path opens a
    database connection per call."""

    def __init__(self, settings: Settings, metadata: Metadata | None = None):
        self.settings = settings
        self.backend = db.backend_for(settings) if settings.backend else None
        self.metadata = metadata or Metadata()

    def list_tables(self):
        return ListTablesResult(source="normalized-data-model/config/destination_schema.yaml",
                                tables=self.metadata.tables())

    def describe_table(self, table):
        try:
            return DescribeTableResult(**self.metadata.describe(table))
        except NotFound as exc:
            raise ToolFailure("not_found", str(exc), {"suggestions": exc.suggestions}) from None

    def execute_query(self, sql, params, max_rows):
        """Dormant: not registered as a tool in any access mode. Kept, and tested, for a later decision."""
        if self.backend is None:
            raise db.Unavailable("no database is configured: set PDP_MCP_BACKEND")
        limit = self.settings.max_rows if max_rows is None else max_rows
        if limit > self.settings.max_rows:
            raise ToolFailure("invalid_argument", f"max_rows can be at most {self.settings.max_rows}, the server's "
                                                  f"limit.", {"max_rows": self.settings.max_rows})
        try:
            sql = check_statement(sql)
            started = time.perf_counter()
            result = self.backend.execute(sql, params, limit, self.settings.query_timeout_seconds)
        except (QueryRejected, db.Rejected) as exc:
            raise ToolFailure("query_rejected", f"Query refused: {exc}.") from None
        except db.TimedOut:
            seconds = self.settings.query_timeout_seconds
            raise ToolFailure("timeout", f"The query ran longer than {seconds:g} seconds and was stopped.",
                              {"timeout_seconds": seconds}) from None
        except db.Failed as exc:
            raise ToolFailure("query_failed", f"The database couldn't run the query: {exc}",
                              {"sqlstate": exc.sqlstate} if exc.sqlstate else None) from None
        return ExecuteQueryResult(columns=result.columns, rows=result.rows, row_count=len(result.rows),
                                  truncated=result.truncated, max_rows=limit,
                                  elapsed_ms=round((time.perf_counter() - started) * 1000, 2))

    def get_column_definition(self, column, table, source_file):
        try:
            matches = self.metadata.define(column, table, source_file)
        except NotFound as exc:
            raise ToolFailure("not_found", str(exc), {"suggestions": exc.suggestions}) from None
        return ColumnDefinitionResult(query={"column": column, "table": table, "source_file": source_file},
                                      matches=matches)

    def get_database_info(self):
        problem, files = self.metadata.status()
        metadata = {"healthy": problem is None, "files": files,
                    "error": ErrorInfo(code="internal_error", message=problem) if problem else None,
                    "table_count": len(self.metadata.schema) if problem is None else 0}
        database, warnings = (self._database_status() if self.backend else (None, []))
        return DatabaseInfoResult(access_mode=self.settings.access_mode,
                                  capabilities=list(TOOLS_BY_MODE[self.settings.access_mode]), read_only=True,
                                  metadata=metadata, database=database, warnings=warnings)

    def _database_status(self):
        """The configured database's health. No metadata tool reads it; this only says if it's reachable."""
        expected = sorted(self.metadata.schema)
        status = {"engine": self.backend.engine, "healthy": False, "error": None, "server_version": None,
                  "database": getattr(self.backend, "database_name", None), "database_schema": None,
                  "model_tables": {"expected": expected, "missing": expected}, "table_count": None,
                  "view_count": None}
        warnings = []
        try:
            with self.backend.connect() as connection:
                self.backend.ping(connection)
                relations = self.backend.relations(connection)
                tables = {r.name for r in relations if r.type == "table"}
                missing = [t for t in expected if t not in tables]
                status.update(healthy=True, server_version=self.backend.server_version(connection),
                              database=self.backend.database_name, database_schema=self.backend.schema_name,
                              model_tables={"expected": expected, "missing": missing}, table_count=len(tables),
                              view_count=len(relations) - len(tables))
                warnings = self.backend.warnings(connection, [t for t in expected if t in tables])
        except db.Unavailable as exc:
            status["error"] = ErrorInfo(code="database_unavailable", message=str(exc))
        if status["healthy"] and status["model_tables"]["missing"]:
            warnings.insert(0, f"The database lacks {len(status['model_tables']['missing'])} of the model's "
                               f"tables. Load it with the loader (normalized-data-model/README.md).")
        return status, warnings


def build_server(settings: Settings | None = None, metadata: Metadata | None = None) -> MCPServer:
    settings = settings or from_env()
    tools = Tools(settings, metadata)
    server = MCPServer(SERVER_NAME, instructions=(
        "Definitions for the normalized PDP datathon data model: its tables, columns, keys, and what each "
        "column means. This server has no data-query tools and returns no student-level values. Start with "
        "list_tables, then describe_table and get_column_definition. The data is synthetic."))

    def list_tables() -> Annotated[CallToolResult, ListTablesResult]:
        return _guarded(lambda: tools.list_tables())

    def describe_table(
        table: Annotated[str, Field(min_length=1, max_length=128,
                                    description="A table name from list_tables, such as cohort_membership.")],
    ) -> Annotated[CallToolResult, DescribeTableResult]:
        return _guarded(lambda: tools.describe_table(table))

    def get_column_definition(
        column: Annotated[str, Field(min_length=1, max_length=128, description=(
            "A raw file column (Retention, Student_GUID), a dictionary name (Student ID), a normalized column "
            "(retention), or `table.column`. Matching ignores case."))],
        table: Annotated[str | None, Field(
            max_length=128, description="Only normalized columns of this table.")] = None,
        source_file: Annotated[str | None, Field(
            max_length=128, description="Only source columns of this file, such as pdp_course_data.csv.")] = None,
    ) -> Annotated[CallToolResult, ColumnDefinitionResult]:
        return _guarded(lambda: tools.get_column_definition(column, table, source_file))

    def get_database_info() -> Annotated[CallToolResult, DatabaseInfoResult]:
        return _guarded(lambda: tools.get_database_info())

    available = {fn.__name__: fn for fn in (list_tables, describe_table, get_column_definition, get_database_info)}
    for name in TOOLS_BY_MODE[settings.access_mode]:
        server.add_tool(available[name], description=TOOL_DESCRIPTIONS[name], annotations=_READ_ONLY)
    return server
