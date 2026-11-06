"""Validate a run's staged tables against the rules in config/.

The only public API is validate(). It checks the tables the Fixer wrote for a run, under
data/staging/<run id>/fixed/, and reads nothing else of the run: map the files (src/mapper) and
fix them (src/fixer) first, or run every step with src/pipeline. Its sources are in one of two
modes, as their source.yaml says: both Analysis-Ready Files together, or one enrichment file.
Every run gets a run id and writes, under logs/:
- validation_report/<run_id>/summary.yaml: what was checked (files and their SHA-256), counts
  of rows, each failed rule (its field, source column, why it failed and example rows), repairs,
  unknowns and no-values per column.
- validation_report/<run_id>/failures.csv: one line per failure.
- failed_records/<run_id>/<source file>.csv: the rows that failed an `error` rule, unchanged,
  after three link columns (run_id, source_row_number, failure_ids).
And under the staging folder, validated/<source file>/: the rows that passed, which the loader
reads, and a source.yaml that says how many rows passed and how many failed, and gives each table file's SHA-256. Rows that fail only `warning` rules are reported and pass on to loading.

Each value is checked as stored, so a repair or a fix is checked after it's made, and failures.csv
shows the value checked. The source file is read to check it's still the file that was mapped
(its SHA-256), and again only when rows failed, to copy them unchanged into failed_records/. It
refuses a run the Fixer didn't write or didn't finish (fixed/sources.yaml).

Run from normalized-data-model/:
    python -m src.validator.validate --staging data/staging/<run id>
Exit code 0 when the run finishes, whatever it found; 2 when a config is invalid.
"""

import argparse
import csv
import shutil
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import yaml

from src.fixer.fix import STAGE
from src.mapper.map import SOURCE_ROW, _sha256, mapped_columns
from src.rules.rules import describe_rule, ConfigError, check_value, key_is_blank, load_rules, optional_tables
from src.tables.files import read_tables, write_tables

__all__ = ["validate"]

_FAILURE_COLUMNS = ["failure_id", "run_id", "source_file", "source_row_number", "destination_table",
                    "destination_column", "value", "rule", "severity", "failed_record"]
_LINK_COLUMNS = ["run_id", "source_row_number", "failure_ids"]
_EXAMPLES = 5   # rows shown for each failed rule in summary.yaml; failures.csv has them all


def validate(staging, sources=None, config_dir="config", logs_dir="logs", run_id=None):
    """Validate one run's fixed tables and write its report, failed records and validated/.

    staging is a run's folder, data/staging/<run id>; sources are the source file names to check
    together, in order (default: all of them). Returns the summary written to summary.yaml, plus
    "passed_rows" ({file name: row numbers that passed}) and "validated" (the folder written).
    Raises ConfigError when a config is invalid, and ValueError when a source hasn't been fixed,
    the run id already has a report or the sources mix the two modes, before any data is checked
    or a report is written.
    """
    staging = Path(staging)
    run_id = run_id or staging.name
    report_dir = Path(logs_dir) / "validation_report" / run_id
    failed_dir = Path(logs_dir) / "failed_records" / run_id
    fixed = staging / STAGE
    sources = sources or (sorted(p.name for p in fixed.iterdir() if p.is_dir()) if fixed.is_dir() else [])
    unfixed = [name for name in sources if not (fixed / name / "source.yaml").is_file()]
    if not sources or unfixed or not (fixed / "sources.yaml").is_file():
        raise ValueError(f"{fixed} has no fixed tables for {', '.join(unfixed) or 'any source'}; "
                         f"run the Fixer first: python -m src.fixer.fix --staging {staging}")
    not_fixer = [name for name in sources if not (fixed / name / "fixes.yaml").is_file()]
    if not_fixer:
        raise ValueError(f"{fixed} has tables for {', '.join(not_fixer)} that the Fixer didn't write (no fixes.yaml); "
                         f"map the files into a new run and fix it: python -m src.fixer.fix --staging <run>")
    metas = [_read_yaml(fixed / name / "source.yaml") for name in sources]
    if len({m["mode"] for m in metas}) != 1:
        raise ValueError(f"{fixed} holds both modes; give the sources to check together")
    mode = metas[0]["mode"]
    record = _read_yaml(fixed / "sources.yaml")
    if mode == "analysis_ready_files":  # the cohort and course files are checked together, or not at all
        left = [n for n, m in record["mapped"].items() if m == mode and n not in sources]
        if left:
            raise ValueError(f"{staging} has {', '.join(left)} mapped too, and the cohort and course files are checked "
                             f"together: fix it if it isn't fixed (python -m src.fixer.fix --staging {staging}), then "
                             f"give both with --sources")
    rules = load_rules(config_dir, [Path(config_dir) / m["config"] for m in metas])
    if report_dir.exists() or failed_dir.exists():  # never overwrite a run's report or mix in its failed records
        raise ValueError(f"run id {run_id} already has a report under {logs_dir}; give a new run id")
    for meta in metas:  # before the report folder is made, so a refused run uses up nothing
        if _sha256(Path(meta["source_file"])) != meta["sha256"]:
            raise ValueError(f"{meta['source_file']} has changed since it was mapped into {fixed / meta['name']}; "
                             f"map it again")
    report_dir.mkdir(parents=True)
    started = datetime.now(timezone.utc)
    summary = {"run_id": run_id, "mode": mode, "started_at": started.isoformat(timespec="seconds"),
               "staging": str(fixed),
               "files": [{"path": str(m["source_file"]), "role": "input", "sha256": m["sha256"]} for m in metas] +
                        [{"path": str(p), "role": "config", "sha256": _sha256(p)} for p in rules["files"]],
               "foreign_keys": "checked against the cohort file of this run" if mode != "enrichment"
               else "not checked: enrichment mode, no database",
               "results": {}}
    passed_rows, seen = {}, defaultdict(set)
    counter = iter(range(1, 10 ** 12))
    try:
        with open(report_dir / "failures.csv", "w", newline="") as report:
            writer = csv.writer(report)
            writer.writerow(_FAILURE_COLUMNS)
            for meta in metas:
                result, passed = _validate_source(rules, staging, meta, mode, seen, run_id, writer, counter,
                                                  failed_dir, Path(logs_dir), report_dir)
                summary["results"][meta["name"]] = result
                passed_rows[meta["name"]] = passed
    except ValueError:  # staged tables that don't match their source: leave nothing half written
        for folder in [report_dir, failed_dir] + [staging / "validated" / m["name"] for m in metas]:
            shutil.rmtree(folder, ignore_errors=True)
        raise
    summary["finished_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    summary["report"] = str(report_dir)
    summary["failed_records"] = str(failed_dir) if failed_dir.exists() else None
    summary["validated"] = str(staging / "validated")
    with open(report_dir / "summary.yaml", "w") as f:
        yaml.safe_dump(summary, f, sort_keys=False, allow_unicode=True, width=120)
    return dict(summary, passed_rows=passed_rows)


def _read_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)


def _validate_source(rules, staging, meta, mode, seen, run_id, writer, counter, failed_dir, logs_dir, report_dir):
    folder, name = staging / STAGE / meta["name"], meta["name"]
    entries = [e for e in rules["mappings"][meta["config"]] if "dropped" not in e]
    optional = optional_tables(rules, {e["destination_table"] for e in entries})
    staged = read_tables(rules["schema"], folder, extra=SOURCE_ROW)
    by_row = {table: {row.pop("source_row"): row for row in rows} for table, rows in staged.items()}
    numbers = range(1, meta["rows"] + 1)
    short = sorted(table for table, rows in by_row.items() if set(rows) != set(numbers))
    if short:
        raise ValueError(f"{folder}: {', '.join(short)} must hold one line for each of the source's {meta['rows']} "
                         f"rows; map and fix the file into a new run")
    problems = defaultdict(dict)
    with open(folder / "problems.csv", newline="") as f:
        for p in csv.DictReader(f):
            problems[int(p["source_row"])][(p["table"], p["column"])] = (p["value"], p["problem"])
    fixes = _read_yaml(folder / "fixes.yaml")
    kept = _kept_by_a_fix(fixes)
    failures_by_rule = defaultdict(lambda: {"counts": defaultdict(int), "examples": []})
    passed, failed = [], {}
    failed_path = failed_dir / name
    for number in numbers:
        values = {table: rows[number] for table, rows in by_row.items()}
        found = _check_row(rules, entries, optional, values, problems.get(number, {}), mode, seen) + kept.get(number, [])
        errors = [p for p in found if p[4] == "error"]
        ids = []
        for table, column, value, rule, severity in found:
            failure_id = next(counter)
            ids.append(failure_id)
            failure = failures_by_rule[rule]
            failure["counts"][severity] += 1
            failure["field"] = f"{table}.{column}"
            if len(failure["examples"]) < _EXAMPLES:
                failure["examples"].append({"source_row": number, "value": value})
            link = str((failed_path).relative_to(logs_dir)) if errors else ""
            writer.writerow([failure_id, run_id, name, number, table, column, value, rule, severity, link])
        if errors:
            failed[number] = ids
            continue
        passed.append(number)
        _remember(rules["schema"], values, seen)
    if failed:
        _copy_failed_rows(Path(meta["source_file"]), failed, run_id, failed_dir, failed_path)
    _write_validated(rules, staging, meta, by_row, set(passed), len(failed), folder, report_dir)
    result = {"rows_read": meta["rows"], "rows_passed": len(passed), "rows_failed": len(failed),
              "failed_records": str(failed_path) if failed else None,
              "failures": {rule: _describe_failure(rules, entries, rule, failure)
                           for rule, failure in sorted(failures_by_rule.items())},
              "repairs": meta["repairs"], "unknown": meta["unknown"], "no_value": meta["no_value"]}
    result["fixes"] = fixes
    return result, passed


def _describe_failure(rules, entries, rule, failure):
    """One failed rule in summary.yaml: its counts, then the field, the source column the value came from,
    what the rule requires, and the first few rows. failures.csv has every row."""
    table, columns = failure["field"].split(".", 1)
    source = [e["source"] for e in entries if e["destination_table"] == table
              and e["destination_column"] in columns.split(",") and "source" in e]
    return {**failure["counts"], "field": failure["field"], "source_column": ", ".join(source) or None,
            "why": describe_rule(rules, rule) or rule, "examples": failure["examples"]}


def _kept_by_a_fix(fixes):
    """{source row: failures}: a value a fix left alone on purpose, such as a credit that isn't 0 in a year
    after the cutoff, loads as it is with a warning on its column."""
    kept = defaultdict(list)
    for name, details in (fixes.get("details") or {}).items():
        for value in details.get("kept_because_not_zero", []):
            kept[value["source_row"]].append((value["table"], value["column"], _text(value["value"]),
                                              f"{value['table']}.{value['column']} {name}: not 0 after the cutoff",
                                              "warning"))
    return kept


def _copy_failed_rows(source_path, failed, run_id, failed_dir, failed_path):
    """failed_records/<run id>/<source>: the rows that broke an error rule, as the file wrote them, after the
    link columns. The only time the validator reads the source file's rows."""
    failed_dir.mkdir(parents=True, exist_ok=True)
    with open(source_path, newline="") as f, open(failed_path, "w", newline="") as out:
        reader, writer = csv.DictReader(f), csv.writer(out)
        writer.writerow(_LINK_COLUMNS + reader.fieldnames)
        for number, source_row in enumerate(reader, start=1):
            if number in failed:
                writer.writerow([run_id, number, "|".join(map(str, failed[number]))] +
                                [source_row[c] for c in reader.fieldnames])


def _write_validated(rules, staging, meta, staged, passed, failed, folder, report_dir):
    """validated/<source>/: the staged rows that passed, with source_row; the source's description, with the
    validation report's folder and the rows that passed and failed added, so a staged load can apply
    on_error_rows, and each table file's SHA-256, so the loader can tell the files are the ones written here;
    and the Fixer's fixes.yaml, so the loader needn't read fixed/."""
    out = staging / "validated" / meta["name"]
    rows = {table: [{"source_row": n, **row} for n, row in staged_rows.items() if n in passed]
            for table, staged_rows in staged.items()}
    columns = mapped_columns(rules, meta["config"])
    for table, staged_rows in staged.items():  # and any column a fix filled, such as credit_years_observed
        present = {c for row in staged_rows.values() for c in row}
        columns[table] = [c for c in rules["schema"][table] if c in present or c in columns.get(table, [])]
    write_tables(rules["schema"], rows, out, meta["format"], extra=SOURCE_ROW, columns=columns)
    table_files = {p.name: _sha256(p) for p in sorted(out.iterdir()) if p.stem in rules["schema"]}
    with open(out / "source.yaml", "w") as f:
        yaml.safe_dump(dict(meta, validation_report=str(report_dir), rows_passed=len(passed), rows_failed=failed,
                            table_files=table_files), f, sort_keys=False, allow_unicode=True, width=120)
    shutil.copyfile(folder / "fixes.yaml", out / "fixes.yaml")
    with open(folder / "problems.csv", newline="") as f, open(out / "problems.csv", "w", newline="") as g:
        reader, writer = csv.reader(f), csv.writer(g)
        writer.writerow(next(reader))
        writer.writerows(p for p in reader if int(p[0]) in passed)


def _check_row(rules, entries, optional, values, problems, mode, seen):
    """Check one source row's stored values. Returns its failures, each being (table, column,
    the value checked, as text, rule, severity). A value that didn't convert to its type is shown as
    the file wrote it, from problems.csv. A table in optional whose whole key is blank isn't
    on this row, so its columns aren't checked. A value is real unless it's blank, the column's
    unknown value or its default."""
    schema = rules["schema"]
    real, raw_values, found = {}, {}, []
    must_exist = defaultdict(list)
    for entry in entries:
        table, column = entry["destination_table"], entry["destination_column"]
        field = schema[table][column]
        value = values[table][column]
        problem = problems.get((table, column))
        raw = problem[0] if problem else _text(value)
        if problem:
            found.append((table, column, raw, f"{table}.{column} type", "error"))
        real[(table, column)] = (value is not None and problem is None and value != field.get("unknown_value")
                                 and not ("default_value" in field and value == field["default_value"]))
        raw_values[(table, column)] = raw
        if entry.get("must_exist"):
            must_exist[table].append(column)
    skipped = {t for t in optional & set(values) if key_is_blank(schema[t], values[t])}
    for (table, column), is_real in real.items():
        if table in skipped:
            continue
        value = values[table][column]
        if value is None and not schema[table][column]["nullable"]:
            found.append((table, column, raw_values[(table, column)], f"{table}.{column} required", "error"))
            continue
        for rule, severity in check_value(rules, table, column, value, values, real=is_real):
            found.append((table, column, raw_values[(table, column)], rule, severity))
    if mode != "enrichment":  # enrichment foreign keys are the loader's to check
        for table, columns in must_exist.items():
            key = _primary_key(schema[table], values[table])
            if key is not None and key not in seen[table]:
                found.append((table, ",".join(columns), "|".join(map(str, key)), f"{table} must_exist", "error"))
    return found


def _text(value):
    """A stored value as failures.csv shows it, written the way the table files write it."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return value.isoformat() if hasattr(value, "isoformat") else str(value)


def _primary_key(fields, row):
    pk = [c for c, p in fields.items() if p.get("primary_key")]
    if not all(row.get(c) is not None for c in pk):
        return None
    return tuple(row[c] for c in pk)


def _remember(schema, values, seen):
    """Rows that passed, so later files in the run can find them (must_exist)."""
    for table, row in values.items():
        key = _primary_key(schema[table], row)
        if key is not None:
            seen[table].add(key)


def _main(argv=None):
    parser = argparse.ArgumentParser(description="Validate a run's fixed tables against config/ .")
    parser.add_argument("--staging", required=True, help="a run's staging folder, data/staging/<run id>, after the Fixer")
    parser.add_argument("--sources", help="the source file names to check together, comma-separated (default: all)")
    parser.add_argument("--config_dir", default="config")
    parser.add_argument("--logs_dir", default="logs")
    parser.add_argument("--run_id", help="default: the run's id, the staging folder's name")
    args = parser.parse_args(argv)
    args.sources = args.sources.split(",") if args.sources else None
    try:
        summary = validate(**vars(args))
    except ConfigError as error:
        print(f"invalid config:\n{error}", file=sys.stderr)
        return 2
    except ValueError as error:
        parser.error(str(error))
    print(f"run id: {summary['run_id']}")
    for name, result in summary["results"].items():
        print(f"{name}: {result['rows_read']} rows read, {result['rows_passed']} passed, "
              f"{result['rows_failed']} failed")
    print(f"foreign keys: {summary['foreign_keys']}")
    print(f"checked: {summary['staging']}")
    print(f"validated: {summary['validated']}")
    print(f"report: {summary['report']}")
    print(f"failed records: {summary['failed_records'] or 'none'}")
    return 0


if __name__ == "__main__":
    sys.exit(_main())
