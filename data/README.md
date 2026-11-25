# Data

**All data in this folder is synthetic. There are no real students in it.** Nothing built on it is a
finding about real students or institutions.

## Where it came from

The two CSV files are mock data from [Achieving the Dream](https://achievingthedream.org/), made in
the shape of the Postsecondary Data Partnership (PDP) analysis-ready files (ARF). They were shared
with the 2026 /dev/color Higher Endeavor Datathon through its shared starter repository. They describe
one made-up institution and have no institution column.

The data's reuse terms are set by Achieving the Dream and /dev/color, not by this repository's MIT
License, which covers the code only.

## What's here

| File | Rows | Columns | What it is |
| --- | ---: | ---: | --- |
| [raw/pdp_cohort_data.csv](raw/pdp_cohort_data.csv) | 10,313 | 85 | One row per student per cohort: demographics, enrollment, gateway courses, credits, retention, credentials |
| [raw/pdp_course_data.csv](raw/pdp_course_data.csv) | 100,951 | 35 | One row per student per course per term: course, grade, credits, delivery |
| [dictionaries/arf_cohort_data_dictionary.md](dictionaries/arf_cohort_data_dictionary.md) | | | What each cohort column and code means |
| [dictionaries/arf_course_data_dictionary.md](dictionaries/arf_course_data_dictionary.md) | | | What each course column and code means |
| [dictionaries/arf_financial_aid_data_dictionary.md](dictionaries/arf_financial_aid_data_dictionary.md) | | | The financial aid file's columns. That file isn't included |
| [dictionaries/column_lookup.csv](dictionaries/column_lookup.csv) | | | The shortened CSV column names and their full PDP names |
| [manifest.json](manifest.json) | | | Each CSV's SHA-256 checksum, row count and column names |
| [quality/](quality/README.md) | | | The known bugs in the mock data, with counts and fixes |

Two more synthetic files feed the data model: on-campus housing and institution events, in
[normalized-data-model/data/input/enrichment/](../normalized-data-model/data/input/enrichment/).

**Don't edit the files in `raw/`.** They use Windows (CRLF) line endings, and any change, even
re-saving, breaks the checksums that `python scripts/check.py` tests.

## Use your own PDP export

> **Warning: never commit real student data.** A PDP export holds student records protected by
> FERPA, the US student-privacy law. Keep it outside this repository, on storage your institution
> approves, and get a privacy and data-governance review before you load it. Once a file is in git
> history, deleting it doesn't remove it.

Don't replace the files in `raw/`. Point the loader at your own cohort and course files instead,
from the repository root:

```bash
python -m api load --cohort /secure/pdp/cohort.csv --course /secure/pdp/course.csv
```

That rebuilds `normalized-data-model/output/pdp.sqlite`, which the pages, API and chat read. Your
files' column names must match the ones in [manifest.json](manifest.json) (full PDP names are in
[column_lookup.csv](dictionaries/column_lookup.csv)). The other choices for a first real load (data
fixes, data coverage, private links for hosted builds) and the checklist before real data goes in are
in the [integration guide](../docs/integration.md#3-load-your-data).
