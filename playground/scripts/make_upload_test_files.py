"""Make CSV files for testing the workbench Upload page's failure cases by hand.

Each case is a folder under normalized-data-model/output/playground/upload_test_files/ with the
files to upload and what should happen. They're built from the data model's 10-student sample files, so they're small
and synthetic. Run from the repo root:
    python playground/scripts/make_upload_test_files.py
"""

import csv
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SAMPLE = REPO / "normalized-data-model/data/input/sample"
# Ignored by git, next to the tables the Playground's loads write.
OUT = REPO / "normalized-data-model/output/playground/upload_test_files"

COHORT = SAMPLE / "pdp_cohort_data.csv"
COURSE = SAMPLE / "pdp_course_data.csv"


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    """A CSV's header and rows."""
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def write_rows(path: Path, header: list[str], rows: list[dict[str, str]]) -> None:
    """Write rows under the same header the source file had."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)


def write_case(name: str, expected: str) -> Path:
    """Start a case's folder with a note on what should happen."""
    folder = OUT / name
    folder.mkdir(parents=True)
    (folder / "EXPECTED.md").write_text(expected.strip() + "\n", encoding="utf-8")
    return folder


def main() -> None:
    """Rebuild every case from the sample files."""
    if OUT.exists():
        shutil.rmtree(OUT)
    header, cohort = read_rows(COHORT)

    # The reviewer's case: valid headers, but every Student_GUID breaks its pattern rule.
    folder = write_case("1_every_row_fails", """
Load good data first (Upload > "Use the mock files", or case 2). Then upload cohort_every_row_fails.csv alone.

- Upload: checks pass, then Save shows an error that no student rows passed validation. No "Saved" step.
- Home, Explore and the nav still show the earlier data, with its counts unchanged.
""")
    write_rows(folder / "cohort_every_row_fails.csv", header,
               [dict(row, Student_GUID="not-a-guid") for row in cohort])

    # Clean files: Home's warning count should be 0, with no enrichment rows counted.
    folder = write_case("2_clean_files", """
Upload both files together.

- Upload: Saved, with 10 students.
- Home: "no warnings" from the checks (before the fix it showed about 8,099, all from on_campus_housing.csv).
""")
    shutil.copy(COHORT, folder / "pdp_cohort_data.csv")
    shutil.copy(COURSE, folder / "pdp_course_data.csv")

    # One bad cohort row: the load saves, and Home counts only cohort and course warnings.
    _, course = read_rows(COURSE)
    bad_student = cohort[0]["Student_GUID"]
    bad_course_rows = sum(row["Student_GUID"] == bad_student for row in course)
    folder = write_case("3_one_row_fails", f"""
Upload both files together.

- Upload: Saved, with 9 students. The summary lists the cohort row and that student's course rows ({bad_course_rows}) as failed checks.
- Home: {1 + bad_course_rows} warnings from the checks.
""")
    write_rows(folder / "cohort_one_row_fails.csv", header,
               [dict(cohort[0], Student_GUID="not-a-guid"), *cohort[1:]])
    shutil.copy(COURSE, folder / "pdp_course_data.csv")

    # Leaving mid-load needs no special file: start a load and switch pages while it runs.
    write_case("4_leave_during_load", """
On Upload, click "Use the mock files", then open the Field guide before it finishes.
Wait about a minute, then go back to Home without reloading.

- Home shows the loaded data, not "No data yet".
""")
    print(f"wrote test cases to {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
