# PDP MCP server: tool contracts

Status: **verified, definitions mode.** These are the four tools the server registers in its
default and only access mode, `definitions`. `mcp/tests/` checks every result against these schemas
over MCP, and checks that the server lists exactly these tools. This replaces the five-tool contract
proposed on #11. [Breaking changes](#breaking-changes-from-the-proposed-five-tool-contract) lists
what changed and who it affects.

**The data is synthetic.** Nothing built on it is a finding about real students or institutions.

- **Machine-readable:** [../schemas/tools.json](../schemas/tools.json). It's exactly what the
  server's `tools/list` returns in definitions mode, for each tool: `name`, `description`,
  `inputSchema`, `outputSchema` and `annotations`. It's generated from the server (`python -m
  pdp_mcp.export_schemas`, run from `mcp/`), and a test fails if it differs, in-process or over stdio.
- **Definition:** [../pdp_mcp/contracts.py](../pdp_mcp/contracts.py) (output models) and
  [../pdp_mcp/server.py](../pdp_mcp/server.py) (tool arguments, and which tools each mode registers).
- **Server name:** `pdp-datathon`. **Transport:** stdio.

## Access modes

| Mode | Set by | Tools |
|---|---|---|
| `definitions` | the default, or `PDP_MCP_ACCESS_MODE=definitions` | `list_tables`, `describe_table`, `get_column_definition`, `get_database_info` |
| `aggregate` | reserved | none yet: setting it stops the server with exit code 2 until the Measures (#9) contract is agreed |

The mode is read once, from the environment, when the server starts. No tool takes an argument
that changes it, and the tool list never changes while the server runs. There is no student-level
mode.

## Common to every tool

**Read-only, no student-level values.** Every tool reads repo metadata files. None reads a table's
rows, and none writes anything. Each is annotated `readOnlyHint: true`, `destructiveHint: false`,
`idempotentHint: true` and `openWorldHint: false`.

**Success.** `isError: false`. `structuredContent` is the tool's result object, which matches its
`outputSchema`. `content[0].text` holds the same JSON.

**Failure.** `isError: true`, and `structuredContent` (and `content[0].text`) is:

```json
{"error": {"code": "not_found", "message": "No table named 'students' in the normalized model.", "details": {"suggestions": ["student"]}}}
```

| `code` | Means | From |
|---|---|---|
| `not_found` | no such table or column. `details.suggestions` lists close names. | `describe_table`, `get_column_definition` |
| `internal_error` | a bug or unreadable metadata. The message is generic, and the detail is logged on the server. | any tool |

The error schema also lists `invalid_argument`, `query_rejected`, `query_failed`, `timeout` and
`database_unavailable`. They're only returned by the dormant query path. Definitions-mode tools
never return them; `get_database_info` reports an unreachable database in its output instead.

**From the MCP SDK:** arguments that break a tool's `inputSchema` (`"table": ""`) are rejected
before the tool runs, as `isError: true` with a text message and no `structuredContent`. Treat
that as `invalid_argument`. Calling a tool that isn't registered, such as `execute_query`, returns
`isError: true` with the text `Unknown tool: <name>`.

**No credentials** appear in any result or error.

---

## `list_tables`

**Purpose.** Find out what tables the normalized model has. Usually the first call.

**Input.** None: `{}`.

**Output.** `ListTablesResult`:

| Field | Type | Meaning |
|---|---|---|
| `source` | string | `normalized-data-model/config/destination_schema.yaml`, where the tables come from |
| `tables[]` | object | by name |
| `tables[].name` | string | |
| `tables[].type` | `"table"` \| `"view"` | always `table` in definitions mode |
| `tables[].in_model` | boolean | always true in definitions mode |
| `tables[].description` | string \| null | what one row is, from "The tables" in [normalized-data-model/README.md](../../normalized-data-model/README.md) |

Only the model's 10 tables are listed. Tables or views a squad adds to its own database aren't in
the model's schema, so they aren't listed.

**Example.**

```json
{"source": "normalized-data-model/config/destination_schema.yaml", "tables": [
  {"name": "cohort_membership", "type": "table", "in_model": true,
   "description": "student and cohort, with everything the cohort file says about that cohort"},
  {"name": "course", "type": "table", "in_model": true, "description": "course prefix and number"}
]}
```

**Errors.** `internal_error` only.

---

## `describe_table`

**Purpose.** Learn a table's columns and how it joins to the others.

**Input.**

| Field | Type | Required | Meaning |
|---|---|---|---|
| `table` | string, 1–128 characters | yes | a name from `list_tables`. Exact match, then a case-insensitive one. |

**Output.** `DescribeTableResult`, from `destination_schema.yaml`, the file the loader creates
every table from:

| Field | Type | Meaning |
|---|---|---|
| `name`, `type`, `in_model`, `description` | | as in `list_tables` |
| `columns[]` | object | in column order |
| `columns[].name` | string | |
| `columns[].data_type` | string \| null | **always null in definitions mode.** It's a database's declared type (`TEXT`, `BIGINT`), and no database is read. |
| `columns[].model_type` | `str` \| `int` \| `float` \| `bool` \| `date` \| `datetime` | the model's type, the same in every engine |
| `columns[].nullable` | boolean | |
| `columns[].primary_key` | boolean | |
| `primary_key` | string[] | in column order |
| `foreign_keys[]` | `{columns, references_table, references_columns}` | in the order of their first column |
| `referenced_by[]` | `{table, columns, references_columns}` | other tables' foreign keys that point here, by table |
| `unique_constraints` | string[][] | each set of columns that is unique together, sorted |

A test checks that, for every model table, these columns, nullability, keys and unique groups are
exactly what SQLite and PostgreSQL report for the tables the loader built.

**Example.** `{"table": "course_enrollment"}` (most columns cut):

```json
{"name": "course_enrollment", "type": "table", "in_model": true,
 "description": "course-file row: a student in a course in a term",
 "columns": [
   {"name": "enrollment_id", "data_type": null, "model_type": "int", "nullable": false, "primary_key": true},
   {"name": "student_id", "data_type": null, "model_type": "str", "nullable": false, "primary_key": false}
 ],
 "primary_key": ["enrollment_id"],
 "foreign_keys": [
   {"columns": ["provider_id"], "references_table": "data_provider", "references_columns": ["provider_id"]},
   {"columns": ["student_id"], "references_table": "student", "references_columns": ["student_id"]},
   {"columns": ["student_id", "cohort"], "references_table": "cohort_membership", "references_columns": ["student_id", "cohort"]},
   {"columns": ["course_id"], "references_table": "course", "references_columns": ["course_id"]},
   {"columns": ["term_id"], "references_table": "term", "references_columns": ["term_id"]}
 ],
 "referenced_by": [],
 "unique_constraints": [["provider_id", "source_row_number"]]}
```

**Errors.** `not_found`, with `details.suggestions` (`students` suggests `student`).

---

## `get_column_definition`

Unchanged from the proposal.

**Purpose.** Find out what a column means, where it comes from, and what values it can hold,
without guessing from its name.

**Input.**

| Field | Type | Required | Meaning |
|---|---|---|---|
| `column` | string, 1–128 characters | yes | a raw file column (`Retention`, `Student_GUID`), a dictionary name (`Student ID`), a normalized column (`retention`), or `table.column` (`cohort_membership.retention`). Case doesn't matter. |
| `table` | string | no | only normalized columns of this table |
| `source_file` | string | no | only source columns of this file, such as `pdp_course_data.csv` |

**Output.** `ColumnDefinitionResult`: the arguments echoed in `query`, and `matches`, each a
**source** or a **normalized** definition, told apart by `kind`. Source matches come first.

`kind: "source"`: a column in a raw input file.

| Field | Meaning |
|---|---|
| `source_file`, `source_column` | as the file writes it |
| `dictionary_name`, `description` | from [column_lookup.csv](../../data/dictionaries/column_lookup.csv). Null if the lookup has nothing: enrichment files aren't in it. |
| `dictionary_file` | the markdown dictionary with the full entry, repo-relative |
| `destinations[]` | `{table, column}`: where the loader stores it |
| `missing_values`, `unknown_values`, `value_map` | how the file writes "no value", "unknown" and values of its own, from its mapping config. Fixes for known mock-data bugs, such as the cut-off race labels, are in `config/data_fixes.yaml` and aren't in `value_map`. |

`kind: "normalized"`: a column of a model table.

| Field | Meaning |
|---|---|
| `table`, `column` | |
| `description` | its source column's description when every source agrees. Otherwise null: read `sources[]`. |
| `model_type`, `nullable`, `primary_key`, `foreign_key`, `unique_group`, `default_value`, `unknown_value` | from `destination_schema.yaml` |
| `allowed_values` | the codes an `enum` or `value_set` rule lists, or null. These come from the schema, not the data. |
| `rules` | the rules as written in the schema, each with its `severity` |
| `sources[]` | `{source_file, source_column, dictionary_name, description}`. Empty for columns the loader makes, such as `term.sort_order`. |

**Example.** `{"column": "gender"}`:

```json
{"query": {"column": "gender", "table": null, "source_file": null},
 "matches": [
  {"kind": "source", "source_file": "pdp_cohort_data.csv", "source_column": "Gender", "dictionary_name": "Gender",
   "description": "Student gender reported to the PDP. ...", "dictionary_file": "data/dictionaries/arf_cohort_data_dictionary.md",
   "destinations": [{"table": "student", "column": "gender"}], "missing_values": [], "unknown_values": ["UK"], "value_map": {}},
  {"kind": "source", "source_file": "pdp_course_data.csv", "source_column": "Gender", "...": "..."},
  {"kind": "normalized", "table": "student", "column": "gender", "description": "Student gender reported to the PDP. ...",
   "model_type": "str", "nullable": true, "primary_key": false, "foreign_key": null, "unique_group": null,
   "default_value": null, "unknown_value": "UNKNOWN", "allowed_values": ["M", "F", "P", "X"],
   "rules": [{"enum": ["M", "F", "P", "X"], "severity": "error"}],
   "sources": [{"source_file": "pdp_cohort_data.csv", "source_column": "Gender", "dictionary_name": "Gender", "description": "..."},
               {"source_file": "pdp_course_data.csv", "source_column": "Gender", "dictionary_name": "Gender", "description": "..."}]}
 ]}
```

**Errors.** `not_found`, with `details.suggestions`, when nothing matches. It's never an empty
`matches`, and never a made-up definition.

**Not included yet.** Field classifications and the meaning of each code (`C` = college ready)
wait on the data dictionary workstream (#28). `dictionary_file` and `dictionary_name` say where to
read the code meanings today.

---

## `get_database_info`

**Purpose.** Check what the server exposes and whether its sources are healthy. Call it first when
something fails.

**Input.** None: `{}`.

**Output.** `DatabaseInfoResult`:

| Field | Meaning |
|---|---|
| `access_mode` | `definitions` |
| `capabilities` | the tools registered for the mode |
| `read_only` | always `true` |
| `metadata` | `{healthy, error, files: [{path, sha256}], table_count}`: the repo files the tools read, each with its SHA-256, so two consumers (MCP and chat, say) can confirm they read the same definitions. The server reads them once, on first use: the checksums are of the bytes its answers come from, until it restarts |
| `database` | null unless `PDP_MCP_BACKEND` is set. Then: `{engine, healthy, error, server_version, database, database_schema, model_tables: {expected, missing}, table_count, view_count}`. It only reports whether the database is reachable and loaded. No tool reads it. |
| `warnings` | for example, a configured database missing model tables, or a PostgreSQL role that is a superuser or can write |

`database.database` is the SQLite file's name or the PostgreSQL database's name: never a path,
host, user or password.

**Example**, with no database configured (two of the nine files shown):

```json
{"access_mode": "definitions",
 "capabilities": ["list_tables", "describe_table", "get_column_definition", "get_database_info"],
 "read_only": true,
 "metadata": {"healthy": true, "error": null, "table_count": 10, "files": [
   {"path": "normalized-data-model/config/destination_schema.yaml", "sha256": "5bce2c840b0bb75573ca9987e03287f270d926f2a7ad4edec304d3cf61815a17"},
   {"path": "normalized-data-model/config/value_sets.yaml", "sha256": "8ebfbe957bc5ab69741abef7ec516a9479a2886a860e4ad6d79b91714fa25b4e"}]},
 "database": null, "warnings": []}
```

With `PDP_MCP_BACKEND=sqlite` and a loaded database, `database` is:

```json
{"engine": "sqlite", "healthy": true, "error": null, "server_version": "3.51.2", "database": "pdp.sqlite",
 "database_schema": "main", "model_tables": {"expected": ["cohort_membership", "course", "...", "term"], "missing": []},
 "table_count": 10, "view_count": 0}
```

**Errors.** None of its own. An unreadable metadata file shows as `metadata.healthy: false`, and an
unreachable database as `database.healthy: false`, each with the reason in `error`.

---

## Dormant: `execute_query`

`execute_query` is **not registered in any access mode**, so a client can't list or call it. Its
implementation (`Tools.execute_query`, with the SQLite and PostgreSQL read-only safeguards in
`db.py` and `query.py`) is kept and tested in Python, for a later student-level access decision.
Exposing it would need that decision, a new access mode, and a contract change announced to every
workstream.

As built and tested, it takes `sql` (one `SELECT`, `WITH`, `VALUES` or `EXPLAIN` statement), optional
`params` (positional, `?` in SQLite and `%s` in PostgreSQL) and optional `max_rows`. It returns
`ExecuteQueryResult`: `columns`, `rows` as arrays, `row_count`, `truncated`, `max_rows` and
`elapsed_ms`. Its errors are `query_rejected`, `query_failed`, `timeout`, `invalid_argument` and
`database_unavailable`.

---

## Breaking changes from the proposed five-tool contract

The five-tool contract was posted on #11 as proposed. It was replaced before anyone integrated
it, to meet the Query Layer's access rules: definitions-only by default, no data-query tools, and
no student-level values.

| Change | Why | Who it affects |
|---|---|---|
| `execute_query` is no longer listed or callable | Definitions-only mode exposes no data-query tools. Student-level access waits on a policy decision. | Chat (#30) can't run SQL through MCP. Anyone who planned to. |
| `list_tables`: `engine` and `database_schema` replaced by `source`. Only the model's tables are listed, never views or squads' own tables. | The tools read the model's schema, not a database | Chat (#30), metadata assistant (#20) |
| `describe_table`: `columns[].data_type` is now nullable, and null in definitions mode | No database is read, and engine types aren't in the schema. Use `model_type`. | Chat (#30), dictionary UI (#28) |
| `get_database_info`: new `access_mode`, `capabilities` and `metadata`. The database fields moved under `database`, which is null without one. `param_style` and `limits` removed. | It now reports what the server exposes. The removed fields only applied to `execute_query`. | Anyone reading those fields |
| The server needs no database to start; a missing or unreachable configured database no longer stops it | The tools don't read one | Setup docs |
| `tools.json` has a new top-level `access_mode` field | The published list is the definitions mode's | Anyone reading the file |

`get_column_definition` is unchanged.

## Changing a contract

1. Change `contracts.py`, or a tool's arguments or registration in `server.py`.
2. Run `python -m pdp_mcp.export_schemas` from `mcp/`, and update this file.
3. In the pull request, say what changed, why, and which workstreams call that tool.

Adding a field to an output is safe for callers that ignore unknown fields. Renaming or removing a
field, or adding a required argument, breaks them.
