# PDP MCP server: local UAT guide

A manual acceptance test of the MCP server in its default `definitions` access mode, for someone who
didn't build it. It checks that a participant can set it up from a fresh clone, that the four
metadata tools work, and that nothing exposes student data.

**The data is synthetic.** Nothing in these tests is a finding about real students or institutions.

- **Time:** about 45 minutes, plus about 15 for each AI client you check.
- **Platform:** the commands are for macOS or Linux, in bash or zsh. Windows isn't covered: if you
  test on Windows, record what you ran in the [results](#results).
- **What "pass" means:** the actual result matches the expected result exactly where a value is
  given, such as a tool list, an exit code or an error code. Message wording can differ slightly.
- Record each result in the [results table](#results) as you go, and any defect in the
  [defect log](#defects).

**Changed since the first UAT round.** The server now runs on the current data model on `main`,
which added a tenth table (`load_run`), a foreign key over two columns, and a separate file for
mock-data fixes. These expected results changed; nothing else did:
- **UAT-06:** `metadata.table_count` is `10` (it was `9`).
- **UAT-07 and UAT-17:** 10 tables, with `load_run` (it was 9).
- **UAT-09:** 80 columns (it was 79), and `referenced_by` now lists `course_enrollment` on
  `student_id` and `cohort` together.
- **UAT-14:** `value_map` is `{}`. The race-label fix moved to `config/data_fixes.yaml`.

## Before you start

You need:
- `git`
- Python 3.10 or newer (`python3 --version`)
- optionally, an MCP client to test: Claude Code, VS Code with GitHub Copilot, or Cursor

Don't reuse a working copy someone developed in: start from a fresh clone (UAT-01).

### The `mcp_call` helper

Most tests call the server the way a client does: they start it over stdio, send one MCP request,
and print the answer. After UAT-01, paste this into your terminal from the repository root. It
defines a shell function for the session and doesn't change any file.

```bash
mcp_call() {
  .venv/bin/python - "$@" <<'EOF'
import json, os, sys
import anyio
from mcp import Client
from mcp.client.stdio import StdioServerParameters

async def main(tool, arguments):
    server = StdioServerParameters(command=sys.executable, args=["mcp/run_server.py"], env=dict(os.environ))
    async with Client(server) as client:
        if tool == "--list":
            print(json.dumps(sorted(t.name for t in (await client.list_tools()).tools)))
            return
        result = await client.call_tool(tool, json.loads(arguments))
        print(json.dumps({"isError": result.is_error, "structuredContent": result.structured_content,
                          "text": result.content[0].text if result.content else None}, indent=2))

anyio.run(main, sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "{}")
EOF
}
```

Usage:
- `mcp_call --list` prints the tools the server lists.
- `mcp_call <tool> '<JSON arguments>'` calls one tool and prints `isError`, `structuredContent`
  and the text content.

Each call starts a fresh server, so a setting on the same line applies to that call only, such as
`PDP_MCP_BACKEND=sqlite mcp_call get_database_info`. The server's own log lines may also appear on
the terminal (for example `Tool 'execute_query' failed`). That's stderr, and it's expected.

---

## 1. Environment setup

### UAT-01: Set up from a fresh clone

**Purpose:** a participant can install everything with the repository's usual steps.

**Steps:**

```bash
git clone https://github.com/devcolor/pdp-datathon-starter.git pdp-uat
cd pdp-uat
git switch mcp/server              # or the branch or pull request under test
python3 --version
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -c "import mcp, yaml; print('ok')"
```

**Expected:** Python is 3.10 or newer. The install finishes without errors. The last command prints
`ok`.

**Pass if:** all of the above. **Fail if:** the install fails, or the import fails.

### UAT-02: No database is present

**Purpose:** the test starts with no loaded database, as a new participant has.

**Steps:**

```bash
ls normalized-data-model/output
```

**Expected:** `No such file or directory`. (If it exists, you loaded data earlier: use a fresh
clone, or move the folder aside for the duration of the test.)

**Pass if:** there's no `normalized-data-model/output/` folder.

---

## 2. Startup without a database

### UAT-03: The server starts with no database and no settings

**Purpose:** definitions mode needs no database and no configuration.

**Steps:**

```bash
env | grep PDP_MCP_                # should print nothing
.venv/bin/python mcp/run_server.py < /dev/null
echo "exit=$?"
```

**Expected:** no `PDP_MCP_` variables are set. The server prints nothing, and `exit=0`.

**Pass if:** exit code 0 with no error output. **Fail if:** any `pdp-mcp: can't start` message.

### UAT-04: The server starts from any directory

**Purpose:** clients start the server from their own working directory.

**Steps:**

```bash
REPO=$(pwd)
(cd / && "$REPO/.venv/bin/python" "$REPO/mcp/run_server.py" < /dev/null; echo "exit=$?")
```

**Expected:** `exit=0`, nothing else.

**Pass if:** exit code 0.

---

## 3. Tool discovery

Paste the [`mcp_call` helper](#the-mcp_call-helper) now.

### UAT-05: Exactly four tools are listed

**Purpose:** the server exposes only the definitions-mode tools.

**Steps:**

```bash
mcp_call --list
```

**Expected:**

```json
["describe_table", "get_column_definition", "get_database_info", "list_tables"]
```

**Pass if:** exactly these four names. **Fail if:** any other tool, especially `execute_query`, is
listed.

### UAT-06: The server reports its access mode and health

**Purpose:** `get_database_info` says what the server exposes, without a database or credentials.

**Steps:**

```bash
mcp_call get_database_info
```

**Expected** in `structuredContent`:
- `access_mode` is `"definitions"`
- `capabilities` lists the same four tools
- `read_only` is `true`
- `metadata.healthy` is `true`, `metadata.table_count` is `10`, and `metadata.files` lists 9 files,
  each with a 64-character `sha256`
- `database` is `null`, and `warnings` is `[]`

**Pass if:** all of the above, and no path outside the repository, password or URL appears anywhere
in the output.

---

## 4. Schema and table discovery

### UAT-07: List the model's tables

**Steps:**

```bash
mcp_call list_tables
```

**Expected:** `isError` is `false`. `source` is
`normalized-data-model/config/destination_schema.yaml`. `tables` holds exactly these 10 names, in
this order: `cohort_membership`, `course`, `course_enrollment`, `data_provider`, `institution`,
`institution_event`, `load_run`, `student`, `student_attribute`, `term`. Each has `"type": "table"`,
`"in_model": true` and a one-line `description`.

**Pass if:** the 10 tables, each with a description.

### UAT-08: Describe a table and its relationships

**Steps:**

```bash
mcp_call describe_table '{"table": "student"}'
```

**Expected:**
- `primary_key` is `["student_id"]`
- `foreign_keys` has one entry: `institution_id` → `institution.institution_id`
- `referenced_by` lists `cohort_membership`, `course_enrollment` and `student_attribute`, each on
  `student_id`
- every column has `"data_type": null` and a `model_type` such as `"str"`

**Pass if:** all of the above. `data_type` must be null: no database is read.

### UAT-09: A composite key, and a case-insensitive name

**Steps:**

```bash
mcp_call describe_table '{"table": "COHORT_MEMBERSHIP"}'
```

**Expected:** `name` is `"cohort_membership"`. `primary_key` is `["student_id", "cohort"]`.
`foreign_keys` point at `student.student_id` and `data_provider.provider_id`. There are 80 columns.
`referenced_by` has one entry: `course_enrollment`, with `columns` and `references_columns` both
`["student_id", "cohort"]`.

**Pass if:** the lowercase name, the two-column key, and the two-column reference.

### UAT-10: Unique groups

**Steps:**

```bash
mcp_call describe_table '{"table": "term"}'
```

**Expected:** `unique_constraints` is `[["academic_year", "academic_term"]]`, and `referenced_by`
lists `course_enrollment` and `student_attribute`.

**Pass if:** both.

---

## 5. Column definitions and dictionary lookups

### UAT-11: A raw column and its table column

**Steps:**

```bash
mcp_call get_column_definition '{"column": "Retention"}'
```

**Expected:** two `matches`:
1. `"kind": "source"`, `source_file` `pdp_cohort_data.csv`, `source_column` `Retention`,
   `description` starting "Retention is defined as either continued enrollment...",
   `dictionary_file` `data/dictionaries/arf_cohort_data_dictionary.md`, and `destinations`
   `[{"table": "cohort_membership", "column": "retention"}]`
2. `"kind": "normalized"`, `table` `cohort_membership`, `column` `retention`, `model_type` `bool`,
   with the same description

**Pass if:** both matches, and the description matches the `Retention` row of
`data/dictionaries/column_lookup.csv`.

### UAT-12: Look up by dictionary name

**Steps:**

```bash
mcp_call get_column_definition '{"column": "Student ID"}'
```

**Expected:** two source matches, both `Student_GUID`: one from `pdp_cohort_data.csv`, one from
`pdp_course_data.csv`.

**Pass if:** both.

### UAT-13: Allowed codes and unknown values

**Steps:**

```bash
mcp_call get_column_definition '{"column": "student.gender"}'
```

**Expected:** one `"kind": "normalized"` match, with `allowed_values` `["M", "F", "P", "X"]`,
`unknown_value` `"UNKNOWN"`, and `sources` from both the cohort and the course file.

**Pass if:** all three.

### UAT-14: A file's own values, and filtering by file

**Steps:**

```bash
mcp_call get_column_definition '{"column": "Race", "source_file": "pdp_cohort_data.csv"}'
```

**Expected:** exactly one match, the cohort file's `Race`, with `unknown_values` `["Unknown"]` and
`value_map` `{}`. The mock data's cut-off race labels, such as `American Indian or Alaska`, are
fixed by `config/data_fixes.yaml`, not by the mapping, so `value_map` doesn't list them.

**Pass if:** one match, from the cohort file only.

### UAT-15: Nothing is made up

**Purpose:** a column with no dictionary entry has no invented description.

**Steps:**

```bash
mcp_call get_column_definition '{"column": "Uses_On_Campus_Housing"}'
mcp_call get_column_definition '{"column": "sort_order", "table": "term"}'
```

**Expected:**
- **First call:** `source_file` is `on_campus_housing.csv`, `description` is `null`, and the
  destination is `student_attribute.attribute_value`.
- **Second call:** one normalized match, with `sources` `[]` and `description` `null`.

**Pass if:** both descriptions are `null`. **Fail if:** any text was filled in.

---

## 6. Invalid tool arguments

### UAT-16: Arguments that break the input schema

**Steps:**

```bash
mcp_call describe_table '{}'
mcp_call describe_table '{"table": ""}'
mcp_call get_column_definition '{"column": 5}'
```

**Expected:** each returns `"isError": true`, `"structuredContent": null`, and a text message from
the MCP SDK:
- the first starts `Error executing tool describe_table` and says `Field required`
- the second says `String should have at least 1 character`
- the third says `Input should be a valid string`

**Pass if:** all three are errors that name the bad argument. The server keeps working: the next
call succeeds.

### UAT-17: An extra argument changes nothing

**Purpose:** no argument can change what the server exposes.

**Steps:**

```bash
mcp_call list_tables '{"mode": "student", "access_mode": "aggregate"}'
mcp_call get_database_info '{"access_mode": "aggregate"}'
```

**Expected:** the extra arguments are ignored. `list_tables` returns the same 10 tables as UAT-07,
and `get_database_info` still says `"access_mode": "definitions"` with the same four
`capabilities`.

**Pass if:** both. **Fail if:** anything about the mode or tools changes.

---

## 7. Unknown tables and columns

### UAT-18: An unknown table

**Steps:**

```bash
mcp_call describe_table '{"table": "students"}'
```

**Expected:** `"isError": true` and:

```json
{"error": {"code": "not_found", "message": "No table named 'students' in the normalized model.", "details": {"suggestions": ["student"]}}}
```

**Pass if:** code `not_found` with `student` suggested.

### UAT-19: An unknown column

**Steps:**

```bash
mcp_call get_column_definition '{"column": "Studnt_GUID"}'
```

**Expected:** `"isError": true`, code `not_found`, and `details.suggestions` starting with
`Student_GUID`.

**Pass if:** code `not_found` with `Student_GUID` suggested.

---

## 8. Attempted student-data queries

### UAT-20: SQL passed as a table or column name

**Purpose:** SQL in an argument is treated as a name, never run.

**Steps:**

```bash
mcp_call describe_table '{"table": "student; DROP TABLE student"}'
mcp_call get_column_definition '{"column": "SELECT * FROM student"}'
```

**Expected:** both return `"isError": true` with code `not_found`.

**Pass if:** both are `not_found`, and no rows or values appear.

### UAT-21: No tool returns student values

**Purpose:** with real student rows available, the tools still return only definitions.

**Steps:** load the full mock data into SQLite (about 30 seconds; this creates
`normalized-data-model/output/pdp.sqlite`, which git ignores), point the server at it, and call
the tools:

```bash
(cd normalized-data-model && ../.venv/bin/python -m src.loader.load)
export PDP_MCP_BACKEND=sqlite
mcp_call --list
mcp_call get_database_info
mcp_call describe_table '{"table": "student"}'
mcp_call get_column_definition '{"column": "student_id"}'
SAMPLE_ID=$(sed -n 2p normalized-data-model/data/output/sample/student.csv | cut -d, -f1)
mcp_call describe_table '{"table": "student"}' | grep -c "$SAMPLE_ID"
unset PDP_MCP_BACKEND
```

**Expected:**
- The tool list is the same four tools as UAT-05.
- `get_database_info` now shows `database.healthy: true`, `database.engine: "sqlite"`,
  `database.database: "pdp.sqlite"` (a file name, not a path) and `model_tables.missing: []`.
- The `describe_table` and `get_column_definition` results are the same as without a database
  (UAT-08).
- The `grep -c` prints `0`.

**Pass if:** no tool output holds a student ID, grade, course name or other row value, and the tool
list doesn't grow.

---

## 9. `execute_query` is unavailable

### UAT-23: It isn't listed, and can't be called

**Steps:**

```bash
mcp_call --list | grep -c execute_query
mcp_call execute_query '{"sql": "SELECT COUNT(*) FROM student"}'
PDP_MCP_BACKEND=sqlite mcp_call execute_query '{"sql": "SELECT COUNT(*) FROM student"}'
```

**Expected:**
- The `grep -c` prints `0`.
- Both calls return:

  ```json
  {"isError": true, "structuredContent": null, "text": "Unknown tool: execute_query"}
  ```

  The second call does this even though it has a database configured.

**Pass if:** `0`, and both calls return `Unknown tool: execute_query`.

---

## 10. Aggregate mode is rejected

### UAT-24: `aggregate` stops the server with a reason

**Steps:**

```bash
PDP_MCP_ACCESS_MODE=aggregate .venv/bin/python mcp/run_server.py < /dev/null; echo "exit=$?"
```

**Expected:**

```
pdp-mcp: can't start: PDP_MCP_ACCESS_MODE=aggregate isn't available yet: it needs the Measures workstream's (#9) manifest and output contract, which aren't agreed yet. Unset PDP_MCP_ACCESS_MODE, or set it to definitions
exit=2
```

**Pass if:** exit code 2 with that reason. **Fail if:** it starts, or falls back to definitions
mode without saying so.

### UAT-25: Other modes are rejected, and `definitions` can be named

**Steps:**

```bash
for mode in student student_level query all; do
  PDP_MCP_ACCESS_MODE=$mode .venv/bin/python mcp/run_server.py < /dev/null; echo "exit=$?"
done
PDP_MCP_ACCESS_MODE=definitions .venv/bin/python mcp/run_server.py < /dev/null; echo "exit=$?"
```

**Expected:** each of the four prints `pdp-mcp: can't start: PDP_MCP_ACCESS_MODE must be
definitions, not '<mode>'` and `exit=2`. The last prints only `exit=0`.

**Pass if:** four rejections, then a clean start.

---

## 11. Missing metadata and configuration errors

### UAT-26: Configuration errors

**Steps:** run each line and note the output:

```bash
PDP_MCP_BACKEND=mysql .venv/bin/python mcp/run_server.py < /dev/null; echo "exit=$?"
PDP_MCP_BACKEND=postgres .venv/bin/python mcp/run_server.py < /dev/null; echo "exit=$?"
PDP_MCP_LOG_LEVEL=LOUD .venv/bin/python mcp/run_server.py < /dev/null; echo "exit=$?"
```

**Expected,** each with `exit=2`:
- `pdp-mcp: can't start: PDP_MCP_BACKEND must be sqlite or postgres, not 'mysql'`
- `pdp-mcp: can't start: PDP_MCP_BACKEND is postgres, but PDP_MCP_POSTGRES_URL isn't set`
- `pdp-mcp: can't start: PDP_MCP_LOG_LEVEL must be one of DEBUG, INFO, WARNING, ERROR, not 'LOUD'`

**Pass if:** all three stop with exit code 2 and say which setting is wrong.

### UAT-27: Settings that don't stop the server

**Purpose:** settings for the dormant query path, and a configured database that isn't there, don't
block definitions mode.

**Steps:**

```bash
PDP_MCP_MAX_ROWS=lots PDP_MCP_QUERY_TIMEOUT_SECONDS=-1 .venv/bin/python mcp/run_server.py < /dev/null; echo "exit=$?"
PDP_MCP_BACKEND=sqlite PDP_MCP_SQLITE_PATH=/nowhere/pdp.sqlite mcp_call get_database_info
ls /nowhere/pdp.sqlite
PDP_MCP_BACKEND=postgres PDP_MCP_POSTGRES_URL='postgresql://someone:s3cret@127.0.0.1:1/pdp' mcp_call get_database_info | grep -c s3cret
```

**Expected:**
- The first command prints only `exit=0`.
- The second returns `metadata.healthy: true` and `database.healthy: false`, with
  `database.error.code` `"database_unavailable"`, and still the four `capabilities`.
- `ls` says no such file: the server never creates a database.
- The last prints `0`: the password isn't in the output. libpq's own message on stderr may name the
  host, but never the password.

**Pass if:** all four.

### UAT-28: A missing metadata file stops the server

**Purpose:** the server refuses to start without the files its definitions come from.

**Steps:** this temporarily moves one file in your clone. Run all four lines together.

```bash
mv normalized-data-model/config/value_sets.yaml /tmp/value_sets.yaml.uat
.venv/bin/python mcp/run_server.py < /dev/null; echo "exit=$?"
mv /tmp/value_sets.yaml.uat normalized-data-model/config/value_sets.yaml
git status --short normalized-data-model/config
```

**Expected:**
- `pdp-mcp: can't start: can't read normalized-data-model/config/value_sets.yaml` and `exit=2`
- the file is back: `git status` prints nothing for `normalized-data-model/config`

**Pass if:** exit code 2 naming the file, and the file is restored.

---

## 12. Client compatibility

For each client you check, use the config from [Connect a client](../README.md#connect-a-client),
replacing `/absolute/path/to/pdp-datathon-starter` with your clone's path (`pwd`). Only Claude Code
has been checked so far, through `--mcp-config`. Your result for VS Code and Cursor is the first
check.

### UAT-22: Asking an AI client for student data

Do this in each client you check (section 12).

**Steps:** ask:
1. "How many students are in the 2022-23 cohort? Use the pdp tools."
2. "Show me five rows from the student table."
3. "Run `SELECT * FROM student` with the pdp server."

**Expected:** the assistant says the pdp server has no tool to query data or count rows. It may
offer to write SQL for you to run yourself. It doesn't report numbers or rows that came from the
pdp server.

**Pass if:** no student values or counts come from a pdp tool call. Check the client's tool-call log
if it shows one. **Note:** an assistant that invents a number without calling a tool is a model
behavior to record, not a server defect.

### UAT-29: Claude Code

**Steps:**
1. From the repository root, run
   `claude mcp add pdp -- "$PWD/.venv/bin/python" "$PWD/mcp/run_server.py"`.
2. Start `claude` and run `/mcp`.
3. Ask: "List the tools the pdp server gives you."
4. Do UAT-22's three questions.
5. When finished, run `claude mcp remove pdp` if you don't want to keep it.

**Expected:** `/mcp` shows `pdp` connected. The tools are exactly the four. UAT-22 passes.

**Pass if:** connected, four tools, no student data.

### UAT-30: VS Code with GitHub Copilot

**Steps:**
1. Create `.vscode/mcp.json` as in the README.
2. Open it and select **Start** above `pdp`.
3. In Copilot Chat, switch to **Agent** mode and open the tools picker.
4. Ask "Describe the student table using the pdp tools."
5. Do UAT-22's three questions.
6. Delete `.vscode/mcp.json` afterwards, unless your team wants it. Don't commit it with secrets.

**Expected:** the server shows as running. The tools picker shows the four pdp tools.
`describe_table` returns `student_id` as the primary key. UAT-22 passes.

**Pass if:** all of the above. Record your VS Code and Copilot versions.

### UAT-31: Cursor

**Steps:**
1. Create `.cursor/mcp.json` as in the README, with absolute paths.
2. Open **Settings → MCP**, and check `pdp` is enabled and shows 4 tools.
3. In Agent chat, ask "Describe the student table using the pdp tools."
4. Do UAT-22's three questions.

**Expected:** 4 tools. `student_id` is the primary key. UAT-22 passes.

**Pass if:** all of the above. Record your Cursor version.

### UAT-32: Troubleshooting checks

**Purpose:** the README's troubleshooting table leads to a fix.

**Steps:** in one client, break the config on purpose, one at a time, and restore it after each:
1. Point `command` at `python3` instead of `.venv/bin/python`.
2. Add `"env": {"PDP_MCP_ACCESS_MODE": "aggregate"}`.
3. Misspell the path to `run_server.py`.

**Expected:**
- The client shows the server as failed.
- Running the same command in a terminal shows the reason: `No module named 'mcp'` (unless your
  system Python has it), the aggregate message, or `can't open file`.
- The README's troubleshooting table covers each of the first two.

**Pass if:** each failure can be diagnosed from the README. Note any that can't.

---

## Results

Copy this table into your notes or the pull request, and fill it in.

| Field | Value |
|---|---|
| Tester | |
| Date | |
| Branch and commit (`git rev-parse --short HEAD`) | |
| OS and version | |
| Python version | |
| Shell | |

| Test | Result (pass / fail / skipped) | Notes, or the actual result if it differed |
|---|---|---|
| UAT-01 Set up from a fresh clone | | |
| UAT-02 No database is present | | |
| UAT-03 Starts with no database | | |
| UAT-04 Starts from any directory | | |
| UAT-05 Exactly four tools | | |
| UAT-06 Access mode and health | | |
| UAT-07 List tables | | |
| UAT-08 Describe a table | | |
| UAT-09 Composite key, case-insensitive name | | |
| UAT-10 Unique groups | | |
| UAT-11 Raw and table column | | |
| UAT-12 Dictionary name lookup | | |
| UAT-13 Allowed codes and unknowns | | |
| UAT-14 A file's own values, file filter | | |
| UAT-15 Nothing made up | | |
| UAT-16 Invalid arguments | | |
| UAT-17 Extra arguments change nothing | | |
| UAT-18 Unknown table | | |
| UAT-19 Unknown column | | |
| UAT-20 SQL as a name | | |
| UAT-21 No student values with data loaded | | |
| UAT-22 Asking a client for student data | | |
| UAT-23 execute_query unavailable | | |
| UAT-24 Aggregate rejected | | |
| UAT-25 Other modes rejected | | |
| UAT-26 Configuration errors | | |
| UAT-27 Settings that don't stop the server | | |
| UAT-28 Missing metadata | | |
| UAT-29 Claude Code | | |
| UAT-30 VS Code | | |
| UAT-31 Cursor | | |
| UAT-32 Troubleshooting | | |

## Defects

One row per defect. Severity:
- **blocker:** a participant can't set up or use the server, or student data is exposed
- **major:** a tool gives a wrong answer, or a check fails
- **minor:** docs or messages are unclear

| ID | Test | Severity | What happened (steps, actual result) | Expected | Status |
|---|---|---|---|---|---|
| D-01 | | | | | |
