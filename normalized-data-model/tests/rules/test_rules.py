"""Checks the rules module: reading and checking configs, reading values, running rules."""

import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest
import yaml

from src.rules import rules as r
from src.rules.rules import ConfigError, check_value, foreign_keys, load_rules, read_value

BUILD = Path(__file__).resolve().parents[2]
RULES = load_rules(BUILD / "config")


def write_configs(tmp_path, schema, mapping=None, value_sets=None):
    (tmp_path / "destination_schema.yaml").write_text(yaml.safe_dump(schema))
    if value_sets is not None:
        (tmp_path / "value_sets.yaml").write_text(yaml.safe_dump(value_sets))
    if mapping is not None:
        (tmp_path / "test_mapping.yaml").write_text(yaml.safe_dump(mapping))
    return tmp_path


def small(rules=None, **field):
    """Rules for one table t with columns a (the one under test), b and c."""
    a = dict({"type": "str", "nullable": True}, **field)
    if rules:
        a["rules"] = rules
    schema = {"t": {"a": a, "b": {"type": "str", "nullable": True}, "c": {"type": "float", "nullable": True}}}
    return {"schema": schema, "value_sets": {"yn": ["Y", "N"]}, "mappings": {}, "files": []}


def entry(**fields):
    return dict({"source": "A", "destination_table": "t", "destination_column": "a", "on_conflict": "replace"}, **fields)


# load_rules

def test_the_real_configs_load():
    assert {"cohort_mapping.yaml", "course_mapping.yaml"} <= set(RULES["mappings"])
    assert [p.name for p in RULES["files"][:2]] == ["destination_schema.yaml", "value_sets.yaml"]


def test_load_rules_reads_only_the_given_mappings():
    loaded = load_rules(BUILD / "config", [BUILD / "config/course_mapping.yaml"])
    assert list(loaded["mappings"]) == ["course_mapping.yaml"]


@pytest.mark.parametrize("rule,message", [
    ({"enumm": ["a"], "severity": "error"}, "unknown rule kind"),
    ({"enum": ["a"]}, "severity"),
    ({"enum": ["a"], "severity": "fatal"}, "severity"),
    ({"enum": ["a"], "pattern": "x", "severity": "error"}, "exactly one rule kind"),
    ({"value_set": "nope", "severity": "error"}, "no value set"),
    ({"pattern": "(", "severity": "error"}, "bad pattern"),
    ({"not_before": "missing", "severity": "error"}, "no column"),
    ({"required_when": {"column": "b"}, "severity": "error"}, "either equals or present"),
    ({"required_when": {"column": "x.y", "present": True}, "severity": "error"}, "no column"),
    ({"required_when": {"column": "b", "present": "false"}, "severity": "error"}, "present must be true or false"),
    ({"enum": ["a"], "when": {"column": "b", "present": 0}, "severity": "error"}, "present must be true or false"),
    ({"enum": "YN", "severity": "error"}, "enum must be a non-empty list"),
    ({"enum": 5, "severity": "error"}, "enum must be a non-empty list"),
    ({"minimum": 0, "severity": "error"}, "needs an int or float column"),
    ({"max_length": "20", "severity": "error"}, "max_length must be a whole number"),
    ("Required; AllowedValues [a]", "must be a map"),
])
def test_load_rules_rejects_a_bad_rule(tmp_path, rule, message):
    schema = {"t": {"a": {"type": "str", "nullable": True, "rules": [rule]}, "b": {"type": "str", "nullable": True}}}
    with pytest.raises(ConfigError, match=message):
        load_rules(write_configs(tmp_path, schema, value_sets={"yn": ["Y", "N"]}))


def test_minimum_and_maximum_may_share_a_rule(tmp_path):
    schema = {"t": {"a": {"type": "int", "nullable": True, "rules": [{"minimum": 0, "maximum": 4, "severity": "error"}]}}}
    load_rules(write_configs(tmp_path, schema))


@pytest.mark.parametrize("limit", ["0", True, None])
def test_load_rules_rejects_a_range_that_is_not_a_number(tmp_path, limit):
    schema = {"t": {"a": {"type": "float", "nullable": True, "rules": [{"minimum": limit, "severity": "error"}]}}}
    with pytest.raises(ConfigError, match="minimum must be a number"):
        load_rules(write_configs(tmp_path, schema))


@pytest.mark.parametrize("field,message", [
    ({"type": "text", "nullable": True}, "type must be one of"),
    ({"type": "str", "nullable": True, "colour": "red"}, "unknown properties"),
    ({"type": "int", "nullable": True, "default_value": "UNKNOWN"}, "default_value"),
    ({"type": "float", "nullable": True, "unknown_value": True}, "unknown_value"),
    ({"type": "int", "nullable": True, "list_delimiter": "|"}, "list_delimiter needs a str column"),
])
def test_load_rules_rejects_a_bad_field(tmp_path, field, message):
    with pytest.raises(ConfigError, match=message):
        load_rules(write_configs(tmp_path, {"t": {"a": field}}))


@pytest.mark.parametrize("field,extra,message", [
    ({"type": "str", "nullable": True}, {"validation_rule": "Required"}, "unknown properties"),
    ({"type": "date", "nullable": True}, {}, "needs format"),
    ({"type": "bool", "nullable": True}, {"true_values": ["1"]}, "true_values and false_values"),
    ({"type": "str", "nullable": True}, {"unknown_values": ["UK"]}, "no unknown_value"),
    ({"type": "str", "nullable": True}, {"on_conflict": "merge"}, "on_conflict"),
    ({"type": "str", "nullable": True}, {"destination_column": "zzz"}, "no destination"),
])
def test_load_rules_rejects_a_bad_mapping_entry(tmp_path, field, extra, message):
    with pytest.raises(ConfigError, match=message):
        load_rules(write_configs(tmp_path, {"t": {"a": field}}, [entry(**extra)]))


def two_tables(keys):
    """A parent p with a two-column primary key, and a child c pointing at it through keys."""
    return {"p": {"x": {"type": "str", "nullable": False, "primary_key": True},
                  "y": {"type": "int", "nullable": False, "primary_key": True}},
            "c": {"id": {"type": "int", "nullable": False, "primary_key": True},
                  "x": {"type": "str", "nullable": False}, "y": {"type": "int", "nullable": False},
                  "foreignKeys": keys}}


def test_a_foreign_key_over_two_columns_loads_next_to_the_one_column_keys():
    loaded = RULES["foreign_keys"]["course_enrollment"]
    assert (("student_id", "cohort"), "cohort_membership", ("student_id", "cohort")) in loaded
    assert (("course_id",), "course", ("course_id",)) in loaded
    assert "foreignKeys" not in RULES["schema"]["course_enrollment"]  # the schema holds only columns


@pytest.mark.parametrize("keys,message", [
    ([], "must be a non-empty list"),
    ([{"fields": ["x", "y"]}], "needs fields and reference"),
    ([{"fields": ["x", "y"], "reference": {"resource": "p", "fields": ["x", "y"], "extra": 1}}], "needs fields and reference"),
    ([{"fields": ["x"], "reference": {"resource": "p", "fields": ["x", "y"]}}], "the same length"),
    ([{"fields": ["x", "z"], "reference": {"resource": "p", "fields": ["x", "y"]}}], "no column"),
    ([{"fields": ["x", "y"], "reference": {"resource": "q", "fields": ["x", "y"]}}], "no table"),
    ([{"fields": ["y", "x"], "reference": {"resource": "p", "fields": ["y", "x"]}}], "primary key"),
    ([{"fields": ["y", "y"], "reference": {"resource": "p", "fields": ["x", "y"]}}], "different types"),
    ([{"fields": ["x", "y"], "reference": {"resource": "p", "fields": ["x", "y"]}, "extra": 1}], "needs fields and reference"),
    ([{"fields": [["x"], "y"], "reference": {"resource": "p", "fields": ["x", "y"]}}], "must be text"),
    ([{"fields": ["x", "y"], "reference": {"resource": ["p"], "fields": ["x", "y"]}}], "must be text"),
])
def test_load_rules_rejects_a_bad_foreign_key_over_several_columns(tmp_path, keys, message):
    with pytest.raises(ConfigError, match=message):
        load_rules(write_configs(tmp_path, two_tables(keys)))


def test_a_good_foreign_key_over_several_columns_is_returned(tmp_path):
    loaded = load_rules(write_configs(tmp_path, two_tables(
        [{"fields": ["x", "y"], "reference": {"resource": "p", "fields": ["x", "y"]}}])))
    assert loaded["foreign_keys"] == {"p": [], "c": [(("x", "y"), "p", ("x", "y"))]}


def test_foreign_keys_gives_one_tables_keys():
    assert foreign_keys(RULES, "course_enrollment") == RULES["foreign_keys"]["course_enrollment"]
    assert foreign_keys(RULES, "institution") == []


def test_a_bad_foreign_key_stops_a_command_with_exit_2(tmp_path):
    config = tmp_path / "config"
    shutil.copytree(BUILD / "config", config)
    schema = (config / "destination_schema.yaml").read_text()
    bad = schema.replace("- {fields: [student_id, cohort], reference:", "- {fields: [[student_id], cohort], reference:")
    assert bad != schema
    (config / "destination_schema.yaml").write_text(bad)
    sample = BUILD / "data/input/sample"
    result = subprocess.run([sys.executable, "-m", "src.mapper.map",
                             "--cohort", str(sample / "pdp_cohort_data.csv"), "--course", str(sample / "pdp_course_data.csv"),
                             "--cohort_config", str(config / "cohort_mapping.yaml"), "--course_config", str(config / "course_mapping.yaml"),
                             "--config_dir", str(config), "--staging_dir", str(tmp_path / "staging")],
                            cwd=BUILD, capture_output=True, text=True)
    assert result.returncode == 2, result.stderr
    assert "column and table names must be text" in result.stderr


def test_key_is_blank_only_when_the_whole_natural_key_is_blank():
    fields = {"course_id": {"primary_key": True}, "course_prefix": {"unique": "k"}, "course_number": {"unique": "k"}}
    assert r.key_is_blank(fields, {"course_prefix": None, "course_number": None})
    assert not r.key_is_blank(fields, {"course_prefix": "ENG", "course_number": None})
    assert not r.key_is_blank({"x": {}}, {"x": None})  # no key mapped: the row is always made


def test_only_tables_reached_through_blank_foreign_keys_are_optional():
    assert r.optional_tables(RULES, {"term", "course", "student", "cohort_membership", "course_enrollment"}) == {"course"}
    assert r.optional_tables(RULES, {"student", "cohort_membership"}) == set()
    assert r.optional_tables(RULES, {"institution_event"}) == set()


def test_table_order_puts_every_table_after_the_tables_it_points_at():
    order = r.table_order(RULES["schema"], RULES["foreign_keys"])
    assert set(order) == set(RULES["schema"])
    for table, keys in RULES["foreign_keys"].items():
        for _, parent, _ in keys:
            assert order.index(parent) < order.index(table), (parent, table)
    assert order.index("cohort_membership") < order.index("course_enrollment")  # through the two-column key


def test_load_rules_reports_a_file_that_is_not_yaml(tmp_path):
    (tmp_path / "destination_schema.yaml").write_text("t: {a: [")
    with pytest.raises(ConfigError):
        load_rules(tmp_path)


# read_value

def test_read_value_states():
    rules = small(default_value="NONE", unknown_value="UNKNOWN")
    e = entry(missing_values=["."], unknown_values=["UK"], value_map={"Alask": "Alaska"})
    assert read_value(rules, e, "x") == (r.VALUE, "x", None)
    assert read_value(rules, e, "Alask") == (r.VALUE, "Alaska", None)  # repaired
    assert read_value(rules, e, ".") == (r.DEFAULT, "NONE", None)
    assert read_value(rules, e, "") == (r.DEFAULT, "NONE", None)
    assert read_value(rules, e, "UK") == (r.UNKNOWN, "UNKNOWN", None)


def test_read_value_without_default_or_unknown_value_is_blank():
    rules = small(type="float")
    e = entry(missing_values=["."], unknown_values=["UK"])
    assert read_value(rules, e, ".") == (r.BLANK, None, None)
    assert read_value(rules, e, "UK") == (r.UNKNOWN, None, None)  # numbers store unknown as blank


def test_read_value_converts_to_the_type():
    assert read_value(small(type="int"), entry(), "3") == (r.VALUE, 3, None)
    assert read_value(small(type="float"), entry(), "2.5") == (r.VALUE, 2.5, None)
    assert read_value(small(type="date"), entry(format="%Y%m%d"), "20240319") == (r.VALUE, date(2024, 3, 19), None)
    assert read_value(small(type="bool"), entry(true_values=["1"], false_values=["0"]), "0") == (r.VALUE, False, None)
    assert read_value(small(type="int"), entry(value=7), "") == (r.VALUE, 7, None)


@pytest.mark.parametrize("type_name,extra,raw", [
    ("int", {}, "abc"), ("float", {}, "x"), ("date", {"format": "%Y%m%d"}, "2024-03-19"),
    ("bool", {"true_values": ["1"], "false_values": ["0"]}, "yes"),
])
def test_read_value_reports_a_value_that_is_not_its_type(type_name, extra, raw):
    assert read_value(small(type=type_name), entry(**extra), raw) == (r.VALUE, None, f"not a {type_name}")


# check_value

def test_a_new_event_type_is_accepted_with_a_warning():
    assert check_value(RULES, "institution_event", "event_type", "powwow") == []
    assert check_value(RULES, "institution_event", "event_type", "orientation") == [
        ("institution_event.event_type#1 value_set", "warning")]


def test_a_malformed_event_type_is_an_error():
    assert ("institution_event.event_type#0 pattern", "error") in check_value(
        RULES, "institution_event", "event_type", "Pow Wow")


def failed(rule, value, row=None, real=True, **field):
    return check_value(small([dict(rule, severity="error")], **field), "t", "a", value, row, real=real)


@pytest.mark.parametrize("rule,good,bad", [
    ({"enum": ["Fall", "Spring"]}, "Fall", "fall"),
    ({"enum": ["Fall"], "ignore_case": True}, "FALL", "Winter"),
    ({"enum": ["> 20-24"], "ignore_spaces": True}, ">20 - 24", "> 25"),
    ({"value_set": "yn"}, "Y", "U"),
    ({"pattern": "^[0-9]{6}$"}, "240101", "24.0101"),
    ({"max_length": 3}, "abc", "abcd"),
    ({"academic_year": True}, "2023-24", "2023-25"),
    ({"academic_year": True}, "1999-00", "2023"),
])
def test_single_column_kinds(rule, good, bad):
    assert failed(rule, good) == []
    assert failed(rule, bad) == [(f"t.a#0 {next(iter(rule))}", "error")]


def test_range_kinds_on_numbers():
    rules = {"schema": {"t": {"a": {"type": "float", "nullable": True,
                                    "rules": [{"minimum": 0, "maximum": 20, "severity": "warning"}]}}}}
    assert check_value(rules, "t", "a", 20.0) == []
    assert check_value(rules, "t", "a", 20.5) == [("t.a#0 minimum+maximum", "warning")]
    assert check_value(rules, "t", "a", -1.0) == [("t.a#0 minimum+maximum", "warning")]


def test_two_column_kinds():
    assert failed({"not_greater_than": "c"}, 3.0, {"t": {"c": 4.0}}) == []
    assert failed({"not_greater_than": "c"}, 5.0, {"t": {"c": 4.0}}) != []
    assert failed({"not_greater_than": "c"}, 5.0, {"t": {"c": None}}) == []  # nothing to compare
    assert failed({"not_before": "b"}, date(2024, 1, 2), {"t": {"b": date(2024, 1, 1)}}) == []
    assert failed({"not_before": "b"}, date(2023, 1, 1), {"t": {"b": date(2024, 1, 1)}}) != []
    assert failed({"not_before": "b"}, date(2023, 1, 1), {"t": {"b": "UNKNOWN"}}) == []


def test_required_when():
    rule = {"required_when": {"column": "b", "equals": "Y"}}
    assert failed(rule, None, {"t": {"b": "Y"}}) != []
    assert failed(rule, None, {"t": {"b": "N"}}) == []
    assert failed(rule, "Humanities", {"t": {"b": "Y"}}) == []
    present = {"required_when": {"column": "u.p", "present": True}}
    assert failed(present, None, {"u": {"p": "ENG"}}) != []
    assert failed(present, None, {"u": {"p": None}}) == []
    assert failed(present, "UNKNOWN", {"u": {"p": "ENG"}}, real=False) == []  # unknown is a value


def test_present_false_means_the_other_column_has_no_value():
    rule = {"required_when": {"column": "b", "present": False}}
    assert failed(rule, None, {"t": {"b": None}}) != []
    assert failed(rule, None, {"t": {"b": "x"}}) == []
    when = {"enum": ["Y"], "when": {"column": "b", "present": False}}
    assert failed(when, "N", {"t": {"b": None}}) != []
    assert failed(when, "N", {"t": {"b": "x"}}) == []


def test_when_limits_a_rule_to_some_rows():
    rule = {"enum": ["true", "false"], "when": {"column": "b", "equals": "uses_on_campus_housing"}}
    assert failed(rule, "maybe", {"t": {"b": "uses_on_campus_housing"}}) != []
    assert failed(rule, "maybe", {"t": {"b": "tribal_affiliation"}}) == []


def test_rules_skip_values_that_are_not_real():
    assert failed({"enum": ["Y"]}, None) == []
    assert failed({"enum": ["Y"]}, "UNKNOWN", real=False) == []


def test_list_delimiter_checks_each_item():
    rule = {"pattern": "^[A-Z]{2}$"}
    assert failed(rule, "MN|ND", list_delimiter="|") == []
    assert failed(rule, "MN|North Dakota", list_delimiter="|") != []


def test_foreign_keys_that_go_round_in_a_circle_are_a_config_error(tmp_path):
    schema = {"a": {"id": {"type": "int", "nullable": False, "primary_key": True},
                    "b_id": {"type": "int", "nullable": True, "foreign_key": "b.id"}},
              "b": {"id": {"type": "int", "nullable": False, "primary_key": True},
                    "a_id": {"type": "int", "nullable": True, "foreign_key": "a.id"}}}
    with pytest.raises(ConfigError, match="round in a circle.*a -> b -> a"):
        load_rules(write_configs(tmp_path, schema))


def test_every_rule_in_the_schema_is_described_in_words():
    rules = RULES
    seen = set()
    for table, columns in rules["schema"].items():
        for column, field in columns.items():
            assert r.describe_rule(rules, f"{table}.{column} required") == "must have a value"
            assert r.describe_rule(rules, f"{table}.{column} type").startswith("must be ")
            for index, rule in enumerate(field.get("rules", [])):
                kinds = [k for k in rule if k in r._KINDS]
                seen.update(kinds)
                text = r.describe_rule(rules, f"{table}.{column}#{index} {'+'.join(kinds)}")
                assert text and "must" in text
                if "when" in rule:
                    assert ", when " in text
    assert seen == r._KINDS  # so a new kind can't arrive without its words


@pytest.mark.parametrize("rule,words", [
    ({"enum": ["a", "b"], "ignore_case": True}, "must be one of a, b, ignoring case"),
    ({"value_set": "yes_no"}, "must be one of Y, N"),
    ({"pattern": "^x$"}, "must match the pattern ^x$"),
    ({"minimum": 0, "maximum": 4}, "must be between 0 and 4"),
    ({"minimum": 0}, "must be at least 0"),
    ({"maximum": 4}, "must be at most 4"),
    ({"max_length": 9}, "must be at most 9 characters"),
    ({"academic_year": True}, "must be an academic year, such as 2024-25"),
    ({"not_before": "start_date"}, "must not be before start_date"),
    ({"not_greater_than": "attempted"}, "must not be greater than attempted"),
    ({"required_when": {"column": "x", "present": True}}, "must have a value when x has a value"),
    ({"enum": ["a"], "when": {"column": "x", "equals": "y"}}, "must be one of a, when x is y"),
    ({"enum": ["a"], "when": {"column": "x", "present": False}}, "must be one of a, when x is blank"),
])
def test_each_kind_of_rule_reads_as_what_it_checks(rule, words):
    rules = {"schema": {"t": {"c": {"type": "str", "rules": [rule]}}}, "value_sets": {"yes_no": ["Y", "N"]}}
    assert r.describe_rule(rules, "t.c#0 x") == words


def test_a_list_rule_applies_to_each_item():
    rules = {"schema": {"t": {"c": {"type": "str", "list_delimiter": "|", "rules": [{"enum": ["a"]}]}}}, "value_sets": {}}
    assert r.describe_rule(rules, "t.c#0 enum") == "each item must be one of a"


def test_a_name_that_isnt_a_rule_has_no_description():
    rules = RULES
    assert r.describe_rule(rules, "no_such.column required") is None
    assert r.describe_rule(rules, "student.student_id#99 pattern") is None
