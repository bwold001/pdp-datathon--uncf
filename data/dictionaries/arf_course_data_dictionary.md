## Course-Level Analysis-Ready File Data Dictionary

First Name

Student’s first name in the submission file.

Middle Name

Student’s middle name or first initial of middle name in the submission file.

Last Name

Student’s last name in the submission file.

SSN

Student’s Social Security number in the submission file.

Date of Birth

Student’s date of birth in the submission file in YYYYMMDD format.

Student ID

Institutionally supplied student ID number in the submission file.

Student Age

A student’s age is calculated as: Term Start Date of the institution term listed for the designated fall term in the cohort year minus Date of Birth divided 365.25 and rounded to the nearest whole number.

- 20 and younger
- > 20-24
- > 24

Race

Student’s race in the submission file.

- Nonresident Alien
- American Indian or Alaska Native
- Asian
- Black or African American
- Native Hawaiian or Other Pacific Islander
- White
- Hispanic
- Two or more races
- Unknown or missing

Ethnicity

Ethnicity Ethnicity Student’s ethnicity in the submission file.

- UK = Unknown
- H = Hispanic
- N = Not Hispanic

Gender

Student gender reported to the PDP. If gender was not reported to the PDP, it is imported from data reported to the Clearinghouse’s enrollment reporting service. If gender was not reported to the PDP or enrollment reporting, it is imputed using methods developed by the Research Center. If gender is reported as *Unknown*, not reported to PDP or enrollment reporting, and cannot be imputed, the value will be *Unknown*.

- M = Male
- F = Female
- P = Prefer not to specify
- X = Nonbinary, intersex, and gender-nonconforming
- UK = Unknown

Institution ID

The institution’s ID (currently only OPEID) 8-digit OPEID

Cohort

Academic year in which the student first enrolled in at least one course in YYYY-YY format. Must match the Cohort value in the course data file. Must be 2 consecutive years between 2000 and today. Example: 2019-20

Cohort Term

Term student first enrolled in at least one course.

- Fall
- Winter
- Spring
- Summer

Academic Year

Academic year in which the student was enrolled in the course in YYYY–YY format.

Academic Term

Academic term in which the student was enrolled in the course.

- Fall
- Winter
- Spring
- Summer

Course Prefix

Course prefix in the submission file. Course prefix as it appears in your institution’s catalog. For example, ENG 101 Composition I = ENG. Can include: period, hyphen, underscore, ampersand

Course Number

Course number in the submission file. Course number as it appears in your institution’s catalog. For example, ENG 101 Composition I = 101. Can include: period, hyphen, underscore, ampersand

Section ID

Section ID in the submission file. Section ID as it appears in your institution’s catalog. If not available, enter Missing. Can include: period, hyphen, underscore, ampersand

Course Name

Course name in the submission file. Course name as it appears in your institution’s catalog. For example, ENG 101 Composition I = Composition I.

Course CIP

Appropriate Course CIP Code. See [https://nces.ed.gov/ipeds/cipcode](https://nces.ed.gov/ipeds/cipcode) for a list of valid codes. Left blank if a code is not available.

Course Type

Type of course.

- CU = College‐level, undergraduate (credit towards certificate, associate’s, or bachelor’s degree)
- CG = College level, graduate (credit towards graduate degree)
- CC = College developmental, remedial or preparatory credit towards credential completion requirements
- CD = College developmental, remedial or preparatory credits not applicable towards credential completion requirements
- EL = ESL (non‐credit adult basic skills courses supported by WIA Title II)
- AB = Adult basic education
- GE = Adult secondary education/GED
- NC = Non‐credit vocational (courses that lead to an occupational certificate, industry certificate, or other type of credential)
- O = Other

Math or English Gateway

Whether the course is considered a Math or English Gateway.

- M = Math
- E = English
- N = N/A

Co-requisite Course

Whether or not this course was a co-requisite, which enrolls students in developmental (remedial) education and college‐level courses in the same subject at the same time.

- Y = Yes
- N = No

Course Begin Date

Date the student began enrollment in the course (not the registration date) in YYYYMMDD format.

Course End Date

Date the student ended enrollment in the course in YYYYMMDD format.

Grade

Grade the student earned for the course in the submission file. Student’s grade for the term on a 4‐point scale. If a numeric grade did not apply to the course, one of the following values may appear:

- P = Pass
- F = Fail
- I = Incomplete
- W = Withdraw
- A = Audit
- M = Missing
- O = Other

Number of Credits Attempted

Attempted Number of credits the student attempted in the course. Should be a number between 0-20.

Number of Credits Earned

Number of credits the student earned for the course. Should be a number between 0-20; cannot be greater than number of credits attempted

Delivery Method

Describes how the course was administered between teacher and student.

- F = Face-to-face
- O = Online
- H = Hybrid

Left blank if the course was delivered by another method.

Core Course

Course is part of core competency/general education courses at the institution.

- Y = Yes
- N = No

Left blank if not applicable.

Core Course Type

Type of core competency. Required if Core Course = Y. Can be up to 20 characters. For example, core course type for “Introduction to Art 101” is “Humanities.”

Core Competency Completed

Student completed the core/general education course.

- Y = Core requirements evaluated and satisfied
- N = Core requirements evaluated but not satisfied

Enrollment Record at Other Institution(s)

Whether or not the student was enrolled at another institution at the same time as this course or during this academic term (if a course record is not available).

- Y = Yes
- N = No

Credential Engine Identifier

Course credential registry number or Credential Transparency Identifier (CTID). Serves as the primary unique identifier for all major objects in the Credential Registry and follows a standard format.

**Note:** This field is optional for data submission. If not submitted by the data provider, it will not appear in the analysis-ready file.

Course Instructor Employment Status

Employment status of the course instructor reported when the student was established in the cohort (can be updated by the data submitter).

- PT = Instructor is employed part time
- FT = Instructor is employed full time

**Note:** This field is optional for data submission. If not submitted by the data provider, it will not appear in the analysis-ready file.

Course Instructor Rank

Academic rank of the course instructor reported when the student was established in the cohort (can be updated by the data submitter).

- 1 = Instructor
- 2 = Lecturer
- 3 = Senior Lecturer
- 4 = Assistant Professor
- 5 = Associate Professor
- 6 = Professor
- 7 = Other

**Note:** This field is optional for data submission. If not submitted by the data provider, it will not appear in the analysis-ready file.

Enrollment Record at Other Institution(s) OPEID(s)

OPEID or OPEIDs where student was enrolled at the same time as this course or during this academic term. If enrolled in multiple other institutions, values will be pipe ( | ) delimited. Field will be blank if no other enrollments.

Enrollment Record at Other Institution(s) STATE(s)

State or states where student was enrolled at the same time as this course or during this academic term. If enrolled in multiple other institutions, values will be pipe ( | ) delimited in the same order as the OPEID list. Field will be blank if no other enrollments.

Enrollment Record at Other Institution(s) CARNEGIE(s)

Carnegie classification or classifications where student was enrolled at the same time as this course or during this academic term. If enrolled in multiple other institutions, values will be pipe ( | ) delimited in the same order as the OPEID list. Field will be blank if no other enrollments.

Enrollment Record at Other Institution(s) LOCALE(s)

Locale or locales where student was enrolled at the same time as this course or during this academic term. If enrolled in multiple other institutions, values will be pipe (|) delimited in the same order as the OPEID list. Field will be blank if no other enrollments.

**LOCALE Values:** *Urban* includes *City Large, City Midsize,* and *City Small* from IPEDS. *Suburb* includes *Suburb Large, Suburb Midsize,* and *Suburb Small* from IPEDS. *Town/Rural* includes *Town Fringe, Town Distant, Town Remote, Rural Fringe, Rural Distant,* and *Rural Remote* from IPEDS.

Term Program of Study

Student’s program of study based on major CIP code reported by the cohort institution for the specific term in which this course was taken.
