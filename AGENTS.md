# AGENTS.md

Instructions for AI coding agents (and the people using them) who change their own copy of the
Student Persistence and Pathway Explorer. [README.md](README.md) says what it is and how to run it,
[docs/architecture.md](docs/architecture.md) how the parts fit, and
[docs/integration.md](docs/integration.md) how to run it on a school's own data.

**The data in this repository is synthetic.** Nothing built on it is a finding about real students
or institutions. Say so whenever you report a result, and never commit real student data.

## Where code goes

Each number has one owner. Put a change with its owner:

- **Every Explorer number** (measures, the filters on them, page breakdowns) and its plain-language
  definition: `measures/`.
- **The chat's analyses** (graduation, retention by major, enrollment, exploration), program
  attribution, data coverage and receipts: `analytics/`.
- **HTTP only** (request checks, response models, one router under `/api/v1/uncf`): `api/`. No
  calculations here. The Playground server mounts this router with one line.
- **Chat provider calls and validated tools:** `playground/server_application/app/chat/`; its
  database access: `playground/server_application/app/services/analytics.py`.
- **Pages:** `playground/client_application/src/app/(uncf-explorer)/uncf/`; their components:
  `playground/client_application/src/components/uncf/`. Pages fetch and draw; they don't calculate.
- **Per-school differences** (names, coverage, data fixes) go in config, not in a copy of the code.

## Rules that keep the numbers right

- **Every number shown comes from a validated, deterministic receipt.** Never let a model write
  numbers, and never answer with arbitrary SQL. The chat proposes a plan; the code calculates.
- **The API and chat share one set of rules** for coverage, missing values and small groups. Change
  them in one place.
- **Keep the API's URLs stable**, including the old `/results` URL, and the routing in
  `vercel.json`, so existing reports and links keep working.
- **Look up PDP columns; don't guess.** The CSV column names are shortened. Use
  `data/dictionaries/column_lookup.csv`, the dictionaries in `data/dictionaries/`, or the
  [`pdp-data` skill](.agents/skills/pdp-data/SKILL.md).
- **For group gaps, use the gap finder** (`find_gaps` or the `equity_gaps` table,
  [gap_finder/README.md](gap_finder/README.md)). Don't recompute gaps from `data/raw/`.

## Data files

- **Never change files in `data/raw/` as a side effect.** Don't re-save, sort, re-encode or change
  their line endings (they use CRLF): any byte change breaks the checksums in `data/manifest.json`.
  Read them and write results somewhere else. To load a school's files, use
  `python -m api load --cohort … --course …`, not a replacement in `data/raw/`.
- **Don't commit generated outputs** such as SQLite or DuckDB databases, Parquet files or exported
  CSVs. Commit the code that makes them and add the path to `.gitignore`. The exceptions are test
  inputs the data model commits on purpose: `normalized-data-model/data/input/` (the synthetic
  enrichment files and 10 sample students), `normalized-data-model/data/output/sample/` and
  `normalized-data-model/config/column_dictionary.yaml`. Regenerate them with the commands in
  [normalized-data-model/README.md](normalized-data-model/README.md); don't edit them by hand.
- **A deliberate change to `data/raw/`** needs `python scripts/check.py --update` and the README's
  data table updated in the same change.

## Building and checking

- **Plan first** for anything bigger than a small fix, and write down how you'll know it works (a
  command, a test or an expected number) before you build.
- **Every new behavior gets a pytest test** in the `tests/` folder next to the code (`api/`,
  `measures/` and `analytics/` each have one).
- **Run the checks.** From the repository root, with `requirements.txt` installed in `.venv/`:
  `make check-fast` while you work and `make check` before you finish. Without `make` (Windows):
  `python scripts/check.py`, `python data/quality/run_checks.py` and
  `cd normalized-data-model && python -m pytest -q`. If you changed `playground/`, also run its
  commands in [playground/README.md](playground/README.md#checks).
- **Cap retry loops** at about three tries, then stop and ask a person.

## Code style

- Every function and class gets a short one-line comment saying what it does.
- Other comments only where needed: the why, or a rule that isn't obvious. Not what the code says.
- Code a reader can follow at a glance. No clever tricks or dense one-liners.
- Python packages go in `requirements.txt`, pinned to exact versions (`package==1.2.3`), installed
  in `.venv/`. Target Python 3.10 or newer. Keep `scripts/check.py` standard-library only.
- For the web app and its Storybook stories, follow
  [the client agent instructions](playground/client_application/AGENTS.md).
