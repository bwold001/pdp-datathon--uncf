"""Checks the four definitions-mode tools over MCP.

They read the repo's metadata files, so most of these tests have no database at all. Where a
database is configured, they check that it changes nothing the tools return, and that
get_database_info only reports whether it's reachable.
"""

import json

import anyio
import pytest
from mcp.client import Client

from conftest import SCHEMA, SAMPLE_OUTPUT, call, call_many
from pdp_mcp import db
from pdp_mcp.config import Settings
from pdp_mcp.server import TOOLS_BY_MODE, build_server

MODEL_TABLES = sorted(SCHEMA)
NO_DATABASE = Settings()   # the default: definitions mode, no database
METADATA_TOOLS = ["describe_table", "get_column_definition", "get_database_info", "list_tables"]


# get_database_info

def test_database_info_reports_the_access_mode_and_metadata_without_a_database():
    is_error, info = call(NO_DATABASE, "get_database_info")
    assert not is_error
    assert info["access_mode"] == "definitions" and info["read_only"] is True
    assert sorted(info["capabilities"]) == METADATA_TOOLS
    assert info["metadata"]["healthy"] and info["metadata"]["error"] is None
    assert info["metadata"]["table_count"] == 10   # load_run is the tenth
    paths = [f["path"] for f in info["metadata"]["files"]]
    assert paths[:5] == ["normalized-data-model/config/destination_schema.yaml",
                         "normalized-data-model/config/value_sets.yaml", "normalized-data-model/config/pipeline.yaml",
                         "normalized-data-model/README.md", "data/dictionaries/column_lookup.csv"]
    assert all(len(f["sha256"]) == 64 for f in info["metadata"]["files"])
    assert info["database"] is None and info["warnings"] == []


def test_database_info_reports_a_configured_database_without_secrets(settings):
    _, info = call(settings, "get_database_info")
    database = info["database"]
    assert database["engine"] == settings.backend and database["healthy"] and database["error"] is None
    assert database["model_tables"] == {"expected": MODEL_TABLES, "missing": []}
    assert database["table_count"] == 10 and database["view_count"] == 0
    assert sorted(info["capabilities"]) == METADATA_TOOLS, "a database adds no tools"
    text = str(info)
    if settings.postgres_url:
        assert settings.postgres_url not in text and "localhost" not in text and "password" not in text.lower()
    else:
        assert str(settings.sqlite_path.parent) not in text and database["database"] == "pdp.sqlite"


def test_a_configured_database_that_is_missing_is_reported_and_never_created(tmp_path):
    settings = Settings(backend="sqlite", sqlite_path=tmp_path / "nothing.sqlite")
    _, info = call(settings, "get_database_info")
    assert not info["database"]["healthy"] and info["database"]["error"]["code"] == "database_unavailable"
    assert info["metadata"]["healthy"], "the metadata tools don't need the database"
    assert not (tmp_path / "nothing.sqlite").exists()


def test_database_info_lists_missing_model_tables(tmp_path):
    import sqlite3
    path = tmp_path / "partial.sqlite"
    with sqlite3.connect(path) as connection:
        connection.execute("CREATE TABLE student (student_id TEXT PRIMARY KEY)")
    _, info = call(Settings(backend="sqlite", sqlite_path=path), "get_database_info")
    assert info["database"]["healthy"] and len(info["database"]["model_tables"]["missing"]) == 9
    assert "lacks 9" in info["warnings"][0]


def test_broken_metadata_is_reported(tmp_path):
    from pdp_mcp.metadata import Metadata
    from pdp_mcp.server import Tools
    info = Tools(NO_DATABASE, Metadata(tmp_path)).get_database_info()
    assert not info.metadata.healthy and "pipeline.yaml" in info.metadata.error.message


# list_tables and describe_table, from the model's schema

def test_list_tables_lists_the_model_with_descriptions():
    _, result = call(NO_DATABASE, "list_tables")
    assert result["source"] == "normalized-data-model/config/destination_schema.yaml"
    assert [t["name"] for t in result["tables"]] == MODEL_TABLES
    assert all(t["type"] == "table" and t["in_model"] and t["description"] for t in result["tables"])


def test_describe_table_gives_columns_keys_and_relationships_without_a_database():
    _, table = call(NO_DATABASE, "describe_table", {"table": "course_enrollment"})
    assert [c["name"] for c in table["columns"]] == list(SCHEMA["course_enrollment"])
    by_name = {c["name"]: c for c in table["columns"]}
    assert by_name["enrollment_id"] == {"name": "enrollment_id", "data_type": None, "model_type": "int",
                                        "nullable": False, "primary_key": True}
    assert by_name["course_id"]["nullable"] and by_name["course_end_date"]["model_type"] == "date"
    assert all(c["data_type"] is None for c in table["columns"]), "no engine types without a database"
    assert table["primary_key"] == ["enrollment_id"]
    assert [(k["columns"], k["references_table"], k["references_columns"]) for k in table["foreign_keys"]] == [
        (["provider_id"], "data_provider", ["provider_id"]), (["student_id"], "student", ["student_id"]),
        (["student_id", "cohort"], "cohort_membership", ["student_id", "cohort"]),   # from the table's foreignKeys
        (["course_id"], "course", ["course_id"]), (["term_id"], "term", ["term_id"])]
    assert table["unique_constraints"] == [["provider_id", "source_row_number"]]
    assert table["referenced_by"] == []


def test_describe_table_lists_tables_that_point_at_it():
    _, student = call(NO_DATABASE, "describe_table", {"table": "student"})
    assert [(r["table"], r["columns"], r["references_columns"]) for r in student["referenced_by"]] == [
        ("cohort_membership", ["student_id"], ["student_id"]), ("course_enrollment", ["student_id"], ["student_id"]),
        ("student_attribute", ["student_id"], ["student_id"])]
    _, membership = call(NO_DATABASE, "describe_table", {"table": "COHORT_MEMBERSHIP"})
    assert membership["name"] == "cohort_membership" and membership["primary_key"] == ["student_id", "cohort"]
    assert membership["referenced_by"] == [{"table": "course_enrollment", "columns": ["student_id", "cohort"],
                                            "references_columns": ["student_id", "cohort"]}]


def test_describe_table_suggests_names_for_an_unknown_table():
    is_error, content = call(NO_DATABASE, "describe_table", {"table": "students"})
    assert is_error and content["error"]["code"] == "not_found"
    assert content["error"]["details"]["suggestions"][0] == "student"


def test_the_schema_describes_what_the_loader_actually_built(settings):
    """Nothing is lost by reading the schema instead of the database: for every model table, the keys and
    columns match what each database reports for the tables the loader created."""
    backend = db.backend_for(settings)
    with backend.connect() as connection:
        relations = {r.name: r for r in backend.relations(connection)}
        for table in MODEL_TABLES:
            _, from_schema = call(NO_DATABASE, "describe_table", {"table": table})
            loaded = backend.describe(connection, relations[table])
            assert [(c["name"], c["nullable"], c["primary_key"]) for c in from_schema["columns"]] == \
                   [(c["name"], c["nullable"], c["primary_key"]) for c in loaded.columns], table
            assert from_schema["primary_key"] == loaded.primary_key, table
            assert sorted(map(json.dumps, from_schema["foreign_keys"])) == \
                   sorted(map(json.dumps, loaded.foreign_keys)), table
            assert from_schema["unique_constraints"] == loaded.unique_constraints, table


def test_a_configured_database_changes_nothing_the_metadata_tools_return(settings):
    calls = [("list_tables", {}), ("describe_table", {"table": "student"}), ("get_column_definition", {"column": "gender"})]
    assert call_many(settings, calls) == call_many(NO_DATABASE, calls)


# No student-level values

def test_no_metadata_tool_returns_a_student_level_value(settings):
    """Every value the four tools can return, for every table and every source and normalized column,
    with a database full of sample students configured, holds none of those students' values."""
    import csv
    student_ids = {r["student_id"] for r in csv.DictReader(open(SAMPLE_OUTPUT / "student.csv"))}
    course_names = {r["course_name"] for r in csv.DictReader(open(SAMPLE_OUTPUT / "course_enrollment.csv"))
                    if r["course_name"] and r["course_name"] != "UNKNOWN"}
    columns = sorted({c for fields in SCHEMA.values() for c in fields})
    calls = ([("list_tables", {}), ("get_database_info", {})]
             + [("describe_table", {"table": t}) for t in SCHEMA]
             + [("get_column_definition", {"column": c}) for c in columns])
    text = json.dumps([content for _, content in call_many(settings, calls)])
    assert not [s for s in student_ids if s in text]
    assert not [n for n in course_names if f'"{n}"' in text]
    assert '"rows"' not in text


# get_column_definition: no database involved

def test_a_source_column_and_its_normalized_column_both_match():
    _, result = call(NO_DATABASE, "get_column_definition", {"column": "retention"})
    source, normalized = result["matches"]
    assert source["kind"] == "source" and source["source_file"] == "pdp_cohort_data.csv"
    assert source["destinations"] == [{"table": "cohort_membership", "column": "retention"}]
    assert source["description"].startswith("Retention is defined as")
    assert source["dictionary_file"] == "data/dictionaries/arf_cohort_data_dictionary.md"
    assert normalized["kind"] == "normalized" and normalized["model_type"] == "bool"
    assert normalized["description"] == source["description"]
    assert normalized["sources"][0]["source_column"] == "Retention"


def test_column_definitions_carry_codes_and_unknowns():
    _, gender = call(NO_DATABASE, "get_column_definition", {"column": "student.gender"})
    [normalized] = gender["matches"]
    assert normalized["allowed_values"] == ["M", "F", "P", "X"] and normalized["unknown_value"] == "UNKNOWN"
    assert {s["source_file"] for s in normalized["sources"]} == {"pdp_cohort_data.csv", "pdp_course_data.csv"}
    _, race = call(NO_DATABASE, "get_column_definition", {"column": "Race", "source_file": "pdp_cohort_data.csv"})
    [source] = race["matches"]
    assert source["unknown_values"] == ["Unknown"] and source["value_map"] == {}, \
        "the mock data's cut-off race labels are fixed in data_fixes.yaml, not the mapping's value_map"
    _, stored = call(NO_DATABASE, "get_column_definition", {"column": "student.race"})
    allowed = stored["matches"][0]["allowed_values"]
    assert "American Indian or Alaska Native" in allowed and "American Indian or Alaska" not in allowed
    _, placement = call(NO_DATABASE, "get_column_definition", {"column": "math_placement"})
    assert placement["matches"][-1]["allowed_values"] == ["C", "N"]


def test_a_dictionary_name_finds_its_source_column():
    _, result = call(NO_DATABASE, "get_column_definition", {"column": "Student ID"})
    assert {(m["source_file"], m["source_column"]) for m in result["matches"]} == {
        ("pdp_cohort_data.csv", "Student_GUID"), ("pdp_course_data.csv", "Student_GUID")}


def test_a_generated_column_has_no_sources_and_no_made_up_description():
    _, result = call(NO_DATABASE, "get_column_definition", {"column": "sort_order", "table": "term"})
    [match] = result["matches"]
    assert match["sources"] == [] and match["description"] is None


def test_an_enrichment_column_has_no_description_rather_than_an_invented_one():
    _, result = call(NO_DATABASE, "get_column_definition", {"column": "Uses_On_Campus_Housing"})
    [match] = result["matches"]
    assert match["source_file"] == "on_campus_housing.csv" and match["description"] is None
    assert match["dictionary_name"] is None and match["dictionary_file"] is None


def test_filters_narrow_to_one_kind():
    _, by_table = call(NO_DATABASE, "get_column_definition", {"column": "gender", "table": "student"})
    assert [m["kind"] for m in by_table["matches"]] == ["normalized"]
    _, by_file = call(NO_DATABASE, "get_column_definition", {"column": "gender", "source_file": "pdp_course_data.csv"})
    assert [(m["kind"], m["source_file"]) for m in by_file["matches"]] == [("source", "pdp_course_data.csv")]


def test_an_unknown_column_is_not_found_with_suggestions():
    is_error, content = call(NO_DATABASE, "get_column_definition", {"column": "Studnt_GUID"})
    assert is_error and content["error"]["code"] == "not_found"
    assert "Student_GUID" in content["error"]["details"]["suggestions"]


def test_arguments_that_break_the_input_schema_are_errors_without_structured_content():
    async def run():
        async with Client(build_server(NO_DATABASE)) as client:
            return await client.call_tool("describe_table", {"table": ""})
    result = anyio.run(run)
    assert result.is_error and result.structured_content is None and "table" in result.content[0].text


@pytest.mark.parametrize("mode", sorted(TOOLS_BY_MODE))
def test_every_mode_registers_only_read_only_metadata_tools(mode):
    assert "execute_query" not in TOOLS_BY_MODE[mode]
