"""Checks the Mapper: what it writes to the staging area, and that the next steps can read it."""

import csv
import re
from pathlib import Path

import pytest
import yaml

from src.mapper import map as m
from src.mapper.map import map_files
from src.rules.rules import ConfigError, load_rules
from src.tables.files import read_tables

BUILD = Path(__file__).resolve().parents[2]
CONFIG = BUILD / "config"
SAMPLE = BUILD / "data/input/sample"
AR = {"cohort": SAMPLE / "pdp_cohort_data.csv", "course": SAMPLE / "pdp_course_data.csv",
      "cohort_config": CONFIG / "cohort_mapping.yaml", "course_config": CONFIG / "course_mapping.yaml"}
SCHEMA = load_rules(CONFIG)["schema"]


def rows_of(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def test_only_public_api_is_map_files_and_mapped_columns():
    assert m.__all__ == ["map_files", "mapped_columns"]


def test_each_source_gets_its_tables_problems_and_description(tmp_path):
    result = map_files(**AR, config_dir=CONFIG, staging_dir=tmp_path, run_id="r")
    assert result == {"run_id": "r", "staging": str(tmp_path / "r"), "mode": "analysis_ready_files",
                      "sources": ["pdp_cohort_data.csv", "pdp_course_data.csv"],
                      "rows": {"pdp_cohort_data.csv": 11, "pdp_course_data.csv": 52}}
    folder = tmp_path / "r/mapped/pdp_course_data.csv"
    assert {p.name for p in folder.iterdir()} == {"source.yaml", "problems.csv", "term.csv", "course.csv", "student.csv",
                                                  "cohort_membership.csv", "course_enrollment.csv", "data_provider.csv"}  # researchid
    source = yaml.safe_load((folder / "source.yaml").read_text())
    raw = rows_of(SAMPLE / "pdp_course_data.csv")
    assert (source["name"], source["rows"], source["config"], source["format"]) == (
        "pdp_course_data.csv", len(raw), "course_mapping.yaml", "csv")
    assert source["sha256"] == m._sha256(SAMPLE / "pdp_course_data.csv")
    enrollments = rows_of(folder / "course_enrollment.csv")
    assert [int(r["source_row"]) for r in enrollments] == list(range(1, len(raw) + 1))  # one line per source row
    assert list(enrollments[0])[:3] == ["source_row", "student_id", "cohort"]  # source_row, then mapped columns only
    assert "enrollment_id" not in enrollments[0]  # filled when the tables are built, not mapped
    assert [r["cohort"] for r in enrollments] == [r["Cohort"] for r in raw]


def test_a_value_that_isnt_its_type_is_listed_in_problems_and_staged_blank(tmp_path):
    raw = rows_of(SAMPLE / "pdp_course_data.csv")
    raw[0]["Number_of_Credits_Attempted"] = "three"
    bad = tmp_path / "course.csv"
    with open(bad, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(raw[0]))
        writer.writeheader()
        writer.writerows(raw)
    map_files(**dict(AR, course=bad), config_dir=CONFIG, staging_dir=tmp_path, run_id="r")
    folder = tmp_path / "r/mapped/course.csv"
    assert rows_of(folder / "problems.csv") == [{"source_row": "1", "table": "course_enrollment",
                                                 "column": "number_of_credits_attempted", "value": "three",
                                                 "problem": "not a float"}]
    assert rows_of(folder / "course_enrollment.csv")[0]["number_of_credits_attempted"] == ""


def test_parquet_stages_the_same_values(tmp_path):
    map_files(**AR, config_dir=CONFIG, staging_dir=tmp_path, run_id="csv")
    map_files(**AR, config_dir=CONFIG, staging_dir=tmp_path, run_id="parquet", fmt="parquet")
    for name in ("pdp_cohort_data.csv", "pdp_course_data.csv"):
        extra = {"source_row": "int"}
        assert read_tables(SCHEMA, tmp_path / "parquet/mapped" / name, extra) == \
            read_tables(SCHEMA, tmp_path / "csv/mapped" / name, extra), name
        assert yaml.safe_load((tmp_path / "parquet/mapped" / name / "source.yaml").read_text())["format"] == "parquet"


def test_a_source_the_run_already_mapped_is_refused_before_writing(tmp_path):
    map_files(**AR, config_dir=CONFIG, staging_dir=tmp_path, run_id="r")
    with pytest.raises(ValueError, match="already mapped"):
        map_files(**AR, config_dir=CONFIG, staging_dir=tmp_path, run_id="r")


def test_enrichments_of_one_run_sit_next_to_the_analysis_ready_files(tmp_path):
    map_files(**AR, config_dir=CONFIG, staging_dir=tmp_path, run_id="r")
    result = map_files(enrichment=SAMPLE / "enrichment/on_campus_housing.csv",
                       enrichment_config=CONFIG / "on_campus_housing_mapping.yaml",
                       config_dir=CONFIG, staging_dir=tmp_path, run_id="r")
    assert result["mode"] == "enrichment"
    assert sorted(p.name for p in (tmp_path / "r/mapped").iterdir()) == [
        "on_campus_housing.csv", "pdp_cohort_data.csv", "pdp_course_data.csv"]


def test_a_bad_format_is_a_config_error(tmp_path):
    with pytest.raises(ConfigError, match="format must be one of"):
        map_files(**AR, config_dir=CONFIG, staging_dir=tmp_path, fmt="xlsx")
    assert not any(tmp_path.iterdir())


@pytest.mark.parametrize("kwargs", [
    {},
    {"cohort": "a", "course": "b", "cohort_config": "c"},
    {"enrichment": "e"},
    {"enrichment": "e", "enrichment_config": "f", "cohort": "a"},
])
def test_inputs_takes_exactly_one_mode(kwargs):
    args = dict.fromkeys(["cohort", "course", "cohort_config", "course_config", "enrichment", "enrichment_config"])
    with pytest.raises(ValueError):
        m._inputs(**dict(args, **kwargs))


def test_inputs_orders_the_cohort_file_first():
    assert m._inputs("a", "b", "c", "d", None, None) == [("a", "c"), ("b", "d")]
    assert m._inputs(None, None, None, None, "e", "f") == [("e", "f")]


def test_inputs_rejects_two_files_with_the_same_name():
    with pytest.raises(ValueError, match="both named data.csv"):
        m._inputs("cohort/data.csv", "course/data.csv", "c", "d", None, None)


def test_run_id_sorts_by_time_and_is_unique():
    first, second = m._new_run_id(), m._new_run_id()
    assert re.fullmatch(r"\d{8}T\d{6}Z-[0-9a-f]{6}", first)
    assert first != second


def test_command_line(tmp_path, capsys):
    args = [f"--{k}={v}" for k, v in AR.items()] + ["--config_dir", str(CONFIG), "--staging_dir", str(tmp_path),
                                                    "--run_id", "r"]
    assert m._main(args) == 0
    assert f"mapped: {tmp_path / 'r/mapped'}" in capsys.readouterr().out
