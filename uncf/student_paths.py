"""Student paths: where each student in an entering class is, term by term.

Each student is followed from the term they entered through the next fall or spring terms (two by default, up to
five). In each term a student is:

- here: took a course at this college that term (a course file row with a course);
- credential: not here, but earned a credential here in an earlier academic year;
- elsewhere: neither, but the course file records enrollment at another college that term;
- stopped: no record at all that term.

The page's retention numbers come from uncf.metrics, by the query's retention type, so they match every other page.
The statuses come from term records, so they can differ from retention. Groups under 10 students are hidden.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path

from measures.calculations.sql_counts import normalize
from measures.models import ALLOWED_VALUES, GroupDimension
from uncf import data, metrics
from uncf.filters import (
    FILTER_NAMES,
    MIN_STUDENTS,
    CohortQuery,
    InvalidFilter,
    listed_value,
    select_students,
    share,
    shown,
)
from uncf.metrics import SEASONS, next_main_term, term_label

STATUSES = ("here", "credential", "elsewhere", "stopped")
DEFAULT_TERMS = 3
MAX_TERMS = 6
# Carnegie classes of the other college, as the course file writes them (sometimes cut short).
FOUR_YEAR = ("doctoral universities", "master's colleges & universities", "baccalaureate colleges", "special focus four-year")
TWO_YEAR = ("associate's colleges", "special focus two-year")


def college_kind(carnegie: str | None) -> str:
    """four_year, two_year or other, from the other college's Carnegie class (pipe-separated when several)."""
    kinds = set()
    for part in (carnegie or "").split("|"):
        part = part.strip().lower()
        if not part:
            continue
        # The file cuts long values short, so a cut-off part still matches the start of its class.
        if any(name.startswith(part) or part.startswith(name) for name in FOUR_YEAR):
            kinds.add("four_year")
        elif any(name.startswith(part) or part.startswith(name) for name in TWO_YEAR):
            kinds.add("two_year")
        else:
            kinds.add("other")
    return kinds.pop() if len(kinds) == 1 else "other"


def term_records(connection, cohort: str) -> dict[tuple[str, tuple[str, str]], dict]:
    """Each student's record per term in the cohort's course file rows: here or elsewhere, and other colleges' types."""
    rows = connection.execute(
        """
        SELECT ce.student_id AS student_id, t.academic_year AS year, UPPER(t.academic_term) AS season,
               ce.course_id IS NOT NULL AS here,
               CASE WHEN ce.course_id IS NULL AND UPPER(TRIM(ce.enrolled_at_other_institution_s)) = 'Y' THEN 1 ELSE 0 END
                   AS elsewhere,
               ce.c_enrollment_record_at_other AS carnegie
        FROM course_enrollment ce
        JOIN term t ON t.term_id = ce.term_id
        WHERE ce.cohort = ?
        """,
        [cohort],
    ).fetchall()
    records: dict[tuple[str, tuple[str, str]], dict] = {}
    for row in rows:
        record = records.setdefault((row["student_id"], (row["year"], row["season"])), {"here": False, "elsewhere": False, "kinds": set()})
        record["here"] = record["here"] or bool(row["here"])
        if row["elsewhere"]:
            record["elsewhere"] = True
            record["kinds"].add(college_kind(row["carnegie"]))
    return records


def academic_year_number(cohort: str, term: tuple[str, str]) -> int:
    """Which academic year of the student's a term is in: 1 for the cohort year, 2 for the next."""
    return int(term[0][:4]) - int(cohort[:4]) + 1


def status_in(record: dict | None, credential_year: int | None, year_number: int) -> str:
    """here, credential, elsewhere or stopped for one term. A credential counts from the academic year after it."""
    if record and record["here"]:
        return "here"
    if credential_year is not None and credential_year < year_number:
        return "credential"
    if record and record["elsewhere"]:
        return "elsewhere"
    return "stopped"


def follow(students: dict, cohort: str, terms: int, records: dict, credentials: dict, observed: set) -> dict[str, list]:
    """Each placed student's terms and status in each, from the entering term on. Unplaced students are left out."""
    paths = {}
    for student_id, student in students.items():
        if student["cohort_term"] not in {normalize(season) for season in SEASONS}:
            continue
        term = (cohort, student["cohort_term"])
        steps = [(term, "entered")]
        for _ in range(terms - 1):
            term = next_main_term(term)
            if term not in observed:
                steps.append((term, "not_observed"))
            else:
                steps.append((term, status_in(records.get((student_id, term)), credentials.get(student_id), academic_year_number(cohort, term))))
        paths[student_id] = steps
    return paths


def column(statuses: list[str], total: int) -> dict:
    """One term's counts and shares of the students followed. Counts under 10 are hidden."""
    counts = Counter(statuses)
    numbers = {status: shown(counts[status]) for status in STATUSES}
    numbers["anywhere"] = shown(counts["here"] + counts["elsewhere"])
    numbers["not_observed"] = shown(counts["not_observed"])
    numbers["shares"] = {key: share(value, total) for key, value in numbers.items() if key != "not_observed"}
    return numbers


def student_paths(query: CohortQuery, terms: int = DEFAULT_TERMS, group_by: str | None = None, database: Path | None = None) -> dict:
    """The Student paths page: class size, status per term, moves between terms, transfers and retention."""
    if not 2 <= terms <= MAX_TERMS:
        raise InvalidFilter(f"terms must be 2 to {MAX_TERMS}.")
    if group_by is not None and group_by not in FILTER_NAMES:
        raise InvalidFilter(f"Student paths can't be grouped by {group_by!r}.")
    connection = data.open_database(database)
    try:
        students = select_students(connection, query)
        records = term_records(connection, query.cohort)
        credentials = metrics.credential_years(connection, query.cohort)
        observed = metrics.observed_terms(connection)
        answers, observable = metrics.retention_answers(connection, query.cohort, query.retention_type)
        stamp = data.loaded_at(connection)
    finally:
        connection.close()

    paths = follow(students, query.cohort, terms, records, credentials, observed)
    total = len(paths)
    start_terms = {students[sid]["cohort_term"] for sid in paths}
    named = len(start_terms) == 1 and total > 0
    labels = [term_label(term) for term, _ in next(iter(paths.values()))] if named else None
    meta = {
        **query.meta(),
        "terms": {"entered": labels[0], "next": labels[1], "year2": labels[2] if terms > 2 else None} if labels else None,
        "term_labels": labels,
        "group_by": group_by,
        "loaded_at": stamp,
    }
    if total < MIN_STUDENTS:
        return {"meta": meta, "status": "suppressed", "students": None, "left_out": None, "columns": None, "path": [], "moves": None, "transfers": None, "retention": None, "groups": []}

    by_position = [[steps[position][1] for steps in paths.values()] for position in range(1, terms)]
    path = [{"position": position, "label": labels[position] if labels else None, **column(statuses, total)} for position, statuses in enumerate(by_position, start=1)]
    last = terms - 1
    transfers = Counter()
    for student_id, steps in paths.items():
        term, status = steps[last]
        if status == "elsewhere":
            kinds = records[(student_id, term)]["kinds"]
            transfers[next(iter(kinds)) if len(kinds) == 1 else "other"] += 1
    return {
        "meta": meta,
        "status": "ok",
        "students": total,
        "left_out": shown(len(students) - total),
        # The first two terms after entering, by the names the page has always used.
        "columns": {"next": path[0], "year2": path[1] if len(path) > 1 else None},
        "path": path,
        "moves": moves(paths, 1, 2) if terms > 2 else [],
        "moves_by_step": [{"from_position": step, "to_position": step + 1, "moves": moves(paths, step, step + 1)} for step in range(1, last)],
        "transfers": {
            "students": shown(sum(transfers.values())),
            "four_year": shown(transfers["four_year"]),
            "two_year": shown(transfers["two_year"]),
            "other": shown(transfers["other"]),
        },
        # Every selected student, placed or not, so it matches the other pages and the Results API.
        "retention": metrics.retention(answers, observable, students, query.retention_type),
        "groups": groups(paths, students, group_by, answers, observable, query.retention_type) if group_by else [],
    }


def moves(paths: dict[str, list], before: int, after: int) -> list[dict]:
    """How many students went from each status in one term to each status in a later term."""
    counts = Counter((steps[before][1], steps[after][1]) for steps in paths.values())
    return [{"from": a, "to": b, "students": shown(counts[(a, b)])} for a in STATUSES for b in STATUSES]


def groups(paths: dict, students: dict, dimension: str, answers: dict, observable: bool, retention_type: str) -> list[dict]:
    """The page's numbers for each value of one filter, so groups can be compared side by side."""
    rows = []
    for value in sorted(ALLOWED_VALUES[GroupDimension(dimension)]):
        members = {sid: steps for sid, steps in paths.items() if listed_value(dimension, students[sid][dimension]) == value}
        if not members:
            continue
        if len(members) < MIN_STUDENTS:
            rows.append({"value": value, "students": None, "path": [], "retention": None})
            continue
        positions = len(next(iter(members.values())))
        path = [{"position": p, **column([steps[p][1] for steps in members.values()], len(members))} for p in range(1, positions)]
        rows.append({"value": value, "students": len(members), "path": path, "retention": metrics.retention(answers, observable, members, retention_type)})
    return rows
