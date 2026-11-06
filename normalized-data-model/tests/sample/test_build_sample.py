"""Checks the sample builder and the published samples."""

import csv
import hashlib
from pathlib import Path

import pytest

from src.rules.rules import ConfigError, load_rules
from src.sample import build_sample as b
from src.sample.build_sample import build_sample
from src.tables.files import read_tables

BUILD = Path(__file__).resolve().parents[2]
SCHEMA = load_rules(BUILD / "config")["schema"]
OUTPUT = BUILD / "data/output/sample"
INPUT = BUILD / "data/input/sample"


def read(path):
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames, list(reader)


def table(name):
    return read(OUTPUT / f"{name}.csv")[1]


def test_only_public_api_is_build_sample():
    public = [n for n, v in vars(b).items() if not n.startswith("_") and callable(v)
              and getattr(v, "__module__", None) == b.__name__]
    assert public == ["build_sample"]
    assert b.__all__ == ["build_sample"]


# Functions

def test_sample_stores_unknown_codes_as_unknown():
    students = table("student")
    assert "UK" not in {r["ethnicity"] for r in students}
    assert "UNKNOWN" in {r["ethnicity"] for r in students}


# Published samples

@pytest.mark.parametrize("name", SCHEMA)
def test_sample_header_matches_the_constants(name):
    fieldnames, _ = read(OUTPUT / f"{name}.csv")
    assert fieldnames == list(SCHEMA[name])


def test_sample_foreign_keys_resolve():
    for name, columns in SCHEMA.items():
        for column, props in columns.items():
            if "foreign_key" not in props:
                continue
            ref_table, ref_column = props["foreign_key"].split(".")
            known = {r[ref_column] for r in table(ref_table)}
            for row in table(name):
                assert row[column] == "" and props["nullable"] or row[column] in known, (name, column, row[column])


def test_sample_has_about_ten_students():
    assert len(table("student")) == 10
    assert len(table("institution")) == 1
    assert len(table("data_provider")) == 4


def test_each_data_provider_row_describes_one_file():
    for provider in table("data_provider"):
        path = BUILD.parent / provider["source_file"]
        assert provider["source_file"].startswith("normalized-data-model/data/input/sample/"), provider
        assert provider["file_sha256"] == hashlib.sha256(path.read_bytes()).hexdigest(), provider
        assert int(provider["row_count"]) == len(read(path)[1]), provider


def test_sample_contains_every_quirk():
    memberships = [r["student_id"] for r in table("cohort_membership")]
    assert len(memberships) > len(set(memberships)), "a student in two cohorts"
    enrollments = table("course_enrollment")
    assert any(r["attempt_number"] == "2" for r in enrollments), "a retake"
    assert any(r["section_id"] == "" and r["course_id"] == "" for r in enrollments), "a row with no course record"
    unknown = next(t["term_id"] for t in table("term") if t["academic_year"] == "UNKNOWN")
    assert any(r["term_id"] == unknown for r in enrollments), "a row in the unknown term"
    assert any(r["term_id"] for r in table("student_attribute")), "a term-scoped student attribute"
    _, cohort = read(INPUT / "pdp_cohort_data.csv")
    _, course = read(INPUT / "pdp_course_data.csv")
    terms = {(r["Student_GUID"], r["Cohort"]): r["Cohort_Term"] for r in cohort}
    assert any(r["Cohort_Term"] != terms[(r["Student_GUID"], r["Cohort"])] for r in course), "a Cohort_Term collision"


def test_sample_keeps_the_cohort_file_value_for_the_cohort_term_collision():
    _, cohort = read(INPUT / "pdp_cohort_data.csv")
    built = {(r["student_id"], r["cohort"]): r["cohort_term"] for r in table("cohort_membership")}
    assert built == {(r["Student_GUID"], r["Cohort"]): r["Cohort_Term"] for r in cohort}


def test_sample_row_counts_match_the_sample_input():
    _, course = read(INPUT / "pdp_course_data.csv")
    _, cohort = read(INPUT / "pdp_cohort_data.csv")
    assert len(table("course_enrollment")) == len(course)
    assert len(table("cohort_membership")) == len(cohort)


# End to end

def test_build_sample_reproduces_the_published_samples(tmp_path):
    summary = build_sample(input_dir=BUILD / "data/input", raw_dir=BUILD.parent / "data/raw", config_dir=BUILD / "config",
                           sample_input_dir=tmp_path / "in", sample_output_dir=tmp_path / "out")
    for name in SCHEMA:
        assert read(tmp_path / "out" / f"{name}.csv") == read(OUTPUT / f"{name}.csv"), name
    assert summary["unconverted"] == {}
    assert summary["collisions"] == {}


def test_parquet_samples_read_back_equal_to_the_csv_ones(tmp_path):
    common = dict(input_dir=BUILD / "data/input", raw_dir=BUILD.parent / "data/raw", config_dir=BUILD / "config",
                  sample_input_dir=tmp_path / "in")
    build_sample(**common, sample_output_dir=tmp_path / "csv")
    build_sample(**common, sample_output_dir=tmp_path / "parquet", fmt="parquet")
    assert sorted(p.name for p in (tmp_path / "parquet").iterdir()) == sorted(f"{t}.parquet" for t in SCHEMA)
    assert read_tables(SCHEMA, tmp_path / "parquet") == read_tables(SCHEMA, tmp_path / "csv")


def test_parquet_isnt_written_over_the_committed_samples():
    with pytest.raises(ConfigError, match="committed samples .* are CSV"):
        build_sample(sample_output_dir=BUILD / "data/output/sample", fmt="parquet")


def test_the_sample_builder_orders_the_cohort_file_by_cohort(tmp_path, monkeypatch):
    real, seen = b.build_tables, []
    monkeypatch.setattr(b, "build_tables", lambda rules, sources, *a: seen.extend(sources) or real(rules, sources, *a))
    build_sample(input_dir=BUILD / "data/input", raw_dir=BUILD.parent / "data/raw", config_dir=BUILD / "config",
                 sample_input_dir=tmp_path / "in", sample_output_dir=tmp_path / "out")
    assert seen[0]["order_by"] == "cohort_membership.cohort"


def test_command_line_end_to_end(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(BUILD)
    calls = {}
    monkeypatch.setattr(b, "build_sample", lambda **kw: calls.update(kw) or {
        "students": ["A" * 32], "reasons": {"A" * 32: ["random"]}, "rows": {}, "collisions": {}, "unconverted": {}})
    b._main(["--students", "5", "--seed", "3"])
    assert calls == {"students": 5, "seed": 3, "fmt": "csv", "sample_output_dir": "data/output/sample"}
    assert "AAAAAAAA" in capsys.readouterr().out
