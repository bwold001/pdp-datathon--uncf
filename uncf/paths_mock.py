"""MOCK year-2 paths for the Explorer's paths chart, until a real endpoint has an owner.

Where each entering student was in their second academic year: back here (the retention flag), at another
college instead (persistence without retention), or no enrollment found. Those who moved are split by the
type of their most recent other college. These definitions and the hiding rule are a proposal, not decided:
see the Explorer design's asks. Hiding follows the measures package: a group under 10 students is hidden.
"""
from __future__ import annotations

import sqlite3
from collections import defaultdict
from itertools import combinations
from pathlib import Path

from measures.models import ALLOWED_VALUES, UNKNOWN, GroupDimension
from measures.run_measures import DEFAULT_DATABASE

MIN_STUDENTS = 10
FOUR_YEAR = {"Doctoral Universities", "Master's Colleges & Universities", "Baccalaureate Colleges", "Special Focus Four-Year"}
TWO_YEAR = {"Associate's Colleges", "Special Focus Two-Year"}

SQL = """
SELECT cm.cohort, cm.retention, cm.persistence, cm.c_most_recent_last_enroll_at_o,
       cm.pell_status_first_year, cm.enrollment_intensity_first_term, cm.cohort_term, cm.enrollment_type,
       s.student_age, s.gender, s.race
FROM cohort_membership cm
JOIN student s ON s.student_id = cm.student_id
"""
# Column order after the first four, matched to the dimensions they hold.
SQL_DIMENSIONS = ["pell", "enrollment_intensity", "cohort_term", "enrollment_type", "age_band", "gender", "race"]


def normalize(text: str) -> str:
    """Compare values the way the measures do: ignoring case and spaces."""
    return text.upper().replace(" ", "")


def group_value(dimension: str, raw: str | None) -> str:
    """The measures' group value: the listed value it matches, or UNKNOWN if blank or not listed."""
    if raw is None or not str(raw).strip():
        return UNKNOWN
    wanted = normalize(str(raw))
    return next((value for value in ALLOWED_VALUES[GroupDimension(dimension)] if normalize(value) == wanted), UNKNOWN)


def college_type(carnegie: str | None) -> str:
    """4-year, 2-year, or not on record, from the most recent other college's Carnegie class."""
    if carnegie in FOUR_YEAR:
        return "four_year"
    if carnegie in TWO_YEAR:
        return "two_year"
    return "not_on_record"


def groupings(dimensions: list[str]) -> list[tuple[str, ...]]:
    """Everyone, every single dimension, and every pair, each sorted the way the saved results key them."""
    return [()] + [tuple(sorted(combo)) for size in (1, 2) for combo in combinations(dimensions, size)]


def build_paths(database: Path = DEFAULT_DATABASE, dimensions: list[str] = SQL_DIMENSIONS) -> dict:
    """Counts for every cohort and grouping: [values, students, here, moved, none, 4-year, 2-year, not on record, status]."""
    tallies: dict = defaultdict(lambda: defaultdict(lambda: [0] * 7))
    keys = groupings(dimensions)
    with sqlite3.connect(database) as connection:
        for cohort, retention, persistence, carnegie, *raw_values in connection.execute(SQL):
            values = {d: group_value(d, raw) for d, raw in zip(SQL_DIMENSIONS, raw_values)}
            for key in keys:
                tally = tallies[(cohort, key)][tuple(values[d] for d in key)]
                tally[0] += 1
                if retention:
                    tally[1] += 1
                elif persistence:
                    tally[2] += 1
                    tally[{"four_year": 4, "two_year": 5, "not_on_record": 6}[college_type(carnegie)]] += 1
                else:
                    tally[3] += 1

    paths: dict = {}
    for (cohort, key), by_values in tallies.items():
        rows = []
        for values, (students, here, moved, none, four, two, unknown) in sorted(by_values.items()):
            label = " x ".join(values) if key else "all"
            if students < MIN_STUDENTS:
                # A hidden group is all blank, never 0.
                rows.append([label, None, None, None, None, None, None, None, "suppressed"])
                continue
            split = [four, two, unknown] if moved >= MIN_STUDENTS else [None, None, None]
            rows.append([label, students, here, moved, none, *split, "ok"])
        paths.setdefault(cohort, {})[" x ".join(key) if key else "all"] = rows
    return paths
