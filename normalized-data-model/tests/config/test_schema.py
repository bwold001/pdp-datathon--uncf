"""Checks the destination schema and the ER diagram."""

import re
from pathlib import Path

from src.rules.rules import load_rules

BUILD = Path(__file__).resolve().parents[2]
RULES = load_rules(BUILD / "config")
SCHEMA, FOREIGN_KEYS = RULES["schema"], RULES["foreign_keys"]
TYPES = {"str", "int", "float", "bool", "date", "datetime"}


def test_constants_fields_have_a_known_type_and_nullability():
    for table, columns in SCHEMA.items():
        for column, props in columns.items():
            assert props["type"] in TYPES, (table, column)
            assert isinstance(props["nullable"], bool), (table, column)
            assert set(props) <= {"type", "nullable", "primary_key", "foreign_key", "unique",
                                  "default_value", "unknown_value", "list_delimiter", "rules"}, (table, column)


def test_constants_every_table_has_a_primary_key_and_keys_are_not_nullable():
    for table, columns in SCHEMA.items():
        pk = [c for c, p in columns.items() if p.get("primary_key")]
        assert pk, table
        assert not any(columns[c]["nullable"] for c in pk), table


def test_constants_foreign_keys_point_at_primary_keys():
    for table, keys in FOREIGN_KEYS.items():
        for columns, ref_table, ref_columns in keys:
            for column, ref_column in zip(columns, ref_columns):
                assert SCHEMA[ref_table][ref_column].get("primary_key"), (table, column)
                assert SCHEMA[ref_table][ref_column]["type"] == SCHEMA[table][column]["type"], (table, column)


def test_course_enrollments_point_at_their_cohort_on_two_columns():
    assert (("student_id", "cohort"), "cohort_membership", ("student_id", "cohort")) in FOREIGN_KEYS["course_enrollment"]


def test_er_diagram_matches_the_constants():
    mmd = (BUILD / "normalized-data-model.mmd").read_text()
    diagram = {}  # rules and defaults aren't drawn; only tables, columns and types
    for table, body in re.findall(r"\n  (\w+) \{\n(.*?)\n  \}", mmd, re.S):
        diagram[table] = [tuple(line.split()[:2])[::-1] for line in body.splitlines()]
    constants = {t: [(c, p["type"]) for c, p in cols.items()] for t, cols in SCHEMA.items()}
    assert diagram == constants


def test_er_diagram_relationships_match_the_foreign_keys():
    """One line per pair of tables joined by a foreign key. The parent's side is |o (zero or one)
    when the foreign key can be blank, and || (exactly one) when it can't."""
    mmd = (BUILD / "normalized-data-model.mmd").read_text()
    drawn = {(parent, child): side for parent, side, child in
             re.findall(r"\n  (\w+) (\|\||\|o)--\S{2} (\w+) :", mmd)}
    expected = {}
    for table, keys in FOREIGN_KEYS.items():
        for columns, parent, _ in keys:
            nullable = any(SCHEMA[table][c]["nullable"] for c in columns)
            expected.setdefault((parent, table), set()).add("|o" if nullable else "||")
    assert all(len(sides) == 1 for sides in expected.values()), expected
    assert drawn == {pair: sides.pop() for pair, sides in expected.items()}
