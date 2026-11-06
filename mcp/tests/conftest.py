"""Test databases built from the committed 10-student sample, and ways to call the server.

- call() and call_many() call a registered tool through an MCP client, in-process, and check the
  result against the published schemas/tools.json: a success against the tool's outputSchema, a
  failure against the error shape.
- query() calls the dormant execute_query path directly in Python, because no access mode
  registers it as a tool. Its results are checked against ExecuteQueryResult or the error shape.

The PostgreSQL tests run when PDP_TEST_POSTGRES_URL holds a connection URL to a database the tests
may create schemas and roles in, as the loader's tests do. They're skipped otherwise; CI skips them.
"""

import csv
import json
import os
import secrets
import sys
from datetime import date, datetime
from pathlib import Path

import anyio
import jsonschema
import pytest
from mcp.client import Client

MCP_DIR = Path(__file__).resolve().parents[1]
REPO = MCP_DIR.parent
MODEL_DIR = REPO / "normalized-data-model"
SAMPLE_OUTPUT = MODEL_DIR / "data/output/sample"
POSTGRES_URL = os.environ.get("PDP_TEST_POSTGRES_URL")

sys.path.insert(0, str(MODEL_DIR))   # the loader's backends create the test tables exactly as a load does
from src.loader import backends  # noqa: E402
from src.rules.rules import load_rules  # noqa: E402

RULES = load_rules(MODEL_DIR / "config")   # the schema's columns and every foreign key, as the loader reads them
SCHEMA = RULES["schema"]

from pdp_mcp.config import Settings  # noqa: E402
from pdp_mcp.contracts import ErrorResult, ExecuteQueryResult  # noqa: E402
from pdp_mcp.server import Tools, _guarded, build_server  # noqa: E402

PUBLISHED = {t["name"]: t for t in json.loads((MCP_DIR / "schemas/tools.json").read_text())["tools"]}
ERROR_SCHEMA = ErrorResult.model_json_schema()
QUERY_SCHEMA = ExecuteQueryResult.model_json_schema()


def sample_tables():
    """The committed sample output, typed as the loader types it."""
    convert = {"int": int, "float": float, "bool": lambda t: t == "true", "date": date.fromisoformat,
               "datetime": datetime.fromisoformat, "str": str}
    tables = {}
    for table, fields in SCHEMA.items():
        with open(SAMPLE_OUTPUT / f"{table}.csv", newline="") as f:
            tables[table] = [{c: (None if row[c] == "" else convert[fields[c]["type"]](row[c])) for c in fields}
                             for row in csv.DictReader(f)]
    return tables


@pytest.fixture(scope="session")
def sqlite_path(tmp_path_factory):
    path = tmp_path_factory.mktemp("sqlite") / "pdp.sqlite"
    backends.refresh(backends.BACKENDS["sqlite"], str(path), SCHEMA, RULES["foreign_keys"], sample_tables(), 1000)
    return path


@pytest.fixture(scope="session")
def postgres():
    """{"url": a superuser-or-owner URL, "reader_url": a SELECT-only role's URL or None}, on a new schema."""
    if not POSTGRES_URL:
        pytest.skip("set PDP_TEST_POSTGRES_URL to run the PostgreSQL tests")
    import psycopg
    from psycopg.conninfo import conninfo_to_dict, make_conninfo

    schema, reader, password = f"mcp_test_{secrets.token_hex(4)}", f"mcp_reader_{secrets.token_hex(4)}", \
        secrets.token_hex(12)
    with psycopg.connect(POSTGRES_URL, autocommit=True) as connection:
        connection.execute(f'CREATE SCHEMA "{schema}"')
    url = make_conninfo(POSTGRES_URL, options=f"-csearch_path={schema}")
    backends.refresh(backends.BACKENDS["postgres"], url, SCHEMA, RULES["foreign_keys"], sample_tables(), 1000)
    reader_url = None
    with psycopg.connect(POSTGRES_URL, autocommit=True) as connection:
        try:
            connection.execute(f"CREATE ROLE \"{reader}\" LOGIN PASSWORD '{password}'")
            connection.execute(f'GRANT USAGE ON SCHEMA "{schema}" TO "{reader}"')
            connection.execute(f'GRANT SELECT ON ALL TABLES IN SCHEMA "{schema}" TO "{reader}"')
            reader_url = make_conninfo(POSTGRES_URL, user=reader, password=password,
                                       options=f"-csearch_path={schema}")
        except psycopg.Error:
            pass   # no CREATEROLE: the reader tests skip
    yield {"url": url, "reader_url": reader_url, "schema": schema,
           "database": conninfo_to_dict(POSTGRES_URL).get("dbname")}
    with psycopg.connect(POSTGRES_URL, autocommit=True) as connection:
        connection.execute(f'DROP SCHEMA "{schema}" CASCADE')
        if reader_url:
            connection.execute(f'DROP OWNED BY "{reader}"')
            connection.execute(f'DROP ROLE "{reader}"')


@pytest.fixture(params=["sqlite", "postgres"])
def settings(request):
    """Settings with a database, for each backend, with small limits so the tests can reach them.

    Definitions mode doesn't need a database: these are for the dormant query path and for
    get_database_info's database status."""
    if request.param == "sqlite":
        return Settings(backend="sqlite", sqlite_path=request.getfixturevalue("sqlite_path"), max_rows=20,
                        query_timeout_seconds=1.0)
    return Settings(backend="postgres", postgres_url=request.getfixturevalue("postgres")["url"], max_rows=20,
                    query_timeout_seconds=1.0)


def call(settings, tool, arguments=None):
    """Call a tool over MCP. Returns (is_error, structured content), each checked against the contract."""
    return call_many(settings, [(tool, arguments or {})])[0]


def call_many(settings, calls):
    async def run():
        results = []
        async with Client(build_server(settings)) as client:
            for tool, arguments in calls:
                with anyio.fail_after(30):
                    results.append(await client.call_tool(tool, arguments))
        return results

    checked = []
    for (tool, _), result in zip(calls, anyio.run(run)):
        if result.is_error:
            jsonschema.validate(result.structured_content, ERROR_SCHEMA)
        else:
            jsonschema.validate(result.structured_content, PUBLISHED[tool]["outputSchema"])
        assert json.loads(result.content[0].text) == result.structured_content
        checked.append((result.is_error, result.structured_content))
    return checked


def error_code(settings, tool, arguments):
    is_error, content = call(settings, tool, arguments)
    assert is_error, content
    return content["error"]["code"]


def query(settings, sql, params=None, max_rows=None):
    """The dormant execute_query, called in Python. Returns (is_error, content), checked against its contract."""
    result = _guarded(lambda: Tools(settings).execute_query(sql, params, max_rows))
    jsonschema.validate(result.structured_content, ERROR_SCHEMA if result.is_error else QUERY_SCHEMA)
    return result.is_error, result.structured_content


def query_error_code(settings, sql, params=None, max_rows=None):
    is_error, content = query(settings, sql, params, max_rows)
    assert is_error, content
    return content["error"]["code"]


def ph(settings):
    """The backend's placeholder."""
    return "?" if settings.backend == "sqlite" else "%s"


def table_counts(settings):
    _, content = query(settings, " UNION ALL ".join(f"SELECT '{t}', COUNT(*) FROM {t}" for t in sorted(SCHEMA)))
    return content["rows"]
