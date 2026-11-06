"""Saves result rows to their own SQLite file, in one table for all measures.

The file holds only counts and rates, with small groups hidden, so it can be shared without any
student rows. It is not the loader's file, so a reload of the data never touches it.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .models import Group, MeasureResult

RESULTS_DATABASE = Path(__file__).parent / "output" / "success_measures.sqlite"
# Where the made-up rows of samples.py go, so they can never replace real results.
SAMPLE_RESULTS_DATABASE = Path(__file__).parent / "output" / "success_measures_sample.sqlite"

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS success_measures (
    measure          TEXT    NOT NULL,
    cohort           TEXT    NOT NULL,
    group_dimensions TEXT    NOT NULL,
    group_values     TEXT    NOT NULL,
    numerator        NUMERIC,
    denominator      NUMERIC,
    metric_rate      REAL,
    suppressed       BOOLEAN NOT NULL,
    status           TEXT    NOT NULL CHECK (status IN ('ok', 'suppressed', 'not_yet_observable')),
    n_excluded       INTEGER,
    n_out_of_scope   INTEGER,
    exclusion_reason TEXT,
    note             TEXT    NOT NULL,
    data_loaded_at   TEXT    NOT NULL,
    exclusions       TEXT,
    PRIMARY KEY (measure, cohort, group_dimensions, group_values),
    -- A hidden group is all blank, never 0. A shown group always has the three numbers.
    CHECK (
        (suppressed AND status != 'ok' AND numerator IS NULL AND denominator IS NULL AND metric_rate IS NULL AND n_excluded IS NULL AND n_out_of_scope IS NULL)
        OR
        (NOT suppressed AND status = 'ok' AND numerator IS NOT NULL AND denominator IS NOT NULL AND metric_rate IS NOT NULL)
    )
)
"""


def group_columns(group: Group) -> tuple[str, str]:
    """The group as two aligned texts, e.g. ('enrollment_intensity x pell', 'Full-time x Y')."""
    if not group.parts:
        return "all", "all"
    parts = sorted(group.parts, key=lambda p: p.dimension.value)
    return " x ".join(p.dimension.value for p in parts), " x ".join(p.value for p in parts)


def save_results(results: list[MeasureResult], data_loaded_at: str, database: Path = RESULTS_DATABASE) -> None:
    """Write the rows. Rows saved earlier for the same measure and cohort are removed first, so a save is always the latest run."""
    database.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database)
    try:
        connection.execute(CREATE_TABLE)
        # A file saved before exclusions existed gets the new column.
        if "exclusions" not in [column[1] for column in connection.execute("PRAGMA table_info(success_measures)")]:
            connection.execute("ALTER TABLE success_measures ADD COLUMN exclusions TEXT")
        for measure, cohort in sorted({(r.measure.value, r.cohort.label) for r in results}):
            connection.execute("DELETE FROM success_measures WHERE measure = ? AND cohort = ?", (measure, cohort))
        for r in results:
            dimensions, values = group_columns(r.group)
            connection.execute(
                "INSERT INTO success_measures VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    r.measure.value, r.cohort.label, dimensions, values,
                    r.numerator, r.denominator, r.metric_rate, r.suppressed, r.status.value,
                    r.n_excluded, r.n_out_of_scope, r.exclusion_reason.value if r.exclusion_reason else None, r.note, data_loaded_at,
                    json.dumps({reason.value: n for reason, n in r.exclusions.items()}, sort_keys=True) if r.exclusions else None,
                ),
            )
        connection.commit()
    finally:
        connection.close()
