"""Meaningful progress toward a degree, the Credit momentum design without major.

It answers two questions for an entering class: did each student do the minimum in year 1, and are they on pace to
finish on time? Then why the students under the minimum fell short, and whether those who did the minimum kept it up
in year 2. Retention by group uses the chosen retention measure's answers (read_answers), as on every other page.

Credits that count are earned credits in courses PDP marks college-level (CU) or developmental credit that applies
(CC), from the course file, in every term of the year. One degree total for every student: this view doesn't use
major. The minimum is checked year by year, not as a running total. Failed or withdrew uses the DFW measure's grade
rule (dfw.grade_result). Every count of students goes through shown(): 1 to 9 is hidden (None), never shown as 0.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Iterable

from ..calculations.dfw import grade_result
from .common import SEASONS, check_cohort, next_main_term, next_year, observed_terms, retained_share, share, shown, term_label

# The school's settings (Benedict, 2026-11-10). A school with other rules changes them here, not in a fork.
MINIMUM_CREDITS = 24  # a year: 12 a semester, the federal full-time minimum
DEGREE_CREDITS = 120
YEARS_TO_DEGREE = 4
HIGHER_DEGREE_CREDITS = 125  # the design's "if the school sets 125 credits"
COUNTING_COURSE_TYPES = ("CU", "CC")  # college-level, and developmental credit that applies to a degree

# Year 1 groups, in the design's order: on pace, did the minimum but slower, below it, and stopped after the first term.
BANDS = ("pace", "minimum", "below", "stopped")
# Why students still taking courses ended year 1 under the minimum, in the design's order.
REASONS = ("under", "failed", "withdrew", "not_counted")


def settings() -> dict:
    """The rules every number on the page uses, so the page can say them."""
    return {
        "minimum": MINIMUM_CREDITS,
        "degree_credits": DEGREE_CREDITS,
        "years": YEARS_TO_DEGREE,
        "pace": DEGREE_CREDITS / YEARS_TO_DEGREE,
        "higher_degree_credits": HIGHER_DEGREE_CREDITS,
        "higher_pace": HIGHER_DEGREE_CREDITS / YEARS_TO_DEGREE,
        "counting_course_types": list(COUNTING_COURSE_TYPES),
    }


def course_credits(connection: sqlite3.Connection, cohort: str) -> dict[str, dict]:
    """Each student's year 1 and year 2 credits here, from the course file.

    Per student: credits that count (y1, y2), all credits attempted and earned in year 1, year 1 credits lost to F
    grades and to withdrawals, whether they took any course in year 2, and the terms they attempted credits in.
    """
    check_cohort(cohort)
    year_two = next_year(cohort)
    rows = connection.execute(
        """
        SELECT ce.student_id AS student_id, t.academic_year AS year, UPPER(t.academic_term) AS season,
               UPPER(TRIM(ce.course_type)) AS course_type, ce.grade AS grade,
               COALESCE(ce.number_of_credits_attempted, 0) AS attempted, COALESCE(ce.number_of_credits_earned, 0) AS earned
        FROM course_enrollment ce
        JOIN term t ON t.term_id = ce.term_id
        WHERE ce.cohort = ? AND ce.course_id IS NOT NULL AND t.academic_year IN (?, ?)
        """,
        [cohort, cohort, year_two],
    ).fetchall()
    credits: dict[str, dict] = {}
    for row in rows:
        student = credits.setdefault(row["student_id"], empty_credits())
        attempted, earned = float(row["attempted"]), float(row["earned"])
        counts = earned if row["course_type"] in COUNTING_COURSE_TYPES else 0.0
        if attempted > 0:
            student["terms"].add((row["year"], row["season"]))
        if row["year"] == year_two:
            student["y2_counting"] += counts
            student["y2_any"] = True
            continue
        student["y1_counting"] += counts
        student["y1_attempted"] += attempted
        student["y1_earned"] += earned
        result = grade_result(row["grade"])
        if result == "F":
            student["y1_lost_to_f"] += attempted
        elif result == "W":
            student["y1_lost_to_w"] += attempted
    return credits


def empty_credits() -> dict:
    """A student with no course here in either year."""
    return {
        "y1_counting": 0.0,
        "y1_attempted": 0.0,
        "y1_earned": 0.0,
        "y1_lost_to_f": 0.0,
        "y1_lost_to_w": 0.0,
        "y2_counting": 0.0,
        "y2_any": False,
        "terms": set(),
    }


def below_reason(credits: dict) -> str | None:
    """Why a student still taking courses ended year 1 under the minimum, or None when no reason fits.

    Signed up for fewer than the minimum; else passed enough but not all of it counts; else whichever cost more
    credits, F grades or withdrawals. Incomplete or missing grades, or an even split, explain nothing.
    """
    if credits["y1_attempted"] < MINIMUM_CREDITS:
        return "under"
    if credits["y1_earned"] >= MINIMUM_CREDITS:
        return "not_counted"
    if credits["y1_lost_to_f"] > credits["y1_lost_to_w"]:
        return "failed"
    if credits["y1_lost_to_w"] > credits["y1_lost_to_f"]:
        return "withdrew"
    return None


def counted(students: Iterable[str], total: int | None) -> dict:
    """How many of the students, and their share of total. 1 to 9 is hidden, and so is its share."""
    number = shown(len(set(students)))
    return {"students": number, "share": share(number, total)}


def credit_progress(connection: sqlite3.Connection, cohort: str, students: dict, answers: dict) -> dict:
    """The design's page for these students: the two questions, the year 1 groups, the reasons and year 2."""
    credits = course_credits(connection, cohort)
    observed = observed_terms(connection)
    year_two = next_year(cohort)
    year_two_seen = any(year == year_two for year, _ in observed)
    pace, higher_pace = DEGREE_CREDITS / YEARS_TO_DEGREE, HIGHER_DEGREE_CREDITS / YEARS_TO_DEGREE
    total = len(students)

    bands: dict[str, set[str]] = {band: set() for band in BANDS}
    reasons: dict[str | None, set[str]] = {reason: set() for reason in (*REASONS, None)}
    unsorted: set[str] = set()
    next_terms = set()
    for student_id, student in students.items():
        mine = credits.get(student_id, empty_credits())
        if mine["y1_counting"] >= pace:
            bands["pace"].add(student_id)
        elif mine["y1_counting"] >= MINIMUM_CREDITS:
            bands["minimum"].add(student_id)
        else:
            # Under the minimum: still taking courses the next fall or spring term, or stopped after the first.
            next_term = next_main_term((cohort, student["cohort_term"])) if student["cohort_term"] in SEASONS else None
            if next_term is None or next_term not in observed:
                unsorted.add(student_id)
                continue
            next_terms.add(next_term)
            if next_term in mine["terms"]:
                bands["below"].add(student_id)
                reasons[below_reason(mine)].add(student_id)
            else:
                bands["stopped"].add(student_id)

    did = bands["pace"] | bands["minimum"]
    again = {sid for sid in did if credits.get(sid, empty_credits())["y2_counting"] >= MINIMUM_CREDITS}
    kept_taking = {sid for sid in did - again if credits.get(sid, empty_credits())["y2_any"]}
    below_total = shown(len(bands["below"]))
    did_total = shown(len(did))
    return {
        "settings": settings(),
        # The term "stopped" looks at, when every student under the minimum shares it, e.g. Spring 2023.
        "next_term": term_label(next(iter(next_terms))) if len(next_terms) == 1 else None,
        "year_two": year_two,
        "minimum": counted(did, total),
        "pace": counted(bands["pace"], total),
        "higher_pace": counted({sid for sid in students if credits.get(sid, empty_credits())["y1_counting"] >= higher_pace}, total),
        "two_year_pace": two_year_pace(students, credits, pace, total, year_two_seen),
        "bands": [{"key": band, **counted(bands[band], total), "retention": retained_share(answers, bands[band])} for band in BANDS],
        # Under the minimum, but their next term isn't in the data yet (or their start term is unknown).
        "unsorted": shown(len(unsorted)),
        "below": {
            "students": below_total,
            "reasons": [{"key": reason, **counted(reasons[reason], below_total)} for reason in REASONS],
            "unexplained": shown(len(reasons[None])),
        },
        "year_two_follow_up": {
            "status": "ok" if year_two_seen else "not_yet_observable",
            "students": did_total,
            "again": counted(again, did_total) if year_two_seen else {"students": None, "share": None},
            "kept_taking_courses": counted(kept_taking, did_total) if year_two_seen else {"students": None, "share": None},
            "no_courses": counted(did - again - kept_taking, did_total) if year_two_seen else {"students": None, "share": None},
        },
        "both_years": counted(again, total) if year_two_seen else {"students": None, "share": None},
    }


def two_year_pace(students: dict, credits: dict, pace: float, total: int, year_two_seen: bool) -> dict:
    """Students still on pace after two years: credits that count in years 1 and 2 at least twice the yearly pace."""
    if not year_two_seen:
        return {"status": "not_yet_observable", "students": None, "share": None}
    on_pace = set()
    for student_id in students:
        mine = credits.get(student_id, empty_credits())
        if mine["y1_counting"] + mine["y2_counting"] >= 2 * pace:
            on_pace.add(student_id)
    return {"status": "ok", **counted(on_pace, total)}
