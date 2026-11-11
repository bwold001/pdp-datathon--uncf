"""Load the normalized data model into SQLite or PostgreSQL.

The only public API is load(), plus a command line. A load:
1. reads config/pipeline.yaml, with any command-line overrides, and stops on a bad setting;
2. unless it's given a run's staging folder, runs every step first (src/pipeline/run.py): it maps
   each file into data/staging/<run id>/mapped/ (src/mapper), fixes it into fixed/ (src/fixer),
   then the validator checks the cohort and course files together, then each enrichment file, and
   writes the rows that pass to validated/. Each validation writes its own report under logs/;
3. checks each validated table file against the SHA-256 the validator recorded, and stops if any is
   changed, missing or added. Then it builds every table with src/loader/tables.py from validated/.
   Rows that broke only `warning` rules load;
4. replaces the model's tables in the database in one transaction (src/loader/backends.py). A
   failed load rolls back and leaves the database as it was. A load with no student rows, such as
   one where every cohort row failed validation, stops first and keeps the last load;
5. writes every loaded table as a file to output/tables/, CSV or Parquet as --format says, after
   the commit, so the files match the database. A squad without a database reads those;
6. writes logs/load_report/<run id>/summary.yaml, whether the load worked or not.

The source files are only read. Given a staging folder, the loader reads that run's validated/ tables
and nothing else: data_provider describes each file as its source.yaml does. With on_error_rows: fail,
a run whose validation held rows back doesn't load, staged or not; source.yaml says how many.

Run from normalized-data-model/:
    python -m src.loader.load                      # SQLite, at output/pdp.sqlite
    python -m src.loader.load --backend postgres   # needs PDP_POSTGRES_URL
    python -m src.loader.load --staging data/staging/<run id>   # load a run that's already validated
Exit code 0 when the load is committed and its files are written, 1 when it fails, 2 when a setting or config
is invalid or a step refuses the run (as that step would on its own).
"""

import argparse
import hashlib
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

from src.build_identity import build_manifest as _build_manifest
from src.loader.backends import BACKENDS, refresh
from src.loader.tables import build_tables
from src.rules.rules import ConfigError, check_value, load_rules
from src.mapper.map import _new_run_id, _sha256
from src.tables.files import FORMATS, check_format, write_tables

__all__ = ["load"]

_SETTINGS = {"mode", "backend", "sqlite", "postgres", "on_error_rows", "batch_size", "logs_dir", "staging_dir", "fixes", "tables", "sources"}
_SOURCE_KEYS = {"kind", "path", "config", "provider"}
_ORDER_TYPES = {"int", "float", "date", "datetime"}  # order_by compares these as they are, and an academic year by its year
_BUILD = Path(__file__).resolve().parents[2]  # normalized-data-model/: relative paths in the settings start here
_CONFIG_DIR = _BUILD / "config"                # the schema and the mapping configs
_REPOSITORY = _BUILD.parent


class _LoadFailed(RuntimeError):
    """The load stopped before committing. The database is unchanged."""


class _StepRefused(RuntimeError):
    """A step refused the run it was given, as it would when run on its own (exit 2). The database is unchanged."""


class _StepConfigError(ConfigError):
    """A step found a config invalid, such as the fixes file (exit 2). The database is unchanged."""


class _TablesNotWritten(RuntimeError):
    """The database committed, but the table files weren't written. The previous files are kept."""


def load(config="config/pipeline.yaml", backend=None, sqlite_path=None, cohort=None, course=None, run_id=None,
         environ=None, staging=None, fmt=None, progress=None, tables_dir=None):
    """Map, check, build and load every table, replacing what the database held.

    Without staging, it runs every step first (src/pipeline/run.py): map, check, then load what
    passed, through data/staging/<run id>/. With staging (a run's folder), it loads that run's
    validated/ tables only, and reads nothing else: not the source files, not the other stages. progress,
    if given, is called with one line as each step finishes. The keyword arguments override config/pipeline.yaml; paths given here
    are relative to the current folder, paths in the file to normalized-data-model/. Mapping
    configs are read from normalized-data-model/config/. environ defaults to os.environ.
    Returns the summary written to summary.yaml. Raises ConfigError for an invalid setting, a used
    run id or a format this machine can't write, before anything is read or written; _StepConfigError
    or _StepRefused when a step stops the run; and RuntimeError when the load fails, after rolling back.
    The summary's failed_step names the step that stopped it.
    """
    settings = _settings(Path(config), backend, sqlite_path, cohort, course,
                         os.environ if environ is None else environ, staged=staging is not None, tables_dir=tables_dir)
    if staging is not None:  # a staged run's files are in its own format, and so are the table files
        staged = _staged_format(Path(staging), settings)
        if fmt is not None and fmt != staged:
            raise ConfigError(f"{staging} is staged in {staged}, so --format {fmt} doesn't apply; leave it out, "
                              f"or map a new run in {fmt}")
        fmt = staged
    fmt = fmt or "csv"
    check_format(fmt)
    run_id = run_id or (Path(staging).name if staging else _new_run_id())
    report_dir = settings["logs_dir"] / "load_report" / run_id
    claimed = [report_dir]
    if staging is None:
        claimed += [settings["logs_dir"] / "validation_report" / i for i, _ in _validation_runs(settings, run_id)]
        claimed += [settings["staging_dir"] / run_id]
    used = [d for d in claimed if d.exists()]
    if used:
        raise ConfigError(f"run id {run_id} already has a report at {used[0]}; give a new run id")
    report_dir.mkdir(parents=True)  # claims the run id
    started = datetime.now(timezone.utc)
    summary = {"run_id": run_id, "status": "failed", "backend": settings["backend"], "target": settings["display"],
               "started_at": started.isoformat(timespec="seconds"), "validation": {}, "steps": []}
    try:
        if staging is None:
            from src.pipeline.run import run_steps  # map and check every source, handing each step the folder
            staging = run_steps(settings, run_id, summary, fmt, progress)
        staging = Path(staging)
        rules = load_rules(settings["config_dir"], [s["config_path"] for s in settings["sources"]])
        folders = [staging / "validated" / s["path"].name for s in settings["sources"]]
        missing = [str(f) for f in folders if not (f / "source.yaml").is_file()]
        if missing:
            raise _LoadFailed(f"no validated tables for {', '.join(missing)}; validate the run first")
        described = [_read_yaml(f / "source.yaml") for f in folders]
        changed = _changed_tables(folders, described, rules["schema"])
        if changed:
            raise _LoadFailed(f"validated tables aren't what the validator wrote: {', '.join(changed)}; "
                              f"map, fix and validate the files into a new run")
        failed = {d["name"]: d["rows_failed"] for d in described if d["rows_failed"]}
        if failed and settings["on_error_rows"] == "fail":  # a staged run was validated without this setting
            raise _LoadFailed(f"rows broke error rules and on_error_rows is fail: {failed}; "
                              f"see logs/validation_report/ and logs/failed_records/")
        # data_provider describes the file that was mapped, as source.yaml records it, not the settings
        sources = [dict(s, tables=f, source_file=_repo_path(Path(d["source_file"])))
                   for s, f, d in zip(settings["sources"], folders, described)]
        summary["staging"] = str(staging)
        tables, report = build_tables(rules, sources, started.replace(tzinfo=None, microsecond=0))
        tables["load_run"] = [{**_load_run(settings, run_id, started, staging, folders, report_dir),
                               "build_manifest": _build_manifest(settings, folders, rules)}]
        broken = [rule for column, value in tables["load_run"][0].items()
                  for rule, severity in check_value(rules, "load_run", column, value) if severity == "error"]
        if broken:  # the loader writes this row itself, so its own rules hold it to the schema too
            raise _LoadFailed(f"the load_run row breaks {', '.join(broken)}: {tables['load_run'][0]}")
        summary["held_back"] = report["held_back"]
        summary["collisions"] = {f"{t}.{c} ({a})": n for (t, c, a), n in sorted(report["collisions"].items())}
        if report["unconverted"]:  # the validator holds these rows back, so this means the two disagree
            raise _LoadFailed(f"values that didn't convert passed validation: {report['unconverted']}")
        if not tables.get("student"):  # a full refresh would swap the last good load for an empty model
            raise _LoadFailed("no student rows passed validation, so the last load was kept; "
                              "see logs/validation_report/ and logs/failed_records/")
        summary["tables"] = refresh(BACKENDS[settings["backend"]], settings["target"], rules["schema"],
                                    rules["foreign_keys"], tables, settings["batch_size"],
                                    stamp=("load_run", "finished_at"))  # when the rows were written
        summary["steps"].append({"step": "load", "read": str(staging / "validated"), "rows": sum(summary["tables"].values())})
        summary["status"] = "loaded"
        try:
            summary["table_files"] = _write_table_files(settings["tables_dir"], rules["schema"], tables, fmt)
        except Exception as error:
            summary["status"] = "loaded, tables not written"
            summary["error"] = f"{type(error).__name__}: {error}"
            raise _TablesNotWritten(f"load {run_id} committed to the database, but the table files in "
                                    f"{settings['tables_dir']} weren't written, so they're from the last load: "
                                    f"{summary['error']}") from error
    except ConfigError as error:  # a config a step rejected, such as the fixes file
        summary["error"] = f"ConfigError: {error}"
        if summary.get("failed_step"):
            raise _StepConfigError(f"the {summary['failed_step']} step stopped the run: {error}") from error
        raise
    except _TablesNotWritten:
        raise
    except ValueError as error:
        summary["error"] = f"{type(error).__name__}: {error}"
        if summary.get("failed_step"):  # a step's refusal, which it gives exit 2 for when run on its own
            raise _StepRefused(f"the {summary['failed_step']} step refused run {run_id}, and the database was not "
                              f"changed: {error}") from error
        raise RuntimeError(f"load {run_id} failed, and the database was not changed: {summary['error']}") from error
    except Exception as error:
        summary["error"] = f"{type(error).__name__}: {error}"
        raise RuntimeError(f"load {run_id} failed, and the database was not changed: {summary['error']}") from error
    finally:
        summary["finished_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        summary["report"] = str(report_dir / "summary.yaml")
        with open(report_dir / "summary.yaml", "w") as f:
            yaml.safe_dump(summary, f, sort_keys=False, allow_unicode=True, width=120)
    return summary


def _changed_tables(folders, described, schema):
    """The validated table files that aren't as the validator wrote them: changed, missing or added."""
    changed = []
    for folder, source in zip(folders, described):
        written = source.get("table_files", {})
        found = {p.name: _sha256(p) for p in folder.iterdir() if p.stem in schema}
        changed += [str(folder / name) for name in sorted(written.keys() | found.keys())
                    if written.get(name) != found.get(name)]
    return changed


def _load_run(settings, run_id, started, staging, folders, report_dir):
    """The one load_run row: which run built the database, and where its reports and staging are. Read
    from validated/ alone, as the run recorded it: each source's source.yaml and fixes.yaml. finished_at
    is set by refresh(), just before the commit."""
    described = [_read_yaml(f / "source.yaml") for f in folders]
    started = started.replace(tzinfo=None, microsecond=0)
    return {"run_id": run_id, "started_at": started, "finished_at": started,  # until refresh() stamps it
            "backend": settings["backend"], "load_report": _local(report_dir / "summary.yaml"),
            "validation_reports": "|".join(sorted({_local(Path(d["validation_report"])) for d in described})) or None,
            "staging_folder": _local(staging), "file_format": described[0]["format"],
            "credit_cutoff": _credit_cutoff(folders)}


def _credit_cutoff(folders):
    """The cutoff the credit-years fix used, from each validated source's fixes.yaml; blank if it didn't run."""
    cutoffs = {d["cutoff"] for f in folders for d in (_read_yaml(f / "fixes.yaml") or {}).get("details", {}).values()
               if "cutoff" in d}
    return cutoffs.pop() if len(cutoffs) == 1 else None


def _local(path):
    """A path from normalized-data-model/ when it's inside it, else as it is."""
    try:
        return Path(path).resolve().relative_to(_BUILD).as_posix()
    except ValueError:
        return str(path)


def _write_table_files(folder, schema, tables, fmt):
    """Every loaded table as one file in folder, written next to it first and then swapped in, so the
    files always match a committed load and a failed write leaves the last ones in place."""
    folder = Path(folder)
    writing, old = folder.with_name(folder.name + ".writing"), folder.with_name(folder.name + ".old")
    for leftover in (writing, old):
        if leftover.exists():
            shutil.rmtree(leftover)
    write_tables(schema, {t: tables.get(t, []) for t in schema}, writing, fmt)
    if folder.exists():
        folder.rename(old)
    try:
        writing.rename(folder)
    except OSError:
        if old.exists() and not folder.exists():
            old.rename(folder)  # the previous files go back, so a failed swap keeps them
        raise
    if old.exists():
        shutil.rmtree(old)
    return str(folder)


def _settings(config, backend, sqlite_path, cohort, course, environ, staged=False, tables_dir=None):
    """Read and check pipeline.yaml and the overrides. Raises ConfigError listing every problem. staged: the
    load reads a run's validated/ tables, so the source files aren't needed, and can't be overridden."""
    try:
        with open(config) as f:
            raw = yaml.safe_load(f) or {}
    except (OSError, yaml.YAMLError) as error:
        raise ConfigError(f"{config}: {error}") from error
    if not isinstance(raw, dict):
        raise ConfigError(f"{config}: must be a map of settings")
    base = _BUILD
    problems = [f"{config}: unknown setting {key!r}" for key in sorted(set(raw) - _SETTINGS)]
    backend = backend or raw.get("backend")
    if raw.get("mode", "full_refresh") != "full_refresh":
        problems.append(f"{config}: mode must be full_refresh, the only mode")
    if backend not in BACKENDS:
        problems.append(f"backend must be one of {sorted(BACKENDS)}, not {backend!r}")
    if raw.get("on_error_rows", "skip") not in ("skip", "fail"):
        problems.append(f"{config}: on_error_rows must be skip or fail")
    batch_size = raw.get("batch_size", 5000)
    if not isinstance(batch_size, int) or isinstance(batch_size, bool) or batch_size < 1:
        problems.append(f"{config}: batch_size must be a whole number of at least 1")
    sources, overrides = [], {"cohort": cohort, "course": course}
    if staged and (cohort or course):
        problems.append("a staged run is loaded from its validated/ tables, so --cohort and --course don't apply: "
                        "give them to the Mapper, or run every step with python -m src.pipeline.run")
    for number, source in enumerate(raw.get("sources") or [], start=1):
        where = f"{config}: source {number}"
        if not isinstance(source, dict) or not _SOURCE_KEYS <= set(source) <= _SOURCE_KEYS | {"order_by"} or \
                not all(isinstance(v, str) and v for v in source.values()):
            problems.append(f"{where} needs exactly {sorted(_SOURCE_KEYS)}, and may have order_by, each a non-empty text")
            continue
        if "order_by" in source:
            problems += _check_order_by(where, source["order_by"])
        path = Path(overrides[source["kind"]]) if overrides.get(source["kind"]) else base / source["path"]
        if Path(source["config"]).name != source["config"]:
            problems.append(f"{where}: config must be the name of a mapping config in config/, such as "
                            f"cohort_mapping.yaml, not a path: {source['config']}")
            continue
        config_path = _CONFIG_DIR / source["config"]
        for label, p in (("file", path), ("mapping config", config_path)):
            if not p.is_file() and not (staged and label == "file"):
                problems.append(f"{where}: no {label} at {p}")
        sources.append({**source, "path": path, "config_path": config_path, "source_file": _repo_path(path)})
    kinds = [s["kind"] for s in sources]
    if kinds.count("cohort") != 1 or kinds.count("course") != 1 or set(kinds) - {"cohort", "course", "enrichment"}:
        problems.append(f"{config}: sources need one cohort, one course, and any number of enrichment files")
    elif kinds[:2] != ["cohort", "course"]:  # the course file's students and cohorts are checked against the cohort file's
        problems.append(f"{config}: sources go in the order cohort, course, then enrichment files, not {', '.join(kinds)}")
    stems = [s["path"].stem for s in sources]
    if len(stems) != len(set(stems)):  # the validator names reports, failed records and run ids by file name
        problems.append(f"{config}: two sources share a file name; rename one")
    elif not problems and not staged:  # a staged run was checked when it was mapped
        digests = [hashlib.sha256(s["path"].read_bytes()).hexdigest() for s in sources]
        if len(digests) != len(set(digests)):  # data_provider has one row per file content
            problems.append(f"{config}: two sources are the same file; list it once")
    if not problems:  # every mapping config, before any step runs: a table the loader fills, a column not in the schema
        try:
            load_rules(_CONFIG_DIR, [s["config_path"] for s in sources])
        except ConfigError as error:
            problems.append(f"{config}: a mapping config is invalid, so no step runs:\n{error}")
    fixes = base / raw.get("fixes", "config/data_fixes.yaml") if isinstance(raw.get("fixes", ""), str) else None
    if fixes is None or not fixes.is_file():
        problems.append(f"{config}: fixes must name the fixes file, such as config/data_fixes.yaml; none at {fixes}")
    target = display = None
    if backend == "sqlite":
        target = Path(sqlite_path) if sqlite_path else base / (raw.get("sqlite") or {}).get("path", "output/pdp.sqlite")
        display = str(target)
    elif backend == "postgres":
        variable = (raw.get("postgres") or {}).get("url_env", "PDP_POSTGRES_URL")
        target = environ.get(variable)
        if not target:
            problems.append(f"backend postgres needs the connection URL in the environment variable {variable}, "
                            f"such as postgresql://user:password@localhost:5432/pdp")
        else:
            display, problem = _describe_postgres(target)
            if problem:
                problems.append(f"{variable}: {problem}")
    if not isinstance(raw.get("logs_dir", "logs"), str) or not isinstance(raw.get("staging_dir", "data/staging"), str) or \
            not isinstance(raw.get("sqlite") or {}, dict) or not isinstance(raw.get("postgres") or {}, dict) or \
            not isinstance(raw.get("tables") or {}, dict):
        problems.append(f"{config}: logs_dir and staging_dir are paths, and sqlite, postgres and tables are maps")
    elif set(raw.get("tables") or {}) - {"path"}:  # the format is the command line's, not a setting
        problems.append(f"{config}: tables takes only path, not {sorted(set(raw['tables']) - {'path'})}; the files' "
                        f"format comes from --format")
    if problems:
        raise ConfigError("\n".join(problems))
    return {"backend": backend, "target": target, "display": display, "on_error_rows": raw.get("on_error_rows", "skip"),
            "batch_size": batch_size, "logs_dir": base / raw.get("logs_dir", "logs"),
            "staging_dir": base / raw.get("staging_dir", "data/staging"), "fixes": fixes, "sources": sources,
            "tables_dir": Path(tables_dir) if tables_dir else base / ((raw.get("tables") or {}).get("path") or "output/tables"),
            "config_dir": _CONFIG_DIR}


def _staged_format(staging, settings):
    """The format a staged run's validated/ tables are in, from their source.yaml (csv if none is there yet)."""
    for source in settings["sources"]:
        described = staging / "validated" / source["path"].name / "source.yaml"
        if described.is_file():
            return _read_yaml(described)["format"]
    return "csv"


def _read_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)


def _check_order_by(where, order_by):
    """order_by names a destination column, table.column, that sorts as a year or a number, never as text."""
    with open(_CONFIG_DIR / "destination_schema.yaml") as f:
        schema = yaml.safe_load(f) or {}
    table, _, column = order_by.partition(".")
    field = schema.get(table, {}).get(column) if isinstance(schema.get(table), dict) else None
    if not isinstance(field, dict):
        return [f"{where}: order_by {order_by!r} is not a column, table.column, in destination_schema.yaml"]
    is_year = any(isinstance(r, dict) and r.get("academic_year") for r in field.get("rules", []))
    if not is_year and field.get("type") not in _ORDER_TYPES:
        return [f"{where}: order_by {order_by!r} would compare text; it needs an academic_year rule or a "
                f"number or date column"]
    return []


def _describe_postgres(url):
    """Where a connection URL points, without its password. Also checks psycopg is installed."""
    try:
        from psycopg.conninfo import conninfo_to_dict
    except ImportError:
        return None, "the postgres backend needs psycopg: python -m pip install -r requirements.txt"
    try:
        parts = conninfo_to_dict(url)
    except Exception as error:  # psycopg raises ProgrammingError for a malformed URL
        return None, f"not a valid connection URL ({error})"
    return f"postgresql://{parts.get('user', '')}@{parts.get('host', '')}:{parts.get('port', '5432')}/" \
           f"{parts.get('dbname', '')}", None


def _repo_path(path):
    """The path data_provider.source_file records: from the repository root when it's inside it."""
    try:
        return path.resolve().relative_to(_REPOSITORY).as_posix()
    except ValueError:
        return str(path.resolve())


def _validation_runs(settings, run_id):
    """(validation run id, map_files() arguments): the cohort and course files together, then each enrichment file."""
    sources = settings["sources"]
    by_kind = {s["kind"]: s for s in sources if s["kind"] != "enrichment"}
    runs = [(run_id, dict(cohort=by_kind["cohort"]["path"], course=by_kind["course"]["path"],
                          cohort_config=by_kind["cohort"]["config_path"],
                          course_config=by_kind["course"]["config_path"]))]
    return runs + [(f"{run_id}-{s['path'].stem}", dict(enrichment=s["path"], enrichment_config=s["config_path"]))
                   for s in sources if s["kind"] == "enrichment"]


def _main(argv=None):
    parser = argparse.ArgumentParser(description="Load the normalized data model into SQLite or PostgreSQL, "
                                                 "replacing the model's tables.")
    parser.add_argument("--config", default="config/pipeline.yaml", help="pipeline settings (default: %(default)s)")
    parser.add_argument("--backend", choices=sorted(BACKENDS), help="overrides backend in the settings")
    parser.add_argument("--sqlite_path", help="overrides sqlite.path")
    parser.add_argument("--tables_dir", help="overrides tables.path")
    parser.add_argument("--cohort", help="overrides the cohort file's path")
    parser.add_argument("--course", help="overrides the course file's path")
    parser.add_argument("--run_id", help="default: the start time in UTC plus 6 random characters")
    parser.add_argument("--staging", help="load this run's validated tables (data/staging/<run id>) instead of running "
                                          "every step")
    parser.add_argument("--format", dest="fmt", choices=FORMATS,
                        help="the staging area's and output/tables/' files (default: csv; with --staging, the run's own)")
    args = parser.parse_args(argv)
    try:
        summary = load(**vars(args))
    except _StepConfigError as error:
        print(error, file=sys.stderr)
        return 2
    except ConfigError as error:
        print(f"invalid pipeline settings:\n{error}", file=sys.stderr)
        return 2
    except _StepRefused as error:
        print(error, file=sys.stderr)
        return 2
    except RuntimeError as error:
        print(error, file=sys.stderr)
        print("see logs/ for the reports", file=sys.stderr)
        return 1
    print(f"run id: {summary['run_id']}")
    for name, v in summary["validation"].items():
        print(f"{name}: {v['rows_read']} rows read, {v['rows_passed']} passed validation, {v['rows_failed']} held back")
    print(f"held back for a missing reference: {len(summary['held_back'])} rows")
    print(f"loaded into {summary['backend']} at {summary['target']}:")
    for table, rows in summary["tables"].items():
        print(f"  {table}: {rows}")
    print(f"table files: {summary['table_files']}")
    print(f"report: {summary['report']}")
    return 0


if __name__ == "__main__":
    sys.exit(_main())
