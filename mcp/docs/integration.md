# Using the PDP MCP server from other workstreams

For the chat endpoint (#30), the metadata assistant (#20), the data dictionary (#28) and the shared
measures (#9). The tools and their schemas are in [tool-contracts.md](tool-contracts.md) and
[../schemas/tools.json](../schemas/tools.json). Setup is in [../README.md](../README.md). **The data
is synthetic.**

The Query Layer's goal is to let apps and coding assistants use shared measures and definitions
within agreed access limits. Today the server covers the **definitions** half, in its default
`definitions` access mode: four metadata tools, no data-query tools, no student-level values. The
**aggregate** half (approved measures) waits on #9.

## One source for definitions: a library and the MCP tools on top of it

Everything the four tools return comes from
[`pdp_mcp.metadata.Metadata`](../pdp_mcp/metadata.py). It's plain Python with no MCP and no
database, and it reads the repo's files. Its only dependency is PyYAML. MCP and any other consumer
give the same answers if they call it:

| Tool | Library call | Returns the same dictionaries as |
|---|---|---|
| `list_tables` | `Metadata().tables()` | `ListTablesResult.tables` |
| `describe_table` | `Metadata().describe(table)` | `DescribeTableResult` |
| `get_column_definition` | `Metadata().define(column, table, source_file)` | `ColumnDefinitionResult.matches` |
| `get_database_info` | `Metadata().status()` | `metadata.files` and its error |

`describe` and `define` raise `pdp_mcp.metadata.NotFound`, with `.suggestions`, where the tools
return `not_found`. To validate the dictionaries, use the Pydantic models in
[`pdp_mcp.contracts`](../pdp_mcp/contracts.py).

`metadata.files[].sha256` in `get_database_info`, or `Metadata().status()`, gives each source
file's checksum. Two consumers can compare them to confirm they read the same definitions.

Each `Metadata` reads every file once, together, on first use, and answers from that snapshot. Its
checksums are of those same bytes. If a file changes on disk later, for example after a `git pull`,
a running server keeps its snapshot and its checksums together; restart it, or make a new
`Metadata()`, to pick up the change.

## Chat endpoint (#30)

Either way works. Pick what fits where the chat backend runs.

**Import the library**, if the backend is Python and can see this repository:

```python
import sys
sys.path.insert(0, "/path/to/pdp-datathon-starter/mcp")
from pdp_mcp.metadata import Metadata, NotFound

metadata = Metadata()                      # reads the repo files once
metadata.describe("cohort_membership")     # dict: columns, keys, relationships
metadata.define("retention")               # list of source and normalized definitions
```

This needs PyYAML in the chat backend's environment. The playground server on `main` has its own
`pyproject.toml` (Python 3.14 or newer), so add `pyyaml` there if chat lives in it.

**Or be an MCP client:** start `mcp/run_server.py` as a subprocess and hand the model the tools from
`tools/list`. Each tool's `name`, `description` and `inputSchema` are what a function-calling API
needs. Return `structuredContent` as the tool result.

```python
import os
from mcp import Client
from mcp.client.stdio import StdioServerParameters

# The SDK passes the server only a minimal environment unless you give it one.
params = StdioServerParameters(command=".venv/bin/python", args=["mcp/run_server.py"], env=dict(os.environ))
async with Client(params) as client:
    tools = (await client.list_tools()).tools
    result = await client.call_tool("describe_table", {"table": "student"})
```

Either way:
- The access mode comes from the server's environment. A chat request can't change it, and no tool
  argument can.
- Chat should run in the same mode, with the same tool list, so both surfaces expose the same
  things.
- Chat gets no SQL tool from this server. If chat runs its own queries, that's outside the Query
  Layer's definitions mode and needs its own access decision.
- Check `isError` first, and read `structuredContent`. An error without `structuredContent.error`
  is an argument the SDK rejected: treat it as `invalid_argument`.

**Chat must confirm:** where the backend runs, and whether it imports the library or uses MCP. End-to-end
parity tests between chat and MCP wait on that.

## Metadata assistant (#20)

Definitions mode is built for #20's rule that the assistant never sees student data. The server
registers only the four metadata tools, and none reads a table's rows. That's enforced by which
tools are registered, not by a prompt: `execute_query` doesn't exist for a client in this mode.
`allowed_values` come from the schema's rules, not from the data.

Not provided: #20's proposed column profiles, such as share of blanks and distinct counts. They're
computed from data, so they belong in #20's metadata pack, built where data access is allowed.

**#20 must confirm:** that the four tools, and the library, meet the assistant's needs.

## Data dictionary (#28)

Issue #28 proposes a database-backed `fields` table populated from the data dictionary files,
supporting a context sidebar and field guide.

The MCP server currently exposes metadata from the repo's schema, mapping and dictionary files,
without requiring a database. `get_column_definition` returns, per column:
- `description` and `dictionary_name`, from `column_lookup.csv`
- `allowed_values`, `unknown_value` and the validation `rules`, from the schema
- `sources` and `destinations`, from the mapping configs

These approaches can coexist, provided the underlying definitions remain consistent.

Additional field classifications (such as identifier, demographic or outcome) and code meanings
(such as `C = college ready`) from #28 aren't in the current MCP contract, and adding them is
outside the scope of PR #63. Before MCP is extended to expose them, the workstreams should agree on
the authoritative source, the data format, and how consistency will be kept between consumers.

## Shared measures (#9)

The server computes no measures and has no aggregate mode yet. Setting
`PDP_MCP_ACCESS_MODE=aggregate` stops the server with a message saying it waits on #9.

When #9's contract is agreed, aggregate mode would register measure tools that:
- list the approved measures
- return one measure's published results unchanged: values, statuses, blanks (NULL) and provenance
- check each published file against #9's manifest before opening it
- never recalculate anything

**#9 must provide, before any of it is built:**

| Needed | Why |
|---|---|
| Manifest format: file paths, checksum algorithm (the repo's own `data/manifest.json` uses SHA-256), version | Verify each file before opening it |
| Measure identifiers | Tool inputs, and the list of approved measures |
| Output file format and columns | The result schema |
| Status values and their meanings | Passed through unchanged |
| How provenance is written | Passed through unchanged |
| Which filters or breakdowns a consumer may choose | Tool inputs |
| Where small groups are suppressed, and how a suppressed cell is written | Passed through unchanged; never recomputed here |

A stub built on a fixture can come first, but only once #9 approves its shape.

## If the contract changes

Contract changes are listed in the pull request that makes them, with the tools and workstreams
affected. `tests/test_contracts.py` fails if `schemas/tools.json` and the server differ, so the
published file is always what the server does.
