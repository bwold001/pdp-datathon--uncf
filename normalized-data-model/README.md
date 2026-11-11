# Normalized data model

This folder holds the contract for the normalized data model (proposal [#8](https://github.com/devcolor/pdp-datathon-starter/issues/8)). It says:
- which tables exist, and each column's type and keys
- where every column of the two mock Analysis-Ready Files goes
- what a valid stored value looks like
- how two example enrichment files feed in
- what the tables look like for 10 real students

The validator checks a run's files against all of it and keeps an audit trail. The loader builds the tables from the full data into SQLite or PostgreSQL: see [Load the data](#load-the-data).

**The sample rows are real rows from the mock data, but they have not been validated.** The schema and the configs are the stable part. Values in the samples can be wrong in the same ways the mock data is.

## What's here

| File | What it is |
|---|---|
| `config/destination_schema.yaml` | The tables, and what a valid stored value looks like. One map per table; each column has its Python type (`str`, `int`, `float`, `bool`, `date`, `datetime`), whether it can be blank, its keys, and its validation rules. A foreign key over several columns is a table-level `foreignKeys` entry. The only place types and rules are defined. |
| `config/value_sets.yaml` | Named value lists that rules check against (`value_set:`): the dictionaries' codes that several columns share, such as `yes_no`, and open lists squads add to, such as `event_type`. See "Shared value lists". |
| `config/cohort_mapping.yaml` | Where each of the 85 cohort-file columns goes. |
| `config/course_mapping.yaml` | Where each of the 35 course-file columns goes. |
| `config/on_campus_housing_mapping.yaml` | Where the on-campus housing enrichment goes (`student_attribute`). |
| `config/institution_events_mapping.yaml` | Where the institution events enrichment goes (`institution_event`). |
| `normalized-data-model.mmd` | The ER diagram, in Mermaid. A picture of `destination_schema.yaml`; a test keeps the two in step. |
| `../data/raw/` | Not in this folder: the two mock Analysis-Ready Files are read where the repository keeps them. A test checks they're the files the mappings were written against. |
| `data/input/enrichment/` | The two example enrichment files. |
| `data/input/sample/` | The raw rows for the 10 sample students, in the same formats. |
| `data/output/sample/` | One CSV per table, built from `data/input/sample/` through the configs. |
| `src/sample/build_sample.py` | Rebuilds both sample folders. |
| `config/column_dictionary.yaml`, `src/dictionary/build.py` | What each normalized column means: one record per table and column the cohort or course file writes, with the ARF dictionary's description, codes and notes, and every source column with its [column_lookup.csv](../data/dictionaries/column_lookup.csv) text (the mock-data specifics). **Generated** from those files: edit them, then rebuild (see [Rebuild and test](#rebuild-and-test)). A test fails if it's stale. |
| `config/pipeline_example.yaml`, `config/example_*_mapping.yaml`, `data/input/enrichment/example_*.csv` | The worked example in [Load your own enrichment files](#load-your-own-enrichment-files). Made-up values, not data. |
| `config/data_fixes.yaml`, `src/fixer/fix.py` | The fixes for known mock-data bugs, and the Fixer that applies them to a run's mapped tables. |
| `sources/registration_holds/` | A draft source spec and synthetic sample for proposal [#19](https://github.com/devcolor/pdp-datathon-starter/issues/19) (on-demand ETL joins). Made-up values, not data. Not wired into the loader yet; #19's load command (match rate, duplicate keys, quarantine) is still open. |
| `src/mapper/map.py`, `src/pipeline/run.py` | The Mapper, which writes each run's mapped tables to `data/staging/<run id>/`, and the command that runs every step. See [The steps, and the staging area](#the-steps-and-the-staging-area). |
| `src/tables/files.py` | Writes and reads table files, one per table, as CSV or Parquet, so a table read back is exactly what was written. Parquet needs `pyarrow`, which is in [requirements.txt](../requirements.txt). |
| `src/generator/enrichment/on_campus_housing.py` | Generates the synthetic on-campus housing file. |
| `Taskfile.yml`, `docker-compose.yml`, `conftest.py` | The local tasks, the PostgreSQL server they start, and the test setting that makes a skipped PostgreSQL test fail when one is required. See [Run everything locally](#run-everything-locally-postgresql-included). |
| `src/rules/rules.py` | Reads and checks the configs, and applies them to one value. Also decides, from the schema, the order tables are filled in and which tables a row may leave out. Used by the validator, the table builder (so the loader and the sample builder) and the loader's database code. |
| `src/validator/validate.py` | The validator: checks a run's fixed tables, writes its report and failed records to `logs/` and the rows that pass to `validated/`. |
| `config/pipeline.yaml` | How a run goes: which source files it starts from and which database it writes. The source files are the Mapper's input; the loader reads only the run's `validated/` tables. |
| `src/loader/tables.py` | Builds every table in memory from a run's `validated/` tables. Used by the loader and the sample builder, so both build the same way. |
| `src/loader/backends.py` | Creates the tables from `destination_schema.yaml` in SQLite or PostgreSQL and writes the rows, in one transaction. |
| `src/loader/load.py` | The loader: validates, builds and loads, and writes a load report to `logs/`. |
| `pyproject.toml`, `pdp_model/` | The package other projects install to run the loader; see [Use the model from another project](#use-the-model-from-another-project). |
| `output/` | The SQLite database the loader writes, `output/pdp.sqlite`. Not committed. |
| `logs/` | One folder per validation run in `validation_report/` and `failed_records/`, and per load in `load_report/`, named by run id. Not committed. |

## The tables

| Table | One row per |
|---|---|
| `institution` | institution. The mock data has one placeholder. |
| `data_provider` | loaded file, found again by its SHA-256, with the file's `researchid` |
| `student` | student, with the demographics and parental education that don't change by cohort |
| `cohort_membership` | student and cohort, with everything the cohort file says about that cohort |
| `term` | academic year and term, plus one `UNKNOWN` term that sorts last |
| `course` | course prefix and number |
| `course_enrollment` | course-file row: a student in a course in a term |
| `student_attribute` | fact from an enrichment file about a student, optionally in a term |
| `institution_event` | event at an institution, such as a closure or a powwow |
| `load_run` | database: the one run that built it, with its start and end time, backend, report and staging paths, file format and credit cutoff |

## Three kinds of config, split by what they describe

| File | Says | Examples |
|---|---|---|
| `config/destination_schema.yaml` | **What a valid stored value looks like**, whichever file it came from. | type, can it be blank, keys, `default_value`, `unknown_value`, `rules` |
| Each mapping config (`config/*_mapping.yaml`) | **How one source file writes its values**, and where each column goes. | `format`, `missing_values`, `unknown_values`, `value_map`, `true_values`, `on_conflict` |
| `config/data_fixes.yaml` | **What we change in the mock data, and why**: each fix for a known mock-data bug, with a link to the bug and to the decision behind it, and a switch to turn it off. | `replace` or `number_format`, on a table and column |

So a squad adding an enrichment file writes only a mapping config, and touches `destination_schema.yaml` only to add a column. A fix acts on a stored table and column, whichever file wrote it, so the `Race` fix is written once for both Analysis-Ready Files. A team that needs different fixes copies `data_fixes.yaml` and names its copy in its pipeline settings (`fixes:`). Two files that write the same column can't disagree about what's valid, because the rule is written once.

## How a column moves from a file to a table

Follow `Number_of_Credits_Earned` from the course file:

```yaml
# config/course_mapping.yaml: how the course file writes it
- source: Number_of_Credits_Earned
  destination_table: course_enrollment
  destination_column: number_of_credits_earned
  missing_values: [.]          # this file writes "." for no value
  on_conflict: replace

# config/destination_schema.yaml: what a valid stored value is
course_enrollment:
  number_of_credits_earned:
    type: float
    nullable: true
    rules:
      - {minimum: 0, maximum: 20, severity: error}
      - {not_greater_than: number_of_credits_attempted, severity: error}
```

1. **Repair.** If the entry has a `value_map` and the value is in it, it's replaced: that's for a file that writes a value its own way. A fix for a known mock-data bug, such as the cut `Race` labels, isn't here; it's in `config/data_fixes.yaml` and applies after mapping.
2. **No value or unknown.**
   - A blank cell, or a code in `missing_values`, means **no value**. The column's `default_value` is stored, or blank.
   - A code in `unknown_values` means the file **doesn't know**. The column's `unknown_value` is stored: `UNKNOWN` for text columns, blank for numbers, dates and true/false columns.
3. **Type.** Anything else is converted to the schema's type, using `format` for dates and `true_values`/`false_values` for true/false. Here `3` becomes `3.0`. A value that won't convert fails.
4. **Rules.** The column's rules check real values only, not blanks, defaults or unknowns.
5. The value is written to `course_enrollment.number_of_credits_earned`.

The other parts of a mapping entry:
- **`on_conflict`** says what happens when the row already exists and already holds a value: `replace` overwrites it, `keep` leaves it, `append` keeps it and adds the new value. For example, the course file repeats each student's gender, which the cohort file already wrote, so that entry is `keep`.
- **`must_exist: true`** means the row must already have been written by another file in the same run. The course file's student and cohort must be in the cohort file.
- **`value:`** replaces `source:` when every row gets the same fixed value, such as `attribute_key: uses_on_campus_housing`.
- **`dropped:`** marks a source column with no destination, with the reason. No column is dropped today.

## Rule kinds

Each rule is one YAML map with one kind and a `severity`: `error` holds the row back, `warning` reports it and still loads it. Names follow [Frictionless Table Schema](https://specs.frictionlessdata.io/table-schema/) where it has one.

| Kind | Checks | Example |
|---|---|---|
| `enum` | one of a list | `{enum: [F, O, H], severity: error}` |
| `value_set` | one of a list in `config/value_sets.yaml` | `{value_set: yes_no, severity: error}` |
| `pattern` | the text matches a regular expression | `{pattern: '^[0-9]{6}$', severity: error}` |
| `minimum`, `maximum` | a number is in range (one rule can have both) | `{minimum: 0, maximum: 20, severity: error}` |
| `max_length` | text is at most this long | `{max_length: 20, severity: error}` |
| `not_before` | a date is on or after another column's | `{not_before: course_begin_date, severity: error}` |
| `not_greater_than` | a number is at most another column's | `{not_greater_than: number_of_credits_attempted, severity: error}` |
| `required_when` | the column has a value when another column equals a value (`equals: Y`), has one (`present: true`) or has none (`present: false`) | `{required_when: {column: core_course, equals: Y}, severity: error}` |
| `academic_year` | `YYYY-YY`, where the second year follows the first | `{academic_year: true, severity: error}` |

Options:
- `enum` and `value_set` take `ignore_case: true` and `ignore_spaces: true`.
- Any rule takes `when: {column: ..., equals: ...}` to apply only to some rows. `when` takes `present:` the same way `required_when` does. `student_attribute.attribute_value` uses it, because one column holds every attribute.
- Each kind's argument is checked when the configs load: `enum` is a list, `minimum` and `maximum` are numbers on an `int` or `float` column, `max_length` is a whole number, and `present` is `true` or `false`. `list_delimiter` is allowed only on a `str` column.
- Two-column rules name a column in the same table (`core_course`) or in another table filled from the same source row (`course.course_prefix`).
- A column can have an `error` rule and a `warning` rule. `institution_event.event_type` does: see "Shared value lists" below.

Whether a column can be blank, its type and its keys are never rules: they're already in the schema.

The rules the mock data breaks are `warning`, with a comment giving the number of rows, so squads get data while the questions to Dena (/dev/color) are open.

### Shared value lists

`config/value_sets.yaml` holds named lists. A rule checks a stored value against one with `value_set:`, for example `{value_set: yes_no, severity: error}`. Put a list there, instead of an `enum` in the rule, when several columns share it or when squads should be able to add values without editing the schema.

There are two kinds, and the rule's severity is what makes the difference:

| Kind | Lists | Severity | A value that isn't in the list |
|---|---|---|---|
| **Closed** | The codes a data dictionary defines: `yes_no`, `yes_no_na`, `placement`, `gateway_status`, `completed_c_d_na`, `count_0_to_7`, `locale`, `academic_term` | `error`, or `warning` for now where the mock data breaks it (see above) | The row is held back, or loads with a warning. Change the list only if a dictionary changes. |
| **Open** | `event_type` | `warning` | The row loads, and the run's report lists the value. Add it to the list once squads agree on it. |

For example, a squad bringing orientation events doesn't wait for anyone: `orientation` loads, with a warning. Once it's agreed, it's added in one line:

```yaml
event_type: [closure, ceremony, powwow, orientation]
```

`event_type` also has a format rule at `error`: lower-case words joined by underscores, such as `community_gathering`. So `Pow Wow`, `pow-wow` or a blank type is held back whatever the list says, and one kind of event can't end up spelled three ways.

Blanks and `UNKNOWN` are never checked against a list. Editing a list changes what's valid for every column that uses it; each list's comment in the file says which columns use it. An empty list, or a rule naming a list that doesn't exist, is rejected when the configs load.

**Keys and links between tables.** A source row can fill several tables at once. A course-file row finds its `term` and `course`, then writes a `course_enrollment` row that points at them. Rows are found by their natural key:
- `student`: `student_id`
- `cohort_membership`: student and cohort
- `term`: year and term
- `course`: prefix and number
- `course_enrollment`: the file plus its row number

Natural keys are only looked up or created, never overwritten, whatever their entry's `on_conflict` says.

A course enrollment also points at its cohort membership, on two columns: `student_id` and `cohort`. A foreign key over several columns can't sit on one column, so it's a table-level `foreignKeys` entry, in [Frictionless Table Schema](https://specs.frictionlessdata.io/table-schema/#foreign-keys)'s format. Its `reference` must name the other table's whole primary key, in order:

```yaml
course_enrollment:
  ...
  foreignKeys:
    - {fields: [student_id, cohort], reference: {resource: cohort_membership, fields: [student_id, cohort]}}
```

The database enforces it like every other key. One-column keys stay on their column (`foreign_key: student.student_id`).

## Things to know before you query

- **Join course enrollments to cohorts on `student_id` and `cohort`, not student alone.** 2 students are in two cohorts. `course_enrollment.cohort` says which one each course row belongs to, so the join gives one row per enrollment.
- **17,755 course-file rows have no course record.** On those rows the student was enrolled at another institution that term, or the term is unknown. They're kept, with a blank `course_id`, `section_id` and `attempt_number`.
- **456 course rows have no year or term.** They point at the one `UNKNOWN` term, which sorts last.
- **`attempt_number` counts retakes.** It's the order of a student's rows for the same course, by term.
- **`UNKNOWN` means the file said it doesn't know; blank means it said nothing.** In text columns, the codes the dictionaries define as unknown or missing (`UK`, `Unknown`, `-1` where it means unknown, `M = Missing`, `MISSING`) are stored as `UNKNOWN`. Codes the dictionaries don't define, such as Pell's `U`, stay as written and fail a `warning` rule. The cohort file writes `UNKNOWN` itself in `Credential_Type_Sought_Year_1` (395 rows); that's kept as unknown too. In number, date and true/false columns both are blank; the validator's summary counts them apart.
- **Some mock-data bugs are fixed before the rules check them**, as listed in [`config/data_fixes.yaml`](config/data_fixes.yaml): two `Race` labels the mock files cut at 25 characters are stored in full (2,023 rows across both files); `Math_or_English_Gateway`'s `NA` is stored as the dictionary's `N` (75,504 rows); each `Credential_Type_Sought_Year_1` label is stored as its dictionary code, such as `A` for "Associate's Degree" (9,678 rows; `Degree Seeking(N)` and `Degree Seeking(Y)` have no code and stay as written); codes a spreadsheet wrote as numbers get back the zeros that can only be read one way: `Course_CIP` such as 5.0202 is stored as 05.0202 (1,239 rows), three-decimal values such as 13.121 get a trailing zero (13.1210; 702 rows), 9.01 as 09.01 and 45.1 as 45.10 (332), and 1 as 01 (69); values such as 24, 24.01 or 09.01 may be a real CIP series or a longer code, so they still warn (2,276 rows), and a five-digit program of study such as 90702 as 090702 (96, 113 and 605 rows in `Program_of_Study_Term_1`, `Program_of_Study_Year_1` and `Term_Program_of_Study`); the developmental completion columns' Y and N are stored as the dictionary's C and D (969 math rows, 688 English); and credit years that hadn't happened yet are blank, not 0 (below). The validation report counts each fix's rows under `fixes`.
- **Each file's `Cohort_Term` is kept, in its own column.** `cohort_membership.cohort_term` is the cohort file's, which the dictionary defines as the term the student first enrolled. `course_enrollment.course_file_cohort_term` is the course file's, as it wrote it on each row. They differ on 4,307 of the 100,951 course rows; compare the two columns to find them.
- **Credit years after 2025-26 are blank, and `cohort_membership.credit_years_observed` says how many the data can see.** The mock data's course credits run to 2025-26, so a 2024-25 student's year 3 (2026-27) and year 4 (2027-28) hadn't happened; the files wrote 0 for them, which would read as no credits. Those zeros are stored blank: 2,520 in year 3 and 5,039 in year 4, in each of the attempted and earned columns. `credit_years_observed` is 4 for the 2021-22 and 2022-23 cohorts, 3 for 2023-24 and 2 for 2024-25. A blank credit year at or below it is missing; above it, the year hadn't happened. The cutoff is a working assumption, set in `config/data_fixes.yaml`; a value other than 0 after it is kept, and loads with a `warning` on its column in the validation report.
- **The mock data has no institution column.** Everything belongs to one placeholder institution, and the two example events come from two real colleges: Leech Lake Tribal College and United Tribes Technical College.
- **Some generated CSVs are committed, on purpose.** The repository's rule is not to commit generated outputs. The on-campus housing file is an input, and committing it means every squad loads the same one. The two sample folders are small (about 70 KB), and the tests compare a rebuild against them. The repository's `AGENTS.md` names these files as the exception.
- **On-campus housing is synthetic.** 30% of students, a 60% chance of staying each term, generated with a fixed seed.

## The steps, and the staging area

A run goes from the source files to the database in steps, and each step reads what the one before it wrote, from `data/staging/<run id>/`:

1. **Map** (`src/mapper/`): reads each source file through its mapping config and writes `mapped/<source file>/`: one file per table the source fills, with `source_row` (the row in the source file) first and then the table's mapped columns, plus `problems.csv` (values that aren't their column's type) and `source.yaml` (the file's SHA-256, row count, mapping config, mode, and the counts of repairs, unknowns and no-values).
2. **Fix** (`src/fixer/`): applies [`config/data_fixes.yaml`](config/data_fixes.yaml) to the mapped tables and writes `fixed/<source file>/`, the same layout plus `fixes.yaml`: the rows each fix changed, and any fix that changed nothing. It also keeps `fixed/sources.yaml`: every source in `mapped/`, with its mode, and the ones it has fixed.
3. **Validate** (`src/validator/`): checks the fixed values against the rules, writes its report under `logs/`, and writes the rows that pass to `validated/<source file>/`, with the source's `source.yaml` (plus where its report is, how many rows passed and failed, and each table file's SHA-256) and `fixes.yaml`.
4. **Load** (`src/loader/`): checks every table file in `validated/` against the SHA-256 in its `source.yaml`, then builds every table from `validated/` and loads it. If a file is changed, missing or added, the load stops with exit code 1 and the database keeps what it had. It reads nothing else: not `fixed/`, and not the source files.

One command runs them all and prints each step as it finishes, with the folder it read and wrote and its counts. If a step stops the run, the command exits with that step's own code and the load report's `failed_step` names it:

```bash
python3 -m src.pipeline.run                      # or ./scripts/run_pipeline.sh, or task load:sqlite
python3 -m src.pipeline.run --format parquet     # the staging area in Parquet instead of CSV
```

Each step also runs on its own, on a run's folder, which is how you check one step's output before the next. These are the commands the pipeline runs for `config/pipeline.yaml`. The loader always loads every source in its settings, so map all four into one run. Use the same run id in every command: any id that hasn't been used, such as `by-hand-1`, or leave `--run_id` off the first command and copy the one it prints.

```bash
# Map: the two Analysis-Ready Files together, then each enrichment file, into the same run.
python3 -m src.mapper.map --cohort ../data/raw/pdp_cohort_data.csv --course ../data/raw/pdp_course_data.csv \
    --cohort_config config/cohort_mapping.yaml --course_config config/course_mapping.yaml --run_id <run id>
python3 -m src.mapper.map --enrichment data/input/enrichment/on_campus_housing.csv \
    --enrichment_config config/on_campus_housing_mapping.yaml --run_id <run id>
python3 -m src.mapper.map --enrichment data/input/enrichment/institution_events.csv \
    --enrichment_config config/institution_events_mapping.yaml --run_id <run id>
# Fix every mapped source.
python3 -m src.fixer.fix --staging data/staging/<run id>
# Validate each mode on its own, each with its own report.
python3 -m src.validator.validate --staging data/staging/<run id> --sources pdp_cohort_data.csv,pdp_course_data.csv
python3 -m src.validator.validate --staging data/staging/<run id> --sources on_campus_housing.csv --run_id <run id>-on_campus_housing
python3 -m src.validator.validate --staging data/staging/<run id> --sources institution_events.csv --run_id <run id>-institution_events
# Load validated/.
python3 -m src.loader.load --staging data/staging/<run id>
```

The staging files are CSV unless `--format parquet` is given; a run's folder holds one format. Every run keeps its own folder, which git ignores. For the full mock data it's about 107 MB in CSV (36 MB for each of `mapped/`, `fixed/` and `validated/`), or 19 MB in Parquet. Nothing deletes old ones; remove them by hand. The whole run takes about 29 seconds in CSV and 25 in Parquet (measured on an Apple M3 Pro laptop with `/usr/bin/time`, 2026-10-29).

## Validate a run

```bash
python3 -m src.validator.validate --staging data/staging/<run id> --sources pdp_cohort_data.csv,pdp_course_data.csv
python3 -m src.validator.validate --staging data/staging/<run id> --sources on_campus_housing.csv --run_id <run id>-on_campus_housing
```

Give `--sources` for one mode at a time: the two Analysis-Ready Files together, or one enrichment file. Without it the validator checks every source in `fixed/`, which works only when they're all in one mode.

The validator reads only `fixed/`, so map and fix the files first (see [The steps, and the staging area](#the-steps-and-the-staging-area)), or let `python3 -m src.pipeline.run` run every step. It refuses a run the Fixer didn't write (a source folder with no `fixes.yaml`) and one it didn't finish (the cohort file fixed without the course file, as `fixed/sources.yaml` records). It checks each value as stored, so a repair or a fix is checked after it's made, and `failures.csv` shows the value it checked. It reads the source file to check it's still the file that was mapped (its SHA-256), before it writes anything, and again only when rows fail, to copy them unchanged into `failed_records/`.

Each run prints its run id, which is the run's, from its staging folder's name, such as `20261026T065015Z-e3f183` (the time the Mapper started, in UTC, plus 6 random characters), and writes:
- `logs/validation_report/<run id>/summary.yaml`: the input and config files with their SHA-256 checksums, rows read, passed and failed, repairs, unknowns and no-values per column, and `fixes`: the rows each fix changed in that file. `failures` lists each rule that failed, with its count, `field`, `source_column`, `why` (what the rule requires, in words) and `examples` (the first 5 rows and their values).
- `logs/validation_report/<run id>/failures.csv`: one line per failure, with its `failure_id`, file, row, column, the value checked, rule and severity. For an `error`, `failed_record` names the file in `failed_records/` that holds the row.
- `logs/failed_records/<run id>/<source file>.csv`: each held-back row, unchanged, after `run_id`, `source_row_number` and `failure_ids` (which point back at `failures.csv`).

In the enrichment mode foreign keys aren't checked, because the other files aren't in the run; the summary says so. The loader checks them. The command exits 0 when the run finishes, and 2 when a config is invalid or it refuses the run. `--config_dir`, `--logs_dir` and `--run_id` change the defaults.

Before reading any data, a run stops if its run id already has a report, so an earlier run's report and failed records are never overwritten. It also stops if the cohort and course files have the same name, because the report and failed records name each file by its name.

A source row can leave a table out only when its whole key is blank and the schema allows it: every foreign key pointing at that table, from the row's other tables, can be blank. In the course file that's `course`, for the rows with no course record (`course_enrollment.course_id` is blank). In the housing file it's `term` (`student_attribute.term_id` can be blank). A blank key on any other table, such as a cohort row with no `Student_GUID` or `Cohort`, fails that table's required columns.

## Load the data

The loader builds every table from the two Analysis-Ready Files and the two enrichment files, and writes them to SQLite or PostgreSQL. **The data is synthetic**: nothing you query here is a finding about real students or a real institution.

### Install

From the repository root, once:

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
```

### SQLite

Nothing to set up. From `normalized-data-model/`:

```bash
python -m src.loader.load
```

This runs [every step](#the-steps-and-the-staging-area) and writes `output/pdp.sqlite` (about 25 MB) in about 30 seconds and prints the rows in each table. **Every load also writes each table as one file to `output/tables/`**, for squads that don't use a database: CSV, with the same headers and formats as `data/output/sample/`, or Parquet with `--format parquet`. Open it with any SQLite tool, for example `sqlite3 output/pdp.sqlite`. `--sqlite_path` writes it somewhere else.

### PostgreSQL

Create an empty database, put its connection URL in `PDP_POSTGRES_URL`, and load:

```bash
createdb pdp
export PDP_POSTGRES_URL=postgresql://user:password@localhost:5432/pdp
python -m src.loader.load --backend postgres
```

The tables go in the connection's default schema, usually `public`. To use another schema, add `?options=-csearch_path%3Dmy_schema` to the URL. The URL is read only from the environment, so a password never goes in a committed file. Keep it in your shell or in a `.env` file, which git ignores.

### Settings

`config/pipeline.yaml` holds the settings. What the tables are and where each column goes stays in `destination_schema.yaml` and the mapping configs; the loader reads those as they are.

| Setting | Default | What it does | Flag |
|---|---|---|---|
| `mode` | `full_refresh` | The only mode. Every load replaces the model's tables. | |
| `backend` | `sqlite` | `sqlite` or `postgres`. | `--backend` |
| `sqlite.path` | `output/pdp.sqlite` | Where the SQLite database goes. | `--sqlite_path` |
| `tables.path` | `output/tables` | Where each loaded table is written as a file. The format is `--format`, CSV by default. | `--tables_dir` |
| `postgres.url_env` | `PDP_POSTGRES_URL` | The name of the environment variable that holds the connection URL. | |
| `on_error_rows` | `skip` | `skip` holds back rows that break an `error` rule and loads the rest. `fail` stops before touching the database if any row does, including in a run loaded with `--staging`, whose `validated/` folders say how many rows failed. | |
| `batch_size` | `5000` | Rows per insert. | |
| `logs_dir` | `logs` | Where validation and load reports go. | |
| `staging_dir` | `data/staging` | Where each run's mapped, fixed and validated tables go. | |
| `fixes` | `config/data_fixes.yaml` | The fixes for known mock-data bugs. A team can name its own copy. | |
| `sources` | the 4 files | Each file's `kind` (`cohort`, `course` or `enrichment`), `path`, mapping `config` and `provider`, in load order. `path` is the file as it came in, which the Mapper reads, not the validator's output: the run's folder doesn't exist until the run starts, so the loader finds each source's tables at `validated/<the path's file name>/`. A source may add `order_by`: a column, such as `cohort_membership.cohort`, by which the later row wins. It must sort as a year or a number, not as text. | `--cohort`, `--course` |

Paths in the file are relative to `normalized-data-model/`, and paths given as flags are relative to the folder you run from. `scripts/run_pipeline.sh` runs from `normalized-data-model/`, so give it paths from there, or absolute ones. Each source's `config` names a mapping config in `config/`. `--config` reads another settings file, and `--run_id` names the run. A bad setting, such as a missing file, an unknown backend or an unset `PDP_POSTGRES_URL`, stops the loader before anything is read or written, with exit code 2.

### What a load does

1. **Maps, fixes and validates** the files ([the steps](#the-steps-and-the-staging-area)): the cohort and course files together, then each enrichment file, through `data/staging/<run id>/`. With `--staging data/staging/<run id>` it skips this and loads that run's `validated/` tables. Each writes its report to `logs/validation_report/<run id>/`, and the enrichment runs add the file name to the run id, such as `<run id>-on_campus_housing`.
2. **Holds back** rows that break an `error` rule (they go to `logs/failed_records/`). Rows that break only `warning` rules load. A course row whose student was held back is held back too.
3. **Builds** every table from `validated/`, the same way the samples are built. A student in two cohorts gets one `student` row and two `cohort_membership` rows. `on_conflict` decides which file's value wins, with two rules on top, whatever it says: a blank never overwrites a value that's already stored, and between a student's two cohort rows the later cohort's values win, whatever order the rows are in (the cohort source's `order_by: cohort_membership.cohort`), even a later cohort's `UNKNOWN`. Any other `UNKNOWN`, such as an enrichment's, never overwrites a stored value. The load report counts each under `collisions`, as `unknown not written` and `replace, earlier row kept`.
4. **Checks references** the validator can't. An enrichment row whose student isn't in the load is held back and listed in the load report, under `held_back`.
5. **Replaces** the model's tables in one transaction: drop, create from `destination_schema.yaml` (types, NOT NULL, primary, unique and foreign keys), insert, commit. If anything fails, it rolls back and **the database keeps what it had before**. The command exits 1 and prints the error.
6. **Writes the table files** to `output/tables/`, after the commit, into a folder next to it that's then swapped in. So the files always match the committed database, and a failed load, or a failed write, leaves the last ones in place. If the database commits but the files can't be written, the report says `loaded, tables not written` and the command exits 1.
7. **Reports** to `logs/load_report/<run id>/summary.yaml`, whether the load worked or not: each file's rows read, passed and held back, the rows held back for a missing reference, the on-conflict collisions, the rows per table, and the error if it failed.

The source files are only read: by the Mapper; by the validator, to check them and to copy failed rows; and before a full run starts, to check no two sources are the same file. `python -m src.loader.load --staging <run>` loads a run's `validated/` tables and reads nothing else, so it doesn't take `--cohort` or `--course`. Each load records every source file in `data_provider`, as its `source.yaml` describes it, with its SHA-256, row count and load time (UTC). Each `course_enrollment` row points back to its file and row number (`provider_id`, `source_row_number`).

A full refresh also drops rows you added to the model's tables by hand. Put your own data in your own tables, or in an enrichment file with a mapping config so it loads every time. If one of your tables has a foreign key to a model table, the load stops before dropping anything and names it, in both databases, because dropping the model's tables would delete or change your rows. In PostgreSQL a view on a model table stops it too. Drop the foreign key or view, load, and add it again. A SQLite view needs nothing: it works again once the load finishes.

### Check what loaded

On the full mock data every row passes validation (with warnings), and a load gives:

| Table | Rows | Why that many |
|---|---:|---|
| `institution` | 1 | the placeholder |
| `data_provider` | 4 | one per file read |
| `student` | 10,311 | distinct `Student_GUID` in the cohort file's 10,313 rows: 2 students are in two cohorts |
| `cohort_membership` | 10,313 | one per cohort-file row |
| `term` | 44 | distinct year and term in the course and housing files, plus `UNKNOWN` |
| `course` | 9,876 | distinct prefix and number. 17,755 course rows have none. |
| `course_enrollment` | 100,951 | one per course-file row. Student, course and term aren't unique: there are 98,865 distinct combinations. |
| `student_attribute` | 8,106 | one per housing-file row |
| `institution_event` | 2 | one per events-file row |
| `load_run` | 1 | the run that built the database |

**Which run built this database**, and where its reports are:

```sql
SELECT run_id, started_at, backend, load_report, validation_reports, staging_folder, file_format, credit_cutoff
FROM load_run;
```

The paths are from `normalized-data-model/` on the machine that ran the load. In a database copied to another machine they name files that aren't there; the run id still finds them where the load ran. `started_at` is the same moment as every `data_provider.loaded_at`; `finished_at` is when the rows were written, just before the commit. A full refresh rebuilds every table, so **every row in the database belongs to this one run**: no table needs a key pointing at `load_run`. Its file format, credit cutoff and validation reports are read from the run's `validated/` folder, so they say what the run did, even for a run loaded with `--staging`.

`load_run.build_manifest` is nullable versioned JSON containing a fresh load generation, pipeline version and normalization digest. New map/fix/validate stages retain the code and configuration identities actually used; the loader includes those staged identities and its own rules, then commits the manifest atomically with the normalized rows. Older staged artifacts and fixed sample outputs leave this field blank: v1 reads remain supported, while v2 snapshot/replay requires a complete pipeline rebuild. See the [snapshot guide](../docs/analysis-v2-snapshots.md) for the identity and transaction contract.

To check the counts and the links between tables yourself, in SQLite or PostgreSQL:

```sql
SELECT 'student', COUNT(*) FROM student
UNION ALL SELECT 'cohort_membership', COUNT(*) FROM cohort_membership
UNION ALL SELECT 'course_enrollment', COUNT(*) FROM course_enrollment;

-- Each should be 0: every row points at a row that exists.
SELECT COUNT(*) FROM course_enrollment e LEFT JOIN student s ON s.student_id = e.student_id WHERE s.student_id IS NULL;
SELECT COUNT(*) FROM course_enrollment e LEFT JOIN term t ON t.term_id = e.term_id WHERE t.term_id IS NULL;
SELECT COUNT(*) FROM course_enrollment e LEFT JOIN course c ON c.course_id = e.course_id
 WHERE e.course_id IS NOT NULL AND c.course_id IS NULL;
```

In SQLite, `PRAGMA foreign_key_check;` lists any row whose foreign key doesn't resolve, for every table at once.

### #8's gateway question, in one join

Proposal [#8](https://github.com/devcolor/pdp-datathon-starter/issues/8) asks for the gateway course pass rate by gender for the 2022-23 cohort, with one join. The cohort file already says, for each student, whether they completed gateway math and English in year 1: `completed_gateway_math_year1` and `completed_gateway_english_year1`, which the [cohort data dictionary](../data/dictionaries/arf_cohort_data_dictionary.md) defines "for students who are required to take gateway math" (and English). `C` is completed, `D` didn't complete, and `NA` or blank is not required. So the rate here is `C` out of `C` and `D`: the dictionary's own scope, not a new definition. How the shared measures are calculated belongs to proposal [#9](https://github.com/devcolor/pdp-datathon-starter/issues/9).

<!-- gateway-query: a test runs this SQL on a full load and checks it against the raw cohort file -->
```sql
SELECT s.gender,
       SUM(CASE WHEN m.completed_gateway_math_year1 = 'C' THEN 1 ELSE 0 END) AS math_completed,
       SUM(CASE WHEN m.completed_gateway_math_year1 IN ('C', 'D') THEN 1 ELSE 0 END) AS math_required,
       ROUND(100.0 * SUM(CASE WHEN m.completed_gateway_math_year1 = 'C' THEN 1 ELSE 0 END)
             / NULLIF(SUM(CASE WHEN m.completed_gateway_math_year1 IN ('C', 'D') THEN 1 ELSE 0 END), 0), 1) AS math_rate,
       SUM(CASE WHEN m.completed_gateway_english_year1 = 'C' THEN 1 ELSE 0 END) AS english_completed,
       SUM(CASE WHEN m.completed_gateway_english_year1 IN ('C', 'D') THEN 1 ELSE 0 END) AS english_required,
       ROUND(100.0 * SUM(CASE WHEN m.completed_gateway_english_year1 = 'C' THEN 1 ELSE 0 END)
             / NULLIF(SUM(CASE WHEN m.completed_gateway_english_year1 IN ('C', 'D') THEN 1 ELSE 0 END), 0), 1) AS english_rate
FROM cohort_membership m
JOIN student s ON s.student_id = m.student_id
WHERE m.cohort = '2022-23'
GROUP BY s.gender
ORDER BY s.gender;
```

It's the same SQL in SQLite and PostgreSQL. On the full mock data it gives, for math, `F` 162 of 620 (26.1%), `M` 116 of 456 (25.4%), `UNKNOWN` 25 of 72 (34.7%) and `X` 1 of 1; for English, `F` 311 of 682 (45.6%), `M` 208 of 510 (40.8%), `UNKNOWN` 21 of 68 (30.9%) and `X` 0 of 1. The data is synthetic, so these aren't findings.

**A course-level example: it counts attempts, not students.** The course file's grades give another view, one row per gateway course a student took. What counts as a pass there is an assumption, not an agreed definition: `P`, or a grade of 2.0 or higher on the 4-point scale. Proposal [#9](https://github.com/devcolor/pdp-datathon-starter/issues/9) owns the shared definition. A course row reaches its cohort on `student_id` and `cohort`, so a student who's in two cohorts is counted in the right one.

```sql
SELECT s.gender,
       COUNT(*) AS gateway_attempts,
       SUM(CASE WHEN e.grade IN ('P', '2', '2.3', '2.5', '2.6', '2.7', '3', '3.3', '3.5', '3.6', '3.7', '4')
                THEN 1 ELSE 0 END) AS passed
FROM course_enrollment e
JOIN cohort_membership m ON m.student_id = e.student_id AND m.cohort = e.cohort
JOIN student s ON s.student_id = e.student_id
WHERE m.cohort = '2022-23'
  AND e.math_or_english_gateway IN ('M', 'E')
GROUP BY s.gender
ORDER BY s.gender;
```

Each retake is its own row. Use `attempt_number = 1` for first attempts only.

### Known limitations

- **Full refresh only.** There's no incremental load: every load rebuilds every table, which takes about 30 seconds in SQLite.
- **Everything is built in memory** before it's written. The full mock data needs about 650 MB of memory at its peak.
- **`append` behaves like `keep`.** No mapping uses it yet. Where an appended value would be stored is still to be decided.
- **No DuckDB.** The loaded tables are also written as CSV or Parquet files (`output/tables/`), which DuckDB reads directly, but there's no DuckDB backend.
- **Old staging folders aren't deleted.** Each run keeps `data/staging/<run id>/`; remove old ones by hand.
- **The financial aid file** isn't in the mock data and isn't loaded.

### Use the model from another project

Another Python project can run the loader, without copying it, through the `pdp_model` package in this folder. The Playground's `/sandbox/pipeline` endpoints do this. Install this folder **editable**, because the loader reads `config/` and writes `data/staging/`, `logs/` and `output/` here, next to its code:

```bash
pip install -e normalized-data-model            # add [postgres] for the PostgreSQL backend
# or, in a uv project: pdp-normalized-data-model = { path = "../normalized-data-model", editable = true }
```

```python
import pdp_model

pdp_model.table_names()             # the 10 tables, in the order the loader fills them
pdp_model.expected_columns("course")  # the columns the course file's mapping config reads
pdp_model.column_dictionary()       # what each normalized column means, from config/column_dictionary.yaml
pdp_model.schema_field("student", "gender")  # how it's stored: type, nullable, unknown_value, allowed_values
run_id = pdp_model.new_run_id()
summary = pdp_model.run_load("sqlite:///my.db", run_id, cohort="my_cohort.csv", tables_dir="out/tables")
```

`run_load` takes a SQLAlchemy-style URL (`sqlite:///...` or `postgresql://...`, async drivers allowed), runs every step, and returns the load summary. It raises `pdp_model.ConfigError` for a bad setting or URL and `RuntimeError` for a failed load; `pdp_model.load_report(run_id)` reads the run's `summary.yaml` either way. Pass `tables_dir` so your loads don't overwrite `output/tables/`, which other squads read. Import from `pdp_model` only: `src/` is the pipeline's inside and can change.

## Load your own enrichment files

A team adds its own data to the model as enrichment files: a CSV and a mapping config each. Two things to know first.

**Every load is a full refresh.** The loader drops and rebuilds every table in the model from every source in its settings file, the cohort and course files always included, in one transaction. Rows you add to the model's tables by hand are gone after the next load. Your own data belongs in an enrichment file, so it loads every time, or in tables of your own. A full load takes about 30 seconds.

**One load takes any number of enrichment files, each with its own mapping config.** Copy `config/pipeline.yaml`, add each file to its `sources` with its own mapping config and `provider`, and load with `--config`. Give your copy its own `sqlite.path` and `tables.path` too, so your load gets a database and table files of its own instead of replacing the default ones. The rules:
- Mapping configs live in [`config/`](config/), next to the others, and are checked like them. Each source's `config` is a file name there; a path stops the load (exit code 2).
- No two sources can share a file name, or the same contents.
- Sources go in the order cohort, course, then your enrichment files. A settings file in another order stops the load (exit code 2), because the course file is checked against the cohort file.
- When two enrichments write the same row and column, the later source's `on_conflict` decides, and a blank or `UNKNOWN` never overwrites a stored value. In `student_attribute` each fact is a row of its own (its key includes the value and its source), so two files that disagree about a student both keep their row; pick between them in your query.
- A row about a student who isn't in the cohort file is held back, and listed in the load report under `held_back`.
- A mapping can't write a table the loader fills itself (`load_run`), or one that isn't in `destination_schema.yaml`: the load stops (exit code 2). Both this and the order are checked with the settings, before any step runs.
- A new table needs only its entry in `destination_schema.yaml`: the loader fills it, after the tables it points at.

### A worked example

Two example files: one new fact about students (whether they commute more than 30 minutes, for 5 real mock students) and one new event (an orientation). All five files are committed, so you can run it as it is.

The student file, `data/input/enrichment/example_commute.csv`, and its mapping config. Each row becomes a `student_attribute` row, with the fixed key `commutes_over_30_minutes`:

<!-- example-file: data/input/enrichment/example_commute.csv -->
```csv
Student_GUID,Commutes_Over_30_Minutes,Source
006F3FF4E1F908EFE0535964C70A009A,true,example: made up for the README
0110949EC5F26B13E0531B64C70A9D19,false,example: made up for the README
01F160D873EE37A2E0634F0F210ABB0B,true,example: made up for the README
1009F9D5EC88516FE063630F210A58BC,false,example: made up for the README
32C0776F4C49F685E0634F0F210A158C,true,example: made up for the README
```

<!-- example-file: config/example_commute_mapping.yaml -->
```yaml
# How the commute example file writes its values, and where each column goes: an example for
# teams, shown in the README's "Load your own enrichment files". What a valid stored value looks like
# (types, allowed values, ranges) is NOT here: it's in config/destination_schema.yaml, the same for
# every file that writes the column.
#
# Each entry: source (or value, a fixed value for every row), destination_table,
# destination_column and on_conflict (append, replace or keep: what the loader does when the
# destination row already holds a value).

- value: commutes_over_30_minutes
  destination_table: student_attribute
  destination_column: attribute_key
  on_conflict: replace

- source: Student_GUID
  destination_table: student_attribute
  destination_column: student_id
  on_conflict: replace

- source: Commutes_Over_30_Minutes
  destination_table: student_attribute
  destination_column: attribute_value
  on_conflict: replace

- source: Source
  destination_table: student_attribute
  destination_column: source
  on_conflict: replace
```

The event file, `data/input/enrichment/example_orientation.csv`, and its mapping config. Each row becomes an `institution_event` row, at the placeholder institution:

<!-- example-file: data/input/enrichment/example_orientation.csv -->
```csv
Event_Type,Event_Name,Start_Date,End_Date,Source
orientation,New student orientation,20250825,20250825,example: made up for the README
```

<!-- example-file: config/example_orientation_mapping.yaml -->
```yaml
# How the orientation example file writes its values, and where each column goes: an example for
# teams, shown in the README's "Load your own enrichment files". What a valid stored value looks like
# (types, allowed values, ranges) is NOT here: it's in config/destination_schema.yaml, the same for
# every file that writes the column.
#
# Each entry: source (or value, a fixed value for every row), destination_table,
# destination_column and on_conflict (append, replace or keep: what the loader does when the
# destination row already holds a value).

- value: 1
  destination_table: institution_event
  destination_column: institution_id
  on_conflict: replace

- source: Event_Type
  destination_table: institution_event
  destination_column: event_type
  on_conflict: replace

- source: Event_Name
  destination_table: institution_event
  destination_column: name
  on_conflict: replace

- source: Start_Date
  destination_table: institution_event
  destination_column: start_date
  format: '%Y%m%d'
  on_conflict: replace

- source: End_Date
  destination_table: institution_event
  destination_column: end_date
  format: '%Y%m%d'
  on_conflict: replace

- source: Source
  destination_table: institution_event
  destination_column: source
  on_conflict: replace
```

The settings, [`config/pipeline_example.yaml`](config/pipeline_example.yaml): a copy of `config/pipeline.yaml` with a database and table files of its own,

```yaml
sqlite:
  path: output/example.sqlite
tables:
  path: output/example_tables
```

and these two sources added at the end:

```yaml
  - kind: enrichment
    path: data/input/enrichment/example_commute.csv
    config: example_commute_mapping.yaml
    provider: 'example: commute survey'
  - kind: enrichment
    path: data/input/enrichment/example_orientation.csv
    config: example_orientation_mapping.yaml
    provider: 'example: orientation calendar'
```

Load:

```bash
python3 -m src.pipeline.run --config config/pipeline_example.yaml
```

It writes `output/example.sqlite` and `output/example_tables/`, so the queries below run on `output/example.sqlite`.

`orientation` isn't in the `event_type` list in `config/value_sets.yaml` yet. The event still loads, and its validation report lists a `warning` for `institution_event.event_type`. To add the type, change that one line to `event_type: [closure, ceremony, powwow, orientation]`.

Then join the new facts to the Analysis-Ready File columns:

<!-- example-query: a test runs this on the example load -->
```sql
SELECT a.student_id, a.attribute_value AS commutes_over_30_minutes, s.gender, m.cohort, m.credential_type_sought_year_1
FROM student_attribute a
JOIN student s ON s.student_id = a.student_id
JOIN cohort_membership m ON m.student_id = a.student_id
WHERE a.attribute_key = 'commutes_over_30_minutes'
ORDER BY a.student_id, m.cohort;
```

The orientation has no student, so it doesn't join to those columns. It belongs to an institution, here the placeholder one, and its `source` says where it came from:

<!-- example-event-query: a test runs this on the example load -->
```sql
SELECT e.event_type, e.name, e.start_date, i.name AS institution, i.is_placeholder, e.source
FROM institution_event e
JOIN institution i ON i.institution_id = e.institution_id
WHERE e.event_type = 'orientation';
```

## Rebuild and test

Run from this folder:

```bash
python3 -m src.generator.enrichment.on_campus_housing   # data/input/enrichment/on_campus_housing.csv
python3 -m src.sample.build_sample                       # data/input/sample/ and data/output/sample/
python3 -m src.dictionary.build                          # config/column_dictionary.yaml, after a dictionary or lookup change
./scripts/test_config.sh                                 # configs, schema, rule format and ER diagram, including its relationships
./scripts/test_rules.sh                                  # the rules module
./scripts/test_validator.sh                              # the validator, including the full mock data
./scripts/test_sample.sh                                 # sample builder and samples
./scripts/test_dictionary.sh                             # column dictionary builder, and that the committed file is current
./scripts/test_generator.sh                              # on-campus housing generator
./scripts/test_loader.sh                                 # the loader, including the full mock data
./scripts/test_tables.sh                                 # writing and reading table files, CSV and Parquet
./scripts/test_mapper.sh                                 # the Mapper and the staging area
./scripts/test_fixer.sh                                  # the Fixer and the fixes file
./scripts/test_pipeline.sh                               # every step, end to end, and a failing step's exit code
```

Requires Python 3.10 or newer and the packages in the repository's [requirements.txt](../requirements.txt). From the repository root, `make check` runs the data check and all of these tests; CI runs the same tests on every pull request, the fast and slow ones on separate machines. `make check-fast` leaves out the tests marked `slow`, so use it while you work and `make check` before you push.

A test that runs on the full mock data takes tens of seconds, so give it `@pytest.mark.slow`.

The loader's PostgreSQL tests run only when `PDP_TEST_POSTGRES_URL` holds a connection URL; otherwise they skip. Each test creates its own schema in that database and drops it afterwards. CI starts a PostgreSQL server and sets `PDP_REQUIRE_POSTGRES=1`, so in CI a PostgreSQL test that skips fails. The tests marked `postgres` are the ones that need it.

### Run everything locally, PostgreSQL included

The tasks in [`Taskfile.yml`](Taskfile.yml) start a PostgreSQL server in Docker and run every test against it, the same way CI does. You need [Task](https://taskfile.dev/installation/) (`brew install go-task` on macOS) and [Docker Desktop](https://docs.docker.com/get-started/get-docker/), running. Then, from this folder:

```bash
task setup          # once: ../.venv with the packages in requirements.txt
task check          # starts PostgreSQL, then runs make check as CI does; a skipped PostgreSQL test fails
task check:fast     # the same without the tests marked slow, for while you work
task --list         # every task and what it does
```

| Task | What it does |
|---|---|
| `task db:up` | Starts PostgreSQL 18 in Docker ([`docker-compose.yml`](docker-compose.yml)) on port 5434, and waits until it's ready. If Docker isn't running, it says so and stops. |
| `task db:down` | Stops it. Its data is kept. |
| `task db:reset` | Deletes its data and starts it again, empty. |
| `task check:fast` | The same as `task check`, without the tests marked `slow`. |
| `task test` | Every test, with SQLite only. The PostgreSQL tests skip. |
| `task test:postgres` | Starts PostgreSQL and runs only the PostgreSQL tests. One that skips fails. |
| `task load:sqlite`, `task load:postgres` | Map, validate and load the full mock data into SQLite or into the PostgreSQL server above, through `data/staging/`. Add `-- --format parquet` for a Parquet staging area. |
| `task test:config`, `test:rules`, `test:validator`, `test:sample`, `test:generator`, `test:loader`, `test:tables`, `test:mapper`, `test:fixer`, `test:pipeline` | One module's tests, through its script in [`scripts/`](scripts/). |

The database uses the local test user, password and database `pdp`, at `postgresql://pdp:pdp@localhost:5434/pdp`, and only this computer can connect to it. It's on port 5434 so it can run next to the playground's database, which uses 5433. The playground keeps its own tasks, in [`playground/mise.toml`](../playground/mise.toml).
