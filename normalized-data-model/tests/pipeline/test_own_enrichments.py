"""Checks the README's "Load your own enrichment files": its files are the committed ones, and it runs as written."""

import csv
import itertools
import re
import shutil
import sqlite3
from pathlib import Path

import pytest
import yaml

from src.loader import load as l
from src.pipeline import run as p
from src.pipeline.run import run
from src.rules.rules import ConfigError

BUILD = Path(__file__).resolve().parents[2]
README = (BUILD / "README.md").read_text()
SECTION = README.split("## Load your own enrichment files", 1)[1].split("\n## ", 1)[0]
RAW = BUILD.parent / "data/raw"


def example_settings(tmp_path, **changes):
    """config/pipeline_example.yaml with its database, logs, staging and table files moved into tmp_path."""
    settings = yaml.safe_load((BUILD / "config/pipeline_example.yaml").read_text())
    settings.update({"sqlite": {"path": str(tmp_path / "pdp.sqlite")}, "logs_dir": str(tmp_path / "logs"),
                     "staging_dir": str(tmp_path / "staging"), "tables": {"path": str(tmp_path / "tables")}}, **changes)
    (tmp_path / "pipeline.yaml").write_text(yaml.safe_dump(settings, sort_keys=False))
    return tmp_path / "pipeline.yaml"


def test_every_file_the_readme_shows_is_the_committed_file():
    shown = re.findall(r"<!-- example-file: (\S+) -->\n```\w+\n(.*?)```", SECTION, re.S)
    assert [path for path, _ in shown] == ["data/input/enrichment/example_commute.csv", "config/example_commute_mapping.yaml",
                                           "data/input/enrichment/example_orientation.csv",
                                           "config/example_orientation_mapping.yaml"]
    for path, text in shown:
        assert (BUILD / path).read_bytes() == text.encode(), path  # byte for byte: line endings too


def test_the_example_settings_are_the_default_ones_plus_the_two_sources_shown():
    added = yaml.safe_load(re.search(r"```yaml\n(  - kind: enrichment.*?)```", SECTION, re.S).group(1))
    default = yaml.safe_load((BUILD / "config/pipeline.yaml").read_text())
    example = yaml.safe_load((BUILD / "config/pipeline_example.yaml").read_text())
    own = yaml.safe_load(re.search(r"```yaml\n(sqlite:\n.*?)```", SECTION, re.S).group(1))
    assert own == {"sqlite": {"path": "output/example.sqlite"}, "tables": {"path": "output/example_tables"}}
    assert example == dict(default, sources=default["sources"] + added, **own)  # its own database and files


@pytest.mark.slow
def test_the_example_loads_as_written_and_its_query_joins_the_new_facts(tmp_path):
    summary = run(example_settings(tmp_path))
    assert summary["status"] == "loaded"
    connection = sqlite3.connect(tmp_path / "pdp.sqlite")
    query = re.search(r"<!-- example-query:.*?-->\n```sql\n(.*?)```", SECTION, re.S).group(1)
    rows = connection.execute(query).fetchall()
    commute = {r["Student_GUID"]: r["Commutes_Over_30_Minutes"]
               for r in csv.DictReader(open(BUILD / "data/input/enrichment/example_commute.csv"))}
    cohort_rows = [r for r in csv.DictReader(open(RAW / "pdp_cohort_data.csv")) if r["Student_GUID"] in commute]
    assert sorted((s, c) for s, _, _, c, _ in rows) == sorted((r["Student_GUID"], r["Cohort"]) for r in cohort_rows)
    assert all(value == commute[student] for student, value, *_ in rows)
    event_query = re.search(r"<!-- example-event-query:.*?-->\n```sql\n(.*?)```", SECTION, re.S).group(1)
    assert connection.execute(event_query).fetchall() == [
        ("orientation", "New student orientation", "2025-08-25", "Placeholder institution", 1, "example: made up for the README")]
    report = yaml.safe_load(open(Path(summary["validation"]["example_orientation.csv"]["report"]) / "summary.yaml"))
    failures = report["results"]["example_orientation.csv"]["failures"]
    assert any(rule.startswith("institution_event.event_type") and counts.get("warning") == 1 for rule, counts in failures.items())


@pytest.mark.parametrize("order", [o for o in itertools.permutations(range(3)) if o[:2] != (0, 1)])
def test_sources_out_of_order_stop_the_load_with_exit_2_before_any_step(tmp_path, capsys, order):
    sources = yaml.safe_load((BUILD / "config/pipeline_example.yaml").read_text())["sources"][:3]  # cohort, course, housing
    assert p._main(["--config", str(example_settings(tmp_path, sources=[sources[i] for i in order]))]) == 2
    assert "sources go in the order cohort, course, then enrichment files" in capsys.readouterr().err
    assert not (tmp_path / "pdp.sqlite").exists() and not (tmp_path / "staging").exists()


@pytest.mark.parametrize("table,column,message", [("load_run", "backend", "load_run is written by the loader, not by a file"),
                                                  ("no_such_table", "x", "no destination no_such_table.x")])
def test_a_mapping_to_a_table_no_file_fills_stops_the_load_with_exit_2_before_any_step(tmp_path, monkeypatch, capsys,
                                                                                       table, column, message):
    config = tmp_path / "config"
    shutil.copytree(BUILD / "config", config)
    (config / "example_commute_mapping.yaml").write_text(yaml.safe_dump([
        {"source": "Source", "destination_table": table, "destination_column": column, "on_conflict": "replace"}]))
    monkeypatch.setattr(l, "_CONFIG_DIR", config)  # a team's mapping configs live in config/
    (tmp_path / "run").mkdir()
    assert p._main(["--config", str(example_settings(tmp_path / "run"))]) == 2
    assert message in capsys.readouterr().err
    assert not (tmp_path / "run/pdp.sqlite").exists() and not (tmp_path / "run/staging").exists()


def test_a_mapping_config_outside_config_stops_the_load(tmp_path, capsys):
    settings = yaml.safe_load((BUILD / "config/pipeline_example.yaml").read_text())
    settings["sources"][2]["config"] = "../elsewhere/on_campus_housing_mapping.yaml"
    assert p._main(["--config", str(example_settings(tmp_path, sources=settings["sources"]))]) == 2
    assert "config must be the name of a mapping config in config/" in capsys.readouterr().err
