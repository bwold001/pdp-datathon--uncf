"""Checks the README's answer to #8's gateway question: its SQL, run on a full load, matches the raw cohort file."""

import csv
import os
import re
import sqlite3
from decimal import Decimal
from pathlib import Path

import pytest
import yaml

from src.pipeline.run import run

BUILD = Path(__file__).resolve().parents[2]
RAW = BUILD.parent / "data/raw"
README = (BUILD / "README.md").read_text()
POSTGRES_URL = os.environ.get("PDP_TEST_POSTGRES_URL")


def readme_query():
    """The SQL block right after the README's gateway-query marker."""
    after = README.split("<!-- gateway-query:", 1)[1]
    return re.search(r"```sql\n(.*?)```", after, re.S).group(1)


def expected():
    """(gender, math completed, math required, math rate, English completed, English required, English rate),
    counted straight from the raw cohort file."""
    rows = [r for r in csv.DictReader(open(RAW / "pdp_cohort_data.csv")) if r["Cohort"] == "2022-23"]
    result = []
    for gender in sorted({r["Gender"] for r in rows}, key=lambda g: "UNKNOWN" if g == "UK" else g):
        mine = [r for r in rows if r["Gender"] == gender]
        line = ["UNKNOWN" if gender == "UK" else gender]
        for column in ("CompletedGatewayMathYear1", "CompletedGatewayEnglishYear1"):
            done, required = sum(r[column] == "C" for r in mine), sum(r[column] in ("C", "D") for r in mine)
            line += [done, required, round(100 * done / required, 1) if required else None]
        result.append(tuple(line))
    return result


def full_load(tmp_path, backend="sqlite", environ=None):
    sources = [{"kind": "cohort", "path": str(RAW / "pdp_cohort_data.csv"), "config": "cohort_mapping.yaml",
                "provider": "Achieving the Dream", "order_by": "cohort_membership.cohort"},
               {"kind": "course", "path": str(RAW / "pdp_course_data.csv"), "config": "course_mapping.yaml",
                "provider": "Achieving the Dream"}]
    (tmp_path / "pipeline.yaml").write_text(yaml.safe_dump({
        "backend": backend, "sqlite": {"path": str(tmp_path / "pdp.sqlite")}, "postgres": {"url_env": "PDP_TEST_POSTGRES_URL"},
        "logs_dir": str(tmp_path / "logs"), "staging_dir": str(tmp_path / "staging"),
        "tables": {"path": str(tmp_path / "tables")}, "sources": sources}))
    run(tmp_path / "pipeline.yaml", environ=environ or {})


def as_numbers(rows):
    return [tuple(float(v) if isinstance(v, Decimal) else v for v in row) for row in rows]


def test_the_readme_query_answers_from_one_join():
    sql = readme_query()
    assert sql.count("JOIN") == 1 and "FROM cohort_membership" in sql and "WHERE m.cohort = '2022-23'" in sql


def test_the_readme_numbers_are_the_ones_the_data_gives():
    for gender, *values in expected():
        math, english = values[:3], values[3:]
        for done, required, rate in (math, english):
            # a rate is written wherever more than one student was required to take the course
            written = f"`{gender}` {done} of {required} ({rate}%)" if required > 1 else f"`{gender}` {done} of {required}"
            assert written in README, (gender, done, required, rate)


@pytest.mark.slow
def test_the_readme_query_matches_the_raw_cohort_file_in_sqlite(tmp_path):
    full_load(tmp_path)
    rows = sqlite3.connect(tmp_path / "pdp.sqlite").execute(readme_query()).fetchall()
    assert as_numbers(rows) == expected()


@pytest.mark.slow
@pytest.mark.postgres
@pytest.mark.skipif(not POSTGRES_URL, reason="set PDP_TEST_POSTGRES_URL to run the PostgreSQL tests")
def test_the_readme_query_gives_the_same_answer_in_postgres(tmp_path, postgres):
    import psycopg
    full_load(tmp_path, backend="postgres", environ={"PDP_TEST_POSTGRES_URL": postgres})
    with psycopg.connect(postgres) as connection:
        rows = connection.execute(readme_query()).fetchall()
    assert as_numbers(rows) == expected()
