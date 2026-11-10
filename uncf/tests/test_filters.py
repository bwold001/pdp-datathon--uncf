"""Checks the cohort bar shared by every page and both APIs: which values they take, which students they pick, and the bar's counts."""
from __future__ import annotations

import pytest

from uncf.data import open_database
from uncf.filters import (
    CohortQuery,
    InvalidFilter,
    cohort_options,
    select_students,
    share,
    shown,
)
from uncf.tests.explorer_fixture import LOADED_AT, make_database, student


def test_query_takes_only_offered_values():
    """A cohort, filter name or value the Explorer doesn't offer is refused; equal queries are equal."""
    with pytest.raises(InvalidFilter, match="Cohort"):
        CohortQuery.of("2019-20")
    with pytest.raises(InvalidFilter, match="no filter"):
        CohortQuery.of("2023-24", housing="on_campus")
    with pytest.raises(InvalidFilter, match="pell has no value"):
        CohortQuery.of("2023-24", pell="Maybe")
    assert CohortQuery.of("2023-24", pell="Y", race="Asian") == CohortQuery.of("2023-24", race="Asian", pell="Y")
    assert CohortQuery.of("2023-24", pell=None).as_dict() == {}
    with pytest.raises(InvalidFilter, match="retention_type"):
        CohortQuery.of("2023-24", "ipeds")
    assert CohortQuery.of("2023-24").retention_type == "school"


def test_filters_match_raw_spellings_and_combine(tmp_path):
    """Values match ignoring case and spaces, unlisted ones count as UNKNOWN, and filters combine with AND."""
    database = make_database(
        tmp_path / "pdp.sqlite",
        [
            student("a", enrollment_intensity="Full-Time", age_band=">20 - 24", pell="Y"),
            student("b", enrollment_intensity="full-time", age_band="20 and younger", pell="U"),
            student("c", enrollment_intensity="Part-Time", pell="N", enrollment_type="Transfer-In"),
            student("d", cohort="2022-23"),
        ],
    )
    connection = open_database(database)
    picked = lambda **filters: sorted(select_students(connection, CohortQuery.of("2023-24", **filters)))
    assert picked() == ["a", "b", "c"]
    assert picked(enrollment_intensity="Full-time") == ["a", "b"]
    assert picked(age_band="> 20-24") == ["a"]
    assert picked(pell="UNKNOWN") == ["b"]
    assert picked(enrollment_intensity="Full-time", pell="Y") == ["a"]
    assert picked(enrollment_type="First-time") == ["a", "b"]
    assert picked(ethnicity="UNKNOWN") == ["a", "b", "c"]
    connection.close()


def test_small_counts_are_hidden_never_zero():
    """Counts of 1 to 9 are hidden; 0 and 10 or more are shown. Shares need both numbers."""
    assert [shown(n) for n in (0, 1, 9, 10)] == [0, None, None, 10]
    assert share(5, 20) == 0.25
    assert share(None, 20) is None
    assert share(5, 0) is None


def test_cohort_options_count_each_value(tmp_path):
    """The bar's counts: students per cohort year, and per filter value in the chosen cohort, small ones hidden."""
    students = [student(f"f{n}", pell="Y") for n in range(12)] + [student(f"s{n}", pell="N", cohort_term="SPRING") for n in range(3)]
    students += [student(f"old{n}", cohort="2022-23") for n in range(10)]
    database = make_database(tmp_path / "pdp.sqlite", students)
    options = cohort_options("2023-24", database)
    assert options["cohorts"] == {"2021-22": 0, "2022-23": 10, "2023-24": 15, "2024-25": 0}
    assert options["filters"]["pell"] == {"Y": 12, "N": None, "UNKNOWN": 0}
    assert options["filters"]["cohort_term"]["Fall"] == 12
    assert options["filters"]["cohort_term"]["Spring"] is None
    assert options["filters"]["enrollment_type"]["First-time"] == 15
    assert set(options["filters"]) == {"cohort_term", "enrollment_intensity", "enrollment_type", "pell", "gender", "race", "ethnicity", "age_band"}
    assert options["retention_types"] == ["school", "federal"]
    assert options["loaded_at"] == LOADED_AT
