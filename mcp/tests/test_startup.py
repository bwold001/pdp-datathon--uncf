"""Checks the server as a client starts it: run_server.py over stdio, with environment variables.

These are the README's smoke test, automated: with no database, the server starts in definitions
mode, lists exactly the four metadata tools, describes a table, defines a column, and has no
execute_query to call. Bad settings, a reserved access mode, or missing metadata stop it with exit
code 2 and a message on stderr, before it serves anything.
"""

import os
import subprocess
import sys

import anyio
from mcp.client import Client
from mcp.client.stdio import StdioServerParameters

from conftest import MCP_DIR

RUN_SERVER = str(MCP_DIR / "run_server.py")
METADATA_TOOLS = ["describe_table", "get_column_definition", "get_database_info", "list_tables"]


def env(**settings):
    clean = {k: v for k, v in os.environ.items() if not k.startswith("PDP_MCP_")}
    return dict(clean, **settings)


def start(**settings):
    return subprocess.run([sys.executable, RUN_SERVER], env=env(**settings), input="", capture_output=True,
                          text=True, timeout=60)


def smoke(**settings):
    async def run():
        params = StdioServerParameters(command=sys.executable, args=[RUN_SERVER], env=env(**settings), cwd="/")
        async with Client(params) as client:
            tools = sorted(t.name for t in (await client.list_tools()).tools)
            info = await client.call_tool("get_database_info", {})
            described = await client.call_tool("describe_table", {"table": "student"})
            defined = await client.call_tool("get_column_definition", {"column": "retention"})
            queried = await client.call_tool("execute_query", {"sql": "SELECT COUNT(*) FROM student"})
            return tools, info, described, defined, queried
    return anyio.run(run)


def test_the_smoke_test_over_stdio_needs_no_database(tmp_path):
    tools, info, described, defined, queried = smoke(PDP_MCP_SQLITE_PATH=str(tmp_path / "nothing.sqlite"))
    assert tools == METADATA_TOOLS
    assert info.structured_content["access_mode"] == "definitions" and info.structured_content["database"] is None
    assert described.structured_content["primary_key"] == ["student_id"]
    assert defined.structured_content["matches"][0]["source_column"] == "Retention"
    assert queried.is_error and queried.structured_content is None
    assert "Unknown tool: execute_query" in queried.content[0].text
    assert not (tmp_path / "nothing.sqlite").exists()


def test_a_configured_database_adds_no_tools(sqlite_path):
    tools, info, _, _, queried = smoke(PDP_MCP_BACKEND="sqlite", PDP_MCP_SQLITE_PATH=str(sqlite_path))
    assert tools == METADATA_TOOLS
    assert info.structured_content["database"]["healthy"]
    assert queried.is_error and "Unknown tool" in queried.content[0].text


def test_definitions_is_the_default_and_can_be_named():
    for settings in ({}, {"PDP_MCP_ACCESS_MODE": "definitions"}, {"PDP_MCP_ACCESS_MODE": " Definitions "}):
        result = start(**settings)
        assert result.returncode == 0 and result.stderr == "", (settings, result.stderr)


def test_aggregate_mode_fails_until_measures_are_integrated():
    result = start(PDP_MCP_ACCESS_MODE="aggregate")
    assert result.returncode == 2 and result.stdout == ""
    assert "PDP_MCP_ACCESS_MODE=aggregate isn't available yet" in result.stderr
    assert "Measures" in result.stderr and "#9" in result.stderr and "set it to definitions" in result.stderr


def test_other_access_modes_fail():
    for mode in ("student", "student_level", "all", "query", "admin"):
        result = start(PDP_MCP_ACCESS_MODE=mode)
        assert result.returncode == 2 and "PDP_MCP_ACCESS_MODE must be definitions" in result.stderr, mode


def test_a_configured_database_that_is_missing_does_not_stop_the_server(tmp_path):
    result = start(PDP_MCP_BACKEND="sqlite", PDP_MCP_SQLITE_PATH=str(tmp_path / "nothing.sqlite"))
    assert result.returncode == 0 and not (tmp_path / "nothing.sqlite").exists()


def test_an_unreachable_postgres_does_not_stop_the_server_or_show_the_url():
    result = start(PDP_MCP_BACKEND="postgres", PDP_MCP_POSTGRES_URL="postgresql://someone:s3cret@127.0.0.1:1/pdp")
    assert result.returncode == 0 and "s3cret" not in result.stderr + result.stdout


def test_bad_settings_stop_the_server():
    for settings, message in [({"PDP_MCP_BACKEND": "mysql"}, "PDP_MCP_BACKEND must be sqlite or postgres"),
                              ({"PDP_MCP_BACKEND": "postgres"}, "PDP_MCP_POSTGRES_URL isn't set"),
                              ({"PDP_MCP_LOG_LEVEL": "LOUD"}, "PDP_MCP_LOG_LEVEL must be one of")]:
        result = start(**settings)
        assert result.returncode == 2 and message in result.stderr, (settings, result.stderr)


def test_the_dormant_query_settings_never_stop_the_server():
    from pdp_mcp.config import Settings, from_env
    for settings in ({"PDP_MCP_MAX_ROWS": "lots"}, {"PDP_MCP_MAX_ROWS": "0"},
                     {"PDP_MCP_QUERY_TIMEOUT_SECONDS": "-1"}, {"PDP_MCP_QUERY_TIMEOUT_SECONDS": "soon"}):
        result = start(**settings)
        assert result.returncode == 0 and result.stderr == "", (settings, result.stderr)
        assert from_env(settings) == Settings(), "they're ignored, not applied"


def test_missing_metadata_stops_the_server(tmp_path):
    from pdp_mcp.__main__ import startup_problem
    from pdp_mcp.metadata import Metadata
    assert startup_problem() is None
    model = tmp_path / "normalized-data-model"
    (model / "config").mkdir(parents=True)
    (model / "config/pipeline.yaml").write_text("sources: []\n")
    problem = startup_problem(Metadata(tmp_path))
    assert problem == "can't read normalized-data-model/config/destination_schema.yaml"
