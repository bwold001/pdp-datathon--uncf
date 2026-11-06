# Mock data quality

Proposal #12. The known data issues in the two mock files in `data/raw/`, and one command that
reproduces every count. The data is synthetic: these are issues in mock data, not findings about
real students or institutions.

| File | What it is |
| --- | --- |
| [findings.csv](findings.csv) | The issue log, one row per finding: `id, file, columns, finding, count, impact, proposed_fix, owner`. |
| [run_checks.py](run_checks.py) | Recomputes every `count` in the log from `data/raw/` and says which ones changed. |
| [../../notebooks/deep_dive.ipynb](../../notebooks/deep_dive.ipynb) | Every finding with example rows and its recommended fix, applied to a copy of the data. Needs `notebooks/requirements.txt`. |

## Run the checks

From the repo root, with `requirements.txt` installed in `.venv/`:

```
python data/quality/run_checks.py            # compare each count with findings.csv; exits 1 on a difference
python data/quality/run_checks.py --missing  # per column: each kind of no value, and whether the dictionary documents it
python data/quality/run_checks.py --update   # after a deliberate data or check change: rewrite the counts
```

`--missing` keeps the kinds of "no value" apart because they mean different things: a blank is
often "not reported", `.` is the files' null marker in numeric columns, `UK`, `-1` and `MISSING`
usually mean unknown, `NA` usually means not applicable (and is also a real `Course_Prefix`), and
`0` can be a real zero or, in a few columns, unknown. Check the dictionary for each column, and
read the CSVs with `dtype=str, keep_default_na=False` for the same reason.

`--missing` then splits these by the data dictionary, reading each column's `- CODE = meaning`
lines in `data/dictionaries/`:

- `documented_unknown` lists the codes the entry defines as unknown, missing or not applicable,
  such as `-1 = Unknown`, `0 = None/Unknown` or a bare `- Unknown`, and `documented_unknown_cells`
  counts them. The whole meaning has to say so: `CD`, whose definition mentions credits "not
  applicable" towards a credential, is a course type.
- A zero the entry doesn't define that way, such as Retention's `0`, stays a valid zero.
- `undocumented_markers` counts `.`, `UK`, `Unknown`, `NA`, `MISSING` or `-1` cells the entry
  doesn't list. A count here is a value to check: `Course_Prefix = NA` is a real prefix, and the
  course file writes Race `Unknown` where its dictionary lists `Unknown or missing` (3,726 cells).

Every count also has a `pct_` column: the share of the file's rows.

## Ids

`1`–`15` (and `7a`–`7c`, `13a`–`13e`) are the original mock-data bug list, `J1`–`J3` the join
checks, `S1`–`S6` smaller items, and `N1`–`N22` findings from the 2026-10-30 audit. To add a
finding, add a row to `findings.csv` and a check with the same id to `CHECKS` in `run_checks.py`,
then run `--update`.

## What remains

Most findings can't be fixed from the files alone, because the true value is unknown: the
`proposed_fix` column says when to flag or exclude rather than rewrite. Questions about how the mock
files were made go to Achieving the Dream, who made them, such as what `First_Gen` Y/N means (1)
and what the `Core_Course_Type` letters stand for (S5); questions about definitions, such as how
year 1 is defined (4), go to PDP. The data model's loader applies the fixes named in
`proposed_fix` (see `normalized-data-model/config/data_fixes.yaml`).
