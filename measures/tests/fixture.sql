-- Plain SQL that runs on SQLite and PostgreSQL.
-- A tiny database with only the tables and columns the measures read. 48 made-up students.
--
--   2022-23  students 1-24   retention: 1-16 yes, 17-20 no, 21-24 blank      persistence: 1, 17-20 yes
--   2023-24  students 25-36  retention: 25-30 yes, 31-36 no
--   2024-25  students 37-48  no answers yet
--
-- Fall starters are 1-14 and 25-48, spring starters 15-24. Pell is yes for 1-12, no for 13-24.
-- Age is "> 20-24" (written the way the mock file spells it) for 1-12.
--
-- Gateway completed flag (C completed, D did not complete). Students not required have NA or a blank.
--   Math 2022-23:    1-12 C   13-20 D (17-20 never took it)   21-22 not required   23 requirement unknown
--                    24 required but blank     12 of 20, 2 left out (23-24), 2 out of scope (21-22).
--   Math 2023-24:    25-30 C   31-36 D     6 of 12.
--   English 2022-23: 1-10 C   11-24 D     10 of 24.
--   English 2023-24: 25-36 C.
--   2024-25: blank for both, so nothing is observable yet.
-- Students 45-48 have a pell value that isn't on the list ('U') and a blank enrollment type, and
-- first gen is blank for everyone, so each of those lands in an UNKNOWN group.
--
-- Year 1 credits attempted / earned, for credit completion. Students 21-22 are Re-admit (out of scope),
-- 23-24 Transfer-In, the rest First-time. 2024-25 has no credits yet.
--   2022-23: 1-10 15/15 (ratio 1)   11-16 3/0 (ratio 0)   17-18 blank   19 0/0   20 12/12 but full- or part-time unknown
--            21-22 12/12 re-admit   23-24 12/6 (ratio 0.5)
--     18 students counted, ratios add up to 11, so the rate is 11 / 18 = 0.6111. Pooled credits would give 162 / 192 = 0.84.
--   2023-24: 25-36 10/5 (ratio 0.5)     6 of 12.
--
-- Course enrollments, for DFW (grades are text, as in the data):
--   2022-23 students 1-24 have one class each. Grades: 1-8 "4", 9-10 "3.7", 11 "2.0", 12 "2", 13 "3",
--     14 "2.3", 15 "1.0", 16 "1.7", 17 "1", 18 "0.3", 19-20 "F", 21 "W", 22 "I", 23 "A" (audit), 24 "P".
--   Students 1-3 also have a second class graded "W", and student 1 has a row with no class at all.
--   Courses: 1 ENGL 1302 (nearly every class), 2 MATH 1314 (the second classes of students 1-3), 3 BIOL 1101 and
--     4 HIST 1301 (only the 2023-24 classes).
--   2023-24 students 25-27 have four classes each, graded "P": 12 enrollments from only 3 students.
--   2024-25 students 37-48 have one class each, graded "I", so nobody has a final grade yet.

CREATE TABLE student (
    student_id TEXT, student_age TEXT, race TEXT, ethnicity TEXT, gender TEXT, first_gen TEXT
);
CREATE TABLE cohort_membership (
    student_id TEXT, cohort TEXT, cohort_term TEXT, enrollment_type TEXT,
    enrollment_intensity_first_term TEXT, pell_status_first_year TEXT,
    retention BOOLEAN, persistence BOOLEAN,
    completed_gateway_math_year1 TEXT, completed_gateway_english_year1 TEXT,
    gateway_math_status TEXT, gateway_english_status TEXT,
    number_of_credits_attempted_yr_1 REAL, number_of_credits_earned_yr_1 REAL
);
CREATE TABLE course (course_id INTEGER, course_prefix TEXT, course_number TEXT);
CREATE TABLE course_enrollment (student_id TEXT, cohort TEXT, course_id INTEGER, grade TEXT);
CREATE TABLE data_provider (provider_id INTEGER, source_file TEXT, file_sha256 TEXT, loaded_at TEXT);

INSERT INTO data_provider VALUES (1, 'fixture.sql', 'not-a-real-hash', '2026-01-01T00:00:00');

-- n holds the numbers 1 to 48, one per student.
CREATE TEMP TABLE n AS
WITH RECURSIVE numbers(i) AS (SELECT 1 UNION ALL SELECT i + 1 FROM numbers WHERE i < 48)
SELECT i FROM numbers;

INSERT INTO student
SELECT CASE WHEN i < 10 THEN 's0' || i ELSE 's' || i END,
       CASE WHEN i <= 12 THEN '>20 - 24' ELSE 'Older than 24' END,
       'White', 'N', 'F', NULL
FROM n;

INSERT INTO cohort_membership
SELECT CASE WHEN i < 10 THEN 's0' || i ELSE 's' || i END,
       CASE WHEN i <= 24 THEN '2022-23' WHEN i <= 36 THEN '2023-24' ELSE '2024-25' END,
       CASE WHEN i BETWEEN 15 AND 24 THEN 'SPRING' ELSE 'FALL' END,
       CASE
           WHEN i >= 45 THEN NULL
           WHEN i BETWEEN 21 AND 22 THEN 'Re-admit'
           WHEN i BETWEEN 23 AND 24 THEN 'Transfer-In'
           ELSE 'First-time'
       END,
       CASE WHEN i = 20 THEN NULL ELSE 'Full-time' END,
       CASE WHEN i BETWEEN 45 AND 48 THEN 'U' WHEN i BETWEEN 13 AND 24 THEN 'N' ELSE 'Y' END,
       CASE
           WHEN i <= 16 THEN TRUE
           WHEN i <= 20 THEN FALSE
           WHEN i <= 24 THEN NULL
           WHEN i <= 30 THEN TRUE
           WHEN i <= 36 THEN FALSE
           ELSE NULL
       END,
       CASE
           WHEN i IN (1, 17, 18, 19, 20) THEN TRUE
           WHEN i <= 36 AND (i < 21 OR i > 24) THEN FALSE
           ELSE NULL
       END,
       CASE
           WHEN i <= 12 THEN 'C'
           WHEN i <= 20 THEN 'D'
           WHEN i <= 22 THEN 'NA'
           WHEN i <= 24 THEN NULL
           WHEN i <= 30 THEN 'C'
           WHEN i <= 36 THEN 'D'
           ELSE NULL
       END,
       CASE
           WHEN i <= 10 THEN 'C'
           WHEN i <= 24 THEN 'D'
           WHEN i <= 36 THEN 'C'
           ELSE NULL
       END,
       CASE WHEN i BETWEEN 21 AND 22 THEN 'N' WHEN i = 23 THEN 'UNKNOWN' ELSE 'R' END,
       'R',
       CASE
           WHEN i <= 10 THEN 15
           WHEN i <= 16 THEN 3
           WHEN i <= 18 THEN NULL
           WHEN i = 19 THEN 0
           WHEN i <= 24 THEN 12
           WHEN i <= 36 THEN 10
           ELSE NULL
       END,
       CASE
           WHEN i <= 10 THEN 15
           WHEN i <= 16 THEN 0
           WHEN i <= 18 THEN NULL
           WHEN i = 19 THEN 0
           WHEN i <= 22 THEN 12
           WHEN i <= 24 THEN 6
           WHEN i <= 36 THEN 5
           ELSE NULL
       END
FROM n;

INSERT INTO course_enrollment
SELECT CASE WHEN i < 10 THEN 's0' || i ELSE 's' || i END,
       '2022-23',
       1,
       CASE
           WHEN i <= 8 THEN '4'
           WHEN i <= 10 THEN '3.7'
           WHEN i = 11 THEN '2.0'
           WHEN i = 12 THEN '2'
           WHEN i = 13 THEN '3'
           WHEN i = 14 THEN '2.3'
           WHEN i = 15 THEN '1.0'
           WHEN i = 16 THEN '1.7'
           WHEN i = 17 THEN '1'
           WHEN i = 18 THEN '0.3'
           WHEN i <= 20 THEN 'F'
           WHEN i = 21 THEN 'W'
           WHEN i = 22 THEN 'I'
           WHEN i = 23 THEN 'A'
           ELSE 'P'
       END
FROM n
WHERE i <= 24;

INSERT INTO course_enrollment SELECT 's0' || i, '2022-23', 2, 'W' FROM n WHERE i <= 3;

INSERT INTO course_enrollment VALUES ('s01', '2022-23', NULL, NULL);

INSERT INTO course_enrollment SELECT 's' || i, '2024-25', 1, 'I' FROM n WHERE i >= 37;

-- Students 25-27 take four classes each. n is joined to itself to give each student the numbers 1 to 4.
INSERT INTO course_enrollment
SELECT 's' || a.i, '2023-24', b.i, 'P' FROM n AS a, n AS b WHERE a.i BETWEEN 25 AND 27 AND b.i <= 4;

INSERT INTO course VALUES (1, 'ENGL', '1302');
INSERT INTO course VALUES (2, 'MATH', '1314');
INSERT INTO course VALUES (3, 'BIOL', '1101');
INSERT INTO course VALUES (4, 'HIST', '1301');

-- Terms and delivery, for DFW's term and delivery groups and for federal (fall to fall) retention.
-- Every enrollment above is in Fall 2022 and taught face to face.
CREATE TABLE term (term_id INTEGER, academic_year TEXT, academic_term TEXT, sort_order INTEGER);
INSERT INTO term VALUES (1, '2022-23', 'FALL', 1);
ALTER TABLE course_enrollment ADD COLUMN term_id INTEGER;
ALTER TABLE course_enrollment ADD COLUMN delivery_method TEXT;
UPDATE course_enrollment SET term_id = 1, delivery_method = 'F';
