# Equity gap finder

Proposal [#26](https://github.com/devcolor/pdp-datathon-starter/issues/26). For each measure and cohort,
it compares every student group with everyone else, ranks the gaps, and flags the ones that are likely
noise. One table holds every group, so a squad doesn't have to pick in advance which groups to look at.
The counts come from the [shared measures](../measures/README.md) (#9), so every squad's gaps use the same
definitions.

**The data is synthetic.** Nothing in this table is a finding about real students or institutions. A gap
shows a difference between groups, not its cause.

## Get the rows

Load the data first ([how](../normalized-data-model/README.md#load-the-data)). Then, from the repo root:

```python
from gap_finder.find_gaps import find_gaps

rows = find_gaps(["retention"], [["2021-22", "2022-23", "2023-24"]], [["race"], ["race", "gender"]])
for row in rows[:5]:
    print(row.group_values, row.gap_pts, row.students_affected, row.likely_noise)
```

- **`measures`:** any of `retention`, `persistence`, `gateway_math`, `gateway_english`. A measure that isn't a yes
  or no per student, such as `dfw_rate`, is refused: the gap finder's statistics don't apply to it.
- **`cohorts`:** each inner list is counted together (pooled), e.g. `[["2022-23"], ["2021-22", "2022-23"]]`.
- **`group_by`:** each inner list is one breakdown, one dimension or two: `race`, `ethnicity`, `gender`,
  `first_gen`, `pell`, `age_band`, `enrollment_type`, `enrollment_intensity`, `cohort_term`.
- **`database`:** the loaded SQLite file, or an open connection. It defaults to the loader's file.

With nothing given, it compares all four measures, the 2021-22 to 2023-24 cohorts pooled, and five
groups (race, gender, Pell, age band, enrollment intensity), each on its own. First gen is left out until
finding 1 in `data/quality/findings.csv` (#74) is settled (see Known limits), but it can still be asked for
with `[["first_gen"]]`. Ask for pairs by name, e.g. `[["race", "gender"]]`: in the default they would
repeat one finding sliced several ways, and push the one-way groups down the ranks. A breakdown asked for
twice is counted once, and a cohort year the loaded data doesn't have is an error.

From SQL or any other stack, save the rows:

```bash
python -m gap_finder.save_results                  # the defaults above
python -m gap_finder.save_results --measure retention --cohort 2021-22,2022-23,2023-24 --group-by race --group-by race,gender
```

That saves the rows twice, neither of them committed:

- **an `equity_gaps` table** in the shared measures' results file, `measures/output/success_measures.sqlite`,
  next to their `success_measures` table, so a query can join a measure to its gaps on measure, cohort and
  group. One column per column below, in the same order, with groups written as ` x ` text and booleans as
  0/1. It refuses a row that breaks the rules below, for example a hidden row with a number in it, or a
  shown group under 10 students. If the table's columns have changed since it was saved, the next save
  rebuilds it, so rerun any other measures you need.
- **`gap_finder/output/equity_gaps.csv`**, the same rows, for Excel or Power BI.

```sql
SELECT group_dimensions, group_values, gap_pts, students_affected, likely_noise
FROM equity_gaps
WHERE measure = 'retention' AND status = 'ok'
ORDER BY cohort, rank_by_affected;
```

Saving again replaces every row for the same measure and cohort, since their q-values and ranks are worked
out together. `--input` reads another loaded file, and `--results` and `--output` save somewhere else.

The table holds every measure and cohort ever saved. The CSV holds only the last run, so after a narrow run
(e.g. `--measure retention --group-by pell`) the two differ: query the table for the full picture.

### The stub

`stub_gaps()` and `python -m gap_finder.save_results --stub` still give 19 hand-written rows, with every
status, for building a page without loading any data. They're retention by race from the mock data, and the
tests check the real calculation gives the same numbers. Stub notes start with `STUB.`, and the stub saves to
its own files, `gap_finder/output/equity_gaps_stub.sqlite` and `.csv`, so it can never replace real results.

| Rows | Cohort | Status |
| --- | --- | --- |
| 8 races, each compared with everyone else | 2021-22 + 2022-23 + 2023-24, pooled | `ok` |
| Unknown race | the same | `unknown_group` |
| Gender X and Two or More Races: 1 student | the same | `suppressed` |
| 9 races | 2024-25, marked too new by hand | `not_yet_observable` |

## An example

Retention by race, 2021-22 to 2023-24 pooled, on the mock data: 4,125 of 7,701 students were retained
(53.6%). Black or African American students: 565 of 1,218 (46.4%), against 54.9% for everyone else. That's
a gap of −8.53 points, or about 104 students, and it ranks first among races.

## The table

One row per measure, cohort and group. The first 14 columns are the shared measures' table, in its order,
so the two read the same way. The comparison columns come after them. Blank means NULL: never read a blank as 0.

| Column | What it is |
| --- | --- |
| `measure` | e.g. `retention` |
| `cohort` | the cohort, or pooled cohorts oldest first, e.g. `2021-22 + 2022-23 + 2023-24` |
| `group_dimensions`, `group_values` | the group, e.g. `race` and `Asian`. A two-way group is joined with ` x `, e.g. `gender x race` and `X x Two or More Races`. There is no everyone row: everyone is what each group is compared with |
| `numerator`, `denominator`, `metric_rate` | the group's own counts, and the rate as a fraction to 4 places |
| `suppressed` | `true` for `suppressed` and `not_yet_observable` rows, as in the shared measures |
| `status` | `ok`, `suppressed`, `not_yet_observable` or `unknown_group` (see below) |
| `n_excluded`, `exclusion_reason` | students the measure applies to but couldn't count, and why, from the measure |
| `n_out_of_scope` | students the measure doesn't apply to, from the measure: for gateway courses, students not required to take one |
| `note` | the measure's own note, then who was compared and over which cohorts. Stub notes start with `STUB.` |
| `data_loaded_at` | when the data was loaded. `stub` in the stub |
| `comparison_numerator`, `comparison_denominator`, `comparison_rate` | everyone else in the cohort: everyone minus the group |
| `gap_pts` | the group's rate minus everyone else's, in percentage points to 2 places. Negative means the group is behind |
| `students_affected` | `gap_pts` / 100 × `denominator`, to 1 place: how many students the gap is worth |
| `ci_low`, `ci_high` | a 95% interval for the gap, in points (Newcombe's method, from each side's Wilson interval). It isn't corrected for testing many groups at once; `likely_noise` is |
| `p_value` | a two-sided two-proportion z-test of the gap, with everyone's rate as the pooled rate |
| `q_value` | the p-value corrected for testing many groups (Benjamini–Hochberg), over the compared rows with the same measure and cohort in one call |
| `likely_noise` | `true` when `q_value` is 0.05 or more |
| `rank_by_affected` | 1 is the most students behind. The default order |
| `rank_by_gap` | 1 is the largest gap behind. Blank for groups under 30 students, whose gaps swing a lot |

### Status

When more than one applies, the first one wins.

| Status | When | What's shown |
| --- | --- | --- |
| `not_yet_observable` | the shared measures say the cohort is too new for the measure | every number blank |
| `suppressed` | fewer than 10 students in the group, or in everyone else | every number blank |
| `unknown_group` | the value is unknown, e.g. race `UNKNOWN` | the group's own counts and rate. They stay in everyone else, but aren't compared or ranked |
| `ok` | otherwise | everything |

### Order and ranks

Ranks start again for each measure and cohort, and put the most behind first. Rows come back in that
order: by measure and cohort, then by `rank_by_affected`, then unranked rows. Sort by `rank_by_gap` to see
the largest gaps instead. Small groups can have large gaps that affect few students.

Ranks and q-values cover every group compared in the same call, across breakdowns, so a gap can be ranked
against all the others. That means they depend on what was asked for: adding Pell to a race run can move
a race group from rank 1 to 2. Compare ranks only between runs with the same breakdowns.

A row that breaks these rules can't be built: `GapResult` in [models.py](models.py) refuses it, and
`check_table` checks the whole table.

## How a gap is worked out

[sources.py](sources.py) runs each measure with `run_measure` and hands its rows, everyone included, to
[compare.py](compare.py) as `CountRow`s. It's the only file that imports the shared measures. For each
group that's shown and known, `compare()` works out:

1. **Everyone else** is everyone minus the group: `comparison_numerator` and `comparison_denominator`.
2. **The gap** is the group's rate minus everyone else's. The 95% interval uses Newcombe's method: a Wilson
   score interval for each side's rate, combined. Unlike 1.96 standard errors either side, it stays honest
   for small groups and rates near 0% or 100%: 0 of 12 against 50% gives −53.1 to −25.6 points, not −53.1 to
   −46.9.
3. **The p-value** is a two-sided two-proportion z-test, using everyone's rate as the pooled rate. If
   everyone has the same outcome (a rate of 0 or 1), there's no gap, and the p-value is 1.
4. **The q-value** corrects the p-values for testing many groups at once (Benjamini–Hochberg). It covers
   every compared group with the same measure and cohort, one-way and two-way together. A row's q-value
   depends on which other groups were tested with it: asking for more groups can raise it or lower it.
5. **Ranks** sort by `students_affected` and by `gap_pts`, the most behind first. Ties go to the larger
   group.

Hidden and unknown groups aren't tested, so they don't change anyone's q-value or rank. A group is hidden
when everyone else has fewer than 10 students too, since the comparison columns would then show a hidden
group's counts. That also covers a group that is everyone.

`compare()` works on counts alone, so it can be used without a database:

```python
from gap_finder.compare import CountRow, compare

rows = [
    CountRow("retention", "2022-23", (), (), 470, 1000, "ok", 0, 0, None, "Made-up counts.", "example"),
    CountRow("retention", "2022-23", ("race",), ("Asian",), 70, 200, "ok", 0, 0, None, "Made-up counts.", "example"),
    # ...one row per group
]
gaps = compare(rows)
```

## Known limits

These come from the shared measures and the mock data, and change here when they change there:

- **2024-25 retention shows as `ok`**, because the mock data already has answers for it, though the cohort
  looks only partly observed. A cohort is `not_yet_observable` only when the shared measures say so.
- **First gen:** the mock data stores `Y`/`N`, but the shared measures' allowed values don't include `Y`, so
  `Y` reads as `UNKNOWN`. So `first_gen = N` is compared with an everyone else that's mostly `UNKNOWN`, which
  is why it's not in the default. It's finding 1 in `data/quality/findings.csv` (#74).
- **Pell** is almost all `Y` or `N` (unknowns are `unknown_group`), so `pell = Y` and `pell = N` are close to the
  same gap seen from each side.

## Run the tests

```bash
make check-fast     # leaves out the full-load test
make check          # includes it: it loads the full mock data into a temporary folder (about 20 seconds)
```

or only these, from the repo root: `python -m pytest gap_finder/tests`.

They cover #26's completion test: the table and CSV with a note on every row (1), the planted 15-point and
2-point gaps (2, 3), hiding under 10 (4), no group under 30 in the gap-size order (5), and the Black or
African American retention gap reproduced by hand from the raw cohort file (6).

## Next

A Playground page for the table, as a follow-up.
