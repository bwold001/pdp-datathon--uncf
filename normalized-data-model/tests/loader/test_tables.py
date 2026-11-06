"""Checks the shared table builder used by the sample builder and the loader."""

import csv
import itertools
import shutil
from datetime import datetime
from pathlib import Path

import pytest
import yaml

from src.loader import tables as t
from src.mapper.map import map_files
from src.rules.rules import load_rules

BUILD = Path(__file__).resolve().parents[2]
RULES = load_rules(BUILD / "config")
SCHEMA = RULES["schema"]


def test_only_public_api_is_build_tables():
    public = [n for n, v in vars(t).items() if not n.startswith("_") and callable(v)
              and getattr(v, "__module__", None) == t.__name__]
    assert public == ["build_tables"]
    assert t.__all__ == ["build_tables"]


def test_identity_uses_primary_key_then_unique_group():
    assert t._identity(SCHEMA, "student", {"student_id": "A"}) == ("A",)
    assert t._identity(SCHEMA, "course", {"course_prefix": "ENG", "course_number": "101"}) == ("ENG", "101")
    with pytest.raises(ValueError):
        t._identity({"t": {"id": {"type": "int", "nullable": False, "primary_key": True}}}, "t", {})


def test_store_applies_on_conflict_actions():
    store = t._Store(SCHEMA)
    store.upsert("cohort_membership", {"student_id": "A", "cohort": "2022-23", "cohort_term": "FALL"}, {})
    actions = {"cohort_term": "append"}
    row = store.upsert("cohort_membership", {"student_id": "A", "cohort": "2022-23", "cohort_term": "SPRING"}, actions)
    assert row["cohort_term"] == "FALL"  # append keeps the existing value until it's decided where an appended value goes
    row = store.upsert("cohort_membership", {"student_id": "A", "cohort": "2022-23", "cohort_term": "SPRING"},
                       {"cohort_term": "keep"})
    assert row["cohort_term"] == "FALL"
    row = store.upsert("cohort_membership", {"student_id": "A", "cohort": "2022-23", "cohort_term": "SPRING"},
                       {"cohort_term": "replace"})
    assert row["cohort_term"] == "SPRING"
    assert store.collisions == {("cohort_membership", "cohort_term", "append"): 1,
                                ("cohort_membership", "cohort_term", "keep"): 1,
                                ("cohort_membership", "cohort_term", "replace"): 1}


def test_store_hands_out_surrogate_ids_and_finds_rows_again():
    store = t._Store(SCHEMA)
    first = store.upsert("course", {"course_prefix": "ENG", "course_number": "101"}, {})
    second = store.upsert("course", {"course_prefix": "MATH", "course_number": "100"}, {})
    again = store.upsert("course", {"course_prefix": "ENG", "course_number": "101"}, {})
    assert (first["course_id"], second["course_id"], again["course_id"]) == (1, 2, 1)


def test_a_row_pointing_at_a_missing_pair_of_columns_is_reported():
    store = t._Store(SCHEMA)
    store.upsert("student", {"student_id": "A"}, {})
    store.upsert("cohort_membership", {"student_id": "A", "cohort": "2022-23"}, {})
    found = {"course_enrollment": {"student_id": "A", "cohort": "2022-23"}}
    assert t._missing_references(RULES["foreign_keys"], store, found) == []
    missing = {"course_enrollment": {"student_id": "A", "cohort": "2023-24"}}
    assert t._missing_references(RULES["foreign_keys"], store, missing) == [
        "course_enrollment.student_id,cohort ('A', '2023-24') is not in cohort_membership"]


def test_fill_term_order_puts_unknown_last():
    terms = [{"term_id": 1, "academic_year": "UNKNOWN", "academic_term": "UNKNOWN"},
             {"term_id": 2, "academic_year": "2022-23", "academic_term": "SPRING"},
             {"term_id": 3, "academic_year": "2022-23", "academic_term": "FALL"}]
    t._fill_term_order(terms)
    assert [t["sort_order"] for t in terms] == [3, 2, 1]


def test_fill_attempt_numbers_counts_retakes_by_term():
    terms = [{"term_id": 1, "sort_order": 2}, {"term_id": 2, "sort_order": 1}]
    rows = [{"student_id": "A", "course_id": 7, "term_id": 1, "provider_id": 1, "source_row_number": 1},
            {"student_id": "A", "course_id": 7, "term_id": 2, "provider_id": 1, "source_row_number": 2},
            {"student_id": "A", "course_id": None, "term_id": 2, "provider_id": 1, "source_row_number": 3}]
    t._fill_attempt_numbers(rows, terms)
    assert [r.get("attempt_number") for r in rows] == [2, 1, None]


def club_tables(tmp_path, club_optional):
    """A squad's club and club_membership tables, from a file with one row that names no club. The club key
    on club_membership can be blank only when club_optional."""
    config = tmp_path / "config"
    shutil.copytree(BUILD / "config", config)
    schema = yaml.safe_load((config / "destination_schema.yaml").read_text())
    schema["club"] = {"club_id": {"type": "int", "nullable": False, "primary_key": True},
                      "name": {"type": "str", "nullable": False, "unique": "club_name"}}
    schema["club_membership"] = {
        "membership_id": {"type": "int", "nullable": False, "primary_key": True},
        "provider_id": {"type": "int", "nullable": False, "foreign_key": "data_provider.provider_id", "unique": "row"},
        "source_row_number": {"type": "int", "nullable": False, "unique": "row"},
        "club_id": {"type": "int", "nullable": club_optional, "foreign_key": "club.club_id"},
        "note": {"type": "str", "nullable": True}}
    (config / "destination_schema.yaml").write_text(yaml.safe_dump(schema, sort_keys=False))
    (config / "club_mapping.yaml").write_text(yaml.safe_dump([
        {"source": "Club", "destination_table": "club", "destination_column": "name", "on_conflict": "replace"},
        {"source": "Note", "destination_table": "club_membership", "destination_column": "note", "on_conflict": "replace"}]))
    clubs = tmp_path / "clubs.csv"
    clubs.write_text("Club,Note\nChess,first\n,second\n")
    rules = load_rules(config, [config / "club_mapping.yaml"])
    map_files(enrichment=clubs, enrichment_config=config / "club_mapping.yaml", config_dir=config,
              staging_dir=tmp_path / "staging", run_id="r")
    tables, _ = t.build_tables(rules, [{"tables": tmp_path / "staging/r/mapped/clubs.csv", "config": "club_mapping.yaml",
                                        "provider": "test", "source_file": "clubs.csv"}], datetime(2026, 10, 29))
    return tables


def test_a_blank_key_leaves_a_table_out_only_when_the_table_is_optional(tmp_path):
    """club is left out of the row that names no club only when nothing requires a club. Otherwise the
    row is built, blank key and all, and the database's own NOT NULL rules refuse it."""
    assert [c["name"] for c in club_tables(tmp_path / "optional", club_optional=True)["club"]] == ["Chess"]
    assert [c["name"] for c in club_tables(tmp_path / "required", club_optional=False)["club"]] == ["Chess", None]


def test_an_enrichment_row_whose_two_column_key_points_nowhere_is_held_back(tmp_path):
    config = tmp_path / "config"
    shutil.copytree(BUILD / "config", config)
    schema = yaml.safe_load((config / "destination_schema.yaml").read_text())
    schema["cohort_note"] = {
        "note_id": {"type": "int", "nullable": False, "primary_key": True},
        "provider_id": {"type": "int", "nullable": False, "foreign_key": "data_provider.provider_id", "unique": "row"},
        "source_row_number": {"type": "int", "nullable": False, "unique": "row"},
        "student_id": {"type": "str", "nullable": False},
        "cohort": {"type": "str", "nullable": False},
        "note": {"type": "str", "nullable": True},
        "foreignKeys": [{"fields": ["student_id", "cohort"],
                         "reference": {"resource": "cohort_membership", "fields": ["student_id", "cohort"]}}]}
    (config / "destination_schema.yaml").write_text(yaml.safe_dump(schema, sort_keys=False))
    (config / "cohort_note_mapping.yaml").write_text(yaml.safe_dump([
        {"source": source, "destination_table": "cohort_note", "destination_column": column, "on_conflict": "replace"}
        for source, column in (("Student", "student_id"), ("Cohort", "cohort"), ("Note", "note"))]))
    sample = BUILD / "data/input/sample"
    with open(sample / "pdp_cohort_data.csv", newline="") as f:
        first = next(csv.DictReader(f))
    notes = tmp_path / "cohort_notes.csv"
    notes.write_text(f"Student,Cohort,Note\n{first['Student_GUID']},{first['Cohort']},in its cohort\n"
                     f"{first['Student_GUID']},1999-00,a cohort the student isn't in\n")
    names = ["cohort_mapping.yaml", "course_mapping.yaml", "cohort_note_mapping.yaml"]
    rules = load_rules(config, [config / name for name in names])
    staging = tmp_path / "staging"
    map_files(cohort=sample / "pdp_cohort_data.csv", course=sample / "pdp_course_data.csv",
              cohort_config=config / names[0], course_config=config / names[1], config_dir=config,
              staging_dir=staging, run_id="r")
    map_files(enrichment=notes, enrichment_config=config / names[2], config_dir=config, staging_dir=staging, run_id="r")
    mapped = staging / "r/mapped"
    sources = [{"tables": mapped / "pdp_cohort_data.csv", "config": names[0], "provider": "cohort", "source_file": "c"},
               {"tables": mapped / "pdp_course_data.csv", "config": names[1], "provider": "course", "source_file": "k"},
               {"tables": mapped / "cohort_notes.csv", "config": names[2], "provider": "squad", "source_file": "n"}]
    tables, report = t.build_tables(rules, sources, datetime(2026, 10, 29))
    assert [n["note"] for n in tables["cohort_note"]] == ["in its cohort"]
    assert [(h["source_file"], h["source_row_number"]) for h in report["held_back"]] == [("cohort_notes.csv", 2)]


def test_a_new_table_and_a_new_optional_table_need_no_code_change(tmp_path):
    """A squad's enrichment adds two tables: club_membership, which points at club through a key
    that can be blank. club is filled where the row names a club and left out where it doesn't,
    and club_membership is filled after club, though neither is named anywhere in the code."""
    config = tmp_path / "config"
    shutil.copytree(BUILD / "config", config)
    schema = yaml.safe_load((config / "destination_schema.yaml").read_text())
    schema["club"] = {"club_id": {"type": "int", "nullable": False, "primary_key": True},
                      "name": {"type": "str", "nullable": False, "unique": "club_name"}}
    schema["club_membership"] = {
        "membership_id": {"type": "int", "nullable": False, "primary_key": True},
        "provider_id": {"type": "int", "nullable": False, "foreign_key": "data_provider.provider_id", "unique": "row"},
        "source_row_number": {"type": "int", "nullable": False, "unique": "row"},
        "club_id": {"type": "int", "nullable": True, "foreign_key": "club.club_id"},
        "note": {"type": "str", "nullable": True}}
    (config / "destination_schema.yaml").write_text(yaml.safe_dump(schema, sort_keys=False))
    (config / "club_mapping.yaml").write_text(yaml.safe_dump([
        {"source": "Club", "destination_table": "club", "destination_column": "name", "on_conflict": "replace"},
        {"source": "Note", "destination_table": "club_membership", "destination_column": "note", "on_conflict": "replace"}]))
    clubs = tmp_path / "clubs.csv"
    clubs.write_text("Club,Note\nChess,first\n,second\nChess,third\n")
    rules = load_rules(config, [config / "club_mapping.yaml"])
    map_files(enrichment=clubs, enrichment_config=config / "club_mapping.yaml", config_dir=config,
              staging_dir=tmp_path / "staging", run_id="r")
    tables, report = t.build_tables(rules, [{"tables": tmp_path / "staging/r/mapped/clubs.csv", "config": "club_mapping.yaml",
                                             "provider": "test", "source_file": "clubs.csv"}], datetime(2026, 10, 29))
    assert [c["name"] for c in tables["club"]] == ["Chess"]
    assert [(m["note"], m.get("club_id")) for m in tables["club_membership"]] == [("first", 1), ("second", None), ("third", 1)]
    assert report["held_back"] == []



def test_unknown_never_overwrites_a_known_value():
    store = t._Store(SCHEMA)
    store.upsert("student", {"student_id": "A", "gender": "F"}, {})
    row = store.upsert("student", {"student_id": "A", "gender": "UNKNOWN"}, {"gender": "replace"})
    assert row["gender"] == "F"
    assert store.collisions == {("student", "gender", "unknown not written"): 1}
    row = store.upsert("student", {"student_id": "B", "gender": "UNKNOWN"}, {})
    row = store.upsert("student", {"student_id": "B", "gender": "M"}, {"gender": "replace"})
    assert row["gender"] == "M"  # a known value still replaces an unknown one


def test_the_later_cohort_wins_whatever_order_the_rows_come_in():
    later, earlier = (0, (1, 2023), 1), (0, (1, 2022), 2)  # the 2023-24 row is read first
    store = t._Store(SCHEMA)
    store.upsert("student", {"student_id": "A", "gender": "F"}, {}, later)
    row = store.upsert("student", {"student_id": "A", "gender": "M"}, {"gender": "replace"}, earlier)
    assert row["gender"] == "F"
    assert store.collisions == {("student", "gender", "replace, earlier row kept"): 1}
    assert t._order_key({"cohort_membership": {"cohort": "2022-23"}}, ("cohort_membership", "cohort")) == (1, 2022)
    assert t._order_key({"cohort_membership": {"cohort": "UNKNOWN"}}, ("cohort_membership", "cohort")) < (1, 1900)


# Ranks as build_tables makes them for the cohort file, read first, with order_by cohort_membership.cohort:
# (the source's place in the list, the row's cohort, its row number).
COHORT_2022, COHORT_2023, COHORT_2024 = (0, (1, 2022), 1), (0, (1, 2023), 2), (0, (1, 2024), 3)


def gender_after(rows):
    store = t._Store(SCHEMA)
    for rank, gender in rows:
        row = store.upsert("student", {"student_id": "A", "gender": gender}, {"gender": "replace"}, rank)
    return row["gender"]


@pytest.mark.parametrize("earlier,later", [("F", "UNKNOWN"), ("UNKNOWN", "F")])
def test_the_later_cohorts_value_wins_in_either_order_even_when_it_is_unknown(earlier, later):
    rows = [(COHORT_2022, earlier), (COHORT_2023, later)]
    assert gender_after(rows) == later
    assert gender_after(list(reversed(rows))) == later


def test_unknown_from_another_source_and_a_later_cohorts_blank_dont_overwrite():
    store = t._Store(SCHEMA)
    store.upsert("student", {"student_id": "A", "gender": "F"}, {}, COHORT_2022)
    enrichment = (2, (0,), 1)  # a later source, with no order_by
    assert store.upsert("student", {"student_id": "A", "gender": "UNKNOWN"}, {"gender": "replace"}, enrichment)["gender"] == "F"
    assert store.upsert("student", {"student_id": "A", "gender": None}, {"gender": "replace"}, COHORT_2023)["gender"] == "F"


def test_three_cohort_rows_in_any_order_give_the_latest_cohorts_value():
    rows = [(COHORT_2022, "F"), (COHORT_2024, "F"), (COHORT_2023, "M")]
    assert {gender_after(list(order)) for order in itertools.permutations(rows)} == {"F"}
