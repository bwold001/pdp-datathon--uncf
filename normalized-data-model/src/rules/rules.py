"""Read, check and apply the validation rules.

Rules live in two places, split by what they describe:
- config/destination_schema.yaml says what a valid stored value looks like: type, nullable, keys,
  default_value, unknown_value, list_delimiter and rules. A foreign key over several columns is a
  table-level foreignKeys entry, as in Frictionless Table Schema. config/value_sets.yaml holds the
  value lists those rules refer to by name.
- Each mapping config says how its source file writes values: format, true_values, false_values,
  value_map, missing_values, unknown_values and must_exist.

Public API:
- load_rules(config_dir, mapping_paths=None) reads and checks every file, or raises ConfigError.
  Its "schema" holds only columns; its "foreign_keys" holds every foreign key, one-column or not.
- foreign_keys(rules, table) gives one table's foreign keys: (columns, table pointed at, columns pointed at).
- read_value(rules, entry, raw) turns one source value into a stored value and says which state
  it is in: a value, a default (no value), unknown, or blank.
- check_value(rules, table, column, value, row=None, real=True) runs the column's rules on one
  stored value.
- table_order(schema, foreign_keys) lists the tables so each comes after the tables it points at.
- optional_tables(rules, tables) and key_is_blank(fields, row) say which tables a source row may
  leave out. The validator and the table builder both use them, so they can't disagree.
"""

import re
from datetime import date, datetime
from pathlib import Path

import yaml

__all__ = ["ConfigError", "load_rules", "read_value", "check_value", "describe_rule", "table_order", "optional_tables", "key_is_blank",
           "VALUE", "DEFAULT", "UNKNOWN", "BLANK"]

_TYPES = {"str", "int", "float", "bool", "date", "datetime"}
_FIELD_KEYS = {"type", "nullable", "primary_key", "foreign_key", "unique",
               "default_value", "unknown_value", "list_delimiter", "rules"}
_ENTRY_KEYS = {"source", "value", "destination_table", "destination_column", "on_conflict",
               "format", "true_values", "false_values", "value_map", "missing_values",
               "unknown_values", "must_exist"}
_ACTIONS = {"append", "replace", "keep"}
_SEVERITIES = {"error", "warning"}
_TYPE_WORDS = {"str": "text", "int": "a whole number", "float": "a number", "bool": "true or false",
               "date": "a date", "datetime": "a date and time"}
# Rule kinds. Each rule has exactly one kind; the options go with it.
_KINDS = {"enum", "value_set", "pattern", "minimum", "maximum", "max_length",
          "not_before", "not_greater_than", "required_when", "academic_year"}
_OPTIONS = {"severity", "ignore_case", "ignore_spaces", "when"}
_RANGE = {"minimum", "maximum"}  # the one pair of kinds that may share a rule
_LOADER_TABLES = {"load_run"}  # tables the loader writes itself, so a mapping can't

# States of a value read from a source file .
VALUE, DEFAULT, UNKNOWN, BLANK = "value", "default", "unknown", "blank"


class ConfigError(ValueError):
    """A config file breaks the rule format. The validator stops before reading any data."""


def load_rules(config_dir="config", mapping_paths=None):
    """Read the schema, the value sets and the mapping configs, and check them all.

    mapping_paths defaults to every *_mapping.yaml in config_dir. Returns
    {"schema": ..., "value_sets": ..., "mappings": {file name: entries}, "files": [paths]}.
    """
    config_dir = Path(config_dir)
    schema_path, sets_path = config_dir / "destination_schema.yaml", config_dir / "value_sets.yaml"
    schema = _load_yaml(schema_path)
    table_keys = {t: columns.pop("foreignKeys") for t, columns in schema.items()
                  if isinstance(columns, dict) and "foreignKeys" in columns}
    value_sets = _load_yaml(sets_path) if sets_path.exists() else {}
    paths = [Path(p) for p in mapping_paths] if mapping_paths else sorted(config_dir.glob("*_mapping.yaml"))
    mappings = {p.name: _load_yaml(p) for p in paths}
    problems = _check_value_sets(value_sets) + _check_schema(schema, value_sets) + _check_foreign_keys(schema, table_keys)
    for name, entries in mappings.items():
        problems += _check_mapping(name, entries, schema)
    if problems:
        raise ConfigError("\n".join(problems))
    files = [schema_path] + ([sets_path] if sets_path.exists() else []) + paths
    keys = _foreign_keys(schema, table_keys)
    table_order(schema, keys)  # a circle of foreign keys is a config error now, not when a load starts
    return {"schema": schema, "foreign_keys": keys, "value_sets": value_sets,
            "mappings": mappings, "files": files}


def read_value(rules, entry, raw):
    """One source value to its stored value.

    Returns (state, value, problem). problem is None, or a short reason the value couldn't be
    converted to the column's type, in which case value is None.
    """
    field = rules["schema"][entry["destination_table"]][entry["destination_column"]]
    if "value" in entry:
        raw = str(entry["value"])
    raw = entry.get("value_map", {}).get(raw, raw)
    if raw == "" or raw in [str(v) for v in entry.get("missing_values", [])]:
        if "default_value" in field:
            return DEFAULT, field["default_value"], None
        return BLANK, None, None
    if raw in [str(v) for v in entry.get("unknown_values", [])]:
        if "unknown_value" in field:
            return UNKNOWN, field["unknown_value"], None
        return UNKNOWN, None, None
    try:
        return VALUE, _convert(raw, field["type"], entry), None
    except (ValueError, KeyError):
        return VALUE, None, f"not a {field['type']}"


def check_value(rules, table, column, value, row=None, real=True):
    """Run the column's rules on one stored value.

    row is {table: {column: value}} for the same source row, for the two-column rules. Rules
    only check real values: for a blank, default or unknown value pass real=False, and only
    required_when runs. Returns a list of (rule name, severity) for the rules that failed.
    """
    field = rules["schema"][table][column]
    row = row or {}
    failed = []
    for index, rule in enumerate(field.get("rules", [])):
        if "when" in rule and not _condition(rule["when"], table, row):
            continue
        kinds = [k for k in rule if k in _KINDS]
        kind = kinds[0]
        name = f"{table}.{column}#{index} {'+'.join(kinds)}"
        if kind == "required_when":
            if value is None and _condition(rule["required_when"], table, row):
                failed.append((name, rule["severity"]))
            continue
        if value is None or not real:
            continue
        items = value.split(field["list_delimiter"]) if field.get("list_delimiter") else [value]
        if not all(_passes(rules, rule, kind, item, table, row) for item in items):
            failed.append((name, rule["severity"]))
    return failed


def describe_rule(rules, name):
    """What a rule named as check_value and the validator name it requires, in words, from the same
    config the check reads, such as `must be one of true, false, when attribute_key is housing`.
    None for a name that isn't a rule in the schema."""
    target, _, kinds = name.partition(" ")
    if kinds == "must_exist":
        return f"must already be in {target}, written by another file in the same run"
    table, _, rest = target.partition(".")
    column, _, index = rest.partition("#")
    field = rules["schema"].get(table, {}).get(column)
    if field is None:
        return None
    if kinds == "required":
        return "must have a value"
    if kinds == "type":
        return f"must be {_TYPE_WORDS[field['type']]}"
    if not index.isdigit() or int(index) >= len(field.get("rules", [])):
        return None
    rule = field["rules"][int(index)]
    each = "each item " if field.get("list_delimiter") else ""
    when = f", when {_describe_condition(rule['when'])}" if "when" in rule else ""
    return f"{each}{_describe_kind(rules, rule)}{when}"


def table_order(schema, foreign_keys):
    """Every table after the tables its foreign keys point at. Raises ConfigError if keys go round in a circle."""
    order, path = [], []

    def visit(table):
        if table in order:
            return
        if table in path:
            circle = " -> ".join(path[path.index(table):] + [table])
            raise ConfigError(f"destination_schema.yaml: foreign keys go round in a circle, so no table can be filled "
                              f"first: {circle}")
        path.append(table)
        for _, target, _ in foreign_keys.get(table, []):
            if target != table:
                visit(target)
        path.pop()
        order.append(table)

    for table in schema:
        visit(table)
    return order


def optional_tables(rules, tables):
    """The tables a source row may leave out: those that the row's other tables point at only
    through foreign keys that can be blank. For the course file that's course, through
    course_enrollment.course_id. A blank key on any other table fails its required columns."""
    schema, foreign_keys = rules["schema"], rules["foreign_keys"]
    optional = set()
    for table in tables:
        pointers = [(other, columns) for other in tables - {table}
                    for columns, target, _ in foreign_keys.get(other, []) if target == table]
        if pointers and all(schema[other][c]["nullable"] for other, columns in pointers for c in columns):
            optional.add(table)
    return optional


def key_is_blank(fields, row):
    """A destination row whose whole natural key has no value isn't created: its primary key if
    the row supplies it, else its unique group."""
    columns = [c for c, p in fields.items() if p.get("primary_key") and c in row]
    columns = columns or [c for c, p in fields.items() if p.get("unique") and c in row]
    return bool(columns) and all(row[c] is None for c in columns)


def _load_yaml(path):
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except (OSError, yaml.YAMLError) as error:
        raise ConfigError(f"{path}: {error}") from error


def _convert(raw, type_name, entry):
    if type_name == "str":
        return raw
    if type_name == "int":
        return int(raw)
    if type_name == "float":
        return float(raw)
    if type_name == "bool":
        if raw in [str(v) for v in entry["true_values"]]:
            return True
        if raw in [str(v) for v in entry["false_values"]]:
            return False
        raise ValueError(raw)
    if type_name == "date":
        return datetime.strptime(raw, entry["format"]).date()
    return datetime.fromisoformat(raw)


def _condition(condition, table, row):
    other_table, other_column = _split_column(condition["column"], table)
    other = row.get(other_table, {}).get(other_column)
    if "present" in condition:
        return (other is not None) == condition["present"]
    return other is not None and str(other) == str(condition["equals"])


def _describe_condition(condition):
    if "present" in condition:
        return f"{condition['column']} {'has a value' if condition['present'] else 'is blank'}"
    return f"{condition['column']} is {condition['equals']}"


def _describe_kind(rules, rule):
    if "enum" in rule or "value_set" in rule:
        allowed = rule["enum"] if "enum" in rule else rules["value_sets"][rule["value_set"]]
        relaxed = [word for word, option in (("case", "ignore_case"), ("spaces", "ignore_spaces")) if rule.get(option)]
        return (f"must be one of {', '.join(map(str, allowed))}"
                + (f", ignoring {' and '.join(relaxed)}" if relaxed else ""))
    if "pattern" in rule:
        return f"must match the pattern {rule['pattern']}"
    if "minimum" in rule or "maximum" in rule:
        low, high = rule.get("minimum"), rule.get("maximum")
        if low is not None and high is not None:
            return f"must be between {low} and {high}"
        return f"must be at least {low}" if low is not None else f"must be at most {high}"
    if "max_length" in rule:
        return f"must be at most {rule['max_length']} characters"
    if "academic_year" in rule:
        return "must be an academic year, such as 2024-25"
    if "not_before" in rule:
        return f"must not be before {rule['not_before']}"
    if "not_greater_than" in rule:
        return f"must not be greater than {rule['not_greater_than']}"
    return f"must have a value when {_describe_condition(rule['required_when'])}"


def _split_column(name, table):
    return tuple(name.split(".", 1)) if "." in name else (table, name)


def _normalize(value, rule):
    text = str(value)
    if rule.get("ignore_spaces"):
        text = re.sub(r"\s+", "", text)
    if rule.get("ignore_case"):
        text = text.casefold()
    return text


def _passes(rules, rule, kind, value, table, row):
    if kind in ("enum", "value_set"):
        allowed = rule["enum"] if kind == "enum" else rules["value_sets"][rule["value_set"]]
        return _normalize(value, rule) in {_normalize(v, rule) for v in allowed}
    if kind == "pattern":
        return re.fullmatch(rule["pattern"], str(value)) is not None
    if kind in _RANGE:
        low, high = rule.get("minimum"), rule.get("maximum")
        return (low is None or value >= low) and (high is None or value <= high)
    if kind == "max_length":
        return len(str(value)) <= rule["max_length"]
    if kind == "academic_year":
        match = re.fullmatch(r"([0-9]{4})-([0-9]{2})", str(value))
        return bool(match) and (int(match.group(1)) + 1) % 100 == int(match.group(2))
    other_table, other_column = _split_column(rule[kind], table)
    other = row.get(other_table, {}).get(other_column)
    if other is None:
        return True  # nothing to compare against
    try:
        return value >= other if kind == "not_before" else value <= other
    except TypeError:
        return True  # the other column holds an unknown or default, not a comparable value


def _check_value_sets(value_sets):
    return [f"value_sets.yaml: {name} must be a non-empty list"
            for name, values in value_sets.items() if not isinstance(values, list) or not values]


def _check_schema(schema, value_sets):
    problems = []
    for table, columns in schema.items():
        for column, field in columns.items():
            where = f"destination_schema.yaml: {table}.{column}"
            unknown_keys = set(field) - _FIELD_KEYS
            if unknown_keys:
                problems.append(f"{where}: unknown properties {sorted(unknown_keys)}")
            if field.get("type") not in _TYPES:
                problems.append(f"{where}: type must be one of {sorted(_TYPES)}")
                continue
            for key in ("default_value", "unknown_value"):
                if key in field and not _fits_type(field[key], field["type"]):
                    problems.append(f"{where}: {key} {field[key]!r} is not a {field['type']}")
            if "list_delimiter" in field and field["type"] != "str":
                problems.append(f"{where}: list_delimiter needs a str column, not {field['type']}")
            for index, rule in enumerate(field.get("rules", [])):
                problems += _check_rule(f"{where} rule {index}", rule, table, field["type"], schema, value_sets)
    return problems


def _check_foreign_keys(schema, table_keys):
    """A table-level foreignKeys entry: {fields: [...], reference: {resource: table, fields: [...]}}, where the
    reference's fields are exactly that table's primary key, in order, with the same types."""
    problems = []
    for table, keys in table_keys.items():
        where = f"destination_schema.yaml: {table}.foreignKeys"
        if not isinstance(keys, list) or not keys:
            problems.append(f"{where}: must be a non-empty list")
            continue
        for index, key in enumerate(keys):
            here = f"{where} entry {index}"
            reference = key.get("reference") if isinstance(key, dict) else None
            if not isinstance(key, dict) or set(key) != {"fields", "reference"} or not isinstance(reference, dict) \
                    or set(reference) != {"resource", "fields"}:
                problems.append(f"{here}: needs fields and reference, with reference's resource and fields")
                continue
            fields, target, target_fields = key["fields"], reference["resource"], reference["fields"]
            if not (isinstance(fields, list) and isinstance(target_fields, list) and fields
                    and len(fields) == len(target_fields)):
                problems.append(f"{here}: fields and reference fields must be lists of the same length")
                continue
            if not all(isinstance(name, str) for name in [*fields, *target_fields, target]):
                problems.append(f"{here}: column and table names must be text")
                continue
            missing = [c for c in fields if c not in schema.get(table, {})]
            if missing:
                problems.append(f"{here}: no column {missing} in {table}")
                continue
            if target not in schema:
                problems.append(f"{here}: no table {target!r}")
                continue
            pk = [c for c, f in schema[target].items() if f.get("primary_key")]
            if target_fields != pk:
                problems.append(f"{here}: reference fields must be {target}'s primary key {pk}, not {target_fields}")
                continue
            for column, other in zip(fields, target_fields):
                if schema[table][column].get("type") != schema[target][other].get("type"):
                    problems.append(f"{here}: {table}.{column} and {target}.{other} have different types")
    return problems


def foreign_keys(rules, table):
    """One table's foreign keys, one-column or not: a list of (columns, table pointed at, columns pointed at)."""
    return rules["foreign_keys"].get(table, [])


def _foreign_keys(schema, table_keys):
    """Every foreign key, per table: (columns, table pointed at, columns pointed at). One-column keys come
    from each column's foreign_key, the others from the table's foreignKeys."""
    keys = {}
    for table, columns in schema.items():
        keys[table] = [((column,), *_reference(field["foreign_key"]))
                       for column, field in columns.items() if field.get("foreign_key")]
        keys[table] += [(tuple(key["fields"]), key["reference"]["resource"], tuple(key["reference"]["fields"]))
                        for key in table_keys.get(table, [])]
    return keys


def _reference(target):
    ref_table, ref_column = target.split(".")
    return ref_table, (ref_column,)


def _fits_type(value, type_name):
    expected = {"str": str, "int": int, "float": (int, float), "bool": bool,
                "date": date, "datetime": datetime}[type_name]
    return isinstance(value, expected) and not (type_name in ("int", "float") and isinstance(value, bool))


def _check_rule(where, rule, table, type_name, schema, value_sets):
    if not isinstance(rule, dict):
        return [f"{where}: a rule must be a map, not {rule!r}"]
    problems = []
    kinds = [k for k in rule if k in _KINDS]
    unknown_keys = set(rule) - _KINDS - _OPTIONS
    if unknown_keys:
        problems.append(f"{where}: unknown rule kind {sorted(unknown_keys)}")
    if not kinds or (len(kinds) > 1 and not set(kinds) <= _RANGE):
        problems.append(f"{where}: needs exactly one rule kind (minimum and maximum may share one)")
    if rule.get("severity") not in _SEVERITIES:
        problems.append(f"{where}: severity must be error or warning")
    # Each kind's argument, so a rule that loads can't crash or pass everything while checking.
    if "enum" in rule and not (isinstance(rule["enum"], list) and rule["enum"]):
        problems.append(f"{where}: enum must be a non-empty list, not {rule['enum']!r}")
    for key in sorted(_RANGE & set(rule)):
        if type_name not in ("int", "float"):
            problems.append(f"{where}: {key} needs an int or float column, not {type_name}")
        elif not _fits_type(rule[key], "float"):
            problems.append(f"{where}: {key} must be a number, not {rule[key]!r}")
    if "max_length" in rule and not _fits_type(rule["max_length"], "int"):
        problems.append(f"{where}: max_length must be a whole number, not {rule['max_length']!r}")
    if "value_set" in rule and rule["value_set"] not in value_sets:
        problems.append(f"{where}: no value set named {rule['value_set']!r}")
    if "pattern" in rule:
        try:
            re.compile(rule["pattern"])
        except re.error as error:
            problems.append(f"{where}: bad pattern ({error})")
    for key in ("not_before", "not_greater_than"):
        if key in rule and not _column_exists(rule[key], table, schema):
            problems.append(f"{where}: no column {rule[key]!r}")
    for key in ("required_when", "when"):
        if key in rule:
            condition = rule[key]
            if not isinstance(condition, dict) or "column" not in condition or \
                    len({"equals", "present"} & set(condition)) != 1:
                problems.append(f"{where}: {key} needs a column and either equals or present")
            elif "present" in condition and not isinstance(condition["present"], bool):
                problems.append(f"{where}: {key} present must be true or false, not {condition['present']!r}")
            elif not _column_exists(condition["column"], table, schema):
                problems.append(f"{where}: no column {condition['column']!r}")
    return problems


def _column_exists(name, table, schema):
    other_table, other_column = _split_column(name, table)
    return other_column in schema.get(other_table, {})


def _check_mapping(name, entries, schema):
    problems = []
    for number, entry in enumerate(entries, start=1):
        where = f"{name} entry {number} ({entry.get('source', entry.get('value'))})"
        if "dropped" in entry:
            if set(entry) != {"source", "dropped"} or not entry["dropped"]:
                problems.append(f"{where}: a dropped entry has only source and dropped (the reason)")
            continue
        unknown_keys = set(entry) - _ENTRY_KEYS
        if unknown_keys:
            problems.append(f"{where}: unknown properties {sorted(unknown_keys)}")
        if ("source" in entry) == ("value" in entry):
            problems.append(f"{where}: needs either source or value")
        if entry.get("on_conflict") not in _ACTIONS:
            problems.append(f"{where}: on_conflict must be one of {sorted(_ACTIONS)}")
        if entry.get("destination_table") in _LOADER_TABLES:
            problems.append(f"{where}: {entry['destination_table']} is written by the loader, not by a file")
            continue
        field = schema.get(entry.get("destination_table"), {}).get(entry.get("destination_column"))
        if field is None:
            problems.append(f"{where}: no destination {entry.get('destination_table')}.{entry.get('destination_column')}")
            continue
        if field.get("type") == "date" and "format" not in entry:
            problems.append(f"{where}: a date column needs format")
        if field.get("type") == "bool" and not ("true_values" in entry and "false_values" in entry):
            problems.append(f"{where}: a true/false column needs true_values and false_values")
        if entry.get("unknown_values") and field.get("type") == "str" and "unknown_value" not in field:
            problems.append(f"{where}: unknown_values on a text column whose schema has no unknown_value")
        if "value_map" in entry and not isinstance(entry["value_map"], dict):
            problems.append(f"{where}: value_map must map source values to repaired values")
    return problems
