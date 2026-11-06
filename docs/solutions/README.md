# Shared learnings

This is the shared learnings folder. When your squad solves something another squad is likely to
hit, write it down here once, so every squad and every AI tool can find it.

## What belongs here

Add an entry when another squad would probably run into the same thing. For example:

- A fix for something broken: a setup error, a confusing data quirk, a failing check.
- Something learned: a better way to query the data, a tool setting that saved time, a convention
  you agreed on.

Leave out anything only your squad will ever need, and anything already in the README or
`AGENTS.md`.

## How to add an entry

1. Copy [docs/solutions-template.md](../solutions-template.md). It sits outside this folder so
   searches of `docs/solutions/` don't pick it up as an entry.
2. Fill in the fields at the top and the sections. Delete the optional ones you don't need.
3. Save it in the subfolder for its type (below), named `YYYY-MM-DD-short-title.md`, for example
   `best-practices/2026-10-28-join-cohort-and-course-files.md`.
4. Commit it in the pull request for the work it came from, or in its own small pull request.

You can also ask any AI tool to write the entry for you: "Add a learning to `docs/solutions/`
using `docs/solutions-template.md`." With Compound Engineering, run `ce-compound`, which writes
here by default using the same fields.

## Where to save it

Use the subfolder for the entry's `problem_type`. If unsure, use `best-practices/`.

| `problem_type` | Subfolder |
| --- | --- |
| `best_practice` (default for something learned) | `best-practices/` |
| `workflow_issue` | `workflow-issues/` |
| `developer_experience` | `developer-experience/` |
| `documentation_gap` | `documentation-gaps/` |
| `convention` | `conventions/` |
| `tooling_decision` | `tooling-decisions/` |
| `architecture_pattern` | `architecture-patterns/` |
| `design_pattern` | `design-patterns/` |
| `build_error` | `build-errors/` |
| `test_failure` | `test-failures/` |
| `runtime_error` | `runtime-errors/` |
| `logic_error` | `logic-errors/` |
| `database_issue` | `database-issues/` |
| `integration_issue` | `integration-issues/` |
| `performance_issue` | `performance-issues/` |
| `security_issue` | `security-issues/` |
| `ui_bug` | `ui-bugs/` |

Create the subfolder if it doesn't exist yet. These names match Compound Engineering's defaults,
so hand-written and `ce-compound` entries end up side by side.

## Fields

Every entry starts with the same fields Compound Engineering uses, so its planning skills read
hand-written entries too:

- **Always:** `title`, `date`, `category`, `module`, `problem_type`, `component`, `severity`,
  `tags`.
- **Only for a fix to something broken** (the bug types in the table above): `symptoms`,
  `root_cause`, `resolution_type`.
- **Tag style:** lowercase and hyphenated. Always include your squad, such as `squad-gia`.
