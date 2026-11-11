"""Checks the retention, persistence, gateway, DFW and credit completion calculations on a tiny database (fixture.sql).

Run from the repo root: python -m pytest measures/tests
"""
import sqlite3
from pathlib import Path

import pytest

from measures.calculations.dfw import (
    DFW_BELOW,
    ENROLLMENT_SQL,
    GRADE_REASONS,
    grade_outcomes,
    open_values,
)
from measures.calculations.dfw import NOTE as DFW_NOTE
from measures.calculations.retention import STUDENT_SQL
from measures.calculations.sql_counts import count_in_sql
from measures.models import (
    ALLOWED_VALUES,
    EVERYONE,
    Cohort,
    ExclusionReason,
    Group,
    GroupBy,
    GroupDimension,
    Measure,
    MeasureResult,
    Status,
)
from measures.run_measures import MEASURES, run_measure
from measures.save_results import CREATE_TABLE, save_results

FIXTURE = Path(__file__).parent / "fixture.sql"

C2022 = Cohort.of("2022-23")


@pytest.fixture
def database():
    """The tiny database, in memory."""
    connection = sqlite3.connect(":memory:")
    connection.executescript(FIXTURE.read_text(encoding="utf-8"))
    return connection


def find(results, label):
    """The one row whose group has this label."""
    rows = [r for r in results if r.group.label == label]
    assert len(rows) == 1, label
    return rows[0]


def test_retention_for_everyone(database):
    row = find(run_measure(Measure.RETENTION, [C2022], database=database), "everyone")
    assert (row.numerator, row.denominator, row.metric_rate) == (16, 20, 0.8)
    assert row.status == Status.OK
    assert (row.n_excluded, row.exclusion_reason) == (4, ExclusionReason.UNKNOWN_OUTCOME)
    assert row.exclusions == {ExclusionReason.UNKNOWN_OUTCOME: 4}
    assert row.n_out_of_scope == 0


def test_persistence_for_everyone(database):
    row = find(run_measure(Measure.PERSISTENCE, [C2022], database=database), "everyone")
    assert (row.numerator, row.denominator, row.metric_rate) == (5, 20, 0.25)


def test_small_group_preserves_counts_and_exclusions(database):
    # 12 students are pell = N, but only 8 have an answer, so the group is hidden.
    results = run_measure(Measure.RETENTION, [C2022], [GroupBy.of(GroupDimension.PELL)], database=database)
    assert find(results, "pell=Y").metric_rate == 1.0

    hidden = find(results, "pell=N")
    assert hidden.status == Status.OK and not hidden.suppressed
    assert (hidden.numerator, hidden.denominator, hidden.metric_rate, hidden.n_excluded) == (4, 8, .5, 4)


def test_group_values_match_ignoring_case_and_spaces(database):
    # The data says FALL and ">20 - 24". The groups say Fall and "> 20-24".
    by_term = run_measure(Measure.RETENTION, [C2022], [GroupBy.of(GroupDimension.COHORT_TERM)], database=database)
    assert (find(by_term, "cohort_term=Fall").numerator, find(by_term, "cohort_term=Fall").denominator) == (14, 14)

    by_age = run_measure(Measure.RETENTION, [C2022], [GroupBy.of(GroupDimension.AGE_BAND)], database=database)
    assert find(by_age, "age_band=> 20-24").denominator == 12


def test_two_way_group(database):
    results = run_measure(
        Measure.RETENTION, [C2022], [GroupBy.of(GroupDimension.PELL, GroupDimension.COHORT_TERM)], database=database
    )
    assert find(results, "cohort_term=Fall, pell=Y").denominator == 12
    # No pell = Y students started in spring, so that group is empty and hidden.
    assert find(results, "cohort_term=Spring, pell=Y").status == Status.SUPPRESSED


def test_pooled_cohort_counts_both_years_together(database):
    row = find(run_measure(Measure.RETENTION, [Cohort.of("2022-23", "2023-24")], database=database), "everyone")
    assert (row.numerator, row.denominator, row.metric_rate) == (22, 32, 0.6875)


def test_cohort_with_no_answers_is_not_yet_observable(database):
    row = find(run_measure(Measure.RETENTION, [Cohort.of("2024-25")], database=database), "everyone")
    assert row.status == Status.NOT_YET_OBSERVABLE and row.suppressed


@pytest.mark.parametrize("dimension", list(ALLOWED_VALUES))  # the dimensions with a fixed list of values
def test_groups_of_a_dimension_add_up_to_everyone(database, dimension):
    # Blank and unlisted values (pell 'U', a blank enrollment type, every first gen) count as UNKNOWN.
    cohort = Cohort.of("2022-23", "2023-24", "2024-25")
    groups = [EVERYONE] + [Group.of((dimension, value)) for value in ALLOWED_VALUES[dimension]]
    counts = count_in_sql(database, STUDENT_SQL, [cohort], groups)

    students = {group: counts[(cohort, group)].denominator + counts[(cohort, group)].n_excluded for group in groups}
    assert students[EVERYONE] == 48
    assert sum(n for group, n in students.items() if group != EVERYONE) == 48


def test_pooling_a_year_with_no_answers_is_not_yet_observable(database):
    # 2023-24 has answers, but 2024-25 doesn't, so the pool can't be read yet.
    row = find(run_measure(Measure.RETENTION, [Cohort.of("2023-24", "2024-25")], database=database), "everyone")
    assert row.status == Status.NOT_YET_OBSERVABLE


def test_no_cohorts_is_an_error(database):
    with pytest.raises(ValueError):
        run_measure(Measure.RETENTION, [], database=database)


def test_every_measure_has_a_calculation():
    assert set(MEASURES) == set(Measure)


def test_gateway_counts_every_required_student(database):
    # Students 17-20 were required but never took math. They count as not completed.
    row = find(run_measure(Measure.GATEWAY_MATH, [C2022], database=database), "everyone")
    assert (row.numerator, row.denominator, row.metric_rate) == (12, 20, 0.6)


def test_gateway_reports_unclassified_and_not_required_students_apart(database):
    # Student 23's requirement is unknown and 24 is required with no outcome: left out. 21 and 22 aren't required: out of scope.
    row = find(run_measure(Measure.GATEWAY_MATH, [C2022], database=database), "everyone")
    assert (row.n_excluded, row.exclusion_reason) == (2, ExclusionReason.UNKNOWN_REQUIREMENT_OR_OUTCOME)
    assert row.exclusions == {ExclusionReason.UNKNOWN_REQUIREMENT_OR_OUTCOME: 2}
    assert row.n_out_of_scope == 2


def test_gateway_english(database):
    row = find(run_measure(Measure.GATEWAY_ENGLISH, [C2022], database=database), "everyone")
    assert (row.numerator, row.denominator) == (10, 24)
    assert (row.n_excluded, row.exclusion_reason, row.n_out_of_scope) == (0, None, 0)


def test_small_gateway_group_preserves_population_counts(database):
    # 12 students are pell = N, but 2 aren't required and 2 can't be classified, so only 8 are counted and the group is hidden.
    results = run_measure(Measure.GATEWAY_MATH, [C2022], [GroupBy.of(GroupDimension.PELL)], database=database)
    assert (find(results, "pell=Y").numerator, find(results, "pell=Y").denominator) == (12, 12)

    hidden = find(results, "pell=N")
    assert hidden.status == Status.OK
    assert (hidden.numerator, hidden.denominator, hidden.n_excluded, hidden.n_out_of_scope) == (0, 8, 2, 2)


def test_gateway_pooled_cohort(database):
    # 12 of 20 in 2022-23 and 6 of 12 in 2023-24.
    row = find(run_measure(Measure.GATEWAY_MATH, [Cohort.of("2022-23", "2023-24")], database=database), "everyone")
    assert (row.numerator, row.denominator, row.metric_rate) == (18, 32, 0.5625)
    assert row.n_out_of_scope == 2


def test_gateway_cohort_with_no_answers_is_not_yet_observable(database):
    row = find(run_measure(Measure.GATEWAY_MATH, [Cohort.of("2024-25")], database=database), "everyone")
    assert row.status == Status.NOT_YET_OBSERVABLE


def test_dfw_counts_enrollments_with_a_final_grade(database):
    row = find(run_measure(Measure.DFW_RATE, [C2022], database=database), "everyone")
    # 27 enrollments with a class. Incomplete and audit are left out, and so is the row with no class.
    # Student 16's 1.7 is a C-, which passes, so 9 of the 25 are a DFW.
    assert (row.numerator, row.denominator, row.metric_rate) == (9, 25, 0.36)
    # Student 22's grade is incomplete and 23 audited. Each is left out for its own reason.
    assert row.n_excluded == 2
    assert row.exclusions == {ExclusionReason.INCOMPLETE: 1, ExclusionReason.AUDIT: 1}
    assert row.exclusion_reason == ExclusionReason.INCOMPLETE  # a tie goes to the reason listed first
    assert (row.n_out_of_scope, row.status) == (0, Status.OK)


def test_dfw_groups_split_the_enrollments(database):
    results = run_measure(Measure.DFW_RATE, [C2022], [GroupBy.of(GroupDimension.PELL)], database=database)
    assert (find(results, "pell=Y").numerator, find(results, "pell=Y").denominator) == (3, 15)
    assert (find(results, "pell=N").numerator, find(results, "pell=N").denominator) == (6, 10)


def test_dfw_cohort_with_no_final_grades_is_not_yet_observable(database):
    row = find(run_measure(Measure.DFW_RATE, [Cohort.of("2024-25")], database=database), "everyone")
    assert row.status == Status.NOT_YET_OBSERVABLE


def test_small_dfw_group_preserves_student_and_enrollment_counts(database):
    # 2023-24 has 12 graded enrollments, but they come from only 3 students, so the group is hidden.
    row = find(run_measure(Measure.DFW_RATE, [Cohort.of("2023-24")], database=database), "everyone")
    assert row.status == Status.OK
    assert (row.numerator, row.denominator, row.n_students) == (0, 12, 3)


def test_dfw_pooled_cohort(database):
    # 9 of 25 in 2022-23 and 0 of 12 in 2023-24.
    row = find(run_measure(Measure.DFW_RATE, [Cohort.of("2022-23", "2023-24")], database=database), "everyone")
    assert (row.numerator, row.denominator, row.metric_rate) == (9, 37, 0.2432)


def test_dfw_every_grade_that_is_left_out_has_a_reason():
    classified = grade_outcomes()
    # A grade is either classified or explained, never both.
    assert not set(GRADE_REASONS) & set(classified)
    assert GRADE_REASONS["I"] == ExclusionReason.INCOMPLETE and GRADE_REASONS["A"] == ExclusionReason.AUDIT
    assert GRADE_REASONS["OTH"] == GRADE_REASONS["O"] == ExclusionReason.OTHER_GRADE


def test_exclusions_must_add_up_and_a_hidden_row_has_none():
    row = shown_row(n_excluded=4, exclusions={ExclusionReason.INCOMPLETE: 3, ExclusionReason.AUDIT: 1})
    MeasureResult(**row)
    with pytest.raises(ValueError):
        MeasureResult(**shown_row(exclusions={}))  # 4 left out, but no reasons given
    with pytest.raises(ValueError):
        MeasureResult(**shown_row(n_excluded=4, exclusions={ExclusionReason.INCOMPLETE: 3}))
    with pytest.raises(ValueError):
        MeasureResult(**shown_row(n_excluded=4, exclusions={ExclusionReason.INCOMPLETE: 4, ExclusionReason.AUDIT: 0}))
    with pytest.raises(ValueError):
        MeasureResult(**shown_row(
            numerator=None, denominator=None, metric_rate=None, status=Status.SUPPRESSED,
            n_excluded=None, n_out_of_scope=None, exclusion_reason=None, exclusions={ExclusionReason.AUDIT: 1},
        ))


def test_saving_into_a_file_from_before_exclusions_existed(database, tmp_path):
    target = tmp_path / "old.sqlite"
    older_table = CREATE_TABLE.replace("    exclusions       TEXT,\n", "")
    assert "exclusions" not in older_table
    old = sqlite3.connect(target)
    old.execute(older_table)
    old.commit()
    old.close()

    save_results(run_measure(Measure.DFW_RATE, [C2022], database=database), "test load", target)
    saved = sqlite3.connect(target).execute("SELECT exclusions FROM success_measures WHERE group_values = 'all'").fetchone()
    assert saved == ('{"audit": 1, "incomplete": 1}',)


def test_exclusions_are_saved_as_text(database, tmp_path):
    results = run_measure(Measure.DFW_RATE, [C2022], database=database)
    target = tmp_path / "results.sqlite"
    save_results(results, "test load", target)
    saved = sqlite3.connect(target).execute("SELECT exclusions FROM success_measures WHERE group_values = 'all'").fetchone()
    assert saved == ('{"audit": 1, "incomplete": 1}',)


def test_dfw_by_course_finds_the_courses_in_the_data(database):
    results = run_measure(Measure.DFW_RATE, [C2022], [GroupBy.of(GroupDimension.COURSE)], database=database)
    # Only the courses with an enrollment in 2022-23 get a row. The courses come from the data, not a list.
    assert sorted(r.group.label for r in results) == ["course=ENGL 1302", "course=MATH 1314", "everyone"]

    english = find(results, "course=ENGL 1302")
    assert (english.numerator, english.denominator, english.metric_rate) == (6, 22, 0.2727)
    # Three students took MATH 1314, so it is hidden whatever its numbers are.
    assert find(results, "course=MATH 1314").status == Status.OK


def test_dfw_by_course_and_pell(database):
    results = run_measure(
        Measure.DFW_RATE, [C2022], [GroupBy.of(GroupDimension.COURSE, GroupDimension.PELL)], database=database
    )
    assert (find(results, "course=ENGL 1302, pell=Y").numerator, find(results, "course=ENGL 1302, pell=Y").denominator) == (0, 12)
    assert (find(results, "course=ENGL 1302, pell=N").numerator, find(results, "course=ENGL 1302, pell=N").denominator) == (6, 10)


def test_only_dfw_can_be_grouped_by_course(database):
    with pytest.raises(ValueError):
        run_measure(Measure.RETENTION, [C2022], [GroupBy.of(GroupDimension.COURSE)], database=database)


def test_a_course_can_be_any_text_but_not_blank():
    Group.of((GroupDimension.COURSE, "ENGL 1302"))
    with pytest.raises(ValueError):
        Group.of((GroupDimension.COURSE, "  "))


def add_student(database, student_id, cohort):
    """A student in a cohort of their own, so their enrollments can be counted apart from the fixture's."""
    database.execute("INSERT INTO student VALUES (?, 'Older than 24', 'White', 'N', 'F', NULL)", (student_id,))
    database.execute(
        "INSERT INTO cohort_membership (student_id, cohort, cohort_term, enrollment_type, enrollment_intensity_first_term,"
        " pell_status_first_year) VALUES (?, ?, 'FALL', 'First-time', 'Full-time', 'Y')",
        (student_id, cohort),
    )


def test_dfw_grades_match_ignoring_case_spaces_and_decimals(database):
    add_student(database, "t1", "2025-26")
    for grade in (" w ", "1.67", "4.00", "f", "3.67", "ABC"):
        database.execute("INSERT INTO course_enrollment VALUES ('t1', '2025-26', 1, ?, 1, 'F')", (grade,))
    cohort = Cohort.of("2025-26")

    counts = count_in_sql(database, ENROLLMENT_SQL, [cohort], [EVERYONE])[(cohort, EVERYONE)]
    # A withdrawal, 1.67 and an F are D, F or W. 4.00 and 3.67 passed. ABC isn't a grade we know.
    assert (counts.numerator, counts.denominator, counts.n_excluded) == (3, 5, 1)
    assert counts.exclusions == {ExclusionReason.UNLISTED_GRADE: 1}


def test_dfw_courses_that_differ_only_in_case_are_one_course(database):
    add_student(database, "t1", "2025-26")
    database.execute("INSERT INTO course VALUES (5, 'ENG', '101')")
    database.execute("INSERT INTO course VALUES (6, 'eng', '101')")
    database.execute("INSERT INTO course_enrollment VALUES ('t1', '2025-26', 5, 'P', 1, 'F')")
    database.execute("INSERT INTO course_enrollment VALUES ('t1', '2025-26', 6, 'F', 1, 'F')")
    cohort = Cohort.of("2025-26")

    assert open_values(database, GroupDimension.COURSE, [cohort]) == ["ENG 101"]
    group = Group.of((GroupDimension.COURSE, "ENG 101"))
    counts = count_in_sql(database, ENROLLMENT_SQL, [cohort], [group])[(cohort, group)]
    assert (counts.numerator, counts.denominator) == (1, 2)


def test_dfw_note_follows_the_cutoff():
    assert f"under {DFW_BELOW:.1f}" in DFW_NOTE


def test_dfw_grade_rules():
    outcomes = grade_outcomes()
    # Below 1.7 (a D+ or lower) is a DFW, written either way. A C- (1.7 to under 2.0) passes, as do P and higher numbers.
    assert outcomes["1.69"] and outcomes["1.3"] and outcomes["1"] and outcomes["1.0"] and outcomes["0"]
    assert not outcomes["1.7"] and not outcomes["1.9"] and not outcomes["2.0"] and not outcomes["4.0"] and not outcomes["P"]
    assert outcomes["F"] and outcomes["W"]
    # Grade points to two decimals, as an institution's own file may write them.
    assert outcomes["1.67"] and not outcomes["3.67"] and not outcomes["4.00"] and outcomes["0.07"]
    # Incomplete, audit, missing and other grades, and anything unknown, have no outcome and are left out.
    for left_out in ("I", "A", "M", "O", "OTH", "UNKNOWN", "UW"):
        assert left_out not in outcomes


def test_credit_completion_averages_each_students_ratio(database):
    row = find(run_measure(Measure.CREDIT_COMPLETION, [C2022], database=database), "everyone")
    # 10 students at 1.0, 6 at 0 and 2 at 0.5 add up to 11 over 18 students. Pooling credits would give 162 / 192 = 0.84.
    assert (row.numerator, row.denominator, row.metric_rate) == (11, 18, 0.6111)
    assert row.status == Status.OK


def test_credit_completion_reports_left_out_students_by_reason(database):
    row = find(run_measure(Measure.CREDIT_COMPLETION, [C2022], database=database), "everyone")
    # 17-18 have no credits recorded, 19 attempted none, 20's full- or part-time status is unknown.
    assert row.exclusions == {
        ExclusionReason.UNKNOWN_OUTCOME: 2,
        ExclusionReason.NO_CREDITS_ATTEMPTED: 1,
        ExclusionReason.UNKNOWN_ATTENDANCE_TYPE: 1,
    }
    assert (row.n_excluded, row.exclusion_reason) == (4, ExclusionReason.UNKNOWN_OUTCOME)
    # 21-22 are re-admits, so the measure doesn't apply to them.
    assert row.n_out_of_scope == 2


def test_credit_completion_groups(database):
    results = run_measure(Measure.CREDIT_COMPLETION, [C2022], [GroupBy.of(GroupDimension.PELL)], database=database)
    assert (find(results, "pell=Y").numerator, find(results, "pell=Y").denominator) == (10, 12)
    # pell = N has only 6 students counted, so it is hidden.
    assert find(results, "pell=N").status == Status.OK


def test_credit_completion_by_enrollment_type(database):
    results = run_measure(Measure.CREDIT_COMPLETION, [C2022], [GroupBy.of(GroupDimension.ENROLLMENT_TYPE)], database=database)
    assert (find(results, "enrollment_type=First-time").numerator, find(results, "enrollment_type=First-time").denominator) == (10, 16)
    assert find(results, "enrollment_type=Transfer-in").status == Status.OK  # 2 students
    assert find(results, "enrollment_type=Re-admit").status == Status.SUPPRESSED  # nobody is counted


def test_credit_completion_pooled_cohort(database):
    # 11 / 18 in 2022-23 and 6 / 12 in 2023-24.
    row = find(run_measure(Measure.CREDIT_COMPLETION, [Cohort.of("2022-23", "2023-24")], database=database), "everyone")
    assert (row.numerator, row.denominator, row.metric_rate) == (17, 30, 0.5667)


def test_credit_completion_cohort_with_no_credits_is_not_yet_observable(database):
    row = find(run_measure(Measure.CREDIT_COMPLETION, [Cohort.of("2024-25")], database=database), "everyone")
    assert row.status == Status.NOT_YET_OBSERVABLE


def test_credit_completion_ratio_is_kept_at_one(database):
    # Student 1 earned 20 of 15 attempted credits. The ratio stays at 1, so the numerator can't pass the denominator.
    database.execute("UPDATE cohort_membership SET number_of_credits_earned_yr_1 = 20 WHERE student_id = 's01'")
    row = find(run_measure(Measure.CREDIT_COMPLETION, [C2022], database=database), "everyone")
    assert (row.numerator, row.denominator) == (11, 18)


def test_credit_completion_leaves_out_blank_and_unknown_enrollment_types(database):
    # Only first-time and transfer-in are counted. A blank or UNKNOWN type can't be told apart, so it is left out with its own reason.
    database.execute("UPDATE cohort_membership SET enrollment_type = NULL WHERE student_id = 's02'")
    database.execute("UPDATE cohort_membership SET enrollment_type = 'UNKNOWN' WHERE student_id = 's03'")
    row = find(run_measure(Measure.CREDIT_COMPLETION, [C2022], database=database), "everyone")
    assert (row.numerator, row.denominator) == (9, 16)
    assert row.exclusions[ExclusionReason.UNKNOWN_ENROLLMENT_TYPE] == 2
    assert row.n_excluded == 6 and row.n_out_of_scope == 2


def test_credit_completion_needs_at_least_one_credit_attempted(database):
    # Half a credit is below the minimum of 1, so student 5 is left out, not counted.
    database.execute(
        "UPDATE cohort_membership SET number_of_credits_attempted_yr_1 = 0.5, number_of_credits_earned_yr_1 = 0.5 WHERE student_id = 's05'"
    )
    row = find(run_measure(Measure.CREDIT_COMPLETION, [C2022], database=database), "everyone")
    assert (row.numerator, row.denominator) == (10, 17)
    assert row.exclusions[ExclusionReason.NO_CREDITS_ATTEMPTED] == 2


def test_results_are_saved_and_replaced(database, tmp_path):
    results = run_measure(Measure.RETENTION, [C2022], [GroupBy.of(GroupDimension.PELL)], database=database)
    target = tmp_path / "results.sqlite"

    save_results(results, "test load", target)
    save_results(results, "test load", target)  # saving again replaces rows, it doesn't add them

    saved = sqlite3.connect(target)
    assert saved.execute("SELECT COUNT(*) FROM success_measures").fetchone() == (len(results),)
    row = saved.execute(
        "SELECT numerator, denominator, status FROM success_measures WHERE group_values = 'N'"
    ).fetchone()
    assert row == (4, 8, "ok")


def test_a_save_is_always_the_latest_run(database, tmp_path):
    by_pell = run_measure(Measure.RETENTION, [C2022], [GroupBy.of(GroupDimension.PELL)], database=database)
    plain = run_measure(Measure.RETENTION, [C2022], database=database)
    persistence = run_measure(Measure.PERSISTENCE, [C2022], database=database)
    target = tmp_path / "results.sqlite"
    saved = sqlite3.connect(target)

    def count_rows(measure):
        return saved.execute("SELECT COUNT(*) FROM success_measures WHERE measure = ?", (measure,)).fetchone()[0]

    save_results(by_pell, "load 1", target)
    save_results(plain, "load 2", target)  # the by-Pell rows must not stay behind
    assert count_rows("retention") == len(plain)
    assert saved.execute("SELECT DISTINCT data_loaded_at FROM success_measures").fetchall() == [("load 2",)]

    # Saving another measure leaves retention alone.
    save_results(persistence, "load 2", target)
    assert count_rows("retention") == len(plain) and count_rows("persistence") == len(persistence)


def shown_row(**changes):
    """A valid shown row. Pass changes to break one rule."""
    row = dict(
        measure=Measure.RETENTION, cohort=C2022, group=EVERYONE, numerator=16, denominator=20,
        metric_rate=0.8, status=Status.OK, n_excluded=4, n_out_of_scope=0,
        exclusion_reason=ExclusionReason.UNKNOWN_OUTCOME, note="n", exclusions={ExclusionReason.UNKNOWN_OUTCOME: 4},
    )
    return {**row, **changes}


def test_a_shown_row_is_checked_against_its_own_numbers():
    MeasureResult(**shown_row())
    with pytest.raises(ValueError):
        MeasureResult(**shown_row(numerator=21))  # more than the denominator
    with pytest.raises(ValueError):
        MeasureResult(**shown_row(metric_rate=0.75))  # not numerator / denominator


def test_suppressed_follows_the_status():
    hidden = dict(
        numerator=None, denominator=None, metric_rate=None, n_excluded=None, n_out_of_scope=None,
        exclusion_reason=None, exclusions={},
    )
    assert not MeasureResult(**shown_row()).suppressed
    assert MeasureResult(**shown_row(**hidden, status=Status.SUPPRESSED)).suppressed
    assert MeasureResult(**shown_row(**hidden, status=Status.NOT_YET_OBSERVABLE)).suppressed
