"""Build every table in config/destination_schema.yaml in memory, from a run's staged tables.

The only public API is build_tables(). The sample builder and the loader both use it, so the
samples and a full load are built the same way.

The values were read through src/rules when they were mapped (src/mapper), so they're already
stored values. A source row fills several tables at once, in foreign-key order, and finds
existing rows by their natural key.

On-conflict actions: `replace` overwrites, `keep` keeps the existing value, and `append` also
keeps the existing value until it's decided where an appended value is stored. Two more rules
sit on top, whatever the action: a blank or UNKNOWN never overwrites a stored value, and with a
source's order_by (such as cohort_membership.cohort) the later row by that column wins, whatever
order the rows are read in. Collisions are counted, not stored.

A source row whose foreign key points at a row that no file in the run wrote is held back and
reported. The validator checks this for the Analysis-Ready Files (must_exist); for enrichment
files it can't, so it happens here.
"""

import csv
from collections import Counter, defaultdict
from pathlib import Path

import yaml

from src.rules.rules import key_is_blank, optional_tables, table_order
from src.tables.files import read_tables

__all__ = ["build_tables"]

_TERM_ORDER = {"FALL": 0, "WINTER": 1, "SPRING": 2, "SUMMER": 3}
_UNKNOWN = "UNKNOWN"
_PLACEHOLDER_INSTITUTION = {"institution_id": 1, "name": "Placeholder institution", "is_placeholder": True}


def build_tables(rules, sources, loaded_at):
    """Build every table from the sources' staged tables, in order.

    sources is a list of {"tables" (a source's staged folder, such as
    data/staging/<run id>/validated/<file name>), "config" (mapping file name), "provider" (data
    provider name), "source_file" (the path data_provider records)}. Every row in the folder is
    built: the validator has already left out the rows that failed.

    Returns (tables, report): tables is {table: [row dicts]}, and report has "collisions",
    "unconverted" and "held_back" (one entry per source row held back for a missing reference).
    """
    schema = rules["schema"]
    order = table_order(schema, rules["foreign_keys"])  # a row's tables are filled after the ones they point at
    store = _Store(schema)
    store.upsert("institution", dict(_PLACEHOLDER_INSTITUTION), {})
    unconverted, held_back = Counter(), []
    for position, source in enumerate(sources):
        folder = Path(source["tables"])
        order_by = tuple(source["order_by"].split(".")) if source.get("order_by") else None
        entries = [e for e in rules["mappings"][source["config"]] if "dropped" not in e]
        actions = defaultdict(dict)
        for entry in entries:
            actions[entry["destination_table"]][entry["destination_column"]] = entry["on_conflict"]
        optional = optional_tables(rules, {e["destination_table"] for e in entries})
        with open(folder / "source.yaml") as f:
            described = yaml.safe_load(f)
        with open(folder / "problems.csv", newline="") as f:
            for problem in csv.DictReader(f):
                unconverted[(problem["table"], problem["column"])] += 1
        staged = read_tables(schema, folder, extra={"source_row": "int"})
        by_row = defaultdict(dict)
        for table, rows in staged.items():
            for row in rows:
                by_row[row.pop("source_row")][table] = row
        provider = store.upsert("data_provider", {
            "name": source["provider"], "source_file": source["source_file"],
            "file_sha256": described["sha256"], "row_count": described["rows"], "loaded_at": loaded_at}, {})
        for number in sorted(by_row):
            pending = {table: dict(row) for table, row in by_row[number].items()}
            rank = (position, _order_key(pending, order_by), number)
            missing = _missing_references(rules["foreign_keys"], store, pending)
            if missing:
                held_back.append({"source_file": described["name"], "source_row_number": number, "missing": missing})
                continue
            if "data_provider" in pending:  # a file-level value, such as researchid, goes on the file's own row
                store.upsert("data_provider", {"file_sha256": provider["file_sha256"], **pending.pop("data_provider")},
                             actions["data_provider"])
            made = {}
            for table in order:
                if table not in pending:
                    continue
                row = pending[table]
                if table in optional and key_is_blank(schema[table], row):
                    continue  # the row leaves this table out, such as a course-file row with no course record
                for column, props in schema[table].items():
                    target = props.get("foreign_key", "")
                    if row.get(column) is None and target:
                        ref_table, ref_column = target.split(".")
                        if ref_table in made:
                            row[column] = made[ref_table][ref_column]
                        elif store.exists(table, row):
                            continue  # an existing row keeps its own provider and institution
                        elif ref_table == "data_provider":
                            row[column] = provider["provider_id"]
                        elif ref_table == "institution":
                            row[column] = _PLACEHOLDER_INSTITUTION["institution_id"]
                if "source_row_number" in schema[table]:
                    row["source_row_number"] = number
                made[table] = store.upsert(table, row, actions[table], rank)
    tables = {t: list(store.rows[t].values()) for t in schema}
    _fill_term_order(tables["term"])
    _fill_attempt_numbers(tables["course_enrollment"], tables["term"])
    return tables, {"collisions": dict(store.collisions), "unconverted": dict(unconverted), "held_back": held_back}


def _order_key(pending, order_by):
    """Where a row stands among a source's rows for "the later one wins": by its order_by column
    as a year or a number, never as text. A blank or UNKNOWN ranks below every value. Without
    order_by every row ranks the same, so the row read last wins, as before."""
    if order_by is None:
        return (0,)
    value = pending.get(order_by[0], {}).get(order_by[1])
    if value is None or value == _UNKNOWN:
        return (0,)
    if isinstance(value, str):  # an academic year, YYYY-YY: checked by the loader's settings
        return (1, int(value[:4]))
    return (1, value)


def _missing_references(foreign_keys, store, pending):
    """Foreign keys on this row that point at a table the row doesn't fill itself, at a row no
    file has written. For example a housing row for a student who isn't in the cohort file."""
    missing = []
    for table, row in pending.items():
        for columns, ref_table, ref_columns in foreign_keys.get(table, []):
            values = [row.get(c) for c in columns]
            if ref_table in pending or any(v is None for v in values):
                continue
            if len(columns) == 1:
                found = store.has(ref_table, values[0])
            else:
                found = store.exists(ref_table, dict(zip(ref_columns, values)))
            if not found:
                shown = values[0] if len(columns) == 1 else tuple(values)
                missing.append(f"{table}.{','.join(columns)} {shown!r} is not in {ref_table}")
    return missing


def _identity(schema, table, row):
    """The natural key that finds an existing row: the primary key if the mapping supplies it,
    otherwise the table's unique group."""
    columns = schema[table]
    pk = [c for c, p in columns.items() if p.get("primary_key")]
    if all(row.get(c) is not None for c in pk):
        return tuple(row[c] for c in pk)
    unique = [c for c, p in columns.items() if p.get("unique")]
    if not unique:
        raise ValueError(f"{table} has no primary key in the mapping and no unique group to find rows by")
    return tuple(row.get(c) for c in unique)


class _Store:
    """Rows per table, found by identity, with surrogate ids handed out in insert order."""

    def __init__(self, schema):
        self.schema = schema
        self.rows = defaultdict(dict)
        self.collisions = Counter()
        self.ids = defaultdict(set)  # each table's single-column primary key values, for has()
        self.ranks = {}  # (table, identity): {column: the rank of the row that wrote it}

    def exists(self, table, row):
        """True when the row's primary key is fully known and already stored."""
        pk = [c for c, p in self.schema[table].items() if p.get("primary_key")]
        return all(row.get(c) is not None for c in pk) and tuple(row[c] for c in pk) in self.rows[table]

    def has(self, table, value):
        """True when a row of table has this primary key value."""
        return value in self.ids[table]

    def upsert(self, table, row, actions, rank=(0,)):
        """Insert row, or merge it into the stored row with the same identity. rank orders the
        writers for `replace`: a value only overwrites one written at a lower or equal rank. A blank
        never overwrites, and an UNKNOWN only does from a row of the same source that its order_by
        puts later, such as a student's later cohort."""
        key = _identity(self.schema, table, row)
        existing = self.rows[table].get(key)
        if existing is None:
            pk = [c for c, p in self.schema[table].items() if p.get("primary_key")]
            if len(pk) == 1 and row.get(pk[0]) is None:
                row[pk[0]] = len(self.rows[table]) + 1
            if len(pk) == 1:
                self.ids[table].add(row[pk[0]])
            self.rows[table][key] = row
            self.ranks[(table, key)] = {column: rank for column in row}
            return row
        ranks = self.ranks[(table, key)]
        for column, value in row.items():
            old = existing.get(column)
            if value is None:
                continue  # a blank never overwrites
            if old == value:
                ranks[column] = max(ranks.get(column, rank), rank)  # the later writer now holds it
                continue
            if old is None:
                existing[column], ranks[column] = value, rank
                continue
            action = actions.get(column, "replace")
            stored = ranks.get(column, rank)
            later_in_order = rank[0] == stored[0] and rank[1:2] > stored[1:2]  # same source, later by its order_by
            if value == self.schema[table][column].get("unknown_value") and not (action == "replace" and later_in_order):
                self.collisions[(table, column, "unknown not written")] += 1  # only a later cohort's UNKNOWN wins
                continue
            if action == "replace" and rank < stored:
                self.collisions[(table, column, "replace, earlier row kept")] += 1
                continue
            if action == "replace":
                existing[column], ranks[column] = value, rank
            self.collisions[(table, column, action)] += 1
        return existing


def _fill_term_order(terms):
    def order(t):
        if t["academic_year"] == _UNKNOWN:
            return ("9999", 9)
        return (t["academic_year"], _TERM_ORDER.get(t["academic_term"], 8))
    for position, term in enumerate(sorted(terms, key=order), start=1):
        term["sort_order"] = position


def _fill_attempt_numbers(enrollments, terms):
    """Order of a student's rows for the same course, by term, then by source row. Blank when there is no course."""
    term_order = {t["term_id"]: t["sort_order"] for t in terms}
    groups = defaultdict(list)
    for row in enrollments:
        if row.get("course_id") is not None:
            groups[(row["student_id"], row["course_id"])].append(row)
    for rows in groups.values():
        rows.sort(key=lambda r: (term_order[r["term_id"]], r["provider_id"], r["source_row_number"]))
        for attempt, row in enumerate(rows, start=1):
            row["attempt_number"] = attempt
