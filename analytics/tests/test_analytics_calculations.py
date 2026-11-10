"""Hand-counted calculations, before suppression or model interpretation."""
from analytics.graduation import calculate as graduation
from analytics.enrollment import calculate as enrollment
from analytics.retention import calculate as retention
from analytics.coverage import Coverage

COVERAGE = Coverage(complete_academic_years=['2022-23', '2023-24'],
                    cohort_followup_years={'2022-23': 4}, cutoff='2026-06-30',
                    provenance='Hand-counted synthetic fixture', suppression_threshold=1)


def test_retention_keeps_known_outcomes_and_unknown_program():
    """Two known outcomes give one retained student, not one of three."""
    rows = [{'program_of_study_term_1': '400501', 'retention': 1},
            {'program_of_study_term_1': '400501', 'retention': 0},
            {'program_of_study_term_1': None, 'retention': None}]
    result = retention(rows, provisional=False)
    assert (result[0].numerator, result[0].denominator, result[0].rate) == (1, 2, .5)
    assert result[0].exclusions == {'unknown_outcome': 1}
    assert result[-1].group == {'entry_program': 'UNKNOWN'}


def test_enrollment_deduplicates_program_year_not_course_rows():
    """A changing major counts in each program and ethnicity never becomes race."""
    rows = [dict(student_id='a', academic_year='2023-24', term_program_of_study='400501',
                 ethnicity='UNKNOWN', course_id=1),
            dict(student_id='a', academic_year='2023-24', term_program_of_study='400501',
                 ethnicity='UNKNOWN', course_id=2),
            dict(student_id='a', academic_year='2023-24', term_program_of_study='520201',
                 ethnicity='UNKNOWN', course_id=3),
            dict(student_id='b', academic_year='2023-24', term_program_of_study='400501',
                 ethnicity='Hispanic', course_id=None)]
    result = enrollment(rows, COVERAGE.latest_two_years())
    assert [(r.count, r.group['ethnicity']) for r in result] == [(1, 'UNKNOWN'), (1, 'UNKNOWN')]


def test_graduation_perspectives_are_distinct_and_horizons_independent():
    """An entrant switching out counts only in any-program completion."""
    base = dict(credential_type_sought_year_1='B', first_year_to_bachelors_at_coh=3,
                years_to_ba_at_cohort_inst=3)
    rows = [dict(base, program_of_study_term_1='400501', graduation_program='520201'),
            dict(base, program_of_study_term_1='400501', graduation_program='400501'),
            dict(base, program_of_study_term_1='520201', graduation_program='400501')]
    result = graduation(rows, '2022-23', 'B', {'400501'}, COVERAGE)
    four = [r for r in result if r.horizon == 'four_year']
    assert [(r.numerator, r.denominator) for r in four] == [(2, 2), (1, 2), (1, 2), (1, 2), (0, 2)]
    assert all(r.status == 'not_yet_observable' for r in result if r.horizon == 'six_year')
    assert all(r.status == 'ok' for r in result if r.horizon == 'to_date')


def test_unknown_graduation_program_is_not_a_different_major():
    """Ambiguous major excludes a completion from program-specific denominators."""
    rows = [dict(credential_type_sought_year_1='B', program_of_study_term_1='400501',
                 first_year_to_bachelors_at_coh=3, years_to_ba_at_cohort_inst=3,
                 graduation_program=None)]
    result = graduation(rows, '2022-23', 'B', {'400501'}, COVERAGE)
    assert result[0].numerator == 1
    assert result[1].status == 'unknown'
    assert result[1].note


def test_retention_counts_match_shared_measure(tmp_path):
    """The program adapter preserves the upstream known-outcome denominator."""
    import sqlite3
    from measures.calculations.retention import count
    from measures.models import Cohort, Group
    from analytics.tests.analytics_fixtures import build_database

    path = build_database(tmp_path / 'fixture.sqlite')
    with sqlite3.connect(path) as db:
        cohort, group = Cohort.of('2022-23'), Group()
        counts = count(db, [cohort], [group])[(cohort, group)]
        db.row_factory = sqlite3.Row
        members = [dict(r) for r in db.execute("SELECT * FROM cohort_membership WHERE cohort='2022-23'")]
    ours = retention(members, False)[0]
    assert (ours.numerator, ours.denominator) == (counts.numerator, counts.denominator) == (1, 2)
    assert ours.exclusions['unknown_outcome'] == counts.n_excluded == 1


def test_earlier_associate_duration_cannot_identify_bachelor_program():
    """Rounded earliest-credential duration is not bachelor award-semester evidence."""
    rows = [dict(credential_type_sought_year_1='B', program_of_study_term_1='400501',
                 first_year_to_bachelors_at_coh=3, years_to_ba_at_cohort_inst=3,
                 first_year_to_a_or_c_at_cohort=1, time_to_credential=.8, graduation_program=None)]
    result = graduation(rows, '2022-23', 'B', {'400501'}, COVERAGE)
    assert result[0].numerator == 1
    assert result[1].status == 'unknown'
    assert result[2].status == 'unknown'
