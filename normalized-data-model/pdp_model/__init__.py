"""The data model's public API for other projects, such as the Playground server.

Import from here, not from src/: src/ is the pipeline's inside and can change. Every path here is
absolute, so a caller's working folder doesn't matter. Install this folder editable
(pyproject.toml says why).
"""

from functools import cache
from pathlib import Path

import yaml

from src.loader.load import load
from src.mapper.map import _new_run_id
from src.rules.rules import ConfigError, load_rules, table_order

__all__ = ["MODEL_DIR", "CONFIG_DIR", "PIPELINE_CONFIG", "COLUMN_DICTIONARY", "UPLOADS_DIR", "SOURCE_KINDS",
           "ConfigError", "table_names", "expected_columns", "column_dictionary", "schema_field", "new_run_id",
           "run_load", "load_report"]

MODEL_DIR = Path(__file__).resolve().parents[1]
CONFIG_DIR = MODEL_DIR / "config"
PIPELINE_CONFIG = CONFIG_DIR / "pipeline.yaml"
COLUMN_DICTIONARY = CONFIG_DIR / "column_dictionary.yaml"  # built by `python -m src.dictionary.build`
UPLOADS_DIR = MODEL_DIR / "data/uploads"  # inside the repo, so data_provider records a repo-relative path
SOURCE_KINDS = ("cohort", "course")       # the files a caller can replace; enrichment files come from pipeline.yaml


def table_names():
    """The model's tables, each after the tables its foreign keys point at."""
    rules = load_rules(CONFIG_DIR)
    return table_order(rules["schema"], rules["foreign_keys"])


def expected_columns(kind, include_dropped=False):
    """The source columns the cohort or course file's mapping config reads, in the config's order.

    A column marked dropped: is left out unless include_dropped, because a file without it maps the same.
    """
    config_name = _source(kind)["config"]
    rules = load_rules(CONFIG_DIR, [CONFIG_DIR / config_name])
    columns = []
    for entry in rules["mappings"][config_name]:
        if "source" not in entry or ("dropped" in entry and not include_dropped):
            continue
        if entry["source"] not in columns:
            columns.append(entry["source"])
    return columns


def column_dictionary():
    """What each normalized column means: one record per table and column the cohort or course file writes.

    Each record has table, column, dictionary_name, description_source, description, dictionary_values
    ([{code, meaning}], the dictionary's codes, not the stored ones), notes and sources
    ([{source_file, source_column, dictionary_file, lookup_description}]).
    """
    with open(COLUMN_DICTIONARY, encoding="utf-8") as f:
        return yaml.safe_load(f) or []


def schema_field(table, column):
    """How destination_schema.yaml stores one column, or None if the model has no such column.

    Returns {type, nullable, unknown_value, allowed_values}. allowed_values lists the codes from the
    column's enum or value_set rules that apply to every row, or is None if no rule lists them.
    """
    rules = _rules()
    field = rules["schema"].get(table, {}).get(column)
    if field is None:
        return None
    allowed = []
    for rule in field.get("rules", []):
        if "when" in rule:
            continue  # applies to some rows only
        listed = rule.get("enum") or rules["value_sets"].get(rule.get("value_set"), [])
        allowed += [str(v) for v in listed if str(v) not in allowed]
    unknown = field.get("unknown_value")
    return {"type": field["type"], "nullable": field["nullable"],
            "unknown_value": None if unknown is None else str(unknown), "allowed_values": allowed or None}


def new_run_id():
    """A new run id in the loader's format, for a caller that needs the id before the run starts."""
    return _new_run_id()


def run_load(database_url, run_id, cohort=None, course=None, progress=None, tables_dir=None):
    """Run every step and load the model into the database at database_url, replacing its tables.

    database_url is a SQLAlchemy-style URL, with or without an async driver: sqlite:///path or
    postgresql://... cohort and course replace pipeline.yaml's files; the enrichment files stay.
    tables_dir replaces output/tables/, so a caller doesn't overwrite the shared table files.
    Returns the load summary. Raises ConfigError for a bad setting or URL, and RuntimeError for a
    failed load; either way load_report(run_id) has the summary.
    """
    backend, sqlite_path, environ = _target(database_url)
    return load(config=str(PIPELINE_CONFIG), backend=backend, sqlite_path=sqlite_path,
                cohort=_absolute(cohort), course=_absolute(course), run_id=run_id, environ=environ,
                progress=progress, tables_dir=_absolute(tables_dir))


def load_report(run_id):
    """The summary.yaml a load wrote for run_id, or None if there isn't one."""
    logs_dir = MODEL_DIR / (_pipeline().get("logs_dir") or "logs")
    path = logs_dir / "load_report" / run_id / "summary.yaml"
    if not path.is_file():
        return None
    with open(path) as f:
        return yaml.safe_load(f)


@cache
def _rules():
    """The checked schema, value sets and mapping configs, read once per process."""
    return load_rules(CONFIG_DIR)


def _pipeline():
    """pipeline.yaml as a map."""
    with open(PIPELINE_CONFIG) as f:
        return yaml.safe_load(f) or {}


def _source(kind):
    """pipeline.yaml's source entry for the cohort or course file."""
    if kind not in SOURCE_KINDS:
        raise ValueError(f"kind must be one of {', '.join(SOURCE_KINDS)}, not {kind!r}")
    return next(s for s in _pipeline()["sources"] if s["kind"] == kind)


def _target(database_url):
    """(backend, sqlite path, environ) for load(), from a database URL."""
    scheme, _, rest = database_url.partition("://")
    driver = scheme.split("+")[0]  # postgresql+asyncpg and sqlite+aiosqlite: the loader brings its own driver
    if driver == "sqlite":
        path = rest[1:] if rest.startswith("/") else rest  # sqlite:///a.db is a.db, sqlite:////a.db is /a.db
        if not path or path == ":memory:":
            raise ConfigError(f"the loader needs a SQLite file, not {database_url!r}")
        return "sqlite", Path(path).resolve(), {}
    if driver in ("postgres", "postgresql"):
        return "postgres", None, {"PDP_POSTGRES_URL": f"postgresql://{rest}"}
    raise ConfigError(f"the loader writes SQLite or PostgreSQL, not {scheme!r}")


def _absolute(path):
    """An absolute path, or None: load() reads relative paths from the current folder."""
    return str(Path(path).resolve()) if path else None
