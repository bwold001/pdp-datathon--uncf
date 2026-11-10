"""A tiny normalized database for the Explorer tests: only the tables and columns the Explorer reads."""
from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE data_provider (provider_id INTEGER PRIMARY KEY, loaded_at TEXT);
CREATE TABLE student (student_id TEXT PRIMARY KEY, race TEXT, gender TEXT, student_age TEXT, ethnicity TEXT, first_gen TEXT);
CREATE TABLE cohort_membership (
    student_id TEXT, cohort TEXT, cohort_term TEXT, enrollment_type TEXT, enrollment_intensity_first_term TEXT,
    pell_status_first_year TEXT, number_of_credits_attempted_yr_1 REAL, number_of_credits_earned_yr_1 REAL,
    retention INTEGER, persistence INTEGER, gateway_math_status TEXT, completed_gateway_math_year1 TEXT,
    gateway_english_status TEXT, completed_gateway_english_year1 TEXT,
    first_year_to_bachelors_at_coh INTEGER, first_year_to_a_or_c_at_cohort INTEGER,
    PRIMARY KEY (student_id, cohort)
);
CREATE TABLE term (term_id INTEGER PRIMARY KEY, academic_year TEXT, academic_term TEXT, sort_order INTEGER);
CREATE TABLE course (course_id INTEGER PRIMARY KEY, course_prefix TEXT, course_number TEXT);
CREATE TABLE course_enrollment (
    enrollment_id INTEGER PRIMARY KEY, student_id TEXT, cohort TEXT, course_id INTEGER, term_id INTEGER,
    section_id TEXT, course_name TEXT, grade TEXT, delivery_method TEXT, math_or_english_gateway TEXT,
    course_type TEXT, number_of_credits_attempted REAL, number_of_credits_earned REAL,
    enrolled_at_other_institution_s TEXT, c_enrollment_record_at_other TEXT
);
"""
LOADED_AT = "2026-11-09T12:00:00"
SEASON_ORDER = {"FALL": 1, "WINTER": 2, "SPRING": 3, "SUMMER": 4}


def student(student_id: str, cohort: str = "2023-24", **values: str) -> dict:
    """A cohort member: a first-time, full-time Fall starter unless values say otherwise (as the raw file spells them).

    retention is the PDP flag (1, 0 or None); credential_year is the academic year of a first credential here.
    """
    return {
        "student_id": student_id,
        "cohort": cohort,
        "cohort_term": values.get("cohort_term", "FALL"),
        "enrollment_type": values.get("enrollment_type", "First-Time"),
        "enrollment_intensity": values.get("enrollment_intensity", "Full-Time"),
        "pell": values.get("pell", "Y"),
        "gender": values.get("gender", "F"),
        "race": values.get("race", "Asian"),
        "age_band": values.get("age_band", "20 and younger"),
        "attempted": values.get("attempted"),
        "earned": values.get("earned"),
        "retention": values.get("retention"),
        "credential_year": values.get("credential_year"),
        "ethnicity": values.get("ethnicity"),
    }


def here(student_id: str, year: str, season: str, cohort: str = "2023-24", **course: str) -> dict:
    """A course taken here by the student in one term."""
    return {"student_id": student_id, "cohort": cohort, "year": year, "season": season, "course": True, "other": "N", **course}


def elsewhere(student_id: str, year: str, season: str, carnegie: str = "Doctoral Universities", cohort: str = "2023-24") -> dict:
    """A term with no course here but enrollment at another college, of the given Carnegie class."""
    return {"student_id": student_id, "cohort": cohort, "year": year, "season": season, "course": False, "other": "Y", "carnegie": carnegie}


def make_database(path: Path, students: list[dict], records: list[dict] = ()) -> Path:
    """Write the fixture database to path and return the path."""
    connection = sqlite3.connect(path)
    connection.executescript(SCHEMA)
    connection.execute("INSERT INTO data_provider VALUES (1, ?)", [LOADED_AT])
    for s in students:
        connection.execute(
            "INSERT OR IGNORE INTO student VALUES (?, ?, ?, ?, ?, NULL)",
            [s["student_id"], s["race"], s["gender"], s["age_band"], s["ethnicity"]],
        )
        connection.execute(
            "INSERT INTO cohort_membership VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, NULL, NULL, NULL, 0, ?)",
            [
                s["student_id"], s["cohort"], s["cohort_term"], s["enrollment_type"], s["enrollment_intensity"], s["pell"],
                s["attempted"], s["earned"], s["retention"], s["credential_year"] or 0,
            ],
        )
    terms: dict[tuple[str, str], int] = {}
    courses: dict[tuple[str, str], int] = {}
    for number, record in enumerate(records, start=1):
        term = (record["year"], record["season"])
        if term not in terms:
            terms[term] = len(terms) + 1
            sort_order = int(term[0][:4]) * 10 + SEASON_ORDER[term[1]]
            connection.execute("INSERT INTO term VALUES (?, ?, ?, ?)", [terms[term], term[0], term[1], sort_order])
        course_id = None
        if record["course"]:
            code = (record.get("prefix", "ENG"), record.get("number", "101"))
            if code not in courses:
                courses[code] = len(courses) + 1
                connection.execute("INSERT INTO course VALUES (?, ?, ?)", [courses[code], *code])
            course_id = courses[code]
        connection.execute(
            "INSERT INTO course_enrollment VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                number, record["student_id"], record["cohort"], course_id, terms[term],
                record.get("section", "01"), record.get("name"), record.get("grade"), record.get("delivery"),
                record.get("gateway", "N"), record.get("course_type", "CU"), record.get("attempted"), record.get("earned"),
                record["other"], record.get("carnegie"),
            ],
        )
    connection.commit()
    connection.close()
    return path
