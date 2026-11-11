"""Credit momentum: how fast an entering class builds credits in year 1, and whether those who earn more are retained.

The numbers come from the measures:
- year 1 credits attempted and earned from the cohort file (a student with either blank is left out and counted);
- the credit completion ratio, the credit_completion measure's row from run_measure;
- retention by the chosen retention measure, from run_measure, as on every other page.

This module only breaks them down: credit milestones, the first two terms (from the course file, averaged over the
students who took a course here that term) and credit tiers. Groups under min_students() are hidden.

progress is the Credit momentum design's page (meaningful progress toward a degree), from credit_progress.py.
"""
from __future__ import annotations

from pathlib import Path

from ..models import EVERYONE, Cohort, Group, Measure, min_students
from ..run_measures import read_answers, run_measure
from .credit_progress import credit_progress
from .common import (
    SEASONS,
    check_retention,
    connect,
    next_main_term,
    retained_share,
    retention,
    retention_term,
    select_students,
    share,
    shown,
    term_label,
    year_one_credits,
)

MILESTONES = (12, 24, 30)
# The design's credit tiers by credits earned in year 1: (key, label, lowest, highest + 1).
TIERS = (("under_15", "Under 15", 0, 15), ("15_29", "15–29", 15, 30), ("30_plus", "30 or more", 30, None))


def average(values: list[float]) -> float | None:
    """The mean to one decimal, or None for an empty list."""
    return round(sum(values) / len(values), 1) if values else None


def term_credits(connection, cohort: str) -> dict[tuple[str, tuple[str, str]], tuple[float, float]]:
    """Each student's credits attempted and earned here, per term, from the course file."""
    rows = connection.execute(
        """
        SELECT ce.student_id AS student_id, t.academic_year AS year, UPPER(t.academic_term) AS season,
               SUM(COALESCE(ce.number_of_credits_attempted, 0)) AS attempted,
               SUM(COALESCE(ce.number_of_credits_earned, 0)) AS earned
        FROM course_enrollment ce
        JOIN term t ON t.term_id = ce.term_id
        WHERE ce.cohort = ? AND ce.course_id IS NOT NULL
        GROUP BY 1, 2, 3
        """,
        [cohort],
    ).fetchall()
    return {(row["student_id"], (row["year"], row["season"])): (row["attempted"], row["earned"]) for row in rows}


def credit_momentum(cohort: str, filters: Group = EVERYONE, retention_measure: Measure = Measure.RETENTION, database: str | Path | None = None) -> dict:
    """The Credit momentum page: year 1 credits, completion, milestones, the first two terms, and tiers."""
    check_retention(retention_measure)
    connection = connect(database)
    try:
        students = select_students(connection, cohort, filters)
        year_one = year_one_credits(connection, cohort)
        per_term = term_credits(connection, cohort)
        answers, _ = read_answers(retention_measure, cohort, database)
        progress = credit_progress(connection, cohort, students, answers) if len(students) >= min_students() else None
    finally:
        connection.close()

    known = {sid: year_one[sid] for sid in students if sid in year_one}
    context = {
        "retention_term": term_label(retention_term(cohort)) if retention_measure == Measure.FEDERAL_RETENTION else "next academic year",
    }
    if len(students) < min_students() or len(known) < min_students():
        return {"context": context, "status": "suppressed", "students": None, "credits": None, "completion": None, "retention": None, "milestones": [], "terms": [], "tiers": [], "progress": None}

    # The completion ratio is the credit_completion measure's row for these students.
    (completion,) = run_measure(Measure.CREDIT_COMPLETION, [Cohort.of(cohort)], database=database, filters=filters)
    return {
        "context": context,
        "status": "ok",
        "students": len(students),
        "credits": {
            "counted": len(known),
            "left_out": shown(len(students) - len(known)),
            "avg_attempted": average([attempted for attempted, _ in known.values()]),
            "avg_earned": average([earned for _, earned in known.values()]),
        },
        "completion": {"counted": completion.denominator, "ratio": completion.metric_rate, "status": completion.status.value},
        "retention": retention(retention_measure, cohort, filters, database),
        "milestones": [milestone(credits, known) for credits in MILESTONES],
        "terms": first_terms(cohort, students, per_term),
        "tiers": tiers(known, answers),
        "progress": progress,
    }


def milestone(credits: int, known: dict) -> dict:
    """Students who earned at least this many credits in year 1, out of those with known credits. Under min_students() is hidden."""
    reached = shown(sum(1 for _, earned in known.values() if earned >= credits))
    return {"credits": credits, "students": reached, "share": share(reached, len(known))}


def first_terms(cohort: str, students: dict, per_term: dict) -> list[dict]:
    """Average credits attempted and earned in the starting term and the next fall or spring term."""
    start_terms = {row["cohort_term"] for row in students.values()} & set(SEASONS)
    named = len(start_terms) == 1
    columns = []
    for position, label in enumerate(("First term", "Second term")):
        attempted, earned = [], []
        term = None
        for student_id, student in students.items():
            if student["cohort_term"] not in SEASONS:
                continue
            term = (cohort, student["cohort_term"])
            if position == 1:
                term = next_main_term(term)
            credits = per_term.get((student_id, term))
            if credits:
                attempted.append(credits[0])
                earned.append(credits[1])
        hidden = len(attempted) < min_students()
        columns.append(
            {
                "label": term_label(term) if named and term else label,
                "enrolled": None if hidden else len(attempted),
                "avg_attempted": None if hidden else average(attempted),
                "avg_earned": None if hidden else average(earned),
            }
        )
    return columns


def tiers(known: dict, answers: dict) -> list[dict]:
    """Students by credits earned in year 1, and how many of each tier were retained."""
    rows = []
    for key, label, lowest, highest in TIERS:
        members = {sid for sid, (_, earned) in known.items() if earned >= lowest and (highest is None or earned < highest)}
        if len(members) < min_students():
            rows.append({"key": key, "label": label, "students": None, "share": None, "retained": None, "rate": None})
            continue
        retained = retained_share(answers, members)
        rows.append({"key": key, "label": label, "students": len(members), "share": share(len(members), len(known)), "retained": retained["retained"], "rate": retained["rate"]})
    return rows
