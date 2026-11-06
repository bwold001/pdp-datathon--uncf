## Cohort-Level Analysis-Ready File Data Dictionary

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

Institution ID

8-digit OPEID.

Cohort

All undergraduate students who attempted at least one course in a given term, for the first time at the cohort institution in YYYY-YY format. **Example:** *2016-17*

Students may be first-time ever in college or new transfer students at the cohort institution and may be enrolled at any program level, including credential- seeking; college remedial, developmental, or college- preparatory; adult basic skills (ESL, ABE, or ASE/GED); and non-credit vocational students. For non-credit vocational students, cohort only includes those who enrolled in courses that could lead to an occupational certificate, industry certificate, or other type of credential of economic value, as well as those students who are simultaneously enrolled in credit- bearing courses.

**Also includes:**

- Past dual enrollment students who took a course or courses at the cohort institution while simultaneously attending high school.
- Fall entry students who enrolled in summer work prior to first term of enrollment with credential-seeking status. Examples of summer work include summer bridge programs or developmental/remedial coursework.

**Does not include:**

- Non-credit vocational students enrolled in purely personal enrichment courses.
- Current dual enrollment students or those taking a course or courses at the cohort institution while simultaneously attending high school.

Cohort Term

Cohort term of entry: Term student first enrolled in at least one course. See definition of cohort. If you have more than one term (e.g. Summer I and Summer II) you can differentiate the terms by using the appropriate Term Begin and Term End dates.

- FALL
- WINTER
- SPRING
- SUMMER

Student Age

A student’s age is calculated as: Term Start Date of the institution term listed for the designated fall term in the cohort year minus Date of Birth divided by 365.25. Once rounded to the nearest whole number, ages are grouped into 3 categories:

- 20 and younger
- > 20-24
- Older than 24

Enrollment Type

The student’s enrollment type at the time of the defined cohort in the submission file.

- First-time
- Re-admit
- Transfer-in

Enrollment Intensity First Term

A student’s full or part-time status is determined by the number of college credits attempted. If this value for the student’s first term is greater than or equal to the single term-based credit threshold provided by the institution, the student is considered full-time. Otherwise, the student is considered part-time.

- Full-time
- Part-time

Math Placement

Student was determined to be college ready, not college ready, or of unknown readiness in math upon entry based on institution’s standard math placement policies (e.g. placement determined by test scores, HS GPA, HS course taking and/or other institutional criteria).

- C = Student is college ready in Math
- N = Student is not college ready in Math
- UK = Unknown or missing

English Placement

Student was determined to be college ready, not college ready, or of unknown readiness in English upon entry based on institution’s standard English placement policies (e.g. placement determined by test scores, HS GPA, HS course taking and/or other institutional criteria).

- C = Student is college ready in English
- N = Student is not college ready in English
- UK = Unknown or missing

Past Dual and Summer Enrollment

Student was a dual or concurrent high school enrollment student prior to first term enrolled with credential-seeking status at the cohort institution, and/or enrolled in summer work prior to first term of enrollment with credential- seeking status. Examples of summer work include, but are not limited to, summer bridge programs or developmental or remedial coursework.

- DE = Past Dual Enrollment
- SE = Past Summer Enrollment
- DS = Past Dual and Summer Enrollment

Race

Student race in the cohort data submission file.

- White
- Hispanic
- American Indian or Alaska Native
- Native Hawaiian or Other Pacific Islander
- Two or More Races
- Black or African American
- Nonresident alien
- Asian
- Unknown

Ethnicity

Student ethnicity in the submission file.

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

First Gen

First Generation Status: A student who is the first member of his or her immediate family to graduate from a college or university.

- N = No parent has attended post-secondary
- P = At least one parent has attended post-secondary but earned no credential or degree
- C = At least one parent has a certificate
- A = At least one parent has an associate degree
- B = At least one parent has a bachelors degree or higher
- E = At least one parent earned a credential or degree (level unknown)

Pell Status First Year

If a student received a Pell Grant in any term within their first academic year. If this field is not populated through PDP data submission, the PDP will attempt to populate it using The Clearinghouse’s enrollment reporting data.

- Y = Yes
- N = No

Attendance Status Term 1

In a student’s first term of study, whether the student is a first-time freshman, a first-time transfer-in, or neither and whether the student is full-time or part-time.

- First-Time Full-Time
- First-Time Part-Time
- Transfer-In Full-Time
- Transfer-In Part-Time

Credential Type Sought Year 1

A student’s credential-seeking status is based on his/her “Degree Type Sought” value in an institution’s submission file. If degree type sought is not populated in the Course Extended file, or if this field was populated in historical data from a secondary data source that does not have values that can be mapped with the values in the Course Extended File submission guide, then this is populated from NSC enrollment records, which is why there are multiple values that correspond to the same credential type.

- C1 = Less than one-year certificate, less than Associate degree
- C2 = One to two year certificate, less than Associate degree
- C4 = Two to four year certificate, less than Bachelor’s degree
- 01 = Undergraduate Certificate or Diploma Program
- A or 02 = Associate Degree
- B or 03 = Bachelor’s Degree
- PB or 04 = Post Baccalaureate Certificate
- M or 05 = Master’s Degree
- D or 06 = Doctoral Degree
- FP or 07 = First Professional Degree
- PC or 08 = Graduate/Professional Certificate
- NC or 99 = Non- Credential Program (Preparatory Coursework/Teach Certification)
- −1= Missing

Program of Study Term 1

Student’s program of study based on major CIP code reported by the cohort institution. Six-digit numeric code.

GPA Group Term 1

Student’s GPA at the end of first term. Continuous with values between 0-4.

GPA Group Year 1

Student’s GPA at the end of first academic year. Continuous with values between 0-4.

Number of Credits Attempted Year 1

The sum of the values in the number of credits attempted fields in the Course Extended file for the student’s first academic year. Continuous with a minimum value of 1.

Number of Credits Earned Year 1

The sum of the values in the number of credits earned fields in the Course Extended file for the student’s first academic year. Continuous with a  
minimum value of 0.

Number of Credits Attempted Year 2

The sum of the values in the number of credits attempted fields in the Course Extended file for the student’s second academic year. Continuous with a minimum value of 0.

Number of Credits Earned Year 2

The sum of the values in the number of credits earned fields in the Course Extended file for the student’s second academic year. Continuous with a minimum value of 0.

Number of Credits Attempted Year 3

The sum of the values in the number of credits attempted fields in the Course Extended file for the student’s third academic year. Continuous with a minimum value of 0.

Number of Credits Earned Year 3

The sum of the values in the number of credits earned fields in the Course Extended file for the student’s third academic year. Continuous with a minimum value of 0.

Number of Credits Attempted Year 4

The sum of the values in the number of credits attempted fields in the Course Extended file for the student’s fourth academic year. Continuous with a minimum value of 0.

Number of Credits Earned Year 4

The sum of the values in the number of credits earned fields in the Course Extended file for the student’s fourth academic year. Continuous with a minimum value of 0.

Gateway Math Status

Indicates whether the student is required to complete a gateway math course at time of first enrollment. Some students may be exempt from gateway math coursework, for example, those transferring from another institution where they completed the requirement, or students fulfilling the requirement by successful completion of AP, IB or similar high school coursework. Also, some majors/program areas may not require a gateway math course.

- R = Gateway Math course is required of student at time of entry
- N = Gateway Math course is not required of student at time of entry
- UK = Unknown or missing

Gateway English Status

Indicates whether the student is required to complete a gateway English course at time of first enrollment. Some students may be exempt from gateway English coursework, for example, those transferring from another institution where they completed the requirement, or students fulfilling the requirement by successful completion of AP, IB or similar high school coursework. Also, some majors/program areas may not require a gateway English course.

- R = Gateway English course is required of student at time of entry
- N = Gateway English course is not required of student at time of entry
- UK = Unknown or missing

AttemptedGatewayMathYear1

If a student is required to complete a gateway math course in the first academic year and the number of credits attempted for a math gateway course are greater than 0, the student is considered to have attempted.


- Y = Attempted Gateway Math Course
- N = Did not Attempt Gateway Math Course
- UK = Unknown

AttemptedGatewayEnglishYear1

If a student is required to complete a gateway English course in the first academic year and the number of credits attempted for an English gateway course are greater than 0, the student is considered to have attempted.

- Y=Attempted Gateway English Course
- N = Did not Attempt Gateway English Course
- UK = Unknown

CompletedGatewayMathYear1

For students who are required to take gateway math, and who receive a grade greater than or equal to 1 on a 4-point scale, or a “P” if the course is Pass/Fail during their first academic year.

- C = Completed
- D = Did not complete
- NA = Not applicable

CompletedGatewayEnglishYear1

Completed English Gateway Course First Year  
For students who are required to take gateway English, and who receive a grade greater than or equal to 1 on a 4-point scale, or a “P” if the course is Pass/Fail during their first academic year.

- C = Completed
- D = Did not complete
- NA = Not applicable

GatewayMathGradeY1

For students who are required to take gateway math the highest grade they received in their attempted gateway math course in their first academic year. Continuous with values between 0-4. If a numeric grade does not apply to the course:

- P = Pass
- F = Fail
- I = Incomplete
- W = Withdraw
- A = Audit
- M = Missing
- O = Other

GatewayEnglishGradeY1

For students who are required to take gateway English, the highest grade they received in their attempted gateway English course in their first academic year. Continuous with values between 0-4. If a numeric grade does not apply to the course:

- P = Pass
- F = Fail
- I = Incomplete
- W = Withdraw
- A = Audit
- M = Missing
- O = Other

AttemptedDevMathY1

If in a student’s first academic year, the student is not considered college ready in math, and has at least one course in the Course Extended file with a course type that is developmental, remedial or preparatory, the student is assumed to have attempted developmental math. If a student is not college ready in math, but no course type is listed as developmental, remedial or preparatory, a student is not considered to have attempted developmental math. If a student’s math placement is unknown then the value will be listed as unknown.

- Y = Yes
- N = No
- NA = Not Applicable
- UK = Unknown

AttemptedDevEnglishY1

If in a student’s first academic year, the student is not considered college ready in English, and has at least one course in the Course Extended file with a course type that is developmental, remedial or preparatory, the student is assumed to have attempted developmental English. If a student is not college ready in English but no course type is listed as developmental, remedial or preparatory, a student is not considered to have attempted developmental English. If a student’s English placement is unknown then the value will be listed as unknown.

- Y = Yes
- N = No
- NA = Not Applicable
- UK = Unknown

CompletedDevMathY1

For students who were referred/placed into developmental math, whether the student completed final developmental Math requirement(s) during the term as reported in the submission file. The student need not have completed all of the requirements during this term, just the final requirement.

- C = Referred/placed, completed dev Math coursework
- D = Referred/placed, did not complete dev math coursework
- NA = Not applicable

CompletedDevEnglishY1

For students who were referred/placed into developmental math, whether the student completed final developmental English requirement(s) during the term as reported in the submission file. The student need not have completed all of the requirements during this term, just the final requirement.

- C = Referred/placed, completed dev English coursework
- D = Referred/placed, did not complete dev English coursework
- NA = Not applicable

Retention

Retention is defined as either continued enrollment at the cohort institution in the second academic year or completion of any credential at the initial institution in the first or second academic year.

- 1 = student was retained
- 0 = student was not retained

Persistence

A student is defined as having persisted if the student has a bachelor’s degree from another institution by second year, or an associate degree or certificate from another institution by second year, or is enrolled at other institution by second year.

- 1 = student persisted
- 0 = student did not persist

Years to Bachelors at Cohort Inst.

The most recent academic year in which the cohort institution awarded a bachelor’s degree to the student (as determined by the student’s reported cohort start date). To calculate a student’s time to credential, PDP uses three values: the credential award date from an institution as reported to the Clearinghouse’s degree verification service, the student’s reported cohort start date value as reported to PDP, and the number of calendar days in a year. The value is calculated as: (credential award date – cohort begin date)/365. If the result is >0 and <=1, the value is 1; if the result is >1 and <=2, the value is 2, and so forth up to value of 7.

- 0
- 1
- 2
- 3
- 4
- 5
- 6
- 7

Years to Associates or Certificate at Cohort Inst.

The most recent academic year in which the cohort institution awarded an associate degree or certificate to the student (as determined by the student’s reported cohort start date). Calculated as degree/certificate awarded date – cohort begin date / 365. If the result is >0 and 1 and <=2, the value is 2, etc.

- 0
- 1
- 2
- 3
- 4
- 5
- 6
- 7

Years to Bachelors at Other Inst.

The most recent academic year in which an institution other than the cohort institution awarded a bachelor’s degree to the student (as determined by the student’s reported cohort start date). To calculate a student’s time to credential, PDP uses three values: the credential award date from an institution as reported to the Clearinghouse’s degree verification service, the student’s reported cohort start date value as reported to PDP, and the number of calendar days in a year. The value is calculated as: (credential award date – cohort begin date)/365. If the result is >0 and <=1, the value is 1; if the result is >1 and <=2, the value is 2, and so forth up to value of 7.

- 0
- 1
- 2
- 3
- 4
- 5
- 6
- 7

Years to Associates or Certificate at Other Inst.

The most recent academic year in which an institution other than the cohort institution awarded an associate degree or certificate to the student (as determined by the student’s reported cohort start date). Calculated as degree/certificate awarded date – cohort begin date / 365. If the result is >0 and 1 and <=2, the value is 2, etc.

- 0
- 1
- 2
- 3
- 4
- 5
- 6
- 7

Year of Last Enrollment at Cohort Institution

The year of the last term enrollment begin date that student was enrolled at the cohort institution.

- 0
- 1
- 2
- 3
- 4
- 5
- 6
- 7

Year of Last Enrollment at Other Institution

The year of the last term enrollment begin date that student was enrolled at an institution other than the cohort institution.

- 0
- 1
- 2
- 3
- 4
- 5
- 6
- 7

Time to Credential

Number of years between a student’s earliest enrollment at cohort institution and earliest degree award date at the cohort institution rounded to nearest decimal.

Reading Placement

Student was determined to be college ready, not college ready, or of unknown readiness in reading upon entry based on institution’s standard reading placement policies (e.g. placement determined by test scores, HS GPA, HS course taking and/or other institutional criteria).

- C = Student is college ready in reading
- N = Student is not college ready in reading
- UK = Unknown or missing

**Note:** This field is optional for data submission. If not submitted by the data provider, it will not appear in the analysis-ready file.

Special Program

Student is participating in a special program as reported by the data submitter. For example, *Mathfocusedprogram2021* or *EarlyInterventioncohort2020*.

**Note:** This field is optional for data submission. If not submitted by the data provider, it will not appear in the analysis-ready file.

NASPA First-Generation

NASPA coding for the student’s first generation status. Does not impact the first generation filter in the dashboard.

- -1 = Unknown
- 0 = Student is not considered first generation
- 1 = Neither biological parent earned a four-year college degree
- 2 = Neither parent or guardian earned a four-year college degree
- 3 = Neither parent or guardian earned a four-year college degree from an institution in the United States
- 4 = Neither parent or guardian with primary influence on the student at age 16 earned a four-year college degree
- 5 = Neither parent completed education beyond an associate/two-year degree
- 6 = Neither parent entered any form of higher education

**Note:** This field is optional for data submission. If not submitted by the data provider, it will not appear in the analysis-ready file.

Incarcerated Status

Whether the student was reported as incarcerated or previously incarcerated when established in the cohort (can be updated by the data submitter).

- Y = Student is currently incarcerated
- P = Student was previously incarcerated (before enrolling at the cohort institution)
- N = Student is not currently incarcerated and was not previously incarcerated
- UK = Unknown

**Note:** This field is optional for data submission. If not submitted by the data provider, it will not appear in the analysis-ready file.

Military Status

Whether the student was reported as a veteran or on active duty when the established in the cohort (can be updated by the data submitter).

- -1 = Unknown
- 0 = None/Unknown
- 1 = Veteran
- 2 = Active Duty/Reserves/National Guard

**Note:** This field is optional for data submission. If not submitted by the data provider, it will not appear in the analysis-ready file.

Employment Status

Whether the student was reported as employed when the established in the cohort (can be updated by the data submitter).

- -1 = Unknown
- 0 = Unknown
- 1 = Student is employed full time
- 2 = Student is employed less than full time but at least half time
- 3 = Student is employed less than half time
- 4 = Student is not employed

**Note:** This field is optional for data submission. If not submitted by the data provider, it will not appear in the analysis-ready file.

Disability Status

Whether the student was reported as having a disability when the established in the cohort (can be updated by the data submitter).

- Y = Student has a learning, physical, and/or psychological disability documented with the disability office or similar office at the cohort institution
- N = Student does not identify as having a disability or have a disability documented/reported with the disability office or similar office at the cohort institution
- UK = Unknown

**Note:** This field is optional for data submission. If not submitted by the data provider, it will not appear in the analysis-ready file.

Foreign Language Completion

Term and year in which the student completed a foreign language requirement.

- Term and Year = Student completed a foreign language requirement in that term of the year (For example, *Fall 2019* or *Winter 2020*)
- N = Student has not completed any foreign language requirement

**Note:** This field is optional for data submission. If not submitted by the data provider, it will not appear in the analysis-ready file.

First Year to Bachelors at Cohort Institution

The academic year in which the cohort institution awarded the first bachelor’s degree to the student (as determined by the student’s reported cohort start date). To calculate a student’s time to credential, PDP uses three values: the credential award date from an institution as reported to the Clearinghouse’s degree verification service, the student’s reported cohort start date value as reported to PDP, and the number of calendar days in a year. The value is calculated as: (credential award date – cohort begin date)/365. If the result is >0 and <=1, the value is 1; if the result is >1 and <=2, the value is 2, and so forth up to value of 7.

- 0
- 1
- 2
- 3
- 4
- 5
- 6
- 7

First Year to Associates or Certificate at Cohort Institution

The academic year in which the cohort institution awarded the first associate degree or certificate to the student (as determined by the student’s reported cohort start date). Calculated as degree/certificate awarded date – cohort begin date / 365. If the result is >0 and 1 and <=2, the value is 2, etc.

- 0
- 1
- 2
- 3
- 4
- 5
- 6
- 7

First Year to Bachelors at Other Institution

The academic year in which an institution other than the cohort institution awarded the first bachelor’s degree to the student (as determined by the student’s reported cohort start date). To calculate a student’s time to credential, PDP uses three values: the credential award date from an institution as reported to the Clearinghouse’s degree verification service, the student’s reported cohort start date value as reported to PDP, and the number of calendar days in a year. The value is calculated as: (credential award date – cohort begin date)/365. If the result is >0 and <=1, the value is 1; if the result is >1 and <=2, the value is 2, and so forth up to value of 7.

- 0
- 1
- 2
- 3
- 4
- 5
- 6
- 7

First Year to Associates or Certificate at Other Institution

The academic year in which an institution other than the cohort institution awarded the first associate degree or certificate to the student (as determined by the student’s reported cohort start date). Calculated as degree/certificate awarded date – cohort begin date / 365. If the result is >0 and 1 and <=2, the value is 2, etc.

- 0
- 1
- 2
- 3
- 4
- 5
- 6
- 7

Program of Study Year 1

The student’s final program of study based on the major CIP code reported by the cohort institution in their first academic year. Six-digit numeric code (the first two digits match the program of study filter on the dashboards).

Most Recent Bachelors at Other Institution OPEID

The OPEID of the institution other than the cohort institution that awarded the student their most recent bachelor’s degree.

Most Recent Associates or Certificate at Other Institution OPEID

The OPEID of the institution other than the cohort institution that awarded the student their most recent associate degree or certificate.

Most Recent Last Enrollment at Other Institution OPEID

The OPEID of the institution other than the cohort institution where the student was most recently enrolled.

First Bachelors at Other Institution OPEID

The OPEID of the institution other than the cohort institution that awarded the student their first bachelor’s degree (after student’s start at the cohort institution).

First Associates or Certificate at Other Institution OPEID

The OPEID of the institution other than the cohort institution that awarded the student their first associate degree or certificate (after student’s start at the cohort institution).

Most Recent Bachelors at Other Institution STATE

The state of the institution other than the cohort institution that awarded the student their most recent bachelor’s degree.

Most Recent Associates or Certificate at Other Institution STATE

The state of the institution other than the cohort institution that awarded the student their most recent associate degree or certificate.

Most Recent Last Enrollment at Other institution STATE

The state of the institution other than the cohort institution where the student was most recently enrolled.

First Bachelors at Other Institution STATE

The state of the institution other than the cohort institution that awarded the student their first bachelor’s degree (after student’s start at the cohort institution).

First Associates or Certificate at Other Institution STATE

The state of the institution other than the cohort institution that awarded the student their first associate degree or certificate (after student’s start at the cohort institution).

Most Recent Bachelors at Other Institution CARNEGIE

The Carnegie classification (rolled up like the PDP benchmarking dashboards) of the institution other than the cohort institution that awarded the student their most recent bachelor’s degree.

Most Recent Associates or Certificate at Other Institution CARNEGIE

The Carnegie classification (rolled up like the PDP benchmarking dashboards) of the institution other than the cohort institution that awarded the student their most recent associate degree or certificate.

Most Recent Last Enrollment at Other institution CARNEGIE

The Carnegie classification (rolled up like the PDP benchmarking dashboards) of the institution other than the cohort institution where the student was most recently enrolled.

First Bachelors at Other Institution CARNEGIE

The Carnegie classification (rolled up like the PDP benchmarking dashboards) of the institution other than the cohort institution that awarded the student their first bachelor’s degree (after student’s start at the cohort institution).

First Associates or Certificate at Other Institution CARNEGIE

The Carnegie classification (rolled up like the PDP benchmarking dashboards) of the institution other than the cohort institution that awarded the student their first associate degree or certificate (after student’s start at the cohort institution).

**LOCALE Values:** *Urban* includes *City Large, City Midsize,* and *City Small* from IPEDS. *Suburb* includes *Suburb Large, Suburb Midsize,* and *Suburb Small* from IPEDS. *Town/Rural* includes *Town Fringe, Town Distant, Town Remote, Rural Fringe, Rural Distant,* and *Rural Remote* from IPEDS.

Most Recent Bachelors at Other Institution LOCALE

The locale of the institution other than the cohort institution that awarded the student their most recent bachelor’s degree.

Most Recent Associates or Certificate at Other Institution LOCALE

The locale of the institution other than the cohort institution that awarded the student their most recent associate degree or certificate.

Most Recent Last Enrollment at Other institution LOCALE

The locale of the institution other than the cohort institution where the student was most recently enrolled.

First Bachelors at Other Institution LOCALE

The locale of the institution other than the cohort institution that awarded the student their first bachelor’s degree (after student’s start at the cohort institution).

First Associates or Certificate at Other Institution LOCALE

The locale of the institution other than the cohort institution that awarded the student their first associate degree or certificate (after student’s start at the cohort institution).

Years to Latest Associates at Cohort Inst

The most recent academic year in which the cohort institution awarded an associate degree to the student (as determined by the student’s reported cohort start date). To calculate a student’s time to credential, PDP uses three values: the credential award date from an institution as reported to the Clearinghouse’s degree verification service, the student’s reported cohort start date value as reported to PDP, and the number of calendar days in a year. The value is calculated as: (credential award date – cohort begin date)/365. If the result is >0 and <=1, the value is 1; if the result is >1 and <=2, the value is 2, and so forth up to value of 7.

Years to Latest Certificate at Cohort Inst

The most recent academic year in which the cohort institution awarded a certificate to the student (as determined by the student’s reported cohort start date). Calculated as certificate awarded date – cohort begin date / 365. If the result is >0 and 1 and <=2, the value is 2, etc.

Years to Latest Associates at Other Inst

The most recent academic year in which an institution other than the cohort institution awarded an associate degree to the student (as determined by the student’s reported cohort start date). To calculate a student’s time to credential, PDP uses three values: the credential award date from an institution as reported to the Clearinghouse’s degree verification service, the student’s reported cohort start date value as reported to PDP, and the number of calendar days in a year. The value is calculated as: (credential award date – cohort begin date)/365. If the result is >0 and <=1, the value is 1; if the result is >1 and <=2, the value is 2, and so forth up to value of 7.

Years to Latest Certificate at Other Inst

The most recent academic year in which an institution other than the cohort institution awarded a certificate to the student (as determined by the student’s reported cohort start date). Calculated as certificate awarded date – cohort begin date / 365. If the result is >0 and 1 and <=2, the value is 2, etc.

First Year to Associates at Cohort Inst

The academic year in which the cohort institution awarded the first associate degree to the student (as determined by the student’s reported cohort start date). To calculate a student’s time to credential, PDP uses three values: the credential award date from an institution as reported to the Clearinghouse’s degree verification service, the student’s reported cohort start date value as reported to PDP, and the number of calendar days in a year. The value is calculated as: (credential award date – cohort begin date)/365. If the result is >0 and <=1, the value is 1; if the result is >1 and <=2, the value is 2, and so forth up to value of 7.

First Year to Certificate at Cohort Inst

The academic year in which the cohort institution awarded the first certificate to the student (as determined by the student’s reported cohort start date). Calculated as certificate awarded date – cohort begin date / 365. If the result is >0 and 1 and <=2, the value is 2, etc.

First Year to Associates at Other Inst

The academic year in which an institution other than the cohort institution awarded the first associate degree to the student (as determined by the student’s reported cohort start date). To calculate a student’s time to credential, PDP uses three values: the credential award date from an institution as reported to the Clearinghouse’s degree verification service, the student’s reported cohort start date value as reported to PDP, and the number of calendar days in a year. The value is calculated as: (credential award date – cohort begin date)/365. If the result is >0 and <=1, the value is 1; if the result is >1 and <=2, the value is 2, and so forth up to value of 7.

First Year to Certificate at Other Inst

The academic year in which an institution other than the cohort institution awarded the first certificate to the student (as determined by the student’s reported cohort start date). Calculated as certificate awarded date – cohort begin date / 365. If the result is >0 and 1 and <=2, the value is 2, etc.
