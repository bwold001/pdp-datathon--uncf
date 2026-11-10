"""Small normalized database with independently countable synthetic outcomes."""
import sqlite3

from analytics.coverage import Coverage


def build_database(path):
    """Create three students, duplicate courses and a student in two entry cohorts."""
    with sqlite3.connect(path) as db:
        db.executescript('''
        CREATE TABLE student (student_id TEXT, ethnicity TEXT, race TEXT, gender TEXT,
                              first_gen TEXT, student_age TEXT);
        CREATE TABLE cohort_membership (
            student_id TEXT, cohort TEXT, retention INTEGER, program_of_study_term_1 TEXT,
            credential_type_sought_year_1 TEXT, first_year_to_bachelors_at_coh INTEGER,
            years_to_ba_at_cohort_inst INTEGER, time_to_credential REAL,
            cohort_term TEXT, enrollment_type TEXT, enrollment_intensity_first_term TEXT,
            pell_status_first_year TEXT);
        CREATE TABLE term (term_id INTEGER, academic_year TEXT, academic_term TEXT, sort_order INTEGER);
        CREATE TABLE course_enrollment (student_id TEXT, cohort TEXT, course_id INTEGER,
                                       term_id INTEGER, term_program_of_study TEXT);
        CREATE TABLE data_provider (provider_id INTEGER, loaded_at TEXT, source_file TEXT, file_sha256 TEXT);
        INSERT INTO data_provider VALUES (1, '2026-06-30T12:00:00', 'hand-counted fixture', 'fixture');
        INSERT INTO student VALUES ('a', 'Hispanic', 'Asian', 'F', NULL, '20');
        INSERT INTO student VALUES ('b', 'UNKNOWN', 'Asian', 'F', NULL, '20');
        INSERT INTO student VALUES ('c', 'Not Hispanic', 'Asian', 'F', NULL, '20');
        INSERT INTO cohort_membership VALUES ('a', '2022-23', 1, '400501', 'B', 3, 3, 1.2, 'FALL', 'First-time', 'Full-Time', 'Y');
        INSERT INTO cohort_membership VALUES ('b', '2022-23', 0, '400501', 'B', 0, 0, 0, 'FALL', 'First-time', 'Full-Time', 'N');
        INSERT INTO cohort_membership VALUES ('c', '2022-23', NULL, NULL, 'B', NULL, NULL, NULL, 'FALL', 'First-time', 'Full-Time', 'N');
        INSERT INTO cohort_membership VALUES ('a', '2021-22', 0, '520201', 'A', 0, 0, 1.2, 'FALL', 'Transfer-In', 'Full-Time', 'Y');
        INSERT INTO term VALUES (1, '2022-23', 'FALL', 1), (2, '2023-24', 'SPRING', 6), (99, 'UNKNOWN', 'UNKNOWN', 99);
        INSERT INTO course_enrollment VALUES ('a', '2022-23', 1, 1, '400501'), ('a', '2022-23', 2, 1, '400501'),
        ('a', '2022-23', 3, 2, '520201'), ('b', '2022-23', 4, 2, '400501'), ('c', '2022-23', NULL, 2, '400501');
        ''')
    return path


def fixture_coverage(threshold=1):
    """Declared completeness for this test fixture only, never for the shared extract."""
    return Coverage(complete_academic_years=['2022-23', '2023-24'],
                    cohort_followup_years={'2022-23': 4}, cutoff='2026-06-30',
                    provenance='Hand-counted synthetic fixture', suppression_threshold=threshold)
