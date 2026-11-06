"""Checks the published contract, schemas/tools.json, against what the server lists.

If a test here fails after a deliberate contract change, run `python -m pdp_mcp.export_schemas`
from mcp/, update docs/tool-contracts.md, and say in the pull request who the change affects.
"""

import json
import os
import sys
from pathlib import Path

import anyio
import jsonschema
from mcp.client import Client
from mcp.client.stdio import StdioServerParameters

from pdp_mcp.config import Settings, from_env
from pdp_mcp.contracts import ErrorResult
from pdp_mcp.export_schemas import SCHEMAS, listed_tools, render
from pdp_mcp.server import build_server

MCP_DIR = Path(__file__).resolve().parents[1]
TOOLS = {"list_tables", "describe_table", "get_column_definition", "get_database_info"}
DATA_QUERY_WORDS = ("query", "sql", "execute", "rows")


def published():
    contract = json.loads(SCHEMAS.read_text())
    assert contract["access_mode"] == "definitions" and contract["status"] == "verified"
    return contract["tools"]


def in_memory_tools(settings=None):
    async def run():
        async with Client(build_server(settings or Settings())) as client:
            return await listed_tools(client)
    return anyio.run(run)


def test_definitions_is_the_default_access_mode():
    assert from_env({}).access_mode == "definitions" == Settings().access_mode


def test_exactly_the_four_metadata_tools_are_registered():
    assert {t["name"] for t in in_memory_tools()} == TOOLS


def test_no_data_query_tool_is_listed():
    for tool in in_memory_tools():
        assert not any(word in tool["name"] for word in DATA_QUERY_WORDS), tool["name"]
        assert not any(word in tool["inputSchema"].get("properties", {}) for word in DATA_QUERY_WORDS), tool["name"]


def test_execute_query_cannot_be_called_over_mcp():
    async def run():
        async with Client(build_server(Settings())) as client:
            return await client.call_tool("execute_query", {"sql": "SELECT 1"})
    result = anyio.run(run)
    assert result.is_error and result.structured_content is None
    assert result.content[0].text == "Unknown tool: execute_query"


def test_a_configured_database_lists_the_same_tools(sqlite_path):
    settings = Settings(backend="sqlite", sqlite_path=sqlite_path)
    assert render(in_memory_tools(settings)) == SCHEMAS.read_text()


def test_no_tool_argument_can_change_the_access_mode():
    for tool in published():
        properties = tool["inputSchema"].get("properties", {})
        assert not any("mode" in name or "access" in name for name in properties), tool["name"]


def test_published_schemas_match_the_server():
    assert SCHEMAS.read_text() == render(in_memory_tools()), "run: python -m pdp_mcp.export_schemas"


def test_published_schemas_match_the_server_over_stdio():
    async def run():
        clean = {k: v for k, v in os.environ.items() if not k.startswith("PDP_MCP_")}
        params = StdioServerParameters(command=sys.executable, args=[str(MCP_DIR / "run_server.py")], env=clean)
        async with Client(params) as client:
            return await listed_tools(client)
    assert anyio.run(run) == published()


def test_every_tool_publishes_valid_input_and_output_schemas_and_is_read_only():
    for tool in published():
        jsonschema.Draft202012Validator.check_schema(tool["inputSchema"])
        jsonschema.Draft202012Validator.check_schema(tool["outputSchema"])
        assert tool["annotations"]["readOnlyHint"] is True
        assert tool["annotations"]["destructiveHint"] is False


def test_error_results_have_the_documented_shape():
    schema = ErrorResult.model_json_schema()
    jsonschema.validate({"error": {"code": "not_found", "message": "no table x", "details": {"suggestions": []}}},
                        schema)
    for bad in ({"error": {"code": "oops", "message": "x"}}, {"error": {"message": "x"}}, {"code": "not_found"}):
        try:
            jsonschema.validate(bad, schema)
        except jsonschema.ValidationError:
            continue
        raise AssertionError(f"accepted {bad}")
