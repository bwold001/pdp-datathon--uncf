# Success measures

The [v2 catalog and adapter guide](../docs/analysis-v2-defined-operations.md) explains `requests.py`,
`registry.py` and `service.py`: pure request validation and dispatch to existing calculation owners on
a caller-owned snapshot, preserving gateway definitions, fractional credit numerators and DFW enrollment counts.

The shared shape for the core student success measures ([#9](https://github.com/devcolor/pdp-datathon-starter/issues/9)).
This folder holds the contract and the calculations for retention, federal (fall to fall) retention, persistence, gateway completion, DFW rate and credit completion, plus the Explorer pages' breakdowns ([breakdowns/](breakdowns/)).

The measures are retention, federal retention, persistence, gateway completion (math and English, one measure each), DFW rate and credit completion.

A measure reads tables from the [#8 data model](https://github.com/devcolor/pdp-datathon-starter/issues/8)
and returns result rows. No files are read or written. Each institution runs this on its own data.

## A result row: `MeasureResult`

[models.py](models.py). One row per measure, cohort and group. Python 3.10 or newer, standard
library only. `measures/` is a Python package, so other code imports it with
`from measures.models import ...` and `from measures.run_measures import run_measure`.

| Field | Meaning |
| --- | --- |
| `measure` | A `Measure`: `retention`, `persistence`, `gateway_math`, `gateway_english`, `dfw_rate` or `credit_completion` |
| `cohort` | A `Cohort`: one year, e.g. `2023-24`, or several pooled, e.g. `2021-22 + 2022-23` |
| `group` | A `Group`: which students the row is about. One condition or several. See below |
| `numerator`, `denominator`, `metric_rate` | The counts, and `numerator / denominator`. None if hidden. For `credit_completion` the numerator adds up student ratios, so it can have decimals |
| `status` | `ok`, `suppressed` (no eligible students) or `not_yet_observable` (nobody in the cohort has an answer yet) |
| `suppressed` | A property, not a stored field: true whenever the status isn't `ok`, so the numbers are hidden |
| `n_excluded` | Students the measure applies to but we couldn't count (course enrollments for `dfw_rate`) |
| `exclusions` | The same students (enrollments for `dfw_rate`) split by reason: a count for each `ExclusionReason`, adding up to `n_excluded`. Retention and persistence have one reason (`unknown_outcome`), gateway has one (`unknown_requirement_or_outcome`), and DFW and credit completion can have several. Empty when nothing was left out or the row is hidden |
| `exclusion_reason` | The reason with the most students (or enrollments) left out, or none. For one reason it is that reason |
| `n_out_of_scope` | Students the measure doesn't apply to, such as students not required to take a gateway course. They are not in `n_excluded` |
| `note` | One sentence: who was counted and how |

## Groups

A `Group` is a set of conditions that all apply at once. Each condition is a `GroupDimension` (a
way to split students) and one of its values, e.g. `Group.of((PELL, "Y"))`.

- One condition is a simple group: `pell = Y`.
- Several make a combination: `Group.of((PELL, "Y"), (GENDER, "F"))` is Pell students who are female.
  Order doesn't matter, and a dimension can be used only once.
- No conditions is `EVERYONE`.

To ask for groups, pass `group_by` a list of `GroupBy`. `GroupBy.of(RACE)` gives the race groups, and
`GroupBy.of(PELL, ENROLLMENT_INTENSITY)` gives every Pell × intensity combination.

The values are the PDP dictionary's, plus `UNKNOWN`. A student whose value is blank, or isn't on the list,
counts in the `UNKNOWN` group, so the groups of one dimension always add up to everyone. A value
outside the list can't be built into a `Group`.

| Dimension | Values |
| --- | --- |
| `race` | the 8 PDP race values, e.g. `White`, `Two or More Races`, and `UNKNOWN` |
| `ethnicity` | `H`, `N`, `UNKNOWN` |
| `gender` | `M`, `F`, `P`, `X`, `UNKNOWN` |
| `first_gen` | `N`, `P`, `C`, `A`, `B`, `E`, `UNKNOWN` |
| `pell` | `Y`, `N`, `UNKNOWN` |
| `age_band` | `20 and younger`, `> 20-24`, `Older than 24`, `UNKNOWN` |
| `enrollment_type` | `First-time`, `Re-admit`, `Transfer-in`, `UNKNOWN` |
| `enrollment_intensity` | `Full-time`, `Part-time`, `UNKNOWN` |
| `cohort_term` | `Fall`, `Winter`, `Spring`, `Summer`, `UNKNOWN`: the term the student started in |
| `course` | `dfw_rate` only. The values come from the data: the course prefix and number, such as `ENGL 1302` |
| `term` | `dfw_rate` only. The season the course was taken, from the data: `FALL`, `WINTER`, `SPRING`, `SUMMER` |
| `delivery` | `dfw_rate` only. How the course was taught, from the data: `F`, `H`, `O` or `UNKNOWN` |

Adding a breakdown means adding a dimension and its values in [models.py](models.py).

## Rules

A row that breaks these can't be built:

- A hidden group has None for counts, `metric_rate`, `n_excluded` and `n_out_of_scope`. Never 0, never a label like `<10`, so
  Excel, Power BI and pandas read the numbers as numbers.
- A shown group always has counts and a `metric_rate`.
- No two rows for the same measure, cohort and group (`check_unique`).

Every nonempty group is visible, including one student. Empty or unobservable populations retain
null rates and their existing statuses. No minimum-size privacy protection is applied.

## How each measure is calculated

Retention, persistence and the gateway measures count students with a yes or no answer. DFW rate counts
course enrollments. Credit completion averages each student's ratio. The rate is `numerator / denominator`, rounded to 4 places.

| Measure | Counts as achieved | Counted in the denominator | Left out |
| --- | --- | --- | --- |
| `retention` | `retention` is true | `retention` is true or false | blank answer: `n_excluded`, reason `unknown_outcome` |
| `federal_retention` | took a course here in the fall after year 1 (fall to fall) | every student, once that fall is in the course file | no answers until that fall is in the data: `not_yet_observable`. First time only and credentials counting are settings in [federal_retention.py](calculations/federal_retention.py), both off |
| `persistence` | `persistence` is true | `persistence` is true or false | blank answer: `n_excluded`, reason `unknown_outcome` |
| `gateway_math`, `gateway_english` | the year 1 completed flag is `C` | the flag is `C` or `D` | not required (status `N`): `n_out_of_scope`, outside the measure. Requirement or outcome unknown: `n_excluded`, reason `unknown_requirement_or_outcome` |
| `dfw_rate` | the grade is a D, F or withdrawal | the grade is one we can classify (see below) | any other grade: `n_excluded`, with the reason in the grade table below |
| `credit_completion` | the student's own ratio, credits earned / credits attempted in year 1 (added up) | first-time and transfer-in students with at least 1 credit attempted and a known full- or part-time status | no credits recorded: `unknown_outcome`. Under 1 attempted: `no_credits_attempted`. Enrollment type unknown: `unknown_enrollment_type`. Full- or part-time unknown: `unknown_attendance_type`. Re-admit and continuing students: `n_out_of_scope` |

- **Small groups:** every group with an eligible known outcome is shown. The compatibility helper
  `min_students()` always returns 1; `UNCF_MIN_STUDENTS` is ignored. Empty groups have no rate.
  A cohort is `not_yet_observable` when it has no observed outcomes; pooling preserves that rule.
- **Group values** are matched ignoring case and spaces, because the data model keeps the source file's
  spelling.

**Retention** means enrolled again in the next academic year, or earned a credential by then. A student who started in Fall 2023 and one who started in Spring 2024 are both in the 2023-24 cohort, and both are checked against 2024-25. The fall starter has about a year to return, and the spring starter has about five months. The group's rate is a blend, so spring starters tend to pull it down. Add `cohort_term` to `group_by` to compare them.

**Persistence** means the student was enrolled at another institution, or earned a credential there,
by their second academic year. A student can be both retained and persisted, so the two can't be added
together to get "enrolled anywhere".

**Gateway completion** (`gateway_math` and `gateway_english`) means a student required to take gateway math
or English got a grade of 1.0 or higher, or a pass, in it during their first academic year. It counts every
student who was required to take the course, so it is the same as the Postsecondary Data Partnership's
first-year gateway course completion: students who completed a required gateway course, out of all students
required to take one. The cohort file stores it as a completed flag: `C` for completed, `D` for did not
complete, `NA` for not required. It also stores whether the course is required: `R` required, `N` not required,
`UNKNOWN` or blank if nobody knows.

Students who aren't required to take the course are outside the measure. They are counted in `n_out_of_scope`,
not in `n_excluded`, so they don't look like a data problem. A student whose requirement is unknown, or who is
required but has no outcome, can't be classified. They are in `n_excluded`, with the reason
`unknown_requirement_or_outcome`.

A required student who never took the course in year 1 is a `D`, so they count as not completed. For example,
take 10 students: 4 required, took it and passed (`C`); 2 required, took it and did not pass (`D`); 2
required and never took it (`D`); 2 not required. The rate is 4 of 8, or 50%. The two who weren't required are
outside the measure (`n_out_of_scope` is 2).

**Unknown attempts.** In the mock data almost every required student whose attempt is unknown is coded `D`, so
they count as not completed. They are a large share of the denominator, and the rate is much higher without
them. This follows the PDP definition, so they stay in. Finding `N1` in `data/quality/findings.csv` has the counts.

**No required students.** If an institution doesn't report whether students are required to take the course,
nobody has a `C` or `D`, and the measure shows `not_yet_observable`, which reads as "too new". Check the
requirement flags in the data before reading it that way.

**DFW rate** is the share of course enrollments, with a final grade, that ended in a D, F or withdrawal.
Each enrollment is counted in the cohort and the groups of the student who took it, across all their terms.
Rows with no class (a term spent at another college) aren't enrollments and aren't counted at all. For this
measure the counts, `n_excluded` and the numerator are course enrollments, not students. Hiding still goes
by distinct students.

The course file has no letter grades. `Grade` is text: a number from 0 to 4 (grade points), or a code. In the
dictionary the code `A` means audit, not an A. So the letter is inferred from the number, on one shared scale in
[calculations/grades.py](calculations/grades.py): the standard 4.0 plus/minus scale, where each letter covers its
grade points up to the next letter's.

A number between steps takes the letter below it: 1.5 is a D+, 2.5 a C+, 3.6 a B+. F is general, not tied to the
numbers one file uses: any number under the lowest D is an F. The PDP has no DFW measure of its own, so DFW means
what it says: a D (any D), an F or a W. A C- is a C and passes. `DFW_BELOW` (1.7) is worked out from the scale and
`DFW_GRADES` in [calculations/dfw.py](calculations/dfw.py); a school that counts a C- adds it to `DFW_GRADES`. The
gateway page keeps the PDP's own line, 1.0 or a P (`GATEWAY_PASS_AT` in grades.py).

**Pages show groups, not + and - letters.** The letters only decide which group a grade falls in. The groups are cut
only where a rule draws a line, so each one means the same thing whatever grades a school's data holds
([breakdowns/grade_scale.py](breakdowns/grade_scale.py)):

| Page | Group | Grade points | Counted |
| --- | --- | --- | --- |
| DFW | C or higher | 1.7 and up (C- and up) | passed |
| DFW | D | 0.7 to under 1.7 (D-, D, D+) | a DFW |
| DFW | F | under 0.7, or the code `F` | a DFW |
| DFW | W | the code `W` | a DFW |
| Gateway | C or higher | 1.7 and up | passed |
| Gateway | D | 1.0 to under 1.7 (D, D+) | passed |
| Gateway | Under 1.0 | under 1.0 (D- or F), or the code `F` | didn't pass |
| Gateway | P / W | the codes | passed / didn't pass |

"D" differs between the pages on purpose: a D- is a D for DFW but fails a gateway course, so on the gateway page it
sits in "Under 1.0". Each answer carries its page's table as `meta.grade_scale`, and the page shows it under "How
grades are counted".

| Grade in the course file | Counted as | Reason it is left out |
| --- | --- | --- |
| A number from 0 to 4 (written `1` or `1.0`) below 1.7 | D or F: in the numerator and the denominator | |
| A number from 1.7 to 4.0 (C- and up) | passed: in the denominator only | |
| `F` or `W` | D or F: in the numerator and the denominator | |
| `P` | passed: in the denominator only | |
| `I` (incomplete) | left out | `incomplete` |
| `A` (audit) | left out | `audit` |
| `MIS` (missing) | left out | `missing_grade` |
| `O` or `OTH` (other) | left out | `other_grade` |
| `UNKNOWN` (the loader also turns `M` and `UK` into `UNKNOWN`) | left out | `unknown_grade` |
| Codes the dictionary doesn't list (`UW`, `N`, `CHE`, ...) or no grade | left out until their meaning is confirmed | `unlisted_grade` |

Grades match ignoring case and spaces, and a number can have up to two decimals (`3.67`, `4.00`, `w`).

**The cutoff, decided.** Until November 2026 the line was 2.0, so a C- (1.7) counted as a DFW. It is now 1.7: a
C- passes. On the synthetic 2023-24 class that moves 60 grades out of the numerator (4,347 to 4,287 of 18,883).

**DFW by course.** `GroupBy.of(COURSE)` gives one group for every course with an enrollment in the requested
cohorts, so the courses come from the data, not a fixed list. A course is its prefix and number, such as
`ENGL 1302`, and it only applies to `dfw_rate`: asking another measure for it is an error. It can be combined
with other groups, like `GroupBy.of(COURSE, PELL)`. Every course with a classifiable final grade is included, including a single enrollment. Courses that differ only in case, like `ENG 101` and `eng 101`, are one course. A college that gives different
classes the same code will see them as one course.

**Credit completion** is how much of the credit load students attempted in their first academic year they
earned. It is modeled on the Postsecondary Data Partnership's (PDP) credit completion ratio, as described on
NSC's [First Year Credit Completion Ratio](https://help.studentclearinghouse.org/pdp/knowledge-base/first-year-credit-completion-ratio-benchmarking-dashboard/)
and [Credit Momentum](https://help.studentclearinghouse.org/pdp/knowledge-base/credit-momentum-dashboard/)
dashboard pages. It is not PDP's exact calculation:

- A student's ratio is credits earned / credits attempted in year 1 (`number_of_credits_earned_yr_1` and
  `number_of_credits_attempted_yr_1`). The group's figure is the **average of the students' ratios**, not
  total credits earned over total credits attempted. A student who attempted 3 credits counts as much as one
  who attempted 15. In a row, `denominator` is the number of students counted, `numerator` is the sum of
  their ratios, and `metric_rate` is the average.
- Who is counted: first-time and transfer-in students who attempted at least one credit (1 or more).
  Re-admit and continuing students are outside the measure (`n_out_of_scope`). A blank or unknown enrollment
  type is left out (`unknown_enrollment_type`).
- **Unknown full- or part-time status is left out** (`unknown_attendance_type`), as the Credit Momentum page
  and the Subgroup Gap Analysis page say. The First Year page includes those students. In the mock data it
  moves the rate by at most 0.0005.
- A ratio above 1 (more credits earned than attempted) is counted as 1, and nothing flags it. The data model
  checks earned against attempted in the course rows but not in these year 1 totals. The mock data has no such
  rows.
- What counts as an earned credit is whatever the data's earned column says. We sum it as given.
- PDP starts each student's year from their starting term, summer and intersession included. The data model
  only has the year 1 totals, so the measure uses those as given.

### Known issues in the mock data

The mock data has known bugs that affect some groups and measures. They are listed, with counts and
proposed fixes, in `data/quality/findings.csv` (added in #74):

- **Retention and persistence:** rows `3` and `N15`.
- **Groups** (first gen, Pell, enrollment values): rows `1`, `7a` and `N6`.
- **DFW rate:** row `9`, duplicate class rows. They count more than once.
- **Credit completion:** row `4`, year 1 credits attempted that differ from the student's course rows (1,303 students), and row `N20`, credits attempted below the minimum of 1. Those students are left out (`no_credits_attempted`).

## Running a measure

[run_measures.py](run_measures.py) is the entry point: `run_measure(measure, cohorts, group_by)`
returns a row for every cohort and group (everyone, plus every group asked for in `group_by`). It
reads from the loader's SQLite file (`normalized-data-model/output/pdp.sqlite`). Pass `database` to
read another SQLite file by path, or an open connection (for PostgreSQL). A measure that isn't written yet raises `NotImplementedError`.

Each measure's calculation is its own file in [calculations/](calculations/): `retention.py`,
`persistence.py`, the two gateway files, `dfw.py` and `credit_completion.py`. A measure file has two parts, and `run_measures.py` does the rest (building the
groups, preserving unavailable outcomes, working out the rate):

- `NOTE`: the sentence that says who was counted
- `count(connection, cohorts, groups)`: return a `Counts` (numerator, denominator and the students
  counted) for every `(cohort, group)`

A measure can count in SQL or in Python, as long as it returns that. Retention and persistence count in
SQL: each gives one query that returns a row per student per cohort (the group columns, whether the
student has an answer, and whether they achieved it), and
[sql_counts.py](calculations/sql_counts.py) does the grouping in the database, one `GROUP BY` for each kind
of group, with `SUM(...)` over each student's 1, 0 or ratio. Group values match ignoring case and spaces, inside
the database (`UPPER(REPLACE(col, ' ', ''))`), because the data stores `FALL` and `>20 - 24`. A pooled
`Cohort` is counted together in the query. A blank or unlisted group value counts as `UNKNOWN`. The SQL is plain, with no query placeholders, so it runs on
SQLite and PostgreSQL. A measure with branching rules, such as D/F/W grades, can count in Python instead.

To add a measure, write its file and list it in `MEASURES` in `run_measures.py`.

**Saving results:** `run_measure(..., save=True)` also writes the rows to
`measures/output/success_measures.sqlite`, in one table, `success_measures`, for all measures. It is its
own file, not the loader's, so a reload of the data doesn't touch it. It holds only counts and rates
(including small groups), without individual student rows. Each row has the `data_loaded_at`
of the data it came from. The `output/` folder is gitignored.

A results file saved before `exclusions` existed gets the new column when you save to it.

A save is always the latest run. It removes the rows saved earlier for the same measure and cohort,
then writes the new ones. For example:

```python
# 1. Saves retention for 2022-23: everyone, every Pell group and every race group.
run_measure(Measure.RETENTION, [Cohort.of("2022-23")],
            [GroupBy.of(GroupDimension.PELL), GroupBy.of(GroupDimension.RACE)], save=True)

# 2. Saves retention for 2022-23 again, only for everyone. The Pell and race rows from 1 are gone.
run_measure(Measure.RETENTION, [Cohort.of("2022-23")], save=True)

# 3. Saves persistence. The retention rows from 2 stay.
run_measure(Measure.PERSISTENCE, [Cohort.of("2022-23")], save=True)
```

So to keep several breakdowns together, ask for them all in one call, as in 1. After the data is
reloaded, run again to refresh the saved rows.

**Logging:** `run_measure` logs one summary line per run (rows shown and hidden, and when the data was
loaded) and warns when a cohort has no answers yet or every row is hidden. It uses Python's standard
`logging`, so turn it on with `logging.basicConfig(level=logging.INFO)`. At `DEBUG` it also logs each
loaded data file and its SHA-256, so a number can be traced to the files it came from.

```python
run_measure(
    measure=Measure.RETENTION,
    cohorts=[Cohort.of("2022-23")],
    group_by=[GroupBy.of(ENROLLMENT_TYPE)],
)
```

`cohorts` and `group_by` take objects from [models.py](models.py), checked when they are built: a
`Cohort` needs at least one year and no repeats, and a `GroupBy` needs at least one dimension and no
repeats.

**Filters:** `run_measure(..., filters=Group.of((PELL, "Y")))` counts only the students who match
every condition, so "everyone" means every Pell student and `group_by` splits them further. Any
dimension the measure supports works as a filter, including `course` for DFW. Filtered rows can't be
saved, since the results table has no column for the filters.

**D, F and W:** `dfw_rate` rows carry `split`, the numerator as D (any D), F and W counts. They always add
up to the numerator. Every row also carries `n_students`, the
distinct students counted.

**Per student answers:** `read_answers(measure, cohort)` returns each in scope student's answer (1, 0, a
ratio, or None when it can't be counted) and whether the cohort has answers yet. The page breakdowns
use it to count a measure among their own sets of students, such as the students who passed a course.

**Breakdowns:** [breakdowns/](breakdowns/) holds the Explorer pages: Student paths, DFW courses,
gateway courses and credit momentum. They get every rate from `run_measure` and only split it by
term, course, flow or tier, with every nonempty group visible.

**Pooling cohorts:** a `Cohort` with several years, like `Cohort.of("2021-22", "2022-23")`, counts
those cohorts together. Pooling combines their counts; no minimum group size hides the result.

## Tests

[tests/test_explorer_measures.py](tests/test_explorer_measures.py) checks filters, federal retention, the
D/F/W split and per student answers, and `tests/test_breakdown_*.py` check the page breakdowns, each on
a small database built in [tests/explorer_fixture.py](tests/explorer_fixture.py).

[tests/test_measures.py](tests/test_measures.py) checks the calculations on a tiny made-up database,
[tests/fixture.sql](tests/fixture.sql): 48 students, with the expected numbers worked out by hand in
that file's header. It needs no loader. [tests/test_measures_postgres.py](tests/test_measures_postgres.py)
runs the same fixture on PostgreSQL when `PDP_TEST_POSTGRES_URL` is set (CI sets it). `make check` runs it, or run it alone from the repo root:

```bash
python -m pytest measures/tests
```

## Sample

[samples/samples.py](samples/samples.py) shows six examples: what you pass to `run_measure` and the rows
that come back. By default the rows are made up and no database is read. The data is mock, so the numbers
mean nothing either way. To run them on the loaded database, load the data first, then run it from the
repo root:

```bash
cd normalized-data-model
python -m src.loader.load
cd ..
python measures/samples/samples.py
```

Add `--input path/to/pdp.sqlite` to run on a loaded database instead of showing made-up rows. Add
`--save` to also save the rows shown and print what was saved. Real rows go to
`success_measures.sqlite`. Made-up rows go to `success_measures_sample.sqlite`, so they can't replace
real results.

- **Sample 1:** retention for one cohort, grouped by enrollment type and by Pell × intensity.
- **Sample 2:** retention for two pooled cohorts, grouped by enrollment type.
- **Samples 3 and 4:** gateway math and gateway English for one cohort, grouped by Pell status. They are the
  same call with a different `measure`.
- **Sample 5:** DFW rate for one cohort, grouped by Pell status. Its counts are course enrollments.
- **Sample 6:** DFW rate for one cohort, grouped by course. A real run returns a row for every course, so
  only the first 15 rows are printed.
- **Sample 7:** credit completion for one cohort, grouped by Pell status. The numerator has decimals, because it adds up student ratios.
