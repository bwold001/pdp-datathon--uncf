# MCP server: plan

Status: **built, then aligned with the Query Layer.** First built as planned below, with five
tools, and approved on #11 with four decisions:
- build a custom server
- no small-group suppression, documented as an open limitation
- commit `mcp/schemas/tools.json` under a narrow AGENTS.md exception
- keep each database's own placeholders

It was then changed to meet the Query Layer's access rules. That change is described in the next
section, and replaces the five-tool contract below. Refs #11.

## Query Layer alignment

The Query Layer's goal is to let apps and coding assistants use shared measures and definitions
within agreed access limits. Definitions-only is the default: it exposes definitions and metadata,
no data-query tools and no student-level values. Access is set by trusted configuration. A gap
assessment against the five-tool server found the default exposure in conflict, and these
decisions were approved:

| # | Decision | What was built |
|---|---|---|
| D1 | Keep `execute_query` without exposing it | `Tools.execute_query`, `db.py` and `query.py` are unchanged and still tested in Python (`tests/test_query.py`, `tests/test_read_only.py`). No access mode registers the tool. There is no student-level mode. |
| D2 | Definitions mode reads repo metadata, not a database | `list_tables` and `describe_table` read `destination_schema.yaml` through `metadata.py`. `data_type` is null. A test checks the schema matches what the loader built in both databases. The server starts and serves with no database. |
| D3 | Measures stay blocked | Nothing built. What #9 must provide is in [integration.md](integration.md#shared-measures-9). |
| D4 | Definitions-only is the default | `PDP_MCP_ACCESS_MODE`, default `definitions`. `aggregate` is reserved: it stops startup with a message naming #9. Other values stop it too. No fallback. |
| D5 | Chat can import or use MCP | `pdp_mcp.metadata` has no MCP or database dependency. Both paths are in [integration.md](integration.md#chat-endpoint-30). |

The contract changes are listed in
[tool-contracts.md](tool-contracts.md#breaking-changes-from-the-proposed-five-tool-contract). The
rest of this file is the original plan, kept as the record of what was built first. Where it
disagrees with the section above, the section above holds.

## Original plan

A local, read-only MCP server over the normalized PDP database that the loader builds (proposal
#8, `normalized-data-model/`). It works with SQLite and PostgreSQL, and has five tools. **The data
is synthetic**: nothing queried through it is a finding about real students or institutions.

## What exists today (on `data-model/8-loaders`)

- **Tables** are defined once, in `normalized-data-model/config/destination_schema.yaml`: 9 tables,
  each column with a Python type, nullability, keys and rules. Closed and open value lists are in
  `config/value_sets.yaml`.
- **Source to table:** `config/*_mapping.yaml` says where each source column goes, and how the file
  writes "no value" and "unknown".
- **Column meanings:** `data/dictionaries/column_lookup.csv` (`file, column_in_csv,
  dictionary_name, description`) for the 120 Analysis-Ready File columns, plus the markdown
  dictionaries.
- **Loader:** `python -m src.loader.load` writes `normalized-data-model/output/pdp.sqlite`, or loads
  PostgreSQL from `PDP_POSTGRES_URL` into the connection's default schema. It drops and recreates the
  model's tables on every load. Types are `TEXT/INTEGER/REAL/BOOLEAN` in SQLite and
  `TEXT/BIGINT/DOUBLE PRECISION/BOOLEAN/DATE/TIMESTAMP` in PostgreSQL. SQLite stores dates as ISO text.
- **Conventions:** Python 3.10+, packages pinned in the root `requirements.txt` and installed in
  `.venv/`, pytest tests added as a line under `make check`, env vars for credentials, no config
  framework.

## Tool contracts

Five tools, specified in [tool-contracts.md](tool-contracts.md). The machine-readable copy is
[../schemas/tools.json](../schemas/tools.json):

| Tool | Input | Returns |
|---|---|---|
| `list_tables` | none | the tables and views, each marked if it's in the model, with a one-line description from the model's README |
| `describe_table` | `table` | columns (database type, model type, nullable, primary key), primary key, foreign keys, incoming references, unique groups |
| `execute_query` | `sql`, optional `params`, optional `max_rows` | `columns`, `rows` as arrays, `row_count`, `truncated`, `elapsed_ms` |
| `get_column_definition` | `column`, optional `table`, optional `source_file` | every match, each marked `source` (a raw file column) or `normalized` (a table column), linked to the other kind |
| `get_database_info` | none | engine, health, schema, model tables present and missing, counts, limits, parameter style, warnings. No credentials. |

**One source of truth, nothing copied by hand.** The tool functions and their Pydantic models in
`mcp/pdp_mcp/` are the definition. `python -m pdp_mcp.export_schemas` asks the running server for
its `tools/list` and writes `mcp/schemas/tools.json`. A test fails if the committed file differs
from what the server lists, both in-process and over stdio.

**Errors** come back as a tool result with `isError: true` and
`structuredContent: {"error": {"code", "message", "details"}}`. The codes are `invalid_argument`,
`not_found`, `query_rejected`, `query_failed`, `timeout`, `database_unavailable` and
`internal_error`. One exception, from the SDK: arguments that don't match the input schema are
rejected before the tool runs, with text only. Treat that as `invalid_argument`.

## Read-only, in layers

No layer relies on matching SQL keywords alone. Each one would stop a write by itself.

| Layer | SQLite | PostgreSQL |
|---|---|---|
| Connection | opened `file:...?mode=ro` (URI), so a missing file is an error, not a new database. `PRAGMA query_only = ON`. | `default_transaction_read_only=on` set at connect. Recommended: a role with `SELECT` only (README gives the SQL). |
| Per query | an authorizer callback allows only `SELECT`, `READ`, `FUNCTION` and `RECURSIVE`. That denies `ATTACH`, `PRAGMA`, writes and DDL, whatever the SQL text says. A short function denylist (`load_extension`, `readfile`, `writefile`, `edit`, `fts3_tokenizer`) also applies. | each query in its own `BEGIN READ ONLY` transaction, always `ROLLBACK`, never commit. That also undoes `set_config`. |
| One statement | `sqlite3` refuses a second statement itself | sent with the extended query protocol, which refuses more than one command |
| Statement kind | the first keyword, after comments, must be `SELECT`, `WITH`, `VALUES` or `EXPLAIN` (`EXPLAIN ANALYZE` is refused). This layer gives a clear error early; the database layers above are what enforce it. | same |
| Time | a progress handler interrupts the query at the deadline | `SET LOCAL statement_timeout` |
| Size | `fetchmany(max_rows + 1)`, so `truncated` is exact and the rest is never read | same, with a server-side cursor |

`get_database_info` warns when the PostgreSQL role is a superuser or can write a model table. A
superuser can read server files with `pg_read_file`, which no read-only transaction stops.

Errors never include the connection URL. PostgreSQL error text is passed through only from the
query's own error (`SQLSTATE` and message). Connection errors are replaced with a fixed message
that names the environment variable, never its value.

## SQLite and PostgreSQL differences the contract exposes

- `engine` is `sqlite` or `postgres`, the same names as the loader's `--backend`.
- **Parameter placeholders** are each database's own: `?` in SQLite and `%s` in PostgreSQL.
  `get_database_info.param_style` says which (`qmark` or `format`). With params in PostgreSQL, a
  literal `%` is written `%%`. Translating one style into the other would mean parsing SQL, so it's
  left out.
- **`data_type`** is the database's declared type (`TEXT`, `BIGINT`...). `model_type` is the
  schema's type (`str`, `int`, `float`, `bool`, `date`, `datetime`) and is the same in both.
- **Dates** come back as ISO 8601 strings in both. SQLite has them as text already.
- **Booleans**: PostgreSQL returns `true`/`false`, SQLite `1`/`0`. Documented, not converted: the
  query decides the shape of its own results.
- **Schema**: SQLite is `main`; PostgreSQL is `current_schema()`, the same schema the loader wrote.

## Configuration

Environment variables only, read at startup. Nothing new to install beyond the root
`requirements.txt`.

| Variable | Default | Meaning |
|---|---|---|
| `PDP_MCP_BACKEND` | `sqlite` | `sqlite` or `postgres` |
| `PDP_MCP_SQLITE_PATH` | `normalized-data-model/output/pdp.sqlite` (from the repo root) | the database the loader wrote |
| `PDP_MCP_POSTGRES_URL` | none | the connection URL. Separate from the loader's `PDP_POSTGRES_URL` so it can use a read-only role. |
| `PDP_MCP_MAX_ROWS` | `500` | the most rows a query returns. A call's `max_rows` can only lower it. |
| `PDP_MCP_QUERY_TIMEOUT_SECONDS` | `30` | per query |
| `PDP_MCP_LOG_LEVEL` | `WARNING` | logs go to stderr, never stdout, which carries the MCP protocol |

**At startup** the server stops with exit code 2 and a message on stderr if:
- a setting is invalid
- the SQLite file is missing
- the database has none of the model's tables

A model that's only partly there starts, with a warning in `get_database_info`. A PostgreSQL server
that's down at a later call returns `database_unavailable`. It doesn't stop the server.

## Layout

```
mcp/
  README.md                 participant setup, client configs, smoke test, troubleshooting
  run_server.py             launcher clients point at (puts pdp_mcp on the path; no cwd needed)
  docs/plan.md              this file
  docs/tool-contracts.md    the contracts, for people
  docs/integration.md       for the chat, metadata assistant, dictionary UI and measures workstreams
  schemas/tools.json        generated from the server: name, description, inputSchema, outputSchema, annotations
  pdp_mcp/
    __main__.py             python -m pdp_mcp
    server.py               MCPServer, the 5 tools, error results
    contracts.py            Pydantic input and output models: the contract
    config.py               env vars
    db.py                   connect, discovery and execution, one small class per backend
    query.py                statement checks, limits, JSON conversion of values
    metadata.py             column_lookup.csv + destination_schema.yaml + mapping configs
    export_schemas.py       writes schemas/tools.json from the server
  tests/                    pytest; PostgreSQL tests need PDP_TEST_POSTGRES_URL, like the loader's
```

`mcp/` has no `__init__.py` on purpose. A regular package named `mcp` would hide the MCP SDK
(`import mcp`) for anything run from the repo root.

## Dependencies

Added to `requirements.txt`, pinned:
- `mcp==2.3.0`: the official SDK. It brings Pydantic and needs Python 3.10 or newer.
- `jsonschema==4.26.0`: checks outputs against `outputSchema` in the tests. The SDK already
  depends on it.

`psycopg[binary]` and `pyyaml` are already there.

## Checks

| Check | How |
|---|---|
| The 5 tools are listed, with the published schemas | test: in-memory `tools/list` equals `schemas/tools.json`. A second test launches `run_server.py` over stdio and compares too. |
| Outputs match `outputSchema` | test: every success result is validated with `jsonschema`, on both backends |
| Errors are consistent | test: each error code is produced at least once and has the error shape |
| Read-only | tests: `INSERT`, `UPDATE`, `DELETE`, `CREATE`, `DROP`, `ATTACH`, `PRAGMA`, `load_extension`, a data-modifying CTE, `set_config`, `nextval`, `SELECT ... FOR UPDATE`, `COPY`, two statements, and comment tricks. Then a checksum (SQLite) or row counts (PostgreSQL) prove nothing changed. |
| Limits | tests: `max_rows` truncates and says so. A recursive CTE and `pg_sleep` time out. |
| Discovery and definitions | tests against a SQLite database built from the committed 10-student sample (`data/output/sample/`), through the loader's own `backends.refresh`, so nothing new is committed |
| PostgreSQL | the same tests against a real server when `PDP_TEST_POSTGRES_URL` is set. Run locally against Homebrew PostgreSQL 17 and reported. CI skips them, as it does the loader's. |
| Clients | the smoke test in `mcp/README.md` with Claude Code. VS Code and Cursor configs are written to their documented formats; whether they're tested by hand is reported in the pull request. |
| Repo | `make check` passes, with `cd mcp && python3 -m pytest -q` added |

## Open questions

1. **Scope against #11.** The proposal says "Out of scope: building a custom MCP server" and plans a
   DBHub config, 5 hours. This plan is a custom server, which is more work. Per CONTRIBUTING ("If it
   grows"), the Leads should OK it in #11, and the issue body should be updated. #11 has no `funded`
   label yet.
2. **Small-group suppression** (#11 completion test 8, Seth's comment). `execute_query` runs any read
   query, so it can't guarantee counts under 10 are hidden. A filter on query results could be
   worked around with an `OFFSET` or a `CASE`. Proposal: say so plainly, and leave suppression to
   #9's measure outputs and #20's metadata pack. If suppression is a hard requirement, the only real
   guarantee is to expose only approved views, which is a different tool.
3. **Committing `mcp/schemas/tools.json`.** AGENTS.md says not to commit generated outputs. This
   file is a contract, not the result of a run, and squads in other stacks need it without running
   Python. Proposal: add it to the AGENTS.md exception list, as #8 did for its samples.
4. **Base branch.** CONTRIBUTING says branch from `main`; this branches from `data-model/8-loaders`
   because the loader isn't merged. The pull request targets that branch, and is retargeted to
   `main` when #8 lands.
5. **Dictionary text.** `get_column_definition` returns the lookup description, the dictionary file
   and entry name, and the allowed codes from the schema. It doesn't return the code meanings from
   the markdown dictionaries (for example `C = college ready`), because those files have no
   reliable headings to parse. #28's `fields` table would fill that in.
6. **Descriptions for `list_tables`** come from the "The tables" table in
   `normalized-data-model/README.md`. That's the only place they're written down. A test fails if
   that table and the schema stop listing the same tables.

## Order of work

1. Contracts: models, tool signatures, `schemas/tools.json`, `tool-contracts.md` and the schema
   test. **Then stop for review.**
2. SQLite: config, startup checks, `get_database_info`, `list_tables`, `describe_table`.
3. `execute_query` with every layer above, and its tests.
4. `get_column_definition`.
5. PostgreSQL backend; the same tests against a real server.
6. README, integration guide, `make check`, pull request to `data-model/8-loaders` with `Refs #11`.
