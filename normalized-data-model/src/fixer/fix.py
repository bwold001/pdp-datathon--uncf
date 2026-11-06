"""Apply the fixes for known mock-data bugs to a run's mapped tables.

The public API is fix() and load_fixes(), plus a command line. Every fix is listed in
config/data_fixes.yaml, with the bug it comes from and the decision behind it. fix() reads a run's
data/staging/<run id>/mapped/<source file>/, applies each switched-on fix to the table and column
it names, whichever file the rows came from, and writes the same layout to fixed/<source file>/,
which the validator reads. It adds fixes.yaml there: the rows each fix changed, and the fixes
that could apply to this file but changed nothing, so a fix that has gone stale is noticed. And it
keeps fixed/sources.yaml: every source mapped/ held, with its mode, and which ones it has fixed, so
the validator can refuse a run with a source mapped but not fixed without reading mapped/.

A fix acts on stored values, before the rules check them, so it must cope with values the rules
would reject: it changes only what it recognizes and leaves the rest for the validator.

Run from normalized-data-model/:
    python -m src.fixer.fix --staging data/staging/<run id>
Exit code 0 when the run's sources are fixed; 2 when the fixes file is invalid.
"""

import argparse
import re
import shutil
import sys
from collections import Counter
from pathlib import Path

import yaml

from src.mapper.map import SOURCE_ROW, mapped_columns
from src.rules.rules import ConfigError, load_rules
from src.tables.files import read_tables, write_tables

__all__ = ["fix", "load_fixes"]

STAGE = "fixed"
_KEYS = {"name", "bug", "decision", "enabled", "table", "column"}
_KINDS = {"replace", "number_format", "blank_after_cutoff"}
_YEAR = re.compile(r"([0-9]{4})-([0-9]{2})")


def load_fixes(path, schema):
    """Read and check the fixes file. Returns the switched-on fixes, in file order."""
    try:
        with open(path) as f:
            raw = yaml.safe_load(f) or {}
    except (OSError, yaml.YAMLError) as error:
        raise ConfigError(f"{path}: {error}") from error
    fixes = raw.get("fixes") if isinstance(raw, dict) else None
    if not isinstance(fixes, list):
        raise ConfigError(f"{path}: needs a list under fixes")
    problems, names = [], set()
    for number, entry in enumerate(fixes, start=1):
        where = f"{Path(path).name} fix {number}"
        if not isinstance(entry, dict):
            problems.append(f"{where}: must be a map")
            continue
        where = f"{where} ({entry.get('name')})"
        kinds = sorted(set(entry) & _KINDS)
        missing = sorted(_KEYS - set(entry))
        if missing:
            problems.append(f"{where}: needs {missing}")
        unknown = sorted(set(entry) - _KEYS - _KINDS)
        if unknown:
            problems.append(f"{where}: unknown properties {unknown}; the kinds are {sorted(_KINDS)}")
        if len(kinds) != 1:
            problems.append(f"{where}: needs exactly one kind of change, one of {sorted(_KINDS)}")
        if entry.get("name") in names:
            problems.append(f"{where}: two fixes are named {entry.get('name')!r}")
        names.add(entry.get("name"))
        if not isinstance(entry.get("enabled"), bool):
            problems.append(f"{where}: enabled must be true or false")
        for key in ("bug", "decision"):
            if key in entry and not (isinstance(entry[key], str) and entry[key].strip()):
                problems.append(f"{where}: {key} must say where it comes from")
        if entry.get("column") not in schema.get(entry.get("table"), {}):
            problems.append(f"{where}: no column {entry.get('table')}.{entry.get('column')} in the schema")
        if "replace" in entry and not (isinstance(entry["replace"], dict) and entry["replace"]):
            problems.append(f"{where}: replace must map old values to new ones")
        if "number_format" in entry:
            problems += _check_number_format(where, entry["number_format"])
        if "blank_after_cutoff" in entry:
            problems += _check_cutoff(where, entry, schema)
    if problems:
        raise ConfigError("\n".join(problems))
    return [entry for entry in fixes if entry["enabled"]]


def _check_number_format(where, spec):
    if not isinstance(spec, dict) or set(spec) != {"match", "format"} or not all(isinstance(v, str) for v in spec.values()):
        return [f"{where}: number_format needs match and format, each a string"]
    try:
        re.compile(spec["match"])
        spec["format"].format(1.0)
    except (re.error, ValueError, IndexError, KeyError) as error:
        return [f"{where}: number_format: {error}"]
    return []


def _check_cutoff(where, entry, schema):
    spec, table = entry["blank_after_cutoff"], entry.get("table")
    if not isinstance(spec, dict) or set(spec) != {"cutoff", "cohort_column", "years"}:
        return [f"{where}: blank_after_cutoff needs cutoff, cohort_column and years"]
    problems = []
    if not _YEAR.fullmatch(str(spec["cutoff"])):
        problems.append(f"{where}: cutoff must be an academic year such as 2025-26, not {spec['cutoff']!r}")
    columns = [spec["cohort_column"]] + [c for cs in (spec["years"] or {}).values() if isinstance(cs, list) for c in cs]
    if not isinstance(spec["years"], dict) or not spec["years"] or \
            not all(isinstance(y, int) and y >= 1 and isinstance(cs, list) for y, cs in spec["years"].items()):
        problems.append(f"{where}: years must map each year number (1, 2, ...) to a list of its columns")
    missing = [c for c in columns if c not in schema.get(table, {})]
    if missing:
        problems.append(f"{where}: no column {missing} in {table}")
    if entry.get("column") in schema.get(table, {}) and schema[table][entry["column"]]["type"] != "int":
        problems.append(f"{where}: {entry['column']} holds a number of years, so it must be an int column")
    return problems


def fix(staging, sources=None, config_dir="config", fixes="config/data_fixes.yaml"):
    """Fix a run's mapped tables into fixed/. sources are the source file names (default: every one
    mapped). Returns {"staging", "sources", "fixed" (the folder written), "changed" ({fix: rows})}.
    Raises ConfigError for an invalid fixes file and ValueError for a source already fixed, before
    anything is written."""
    staging = Path(staging)
    mapped = staging / "mapped"
    sources = sources or sorted(p.name for p in mapped.iterdir() if p.is_dir())
    metas = {name: _read_yaml(mapped / name / "source.yaml") for name in sources}
    rules = load_rules(config_dir, [Path(config_dir) / m["config"] for m in metas.values()])
    active = load_fixes(fixes, rules["schema"])
    done = [name for name in sources if (staging / STAGE / name).exists()]
    if done:
        raise ValueError(f"{staging} has already fixed {', '.join(done)}; map into a new run")
    changed = Counter()
    for name in sources:
        result = _fix_source(rules, active, mapped / name, staging / STAGE / name, metas[name])
        changed.update(result["changed"])
    _record_sources(staging, sources)
    return {"staging": str(staging), "sources": sources, "fixed": str(staging / STAGE), "changed": dict(changed)}


def _fix_source(rules, active, folder, out, meta):
    columns = mapped_columns(rules, meta["config"])
    tables = read_tables(rules["schema"], folder, extra=SOURCE_ROW)
    changed, details = {}, {}
    for entry in active:
        table, column = entry["table"], entry["column"]
        if "replace" in entry or "number_format" in entry:
            if column not in columns.get(table, []):
                continue  # this file doesn't write that column
            count, number = 0, entry.get("number_format")
            for row in tables.get(table, []):
                if row.get(column) in entry.get("replace", {}):
                    row[column] = entry["replace"][row[column]]
                    count += 1
                elif number and isinstance(row.get(column), str) and re.fullmatch(number["match"], row[column]):
                    new = number["format"].format(float(row[column]))
                    count += new != row[column]  # a value already written right isn't a change
                    row[column] = new
        else:
            spec = entry["blank_after_cutoff"]
            written = columns.get(table, [])
            if spec["cohort_column"] not in written or not any(c in written for cs in spec["years"].values() for c in cs):
                continue  # this file doesn't write the credit years
            count, details[entry["name"]] = _blank_after_cutoff(tables.get(table, []), column, spec, table)
            columns[table] = [c for c in rules["schema"][table] if c in columns[table] or c == column]
        changed[entry["name"]] = count
    write_tables(rules["schema"], tables, out, meta["format"], extra=SOURCE_ROW, columns=columns)
    for name in ("source.yaml", "problems.csv"):
        shutil.copyfile(folder / name, out / name)
    result = {"changed": changed, "changed_nothing": sorted(n for n, count in changed.items() if count == 0)}
    if details:
        result["details"] = details
    with open(out / "fixes.yaml", "w") as f:
        yaml.safe_dump(result, f, sort_keys=False, allow_unicode=True, width=120)
    return result


def _record_sources(staging, fixed_now):
    """fixed/sources.yaml: every source in mapped/, with its mode, and the ones fixed so far."""
    path = staging / STAGE / "sources.yaml"
    fixed = set(_read_yaml(path)["fixed"]) if path.is_file() else set()
    mapped = {p.name: _read_yaml(p / "source.yaml")["mode"] for p in sorted((staging / "mapped").iterdir()) if p.is_dir()}
    with open(path, "w") as f:
        yaml.safe_dump({"mapped": mapped, "fixed": sorted(fixed | set(fixed_now))}, f, sort_keys=False)


def _blank_after_cutoff(rows, observed, spec, table):
    """For each row, the credit years its cohort could have reached by the cutoff go in observed,
    and a 0 in a later year becomes blank. Returns (values blanked, details)."""
    cutoff = int(_YEAR.fullmatch(str(spec["cutoff"])).group(1))
    years = max(spec["years"])
    blanked, kept, unreadable = Counter(), [], 0
    for row in rows:
        match = _YEAR.fullmatch(str(row.get(spec["cohort_column"]) or ""))
        if not match:
            unreadable += 1  # left as it is: the validator checks the cohort itself
            row[observed] = None
            continue
        seen = min(max(cutoff - int(match.group(1)) + 1, 0), years)
        row[observed] = seen
        for year, columns in spec["years"].items():
            if year <= seen:
                continue
            for column in columns:
                if row.get(column) == 0:
                    row[column] = None
                    blanked[column] += 1
                elif row.get(column) is not None:
                    kept.append({"source_row": row["source_row"], "table": table, "column": column, "value": row[column]})
    details = {"cutoff": str(spec["cutoff"]), "blanked": dict(sorted(blanked.items())),
               "kept_because_not_zero": kept, "cohort_not_a_year": unreadable}
    return sum(blanked.values()), details


def _read_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)


def _main(argv=None):
    parser = argparse.ArgumentParser(description="Apply config/data_fixes.yaml to a run's mapped tables.")
    parser.add_argument("--staging", required=True, help="a run's staging folder, data/staging/<run id>")
    parser.add_argument("--sources", help="the source file names to fix, comma-separated (default: all)")
    parser.add_argument("--config_dir", default="config")
    parser.add_argument("--fixes", default="config/data_fixes.yaml")
    args = parser.parse_args(argv)
    try:
        result = fix(args.staging, args.sources.split(",") if args.sources else None, args.config_dir, args.fixes)
    except ConfigError as error:
        print(f"invalid fixes:\n{error}", file=sys.stderr)
        return 2
    except ValueError as error:
        parser.error(str(error))
    print(f"fixed: {result['fixed']} ({', '.join(result['sources'])})")
    for name, rows in result["changed"].items():
        print(f"  {name}: {rows} rows" + ("  <- changed nothing" if rows == 0 else ""))
    return 0


if __name__ == "__main__":
    sys.exit(_main())
