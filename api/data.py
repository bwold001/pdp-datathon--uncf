"""Where the normalized data lives and what every answer says about it.

Shared by the metrics, the page modules and both routers. Tests point data_path somewhere else with
monkeypatch.setattr(data, "data_path", ...), so code here always calls data_path() at run time.

Nothing here names a school's cohort years: they come from the loaded data, and the provisional ones from the
analytics config (UNCF_ANALYTICS_CONFIG), so a school's own files work without code changes.
"""
from __future__ import annotations

import os
import sqlite3
from functools import lru_cache
from pathlib import Path

from yaml import YAMLError

from analytics.coverage import DEFAULT_CONFIG, load_coverage
from measures.run_measures import DEFAULT_DATABASE, configured_data_label

# What every answer names as its source, unless UNCF_SOURCE says otherwise (a school's own files, for example).
SOURCE = "PDP analysis-ready cohort and course files (synthetic sample)"


class DataMissing(Exception):
    """The normalized data isn't loaded yet: run `python -m api load`."""


class ConfigInvalid(Exception):
    """The analytics config (UNCF_ANALYTICS_CONFIG) is missing or can't be read."""


def data_path() -> Path:
    """The normalized data file to read. A function, so tests can point it somewhere else."""
    return DEFAULT_DATABASE


def source() -> str:
    """The source every answer names: UNCF_SOURCE, or the synthetic sample's description."""
    return os.environ.get("UNCF_SOURCE", "").strip() or SOURCE


def data_label() -> str:
    """What kind of data is loaded (UNCF_DATA_LABEL): "synthetic" (the sample) or "institution" (a school's files)."""
    try:
        return configured_data_label()
    except ValueError as invalid:
        raise ConfigInvalid(str(invalid)) from invalid


def data_stamp() -> float:
    """The data file's modification time, so cached answers are dropped when the data is reloaded."""
    path = data_path()
    if not path.exists():
        raise DataMissing(f"{path} does not exist. Run: python -m api load")
    return path.stat().st_mtime


def open_database(database: Path | None = None) -> sqlite3.Connection:
    """A read-only connection with rows by column name. Raises DataMissing if the data isn't loaded."""
    path = database or data_path()
    if not path.exists():
        raise DataMissing(f"{path} does not exist. Run: python -m api load")
    connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    return connection


def cohorts() -> tuple[str, ...]:
    """Every cohort year in the loaded data, oldest first. Raises DataMissing if the data isn't loaded."""
    return _cohorts(data_path(), data_stamp())


@lru_cache(maxsize=8)
def _cohorts(path: Path, stamp: float) -> tuple[str, ...]:
    """The cohort years in one version of one data file (stamp keeps a reloaded file from reusing the old list)."""
    connection = open_database(path)
    try:
        rows = connection.execute(
            "SELECT DISTINCT cohort FROM cohort_membership WHERE cohort IS NOT NULL ORDER BY cohort"
        ).fetchall()
    finally:
        connection.close()
    return tuple(row[0] for row in rows)


def default_cohort() -> str:
    """The cohort shown when a request names none: the latest one that isn't provisional, else the latest."""
    years = cohorts()
    if not years:
        raise DataMissing(f"{data_path()} has no cohorts. Load the cohort and course files: python -m api load")
    complete = [year for year in years if not is_provisional(year)]
    return (complete or list(years))[-1]


def provisional_cohorts() -> frozenset[str]:
    """Cohorts whose second year is only partly in the data, from the analytics config the chat also reads."""
    path = Path(os.environ.get("UNCF_ANALYTICS_CONFIG", DEFAULT_CONFIG))
    try:
        return frozenset(load_coverage(path).provisional_retention_cohorts)
    except (OSError, ValueError, YAMLError) as error:
        raise ConfigInvalid(f"The analytics config at {path} is missing or invalid.") from error


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
    return cohort in provisional_cohorts()
