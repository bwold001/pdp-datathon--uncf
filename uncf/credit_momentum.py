"""Credit momentum: how fast an entering class builds credits in year 1, and whether those who earn more are retained.

The numbers come from uncf.metrics:
- year 1 credits attempted and earned from the cohort file (a student with either blank is left out and counted);
- the credit completion ratio, the shared credit_completion measure's own per student ratio, averaged;
- retention by the query's retention type, as on every other page.

This module only breaks them down: credit milestones, the first two terms (from the course file, averaged over the
students who took a course here that term) and credit tiers. Groups under 10 students are hidden.
"""
from __future__ import annotations

from pathlib import Path

from uncf import data, metrics
from uncf.filters import MIN_STUDENTS, CohortQuery, select_students, share, shown
from uncf.metrics import SEASONS, next_main_term, retention_term, term_label

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


def credit_momentum(query: CohortQuery, database: Path | None = None) -> dict:
    """The Credit momentum page: year 1 credits, completion, milestones, the first two terms, and tiers."""
    connection = data.open_database(database)
    try:
        students = select_students(connection, query)
        year_one = metrics.year_one_credits(connection, query.cohort)
        completion = metrics.completion_answers(connection, query.cohort)
        per_term = term_credits(connection, query.cohort)
        answers, observable = metrics.retention_answers(connection, query.cohort, query.retention_type)
        stamp = data.loaded_at(connection)
    finally:
        connection.close()

    known = {sid: year_one[sid] for sid in students if sid in year_one}
    meta = {
        **query.meta(),
        "retention_term": term_label(retention_term(query.cohort)) if query.retention_type == "federal" else "next academic year",
        "loaded_at": stamp,
    }
    if len(students) < MIN_STUDENTS or len(known) < MIN_STUDENTS:
        return {"meta": meta, "status": "suppressed", "students": None, "credits": None, "completion": None, "retention": None, "milestones": [], "terms": [], "tiers": []}

    ratio = metrics.credit_completion(completion, students)
    return {
        "meta": meta,
        "status": "ok",
        "students": len(students),
        "credits": {
            "counted": len(known),
            "left_out": shown(len(students) - len(known)),
            "avg_attempted": average([attempted for attempted, _ in known.values()]),
            "avg_earned": average([earned for _, earned in known.values()]),
        },
        "completion": {"counted": ratio["counted"], "ratio": ratio["ratio"], "status": ratio["status"]},
        "retention": metrics.retention(answers, observable, students, query.retention_type),
        "milestones": [
            {"credits": credits, "students": (n := sum(1 for _, earned in known.values() if earned >= credits)), "share": share(n, len(known))}
            for credits in MILESTONES
        ],
        "terms": first_terms(query.cohort, students, per_term),
        "tiers": tiers(known, answers),
    }


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
        hidden = len(attempted) < MIN_STUDENTS
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
        if len(members) < MIN_STUDENTS:
            rows.append({"key": key, "label": label, "students": None, "share": None, "retained": None, "rate": None})
            continue
        retained = metrics.retained_share(answers, members)
        rows.append({"key": key, "label": label, "students": len(members), "share": share(len(members), len(known)), "retained": retained["retained"], "rate": retained["rate"]})
    return rows
