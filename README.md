# PDP Datathon Starter

Shared data and reusable foundations for the 2026 /dev/color datathon. Everything built here is
cloned by all six squads, so it should be something several squads would use.

## Dates

| When | What |
| --- | --- |
| Now | Proposals open |
| **Oct 21** | Proposals close |
| **Oct 22** | Leads decide fund / no fund. If hours are left over, a few more proposals may be let in. |
| **Oct 24 – Oct 31** | Funded work is built, unless Leads greenlight an earlier start. |

## Raw data

Mock data from [Achieving the Dream](https://achievingthedream.org/). These are synthetic student
records in the shape of the Postsecondary Data Partnership (PDP) analysis-ready files (ARF). No real
students are in it, and nothing built on it is a finding about real students or a real institution.

| File | Rows | Columns | What it is |
| --- | ---: | ---: | --- |
| [pdp_cohort_data.csv](data/raw/pdp_cohort_data.csv) | 10,313 | 85 | One row per student. Dictionary: [cohort](data/dictionaries/arf_cohort_data_dictionary.md) |
| [pdp_course_data.csv](data/raw/pdp_course_data.csv) | 100,951 | 35 | One row per student per course per term. Dictionary: [course](data/dictionaries/arf_course_data_dictionary.md) |

What we know so far:

- No institution column, so treat it as one institution's extract.
- The third ARF file, financial aid, is not included. Its [dictionary](data/dictionaries/arf_financial_aid_data_dictionary.md) is here for reference.
- Expect blanks in optional-to-report columns (demographics, placement, gateway status, GPA,
  first-gen). That is realistic, not a bug.
- Known quirks: 2 students appear twice in the cohort file (each in two cohorts), course years run
  from 2012-13 to 2026-27 while cohorts are 2021-22 to 2024-25, and `researchid` has one value per
  file (`cohort2026atd` or `course2026atd`). Full list in the [pdp-data skill](.agents/skills/pdp-data/SKILL.md#known-data-facts).

### Understand the columns

The CSV column names are shortened, and many don't match the data dictionaries.
[column_lookup.csv](data/dictionaries/column_lookup.csv) maps every column in both files to its
dictionary name and description (`file, column_in_csv, dictionary_name, description`). It is a plain
CSV, so any language or tool can use it.

For AI tools, the **pdp-data** skill explains a column, profiles a file, or answers a data
question using the lookup table:

- **Claude Code:** found automatically (`.claude/skills/pdp-data/`). Ask "What does
  `S_First_Associates_or_Cert` mean?"
- **Other tools:** point your agent at [.agents/skills/pdp-data/SKILL.md](.agents/skills/pdp-data/SKILL.md)
  if it doesn't load skills from `.agents/skills/` on its own.

## dev/color Playground

[playground/](playground/README.md) is a starter app: a Next.js client and a FastAPI server that
talk to each other locally out of the box, with charts and an extendable sandbox where crews add
their own examples. Its Workbench loads PDP files into the data model and lets you look through
them, with a field guide to every column. Crews choose the database: SQLite or PostgreSQL.

You need [mise](https://mise.jdx.dev) and [bun](https://bun.sh). For PostgreSQL you also need
Docker (or OrbStack); SQLite needs no Docker.

```bash
cd playground
mise trust && mise install
mise run db:choose sqlite   #OR   mise run db:choose postgresql
```

Then follow [playground/README.md](playground/README.md) to start the server and the client.

Storybook's MCP server helps AI agents discover documented components, follow story-writing
instructions, and run story tests while Storybook is running.

- **Claude Code:** the client's [`CLAUDE.md`](playground/client_application/CLAUDE.md) imports its
  local agent instructions.
- **Other tools:** read [the client agent instructions](playground/client_application/AGENTS.md).

For an AI-built institution feature developed in Sandbox, use the normalized data model and
[pdp-sandbox](.agents/skills/pdp-sandbox/SKILL.md) to build the typed endpoint and chart.
Use [pdp-data](.agents/skills/pdp-data/SKILL.md) when an original ARF field or dictionary term
needs interpretation.

## Checks

Use this table to pick what to run. Commands run from the repository root unless they start with `cd`.

| You changed | While you work | Before you open a pull request |
| --- | --- | --- |
| Data, or a foundation | `make check-fast` | `make check` |
| [`playground/`](playground/README.md) | `cd playground && mise run api:test-sqlite` | `make check`, then the Playground's commands below |

`make check` doesn't run the Playground's tests, and the Playground's commands don't run the
foundations'. CI runs both on every pull request. It runs these for the Playground:

```bash
cd playground
mise run api:lint
mise run api:test-sqlite
mise run web:install
mise run web:build   # first: it generates the Next.js types the type check needs
mise run web:lint
```

The `make` commands need the [Python packages](#python-packages) installed first:

| Command | What it runs | How long |
| --- | --- | --- |
| `make check-fast` | The data check, and every foundation test not marked `slow` | About a minute |
| `make check` | The data check, and every foundation test | A few minutes |
| `make check-slow` | The data check, and only the tests marked `slow` | A few minutes |

CI runs `make check-fast` on one machine and `make check-slow` on another, so together they cover
`make check`.

- **Narrow a run:** `make check-fast PYTEST_ARGS='-k gateway'`. `PYTEST_ARGS` is passed to pytest
  on all three commands. A run where nothing matches still passes, so read the last line: it says
  `no tests ran`.
- **Use fewer workers:** `make check PYTEST_WORKERS=2`. The default is 4. A full-data test uses
  about 0.7 GB of memory.
- **PostgreSQL:** without a database, the data model's PostgreSQL tests skip, locally only. To run
  them, see [its README](normalized-data-model/README.md#run-everything-locally-postgresql-included).

| What you see | What it means | What to do |
| --- | --- | --- |
| `Python packages are missing or out of date` | The packages aren't installed, or `requirements.txt` has changed | [Install them](#python-packages) |

On Windows, or anywhere without `make`, run the same commands. Add `-m "not slow"` for the fast
check, and `-n 4` to run on four workers, as `make` does:

```bash
python scripts/check.py
python data/quality/run_checks.py
cd normalized-data-model && python -m pytest -q
```

`python scripts/check.py` alone needs nothing installed, so the data check works on a fresh clone.

- **Data:** each CSV in `data/raw/` must match its entry in [data/manifest.json](data/manifest.json):
  checksum, row count, column count, and exact column names. Changing even one cell fails, and so
  does a new or renamed column.
- **README:** the Rows and Columns in the table above must match the manifest.
- **Links:** CI also checks that every link to a file in this repo works, in every Markdown file.
  Links to outside websites are not checked, so a slow or offline site can't block a merge.

GitHub runs all of this on every pull request, and it must pass before merging to `main`.

**Changing the data on purpose:** run `python scripts/check.py --update`, update the table above,
and commit both in the same pull request, so the Reviewer sees the change.

### Add a project's tests

For a Python project, once it has a real test to run:

1. Add a line under `check:` in the [Makefile](Makefile): `cd your-project && $(PYTEST)`. That gives
   it the workers and the markers, and CI then runs it on every pull request.
2. Put its packages in [requirements.txt](requirements.txt).
3. Mark any test that takes more than a few seconds with `@pytest.mark.slow`, and register the
   marker in the project's `conftest.py`, as
   [the data model's](normalized-data-model/conftest.py) does. A project with no slow tests is fine.

A project that isn't Python gets its own CI job in
[.github/workflows/check.yml](.github/workflows/check.yml), as the Playground has, and a row in the
first table above.

### Python packages

Foundations target Python 3.10 or newer. Shared packages go in
[requirements.txt](requirements.txt), pinned to exact versions. Install them in a virtual
environment before running `make check`:

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
```

Without them, `make check` stops and tells you to install them. Install again whenever
`requirements.txt` changes.

## Foundations

| Foundation | What it is |
| --- | --- |
| [Normalized data model](normalized-data-model/README.md) | Proposal #8. The tables every squad can build on, where every Analysis-Ready File column goes, what a valid value is, how enrichment files feed in, samples for 10 students, a validator, and a loader into SQLite or PostgreSQL ([Load the data](normalized-data-model/README.md#load-the-data)). |
| [Mock data quality](data/quality/README.md) | Proposal #12. The log of known data issues with counts, impact and proposed fixes, one command that reproduces every count, and a notebook that shows each issue. |
| [PDP MCP server](mcp/README.md) | Proposal #11, part of the Query Layer. A local, read-only MCP server for AI coding assistants (checked with Claude Code). In its default definitions mode, four tools describe the normalized model's tables, keys and column definitions from the repo's files: no database needed, no data-query tools, no student-level values. Aggregate measures wait on #9. |
| [Equity gap finder](gap_finder/README.md) | Proposal #26. Ranks each group's gap from everyone else on a measure, such as retention by race, and flags the gaps that are likely noise. Saved as an `equity_gaps` SQLite table and a CSV. A stub for now: hand-written rows from the synthetic mock data, in the final columns, so consumers can build against them. |
| [Metadata Advisor Skill](.agents/skills/metadata-advisor/SKILL.md) | A private AI advisor skill that guides university staff on what data to explore without touching student information. It suggests measures, breakdowns, small-group cautions ($n < 10$), and how to link outside data (holds, degree audit near-completers, caregivers) using MCP definitions. |

## Recommended AI workflows

Squads use different AI coding tools. Two maintained, MIT-licensed skill sets work in most of them.
Install them from their own repos, so they stay current; nothing is copied into this repo.

Checked on 2026-10-30: Compound Engineering `v3.33.2`, Matt Pocock's skills `v1.3.1`.

### Install

| Tool | [Compound Engineering](https://github.com/EveryInc/compound-engineering-plugin) | [Matt Pocock's skills](https://github.com/mattpocock/skills) |
| --- | --- | --- |
| Claude Code | `claude plugin marketplace add EveryInc/compound-engineering-plugin`, then `claude plugin install compound-engineering@compound-engineering-plugin` | `claude plugin install mattpocock-skills@claude-plugins-official` |
| Cursor | In Agent chat: `/add-plugin compound-engineering` | `npx skills@latest add mattpocock/skills -a cursor` |
| Codex CLI | `codex plugin marketplace add EveryInc/compound-engineering-plugin`, then `codex plugin add compound-engineering@compound-engineering-plugin` | `codex plugin marketplace add mattpocock/skills`, then `codex plugin add mattpocock-skills@mattpocock` |
| Anything else | [More install options](https://github.com/EveryInc/compound-engineering-plugin#more-install-options) (Copilot, OpenCode, Cline, and more) | [Installation](https://github.com/mattpocock/skills#installation-30-second-setup) (Copilot, Gemini CLI, or `npx skills@latest add mattpocock/skills`) |

Skills only appear in a session started after the install, so open a new one. Each set's repo
setup (`/ce-setup`, `/setup-matt-pocock-skills`) is already done and committed, under
`docs/agents/`, so there is nothing to run. In Codex, skills start with `$` instead of `/`.

### Which skill when

Install both sets, then use one skill per phase:

| Phase | Skill | From |
| --- | --- | --- |
| Sharpen an idea | `/grill-with-docs` | Matt Pocock's |
| Plan | `ce-plan`, given an issue link, a file, or the conversation. It writes to `docs/plans/`. Don't commit the plan before Build: `ce-work` won't open a PR on a branch that already has commits of yours. Once it opens the PR, commit the plan to that branch and push. | Compound Engineering |
| Build | `ce-work docs/plans/<file>` (it also simplifies, reviews, and opens the PR) | Compound Engineering |
| Debug | `ce-debug` | Compound Engineering |
| Review | `ce-code-review`, for changes made outside `ce-work` | Compound Engineering |
| Open a PR / fix CI | `ce-commit-push-pr`, then `ce-babysit-pr` to watch CI, for changes made outside `ce-work` | Compound Engineering |
| Capture lessons | `ce-compound` (writes to `docs/solutions/`) | Compound Engineering |
| Hand off | `ce-handoff` | Compound Engineering |

Run Sharpen and Plan in the same session, so `ce-plan` has the conversation to work from. If you
can't, `/to-spec` saves the idea as an issue to give `ce-plan` later. `ce-work` reads a plan file or
a prompt, never an issue, so always hand it the plan. None of this needs an issue tracker.

**Same job, two skills.** Both sets have their own review, debug, and handoff skills (for example
`code-review` and `ce-code-review`), and some start on their own when a task matches. `AGENTS.md`
tells agents to use the skill in this table. If you'd rather install only one set: Compound
Engineering alone covers every phase (`ce-brainstorm`, `ce-plan` for the first two). Matt Pocock's
alone has `implement`, `diagnosing-bugs`, `code-review`, `pr`, and `handoff`, but no skill that
writes down lessons.

**Shared learnings** go in [docs/solutions/](docs/solutions/README.md): when your squad solves
something another squad is likely to hit, write it down there once, by hand from the template or
with `ce-compound`.

**Repo rules for agents** are in [AGENTS.md](AGENTS.md), which most AI coding tools read
automatically. Claude Code reads it through [CLAUDE.md](CLAUDE.md).

### Matt Pocock's skills during team work

Some moments call for one of Matt Pocock's skills instead:

| When | Skill |
| --- | --- |
| A backlog of loosely written issues | `/triage` |
| Words or concepts in the data keep getting confused | `domain-modeling` |
| Logic is risky and you want tests first | `tdd` |
| The code is getting tangled | `/improve-codebase-architecture` |
| Stuck on a decision only a mentor or data owner can answer | `/to-questionnaire` |
| Someone hits an unfamiliar concept | `/teach` |
| End of day | `/retro` (alongside `ce-compound`) |

## Submit a proposal

Every proposal has a **DRI** and a **Reviewer** from different squads. The DRI drives it; the
Reviewer gives feedback and tests the result. Don't DRI more than two.

1. **DRI:** [Open a proposal](https://github.com/devcolor/pdp-datathon-starter/issues/new?template=foundation-proposal.md).
   What, why, and total engineering hours. One hour max to write and revise it, including
   integrating feedback.
2. **Everyone:** 👍 the issue if you'd use it. Add your squad's label (`squad:aascu` …
   `squad:uncf`) if your squad would use it. Comment with feedback. One hour max per fellow
   across all proposals.
3. **DRI:** Finalize and comment **Ready for decision**.
4. **Leads** (the six squad leads, Shannon, and Dena): comment **Fund** or **No fund** with a
   short reason and the approved hours. Unfunded proposals stay open with the reason, so the
   thinking isn't lost.

## Deliver funded work

See [Contributing](CONTRIBUTING.md) for how to open a pull request, what the Reviewer checks, and
what to do if the work grows past what was approved.
