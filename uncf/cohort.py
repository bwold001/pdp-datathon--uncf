"""One cohort bar for every page and both APIs: the cohort year, eight filters, the retention type, and the
students they pick.

Filter names and values are the measures' own (measures/models.py). Values match the data the way the measures
match them, ignoring case and spaces, with anything blank or unlisted counted as UNKNOWN. Groups of 1 to 9
students are hidden here and nowhere else.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

from measures.calculations.sql_counts import group_value_sql, normalize
from measures.models import ALLOWED_VALUES, SUPPRESSION_THRESHOLD, GroupDimension
from uncf import data
from uncf.data import COHORTS, DEFAULT_COHORT

# The cohort bar's filters after the cohort year, in the bar's order. The Results API groups by the same list.
FILTER_DIMENSIONS = (
    GroupDimension.COHORT_TERM,
    GroupDimension.ENROLLMENT_INTENSITY,
    GroupDimension.ENROLLMENT_TYPE,
    GroupDimension.PELL,
    GroupDimension.GENDER,
    GroupDimension.RACE,
    GroupDimension.ETHNICITY,
    GroupDimension.AGE_BAND,
)
FILTER_NAMES = tuple(dimension.value for dimension in FILTER_DIMENSIONS)
FILTER_LABELS = {
    "cohort_term": "Starting term",
    "enrollment_intensity": "Full or part time",
    "enrollment_type": "Enrollment type",
    "pell": "Pell grant",
    "gender": "Gender",
    "race": "Race",
    "ethnicity": "Ethnicity",
    "age_band": "Age",
}
RETENTION_TYPES = ("school", "federal")
DEFAULT_RETENTION_TYPE = "school"
MIN_STUDENTS = SUPPRESSION_THRESHOLD
FIRST_TIME = normalize("First-time")


class InvalidFilter(ValueError):
    """A cohort, filter or retention type the Explorer doesn't offer."""


@dataclass(frozen=True)
class CohortQuery:
    """One cohort year, the filters set on it, and which retention to report. A filter left out means "All"."""

    cohort: str = DEFAULT_COHORT
    filters: tuple[tuple[str, str], ...] = field(default_factory=tuple)
    retention_type: str = DEFAULT_RETENTION_TYPE

    def __post_init__(self) -> None:
        if self.cohort not in COHORTS:
            raise InvalidFilter(f"Cohort has no value {self.cohort!r}.")
        if self.retention_type not in RETENTION_TYPES:
            raise InvalidFilter(f"retention_type has no value {self.retention_type!r}. Use school or federal.")
        for name, value in self.filters:
            if name not in FILTER_NAMES:
                raise InvalidFilter(f"There is no filter called {name!r}.")
            if value not in ALLOWED_VALUES[GroupDimension(name)]:
                raise InvalidFilter(f"{name} has no value {value!r}.")

    @classmethod
    def of(cls, cohort: str = DEFAULT_COHORT, retention_type: str = DEFAULT_RETENTION_TYPE, **filters: str | None) -> CohortQuery:
        """A query from keyword filters, skipping the ones left as None. Sorted, so equal queries are equal."""
        chosen = tuple(sorted((name, value) for name, value in filters.items() if value is not None))
        return cls(cohort, chosen, retention_type)

    def as_dict(self) -> dict[str, str]:
        """The filters that are set, by name."""
        return dict(self.filters)

    def meta(self) -> dict:
        """What every answer says about the question it answers."""
        return {
            "cohort": self.cohort,
            "filters": self.as_dict(),
            "retention_type": self.retention_type,
            "provisional": data.is_provisional(self.cohort),
            "min_students": MIN_STUDENTS,
            "source": data.SOURCE,
        }


def students_sql() -> str:
    """One row per student per cohort, with each filter's value matched the measures' way (see sql_counts)."""
    columns = "".join(f",\n       {group_value_sql(dimension)} AS {dimension.value}" for dimension in FILTER_DIMENSIONS)
    return f"""
SELECT s.student_id AS student_id, s.cohort AS cohort{columns}
FROM (
    SELECT cm.student_id AS student_id, cm.cohort AS cohort,
           cm.cohort_term AS cohort_term,
           cm.enrollment_intensity_first_term AS enrollment_intensity,
           cm.enrollment_type AS enrollment_type,
           cm.pell_status_first_year AS pell,
           st.gender AS gender, st.race AS race, st.ethnicity AS ethnicity, st.student_age AS age_band
    FROM cohort_membership cm
    JOIN student st ON st.student_id = cm.student_id
) s"""


def select_students(connection: sqlite3.Connection, query: CohortQuery) -> dict[str, sqlite3.Row]:
    """The students of the query's cohort that match every filter, by id, with their (normalized) filter values."""
    conditions = ["cohort = ?"]
    parameters: list[str] = [query.cohort]
    for name, value in query.filters:
        # Names were checked against FILTER_NAMES, so they are safe to write into the query.
        conditions.append(f"{name} = ?")
        parameters.append(normalize(value))
    sql = f"SELECT * FROM ({students_sql()}) WHERE {' AND '.join(conditions)}"
    return {row["student_id"]: row for row in connection.execute(sql, parameters).fetchall()}


# Each dimension's values in matching form (upper case, no spaces), mapped back to the listed spelling.
LISTED = {dimension.value: {normalize(value): value for value in values} for dimension, values in ALLOWED_VALUES.items()}


def listed_value(dimension: str, normalized: str) -> str:
    """The listed spelling of a normalized value, e.g. FIRST-TIME -> First-time."""
    return LISTED[dimension][normalized]


def shown(count: int | None) -> int | None:
    """A count as a page may show it: groups of 1 to 9 students are hidden (None), never shown as 0."""
    if count is None or 0 < count < MIN_STUDENTS:
        return None
    return count


def share(count: int | None, total: int | None) -> float | None:
    """count / total to four places, or None when either is hidden or the total is 0."""
    if count is None or not total:
        return None
    return round(count / total, 4)


def cohort_options(cohort: str = DEFAULT_COHORT, database: Path | None = None) -> dict:
    """How many students entered in each cohort year, and in the chosen cohort, how many have each filter value."""
    CohortQuery(cohort)  # checks the cohort
    connection = data.open_database(database)
    try:
        rows = connection.execute(f"SELECT * FROM ({students_sql()})").fetchall()
        stamp = data.loaded_at(connection)
    finally:
        connection.close()

    cohorts = {year: 0 for year in COHORTS}
    filters = {name: {value: 0 for value in ALLOWED_VALUES[GroupDimension(name)]} for name in FILTER_NAMES}
    for row in rows:
        if row["cohort"] in cohorts:
            cohorts[row["cohort"]] += 1
        if row["cohort"] == cohort:
            for name in FILTER_NAMES:
                filters[name][listed_value(name, row[name])] += 1
    return {
        "cohort": cohort,
        "cohorts": {year: shown(count) for year, count in cohorts.items()},
        "filters": {name: {value: shown(count) for value, count in counts.items()} for name, counts in filters.items()},
        "labels": FILTER_LABELS,
        "retention_types": list(RETENTION_TYPES),
        "min_students": MIN_STUDENTS,
        "source": data.SOURCE,
        "loaded_at": stamp,
    }
