"""Gateway courses: how students get through each first-year gateway course, and whether they are retained.

A gateway course is one the institution flags as gateway math (M) or English (E) in the PDP course file. Only the
grades it flags count, and only in the cohort's first academic year, as in the PDP's own gateway measure. If a cohort
has no flagged grades, the page lists no courses and says so; it never guesses which courses are gateway.

Passing uses the PDP's gateway line, not the DFW one: a grade of 1.0 or higher, or a P (the dictionary's
CompletedGatewayMathYear1 and CompletedGatewayEnglishYear1). F and W don't pass. Grades that aren't final
(incomplete, audit, missing) are left out and counted apart, as in the DFW measure.

A try is a term: several rows in one term (duplicate class rows, data finding 9) are one try, passed if any passed.
Each student's path through a course: passed on the first try, failed and passed on a later try, failed and failed
again, or failed and didn't retake (all within year 1).

This module only counts. The comparisons (the filtered students against everyone else who took a course, and each
course pair against everyone else) are the gap finder's job, which sits on top of measures: gap_finder/gateway.py
runs these counts through gap_finder.compare, and the API calls it. Groups under min_students() are hidden.
Only course pairs taken by 10 or more students are sent for comparing (MIN_PAIR_STUDENTS).
"""
from __future__ import annotations

from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

from ..calculations.dfw import grade_result
from ..data_access import ReadSnapshot
from ..models import EVERYONE, Group, Measure, min_students
from ..run_measures import read_answers
from .common import (
    check_retention,
    page_source,
    course_rows,
    retained_share,
    retention,
    retention_term,
    select_students,
    shown,
    term_label,
)

SUBJECTS = ("E", "M")
# The PDP's gateway pass line: a grade of 1.0 or higher (the DFW measure's line is 2.0).
GATEWAY_PASS_AT = 1.0
PATH_STEPS = ("first", "retook_passed", "retook_not", "no_retake")
# Course pairs are compared only with this many students. Not a privacy rule: the gap finder corrects for how many
# comparisons it runs, so thousands of tiny pairs would make real gaps read as noise.
MIN_PAIR_STUDENTS = 10


def gateway_passed(grade: str | None) -> bool | None:
    """True for a gateway pass (1.0 or higher, or P), False for anything lower, F or W, None if it isn't a final grade."""
    if grade_result(grade) is None:
        return None
    code = grade.strip().upper()
    if code == "P":
        return True
    if code in ("F", "W"):
        return False
    return float(code) >= GATEWAY_PASS_AT


def gateway_courses(cohort: str, filters: Group = EVERYONE, retention_measure: Measure = Measure.RETENTION, database: str | Path | None = None, *, snapshot: ReadSnapshot | None = None) -> dict:
    """Run the page with a borrowed snapshot, or own one local read transaction."""
    with page_source(database, snapshot) as source:
        return _gateway_courses(cohort, filters, retention_measure, database=source.positional, connection=source.named)


def _gateway_courses(cohort: str, filters: Group = EVERYONE, retention_measure: Measure = Measure.RETENTION, database: str | Path | None = None, *, connection) -> dict:
    """The Gateway courses page: each gateway course's student path and retention, and the riskiest course pairs."""
    check_retention(retention_measure)
    everyone = select_students(connection, cohort)
    students = select_students(connection, cohort, filters)
    # Year 1 flagged grades for the whole cohort: the filtered students' own, and everyone else's to compare with.
    flagged_rows = [row for row in course_rows(connection, cohort, everyone) if row["year"] == cohort and row["gateway"] in SUBJECTS]
    first_term_rows = [row for row in course_rows(connection, cohort, students) if is_first_term(row)]
    answers, observable = read_answers(retention_measure, cohort, database)

    start_terms = {row["cohort_term"] for row in students.values()}
    first_term = None
    if len(start_terms) == 1 and next(iter(start_terms)) != "UNKNOWN":
        first_term = term_label((cohort, next(iter(start_terms))))
    context = {
        "flagged": bool(flagged_rows),
        "year_one": cohort,
        "retention_term": term_label(retention_term(cohort)) if retention_measure == Measure.FEDERAL_RETENTION else "next academic year",
        "retention_observed": observable,
        "first_term": first_term,
        "compared": filters != EVERYONE,
        "min_pair_students": max(MIN_PAIR_STUDENTS, min_students()),
    }
    if len(students) < min_students():
        return {"context": context, "status": "suppressed", "students": None, "cohort_retention": None, "courses": [], "hidden_courses": 0, "left_out": None, "pair_counts": [], "pairs_considered": 0}

    cohort_retention = retention(retention_measure, cohort, filters, database)
    return {
        "context": context,
        "status": "ok",
        "students": len(students),
        "cohort_retention": cohort_retention,
        **course_paths(flagged_rows, set(students), filters != EVERYONE, answers),
        **course_pairs(first_term_rows, answers),
    }


def is_first_term(row: dict) -> bool:
    """Whether a course row is in the student's starting term."""
    return row["year"] == row["student"]["cohort"] and row["season"] == row["student"]["cohort_term"]


def student_tries(rows: list[dict]) -> tuple[dict[str, dict[str, list[bool]]], dict[str, set[str]], dict[str, Counter], dict[str, Counter]]:
    """Per course and student, a pass or fail per term in order; plus students with no final grade, names and flags."""
    by_term: dict[str, dict[str, dict[int, list[bool]]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    no_grade: dict[str, set[str]] = defaultdict(set)
    names: dict[str, Counter] = defaultdict(Counter)
    flags: dict[str, Counter] = defaultdict(Counter)
    for row in rows:
        course = row["course"]
        flags[course][row["gateway"]] += 1
        if row["name"]:
            names[course][row["name"]] += 1
        passed = gateway_passed(row["grade"])
        if passed is None:
            no_grade[course].add(row["student_id"])
        else:
            by_term[course][row["student_id"]][row["sort_order"]].append(passed)
    tries = {
        course: {sid: [any(terms[order]) for order in sorted(terms)] for sid, terms in takers.items()}
        for course, takers in by_term.items()
    }
    return tries, no_grade, names, flags


def path_counts(tries: dict[str, list[bool]]) -> dict:
    """First-try passes, passes in the end, and each step of the path, for these students. Steps hide under min_students()."""
    steps = Counter()
    for passes in tries.values():
        if passes[0]:
            steps["first"] += 1
        elif len(passes) == 1:
            steps["no_retake"] += 1
        elif any(passes[1:]):
            steps["retook_passed"] += 1
        else:
            steps["retook_not"] += 1
    return {
        "students": len(tries),
        "first_pass": steps["first"],
        "passed": steps["first"] + steps["retook_passed"],
        "path": {step: shown(steps[step]) for step in PATH_STEPS},
    }


def course_paths(rows: list[dict], students: set[str], compared: bool, answers: dict) -> dict:
    """Each gateway course with min_students() or more of the filtered students: their path, retention, and the group gap."""
    tries, no_grade, names, flags = student_tries(rows)
    courses = []
    hidden = 0
    left_out = 0
    for course, takers in tries.items():
        mine = {sid: passes for sid, passes in takers.items() if sid in students}
        if len(mine) < min_students():
            hidden += 1
            continue
        # Filtered students whose only year 1 grades here weren't final (incomplete, audit, missing).
        left_out += len(no_grade[course] & (students - set(mine)))
        passed = {sid for sid, passes in mine.items() if any(passes)}
        courses.append(
            {
                "course": course,
                "name": names[course].most_common(1)[0][0] if names[course] else None,
                # A course flagged both ways takes the subject most of its grades carry.
                "subject": flags[course].most_common(1)[0][0],
                **path_counts(mine),
                "retained_if_passed": retained_share(answers, passed),
                "retained_if_not_passed": retained_share(answers, set(mine) - passed),
                # Everyone who took the course, filtered or not: what the API compares the filtered students with.
                "all_takers": {"students": len(takers), "first_pass": sum(p[0] for p in takers.values())} if compared else None,
            }
        )
    courses.sort(key=lambda c: (-c["students"], c["course"]))
    return {"courses": courses, "hidden_courses": hidden, "left_out": shown(left_out)}


def course_pairs(rows: list[dict], answers: dict) -> dict:
    """Retention for each gateway course taken with another course in the first term, by MIN_PAIR_STUDENTS or more."""
    first_courses: dict[str, set[str]] = defaultdict(set)
    gateway: set[str] = set()
    for row in rows:
        first_courses[row["student_id"]].add(row["course"])
        if row["gateway"] in SUBJECTS:
            gateway.add(row["course"])

    takers: dict[tuple[str, str], set[str]] = defaultdict(set)
    for student_id, courses in first_courses.items():
        for pair in combinations(sorted(courses), 2):
            if gateway & set(pair):
                takers[pair].add(student_id)

    counted = []
    for pair, who in sorted(takers.items()):
        numbers = retained_share(answers, who)
        if numbers["students"] is not None and numbers["students"] >= MIN_PAIR_STUDENTS:
            counted.append({"courses": list(pair), "students": numbers["students"], "retained": numbers["retained"]})
    return {"pair_counts": counted, "pairs_considered": len(counted)}
