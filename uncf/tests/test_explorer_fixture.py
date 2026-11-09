"""Checks the Explorer fixture writer."""
import sqlite3

from measures.save_results import CREATE_TABLE
from types import SimpleNamespace

from measures.models import Cohort, Group, GroupDimension, Measure, Status
from uncf.explorer_fixture import add_missing_measures, build_fixture, is_offered

INSERT = """
INSERT INTO success_measures (measure, cohort, group_dimensions, group_values, numerator, denominator,
    metric_rate, suppressed, status, n_excluded, note, data_loaded_at)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '', ?)
"""


def make_database(path) -> None:
    """A tiny results table with a shown row, a hidden row, a pair and an ethnicity row."""
    with sqlite3.connect(path) as connection:
        connection.execute(CREATE_TABLE)
        connection.executemany(INSERT, [
            ("retention", "2022-23", "all", "all", 1414.0, 2617.0, 0.5403, False, "ok", 0, "2026-11-08T22:00:00"),
            ("retention", "2022-23", "gender", "X", None, None, None, True, "suppressed", None, "2026-11-08T22:00:00"),
            ("retention", "2022-23", "enrollment_intensity x pell", "Full-time x Y", 302.0, 465.0, 0.6495, False, "ok", 0, "2026-11-08T22:30:00"),
            ("retention", "2022-23", "ethnicity", "H", 100.0, 200.0, 0.5, False, "ok", 0, "2026-11-08T22:00:00"),
        ])


def test_offered_groupings_leave_out_ethnicity() -> None:
    """Everyone, singles and pairs of offered dimensions are kept; anything with ethnicity is not."""
    assert is_offered("all")
    assert is_offered("pell")
    assert is_offered("enrollment_intensity x pell")
    assert not is_offered("ethnicity")
    assert not is_offered("ethnicity x race")


def test_fixture_keeps_hidden_rows_as_nulls(tmp_path) -> None:
    """A hidden group keeps nulls and its status, counts are whole numbers, and the newest load time wins."""
    database = tmp_path / "results.sqlite"
    make_database(database)
    fixture = build_fixture(database)
    cohort = fixture["rows"]["retention"]["2022-23"]
    assert cohort["all"] == [["all", 1414, 2617, "ok", 0]]
    assert cohort["gender"] == [["X", None, None, "suppressed", None]]
    assert cohort["enrollment_intensity x pell"] == [["Full-time x Y", 302, 465, "ok", 0]]
    assert "ethnicity" not in cohort
    assert fixture["loaded_at"] == "2026-11-08T22:30:00"


def test_missing_outcomes_are_calculated_and_saved_ones_kept(tmp_path) -> None:
    """Persistence isn't saved yet, so it's calculated; retention comes from the saved rows and isn't recalculated."""
    database = tmp_path / "results.sqlite"
    make_database(database)
    fixture = build_fixture(database)
    asked = []

    def fake_run(measure, cohorts, group_by):
        asked.append(measure)
        pell = Group.of((GroupDimension.PELL, "Y"))
        return [
            SimpleNamespace(group=Group(), cohort=Cohort.of("2022-23"), numerator=370.0, denominator=2617.0, status=Status.OK, n_excluded=0),
            SimpleNamespace(group=pell, cohort=Cohort.of("2022-23"), numerator=None, denominator=None, status=Status.SUPPRESSED, n_excluded=None),
        ]

    added = add_missing_measures(fixture, run=fake_run)
    assert Measure.RETENTION not in asked
    assert "persistence" in added and "retention" not in added
    persistence = fixture["rows"]["persistence"]["2022-23"]
    assert persistence["all"] == [["all", 370, 2617, "ok", 0]]
    assert persistence["pell"] == [["Y", None, None, "suppressed", None]]
