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

For chat, run the [Playground](playground/README.md) backend and frontend and open `/uncf/chat`.
The original `/chat` and `/sandbox/data-chat-ui` bookmarks redirect there.
Load the cohort and course files using Workbench. Chat and its direct analysis endpoints use
Playground's configured `DATABASE_URL`, including newly uploaded data. SQLite and PostgreSQL
read the same deterministic calculations in read-only snapshots, without a results cache.
LiteLLM supplies natural-language interpretation using `UNCF_CHAT_MODEL` and the matching
server-side `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`. `UNCF_CHAT_ENABLED` controls chat independently
of Sandbox. Local development enables it; the dedicated Vercel chat service also enables it
unless explicitly disabled. The full Playground production app remains opt-in.

Directory ownership:

- `analytics/`: graduation, retention-by-major and enrollment calculations, receipts, coverage
  configuration and program attribution. No provider or Playground dependency.
- `measures/`: existing foundational calculations and their shared staff-facing definitions.
- `playground/server_application/app/chat/`: bounded provider orchestration and validated tools.
- `playground/server_application/app/services/analytics.py`: configured database adapter.
- `api/`: the provider-free Results and analysis HTTP interfaces used by the existing deployment.

#### Existing Results deployment

The existing Results API and its public `/api/v1/uncf/results`, `/options`, `/health` and
`/analyses` routes remain compatible. To run that standalone interface from the repository root:

```bash
python -m api load
python -m api serve
```

Vercel now points to `api.app:app` and builds the standalone extract with `python -m api load`.
The frontend still uses the same-origin `/api/v1` and `/` still opens `/uncf/paths`.
A separate `chat_app:app` service hosts chat at `/api/v1/chat` and `/api/v1/uncf/chat`.
It builds the same synthetic extract, reads it in read-only snapshots and exposes no uploads or
Sandbox endpoints. The Results service remains provider-free. See [deploy chat](docs/chat-deployment.md)
for secrets, model selection, preview verification and rollback. Tests in
`api/tests/test_vercel_config.py` verify routing and bundle contents.

The old top-level squad package and its precompute command have been retired. The independent
`run_measure(..., save=True)` API remains available for existing callers. No legacy result API
or dataset has been substituted for Playground uploads.

#### Numerical consistency

The model can select only approved analyses and definitions; no tool accepts arbitrary SQL.
Missing material parameters trigger typed clarification. Displayed numbers, formulas and
limitations come from validated receipts, never numerical model prose. Rates must match their
numerators and denominators. Suppressed values stay absent from evidence and display text.
All three graduation horizons, program perspectives, ethnicity handling and certified-coverage
rules remain intact. Missing award-semester evidence stays unknown, rather than inferred from
rounded time-to-credential. These safeguards are for synthetic demonstrations, not a universal
production privacy guarantee.

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

## Student success chat

The demonstration at `/uncf/chat` answers the agreed graduation, retention and annual enrollment questions with shared calculation receipts. See [calculation definitions and coverage requirements](docs/analytics-definitions.md).

1. Install Playground dependencies with `uv sync` in `playground/server_application/`, then load cohort and course files in Workbench.
2. Follow [Playground setup](playground/README.md) for its Python 3.14/uv and Node 24/Bun runtimes. Root Python and the Playground provider runtime are separate environments.
3. Set `UNCF_CHAT_MODEL=anthropic/claude-sonnet-5-5` with `ANTHROPIC_API_KEY`, or `UNCF_CHAT_MODEL=openai/gpt-4.1` with `OPENAI_API_KEY`, in the server's ignored `.env.development.local` or environment. LiteLLM handles provider translation. Use a tool-capable model available to your account and keep keys server-side. Existing unprefixed `claude-*` settings remain compatible.
4. Run the Playground API and client (`mise run api:dev`, `mise run web:dev`). The client uses its existing `NEXT_PUBLIC_API_BASE_URL`. Open `/uncf/chat` or use the Explorer’s Chat tab. The API demo routes use `UNCF_CHAT_ENABLED` (enabled in local development), independently of `SANDBOX_ENABLED`. Production remains opt-in.
5. Try “What is the graduation rate for chemistry majors?”, “What is the retention rate for all majors?” and “What is enrollment ethnicity by academic program over the past 2 years?” Choose the requested cohort, credential and chemistry definition. Open “How these results were calculated” to inspect supporting evidence.

The model can call only the catalog, definitions and approved analysis tools. It cannot submit SQL, student IDs or filesystem paths. A new question starts a separate analysis; only a pending typed request is carried through clarification. Reset discards late replies.

The unmodified mock extract does **not** certify complete academic years, full cohort follow-up or exact award semesters. Accordingly, some answers show unavailable/unknown states. Configure only verified coverage in `analytics/config/analytics.yaml`; an earlier associate award or rounded time-to-credential must never be used to invent a bachelor's award semester. These are implementation data limits, not permission to present fixture numbers as campus findings.

The standalone `python -m api` app also exposes deterministic `GET /api/v1/uncf/analyses/catalog` and `POST /api/v1/uncf/analyses`, without importing a model provider. Chat is served by Playground at `POST /api/v1/chat`; `/api/v1/uncf/chat` remains an alias. Existing `/results`, `/options` and `/health` contracts are preserved.

Verify with `make check` at the root; in Playground run `mise run api:lint`, `mise run api:test-sqlite`, `mise run web:build`, `mise run web:lint` and `mise run web:test-storybook`. New Python tests use small independently counted SQLite fixtures and a scripted model, with no live provider calls. Stories cover calculation details, clarification, unavailable states, errors and reset while pending.

Chat first proposes the full scope and requires explicit approval before calculating. No additional filters are inferred.
The Vercel frontend now enables Chat and routes requests to the dedicated chat service. Set the
matching provider key and model in Vercel before deployment; without a key, chat returns a readable
503 configuration error. `NEXT_PUBLIC_STUDENT_SUCCESS_CHAT_ENABLED=false` disables the UI after a
rebuild, and `UNCF_CHAT_ENABLED=false` disables backend chat routes. See the
[deployment guide](docs/chat-deployment.md).

Calculation deadlines cancel SQLite VM work and cooperative counting loops. Timeout responses wait for worker transaction cleanup; PostgreSQL statements use the remaining request budget.
