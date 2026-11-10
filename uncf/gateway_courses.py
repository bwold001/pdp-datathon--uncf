"""Gateway courses: how students do in first year gateway math and English, and whether they are retained.

A gateway course is one the institution flags as gateway math (M) or English (E) in the PDP course file. If a cohort
has no flagged courses in year 1, the page says so and infers them instead: year 1 college level courses whose prefix
is a math or English one.

Outcomes and retention come from uncf.metrics: each student's first attempt in year 1 is passed, D, F or W by the
shared grade rules, and retention is the query's retention type, as on every other page. Grades that aren't final
(incomplete, audit, missing) are left out and counted apart.

Riskiest course pairs: two courses taken together in the student's first term, by 10 or more students, whose
retention is below the whole cohort's. The three furthest below are shown. Groups under 10 students are hidden.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

from uncf import data, metrics
from uncf.cohort import MIN_STUDENTS, CohortQuery, select_students, shown
from uncf.metrics import retention_term, term_label

TOP_PAIRS = 3
# Used only when the institution flags no gateway courses for a cohort: college level courses with these prefixes.
INFERRED_PREFIXES = {"M": {"MATH", "MTH", "MAT", "MA", "STAT"}, "E": {"ENG", "ENGL"}}
SUBJECTS = ("E", "M")
OUTCOMES = {"pass": "passed", "D": "d", "F": "f", "W": "w", None: "other"}


def subject_of(row: dict, flagged: bool) -> str | None:
    """M or E when the course counts as gateway math or English, else None: the flag, or the inferred prefix."""
    if flagged:
        return row["gateway"] if row["gateway"] in SUBJECTS else None
    if row["course_type"] != "CU":
        return None
    for subject, prefixes in INFERRED_PREFIXES.items():
        if row["prefix"] in prefixes:
            return subject
    return None


def gateway_courses(query: CohortQuery, database: Path | None = None) -> dict:
    """The Gateway courses page: each gateway course's outcomes and retention, and the riskiest course pairs."""
    connection = data.open_database(database)
    try:
        everyone = select_students(connection, CohortQuery(query.cohort, retention_type=query.retention_type))
        students = select_students(connection, query)
        # Whether the institution flags gateway courses at all this year is read across the whole cohort.
        all_rows = [row for row in metrics.course_rows(connection, query.cohort, everyone) if row["year"] == query.cohort]
        answers, observable = metrics.retention_answers(connection, query.cohort, query.retention_type)
        stamp = data.loaded_at(connection)
    finally:
        connection.close()

    flagged = any(row["gateway"] in SUBJECTS for row in all_rows)
    mine = [row for row in all_rows if row["student_id"] in students]
    start_terms = {row["cohort_term"] for row in students.values()}
    first_term = None
    if len(start_terms) == 1 and next(iter(start_terms)) != "UNKNOWN":
        first_term = term_label((query.cohort, next(iter(start_terms))))

    meta = {
        **query.meta(),
        "flagged": flagged,
        "retention_term": term_label(retention_term(query.cohort)) if query.retention_type == "federal" else "next academic year",
        "retention_observed": observable,
        "first_term": first_term,
        "min_pair_students": MIN_STUDENTS,
        "loaded_at": stamp,
    }
    if len(students) < MIN_STUDENTS:
        return {"meta": meta, "status": "suppressed", "students": None, "cohort_retention": None, "courses": [], "hidden_courses": 0, "left_out": None, "pairs": [], "pairs_considered": 0}

    cohort_retention = metrics.retention(answers, observable, students, query.retention_type)
    outcomes = course_outcomes(mine, flagged, answers)
    return {
        "meta": meta,
        "status": "ok",
        "students": len(students),
        "cohort_retention": cohort_retention,
        **outcomes,
        **course_pairs(mine, students, answers, cohort_retention["rate"]),
    }


def course_outcomes(rows: list[dict], flagged: bool, answers: dict) -> dict:
    """Each gateway course with 10 or more students: outcomes of their first attempt, and their retention."""
    first_attempts: dict[tuple[str, str], dict] = {}
    subjects: dict[str, str] = {}
    names: dict[str, Counter] = defaultdict(Counter)
    for row in sorted(rows, key=lambda r: (r["sort_order"], r["enrollment_id"])):
        subject = subject_of(row, flagged)
        if subject is None:
            continue
        subjects.setdefault(row["course"], subject)
        if row["name"]:
            names[row["course"]][row["name"]] += 1
        first_attempts.setdefault((row["course"], row["student_id"]), row)

    by_course: dict[str, dict[str, set]] = defaultdict(lambda: defaultdict(set))
    for (course, student_id), row in first_attempts.items():
        by_course[course][OUTCOMES[row["result"]]].add(student_id)

    courses = []
    hidden = 0
    left_out = 0
    for course, outcomes in by_course.items():
        not_passed = outcomes["d"] | outcomes["f"] | outcomes["w"]
        graded = outcomes["passed"] | not_passed
        if len(graded) < MIN_STUDENTS:
            hidden += 1
            continue
        left_out += len(outcomes["other"])
        courses.append(
            {
                "course": course,
                "name": names[course].most_common(1)[0][0] if names[course] else None,
                "subject": subjects[course],
                "students": len(graded),
                "passed": len(outcomes["passed"]),
                "d": len(outcomes["d"]),
                "f": len(outcomes["f"]),
                "df": len(outcomes["d"]) + len(outcomes["f"]),
                "w": len(outcomes["w"]),
                "other": shown(len(outcomes["other"])),
                "shares": {key: round(len(outcomes[key]) / len(graded), 4) for key in ("passed", "d", "f", "w")},
                "retained_if_passed": metrics.retained_share(answers, outcomes["passed"]),
                "retained_if_not_passed": metrics.retained_share(answers, not_passed),
            }
        )
    # English first, then math, as in the design; each by how many students took it.
    courses.sort(key=lambda c: (SUBJECTS.index(c["subject"]), -c["students"], c["course"]))
    return {"courses": courses, "hidden_courses": hidden, "left_out": shown(left_out)}


def course_pairs(rows: list[dict], students: dict, answers: dict, cohort_rate: float | None) -> dict:
    """Pairs of courses taken together in the student's first term whose retention is below the cohort's."""
    if cohort_rate is None:
        return {"pairs": [], "pairs_considered": 0}
    first_courses: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        if row["year"] == row["student"]["cohort"] and row["season"] == row["student"]["cohort_term"]:
            first_courses[row["student_id"]].add(row["course"])

    takers: dict[tuple[str, str], set[str]] = defaultdict(set)
    for student_id, courses in first_courses.items():
        for pair in combinations(sorted(courses), 2):
            takers[pair].add(student_id)

    considered = []
    for pair, who in takers.items():
        numbers = metrics.retained_share(answers, who)
        if numbers["students"] is None:
            continue
        considered.append({"courses": list(pair), **numbers, "gap": round((numbers["rate"] - cohort_rate) * 100, 1)})
    below = sorted((pair for pair in considered if pair["gap"] < 0), key=lambda pair: (pair["gap"], -pair["students"]))
    return {"pairs": below[:TOP_PAIRS], "pairs_considered": len(considered)}
