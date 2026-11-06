"""Checks the column dictionary builder, the committed config/column_dictionary.yaml and pdp_model's readers."""

from pathlib import Path

import pytest

import pdp_model
from src.dictionary.build import DictionaryError, _parse, build_dictionary, render
from src.rules.rules import load_rules

BUILD = Path(__file__).resolve().parents[2]
CONFIG = BUILD / "config"
RECORDS = build_dictionary()
BY_COLUMN = {(r["table"], r["column"]): r for r in RECORDS}


def test_committed_file_matches_a_rebuild():
    committed = (CONFIG / "column_dictionary.yaml").read_text(encoding="utf-8")
    assert committed == render(RECORDS), "stale: run `python -m src.dictionary.build` from normalized-data-model/"


def test_one_record_per_column_the_cohort_or_course_file_writes():
    rules = load_rules(CONFIG, [CONFIG / "cohort_mapping.yaml", CONFIG / "course_mapping.yaml"])
    written = {(e["destination_table"], e["destination_column"])
               for entries in rules["mappings"].values() for e in entries
               if "source" in e and "destination_table" in e}
    assert len(RECORDS) == len(BY_COLUMN)
    assert set(BY_COLUMN) == written


def test_codes_have_their_meanings():
    record = BY_COLUMN[("cohort_membership", "math_placement")]
    assert record["dictionary_values"] == [
        {"code": "C", "meaning": "Student is college ready in Math"},
        {"code": "N", "meaning": "Student is not college ready in Math"},
        {"code": "UK", "meaning": "Unknown or missing"},
    ]


def test_cohort_lists_go_to_notes_not_codes():
    record = BY_COLUMN[("cohort_membership", "cohort")]
    assert record["description_source"] == "pdp_cohort_data.csv"
    assert record["description"].startswith("All undergraduate students")
    assert record["dictionary_values"] == []
    assert "**Also includes:**" in record["notes"]


def test_cohort_file_wins_and_every_source_is_kept():
    record = BY_COLUMN[("student", "student_age")]
    assert record["description_source"] == "pdp_cohort_data.csv"
    assert [s["source_file"] for s in record["sources"]] == ["pdp_cohort_data.csv", "pdp_course_data.csv"]
    assert "Older than 24" in [v["code"] for v in record["dictionary_values"]]


def test_mock_data_notes_come_from_the_lookup():
    cohort_source = BY_COLUMN[("student", "student_id")]["sources"][0]
    assert cohort_source["source_file"] == "pdp_cohort_data.csv"
    assert "Join the cohort and course files on Student_GUID + Cohort" in cohort_source["lookup_description"]


def test_a_column_with_no_dictionary_entry_has_only_lookup_text():
    record = BY_COLUMN[("data_provider", "research_id")]
    assert record["dictionary_name"] is None and record["description"] is None
    assert [s["lookup_description"].rsplit(" ", 1)[1] for s in record["sources"]] == ["cohort2026atd.", "course2026atd."]


def test_locale_note_goes_to_every_locale_column():
    with_note = {k for k, r in BY_COLUMN.items() if r["notes"] and "**LOCALE Values:**" in r["notes"]}
    assert with_note == {k for k, r in BY_COLUMN.items() if r["dictionary_name"] and "LOCALE" in r["dictionary_name"]}


def test_a_name_missing_from_the_markdown_stops_the_build():
    with pytest.raises(DictionaryError, match="entries not found"):
        _parse("Gender\n\nStudent gender.\n", ["Gender", "Race"], [], "test.md")


def test_a_name_found_twice_stops_the_build():
    with pytest.raises(DictionaryError, match="more than once"):
        _parse("Gender\n\nOne.\n\nGender\n\nTwo.\n", ["Gender"], [], "test.md")


def test_an_unused_entry_ends_the_entry_before_it():
    parsed = _parse("Gender\n\nStudent gender.\n\nSSN\n\nA number.\n", ["Gender"], ["SSN"], "test.md")
    assert parsed["Gender"]["description"] == "Student gender."


def test_pdp_model_reads_the_committed_file():
    assert pdp_model.column_dictionary() == RECORDS


def test_pdp_model_schema_field():
    assert pdp_model.schema_field("student", "gender") == {
        "type": "str", "nullable": True, "unknown_value": "UNKNOWN", "allowed_values": ["M", "F", "P", "X"]}
    assert pdp_model.schema_field("term", "sort_order")["allowed_values"] is None
    assert pdp_model.schema_field("student", "no_such_column") is None
