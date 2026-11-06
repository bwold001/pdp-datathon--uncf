"""Map source files onto the model's tables, and write them to the staging area.

The only public API is map_files(). It runs in one of two modes: both Analysis-Ready Files with
their mapping configs, or one enrichment file with its config. Each source file's values are
read through src/rules (repairs, codes for "no value" and "unknown", and each column's type),
and written under data/staging/<run id>/mapped/<source file name>/:
- one file per table the source fills, with source_row (1 = the first data row) first, then the
  table's mapped columns. One line per source row, before any merging across rows or files.
- problems.csv: each value that couldn't be turned into its column's type.
- source.yaml: the source file's path, SHA-256 and row count, its mapping config, the run mode,
  the format, and the counts of repairs, unknowns and no-values per column.

The next step reads that folder. Nothing is checked here: the validator does that.

Run from normalized-data-model/:
    python -m src.mapper.map --cohort ../data/raw/pdp_cohort_data.csv \\
        --course ../data/raw/pdp_course_data.csv \\
        --cohort_config config/cohort_mapping.yaml --course_config config/course_mapping.yaml
    python -m src.mapper.map --enrichment data/input/enrichment/on_campus_housing.csv \\
        --enrichment_config config/on_campus_housing_mapping.yaml
Exit code 0 when the files are mapped; 2 when a config or the format is invalid.
"""

import argparse
import csv
import hashlib
import secrets
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import yaml

from src.rules.rules import BLANK, DEFAULT, UNKNOWN, ConfigError, load_rules, read_value
from src.tables.files import FORMATS, check_format, write_tables

__all__ = ["map_files", "mapped_columns"]

STAGE = "mapped"
SOURCE_ROW = {"source_row": "int"}  # the extra first column of every staged table
_PROBLEM_COLUMNS = ["source_row", "table", "column", "value", "problem"]


def map_files(cohort=None, course=None, cohort_config=None, course_config=None, enrichment=None,
              enrichment_config=None, config_dir="config", staging_dir="data/staging", run_id=None, fmt="csv"):
    """Map one run's files into staging_dir/<run id>/mapped/. Returns {"run_id", "staging" (the
    run's folder), "mode", "sources" (the source file names, in order), "rows" ({source: rows mapped})}. Raises ConfigError for an
    invalid config or format, and ValueError for a bad mode or a source the run already mapped,
    before anything is written."""
    check_format(fmt)  # before any file is read, so a missing pyarrow uses up nothing
    inputs = _inputs(cohort, course, cohort_config, course_config, enrichment, enrichment_config)
    rules = load_rules(config_dir, [config for _, config in inputs])
    run_id = run_id or _new_run_id()
    staging = Path(staging_dir) / run_id
    for source_path, _ in inputs:
        if (staging / STAGE / Path(source_path).name).exists():
            raise ValueError(f"run id {run_id} has already mapped {Path(source_path).name}; give a new run id")
    mode = "enrichment" if enrichment else "analysis_ready_files"
    rows = {Path(source_path).name: _map_file(rules, Path(source_path), Path(config_path).name, mode,
                                               staging / STAGE / Path(source_path).name, fmt)
            for source_path, config_path in inputs}
    return {"run_id": run_id, "staging": str(staging), "mode": mode, "sources": list(rows), "rows": rows}


def mapped_columns(rules, config_name):
    """{table: [columns]} that a mapping config writes, in schema order."""
    written = defaultdict(set)
    for entry in rules["mappings"][config_name]:
        if "dropped" not in entry:
            written[entry["destination_table"]].add(entry["destination_column"])
    return {table: [c for c in rules["schema"][table] if c in columns] for table, columns in written.items()}


def _map_file(rules, source_path, config_name, mode, folder, fmt):
    entries = [e for e in rules["mappings"][config_name] if "dropped" not in e]
    tables, problems = defaultdict(list), []
    repairs, unknowns, no_values = Counter(), Counter(), Counter()
    rows = 0
    with open(source_path, newline="") as f:
        for number, source_row in enumerate(csv.DictReader(f), start=1):
            rows = number
            values = defaultdict(dict)
            for entry in entries:
                table, column = entry["destination_table"], entry["destination_column"]
                raw = str(entry["value"]) if "value" in entry else source_row.get(entry["source"], "")
                state, value, problem = read_value(rules, entry, raw)
                name = f"{table}.{column}"
                if raw in entry.get("value_map", {}):
                    repairs[name] += 1
                if state == UNKNOWN:
                    unknowns[name] += 1
                elif state in (BLANK, DEFAULT):
                    no_values[name] += 1
                if problem:
                    problems.append([number, table, column, raw, problem])
                values[table][column] = value
            for table, row in values.items():
                tables[table].append({"source_row": number, **row})
    columns = mapped_columns(rules, config_name)
    write_tables(rules["schema"], {t: tables.get(t, []) for t in columns}, folder, fmt, extra=SOURCE_ROW,
                 columns=columns)
    with open(folder / "problems.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(_PROBLEM_COLUMNS)
        writer.writerows(problems)
    source = {"source_file": str(source_path), "name": source_path.name, "sha256": _sha256(source_path),
              "rows": rows, "config": config_name, "mode": mode, "format": fmt,
              "mapped_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "repairs": dict(sorted(repairs.items())), "unknown": dict(sorted(unknowns.items())),
              "no_value": dict(sorted(no_values.items()))}
    with open(folder / "source.yaml", "w") as f:
        yaml.safe_dump(source, f, sort_keys=False, allow_unicode=True, width=120)
    return rows


def _inputs(cohort, course, cohort_config, course_config, enrichment, enrichment_config):
    """The run's (file, mapping config) pairs, in load order. Exactly one mode."""
    analysis_ready = [cohort, course, cohort_config, course_config]
    if enrichment or enrichment_config:
        if any(analysis_ready) or not (enrichment and enrichment_config):
            raise ValueError("enrichment mode takes only --enrichment and --enrichment_config")
        return [(enrichment, enrichment_config)]
    if not all(analysis_ready):
        raise ValueError("give --cohort, --course, --cohort_config and --course_config, "
                         "or --enrichment and --enrichment_config")
    if Path(cohort).name == Path(course).name:  # results, failed records and staging folders are named by file name
        raise ValueError(f"the cohort and course files are both named {Path(cohort).name}; rename one")
    return [(cohort, cohort_config), (course, course_config)]


def _new_run_id():
    """Start time in UTC plus 6 random hexadecimal characters, so run ids sort by time."""
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + secrets.token_hex(3)


def _sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _main(argv=None):
    parser = argparse.ArgumentParser(description="Map source files into the staging area.")
    for name in ("cohort", "course", "cohort_config", "course_config", "enrichment", "enrichment_config"):
        parser.add_argument(f"--{name}")
    parser.add_argument("--config_dir", default="config")
    parser.add_argument("--staging_dir", default="data/staging")
    parser.add_argument("--run_id")
    parser.add_argument("--format", dest="fmt", default="csv", choices=FORMATS, help="table files (default: csv)")
    args = parser.parse_args(argv)
    try:
        result = map_files(**vars(args))
    except ConfigError as error:
        print(f"invalid config:\n{error}", file=sys.stderr)
        return 2
    except ValueError as error:
        parser.error(str(error))
    print(f"run id: {result['run_id']}")
    print(f"mapped: {Path(result['staging']) / STAGE} ({', '.join(result['sources'])})")
    return 0


if __name__ == "__main__":
    sys.exit(_main())
