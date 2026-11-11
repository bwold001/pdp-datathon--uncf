"""Checks the equity_gaps table and the CSV: columns, blanks, booleans, two-way groups, privacy rules and replacing old rows."""
import csv
import sqlite3
import sys

import pytest

from gap_finder.find_gaps import stub_gaps
from gap_finder.models import COLUMNS, GapStatus
from gap_finder.save_results import main, save_gaps, table_columns, write_csv
from gap_finder.stub import NEWEST, POOLED


def read(path) -> list[dict[str, str]]:
    """The CSV's rows as dicts."""
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_header_is_the_contract(tmp_path):
    path = tmp_path / "gaps.csv"
    write_csv(stub_gaps(), path)
    assert path.read_text(encoding="utf-8").splitlines()[0] == ",".join(COLUMNS)


def test_one_line_per_row_with_unix_line_endings(tmp_path):
    path = tmp_path / "gaps.csv"
    rows = stub_gaps()
    write_csv(rows, path)
    content = path.read_bytes()
    assert b"\r\n" not in content
    assert len(content.decode("utf-8").splitlines()) == len(rows) + 1


def test_blank_is_an_empty_cell_and_booleans_are_words(tmp_path):
    path = tmp_path / "gaps.csv"
    write_csv(stub_gaps(), path)
    rows = read(path)
    hidden = next(r for r in rows if r["status"] == "not_yet_observable")
    assert hidden["numerator"] == "" and hidden["gap_pts"] == "" and hidden["suppressed"] == "true"
    black = next(r for r in rows if r["group_values"] == "Black or African American" and r["status"] == "ok")
    assert (black["likely_noise"], black["suppressed"], black["exclusion_reason"]) == ("false", "false", "")
    assert all("None" not in value for r in rows for value in r.values())


def test_two_way_group_is_joined_with_x(tmp_path):
    path = tmp_path / "gaps.csv"
    write_csv(stub_gaps(), path)
    two_way = next(r for r in read(path) if r["group_dimensions"] == "gender x race")
    assert two_way["group_values"] == "X x Two or More Races"


def test_table_columns_are_the_contract(tmp_path):
    database = tmp_path / "gaps.sqlite"
    save_gaps(stub_gaps(), database)
    with sqlite3.connect(database) as connection:
        names = [row[1] for row in connection.execute("PRAGMA table_info(equity_gaps)")]
    assert tuple(names) == COLUMNS


def test_table_holds_every_row_and_can_be_queried(tmp_path):
    database = tmp_path / "gaps.sqlite"
    save_gaps(stub_gaps(), database)
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT COUNT(*) FROM equity_gaps").fetchone()[0] == len(stub_gaps())
        top = connection.execute(
            "SELECT group_values, gap_pts, likely_noise FROM equity_gaps"
            " WHERE measure = 'retention' AND status = 'ok' ORDER BY rank_by_affected LIMIT 1"
        ).fetchone()
        hidden = connection.execute(
            "SELECT numerator, gap_pts, suppressed FROM equity_gaps WHERE group_values = 'X x Two or More Races'"
        ).fetchone()
    assert top == ("Black or African American", -8.53, 0)
    assert hidden == (None, None, 1)


def test_saving_again_replaces_the_measure_and_cohort_whole(tmp_path):
    database = tmp_path / "gaps.sqlite"
    rows = stub_gaps()
    save_gaps(rows, database)
    # A later run with fewer groups for the pooled cohorts: none of the first run's pooled rows stay behind.
    fewer = [r for r in rows if r.cohort == POOLED and r.rank_by_affected == 1]
    save_gaps(fewer, database)
    with sqlite3.connect(database) as connection:
        counts = dict(connection.execute("SELECT cohort, COUNT(*) FROM equity_gaps GROUP BY cohort"))
    assert counts == {POOLED: 1, NEWEST: 9}


def test_table_refuses_a_hidden_row_with_a_number(tmp_path):
    database = tmp_path / "gaps.sqlite"
    hidden = next(r for r in stub_gaps() if r.status == GapStatus.SUPPRESSED)
    save_gaps([hidden], database)
    with sqlite3.connect(database) as connection, pytest.raises(sqlite3.IntegrityError):
        connection.execute("UPDATE equity_gaps SET numerator = 0 WHERE status = 'suppressed'")


def test_table_refuses_a_shown_row_with_no_students(tmp_path):
    database = tmp_path / "gaps.sqlite"
    save_gaps(stub_gaps(), database)
    with sqlite3.connect(database) as connection, pytest.raises(sqlite3.IntegrityError):
        connection.execute("UPDATE equity_gaps SET denominator = 0 WHERE status = 'unknown_group'")


def test_table_refuses_a_comparison_with_no_students(tmp_path):
    database = tmp_path / "gaps.sqlite"
    save_gaps(stub_gaps(), database)
    with sqlite3.connect(database) as connection, pytest.raises(sqlite3.IntegrityError):
        connection.execute("UPDATE equity_gaps SET comparison_denominator = 0 WHERE status = 'ok'")


def test_old_table_with_other_columns_is_rebuilt(tmp_path):
    database = tmp_path / "gaps.sqlite"
    # A table saved before n_out_of_scope was added, with one old row in it.
    old_columns = [name for name in COLUMNS if name != "n_out_of_scope"]
    with sqlite3.connect(database) as connection:
        connection.execute(f"CREATE TABLE equity_gaps ({', '.join(old_columns)})")
        connection.execute("INSERT INTO equity_gaps (measure, cohort) VALUES ('retention', 'old')")
    save_gaps(stub_gaps(), database)
    with sqlite3.connect(database) as connection:
        assert table_columns(connection) == COLUMNS
        assert connection.execute("SELECT COUNT(*) FROM equity_gaps").fetchone()[0] == len(stub_gaps())


def test_stub_command_writes_both_files(tmp_path, monkeypatch):
    results, output = tmp_path / "gaps.sqlite", tmp_path / "gaps.csv"
    monkeypatch.setattr(sys, "argv", ["save_results", "--stub", "--results", str(results), "--output", str(output)])
    main()
    assert results.exists() and output.exists()
