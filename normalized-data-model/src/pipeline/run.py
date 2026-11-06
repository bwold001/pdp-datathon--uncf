"""Run every step, from the source files to the database, handing each step the folder the last one wrote.

The public API is run(), plus a command line, and run_steps(), which the loader calls when it
isn't given a staging folder. For the cohort and course files together, then for each enrichment
file, as in config/pipeline.yaml:
1. the Mapper (src/mapper) writes data/staging/<run id>/mapped/;
2. the Fixer (src/fixer) applies config/data_fixes.yaml to it and writes fixed/;
3. the validator (src/validator) checks fixed/, writes its report under logs/, and writes the
   rows that pass to validated/;
then the loader (src/loader) builds every table from validated/ and loads them. Each step's line is
printed as it finishes, with its counts. A step that fails stops the run, the load report's
failed_step names it, and the exit code is the one that step gives on its own.

Run from normalized-data-model/ (or scripts/run_pipeline.sh):
    python -m src.pipeline.run                     # SQLite, at output/pdp.sqlite
    python -m src.pipeline.run --backend postgres  # needs PDP_POSTGRES_URL
    python -m src.pipeline.run --format parquet    # the staging area and output/tables/ in Parquet
Exit code 0 when the load is committed; 2 when a setting or config is invalid, or a step refuses the
run; 1 when the load fails.
"""

import argparse
import os
import sys

from src.fixer.fix import fix
from src.loader.backends import BACKENDS
from src.loader.load import _StepConfigError, _StepRefused, _LoadFailed, _validation_runs, load
from src.mapper.map import map_files
from src.rules.rules import ConfigError
from src.tables.files import FORMATS
from src.validator.validate import validate

__all__ = ["run", "run_steps"]


def run(config="config/pipeline.yaml", **kwargs):
    """Every step, then the load: load() without a staging folder. Returns the load summary."""
    kwargs.pop("staging", None)
    return load(config, **kwargs)


def run_steps(settings, run_id, summary, fmt, progress=None):
    """Map, fix and validate every source into settings["staging_dir"]/<run id>/. Adds each step to
    summary["steps"] and each validation to summary["validation"]; while a step runs,
    summary["failed_step"] names it, so a step that stops the run is named in the load report.
    progress, if given, is called with one line as each step finishes. Returns the run's folder."""
    staging = settings["staging_dir"] / run_id
    say = progress or (lambda line: None)
    for validation_id, files in _validation_runs(settings, run_id):
        summary["failed_step"] = "map"
        mapped = map_files(**files, config_dir=settings["config_dir"], staging_dir=settings["staging_dir"],
                           run_id=run_id, fmt=fmt)
        summary["steps"].append({"step": "map", "wrote": f"{staging}/mapped", "sources": mapped["sources"],
                                 "rows": mapped["rows"]})
        say(f"map: {_here(staging / 'mapped')} ({_each(mapped['rows'], 'rows')})")
        summary["failed_step"] = "fix"
        fixed = fix(staging, mapped["sources"], config_dir=settings["config_dir"], fixes=settings["fixes"])
        summary["steps"].append({"step": "fix", "read": f"{staging}/mapped", "wrote": fixed["fixed"],
                                 "sources": mapped["sources"], "changed": fixed["changed"]})
        for name, rows in fixed["changed"].items():
            summary.setdefault("fixes", {})[name] = summary.get("fixes", {}).get(name, 0) + rows
        changed = _each(fixed["changed"], "rows changed") or "no fix applies"
        say(f"fix: {_here(staging / 'mapped')} -> {_here(fixed['fixed'])} ({', '.join(mapped['sources'])}: {changed})")
        summary["failed_step"] = "validate"
        result = validate(staging=staging, sources=mapped["sources"], config_dir=settings["config_dir"],
                          logs_dir=settings["logs_dir"], run_id=validation_id)
        summary["steps"].append({"step": "validate", "read": result["staging"], "wrote": result["validated"],
                                 "sources": mapped["sources"],
                                 "rows_failed": sum(r["rows_failed"] for r in result["results"].values())})
        for name, counts in result["results"].items():
            summary["validation"][name] = {"run_id": validation_id, "rows_read": counts["rows_read"],
                                           "rows_passed": counts["rows_passed"], "rows_failed": counts["rows_failed"],
                                           "report": result["report"]}
        say(f"validate: {_here(result['staging'])} -> {_here(result['validated'])} (" + "; ".join(
            f"{name}: {r['rows_passed']} passed, {r['rows_failed']} held back" for name, r in result["results"].items()) + ")")
    summary.pop("failed_step")
    failed = {name: v["rows_failed"] for name, v in summary["validation"].items() if v["rows_failed"]}
    if failed and settings["on_error_rows"] == "fail":
        raise _LoadFailed(f"rows broke error rules and on_error_rows is fail: {failed}; "
                          f"see logs/validation_report/ and logs/failed_records/")
    return staging


def _here(path):
    return os.path.relpath(path)


def _each(counts, unit):
    return ", ".join(f"{name}: {n} {unit}" for name, n in counts.items())


def _main(argv=None):
    parser = argparse.ArgumentParser(description="Map, validate and load the normalized data model, step by step.")
    parser.add_argument("--config", default="config/pipeline.yaml", help="pipeline settings (default: %(default)s)")
    parser.add_argument("--backend", choices=sorted(BACKENDS), help="overrides backend in the settings")
    parser.add_argument("--sqlite_path", help="overrides sqlite.path")
    parser.add_argument("--cohort", help="overrides the cohort file's path")
    parser.add_argument("--course", help="overrides the course file's path")
    parser.add_argument("--run_id", help="default: the start time in UTC plus 6 random characters")
    parser.add_argument("--format", dest="fmt", default="csv", choices=FORMATS,
                        help="the staging area's and output/tables/' files (default: %(default)s)")
    args = parser.parse_args(argv)
    try:
        summary = run(**vars(args), progress=print)  # each step's line as it finishes
    except _StepConfigError as error:
        print(error, file=sys.stderr)
        print("see logs/load_report/ for the report", file=sys.stderr)
        return 2
    except ConfigError as error:
        print(f"invalid settings:\n{error}", file=sys.stderr)
        return 2
    except _StepRefused as error:
        print(error, file=sys.stderr)
        print("see logs/load_report/ for the report", file=sys.stderr)
        return 2
    except RuntimeError as error:
        print(error, file=sys.stderr)
        print("see logs/ for the reports", file=sys.stderr)
        return 1
    load_step = summary["steps"][-1]
    print(f"load: {_here(load_step['read'])} ({load_step['rows']} rows)")
    print(f"run id: {summary['run_id']}")
    print(f"loaded into {summary['backend']} at {summary['target']}:")
    for table, rows in summary["tables"].items():
        print(f"  {table}: {rows}")
    print(f"table files: {summary['table_files']}")
    print(f"report: {summary['report']}")
    return 0


if __name__ == "__main__":
    sys.exit(_main())
