"""Write and read tables as files, one file per table, CSV or Parquet.

The public API is write_tables(), read_tables() and FORMATS. Every table file the build writes is
written and read here, so a table read back gives exactly what was written.

CSV: a header row of column names, then one line per row. Blank means no value. True and false
are written `true` and `false`, dates and timestamps in ISO 8601, and everything else as Python
writes it. Reading turns each value back into its column's type from the schema.

Parquet: each column has its type from the schema, so nothing is converted on the way back. It
needs the pyarrow package, which is imported only when Parquet is asked for.

A table can carry extra columns before its schema columns, such as the staging area's
source_row; each one is given with its type.
"""

import csv
from datetime import date, datetime
from pathlib import Path

from src.rules.rules import ConfigError

__all__ = ["FORMATS", "check_format", "write_tables", "read_tables"]

FORMATS = ("csv", "parquet")
_INSTALL = "python3 -m pip install -r requirements.txt (it includes pyarrow), from the repository root"


def check_format(fmt):
    """Raise ConfigError unless fmt is a format this machine can write: an unknown format, or Parquet
    without pyarrow. A step calls it before it reads or writes anything, so a bad format costs nothing."""
    if fmt not in FORMATS:
        raise ConfigError(f"format must be one of {', '.join(FORMATS)}, not {fmt!r}")
    if fmt == "parquet":
        _pyarrow()


def write_tables(schema, tables, folder, fmt="csv", extra=None, columns=None):
    """Write each table in tables ({table: [row dicts]}) to folder/<table>.<fmt>.

    extra is {column: type} for columns written before the schema's own, in that order. columns
    is {table: [column names]} to write only some of a table's columns, in schema order.
    """
    if fmt not in FORMATS:
        raise ConfigError(f"format must be one of {', '.join(FORMATS)}, not {fmt!r}")
    pyarrow = _pyarrow() if fmt == "parquet" else None  # before anything is written
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    for table, rows in tables.items():
        wanted = (columns or {}).get(table)
        types = {**(extra or {}), **{c: f["type"] for c, f in schema[table].items() if wanted is None or c in wanted}}
        if fmt == "csv":
            with open(folder / f"{table}.csv", "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(list(types))
                for row in rows:
                    writer.writerow([_format(row.get(c)) for c in types])
        else:
            pa, pq = pyarrow
            arrow_schema = pa.schema([(c, _ARROW[t](pa)) for c, t in types.items()])
            data = {c: [row.get(c) for row in rows] for c in types}
            pq.write_table(pa.Table.from_pydict(data, schema=arrow_schema), folder / f"{table}.parquet")


def read_tables(schema, folder, extra=None):
    """Read every table file in folder back into {table: [row dicts]}, with each value in its
    column's type. The folder must hold one format only."""
    folder = Path(folder)
    files = sorted(p for p in folder.iterdir() if p.suffix in (".csv", ".parquet") and p.stem in schema)
    formats = {p.suffix for p in files}
    if len(formats) > 1:
        raise ConfigError(f"{folder} holds both CSV and Parquet table files; keep one format per folder")
    tables = {}
    for path in files:
        types = {**(extra or {}), **{c: f["type"] for c, f in schema[path.stem].items()}}
        if path.suffix == ".csv":
            with open(path, newline="") as f:
                tables[path.stem] = [{c: _parse(v, types[c]) for c, v in row.items()} for row in csv.DictReader(f)]
        else:
            _, pq = _pyarrow()
            tables[path.stem] = pq.read_table(path).to_pylist()
    return tables


def _format(value):
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return str(value)


def _parse(text, type_name):
    if text == "":
        return None
    if type_name == "str":
        return text
    if type_name == "int":
        return int(text)
    if type_name == "float":
        return float(text)
    if type_name == "bool":
        return {"true": True, "false": False}[text]
    if type_name == "date":
        return date.fromisoformat(text)
    return datetime.fromisoformat(text)


_ARROW = {"str": lambda pa: pa.string(), "int": lambda pa: pa.int64(), "float": lambda pa: pa.float64(),
          "bool": lambda pa: pa.bool_(), "date": lambda pa: pa.date32(), "datetime": lambda pa: pa.timestamp("us")}


def _pyarrow():
    try:
        import pyarrow
        import pyarrow.parquet
    except ImportError as error:
        raise ConfigError(f"Parquet needs the pyarrow package, which isn't installed. Install it: {_INSTALL}") from error
    return pyarrow, pyarrow.parquet
