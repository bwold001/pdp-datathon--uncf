## Financial aid Analysis-Ready File Data Dictionary

First Name
Student’s first name
Middle Name
Student’s middle name or initial
Last Name
Student’s last name
SSN
Student’s Social Security Number
Date of Birth
Student’s date of birth in YYYYMMDD format
Student ID
Student’s ID number at your institution
Institution ID
8-digit OPEID
Cohort
YYYY- YY format. Includes all undergraduate students who attempted at least one course in a given term for the first time at your institution. Students may be first-time ever in college or new transfer students and may be enrolled at any program level, including credential-seeking, college remedial, developmental, college-preparatory, adult basic skills (ESL, ABE, or ASE/GED), and non-credit vocational students. For non-credit vocational students, cohort only includes those who enrolled in courses that could lead to an occupational certificate, industry certificate, or other type of credential of economic value as well as those students who are simultaneously enrolled in credit- bearing courses.
Also includes:

Past dual enrollment students who took a course or courses at the cohort institution while simultaneously
attending high school
Fall entry students who enrolled in summer work prior to first term of enrollment with credential-seeking status. Examples of summer work include, but are not limited to, summer bridge programs or developmental/remedial coursework
Excludes:

Non-credit vocational students enrolled in purely personal enrichment courses
Current dual enrollment students or those taking a course or courses at the cohort institution while simultaneously
attending high school.
Cohort Term
(Fall, Winter, Spring, or Summer) Term student first enrolled in at least one course. See definition of cohort. If you have more than one term (e.g. Summer I and Summer II) you can differentiate the terms by using the appropriate Term Begin and Term End dates.
Student Age
A student’s age is calculated as Term Start Date of the institution term listed for the designated fall term in the cohort year minus Date of Birth divided by 365.25. Once rounded to the nearest whole number, ages are grouped into 3 categories: 20 and younger, >20-24, older than 24.
Academic Year
Academic year in which the student was enrolled in the course in YYYY–YY format.
Dependency Status
Student’s dependency status at the time of FAFSA application or first term of enrollment for the academic year if FAFSA data is not available.
D = Dependent
I = Independent
X = Rejected Dependent
Y = Rejected Independent
If blank or any other value code as UK
Housing Status
Type of housing student stayed in during the academic year.
1 = Off-campus (not with family): Student does not live with parents or legal guardians in a housing facility that is not owned or controlled by the educational institution.
2 = Off-campus (with family): Student lives with parents or legal guardians in a housing facility that is not owned or controlled by the educational institution.
3 = Off-campus: Only use this option if ISIR for student is not available and detail of Off-Campus living (with or without family) is unknown.
4 = On-campus housing: Any residence hall or housing facility owned or controlled by an institution within the same reasonably contiguous geographic area and used by the institution in direct support of or in a manner related to the institution’s educational purposes.
Any other value, or if blank, recode to UK
Cost of Attendance
Tuition + Room Charges + Board Charges + Books + Other Expenses. Continuous with a minimum value of 0.
EFC
Expected Family Contribution: An index number that financial aid staff use to determine how much financial aid a student would receive if they were to attend the institution. The information reported on the student’s FAFSA form is used to calculate their EFC. EFC Passes through from the data intake file. Continuous with a minimum value of 0.
Total Institutional Grants
Institution Grant Need Based + Institution Grant Employer Aid + Institution Grant Merit + Institution Grant Military or Veteran + Other Institution Grant (Non-need Based). Continuous with a minimum value of 0.
Total State Grants
State Grant Need Based + State Grant Non-need Based. Continuous with a minimum value of 0.
Total Federal Grants
SEOG + TEACH + Veteran and Military + Other Federal Grant + Pell Amount. SEOG: Supplemental Educational Opportunity Grant. TEACH: Teacher Education Assistance for College and Higher Education. Continuous with a minimum value of 0.
Unmet Need
Cost of Attendance – EFC – Total Institutional Grants – Total State Grants – Total Federal Grants. Continuous with a minimum value of 0.
Net Price
Cost of Attendance – Total Institutional Grants – Total State Grants – Total Federal Grants. Continuous with a minimum value of 0.
Applied Aid
Whether the institution received an ISIR record (including rejected ISIR records) for the student for the academic year.
Y = Yes
N = No
