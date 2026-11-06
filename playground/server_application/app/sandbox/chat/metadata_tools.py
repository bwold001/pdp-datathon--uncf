"""The MCP server's four definitions tools, called through its library instead of over MCP.

Same names, input schemas and results as mcp/schemas/tools.json, so chat and the MCP server
expose the same things. Like the server's definitions mode, they read the repo's metadata files,
never a database, and have no query tool.
"""

import json
from functools import cache
from typing import Any

from .repo import import_path, repo_root

TOOL_NAMES = ("list_tables", "describe_table", "get_column_definition", "get_database_info")


class ToolError(Exception):
    """A tool couldn't answer; carries the MCP ErrorResult body."""

    def __init__(self, body: dict[str, Any]):
        super().__init__(body["error"]["message"])
        self.body = body


@cache
def tool_schemas() -> list[dict[str, Any]]:
    """The four tools as Anthropic tool definitions, from the MCP server's published contract."""
    published = json.loads((repo_root() / "mcp/schemas/tools.json").read_text(encoding="utf-8"))
    return [
        {"name": t["name"], "description": t["description"], "input_schema": t["inputSchema"]}
        for t in published["tools"]
        if t["name"] in TOOL_NAMES
    ]


@cache
def _library() -> tuple[Any, Any, Any]:
    """(Metadata instance, NotFound, contracts module), imported once."""
    import_path("mcp")
    from pdp_mcp import contracts  # type: ignore[import-not-found]
    from pdp_mcp.metadata import Metadata, NotFound  # type: ignore[import-not-found]

    return Metadata(repo_root=repo_root()), NotFound, contracts


def call(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Run one definitions tool. Raises ToolError with an MCP-shaped error body."""
    metadata, not_found, contracts = _library()
    try:
        result = _run(name, arguments, metadata, contracts)
    except not_found as exc:
        details = {"suggestions": exc.suggestions}
        raise ToolError(error_body("not_found", str(exc), details)) from None
    except (KeyError, TypeError) as exc:
        message = f"Bad arguments for {name}: {exc}"
        raise ToolError(error_body("invalid_argument", message)) from None
    return result.model_dump(mode="json")


def _run(name: str, arguments: dict[str, Any], metadata: Any, contracts: Any) -> Any:
    """Build the tool's contract model, as mcp/pdp_mcp/server.py's Tools does."""
    if name == "list_tables":
        return contracts.ListTablesResult(
            source="normalized-data-model/config/destination_schema.yaml",
            tables=metadata.tables(),
        )
    if name == "describe_table":
        return contracts.DescribeTableResult(**metadata.describe(arguments["table"]))
    if name == "get_column_definition":
        column, table = arguments["column"], arguments.get("table")
        source_file = arguments.get("source_file")
        return contracts.ColumnDefinitionResult(
            query={"column": column, "table": table, "source_file": source_file},
            matches=metadata.define(column, table, source_file),
        )
    if name == "get_database_info":
        problem, files = metadata.status()
        return contracts.DatabaseInfoResult(
            access_mode="definitions",
            capabilities=list(TOOL_NAMES),
            read_only=True,
            metadata={
                "healthy": problem is None,
                "files": files,
                "error": error_body("internal_error", problem)["error"] if problem else None,
                "table_count": len(metadata.schema) if problem is None else 0,
            },
            database=None,
            warnings=[],
        )
    raise ToolError(error_body("invalid_argument", f"Unknown tool: {name}"))


def error_body(code: str, message: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    """An MCP ErrorResult body."""
    return {"error": {"code": code, "message": message, "details": details}}
