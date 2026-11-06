"""Build the sample files.

The only public API is build_sample(). It picks about 10 students so that every known
quirk appears, writes their raw rows to data/input/sample/, and builds every table in
config/destination_schema.yaml from them by reading the mapping configs. The result goes to
data/output/sample/, one CSV per table, written by src/tables/files.py.

The tables are built the same way a load builds them: the sample input is mapped, fixed and
validated into a temporary staging folder (src/mapper, src/fixer, src/validator), and
src/loader/tables.py builds the tables from its validated/ folder, applying on-conflict actions.
Collisions are counted and printed, not written to a file.

Run from normalized-data-model/:
    python -m src.sample.build_sample
"""

import argparse
import csv
import random
import tempfile
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import yaml

from src.fixer.fix import fix
from src.loader.tables import build_tables
from src.mapper.map import map_files
from src.validator.validate import validate
from src.rules.rules import ConfigError, load_rules
from src.tables.files import FORMATS, write_tables

__all__ = ["build_sample"]

# Load order, file name, mapping config and data provider name. The two Analysis-Ready Files are
# read from the repository's data/raw/; the enrichment files from this folder's data/input/.
_SOURCES = [
    ("pdp_cohort_data.csv", "cohort_mapping.yaml", "Achieving the Dream"),
    ("pdp_course_data.csv", "course_mapping.yaml", "Achieving the Dream"),
    ("enrichment/on_campus_housing.csv", "on_campus_housing_mapping.yaml", "synthetic: on-campus housing generator"),
    ("enrichment/institution_events.csv", "institution_events_mapping.yaml", "public: institution events"),
]
_RAW_FILES = {"pdp_cohort_data.csv", "pdp_course_data.csv"}
# Where the sample input is published, from the repository root. data_provider.source_file names
# the sample input file, so its checksum and row count describe that same file.
_SAMPLE_INPUT = "normalized-data-model/data/input/sample"
_BUILD = Path(__file__).resolve().parents[2]


def build_sample(input_dir="data/input", raw_dir="../data/raw", config_dir="config", sample_input_dir="data/input/sample",
                 sample_output_dir="data/output/sample", students=10, seed=2026,
                 loaded_at="2026-10-25T00:00:00", fmt="csv"):
    """Write the sample input and output files, the output tables as CSV or Parquet (fmt). Returns a
    summary of what was built. The committed samples are CSV, so Parquet needs another output folder."""
    if fmt != "csv" and Path(sample_output_dir).resolve() == (_BUILD / "data/output/sample").resolve():
        raise ConfigError(f"the committed samples in data/output/sample are CSV; give another output folder "
                          f"for {fmt}, such as --output_dir output/sample_{fmt}")
    input_dir, raw_dir, config_dir = Path(input_dir), Path(raw_dir), Path(config_dir)
    rules = load_rules(config_dir)
    schema = rules["schema"]
    raw = {name: _read_csv((raw_dir if name in _RAW_FILES else input_dir) / name) for name, _, _ in _SOURCES}
    chosen, reasons = _pick_students(raw, students, seed)
    _write_sample_input(raw, chosen, Path(sample_input_dir))
    with tempfile.TemporaryDirectory() as staging_dir:
        validated = _map(Path(sample_input_dir), config_dir, Path(staging_dir))
        sources = [{"tables": validated / Path(name).name, "config": config, "provider": provider,
                    "source_file": f"{_SAMPLE_INPUT}/{name}"} for name, config, provider in _SOURCES]
        sources[0]["order_by"] = "cohort_membership.cohort"  # as config/pipeline.yaml: the later cohort wins
        tables, report = build_tables(rules, sources, datetime.fromisoformat(loaded_at))
        tables["load_run"] = [_load_run(validated, datetime.fromisoformat(loaded_at), fmt)]
    write_tables(schema, {t: tables[t] for t in schema}, sample_output_dir, fmt)
    return {"students": chosen, "reasons": reasons,
            "rows": {t: len(rows) for t, rows in tables.items()},
            "collisions": report["collisions"], "unconverted": report["unconverted"]}


def _map(sample_input_dir, config_dir, staging_dir):
    """Map, fix and validate the sample input the way a load does, the two Analysis-Ready Files together
    and each enrichment on its own, into one run's staging folder. Returns its validated/ folder. The
    validation reports go in the same temporary folder, and are thrown away with it."""
    (cohort, cohort_config, _), (course, course_config, _), *enrichments = _SOURCES
    map_files(cohort=sample_input_dir / cohort, course=sample_input_dir / course,
              cohort_config=config_dir / cohort_config, course_config=config_dir / course_config,
              config_dir=config_dir, staging_dir=staging_dir, run_id="sample")
    for name, config, _ in enrichments:
        map_files(enrichment=sample_input_dir / name, enrichment_config=config_dir / config,
                  config_dir=config_dir, staging_dir=staging_dir, run_id="sample")
    run = staging_dir / "sample"
    fix(run, config_dir=config_dir, fixes=config_dir / "data_fixes.yaml")
    validate(run, [Path(cohort).name, Path(course).name], config_dir=config_dir, logs_dir=staging_dir / "logs")
    for name, _, _ in enrichments:
        validate(run, [Path(name).name], config_dir=config_dir, logs_dir=staging_dir / "logs",
                 run_id=f"sample-{Path(name).stem}")
    return run / "validated"


def _load_run(validated, loaded_at, fmt):
    """The samples' one load_run row: run id sample, the samples' fixed load time, and no backend or paths.
    The cutoff comes from validated/, as a load reads it. The staging area is CSV, whatever fmt the
    output tables are written in."""
    cutoffs = {d["cutoff"] for p in sorted(validated.glob("*/fixes.yaml"))
               for d in (yaml.safe_load(p.read_text()) or {}).get("details", {}).values() if "cutoff" in d}
    return {"run_id": "sample", "started_at": loaded_at, "finished_at": loaded_at, "file_format": "csv",
            "credit_cutoff": cutoffs.pop() if len(cutoffs) == 1 else None}


def _read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def _pick_students(raw, count, seed):
    """One student per known quirk (the one with the fewest course rows), then random ones up to count."""
    cohort, course = raw["pdp_cohort_data.csv"], raw["pdp_course_data.csv"]
    housing = raw["enrichment/on_campus_housing.csv"]
    course_rows = defaultdict(list)
    for row in course:
        course_rows[row["Student_GUID"]].append(row)
    cohort_terms = {(r["Student_GUID"], r["Cohort"]): r["Cohort_Term"] for r in cohort}
    cohort_count = Counter(r["Student_GUID"] for r in cohort)
    housing_flags = defaultdict(set)
    for row in housing:
        housing_flags[row["Student_GUID"]].add(row["Uses_On_Campus_Housing"])

    def retake(rows):
        terms = defaultdict(set)
        for r in rows:
            if r["Course_Prefix"]:
                terms[(r["Course_Prefix"], r["Course_Number"])].add((r["Academic_Year"], r["Academic_Term"]))
        return any(len(t) > 1 for t in terms.values())

    quirks = {
        "in two cohorts": lambda g, rows: cohort_count[g] > 1,
        "course-file Cohort_Term differs from the cohort file's": lambda g, rows: any(
            r["Cohort_Term"] != cohort_terms.get((g, r["Cohort"])) for r in rows),
        "retake": lambda g, rows: retake(rows),
        "course row with no course record or Section_ID": lambda g, rows: any(
            not r["Course_Prefix"] and r["Academic_Year"] for r in rows),
        "course row in the unknown term": lambda g, rows: any(not r["Academic_Year"] for r in rows),
        "on-campus housing, entering and leaving": lambda g, rows: housing_flags[g] == {"true", "false"},
    }
    candidates = sorted(course_rows, key=lambda g: (len(course_rows[g]), g))
    chosen, reasons = [], {}
    for reason, test in quirks.items():
        if any(test(g, course_rows[g]) for g in chosen):
            reasons.setdefault(next(g for g in chosen if test(g, course_rows[g])), []).append(reason)
            continue
        guid = next(g for g in candidates if g not in chosen and test(g, course_rows[g]))
        chosen.append(guid)
        reasons.setdefault(guid, []).append(reason)
    rest = [g for g in candidates if g not in chosen and len(course_rows[g]) <= 12]
    for guid in random.Random(seed).sample(rest, max(0, count - len(chosen))):
        chosen.append(guid)
        reasons[guid] = ["random"]
    return chosen, reasons


def _write_sample_input(raw, chosen, sample_input_dir):
    keep = set(chosen)
    for name, rows in raw.items():
        selected = rows if "Student_GUID" not in rows[0] else [r for r in rows if r["Student_GUID"] in keep]
        path = sample_input_dir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(selected)


def _main(argv=None):
    parser = argparse.ArgumentParser(description="Build the sample input and output files.")
    parser.add_argument("--students", type=int, default=10)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--format", dest="fmt", default="csv", choices=FORMATS,
                        help="the output tables' format (default: %(default)s)")
    parser.add_argument("--output_dir", default="data/output/sample",
                        help="where the output tables go (default: %(default)s, the committed CSV samples)")
    args = parser.parse_args(argv)
    try:
        summary = build_sample(students=args.students, seed=args.seed, fmt=args.fmt,
                               sample_output_dir=args.output_dir)
    except ConfigError as error:
        parser.error(str(error))
    for guid in summary["students"]:
        print(f"{guid[:8]}…  {', '.join(summary['reasons'][guid])}")
    print("rows:", summary["rows"])
    print("collisions (table, column, action): count:", summary["collisions"])
    print("values that didn't convert to their type:", summary["unconverted"])


if __name__ == "__main__":
    _main()
