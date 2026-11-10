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
python -m uncf              # load the data if it's missing, then serve the Results API on http://localhost:8001
python -m uncf load         # only load the data (about 75 seconds the first time)
python -m uncf serve        # only serve the API; --port to change it
```

`python -m uncf` is the one entry point for everything we build in `uncf/`. It doesn't need the
Playground. Test it with `python -m pytest uncf`. Interactive API docs: http://localhost:8001/docs.

#### Hosting on Vercel

[`vercel.json`](vercel.json) deploys only the Explorer, as one Vercel project with two
[services](https://vercel.com/docs/services):

- **frontend:** the Next.js app in `playground/client_application`. `/` redirects to `/uncf/paths`.
- **backend:** the UNCF API (`uncf.api_route:app`) as a Python function. Its build runs
  `python -m uncf load`, so every deploy builds `pdp.sqlite` from the mock CSVs in `data/raw/`.

Both sit on one site: `/api/v1/uncf/*` goes to the API and everything else goes to the pages. The
client is built with `NEXT_PUBLIC_API_BASE_URL=/api/v1`, so a preview calls its own API and needs
no CORS. Call it from client components: a relative URL doesn't work in a server-side `fetch`.
`uncf/tests/test_vercel_config.py` checks the wiring.

The data is mock data and the site is public. Before real student data goes here, it needs a
login, data that doesn't live in git, and the data owner's sign-off.

#### How the numbers are calculated

One place defines every metric, and everything else asks it:

```
uncf/filters.py     the filters: cohort, 8 filters, retention type, student selection, hide under 10
uncf/metrics.py     every named metric, once: retention (school or federal), DFW (D, F, W),
                    gateway outcome, credit completion. Built on the shared measures' own SQL and
                    grade rules; the tests check each one against run_measure on the real data.
uncf/api_results.py the Results API's rows from the metrics
uncf/student_paths.py, dfw_courses.py, gateway_courses.py, credit_momentum.py
                    the Explorer pages: break the metrics down by term, course, flow or tier
uncf/api_route.py   one router for all of it, under /api/v1/uncf (Vercel entrypoint uncf.api_route:app)
uncf/data.py        where the data lives, load time, provisional cohorts
```

- **Calculated per request** from `normalized-data-model/output/pdp.sqlite`. Nothing is saved.
  Answers are cached in memory and recalculated when `pdp.sqlite` changes.
- **Pages don't calculate.** The UI fetches and draws. Shares, gaps, totals and hiding all come
  from the API.
- **Retention type** on every route: `school` (default, the PDP retention flag) or `federal`
  (fall to fall: took a course here the fall after year 1). The federal rules still open with
  stakeholders (first time students only, credentials) are in `metrics.FEDERAL_RETENTION`.
- **DFW** is split into D (0.7 to under 2.0), F (an F or under 0.7) and W. D + F + W is the
  `dfw_rate` measure.
- **Definitions** come from `uncf/definitions.py`. A school's own metric names go in
  `LOCAL_NAMES`, picked with `UNCF_SCHOOL=fmu` or `benedict`.

Every page route and `/results` take the same query values: `cohort`, the 8 filters
(`cohort_term`, `enrollment_intensity`, `enrollment_type`, `pell`, `gender`, `race`, `ethnicity`,
`age_band`, with the measures' values), `retention_type=school|federal` and `format=json|csv`.

| Endpoint | What it returns |
| --- | --- |
| `GET /api/v1/uncf/results?measure=&cohort=&group_by=` | One measure: the everyone row, then one row per group. `group_by` up to twice. `dfw_rate` rows carry the D, F, W split |
| `GET /api/v1/uncf/options` | The measures, classes and groupings a client can ask for |
| `GET /api/v1/uncf/health` | Whether the data is loaded, and `loaded_at` |
| `GET /api/v1/uncf/cohort-options?cohort=` | Students per cohort year, and per filter value in the chosen cohort |
| `GET /api/v1/uncf/definitions` | Every plain-language definition |
| `GET /api/v1/uncf/student-paths?…&terms=&group_by=` | Each student's status term by term (here, credential, elsewhere, stopped) with shares, moves, transfers, retention, and per group paths |
| `GET /api/v1/uncf/dfw?…` | Everyone's DFW rate with D, F, W, then each course with 10 or more students |
| `GET /api/v1/uncf/dfw/course?course=ENG%20101&…` | One course by term, delivery and group, each with `rest_rate` and `gap` against everyone else |
| `GET /api/v1/uncf/gateway?…` | Gateway first attempts in year 1 (passed, D, F, W, shares), retention by outcome, riskiest first term pairs |
| `GET /api/v1/uncf/credit-momentum?…` | Year 1 credits, completion ratio, 12/24/30 milestones, first two terms, credit tiers with retention |

- **Hidden or missing numbers** are `null` with a status: `suppressed` (under 10 students),
  `not_yet_observable`, or `not_reported` (a gateway measure the college doesn't report). Never 0.
  Starter issue #87 (working out a hidden group by subtraction) is not fixed.
- **`provisional`** is true for the 2024-25 class, whose second year is only partly in the data.
- **Errors:** 422 for a value the API doesn't offer (`invalid_filter`, `invalid_group_by`), 404
  `unknown_course`, 503 `data_missing`. Bodies are `{"error": {"code", "message"}}`.
- **Run it:** `python -m uncf` (port 8001, docs at http://localhost:8001/docs). CORS allows
  http://localhost:3000 (change with `UNCF_CORS_ORIGINS`). The Playground server mounts the same
  router (`playground/server_application/app/uncf.py`).

How to build a tab: `playground/client_application/src/components/uncf/layout/README.md`.

#### How the precompute works

> **Being retired in #4:** the Results API now calculates per request, so it no longer reads
> `success_measures.sqlite`. `python -m uncf precompute` still works until #4 removes it.

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
