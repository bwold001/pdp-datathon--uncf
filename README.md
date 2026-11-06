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
