"""Saves gap rows as an equity_gaps table in SQLite, so squads can query them, and as a CSV for spreadsheets.

Run from the repo root, after loading the data: python -m gap_finder.save_results
Add --stub for the hand-written rows, which need no data. The files hold only counts and rates, with small
groups hidden. They're outputs, so they aren't committed.
"""
from __future__ import annotations

import argparse
import csv
import sqlite3
from enum import Enum
from pathlib import Path

from measures.save_results import RESULTS_DATABASE

from .find_gaps import find_gaps, stub_gaps
from .models import COLUMNS, GROUP_JOIN, GapResult, min_students

OUTPUT = Path(__file__).parent / "output"
# Real results: the table goes in the shared measures' results file, next to their own table, so the two join
# on measure, cohort and group.
RESULTS_CSV = OUTPUT / "equity_gaps.csv"
# The stub's own files, so they can never replace real results.
STUB_DATABASE = OUTPUT / "equity_gaps_stub.sqlite"
STUB_CSV = OUTPUT / "equity_gaps_stub.csv"

# One column per COLUMNS entry, in the same order. The CHECKs are GapResult's main rules, so a bad row
# can't be saved by code that skips GapResult either. {min_students} is filled in by create_table_sql().
CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS equity_gaps (
    measure                TEXT    NOT NULL,
    cohort                 TEXT    NOT NULL,
    group_dimensions       TEXT    NOT NULL,
    group_values           TEXT    NOT NULL,
    numerator              INTEGER,
    denominator            INTEGER,
    metric_rate            REAL,
    suppressed             BOOLEAN NOT NULL CHECK (suppressed IN (0, 1)),
    status                 TEXT    NOT NULL CHECK (status IN ('ok', 'suppressed', 'not_yet_observable', 'unknown_group')),
    n_excluded             INTEGER,
    n_out_of_scope         INTEGER,
    exclusion_reason       TEXT,
    note                   TEXT    NOT NULL,
    data_loaded_at         TEXT    NOT NULL,
    comparison_numerator   INTEGER,
    comparison_denominator INTEGER,
    comparison_rate        REAL,
    gap_pts                REAL,
    students_affected      REAL,
    ci_low                 REAL,
    ci_high                REAL,
    p_value                REAL,
    q_value                REAL,
    likely_noise           BOOLEAN CHECK (likely_noise IN (0, 1)),
    rank_by_affected       INTEGER,
    rank_by_gap            INTEGER,
    PRIMARY KEY (measure, cohort, group_dimensions, group_values),
    CHECK (suppressed = (status IN ('suppressed', 'not_yet_observable'))),
    -- A hidden row is all blank, never 0.
    CHECK (NOT suppressed OR COALESCE(
        numerator, denominator, metric_rate, n_excluded, n_out_of_scope, comparison_numerator, comparison_denominator,
        comparison_rate, gap_pts, students_affected, ci_low, ci_high, p_value, q_value, likely_noise,
        rank_by_affected, rank_by_gap) IS NULL),
    -- A shown row has its own counts.
    CHECK (suppressed OR (numerator IS NOT NULL AND denominator IS NOT NULL AND metric_rate IS NOT NULL
                          AND n_excluded IS NOT NULL AND n_out_of_scope IS NOT NULL)),
    -- A shown group has at least min_students() students.
    CHECK (suppressed OR denominator >= {min_students}),
    -- An ok row has every comparison column and both ranks.
    CHECK (status != 'ok' OR (comparison_numerator IS NOT NULL AND comparison_denominator IS NOT NULL
        AND comparison_rate IS NOT NULL AND gap_pts IS NOT NULL AND students_affected IS NOT NULL
        AND ci_low IS NOT NULL AND ci_high IS NOT NULL AND p_value IS NOT NULL AND q_value IS NOT NULL
        AND likely_noise IS NOT NULL AND rank_by_affected IS NOT NULL AND rank_by_gap IS NOT NULL)),
    -- An ok row's everyone else has at least min_students() too, or its comparison columns would show a hidden group.
    CHECK (status != 'ok' OR comparison_denominator >= {min_students}),
    -- An unknown group is shown but not compared.
    CHECK (status != 'unknown_group' OR COALESCE(
        comparison_numerator, comparison_denominator, comparison_rate, gap_pts, students_affected, ci_low,
        ci_high, p_value, q_value, likely_noise, rank_by_affected, rank_by_gap) IS NULL)
)
"""


def sql_value(value):
    """One value as SQLite stores it: ' x ' between group parts, an enum's text, booleans as 0/1."""
    if isinstance(value, tuple):
        return GROUP_JOIN.join(value)
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, bool):
        return int(value)
    return value


def create_table_sql() -> str:
    """The equity_gaps table, with today's min_students() in its checks."""
    return CREATE_TABLE.format(min_students=min_students())


def made_with_todays_minimum(connection: sqlite3.Connection) -> bool:
    """Whether the saved equity_gaps table's checks use today's min_students()."""
    row = connection.execute("SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'equity_gaps'").fetchone()
    return row is not None and f"denominator >= {min_students()})" in row[0]


def table_columns(connection: sqlite3.Connection) -> tuple[str, ...]:
    """The equity_gaps table's column names, in order. Empty if there's no table."""
    return tuple(row[1] for row in connection.execute("PRAGMA table_info(equity_gaps)"))


def save_gaps(rows: list[GapResult], database: Path) -> None:
    """Write the rows to equity_gaps. Each measure and cohort is replaced whole, since its q-values and ranks go together."""
    database.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database)
    try:
        # An older layout, or one made with another minimum, can't take today's rows. Results are regenerated, so
        # rebuild the table.
        columns = table_columns(connection)
        if columns and (columns != COLUMNS or not made_with_todays_minimum(connection)):
            connection.execute("DROP TABLE equity_gaps")
        connection.execute(create_table_sql())
        # Deleting first means a run with fewer breakdowns can't leave old rows, with old ranks, behind.
        for measure, cohort in sorted({(r.measure, r.cohort) for r in rows}):
            connection.execute("DELETE FROM equity_gaps WHERE measure = ? AND cohort = ?", (measure, cohort))
        placeholders = ", ".join("?" for _ in COLUMNS)
        connection.executemany(
            f"INSERT INTO equity_gaps ({', '.join(COLUMNS)}) VALUES ({placeholders})",
            [[sql_value(getattr(row, name)) for name in COLUMNS] for row in rows],
        )
        connection.commit()
    finally:
        connection.close()


def cell(value) -> str:
    """One value as CSV text: blank for NULL, true/false for booleans, ' x ' between group parts."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, tuple):
        return GROUP_JOIN.join(value)
    return str(value)


def write_csv(rows: list[GapResult], path: Path) -> None:
    """Write the rows with a header of COLUMNS, replacing the file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(COLUMNS)
        for row in rows:
            writer.writerow(cell(getattr(row, name)) for name in COLUMNS)


def split(text: str) -> list[str]:
    """'2021-22,2022-23' as ['2021-22', '2022-23']."""
    return [part.strip() for part in text.split(",") if part.strip()]


def main() -> None:
    """Save the gap table, or the stub, to the equity_gaps table and a CSV."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--stub", action="store_true", help="save the hand-written stub rows instead, to their own files")
    parser.add_argument("--measure", action="append", help="e.g. retention. Repeat for more. Default: all four")
    parser.add_argument("--cohort", action="append", type=split,
                        help="cohorts counted together, e.g. 2021-22,2022-23. Repeat for more. Default: 2021-22 to 2023-24")
    parser.add_argument("--group-by", action="append", type=split,
                        help="one breakdown, e.g. race or race,gender. Repeat for more. Default: race, gender, pell, age_band and enrollment_intensity, each on its own")
    parser.add_argument("--input", type=Path, help="the loaded data's SQLite file to read (default: the loader's)")
    parser.add_argument("--results", type=Path,
                        help=f"the SQLite file to save the table to (default {RESULTS_DATABASE.name}, or {STUB_DATABASE.name})")
    parser.add_argument("--output", type=Path, help=f"the CSV (default {RESULTS_CSV.name}, or {STUB_CSV.name})")
    args = parser.parse_args()

    if args.stub:
        rows = stub_gaps()
        results, output = args.results or STUB_DATABASE, args.output or STUB_CSV
        about = "stub rows. Hand-written from synthetic mock data, not computed"
    else:
        rows = find_gaps(args.measure, args.cohort, args.group_by, args.input)
        results, output = args.results or RESULTS_DATABASE, args.output or RESULTS_CSV
        about = "rows"
    save_gaps(rows, results)
    write_csv(rows, output)
    print(f"Saved {len(rows)} {about} to {results} (table equity_gaps) and {output}.")


if __name__ == "__main__":
    main()
