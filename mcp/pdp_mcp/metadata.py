"""What the repo says about the model and its source columns. Read from the repo's files, never the database.

- normalized-data-model/config/destination_schema.yaml and value_sets.yaml: the tables and columns
- normalized-data-model/config/pipeline.yaml: which source file each mapping config reads
- normalized-data-model/config/*_mapping.yaml: where each source column goes
- data/dictionaries/column_lookup.csv: what each Analysis-Ready File column means
- normalized-data-model/README.md, "The tables": what one row of each table is

Nothing is filled in that these files don't say. Nothing here reads a database or depends on MCP,
so the chat endpoint can import it and give the same answers as the MCP tools:

    from pdp_mcp.metadata import Metadata
    Metadata().tables(); Metadata().describe("student"); Metadata().define("retention")
"""

import csv
import difflib
import hashlib
import io
import re
from collections import defaultdict
from functools import cached_property
from pathlib import Path

import yaml

from .config import REPO_ROOT

__all__ = ["Metadata", "NotFound", "MetadataError"]

MODEL_DIR = REPO_ROOT / "normalized-data-model"
DICTIONARIES = {"pdp_cohort_data.csv": "data/dictionaries/arf_cohort_data_dictionary.md",
                "pdp_course_data.csv": "data/dictionaries/arf_course_data_dictionary.md"}


class MetadataError(RuntimeError):
    """A metadata file is missing or can't be parsed."""


class NotFound(LookupError):
    def __init__(self, message, suggestions):
        super().__init__(message)
        self.suggestions = suggestions


class Metadata:
    def __init__(self, repo_root: Path = REPO_ROOT):
        self.root = Path(repo_root)
        self.model_dir = self.root / "normalized-data-model"

    @cached_property
    def files(self) -> list[Path]:
        """Every repo file the metadata comes from: the fixed ones, then each mapping config the loader names."""
        fixed = [self.model_dir / "config/destination_schema.yaml", self.model_dir / "config/value_sets.yaml",
                 self.model_dir / "config/pipeline.yaml", self.model_dir / "README.md",
                 self.root / "data/dictionaries/column_lookup.csv"]
        return fixed + [self.model_dir / "config" / source["config"] for source in self._loader["sources"]]

    def status(self) -> tuple[str | None, list[dict]]:
        """(the first problem or None, [{path, sha256}] for every file). Each checksum is of the bytes in the
        snapshot, which is what every answer comes from."""
        problem, listed = None, []
        try:
            snapshot = self._snapshot
        except Exception as exc:
            return f"can't read normalized-data-model/config/pipeline.yaml: {exc}", []
        for path, data in snapshot.items():
            relative = path.relative_to(self.root).as_posix()
            listed.append({"path": relative, "sha256": None if data is None else hashlib.sha256(data).hexdigest()})
            if data is None:
                problem = problem or f"can't read {relative}"
        if problem is None:
            try:
                self.foreign_keys, self.value_sets, self.table_descriptions, self.lookup, self.source_columns
            except Exception as exc:
                problem = f"a metadata file can't be parsed: {exc}"
        return problem, listed

    @cached_property
    def _snapshot(self) -> dict:
        """{path: its bytes, or None if it can't be read}: every file in files, read together on first use.
        Everything this instance answers, and every checksum it reports, comes from these bytes. A file changed
        on disk later shows up in a new Metadata, never half in this one."""
        snapshot = {}
        for path in self.files:
            try:
                snapshot[path] = self._loader_bytes if path == self._loader_path else path.read_bytes()
            except OSError:
                snapshot[path] = None
        return snapshot

    def _read(self, path) -> bytes:
        data = self._snapshot[path]
        if data is None:
            raise MetadataError(f"can't read {path.relative_to(self.root).as_posix()}")
        return data

    @cached_property
    def _loader_path(self) -> Path:
        return self.model_dir / "config/pipeline.yaml"

    @cached_property
    def _loader_bytes(self) -> bytes:
        return self._loader_path.read_bytes()   # read once: it names the other files, and is in the snapshot

    @cached_property
    def _loader(self) -> dict:
        return _yaml(self._loader_bytes)

    @cached_property
    def _schema_file(self) -> dict:
        return _yaml(self._read(self.model_dir / "config/destination_schema.yaml"))

    @cached_property
    def schema(self) -> dict:
        """{table: {column: field}}. A table's foreignKeys list isn't a column: see foreign_keys."""
        return {t: {c: f for c, f in columns.items() if c != "foreignKeys"} for t, columns in self._schema_file.items()}

    @cached_property
    def foreign_keys(self) -> dict:
        """{table: [{columns, references_table, references_columns}]}, in the order of their first column: each
        column's foreign_key, and the table's foreignKeys over several columns (Frictionless Table Schema)."""
        keys = {}
        for table, columns in self.schema.items():
            found = [_foreign_key(c, f["foreign_key"]) for c, f in columns.items() if f.get("foreign_key")]
            found += [{"columns": k["fields"], "references_table": k["reference"]["resource"],
                       "references_columns": k["reference"]["fields"]}
                      for k in self._schema_file[table].get("foreignKeys", [])]
            order = list(columns)
            keys[table] = sorted(found, key=lambda k: order.index(k["columns"][0]))
        return keys

    @cached_property
    def value_sets(self) -> dict:
        return _yaml(self._read(self.model_dir / "config/value_sets.yaml"))

    @cached_property
    def table_descriptions(self) -> dict:
        """{table: what one row is}, from the "The tables" section of the model's README."""
        text = self._read(self.model_dir / "README.md").decode("utf-8").replace("\r\n", "\n")   # as read_text did
        section = text.split("## The tables", 1)[1].split("\n## ", 1)[0]
        return {m.group(1): m.group(2).strip()
                for m in re.finditer(r"^\| `([a-z_]+)` \| (.+?) \|$", section, re.M)}

    @cached_property
    def lookup(self) -> dict:
        """{(file, column): row of column_lookup.csv}."""
        text = self._read(self.root / "data/dictionaries/column_lookup.csv").decode("utf-8-sig")
        return {(r["file"], r["column_in_csv"]): r for r in csv.DictReader(io.StringIO(text, newline=""))}

    @cached_property
    def source_columns(self) -> list[dict]:
        """One entry per source column of every file the loader reads, in load order."""
        columns = {}
        for source in self._loader["sources"]:
            file = Path(source["path"]).name
            for entry in _yaml(self._read(self.model_dir / "config" / source["config"])):
                if "source" not in entry:
                    continue   # a fixed value, not a column of the file
                key = (file, entry["source"])
                if key not in columns:
                    found = self.lookup.get(key, {})
                    columns[key] = {
                        "kind": "source", "source_file": file, "source_column": entry["source"],
                        "dictionary_name": found.get("dictionary_name") or None,
                        "description": found.get("description") or None,
                        "dictionary_file": DICTIONARIES.get(file),
                        "destinations": [], "missing_values": [], "unknown_values": [], "value_map": {}}
                column = columns[key]
                if "destination_table" in entry and not entry.get("dropped"):
                    destination = {"table": entry["destination_table"], "column": entry["destination_column"]}
                    if destination not in column["destinations"]:
                        column["destinations"].append(destination)
                for name in ("missing_values", "unknown_values"):
                    column[name] += [str(v) for v in entry.get(name, []) if str(v) not in column[name]]
                column["value_map"].update({str(k): str(v) for k, v in (entry.get("value_map") or {}).items()})
        return list(columns.values())

    def tables(self) -> list[dict]:
        """The model's tables, by name, with what one row of each is."""
        return [{"name": t, "type": "table", "in_model": True, "description": self.table_descriptions.get(t)}
                for t in sorted(self.schema)]

    def describe(self, table) -> dict:
        """One model table's columns and keys, as destination_schema.yaml defines them. Raises NotFound.

        The loader creates every table from the same file, so these are the keys a loaded database has.
        A database's own column types (TEXT, BIGINT) aren't in it: data_type is None.
        """
        name = table if table in self.schema else next(
            (t for t in self.schema if t.casefold() == table.strip().casefold()), None)
        if name is None:
            raise NotFound(f"No table named {table!r} in the normalized model.", suggest(table, list(self.schema)))
        fields = self.schema[name]
        unique = defaultdict(list)
        for column, field in fields.items():
            if field.get("unique"):
                unique[field["unique"]].append(column)
        return {
            **next(t for t in self.tables() if t["name"] == name),
            "columns": [{"name": c, "data_type": None, "model_type": f["type"], "nullable": f["nullable"],
                         "primary_key": bool(f.get("primary_key"))} for c, f in fields.items()],
            "primary_key": [c for c, f in fields.items() if f.get("primary_key")],
            "foreign_keys": self.foreign_keys[name],
            "referenced_by": sorted(({"table": t, "columns": k["columns"], "references_columns": k["references_columns"]}
                                     for t, keys in self.foreign_keys.items() for k in keys
                                     if k["references_table"] == name),
                                    key=lambda r: (r["table"], r["columns"])),
            "unique_constraints": sorted(unique.values())}

    def normalized_column(self, table, column) -> dict:
        field = self.schema[table][column]
        rules = field.get("rules", [])
        sources = [{k: s[k] for k in ("source_file", "source_column", "dictionary_name", "description")}
                   for s in self.source_columns if {"table": table, "column": column} in s["destinations"]]
        descriptions = {s["description"] for s in sources if s["description"]}
        return {
            "kind": "normalized", "table": table, "column": column,
            "description": descriptions.pop() if len(descriptions) == 1 else None,
            "model_type": field["type"], "nullable": field["nullable"],
            "primary_key": bool(field.get("primary_key")), "foreign_key": field.get("foreign_key"),
            "unique_group": field.get("unique"),
            "default_value": _text(field.get("default_value")), "unknown_value": _text(field.get("unknown_value")),
            "allowed_values": self._allowed_values(rules), "rules": rules, "sources": sources}

    def _allowed_values(self, rules):
        values = []
        for rule in rules:
            if "when" in rule:
                continue   # applies to some rows only
            listed = rule.get("enum") or self.value_sets.get(rule.get("value_set"), [])
            values += [str(v) for v in listed if str(v) not in values]
        return values or None

    def define(self, column, table=None, source_file=None) -> list[dict]:
        """Every source and normalized column matching column, source matches first. Raises NotFound."""
        table = (table or "").strip().casefold() or None
        source_file = (source_file or "").strip().casefold() or None
        wanted = column.strip().casefold()
        want_sources, want_normalized = table is None or source_file is not None, source_file is None or table is not None
        if "." in wanted and wanted.split(".", 1)[0] in self.schema:
            table, wanted = wanted.split(".", 1)   # table.column names a normalized column only
            want_sources, want_normalized = False, True

        sources = [s for s in self.source_columns if want_sources
                   and (source_file is None or s["source_file"].casefold() == source_file)
                   and wanted in {s["source_column"].casefold(), (s["dictionary_name"] or "").casefold()}]
        normalized = [self.normalized_column(t, c) for t, fields in self.schema.items() for c in fields
                      if want_normalized and (table is None or t.casefold() == table) and c.casefold() == wanted]

        if not sources and not normalized:
            names = sorted({s["source_column"] for s in self.source_columns}
                           | {s["dictionary_name"] for s in self.source_columns if s["dictionary_name"]}
                           | {c for fields in self.schema.values() for c in fields})
            raise NotFound(f"No column named {column!r}" + _scope(table, source_file) + ".",
                           suggest(column, names))
        return sources + normalized


def suggest(name, names, n=5):
    """Close names, by spelling and then by containing it."""
    folded = {x.casefold(): x for x in names}
    close = difflib.get_close_matches(name.casefold(), folded, n=n, cutoff=0.6)
    close += [k for k in folded if name.casefold() in k and k not in close]
    return [folded[k] for k in close[:n]]


def _scope(table, source_file):
    scope = ([f"table {table!r}"] if table else []) + ([f"file {source_file!r}"] if source_file else [])
    return " in " + " and ".join(scope) if scope else ""


def _foreign_key(column, target):
    table, target_column = target.split(".")
    return {"columns": [column], "references_table": table, "references_columns": [target_column]}


def _text(value):
    return None if value is None else str(value)


def _yaml(data):
    return yaml.safe_load(data.decode("utf-8"))
