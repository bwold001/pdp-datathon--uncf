# UNCF Squad: Student Success Explorer

The UNCF squad's build for the /dev/color × Gates PDP Datathon (Seattle, starts Nov 9, 2026).
One shared tool that helps Florida Memorial University (FMU) and Benedict College staff explore
student-success outcomes, read the definitions behind each number, and export results.

**All data here is synthetic.** Nothing built on it is a finding about real students or either
university.

Made from [devcolor/pdp-datathon-starter](https://github.com/devcolor/pdp-datathon-starter) at
commit `cef57aa` (the starter's latest commit when this repo was created, 2026-11-05).

## What we're building

| Priority | What | Done when |
| --- | --- | --- |
| **Core** | Student Success Explorer: pick a cohort and two group filters, see retention and gateway math/English completion, with definitions, denominators and limitations. CSV export. | Answers the two agreed demo questions; charts and CSV match |
| **Stretch 1** | Shareable insight card with a print/PDF layout | At least one card whose numbers match the Explorer |
| **Stretch 2** | Bounded chat agent over the same aggregate results | Agreed questions get verified answers; unsupported ones are declined |

Every screen, card and chat answer uses one result contract: measure, filters, numerator,
denominator, rate, suppression status, limitations, definition, source and load time. "Unavailable"
is never shown as zero. Small groups are suppressed everywhere, including exports and chat.

## Set up

You need Python 3.10 or newer. The Playground also needs [mise](https://mise.jdx.dev) and
[bun](https://bun.sh) (see [playground/README.md](playground/README.md)).

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
make check-fast                  # no make on Windows? see Checks below
```

Reinstall whenever `requirements.txt` changes.

### Run the project

From the repo root, with `.venv` active:

```bash
python -m uncf
```

`python -m uncf` is the one entry point for everything we build in `uncf/`. Today it runs the precompute; the API and later pieces will start from here too. It loads the data if `normalized-data-model/output/pdp.sqlite` is missing (about 75 seconds), then
runs retention, gateway math and gateway English for every cohort and group, and writes the rows to
`measures/output/success_measures.sqlite` (about 10 seconds). It doesn't need the Playground. Test it
with `python -m pytest uncf`.

#### How the precompute works

- **Runs standalone.** It runs from the root env and needs no Playground. `measures/` uses only the
  standard library, so it imports from the repo root. The API will read `success_measures.sqlite`
  with `sqlite3` and never call `run_measure`.
- **Two databases.** The loader writes `normalized-data-model/output/pdp.sqlite` (the source). The
  precompute writes `measures/output/success_measures.sqlite` (the results). The Playground's own
  database (PostgreSQL by default) is a third, separate one and is not used here.
- **One save per measure.** A save replaces earlier rows for the same measure and cohort, so
  `precompute()` passes every cohort and group in one `run_measure` call per measure. Splitting
  groups across calls would wipe the first ones.
- **What is saved.** Retention, gateway math and gateway English, for 2021-22 to 2024-25, by every
  single dimension and every pair except first-gen: 36 groups, 7,080 rows.
- **Timestamp.** There is no separate timestamp table. Each row's `data_loaded_at` is when
  `pdp.sqlite` was built, not when the precompute ran, so a restart never makes old data look new. The API's `loaded_at` is `MAX(data_loaded_at)`.
- **When data changes.** Every start recomputes (about 10 seconds), so new data shows up after a
  reload of `pdp.sqlite` and a restart, with a newer `data_loaded_at`. The loader only runs when
  `pdp.sqlite` is missing: to pick up new source files, delete it or run the loader yourself.
- **Small groups.** Hidden groups (under 10 students) have blank numbers, never 0. Saving every pair
  gives more ways to subtract a hidden group from totals (starter issue #87, not fixed).
- **Where the API runs.** The API is a standalone FastAPI app from `uncf/`. It needs only
  `success_measures.sqlite` to exist. The Playground is not required.
- **Columns.** The `success_measures` columns are defined in `measures/save_results.py`.

#### See the Explorer

The Explorer (#6) is at http://localhost:3000/uncf/explorer once the Playground web app runs
(`mise run web:dev` from `playground/`). Until the #5 API exists, it reads a fixture of the saved
results. Build it after the precompute:

```bash
python -m uncf                   # the precompute, if you haven't run it
python -m uncf.explorer_fixture  # writes playground/client_application/public/uncf/explorer-fixture.json
```

The fixture is git-ignored (it's a generated output). When #5 lands, `loadResults` in
`playground/client_application/src/app/(app)/uncf/data.ts` calls the API instead and this step goes away.

Outcomes the precompute doesn't save yet (persistence, today) are calculated by the fixture script with
the same measures code, and it says so when it runs. Once the precompute saves them, its rows are used instead.

The fixture also holds **mock** year-2 paths (`uncf/paths_mock.py`) for the "Where were they in year 2?"
chart, which is labeled "Mock data" on screen and in the CSV. No endpoint serves paths yet; the shape in
`data.ts` (`PathsResponse`) is a proposal for whoever builds it. The Explorer also has trend lines across
entering classes, a "Download CSV" button (every outcome and the paths for the view, with the shared
result contract's columns), and "Create insight card", which opens `/uncf/card?cohort=…&group_by=…&measure=…`.

## Data

Mock data from [Achieving the Dream](https://achievingthedream.org/), in the shape of PDP's
analysis-ready files. One institution's extract, with no institution column.

| File | Rows | Columns | What it is |
| --- | ---: | ---: | --- |
| [pdp_cohort_data.csv](data/raw/pdp_cohort_data.csv) | 10,313 | 85 | One row per student. Dictionary: [cohort](data/dictionaries/arf_cohort_data_dictionary.md) |
| [pdp_course_data.csv](data/raw/pdp_course_data.csv) | 100,951 | 35 | One row per student per course per term. Dictionary: [course](data/dictionaries/arf_course_data_dictionary.md) |

CSV column names are shortened. Look them up in
[column_lookup.csv](data/dictionaries/column_lookup.csv). Known quirks and the skill that explains
columns: [pdp-data skill](.agents/skills/pdp-data/SKILL.md#known-data-facts). Never edit files in
`data/raw/`; the checksums in [data/manifest.json](data/manifest.json) will fail.

## Starter pieces we reuse

| Piece | Use |
| --- | --- |
| [Normalized data model](normalized-data-model/README.md) | Tables, keys, loader into SQLite or PostgreSQL |
| [Success measures](measures/README.md) | Retention, persistence, gateway completion |
| [Playground](playground/README.md) | Next.js + FastAPI app shell and chart examples |
| [Data quality log](data/quality/README.md) | Known mock-data issues, such as first-generation status |
| [PDP MCP server](mcp/README.md) | Definitions only, for development support |
| [Equity gap finder](gap_finder/README.md) | Optional group comparisons |

## Checks

Run from the repository root. CI runs all of this on every pull request, and the `data`, `links`
and `playground` checks must pass to merge.

| You changed | While you work | Before a pull request |
| --- | --- | --- |
| Data or a foundation | `make check-fast` | `make check` |
| [`playground/`](playground/README.md) | `cd playground && mise run api:test-sqlite` | `make check`, then the Playground commands in its README |

Without `make` (Windows), run `python scripts/check.py`, `python data/quality/run_checks.py`, and
`cd normalized-data-model && python -m pytest -q`. If you change `data/raw/` on purpose, run
`python scripts/check.py --update` and update the table above in the same pull request.

## How we work

Short branch, pull request, a teammate reviews, then merge. See
[CONTRIBUTING.md](CONTRIBUTING.md) and [AGENTS.md](AGENTS.md).
