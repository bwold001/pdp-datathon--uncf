"""Checks find_gaps on the shared measures: on their tiny fixture, and on a full load of the mock data."""
import csv
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from gap_finder.find_gaps import DEFAULT_DIMENSIONS, default_group_by, find_gaps, stub_gaps
from gap_finder.models import GapStatus
from gap_finder.save_results import main
from gap_finder.sources import count_rows
from gap_finder.stub import POOLED
from gap_finder.tests.test_compare import COMPUTED
from measures.models import Cohort, GroupBy, GroupDimension, Measure
from measures.run_measures import run_measure

REPO = Path(__file__).resolve().parents[2]
FIXTURE = REPO / "measures" / "tests" / "fixture.sql"
MODEL = REPO / "normalized-data-model"
RAW_COHORT = REPO / "data" / "raw" / "pdp_cohort_data.csv"
POOLED_YEARS = ["2021-22", "2022-23", "2023-24"]


@pytest.fixture
def database():
    """The shared measures' tiny database, in memory."""
    connection = sqlite3.connect(":memory:")
    connection.executescript(FIXTURE.read_text(encoding="utf-8"))
    return connection


def test_counts_come_from_run_measure(database):
    expected = run_measure(Measure.RETENTION, [Cohort.of("2022-23")], [GroupBy.of(GroupDimension.PELL)], database=database)
    rows = count_rows(["retention"], [["2022-23"]], [["pell"]], database)
    assert [(r.group_values, r.numerator, r.denominator, r.status) for r in rows] == [
        (tuple(p.value for p in e.group.parts), e.numerator, e.denominator, e.status.value) for e in expected
    ]
    assert rows[0].group_dimensions == () and rows[0].data_loaded_at != "unknown"


def test_each_gap_is_against_everyone_minus_the_group(database):
    everyone = run_measure(Measure.RETENTION, [Cohort.of("2022-23")], database=database)[0]
    for row in find_gaps(["retention"], [["2022-23"]], [["pell"], ["enrollment_intensity"]], database):
        if row.status == GapStatus.OK:
            assert row.numerator + row.comparison_numerator == everyone.numerator
            assert row.denominator + row.comparison_denominator == everyone.denominator


def test_several_measures_and_cohorts_in_one_call(database):
    rows = find_gaps(["retention", "gateway_math"], [["2022-23"], ["2022-23", "2023-24"]], [["pell"]], database)
    assert {(r.measure, r.cohort) for r in rows} == {
        ("retention", "2022-23"), ("retention", "2022-23 + 2023-24"),
        ("gateway_math", "2022-23"), ("gateway_math", "2022-23 + 2023-24"),
    }


def test_cohort_too_new_is_not_yet_observable(database):
    rows = find_gaps(["retention"], [["2024-25"]], [["pell"]], database)
    assert {r.status for r in rows} == {GapStatus.NOT_YET_OBSERVABLE}


def test_notes_say_what_was_compared(database):
    for row in find_gaps(["retention"], [["2022-23"]], [["pell"]], database):
        assert "everyone else in the same cohort (2022-23)" in row.note and "not its cause" in row.note


def test_default_groups_are_each_dimension_on_its_own():
    assert default_group_by() == [[name] for name in DEFAULT_DIMENSIONS]


def test_first_gen_is_left_out_of_the_default_but_can_be_asked_for(database):
    assert "first_gen" not in DEFAULT_DIMENSIONS
    # The fixture's first gen is blank for everyone, so the rows are UNKNOWN; any status will do here.
    rows = find_gaps(["retention"], [["2022-23"]], [["first_gen"]], database)
    assert rows and {r.group_dimensions for r in rows} == {("first_gen",)}


def test_a_breakdown_asked_for_twice_is_counted_once(database):
    once = count_rows(["retention"], [["2022-23"]], [["pell", "gender"]], database)
    twice = count_rows(["retention"], [["2022-23"]], [["pell", "gender"], ["gender", "pell"]], database)
    assert twice == once


def test_a_cohort_with_no_students_is_an_error(database):
    with pytest.raises(ValueError, match="no students in cohort 2031-32"):
        find_gaps(["retention"], [["2031-32"]], [["pell"]], database)


def test_gateway_counts_keep_the_measures_split(database):
    # Not required to take the course is out of scope, not excluded, and the reason is plain text.
    expected = run_measure(Measure.GATEWAY_MATH, [Cohort.of("2022-23")], database=database)[0]
    everyone = count_rows(["gateway_math"], [["2022-23"]], [["pell"]], database)[0]
    assert (everyone.n_excluded, everyone.n_out_of_scope) == (expected.n_excluded, expected.n_out_of_scope)
    assert everyone.exclusion_reason == (expected.exclusion_reason.value if expected.exclusion_reason else None)
    assert everyone.n_out_of_scope > 0


def test_unknown_measure_is_refused(database):
    with pytest.raises(ValueError):
        find_gaps(["graduation"], [["2022-23"]], [["pell"]], database)


def test_dfw_is_refused_because_it_is_not_a_yes_or_no(database):
    with pytest.raises(ValueError, match="yes-or-no"):
        find_gaps(["dfw_rate"], [["2022-23"]], [["pell"]], database)


def test_credit_completion_is_refused_because_it_is_an_average_of_ratios(database):
    with pytest.raises(ValueError, match="yes-or-no"):
        find_gaps(["credit_completion"], [["2022-23"]], [["pell"]], database)


@pytest.fixture(scope="module")
def full_load(tmp_path_factory) -> Path:
    """The full mock data, loaded into a temporary SQLite file with the data model's own pipeline settings."""
    folder = tmp_path_factory.mktemp("load")
    settings = yaml.safe_load((MODEL / "config" / "pipeline.yaml").read_text(encoding="utf-8"))
    settings["backend"] = "sqlite"
    settings["sqlite"]["path"] = str(folder / "pdp.sqlite")
    settings["tables"]["path"] = str(folder / "tables")
    settings["logs_dir"] = str(folder / "logs")
    settings["staging_dir"] = str(folder / "staging")
    config = folder / "pipeline.yaml"
    config.write_text(yaml.safe_dump(settings), encoding="utf-8")
    subprocess.run([sys.executable, "-m", "src.loader.load", "--config", str(config)], cwd=MODEL, check=True,
                   capture_output=True)
    return folder / "pdp.sqlite"


def raw_retention(rows, race=None) -> tuple[int, int]:
    """(retained, students) in the pooled cohorts, counted straight from the raw cohort file."""
    mine = [r for r in rows if r["Cohort"] in POOLED_YEARS and (race is None or r["Race"] == race)]
    return sum(r["Retention"] == "1" for r in mine), len(mine)


# One test, so the full load runs once per machine rather than once per test.
@pytest.mark.slow
def test_full_load(full_load, tmp_path, monkeypatch):
    # Retention by race reproduces the stub, every computed column: the stub was typed in from this run.
    computed = {r.group_values: r for r in find_gaps(["retention"], [POOLED_YEARS], [["race"]], full_load)}
    stub = {r.group_values: r for r in stub_gaps() if r.cohort == POOLED and r.group_dimensions == ("race",)}
    for values, row in stub.items():
        for name in COMPUTED:
            assert getattr(computed[values], name) == pytest.approx(getattr(row, name), rel=1e-12), (values, name)

    # #26's completion test 6: one gap, by hand from the raw file.
    with RAW_COHORT.open(newline="", encoding="utf-8") as f:
        raw = list(csv.DictReader(f))
    retained, students = raw_retention(raw)
    black_retained, black_students = raw_retention(raw, "Black or African American")
    black = computed[("Black or African American",)]
    assert (black.numerator, black.denominator) == (black_retained, black_students)
    assert (black.comparison_numerator, black.comparison_denominator) == (retained - black_retained, students - black_students)
    by_hand = black_retained / black_students - (retained - black_retained) / (students - black_students)
    assert black.gap_pts == round(by_hand * 100, 2)

    # #26's completion test 1: the script saves one table and one CSV, every row with its note.
    database, output = tmp_path / "results.sqlite", tmp_path / "equity_gaps.csv"
    saved = ["save_results", "--input", str(full_load), "--results", str(database), "--output", str(output)]
    monkeypatch.setattr(sys, "argv", saved)
    main()
    with output.open(newline="", encoding="utf-8") as f:
        written = list(csv.DictReader(f))
    assert {r["measure"] for r in written} == {"retention", "persistence", "gateway_math", "gateway_english"}
    assert all(r["note"] for r in written)
    assert not any("first_gen" in r["group_dimensions"] for r in written)
    assert table_count(database) == len(written)

    # A second run with other breakdowns replaces retention's rows whole, and leaves the other measures alone.
    monkeypatch.setattr(sys, "argv", saved + ["--measure", "retention", "--group-by", "pell"])
    main()
    others = sum(r["measure"] != "retention" for r in written)
    assert table_count(database, "measure = 'retention' AND group_dimensions != 'pell'") == 0
    pell_rows = find_gaps(["retention"], [POOLED_YEARS], [["pell"]], full_load)
    assert table_count(database) == others + len(pell_rows)


def table_count(database: Path, where: str = "1 = 1") -> int:
    """How many equity_gaps rows match."""
    with sqlite3.connect(database) as connection:
        return connection.execute(f"SELECT COUNT(*) FROM equity_gaps WHERE {where}").fetchone()[0]
