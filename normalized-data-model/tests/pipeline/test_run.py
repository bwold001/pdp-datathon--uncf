"""Checks the end-to-end run: each step hands the next the folder it wrote, and a failing step stops the run."""

import builtins
import os
import shutil
import sqlite3
import subprocess
from pathlib import Path

import pytest
import yaml

from src.fixer.fix import fix
from src.loader import load as l
from src.loader.load import load
from src.mapper.map import map_files
from src.pipeline import run as p
from src.rules.rules import ConfigError
from src.validator.validate import validate
from tests.loader.test_load import read_sqlite, sample_sources, sample_tables, without_load_time

BUILD = Path(__file__).resolve().parents[2]
CONFIG = BUILD / "config"
SAMPLE = BUILD / "data/input/sample"


def settings(tmp_path, **changes):
    """A pipeline.yaml in tmp_path reading the sample files, with the database, logs and staging in tmp_path."""
    sources = [
        {"kind": "cohort", "path": str(SAMPLE / "pdp_cohort_data.csv"), "config": "cohort_mapping.yaml",
         "provider": "Achieving the Dream"},
        {"kind": "course", "path": str(SAMPLE / "pdp_course_data.csv"), "config": "course_mapping.yaml",
         "provider": "Achieving the Dream"},
        {"kind": "enrichment", "path": str(SAMPLE / "enrichment/on_campus_housing.csv"),
         "config": "on_campus_housing_mapping.yaml", "provider": "synthetic: on-campus housing generator"}]
    values = {"backend": "sqlite", "sqlite": {"path": str(tmp_path / "pdp.sqlite")}, "logs_dir": str(tmp_path / "logs"),
              "staging_dir": str(tmp_path / "staging"), "tables": {"path": str(tmp_path / "tables")}, "sources": sources}
    values.update(changes)
    (tmp_path / "pipeline.yaml").write_text(yaml.safe_dump(values, sort_keys=False))
    return tmp_path / "pipeline.yaml"


def test_only_public_api_is_run_and_run_steps():
    assert p.__all__ == ["run", "run_steps"]


def test_each_step_reads_the_folder_the_one_before_wrote(tmp_path):
    summary = p.run(settings(tmp_path), run_id="r")
    staging = tmp_path / "staging/r"
    each = [("map", None, f"{staging}/mapped"), ("fix", f"{staging}/mapped", f"{staging}/fixed"),
            ("validate", f"{staging}/fixed", f"{staging}/validated")]
    assert [(s["step"], s.get("read"), s.get("wrote")) for s in summary["steps"]] == \
        each + each + [("load", f"{staging}/validated", None)]
    for stage in ("mapped", "fixed", "validated"):
        assert sorted(x.name for x in (staging / stage).iterdir() if x.is_dir()) == [
            "on_campus_housing.csv", "pdp_cohort_data.csv", "pdp_course_data.csv"]
    record = yaml.safe_load((staging / "fixed/sources.yaml").read_text())  # what the Fixer saw and fixed
    assert record == {"mapped": {"on_campus_housing.csv": "enrichment", "pdp_cohort_data.csv": "analysis_ready_files",
                                 "pdp_course_data.csv": "analysis_ready_files"},
                      "fixed": ["on_campus_housing.csv", "pdp_cohort_data.csv", "pdp_course_data.csv"]}


def test_validated_holds_exactly_the_rows_that_passed(tmp_path):
    rows = (SAMPLE / "pdp_cohort_data.csv").read_text().splitlines()
    rows[2] = rows[2].replace(rows[2].split(",")[1], "not-a-guid", 1)  # one bad student id
    bad = tmp_path / "cohort.csv"
    bad.write_text("\n".join(rows) + "\n")
    map_files(cohort=bad, course=SAMPLE / "pdp_course_data.csv", cohort_config=CONFIG / "cohort_mapping.yaml",
              course_config=CONFIG / "course_mapping.yaml", config_dir=CONFIG, staging_dir=tmp_path / "staging", run_id="r")
    fix(tmp_path / "staging/r", config_dir=CONFIG, fixes=CONFIG / "data_fixes.yaml")
    result = validate(tmp_path / "staging/r", config_dir=CONFIG, logs_dir=tmp_path / "logs")
    passed = result["passed_rows"]["cohort.csv"]
    assert 2 not in passed and len(passed) == len(rows) - 2
    with open(tmp_path / "staging/r/validated/cohort.csv/student.csv") as f:
        staged = [int(line.split(",")[0]) for line in f.read().splitlines()[1:]]
    assert staged == passed


def test_a_source_changed_after_mapping_stops_the_validator(tmp_path):
    cohort = tmp_path / "pdp_cohort_data.csv"
    cohort.write_bytes((SAMPLE / "pdp_cohort_data.csv").read_bytes())
    args = dict(cohort=cohort, course=SAMPLE / "pdp_course_data.csv", cohort_config=CONFIG / "cohort_mapping.yaml",
                course_config=CONFIG / "course_mapping.yaml", config_dir=CONFIG, staging_dir=tmp_path / "staging")
    map_files(**args, run_id="r")
    fix(tmp_path / "staging/r", config_dir=CONFIG, fixes=CONFIG / "data_fixes.yaml")
    cohort.write_text(cohort.read_text() + "\n")
    with pytest.raises(ValueError, match="has changed since it was mapped"):
        validate(staging=tmp_path / "staging/r", config_dir=CONFIG, logs_dir=tmp_path / "logs")
    assert not (tmp_path / "logs").exists()  # checked before the report folder is made, so nothing is used up


def test_the_loader_loads_a_run_that_is_already_validated(tmp_path):
    config = settings(tmp_path)
    p.run(config, run_id="r")
    first = sqlite3.connect(tmp_path / "pdp.sqlite").execute("SELECT COUNT(*) FROM course_enrollment").fetchone()
    summary = load(config, staging=tmp_path / "staging/r", run_id="again")
    assert summary["status"] == "loaded" and [s["step"] for s in summary["steps"]] == ["load"]
    assert sqlite3.connect(tmp_path / "pdp.sqlite").execute("SELECT COUNT(*) FROM course_enrollment").fetchone() == first


def test_a_staging_folder_that_was_never_validated_fails_the_load(tmp_path):
    (tmp_path / "staging/empty").mkdir(parents=True)
    with pytest.raises(RuntimeError, match="no validated tables"):
        load(settings(tmp_path), staging=tmp_path / "staging/empty")


@pytest.mark.parametrize("fmt", ["csv", "parquet"])
@pytest.mark.parametrize("change", ["edited", "cut short", "deleted", "added"])
def test_validated_tables_that_arent_what_the_validator_wrote_stop_the_load(tmp_path, change, fmt):
    config = settings(tmp_path)
    p.run(config, run_id="r", fmt=fmt)
    before = read_sqlite(tmp_path / "pdp.sqlite")
    folder = tmp_path / "staging/r/validated/pdp_course_data.csv"
    table = folder / f"course_enrollment.{fmt}"
    data = table.read_bytes()
    if change == "edited":
        table.write_bytes(data[:-1] + bytes([data[-1] ^ 1]))
    elif change == "cut short":
        table.write_bytes(data[:len(data) // 2])
    elif change == "deleted":
        table.unlink()
    else:
        (folder / f"institution_event.{fmt}").write_bytes(data)
    named = table if change != "added" else folder / f"institution_event.{fmt}"
    with pytest.raises(RuntimeError, match=rf"aren't what the validator wrote: {named}"):
        load(config, staging=tmp_path / "staging/r", run_id="again")
    assert read_sqlite(tmp_path / "pdp.sqlite") == before
    report = yaml.safe_load((tmp_path / "logs/load_report/again/summary.yaml").read_text())
    assert report["status"] == "failed" and "aren't what the validator wrote" in report["error"]


def test_a_run_validated_without_table_checksums_stops_the_load(tmp_path):
    config = settings(tmp_path)
    p.run(config, run_id="r")
    described = tmp_path / "staging/r/validated/pdp_cohort_data.csv/source.yaml"
    source = yaml.safe_load(described.read_text())
    del source["table_files"]
    described.write_text(yaml.safe_dump(source))
    with pytest.raises(RuntimeError, match="aren't what the validator wrote"):
        load(config, staging=tmp_path / "staging/r", run_id="again")


def test_a_staged_run_that_held_rows_back_does_not_load_when_on_error_rows_is_fail(tmp_path):
    failing = tmp_path / "failing"
    failing.mkdir()
    rows = (SAMPLE / "pdp_cohort_data.csv").read_text().splitlines()
    rows[2] = rows[2].replace(rows[2].split(",")[1], "not-a-guid", 1)
    (failing / "pdp_cohort_data.csv").write_text("\n".join(rows) + "\n")  # the name the settings give validated/
    p.run(settings(tmp_path, sqlite={"path": str(tmp_path / "scratch.sqlite")}),  # skip: held back, the rest loads
          cohort=failing / "pdp_cohort_data.csv", run_id="r")
    counts = yaml.safe_load((tmp_path / "staging/r/validated/pdp_cohort_data.csv/source.yaml").read_text())
    assert (counts["rows"], counts["rows_passed"], counts["rows_failed"]) == (len(rows) - 1, len(rows) - 2, 1)
    p.run(settings(tmp_path), run_id="good")
    before = read_sqlite(tmp_path / "pdp.sqlite")
    # the course file holds back the bad student's enrollment, too
    with pytest.raises(RuntimeError, match=r"on_error_rows is fail: \{'pdp_cohort_data.csv': 1, 'pdp_course_data.csv': 1\}"):
        load(settings(tmp_path, on_error_rows="fail"), staging=tmp_path / "staging/r", run_id="again")
    assert read_sqlite(tmp_path / "pdp.sqlite") == before


def test_a_used_run_id_is_refused_before_anything_is_written(tmp_path):
    p.run(settings(tmp_path), run_id="r")
    with pytest.raises(ConfigError, match="already has a report"):
        p.run(settings(tmp_path), run_id="r")


def test_the_script_runs_every_step_and_a_failing_step_sets_the_exit_code(tmp_path):
    script = BUILD / "scripts/run_pipeline.sh"
    env = dict(os.environ)
    done = subprocess.run([str(script), "--config", str(settings(tmp_path, sources=sample_sources())), "--run_id", "r"],
                          capture_output=True, text=True, env=env)
    assert done.returncode == 0, done.stderr
    assert "map: " in done.stdout and "pdp_cohort_data.csv: 11 rows" in done.stdout
    assert "race_cut_at_25_characters: " in done.stdout and "pdp_course_data.csv: 52 passed, 0 held back" in done.stdout
    assert "validate: " in done.stdout and "load: " in done.stdout
    # what the run wrote: every stage, every report, and a database equal to the published samples
    staging = tmp_path / "staging/r"
    for stage in ("mapped", "fixed", "validated"):
        assert sorted(x.name for x in (staging / stage).iterdir() if x.is_dir()) == sorted(
            Path(s["path"]).name for s in sample_sources())
    report = yaml.safe_load((tmp_path / "logs/load_report/r/summary.yaml").read_text())
    assert report["status"] == "loaded" and "failed_step" not in report
    for run_id in ("r", "r-on_campus_housing", "r-institution_events"):
        assert (tmp_path / "logs/validation_report" / run_id / "summary.yaml").is_file()
    assert without_load_time(read_sqlite(tmp_path / "pdp.sqlite")) == sample_tables()
    bad = subprocess.run([str(script), "--config", str(settings(tmp_path, backend="oracle"))],
                         capture_output=True, text=True, env=env)
    assert bad.returncode == 2 and "backend must be one of" in bad.stderr
    failing = tmp_path / "failing"
    failing.mkdir()
    rows = (SAMPLE / "pdp_cohort_data.csv").read_text().splitlines()
    rows[2] = rows[2].replace(rows[2].split(",")[1], "not-a-guid", 1)
    (failing / "cohort.csv").write_text("\n".join(rows) + "\n")
    config = settings(failing, on_error_rows="fail")
    held = subprocess.run([str(script), "--config", str(config), "--cohort", str(failing / "cohort.csv")],
                          capture_output=True, text=True, env=env)
    assert held.returncode == 1 and "on_error_rows is fail" in held.stderr


def copied_sources(folder):
    """The sample files copied into folder, so a test can change or move them."""
    sources = sample_sources()
    for source in sources:
        copy = folder / Path(source["path"]).name
        shutil.copyfile(source["path"], copy)
        source["path"] = str(copy)
    return sources


def test_a_step_that_refuses_the_run_exits_2_and_is_named_in_the_load_report(tmp_path, monkeypatch, capsys):
    sources = copied_sources(tmp_path)
    real_fix = p.fix

    def fix_then_change_the_cohort_file(*args, **kwargs):
        result = real_fix(*args, **kwargs)
        Path(sources[0]["path"]).write_text(Path(sources[0]["path"]).read_text() + "\n")
        return result

    monkeypatch.setattr(p, "fix", fix_then_change_the_cohort_file)
    assert p._main(["--config", str(settings(tmp_path, sources=sources)), "--run_id", "r"]) == 2  # as the validator alone
    err = capsys.readouterr().err
    assert "the validate step refused run r" in err and "has changed since it was mapped" in err
    report = yaml.safe_load((tmp_path / "logs/load_report/r/summary.yaml").read_text())
    assert report["failed_step"] == "validate" and report["status"] == "failed"
    assert not (tmp_path / "pdp.sqlite").exists()


def test_an_invalid_fixes_file_stops_the_run_at_the_fix_step(tmp_path, capsys):
    fixes = yaml.safe_load((CONFIG / "data_fixes.yaml").read_text())
    fixes["fixes"][0]["column"] = "nope"
    (tmp_path / "bad_fixes.yaml").write_text(yaml.safe_dump(fixes))
    config = settings(tmp_path, fixes=str(tmp_path / "bad_fixes.yaml"))
    assert p._main(["--config", str(config), "--run_id", "r"]) == 2
    captured = capsys.readouterr()
    assert "the fix step stopped the run" in captured.err and "no column student.nope" in captured.err
    assert "map: " in captured.out  # the steps before it are printed as they finish
    assert yaml.safe_load((tmp_path / "logs/load_report/r/summary.yaml").read_text())["failed_step"] == "fix"


def test_without_pyarrow_a_parquet_run_stops_before_anything_is_written(tmp_path, monkeypatch, capsys):
    real_import = builtins.__import__
    monkeypatch.setattr(builtins, "__import__", lambda name, *a, **k: (_ for _ in ()).throw(ImportError(name))
                        if name.startswith("pyarrow") else real_import(name, *a, **k))
    assert p._main(["--config", str(settings(tmp_path)), "--run_id", "r", "--format", "parquet"]) == 2
    assert "needs the pyarrow package" in capsys.readouterr().err
    assert not (tmp_path / "staging").exists() and not (tmp_path / "logs").exists()
    from src.mapper import map as m
    assert m._main(["--cohort", str(SAMPLE / "pdp_cohort_data.csv"), "--course", str(SAMPLE / "pdp_course_data.csv"),
                 "--cohort_config", str(CONFIG / "cohort_mapping.yaml"), "--course_config", str(CONFIG / "course_mapping.yaml"),
                    "--staging_dir", str(tmp_path / "staging"), "--run_id", "r", "--format", "parquet"]) == 2
    assert not (tmp_path / "staging").exists()  # the Mapper alone, the same way


def test_a_staged_run_loads_from_validated_alone(tmp_path):
    """With --staging the loader reads validated/ and nothing else: the source files can be gone, and
    data_provider says which file was mapped, from source.yaml."""
    (tmp_path / "files").mkdir()
    sources = copied_sources(tmp_path / "files")
    config = settings(tmp_path, sources=sources)
    p.run_steps(l._settings(config, None, None, None, None, os.environ), "r", {"steps": [], "validation": {}}, "csv")
    shutil.move(tmp_path / "files", tmp_path / "moved")
    summary = load(config, staging=tmp_path / "staging/r")
    assert summary["status"] == "loaded"
    with sqlite3.connect(tmp_path / "pdp.sqlite") as connection:
        recorded = [r[0] for r in connection.execute("SELECT source_file FROM data_provider ORDER BY provider_id")]
    assert recorded == [str((tmp_path / "files" / Path(s["path"]).name).resolve()) for s in sources]
    with pytest.raises(ConfigError, match="--cohort and --course don't apply"):
        load(config, staging=tmp_path / "staging/r", cohort=str(tmp_path / "moved/pdp_cohort_data.csv"))


def test_a_run_id_whose_staging_folder_exists_is_refused(tmp_path):
    (tmp_path / "staging/r").mkdir(parents=True)
    with pytest.raises(ConfigError, match="run id r already has a report"):
        p.run(settings(tmp_path), run_id="r")
    assert not (tmp_path / "logs").exists()


def test_a_parquet_run_goes_through_every_step_in_parquet(tmp_path):
    (tmp_path / "pq").mkdir()
    (tmp_path / "csv").mkdir()
    p.run(settings(tmp_path / "pq", sources=sample_sources()), run_id="r", fmt="parquet")
    p.run(settings(tmp_path / "csv", sources=sample_sources()), run_id="r")
    for stage in ("mapped", "fixed", "validated"):
        files = {f.suffix for f in (tmp_path / "pq/staging/r" / stage).glob("*/*")
                 if f.suffix in (".csv", ".parquet") and f.name != "problems.csv"}  # problems.csv is always CSV
        assert files == {".parquet"}, stage
    assert read_sqlite(tmp_path / "pq/pdp.sqlite").keys() == read_sqlite(tmp_path / "csv/pdp.sqlite").keys()
    pq, csv_ = (without_load_time(read_sqlite(tmp_path / f / "pdp.sqlite")) for f in ("pq", "csv"))
    assert (pq.pop("load_run"), csv_.pop("load_run")) == ([("parquet", "2025-26")], [("csv", "2025-26")])
    assert pq == csv_  # the same database, whatever the staging format


def two_cohort_student_reversed(tmp_path):
    """The sample cohort file with the two-cohort student's rows swapped, and a different gender on each."""
    import csv
    rows = list(csv.DictReader(open(SAMPLE / "pdp_cohort_data.csv")))
    counts = {}
    for r in rows:
        counts[r["Student_GUID"]] = counts.get(r["Student_GUID"], 0) + 1
    student = next(s for s, n in counts.items() if n == 2)
    first, second = [i for i, r in enumerate(rows) if r["Student_GUID"] == student]
    rows[first], rows[second] = rows[second], rows[first]
    later = max(rows[first]["Cohort"], rows[second]["Cohort"])
    for i in (first, second):
        rows[i]["Gender"] = "F" if rows[i]["Cohort"] == later else "M"
    path = tmp_path / "cohort.csv"
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return path, student


@pytest.mark.parametrize("order_by,expected", [("cohort_membership.cohort", "F"), (None, "M")])
def test_order_by_makes_the_later_cohort_win(tmp_path, order_by, expected):
    path, student = two_cohort_student_reversed(tmp_path)
    config = yaml.safe_load(settings(tmp_path).read_text())
    config["sources"][0]["path"] = str(path)
    if order_by:
        config["sources"][0]["order_by"] = order_by
    (tmp_path / "pipeline.yaml").write_text(yaml.safe_dump(config))
    summary = p.run(tmp_path / "pipeline.yaml", run_id="r")
    gender = sqlite3.connect(tmp_path / "pdp.sqlite").execute(
        "SELECT gender FROM student WHERE student_id = ?", (student,)).fetchone()[0]
    assert gender == expected  # without order_by, the row read last wins
    label = "student.gender (replace, earlier row kept)" if order_by else "student.gender (replace)"
    assert summary["collisions"].get(label) == 1  # the load report counts what the rule did


def test_the_default_settings_order_the_cohort_file_by_cohort():
    cohort = next(s for s in yaml.safe_load((BUILD / "config/pipeline.yaml").read_text())["sources"] if s["kind"] == "cohort")
    assert cohort["order_by"] == "cohort_membership.cohort"


@pytest.mark.parametrize("order_by,message", [
    ("student.gender", "would compare text"),
    ("cohort_membership.nope", "is not a column"),
])
def test_order_by_must_sort_as_a_year_or_a_number(tmp_path, order_by, message):
    config = yaml.safe_load(settings(tmp_path).read_text())
    config["sources"][0]["order_by"] = order_by
    (tmp_path / "pipeline.yaml").write_text(yaml.safe_dump(config))
    with pytest.raises(ConfigError, match=message):
        p.run(tmp_path / "pipeline.yaml")
