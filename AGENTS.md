# AGENTS.md

Instructions for AI coding agents working in this repo. People can read it too.

This is the UNCF squad's repo for the 2026 /dev/color datathon: a Student Success Explorer for FMU
and Benedict College, built on the starter's shared data and foundations. See
[README.md](README.md) for the goal and data and [CONTRIBUTING.md](CONTRIBUTING.md) for how
changes get in. Priorities: Core (Explorer), Stretch 1 (insight cards), Stretch 2 (chat agent).
Never push to `main`, and never commit, push, or open a pull request without the user's explicit
yes. Keep per-school differences in config, not forks.

**New code goes in `uncf` folders.** Don't edit the starter's Sandbox examples or shared
foundations to build our features. Copy their pattern into our own folders instead:
- Python (definitions, precompute, response models, API router): the top-level `uncf/` folder.
  Mount its router in the Playground server with one line.
- Client pages: `playground/client_application/src/app/(app)/uncf/`
- Client components: `playground/client_application/src/components/uncf/`

This keeps upstream fixes easy to merge and our changes easy to review. If a shared file must
change, say so in the pull request.

## Before prompting

- **Plan first.** For anything bigger than a small fix, use a planning skill before writing code.
  See "Recommended AI workflows" in the README.
- **Run steps in parallel when you can.** For each step, ask whether it really needs the previous
  step's result. If it doesn't, run it in parallel.
- **Start simple.** Build the plain version first. Split work up only after you see where it's
  slow.

## While building

- **Define the check first.** Before building, write down how you'll know it works: a command, a
  test, or an expected number.
- **Every feature gets tests.** Add a pytest test with each feature, in a `tests/` folder next to
  the code (for `uncf/`, `uncf/tests/`). A pull request without tests for its new behavior isn't done.
- **Cap every retry loop.** Give each fix-and-retry loop a maximum number of tries (3 is a good
  default). At the cap, stop and ask a person. Don't keep trying.
- **Use the README's skill for each phase.** When two installed skills do the same job (for
  example `code-review` and `ce-code-review`), use the one in the README's "Which skill when"
  table.
- **Run the checks.** Use `make check-fast` while you work and `make check` before opening a pull
  request. If you changed `playground/`, also run the Playground's commands, because `make check`
  doesn't cover them. The README's [Checks](README.md#checks) section says what to run when, what
  each error means, and how to add a project's tests. On Windows, run the commands listed there.
  CI runs all of it on every pull request, and it must pass to merge. Install `requirements.txt`
  into `.venv/` first, and again whenever it changes: `python -m pip install -r requirements.txt`.

## Code and comments

- Every method and class gets a short one-line comment saying what it does.
- Other comments are short, plain and only where needed. No walls of text.
- Don't comment what the code already says. Comment the why, or a rule that isn't obvious.
- Write code a teammate can read at a glance. No clever tricks or dense one-liners.

## Repo rules

- **The data is synthetic.** Nothing built on it is a finding about real students or
  institutions. Say so whenever you report a result.
- **Use the `pdp-data` skill for raw ARF data questions** ([.agents/skills/pdp-data/SKILL.md](.agents/skills/pdp-data/SKILL.md)).
  CSV column names are shortened; look them up in `data/dictionaries/column_lookup.csv` instead
  of guessing.
- **For comparing groups or finding gaps, use the gap finder:** `find_gaps` or the `equity_gaps`
  table ([gap_finder/README.md](gap_finder/README.md)). Don't recompute gaps from `data/raw/`.
- **Use `pdp-sandbox`** when building a Playground Sandbox endpoint or chart from the normalized
  PDP data model ([.agents/skills/pdp-sandbox/SKILL.md](.agents/skills/pdp-sandbox/SKILL.md)).
- **For Playground UI and stories,** follow
  [the client agent instructions](playground/client_application/AGENTS.md), including the Storybook
  MCP guidance and source-file fallback.
- **Python packages go in `requirements.txt`,** pinned to exact versions (`package==1.2.3`) with
  a comment naming the foundation that needs them. Packages only a notebook needs go in
  `notebooks/requirements.txt`, which CI doesn't install. Install them in a virtual environment
  (`.venv/`), never into the system Python. Target Python 3.10 or newer. Keep
  `scripts/check.py` standard-library only.
- **Never rewrite or reformat files in `data/raw/` as a side effect.** Don't re-save, sort,
  re-encode, or change the line endings of the CSVs. They use Windows (CRLF) line endings, and any byte change breaks the
  checksum in `data/manifest.json`. Read them; write results somewhere else.
- **Never commit generated outputs,** such as DuckDB or SQLite databases, Parquet files, or
  exported CSVs. Commit the code that makes them, and add the output path to `.gitignore`.
  - **Exception, proposed until squads agree on #8:** the data model in `normalized-data-model/`
    commits the generated files listed below. Each is an input or a test fixture, not the result
    of a run: committing it means every squad loads and tests against the same file. Regenerate
    them with the commands in `normalized-data-model/README.md`; don't edit them by hand.
    - `normalized-data-model/data/input/enrichment/on_campus_housing.csv`: the synthetic
      on-campus housing input, made with a fixed seed.
    - `normalized-data-model/data/input/sample/` and `normalized-data-model/data/output/sample/`:
      the raw rows and the tables for 10 sample students (about 70 KB). The tests compare a
      rebuild against them, and squads can open them without running anything.
    - `normalized-data-model/config/column_dictionary.yaml`: what each normalized column means,
      built from `data/dictionaries/arf_*_data_dictionary.md` and `column_lookup.csv`. Edit those
      files, not this one: `tests/dictionary/test_build.py` fails if it differs from a rebuild.
  - **Exception, agreed for #11:** `mcp/schemas/tools.json`, the MCP server's published tool
    contract. It's the server's `tools/list`, written by `python -m pdp_mcp.export_schemas` (run
    from `mcp/`), so squads in any stack can read the schemas without running Python. Don't edit
    it by hand: `mcp/tests/test_contracts.py` fails if it differs from the running server. This
    exception covers that one file only.
- **Data changes must be deliberate.** If you change anything in `data/raw/` on purpose, run
  `python scripts/check.py --update`, update the README data table, and commit both in the same
  pull request.
- **Follow [CONTRIBUTING.md](CONTRIBUTING.md) and the pull request template.** Before you open a
  pull request:
  - Link the task with `Closes #N`, or `Refs #N` if more pull requests are coming for it.
  - Make sure `make check` passes.
  - If you add something other squads will use, explain it in the README.

## Agent skills

Compound Engineering is configured in `.compound-engineering/config.yaml`. Commit shared
settings and the example configuration; keep personal overrides in
`.compound-engineering/config.local.yaml` untracked. Run `$ce-setup` when checking or updating
the configuration. Setup for the other recommended skill set is already complete.

### Issue tracker

Tasks live in GitHub Issues (`bwold001/pdp-datathon--uncf`), managed with the `gh` CLI. See
[docs/agents/issue-tracker.md](docs/agents/issue-tracker.md).

- Always pass `--repo bwold001/pdp-datathon--uncf` to `gh issue` and `gh pr` commands. Without it,
  `gh` can pick the upstream starter (`devcolor/pdp-datathon-starter`) and post there.
- Every new issue goes on the squad's project board (`https://github.com/users/bwold001/projects/5`)
  in the **To Do** column of the kanban view. Add it with `gh project item-add 5 --owner bwold001
  --url <issue url>`, then set its Status to To Do.

### Triage labels

`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. All five exist.
See [docs/agents/triage-labels.md](docs/agents/triage-labels.md).

### Domain docs

Single-context: one `GLOSSARY.md` and `docs/adr/` at the repo root. See
[docs/agents/domain.md](docs/agents/domain.md).

### Knowledge store

Documented solutions to past problems live in `docs/solutions/`, one file per entry with YAML
frontmatter (`module`, `tags`, `problem_type`). Check it before planning or debugging in an area
that already has one. After solving something another squad might hit, add an entry using
[docs/solutions-template.md](docs/solutions-template.md); see
[docs/solutions/README.md](docs/solutions/README.md) for where to save it.

The project glossary is `GLOSSARY.md` at the repo root; read it for domain terms. Don't create
`CONCEPTS.md`. If a skill wants to add a term there, add it to `GLOSSARY.md` instead.
