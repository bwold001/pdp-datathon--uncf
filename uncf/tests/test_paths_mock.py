"""Checks the mock year-2 paths."""
import sqlite3

from uncf.paths_mock import build_paths, college_type, group_value, groupings


def make_database(path, students) -> None:
    """A tiny source database: (cohort, retention, persistence, carnegie, pell, gender) per student."""
    with sqlite3.connect(path) as connection:
        connection.execute(
            "CREATE TABLE cohort_membership (student_id, cohort, retention, persistence, c_most_recent_last_enroll_at_o,"
            " pell_status_first_year, enrollment_intensity_first_term, cohort_term, enrollment_type)"
        )
        connection.execute("CREATE TABLE student (student_id, student_age, gender, race)")
        for index, (cohort, retention, persistence, carnegie, pell, gender) in enumerate(students):
            connection.execute(
                "INSERT INTO cohort_membership VALUES (?, ?, ?, ?, ?, ?, 'Full-time', 'Fall', 'First-time')",
                (index, cohort, retention, persistence, carnegie, pell),
            )
            connection.execute("INSERT INTO student VALUES (?, '20 and younger', ?, 'White')", (index, gender))


def test_values_follow_the_measures_rules() -> None:
    """Case and spaces are ignored, and blank or unlisted values are UNKNOWN."""
    assert group_value("pell", "y") == "Y"
    assert group_value("enrollment_intensity", "full-time") == "Full-time"
    assert group_value("pell", "") == "UNKNOWN"
    assert group_value("pell", "maybe") == "UNKNOWN"
    assert college_type("Doctoral Universities") == "four_year"
    assert college_type("Associate's Colleges") == "two_year"
    assert college_type(None) == "not_on_record"


def test_groupings_are_everyone_singles_and_sorted_pairs() -> None:
    """Pairs are keyed in sorted order, as the saved results are."""
    keys = groupings(["pell", "gender"])
    assert keys == [(), ("pell",), ("gender",), ("gender", "pell")]


def test_paths_count_each_student_once_and_hide_small_groups(tmp_path) -> None:
    """Returned here wins over another college; groups under 10 are blank, never 0."""
    database = tmp_path / "pdp.sqlite"
    students = (
        [("2022-23", 1, 0, None, "Y", "F")] * 8
        + [("2022-23", 1, 1, "Doctoral Universities", "Y", "F")] * 2
        + [("2022-23", 0, 1, "Doctoral Universities", "N", "M")] * 6
        + [("2022-23", 0, 1, "Associate's Colleges", "N", "M")] * 4
        + [("2022-23", 0, 0, None, "N", "X")] * 3
    )
    make_database(database, students)
    paths = build_paths(database, ["pell", "gender"])["2022-23"]
    # 23 students: 10 back here (2 also elsewhere, counted once), 10 moved, 3 with no enrollment.
    assert paths["all"] == [["all", 23, 10, 10, 3, 6, 4, 0, "ok"]]
    pell = {row[0]: row for row in paths["pell"]}
    assert pell["Y"] == ["Y", 10, 10, 0, 0, None, None, None, "ok"]
    assert pell["N"] == ["N", 13, 0, 10, 3, 6, 4, 0, "ok"]
    gender = {row[0]: row for row in paths["gender"]}
    assert gender["X"] == ["X", None, None, None, None, None, None, None, "suppressed"]
    assert "gender x pell" in paths
