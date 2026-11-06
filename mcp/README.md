# PDP MCP server

A local, read-only [Model Context Protocol](https://modelcontextprotocol.io/) server for the
definitions of the normalized PDP data model (proposal
[#11](https://github.com/devcolor/pdp-datathon-starter/issues/11), part of the Query Layer). Point
an MCP-capable AI client at it, and the assistant can find the model's tables, see how they join,
and read what each column means, without seeing any student data. See
[client status](#client-status) for which clients have been checked.

**The data is synthetic.** Nothing built on it is a finding about real students or institutions.

- It runs on your machine, over stdio. Nothing is hosted.
- **It needs no database.** It reads the repository's metadata files: the model's schema, the
  mapping configs and the data dictionaries.
- It has no data-query tools and returns no student-level values.
- It has no embeddings or vector search.

## Access modes

What the server exposes is set by trusted configuration when it starts, never by a tool argument
or a chat message.

| `PDP_MCP_ACCESS_MODE` | What it exposes | Status |
|---|---|---|
| `definitions` (the default) | The four metadata tools below. No data-query tools, no student-level values. | Available |
| `aggregate` | Approved shared measures from the Measures workstream (#9), as published. | **Not available yet.** It waits for #9's manifest and output contract. Setting it stops the server with a message saying so. |

There is no student-level mode. Running SQL against student rows waits on an access-policy decision.
The query code is kept and tested, but no mode exposes it (see
[tool-contracts.md](docs/tool-contracts.md#dormant-execute_query)).

## The tools

| Tool | What it does |
|---|---|
| `list_tables` | Lists the model's 10 tables and what one row of each is. |
| `describe_table` | A table's columns, model types, nullability, primary key, foreign keys, unique groups, and the tables that point at it. |
| `get_column_definition` | What a column means: the data dictionary description, allowed codes, and where it comes from or goes to. Works for raw file columns (`Retention`) and table columns (`cohort_membership.retention`). |
| `get_database_info` | The access mode, the tools it exposes, the metadata files it reads (with checksums), and, if you configured one, whether your database is reachable. |

The full contracts are in [docs/tool-contracts.md](docs/tool-contracts.md). The machine-readable
copy is [schemas/tools.json](schemas/tools.json).

## Set up

You need Python 3.10 or newer, and a checkout that includes the data model (`normalized-data-model/`),
whose files the server reads. You don't need to load a database. Everything below runs from the
repository root.

1. **Check your Python.** On macOS and Linux, `python` may be missing or old: use `python3`.

   ```bash
   python3 --version        # 3.10 or newer. Windows: py --version
   ```

2. **Install**, once. This is the repository's usual virtual environment; skip it if you already
   made `.venv` for another foundation.

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   python -m pip install -r requirements.txt
   ```

   That installs every foundation's pinned packages, including the MCP SDK (`mcp==2.3.0`). The MCP
   server itself needs only `mcp` and `pyyaml` from that list.

3. **Check that it starts:**

   ```bash
   .venv/bin/python mcp/run_server.py < /dev/null
   echo $?                          # 0
   ```

   On Windows, in Command Prompt: `.venv\Scripts\python mcp\run_server.py < NUL`, then `echo %ERRORLEVEL%`.
   (Windows hasn't been tested.)

   No output and exit code 0 means it started, read its metadata, and stopped when its input
   closed. A problem prints `pdp-mcp: can't start: ...` and exits with code 2. A server that
   starts and then waits is normal when you leave out `< /dev/null`: it's waiting for a client.
   Press Ctrl+C.

4. **Add it to your AI client**: see [Connect a client](#connect-a-client).

5. **Check it in the client** with the [smoke test](#smoke-test). For a full manual test, see
   [docs/uat.md](docs/uat.md).

## Settings

Environment variables, read once when the server starts. Set them in your client's config (`env`),
not in a committed file. None is required.

| Variable | Default | What it does |
|---|---|---|
| `PDP_MCP_ACCESS_MODE` | `definitions` | See [Access modes](#access-modes). Anything else stops the server. |
| `PDP_MCP_BACKEND` | unset | Optional: `sqlite` or `postgres`. Only lets `get_database_info` report whether your loaded database is reachable. No tool reads it, and it adds no tools. |
| `PDP_MCP_SQLITE_PATH` | `normalized-data-model/output/pdp.sqlite` | With `PDP_MCP_BACKEND=sqlite`: the database the [loader](../normalized-data-model/README.md#load-the-data) wrote. A relative path is read from the repository root. Opened read-only, never created. |
| `PDP_MCP_POSTGRES_URL` | none | With `PDP_MCP_BACKEND=postgres`: the connection URL. Use a role that can only read (see below). |
| `PDP_MCP_LOG_LEVEL` | `WARNING` | `DEBUG`, `INFO`, `WARNING` or `ERROR`. Logs go to stderr; your client usually shows them in its MCP output panel. |

If you do point it at PostgreSQL, use a read-only role. The loader's role can write.

```sql
CREATE ROLE pdp_reader LOGIN PASSWORD 'choose-a-password';
GRANT CONNECT ON DATABASE pdp TO pdp_reader;
GRANT USAGE ON SCHEMA public TO pdp_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO pdp_reader;
ALTER DEFAULT PRIVILEGES FOR ROLE <loader_role> IN SCHEMA public GRANT SELECT ON TABLES TO pdp_reader;
```

`get_database_info` warns if the role is a superuser or can write a model table.

## Connect a client

Every client starts the same command: the repository's Python running `mcp/run_server.py`. The
launcher needs no working directory.
- Replace `/absolute/path/to/pdp-datathon-starter` with where you cloned the repository. Run `pwd`
  in it to see.
- On Windows, the Python is `.venv\Scripts\python.exe` instead of `.venv/bin/python`.
- No settings are needed for definitions mode. A client only passes the environment variables you
  put in its config, not your shell's, so put any `PDP_MCP_*` setting in the config's `env`.

### Client status

| Client | Status |
|---|---|
| Claude Code (CLI) | **Checked** on macOS, with the config below given through `--mcp-config`: all 4 tools found and used, no query tool offered. |
| VS Code (GitHub Copilot agent mode) | Config follows VS Code's documented `mcp.json` format. **Not yet checked by hand.** |
| Cursor | Config follows Cursor's documented `mcp.json` format. **Not yet checked by hand.** |
| Others | Any client that runs a stdio MCP server should work with the generic config. Not checked. |

If you check one, record it in [docs/uat.md](docs/uat.md).

### VS Code (GitHub Copilot agent mode)

Create `.vscode/mcp.json` in the repository. On Windows, use
`${workspaceFolder}/.venv/Scripts/python.exe` as the command.

```json
{
  "servers": {
    "pdp": {
      "type": "stdio",
      "command": "${workspaceFolder}/.venv/bin/python",
      "args": ["${workspaceFolder}/mcp/run_server.py"]
    }
  }
}
```

Open the file, select **Start** above `pdp`, then open Copilot Chat in **Agent** mode and check the
tools list.

### Cursor

Create `.cursor/mcp.json` in the repository, or add the entry to `~/.cursor/mcp.json` for every
project. Use absolute paths:

```json
{
  "mcpServers": {
    "pdp": {
      "command": "/absolute/path/to/pdp-datathon-starter/.venv/bin/python",
      "args": ["/absolute/path/to/pdp-datathon-starter/mcp/run_server.py"]
    }
  }
}
```

Then open **Settings → MCP**, check `pdp` is on and shows 4 tools, and use it from Agent chat.

### Claude Code

From the repository root:

```bash
claude mcp add pdp -- "$PWD/.venv/bin/python" "$PWD/mcp/run_server.py"
```

This adds it for this project only (Claude Code's default `local` scope). `/mcp` in a session shows
its status. Or, without changing your Claude Code settings, put the [generic config](#any-other-mcp-client)
in a file and start a session with `claude --mcp-config that-file.json`. That's how it was checked.

### Any other MCP client

Any client that runs a stdio server takes the same three things:

| | Value |
|---|---|
| command | `/absolute/path/to/pdp-datathon-starter/.venv/bin/python` |
| args | `["/absolute/path/to/pdp-datathon-starter/mcp/run_server.py"]` |
| env | the [settings](#settings) you need, usually none |

Most use this shape:

```json
{"mcpServers": {"pdp": {"command": "...", "args": ["..."], "env": {}}}}
```

## Things to ask

Once connected, ask in plain language. The assistant chooses the tools. For example:

- "What tables are in the PDP data model, and how do they join?"
- "What does `Gateway_Math_Status` mean, and what codes can it have?"
- "Is `enrollment_type` in the cohort table or the student table? Which file column does it come from?"
- "Which columns could I use to break down retention by student group?"
- "Write a SQL query for first-time students' retention by Pell status. I'll run it myself."

The server can't run queries or count students: ask the assistant to write the SQL, then run it
yourself against your own database (see [Load the data](../normalized-data-model/README.md#load-the-data)).
How measures such as retention should be counted belongs to the Measures workstream (#9).

## Example tool calls

These are the arguments a client sends. The results are shortened.

```json
// list_tables
{}
// → {"source": "normalized-data-model/config/destination_schema.yaml",
//    "tables": [{"name": "cohort_membership", "type": "table", "in_model": true,
//                "description": "student and cohort, with everything the cohort file says about that cohort"}, ...]}

// describe_table
{"table": "student"}
// → {"primary_key": ["student_id"],
//    "columns": [{"name": "student_id", "data_type": null, "model_type": "str", "nullable": false, ...}, ...],
//    "referenced_by": [{"table": "cohort_membership", "columns": ["student_id"], ...}, ...], ...}

// get_column_definition
{"column": "retention"}
// → matches: [{"kind": "source", "source_file": "pdp_cohort_data.csv", "source_column": "Retention",
//              "description": "Retention is defined as either continued enrollment ...", ...},
//             {"kind": "normalized", "table": "cohort_membership", "column": "retention", "model_type": "bool", ...}]
```

## Smoke test

After setting up, check these five things in your client:

1. **It starts.** The client shows `pdp` as running or connected. If not, run step 3 of
   [Set up](#set-up) in a terminal and read the message.
2. **It has exactly 4 tools:** `list_tables`, `describe_table`, `get_column_definition`,
   `get_database_info`.
3. **Schema discovery works.** Ask "Describe the student table." It should give `student_id` as
   the primary key and list the 3 tables that point at it.
4. **Definitions work.** Ask "What does Retention mean?" It should quote the data dictionary.
5. **It has no data access.** Ask "How many students are there? Use the pdp tools." The assistant
   should say it has no tool for that. `get_database_info` shows `access_mode: definitions`.

The tests run the same steps over stdio, with no database (`tests/test_startup.py`).

## Troubleshooting

| What you see | What to do |
|---|---|
| `can't start: PDP_MCP_ACCESS_MODE=aggregate isn't available yet` | Aggregate mode waits for the Measures workstream. Unset `PDP_MCP_ACCESS_MODE`. |
| `can't start: can't read normalized-data-model/...` | A metadata file is missing: your checkout is incomplete or on the wrong branch. |
| The client shows the server failing with no message | Run the client's command in a terminal: the message goes to stderr. Check the paths are absolute and point at `.venv`'s Python. |
| `ModuleNotFoundError: No module named 'mcp'` | The client is using another Python. Point `command` at the repository's `.venv` Python, and install the requirements there. |
| A `PDP_MCP_*` setting seems to be ignored | Clients don't pass your shell's environment to the server. Put the setting in the client config's `env`. |
| `get_database_info` shows `database.healthy: false` | Only if you set `PDP_MCP_BACKEND`. The tools still work. The reason is in `database.error`. |
| A warning that the PostgreSQL role is a superuser or can write | Make the `pdp_reader` role above and use it. |
| Answers don't show a change you pulled or made to the data model's configs | The server reads them once, on first use. Restart it: in your client, restart or reconnect the `pdp` server. |

## Security and limits

- **Definitions only.** The registered tools read repo files and return names, types, keys,
  dictionary text and the codes the schema allows. A test sends every table and column to every tool
  with a database of sample students configured, and checks that no student ID or course name
  comes back.
- **Nothing to query.** `execute_query` isn't registered, so a client can't list or call it: calling
  it returns `Unknown tool`. No setting registers it.
- **The access mode is fixed at startup** by environment variables. No tool has an argument that
  changes it.
- **No authentication.** The server trusts whoever starts it, as any local stdio server does. It
  has no network port.
- **Credentials** are read from the environment and never returned or logged by the server.
- **Small groups:** this mode returns no counts, so there's nothing to suppress. When aggregate
  mode arrives, it will pass on the Measures workstream's published results, statuses and blanks
  as they are. Suppression is decided there, not here.

## For other workstreams

[docs/integration.md](docs/integration.md) covers the chat endpoint, the metadata assistant, the
data dictionary and the measures work, and what each workstream still needs to provide.

## Develop and test

From `mcp/`:

```bash
python -m pytest -q                         # all tests; PostgreSQL ones skip without a server
PDP_TEST_POSTGRES_URL=postgresql://user@localhost:5432/pdp_test python -m pytest -q
python -m pdp_mcp.export_schemas            # after changing a tool's arguments or output models
```

The metadata tools are tested over MCP, without a database. The dormant query path and its
read-only safeguards are tested in Python, in SQLite and, with `PDP_TEST_POSTGRES_URL` set,
PostgreSQL. Those tests build their databases from the committed 10-student sample through the
loader's own table code. CI runs `make check`, which runs everything except PostgreSQL.

| File | What it is |
|---|---|
| `run_server.py` | The launcher clients start. |
| `pdp_mcp/server.py` | Registers the tools the access mode allows, and turns failures into error results. |
| `pdp_mcp/contracts.py` | The output models: the contract. |
| `pdp_mcp/metadata.py` | Tables, keys and column definitions from the repo's files. No MCP and no database: chat can import it. |
| `pdp_mcp/config.py` | The settings and access modes. |
| `pdp_mcp/db.py`, `pdp_mcp/query.py` | SQLite and PostgreSQL, read-only. Used for `get_database_info`'s database status, and by the dormant query path. |
| `pdp_mcp/export_schemas.py` | Writes `schemas/tools.json` from the running server. |
| `docs/plan.md` | The plan, and how it changed for the Query Layer. |

`mcp/` has no `__init__.py` on purpose. A package named `mcp` would hide the MCP SDK, which is
also imported as `mcp`.
