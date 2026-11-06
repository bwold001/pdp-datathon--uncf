---
name: pdp-data
description: Explain, profile, and answer questions about the PDP mock data in data/raw/ (pdp_cohort_data.csv and pdp_course_data.csv). Use when someone asks what a column means, wants a file profiled, or asks a question the data can answer, such as counts, rates, or comparisons.
---

# pdp-data

Helps with the two mock PDP files in `data/raw/`:

| File | One row per | Rows | Columns |
| --- | --- | ---: | ---: |
| `pdp_cohort_data.csv` | student | 10,313 | 85 |
| `pdp_course_data.csv` | student per course per term | 100,951 | 35 |

Join the files on `Student_GUID` **and** `Cohort`. Joining on `Student_GUID` alone matches 2
students to two cohort rows each and adds 63 extra course rows (101,014 instead of 100,951).

The CSV column names are shortened and often don't match the data dictionaries. Always go through
`data/dictionaries/column_lookup.csv`. It has one row per CSV column: `file, column_in_csv,
dictionary_name, description`. Never guess what a column means from its name.

**All of this data is synthetic.** End every answer about the data with one line saying the result
describes mock data, not real students or institutions.

Pick the path that fits the question.

## 1. Explain a column

1. Find the column in `column_lookup.csv`. Match `column_in_csv` exactly first. If nothing matches,
   search `column_in_csv` and `dictionary_name` for parts of the name.
2. Give the `dictionary_name` and the `description`.
3. For allowed values or longer detail, open the dictionary for that file and find the
   `dictionary_name` heading:
   - `data/dictionaries/arf_cohort_data_dictionary.md`
   - `data/dictionaries/arf_course_data_dictionary.md`
4. Prefixes `S_`, `C_`, `L_` mean the other institution's **state**, **Carnegie type**, and
   **locale**. The data never names other institutions.

## 2. Profile a file

Write and run a short script (Python with pandas if installed, otherwise the `csv` module). Read
with `encoding="utf-8-sig"` and keep every value as a string at first. Report:

- **Shape:** rows and columns.
- **Blanks per column:** count and percent, highest first. Blanks in optional-to-report columns
  (demographics, placement, gateway status, GPA, first-gen) are expected and not a bug.
- **Duplicate students:** `Student_GUID` values that appear more than once in the cohort file.
- **Out-of-range values:** for example, course `Academic_Year` outside the cohort years, or numeric
  columns with impossible values (negative credits).
- **Single-value columns:** columns with only one distinct value.

Then compare what you found with the known facts below, and say if anything differs. A difference
may mean the data changed.

## 3. Answer a data question

For gaps between groups on retention, persistence or gateway courses, use `gap_finder`
(`find_gaps` or the `equity_gaps` table) instead of writing a script. See `gap_finder/README.md`.

1. Turn the question into columns using `column_lookup.csv`. Say which columns you used and why.
2. Write and run a short query or script. Don't estimate by eye.
3. Show the number, and the filter or code that produced it, so someone can check it.
4. Mention any known fact below that affects the answer. For example, counting students in the
   cohort file without removing duplicates counts 2 students twice overall, and joining on
   `Student_GUID` alone adds 63 extra course rows.
5. End with the synthetic-data line.

## Known data facts

For data-quality questions, use the issue log `data/quality/findings.csv`: one row per known
issue, with its count, impact and proposed fix. `python data/quality/run_checks.py` reproduces
the counts.

Checked on 2026-10-19 against the files in `data/raw/`:

- **Duplicate students:** 10,313 cohort rows but 10,311 distinct `Student_GUID`s. 2 students
  appear twice, each in two different cohorts: one in 2021-22 and 2022-23, one in 2022-23 and
  2023-24.
- **Cohorts:** 2021-22 (2,504 rows), 2022-23 (2,617), 2023-24 (2,580), 2024-25 (2,612). Within
  each single cohort, every `Student_GUID` is distinct.
- **Course years run wider than the cohorts:** `Academic_Year` goes from 2012-13 to 2026-27, and
  456 course rows have a blank `Academic_Year`.
- **Credits stored as `.`:** 221 cohort rows have `.` in all 8 `Number_of_Credits_*` columns.
  Treat `.` as missing before doing math.
- **Zero credits:** 47 cohort rows have `Number_of_Credits_Attempted_Yr_1 = 0`, below the
  dictionary's stated minimum of 1.
- **Two spellings of one category:** `Credential_Type_Sought_Year_1` has "...Teach Certification"
  (976 rows) and "...Teacher Certification" (147). Merge them before grouping.
- **`Grade` in the course file is text, not a number:**
  - Numbers from 0 to 4, mostly whole numbers and plus/minus steps (0.3, 0.7, … 3.7).
  - The documented codes `P`, `F`, `I`, `W`, `A`, `M`, `O`.
  - Codes the dictionary doesn't list: `OTH` (75 rows), `UW` (12), `N` (4), `MIS` (3), `CHE` (1),
    `UK` (1). `OTH` and `MIS` likely mean `O` and `M`; the rest are unclear.
  - A few grades between the usual steps: 3.6 (9 rows), 2.5 (7), 3.5 (5), 2.6 (2), 1.5 (1).
  - 17,755 rows (17.6%) are blank.

  Read it as text, map or drop the codes, then convert to numbers.
- **`-1` means Unknown** in `NASPAFirstGeneration`, `MilitaryStatus`, and `EmploymentStatus`, as
  the dictionary defines. In the last two, `0` can also mean unknown.
- **`researchid`** has one value per file: `cohort2026atd` on every cohort row and `course2026atd`
  on every course row. It labels the file, not the student, so don't join on it. It is not in the
  dictionaries.
- **No institution column:** treat the data as one institution's extract.
- **Every course row matches exactly one cohort row on `Student_GUID` + `Cohort`.** Every
  `Student_GUID` in the course file also appears in the cohort file.
- **The financial aid file is not included.** Only its dictionary is.
