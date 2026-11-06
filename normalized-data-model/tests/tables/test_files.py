"""Checks writing and reading table files: CSV and Parquet give back exactly what was written."""

import builtins
from datetime import date, datetime
from pathlib import Path

import pytest

from src.loader.tables import build_tables
from src.mapper.map import map_files
from src.rules.rules import ConfigError, load_rules
from src.tables import files as f
from src.tables.files import read_tables, write_tables

BUILD = Path(__file__).resolve().parents[2]
RULES = load_rules(BUILD / "config")
SCHEMA = RULES["schema"]
SAMPLES = BUILD / "data/output/sample"
RAW = BUILD.parent / "data/raw"
TYPED = {"t": {"s": {"type": "str", "nullable": True}, "i": {"type": "int", "nullable": True},
               "x": {"type": "float", "nullable": True}, "b": {"type": "bool", "nullable": True},
               "d": {"type": "date", "nullable": True}, "dt": {"type": "datetime", "nullable": True}}}
ROWS = [{"s": "a|b", "i": 3, "x": 12.0, "b": False, "d": date(2026, 10, 29), "dt": datetime(2026, 10, 29, 7, 1, 2)},
        {"s": None, "i": None, "x": None, "b": None, "d": None, "dt": None}]


def test_only_public_api_is_write_read_and_formats():
    assert f.__all__ == ["FORMATS", "check_format", "write_tables", "read_tables"]
    assert f.FORMATS == ("csv", "parquet")


@pytest.mark.parametrize("fmt", ["csv", "parquet"])
def test_every_type_and_a_blank_come_back_as_written(tmp_path, fmt):
    write_tables(TYPED, {"t": ROWS}, tmp_path, fmt)
    assert read_tables(TYPED, tmp_path) == {"t": ROWS}


@pytest.mark.parametrize("fmt", ["csv", "parquet"])
def test_extra_columns_come_first_with_their_own_type(tmp_path, fmt):
    rows = [dict(r, source_row=n) for n, r in enumerate(ROWS, start=1)]
    write_tables(TYPED, {"t": rows}, tmp_path, fmt, extra={"source_row": "int"})
    assert read_tables(TYPED, tmp_path, extra={"source_row": "int"}) == {"t": rows}
    if fmt == "csv":
        assert (tmp_path / "t.csv").read_text().splitlines()[0] == "source_row,s,i,x,b,d,dt"


def test_the_published_samples_read_and_write_back_byte_for_byte(tmp_path):
    tables = read_tables(SCHEMA, SAMPLES)
    assert set(tables) == set(SCHEMA)
    write_tables(SCHEMA, tables, tmp_path)
    for table in SCHEMA:
        assert (tmp_path / f"{table}.csv").read_bytes() == (SAMPLES / f"{table}.csv").read_bytes(), table


@pytest.mark.slow
@pytest.mark.parametrize("fmt", ["csv", "parquet"])
def test_the_full_mock_data_tables_come_back_value_for_value(tmp_path, fmt):
    map_files(cohort=RAW / "pdp_cohort_data.csv", course=RAW / "pdp_course_data.csv",
              cohort_config=BUILD / "config/cohort_mapping.yaml", course_config=BUILD / "config/course_mapping.yaml",
              config_dir=BUILD / "config", staging_dir=tmp_path / "staging", run_id="r")
    mapped = tmp_path / "staging/r/mapped"
    sources = [{"tables": mapped / name, "config": config, "provider": "ATD", "source_file": name}
               for name, config in (("pdp_cohort_data.csv", "cohort_mapping.yaml"),
                                    ("pdp_course_data.csv", "course_mapping.yaml"))]
    tables, _ = build_tables(RULES, sources, datetime(2026, 10, 29))
    write_tables(SCHEMA, tables, tmp_path / "out", fmt)
    back = read_tables(SCHEMA, tmp_path / "out")
    for table, rows in tables.items():
        columns = list(SCHEMA[table])
        typed = lambda row: [(type(row.get(c)), row.get(c)) for c in columns]  # 12 == 12.0 in Python, so types too
        assert [typed(r) for r in back[table]] == [typed(r) for r in rows], table


def test_a_folder_with_both_formats_is_refused(tmp_path):
    write_tables(TYPED, {"t": ROWS}, tmp_path, "csv")
    write_tables({"u": TYPED["t"]}, {"u": ROWS}, tmp_path, "parquet")
    with pytest.raises(ConfigError, match="both CSV and Parquet"):
        read_tables({**TYPED, "u": TYPED["t"]}, tmp_path)


def test_an_unknown_format_is_a_config_error(tmp_path):
    with pytest.raises(ConfigError, match="format must be one of csv, parquet"):
        write_tables(TYPED, {"t": ROWS}, tmp_path, "xlsx")


def test_parquet_without_pyarrow_says_how_to_install_it(tmp_path, monkeypatch):
    real_import = builtins.__import__

    def no_pyarrow(name, *args, **kwargs):
        if name.startswith("pyarrow"):
            raise ImportError("No module named 'pyarrow'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", no_pyarrow)
    with pytest.raises(ConfigError, match="needs the pyarrow package.*requirements.txt"):
        write_tables(TYPED, {"t": ROWS}, tmp_path, "parquet")
    assert not (tmp_path / "t.parquet").exists()
    assert list(tmp_path.iterdir()) == []  # nothing written


def test_written_nowhere_without_pyarrow(tmp_path, monkeypatch):
    real_import = builtins.__import__
    monkeypatch.setattr(builtins, "__import__", lambda name, *a, **k: (_ for _ in ()).throw(ImportError(name))
                        if name.startswith("pyarrow") else real_import(name, *a, **k))
    with pytest.raises(ConfigError):
        write_tables(TYPED, {"t": ROWS}, tmp_path / "new", "parquet")
    assert not (tmp_path / "new").exists()


def test_parquet_columns_have_the_schemas_types_even_when_every_value_is_blank(tmp_path):
    import pyarrow as pa
    import pyarrow.parquet as pq
    write_tables(TYPED, {"t": [ROWS[1]]}, tmp_path, "parquet")  # every value blank: pyarrow alone would guess null
    types = {field.name: field.type for field in pq.read_schema(tmp_path / "t.parquet")}
    assert types == {"s": pa.string(), "i": pa.int64(), "x": pa.float64(), "b": pa.bool_(), "d": pa.date32(),
                     "dt": pa.timestamp("us")}


def test_a_stored_default_is_also_its_columns_unknown_value():
    """Once a value is in a file, a stored default can't be told from a value the file gave, and the rules
    skip defaults. That loses nothing only while every default is also its column's unknown value, which the
    rules skip anyway."""
    defaults = {(t, c): props["default_value"] for t, columns in SCHEMA.items()
                for c, props in columns.items() if "default_value" in props}
    assert defaults  # today: term.academic_year and term.academic_term, both UNKNOWN
    for (table, column), value in defaults.items():
        assert value == SCHEMA[table][column].get("unknown_value"), (table, column)
