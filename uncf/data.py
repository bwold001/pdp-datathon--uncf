"""Where the normalized data lives and what every answer says about it.

Shared by the metrics, the page modules and both routers. Tests point data_path somewhere else with
monkeypatch.setattr(data, "data_path", ...), so code here always calls data_path() at run time.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

from measures.run_measures import DEFAULT_DATABASE

COHORTS = ("2021-22", "2022-23", "2023-24", "2024-25")
DEFAULT_COHORT = "2023-24"
# Classes whose second academic year is only partly in the course file. Move to config if a school's data differs.
PROVISIONAL_COHORTS = frozenset({"2024-25"})
SOURCE = "PDP analysis-ready cohort and course files (synthetic sample)"


class DataMissing(Exception):
    """The normalized data isn't loaded yet: run `python -m uncf load`."""


def data_path() -> Path:
    """The normalized data file to read. A function, so tests can point it somewhere else."""
    return DEFAULT_DATABASE


def data_stamp() -> float:
    """The data file's modification time, so cached answers are dropped when the data is reloaded."""
    path = data_path()
    if not path.exists():
        raise DataMissing(f"{path} does not exist. Run: python -m uncf load")
    return path.stat().st_mtime


def open_database(database: Path | None = None) -> sqlite3.Connection:
    """A read-only connection with rows by column name. Raises DataMissing if the data isn't loaded."""
    path = database or data_path()
    if not path.exists():
        raise DataMissing(f"{path} does not exist. Run: python -m uncf load")
    connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    return connection


def loaded_at(connection: sqlite3.Connection | None = None) -> str:
    """When the source data was loaded: the latest load time of the files in it."""
    own = connection is None
    connection = connection or open_database()
    try:
        (value,) = connection.execute("SELECT MAX(loaded_at) FROM data_provider").fetchone()
    finally:
        if own:
            connection.close()
    return value or "unknown"


def is_provisional(cohort: str) -> bool:
    """True when the class's second year is only partly in the data, so year 2 numbers can still change."""
    return cohort in PROVISIONAL_COHORTS
