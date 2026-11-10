"""Counts a measure in SQL, for measures whose answer is a yes, no, a ratio or blank per student.

The measure's query gives one row per student per cohort (see students.py). This file groups those rows,
one GROUP BY for each kind of group. It uses plain SQL that runs on SQLite and PostgreSQL, and puts no values
in query parameters: cohort years are checked, then written into the query text.

filters narrows the students before grouping (every condition holds), e.g. only Pell students. Filter values
are checked by GroupPart, then written into the query text. A measure whose rows have an `outcome` column can
ask for split, the numerator counted by outcome (DFW: D, F and W).
"""
from __future__ import annotations

import re

from ..models import (
    ALLOWED_VALUES,
    EVERYONE,
    OPEN_DIMENSIONS,
    UNKNOWN,
    Cohort,
    Counts,
    ExclusionReason,
    Group,
    GroupDimension,
)

# Cohort years go into the query text, so only plain text like 2022-23 is allowed.
SAFE_YEAR = re.compile(r"^[A-Za-z0-9_-]+$")

EVERYONE_KEY = ()


def normalize(text: str) -> str:
    """Group values match ignoring case and spaces, the same way the SQL does it."""
    return text.replace(" ", "").upper()


def count_in_sql(
    connection,
    student_sql: str,
    cohorts: list[Cohort],
    groups: list[Group],
    filters: Group = EVERYONE,
    split: tuple[str, ...] = (),
) -> dict[tuple[Cohort, Group], Counts]:
    """Count every cohort and group in the database. Empty groups get zero counts.

    Each row of student_sql says why it is left out of the count, so the left-out rows are counted by reason too.
    """
    cohort_values = cohort_values_sql(cohorts)
    tallies = {}
    reasons = {}
    for dimensions in kinds_of_group(groups):
        query = group_query(student_sql, cohort_values, dimensions, filters, split)
        tallies[dimensions] = read_tallies(connection, query, len(dimensions), split)
        reasons[dimensions] = read_reasons(connection, reasons_query(student_sql, cohort_values, dimensions, filters), len(dimensions))

    unanswered_years = years_without_answers(connection, student_sql)
    counts = {}
    for number, cohort in enumerate(cohorts):
        # A pooled cohort is not yet observable if any of its years has no answers yet.
        not_yet_observable = any(year in unanswered_years for year in cohort.years)
        for group in groups:
            values = group_values(group)
            kind = tuple(sorted(values, key=lambda d: d.value))
            tally = tallies[kind].get((number, tuple_of(values)), (0, 0, 0, 0, 0, {value: 0 for value in split}))
            excluded = reasons[kind].get((number, tuple_of(values)), {})
            counts[(cohort, group)] = to_counts(tally, excluded, not_yet_observable, bool(split))
    return counts


def years_without_answers(connection, student_sql: str) -> set[str]:
    """The cohort years that have in-scope students but no answers yet."""
    cursor = connection.cursor()
    cursor.execute(f"WITH students AS ({student_sql}) SELECT cohort, SUM(in_scope), SUM(has_answer) FROM students GROUP BY cohort")
    return {cohort for cohort, members, answers in cursor.fetchall() if int(members) > 0 and int(answers) == 0}


def group_values(group: Group) -> dict[GroupDimension, str]:
    """The group's conditions as dimension -> normalized value."""
    return {part.dimension: normalize(part.value) for part in group.parts}


def tuple_of(values: dict[GroupDimension, str]) -> tuple[str, ...]:
    """The values in dimension order, the same order the query returns its group columns."""
    return tuple(values[d] for d in sorted(values, key=lambda d: d.value))


def kinds_of_group(groups: list[Group]) -> list[tuple[GroupDimension, ...]]:
    """The distinct sets of dimensions the groups use, each sorted by name. Everyone is always first."""
    kinds = [EVERYONE_KEY]
    for group in groups:
        dimensions = tuple(sorted((part.dimension for part in group.parts), key=lambda d: d.value))
        if dimensions not in kinds:
            kinds.append(dimensions)
    return kinds


def cohort_values_sql(cohorts: list[Cohort]) -> str:
    """VALUES rows pairing each cohort year with the position of the requested cohort it belongs to."""
    pairs = []
    for number, cohort in enumerate(cohorts):
        for year in sorted(cohort.years):
            if not SAFE_YEAR.match(year):
                raise ValueError(f"{year!r} is not a valid cohort year")
            pairs.append(f"('{year}', {number})")
    return ", ".join(pairs)


def group_value_sql(dimension: GroupDimension) -> str:
    """A student's group value: matched ignoring case and spaces, or UNKNOWN if blank or not on the list."""
    column = f"UPPER(REPLACE(s.{dimension.value}, ' ', ''))"
    if dimension in OPEN_DIMENSIONS:
        return f"COALESCE(NULLIF({column}, ''), '{normalize(UNKNOWN)}')"
    listed = ", ".join("'" + normalize(v).replace("'", "''") + "'" for v in sorted(ALLOWED_VALUES[dimension]))
    return f"CASE WHEN {column} IN ({listed}) THEN {column} ELSE '{normalize(UNKNOWN)}' END"


def filters_sql(filters: Group) -> str:
    """A WHERE clause keeping the rows that match every filter, or nothing when there are no filters."""
    # Values were checked against the dimension's list (or are an open dimension's name), and quotes are doubled.
    conditions = []
    for part in sorted(filters.parts, key=lambda p: p.dimension.value):
        value = normalize(part.value).replace("'", "''")
        conditions.append(f"{group_value_sql(part.dimension)} = '{value}'")
    return f"WHERE {' AND '.join(conditions)}" if conditions else ""


def members_sql(student_sql: str, cohort_values: str, dimensions: tuple[GroupDimension, ...], filters: Group = EVERYONE, split: tuple[str, ...] = ()) -> str:
    """The start of a group query: the students of every requested cohort that match the filters, with their group values."""
    # Dimension names come from the GroupDimension enum, so they are safe to write into the query.
    inner = "".join(f", {group_value_sql(d)} AS {d.value}" for d in dimensions)
    outcome = ", s.outcome AS outcome" if split else ""
    return f"""
WITH cohort_numbers(cohort, cohort_no) AS (VALUES {cohort_values}),
students AS ({student_sql}),
members AS (
    SELECT c.cohort_no AS cohort_no, s.student_id AS student_id, s.in_scope AS in_scope, s.has_answer AS has_answer,
           s.achieved AS achieved, s.exclusion_reason AS exclusion_reason{outcome}{inner}
    FROM students s
    JOIN cohort_numbers c ON c.cohort = s.cohort
    {filters_sql(filters)}
)"""


def group_query(student_sql: str, cohort_values: str, dimensions: tuple[GroupDimension, ...], filters: Group = EVERYONE, split: tuple[str, ...] = ()) -> str:
    """The query that counts one kind of group: one GROUP BY over the students of every requested cohort."""
    outer = "".join(f", {d.value}" for d in dimensions)
    # Split values come from a measure's file (e.g. D, F, W), never from the data or a request.
    splits = "".join(f",\n       SUM(CASE WHEN has_answer = 1 AND outcome = '{value}' THEN 1 ELSE 0 END) AS split_{value}" for value in split)
    return members_sql(student_sql, cohort_values, dimensions, filters, split) + f"""
SELECT cohort_no{outer},
       SUM(CASE WHEN in_scope = 1 THEN 1 ELSE 0 END) AS n_members,
       SUM(CASE WHEN has_answer = 1 THEN 1 ELSE 0 END) AS denominator,
       SUM(achieved) AS numerator,
       COUNT(DISTINCT CASE WHEN has_answer = 1 THEN student_id END) AS n_students,
       SUM(CASE WHEN in_scope = 0 THEN 1 ELSE 0 END) AS n_out_of_scope{splits}
FROM members
GROUP BY cohort_no{outer}
"""


def reasons_query(student_sql: str, cohort_values: str, dimensions: tuple[GroupDimension, ...], filters: Group = EVERYONE) -> str:
    """The query that counts the left-out rows of one kind of group, by the reason they were left out."""
    outer = "".join(f", {d.value}" for d in dimensions)
    return members_sql(student_sql, cohort_values, dimensions, filters) + f"""
SELECT cohort_no{outer}, exclusion_reason, COUNT(*) AS n_excluded
FROM members
WHERE in_scope = 1 AND has_answer = 0
GROUP BY cohort_no{outer}, exclusion_reason
"""


def read_reasons(connection, query: str, group_columns: int) -> dict[tuple, dict[ExclusionReason, int]]:
    """Run a reasons query. Returns (cohort number, group values) -> how many were left out for each reason."""
    cursor = connection.cursor()
    cursor.execute(query)
    reasons = {}
    for row in cursor.fetchall():
        key = (row[0], tuple(row[1 : 1 + group_columns]))
        reasons.setdefault(key, {})[ExclusionReason(row[1 + group_columns])] = int(row[2 + group_columns])
    return reasons


def read_tallies(connection, query: str, group_columns: int, split: tuple[str, ...] = ()) -> dict[tuple, tuple]:
    """Run a group query. Returns (cohort number, group values) -> (in-scope members, denominator, numerator,
    n_students, out of scope, numerator by split value)."""
    cursor = connection.cursor()
    cursor.execute(query)
    tallies = {}
    for row in cursor.fetchall():
        values = tuple(row[1 : 1 + group_columns])
        members, denominator, numerator, n_students, n_out_of_scope = row[1 + group_columns : 6 + group_columns]
        by_value = {value: int(total) for value, total in zip(split, row[6 + group_columns :])}
        tallies[(row[0], values)] = (int(members), int(denominator), as_number(numerator), int(n_students), int(n_out_of_scope), by_value)
    return tallies


def as_number(total) -> int | float:
    """A summed numerator as a whole number when it is one, else a float (PostgreSQL returns decimals)."""
    number = float(total)
    return int(number) if number.is_integer() else round(number, 10)


def largest_reason(excluded: dict[ExclusionReason, int]) -> ExclusionReason | None:
    """The reason with the most students left out. A tie goes to the reason listed first in ExclusionReason."""
    if not excluded:
        return None
    order = list(ExclusionReason)
    return sorted(excluded, key=lambda reason: (-excluded[reason], order.index(reason)))[0]


def to_counts(tally: tuple, excluded: dict[ExclusionReason, int], not_yet_observable: bool, has_split: bool = False) -> Counts:
    """Turn one group's tally into the Counts the runner expects."""
    members, denominator, numerator, n_students, n_out_of_scope, by_value = tally
    return Counts(
        numerator=numerator,
        denominator=denominator,
        n_students=n_students,
        n_excluded=members - denominator,
        n_out_of_scope=n_out_of_scope,
        exclusion_reason=largest_reason(excluded),
        not_yet_observable=not_yet_observable,
        exclusions=excluded,
        split=dict(by_value) if has_split else None,
    )
