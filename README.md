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
| **Core** | Student Success Explorer: pick a cohort and filters, see each page's measures with definitions, denominators and limitations. Each page exports everything it shows as CSV. | Answers the agreed demo questions; charts and CSV match |
| **Stretch** | Bounded chat agent over the same aggregate results | Agreed questions get verified answers; unsupported ones are declined |

Every page, export and chat answer uses one result contract: measure, filters, numerator,
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

Four folders hold our code. Each number has one owner:

| Folder | What it holds |
| --- | --- |
| `measures/` | Every Explorer number: `run_measure`, one file per measure, the page breakdowns, and the staff facing definitions (`measures/definitions.py`) |
| `analytics/` | The chat's deterministic analyses: graduation, retention by major, annual enrollment, program attribution, coverage rules and receipts. No model provider or Playground needed |
| `api/` | HTTP only: request checks, response shapes and one router under `/api/v1/uncf`. No calculations |
| `playground/server_application/app/chat/` | The bounded chat: provider calls and validated tools. Database access is in `app/services/analytics.py` |

From the repo root, with `.venv` active:

```bash
python -m api              # load the data if it's missing, then serve the API on http://localhost:8001
python -m api load         # only load the data (about 75 seconds the first time)
python -m api serve        # only serve the API; --port to change it
```

`python -m api` doesn't need the Playground. Test it with `python -m pytest api`. Interactive API
docs: http://localhost:8001/docs. For the pages and chat, run the [Playground](playground/README.md)
backend and frontend: it mounts the same router (`playground/server_application/app/uncf.py`).
Chat setup is in [Student success chat](#student-success-chat).

#### Hosting on Vercel

[`vercel.json`](vercel.json) deploys only the Explorer, as one Vercel project with three
[services](https://vercel.com/docs/services):

- **frontend:** the Next.js app in `playground/client_application`. `/` redirects to `/uncf/paths`.
  Chat is enabled by default; `NEXT_PUBLIC_STUDENT_SUCCESS_CHAT_ENABLED=false` disables it after
  a rebuild.
- **backend:** the UNCF API (`api.route:app`) as a Python function. Its build runs
  `python -m api load`, so every deploy builds `pdp.sqlite` from the mock CSVs in `data/raw/`.
  The bundle includes `analytics/`, so `/analyses` works there too. This service is provider-free.
- **chat:** the dedicated `chat_app:app` service uses the official OpenRouter Python SDK. It builds
  the same synthetic extract, reads it in read-only snapshots and exposes no uploads or Sandbox
  endpoints. Build-only PyArrow is removed after loading the extract to keep the function bundle
  within Vercel’s limit. See [deploy chat](docs/chat-deployment.md) for credentials, model selection,
  Preview verification and rollback.

All three sit on one site: `/api/v1/chat` and `/api/v1/uncf/chat` go to chat before the
`/api/v1/uncf/*` API catch-all; everything else goes to the pages. The client is built with
`NEXT_PUBLIC_API_BASE_URL=/api/v1`, so a preview calls its own API and needs no CORS. Call it from client components: a relative URL doesn't work in a server side `fetch`.
`api/tests/test_vercel_config.py` checks the wiring.

The data is mock data and the site is public. Before real student data goes here, it needs a
login, data that doesn't live in git, and the data owner's sign off.

#### How the numbers are calculated

Every Explorer number comes from `measures/`. The API only checks the request and shapes the answer:

```
measures/run_measures.py   run_measure: every rate (retention, federal retention, persistence,
                           gateway math and English, DFW with D/F/W, credit completion), with
                           group_by and filters; read_answers: each student's answer
measures/calculations/     one file per measure, including federal_retention.py
measures/breakdowns/       the Explorer pages: Student paths, DFW courses, gateway courses,
                           credit momentum. Rates from run_measure, split by term, course, flow or tier
measures/definitions.py    every plain language definition
api/filters.py             the cohort bar: checks cohort, 8 filters and retention type
api/measure_by_group.py    one measure split by group, for /measures/{measure}, from run_measure
api/analyses.py            the chat's analyses over HTTP, from analytics/
api/route.py               one app under /api/v1/uncf (Vercel entrypoint api.route:app)
api/data.py                where the data lives, load time, provisional cohorts
api/load.py                builds pdp.sqlite when it's missing
```

- **Calculated per request** from `normalized-data-model/output/pdp.sqlite`. Nothing is saved.
  Answers are cached in memory and recalculated when `pdp.sqlite` changes.
- **Pages don't calculate.** The UI fetches and draws. Shares, gaps, totals and hiding all come
  from the API, which gets them from `measures/`.
- **Retention type** on every route: `school` (default, the `retention` measure, the PDP
  retention flag) or `federal` (the `federal_retention` measure: took a course here the fall
  after year 1). The rules still open with stakeholders (first time students only, credentials)
  are settings in `measures/calculations/federal_retention.py`.
- **DFW** rows carry `split`: D (0.7 to under 2.0), F (an F or under 0.7) and W, adding up to the
  numerator. DFW can also be grouped or filtered by `course`, `term` and `delivery`.
- **Definitions** come from `measures/definitions.py`. A school's own metric names go in
  `LOCAL_NAMES`, picked with `UNCF_SCHOOL=fmu` or `benedict`.

Every page route and `/measures/{measure}` take the same query values: `cohort`, the 8 filters
(`cohort_term`, `enrollment_intensity`, `enrollment_type`, `pell`, `gender`, `race`, `ethnicity`,
`age_band`, with the measures' values), `retention_type=school|federal` and `format=json|csv`.

| Endpoint | What it returns |
| --- | --- |
| `GET /api/v1/uncf/measures/{measure}?cohort=&group_by=` | One measure split by group: the everyone row, then one row per group. `group_by` up to twice. `dfw_rate` rows carry the D, F, W split. No page calls it; it's for chat questions a page doesn't answer, such as a rate by race. The old `GET /results?measure=` URL still answers, hidden from the docs |
| `GET /api/v1/uncf/options` | The measures, classes and groupings `/measures/{measure}` takes |
| `GET /api/v1/uncf/health` | Whether the data is loaded, and `loaded_at` |
| `GET /api/v1/uncf/cohort-options?cohort=` | Students per cohort year, and per filter value in the chosen cohort |
| `GET /api/v1/uncf/definitions` | Every plain language definition |
| `GET /api/v1/uncf/student-paths?…&terms=&group_by=` | Each student's status term by term (here, credential, elsewhere, stopped) with shares, moves, transfers, retention, and per group paths |
| `GET /api/v1/uncf/dfw?…` | Everyone's DFW rate with D, F, W, then each course with 10 or more students |
| `GET /api/v1/uncf/dfw/course?course=ENG%20101&…` | One course by term, delivery and group, each with `rest_rate` and `gap` against everyone else |
| `GET /api/v1/uncf/gateway?…` | Each flagged gateway course in year 1: students, passed on the first try and in the end (the PDP's 1.0 line), the path after the first try, retention if passed / not, the filtered group's gap against everyone else, and the course pairs with lower retention |
| `GET /api/v1/uncf/credit-momentum?…` | Year 1 credits, completion ratio, 12/24/30 milestones, first two terms, credit tiers with retention; `progress`: meaningful progress toward a degree (the 24-credit minimum, 4-year pace, year 1 groups with retention, why students fell below, year 2), settings in `measures/breakdowns/credit_progress.py` |
| `GET /api/v1/uncf/analyses/catalog` | The chat's approved analyses, their choices and declared data coverage |
| `POST /api/v1/uncf/analyses` | One approved analysis with its receipt, or a clarification when a needed choice is missing |

- **Hidden or missing numbers** are `null` with a status: `suppressed` (under 10 students),
  `not_yet_observable`, or `not_reported` (a gateway measure the college doesn't report). Never 0.
  Starter issue #87 (working out a hidden group by subtraction) is not fixed.
- **`provisional`** is true for the 2024-25 class, whose second year is only partly in the data.
- **Errors:** 422 for a value the API doesn't offer (`invalid_filter`, `invalid_group_by`,
  `invalid_analysis`), 404 `unknown_course`, 503 `data_missing` or `analytics_unavailable`. Bodies
  are `{"error": {"code", "message"}}`.
- **CORS** allows http://localhost:3000 (change with `UNCF_CORS_ORIGINS`).

How to build a tab: `playground/client_application/src/components/uncf/layout/README.md`.

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
| [Success measures](measures/README.md) | Retention, persistence, gateway completion; we added federal retention, DFW, credit completion, filters and the page breakdowns |
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

## Student success chat

The demonstration at `/uncf/chat` (the Explorer's Chat tab) answers the agreed graduation,
retention and annual enrollment questions with shared calculation receipts from `analytics/`. The
old `/chat` and `/sandbox/data-chat-ui` bookmarks redirect there. See
[calculation definitions and coverage requirements](docs/analytics-definitions.md).

1. Install the Playground's dependencies with `uv sync` in `playground/server_application/`, then
   load the cohort and course files in Workbench. Chat and `/analyses` read the Playground's
   `DATABASE_URL` (SQLite or PostgreSQL, read only snapshots, no results cache), so newly uploaded
   data shows up.
2. Follow [Playground setup](playground/README.md) for its Python 3.14/uv and Node 24/Bun runtimes.
   The root Python and the Playground's provider runtime are separate environments.
3. Set `OPENROUTER_API_KEY` and `UNCF_CHAT_MODEL=openai/gpt-4.1` in the server's ignored
   `.env.development.local` or environment. Use a canonical, tool-capable OpenRouter model ID
   available to your account. The same key supports model changes. Replace legacy OpenAI/Anthropic
   keys and bare `claude-*` settings; no names are rewritten. Keep the key server-side.
4. Run the Playground API and client (`mise run api:dev`, `mise run web:dev`) and open `/uncf/chat`.
   `UNCF_CHAT_ENABLED` controls chat independently of `SANDBOX_ENABLED`. It is enabled in local
   development and the dedicated Vercel chat service unless explicitly disabled. Full Playground
   production remains opt-in. The client uses its existing `NEXT_PUBLIC_API_BASE_URL`.
5. Try "What is the graduation rate for chemistry majors?", "What is the retention rate for all
   majors?" and "What is enrollment ethnicity by academic program over the past 2 years?" Choose
   the cohort, credential and chemistry definition it asks for, then open "How these results were
   calculated" to see the evidence.

Chat is served by the Playground at `POST /api/v1/chat` (`/api/v1/uncf/chat` is an alias). It
uses the same `/api/v1/uncf/analyses` routes the standalone API offers.

**Safeguards.** The model can call only the catalog, definitions and approved analysis tools. No
tool accepts SQL, student IDs or file paths. Chat proposes the full scope and needs explicit
approval before calculating, and infers no extra filters. A missing choice gets a typed
clarification. A new question starts a separate analysis; only a pending typed request carries
through clarification, and reset discards late replies. Displayed numbers, formulas and
limitations come from validated receipts, never from the model's prose. Rates must match their
numerators and denominators, and suppressed values stay out of evidence and display text. All
three graduation horizons, program perspectives, ethnicity handling and certified coverage rules
stay in place. Calculation deadlines cancel SQLite work and counting loops; timeouts wait for
transaction cleanup, and PostgreSQL statements use the remaining request budget. These
safeguards are for synthetic demonstrations, not a production privacy guarantee.

**Data limits.** The unmodified mock extract does **not** certify complete academic years, full
cohort follow up or exact award semesters, so some answers show unavailable or unknown. Configure
only verified coverage in `analytics/config/analytics.yaml`. An earlier associate award or a
rounded time to credential must never be used to invent a bachelor's award semester.

**Checks.** `make check` at the root covers `analytics/`. In the Playground run `mise run api:lint`,
`mise run api:test-sqlite`, `mise run web:build`, `mise run web:lint` and
`mise run web:test-storybook`. Python tests use small, independently counted SQLite fixtures and a
scripted model, with no live provider calls.

The Vercel chat service needs the OpenRouter key and model configured before deployment; without
its key, chat returns a readable 503 configuration error.
`NEXT_PUBLIC_STUDENT_SUCCESS_CHAT_ENABLED=false` disables the UI after a rebuild, and `UNCF_CHAT_ENABLED=false` disables backend chat routes.
See the [deployment guide](docs/chat-deployment.md).

The proposed v2 analysis boundary is currently inactive and does not change the routes above.
See [v2 contracts and client fixtures](docs/analysis-v2-contracts.md) for typed plans, clarification,
evidence and partial-result rules, and the focused test command for work on that boundary.

The [shared snapshot and replay guide](docs/analysis-v2-snapshots.md) describes transaction ownership,
configured database access, loader build identity, cancellation and reproducible computation inputs.

The [defined operation catalog](docs/analysis-v2-defined-operations.md) registers the existing dashboard
and legacy analyses with executable request schemas and typed result adapters. It remains inactive in HTTP/chat.

The [disclosure and parity guide](docs/analysis-v2-disclosure.md) documents versioned dashboard/legacy
policies, shared API/CSV execution, and the conservative guard for future mixed v2 plans.
