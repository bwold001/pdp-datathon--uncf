# Known issues and limitations

The one list of what doesn't work, what only works in some setups, and what nobody has tested. Read
it before you try the Explorer on your own data. The steps to run it on real data, and the checklist
before you do, are in the [integration guide](integration.md).

**All data in this repository is synthetic.** Nothing it shows is a finding about real students or
institutions.

## The mock data

The mock PDP files have known bugs, which the loader fixes or flags. Each one is logged, with counts
and the fix, in [data/quality/findings.csv](../data/quality/findings.csv), and
`python data/quality/run_checks.py` recomputes every count. The ones that change Explorer numbers:

- **Retention and persistence disagree** with the course rows for some students. For example, 577
  students have retention = 1 and a course at another college, but persistence = 0 (rows `3`,
  `N15`). The Explorer keeps the reported flags and doesn't overwrite them.
- **Group columns use values the dictionary doesn't list.** First-generation status holds Y/N,
  Pell status has `U`, and enrollment fields have `Continuing` or `Unknown` (rows `1`, `7a`, `N6`).
  These show up as "unknown" groups.
- **Duplicate class rows** (530 extra rows) count more than once in the DFW rate (row `9`).
- **Year 1 credits attempted** differ from the student's own course rows for 1,303 students
  (row `4`). Students with no credits attempted are left out of credit completion.
- **Gateway flags** sometimes contradict the course rows (rows `N1` to `N4`).
- **There's no institution column.** The files hold one institution's extract, so the Explorer
  can't compare schools or tell whether two course names belong to different schools (row `5`).
- **Nobody knows how complete the data is.** The mock files don't say which academic years are
  complete or how long each cohort was followed. `analytics/config/analytics.yaml` is left empty,
  so some chat answers (graduation within six years, for example) say "unavailable".
- **The 2024-25 cohort is provisional.** Its second year is only partly in the data, so its
  retention may change.

## Definitions to confirm with your institution

These are set for the mock data. They are team choices, not campus-confirmed rules:

- **Federal retention:** who counts (first-time students only, which credentials) is a setting in
  `measures/calculations/federal_retention.py`, still open with stakeholders.
- **Grade lines:** a C- passes for DFW (the line is 1.7 grade points). The Gateway courses page
  counts a first attempt of C or better (2.0 grade points), or P, as passing, while the cohort
  gateway completion measures keep the PDP's own completion flags (a D, 1.0, or better). So the
  page's pass rates can be lower than the PDP dashboard's for the same course. Check which line
  your office reports. It is `GATEWAY_PASS_AT` in `measures/calculations/grades.py`; the DFW line
  is in `measures/calculations/dfw.py`.
- **Gateway courses** come from the PDP's gateway flag in the course file, not a campus course
  list.
- **Credit milestones** (12, 24 and 30 credits, the 24-credit minimum for meaningful progress) are
  settings in `measures/breakdowns/credit_progress.py`.
- **School names for measures** go in `LOCAL_NAMES` in `measures/definitions.py`, picked with
  `UNCF_SCHOOL`. Entries exist for `fmu` and `benedict`, but both are empty, so the pages show the
  PDP's standard names.

## Pages and exports

- **"Synthetic" labels stay on with real data.** The header badge, the disclaimers and the chat's
  evidence cards and receipts say the data is synthetic whatever you load. `UNCF_SOURCE` changes
  only the API's source line. Change these before staff use real numbers, so nobody misreads them as
  a demonstration.
- **The cohort picker lists only the four sample years** (2021-22 to 2024-25), set in
  `playground/client_application/src/components/uncf/layout/explorer-config.ts`. The API offers the
  years in your data, but until the picker reads them from `/api/v1/uncf/options`, add your years
  to that list and rebuild the pages.
- **No CSV button.** The pages download as a PDF (**Share Insight**). The API returns every page as
  CSV with `format=csv` ([integration guide, section 9](integration.md#9-getting-numbers-into-power-bi-or-a-data-lake)).
- **CSV columns can change with the filters.** A page's CSV columns follow what its answer holds, so a
  few can come and go (Gateway's group-comparison columns, for example).
- **The pages and API read SQLite only.** PostgreSQL works for the loader and the chat, not the
  pages. SQL Server and data lakes aren't supported.

## Privacy and access

- **No sign in.** Anyone who can reach the site sees everything. Put sign in in front of it
  ([integration guide, section 7](integration.md#7-sign-in-and-access)).
- **Small groups are not hidden.** Every nonempty group is shown, including groups of one. That's
  fine for synthetic data and **not** safe for real student records without a decision from your
  data owner.
- **Loads leave student-level working files** in `normalized-data-model/` (staging, tables and
  failed records). Protect and clean them up on real data.
- **Real student data must never be committed.** Keep PDP files outside the repository.

## Chat

- **Chat needs an OpenRouter key** and only works with OpenRouter for now. Other providers (Azure
  OpenAI, a model your school runs) are planned, not built. Chat sends the question text to the
  provider and model you pick. Turning chat on and off:
  [integration guide, section 8](integration.md#8-chat).
- **The safeguards are for demonstrations**, not a privacy guarantee.
- **Not checked against a live model.** The chat's tests use a scripted model. The fixed set of 41
  questions that checks how a real model reads questions has never run against a live model, because it
  needs a key. Run the [model check](chat.md#check-a-model-before-you-rely-on-it) before you rely on
  chat, and again whenever you change the model.
- **Hosted chat not verified.** Matching answers between the pages, the API and chat were checked
  locally, not on a deployed site.
- **Exploration answers:** `measure_variant` always returns "unavailable" for now. A correlation from
  two students is always +1 or -1, so treat coefficients from very small groups with caution. If one
  student's rows conflict, exploration answers for that whole cohort are unavailable (the pages are
  not affected).

## Setup

- **`vercel.json` only works on Vercel.** Each deploy rebuilds the database, and the chat bundle is
  near Vercel's size limit.
- **Windows:** `mise` runs tasks with `cmd`. If a task fails, run it from Git Bash or run the command
  it wraps (for example `uv run fastapi dev app/main.py` in `playground/server_application/`).
- **Two Python setups.** The root tools need Python 3.10 or newer; the Playground server uses Python
  3.14 through uv. They are separate environments.
- **Planned, not built:** a container image, SQL Server support and other chat providers.

## Not tested

- **A real PDP export.** Everything has only run on the mock files. A real export may have different
  values, more institutions or columns the mappings don't expect.
- **Several institutions in one extract.** The data model has an `institution` table, but the
  pages assume one school.
- **Many users at once.** Results are cached in memory per server process. Load was never tested.
- **Accessibility.** Storybook reports accessibility problems but doesn't fail on them, and no one
  did a full screen-reader review.

## What breaks when you swap in your own data

- `python scripts/check.py` checks `data/raw/` against the checksums in `data/manifest.json`, and a
  data model test checks the files match the ones the mappings were written for. Both fail on any
  other file. That's expected: load your files with `python -m api load --cohort … --course …`
  instead of replacing `data/raw/`.
- Tests that count rows in the mock data fail on other data.
- The loader rebuilds every table each time (no incremental load). The mock data needs about
  650 MB of memory at its peak, so a larger export needs more.
- The financial aid file isn't in the mock data and isn't loaded.
