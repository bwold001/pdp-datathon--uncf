"""Reproduce every count in data/quality/findings.csv from the raw files.

Each finding has one check below, keyed by its id. The script recomputes the counts and compares
them with the log, so the log can't drift from the data. It never changes data/raw/.

    python data/quality/run_checks.py            # compare counts with findings.csv (exit 1 on a difference)
    python data/quality/run_checks.py --update   # rewrite the count column after a deliberate change
    python data/quality/run_checks.py --missing  # per column: each kind of no value, and whether the dictionary documents it

Needs pandas (requirements.txt). The notebook notebooks/deep_dive.ipynb shows each finding with
examples and a recommended fix.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
DICTIONARIES = ROOT / "data" / "dictionaries"
FINDINGS = Path(__file__).with_name("findings.csv")

KEY = ["Student_GUID", "Cohort"]
CUTOFF = 2025  # last academic year the files cover (2025-26): an assumption, see finding 2
TERM_ORDER = {"FALL": 0, "WINTER": 1, "SPRING": 2, "SUMMER": 3}
SPECIFIC_RACE = ["White", "Black or African American", "Asian", "American Indian or Alaska",
                 "Native Hawaiian or Other", "Two or More Races"]
ATTENDANCE = ["First-Time Full-Time", "First-Time Part-Time", "Transfer-In Full-Time", "Transfer-In Part-Time"]
TERM_MONTHS = {"FALL": [7, 8, 9, 10, 11], "SPRING": [12, 1, 2, 3, 4], "SUMMER": [4, 5, 6, 7, 8], "WINTER": [11, 12, 1, 2]}
SUBJECTS = {"Math": "M", "English": "E"}

# Every value as a string: "NA" is a real Course_Prefix, and "." marks no value in some columns.
cohort = pd.read_csv(RAW / "pdp_cohort_data.csv", dtype=str, keep_default_na=False)
course = pd.read_csv(RAW / "pdp_course_data.csv", dtype=str, keep_default_na=False)


def num(s):
    """Numbers as floats; the files' null markers become NaN."""
    return pd.to_numeric(s.mask(s.isin(["", ".", "NA", "UK"])), errors="coerce")


def year(s):
    """First year of a 'YYYY-YY' academic year: '2024-25' -> 2024."""
    return pd.to_numeric(s.str[:4], errors="coerce")


def in_rows(rows, df=cohort):
    """True for each row of df whose (Student_GUID, Cohort) appears in rows."""
    return pd.Series(df.set_index(KEY).index.isin(rows.set_index(KEY).index), index=df.index)


course_year = year(course.Academic_Year)
year_n = course_year - year(course.Cohort) + 1  # 1 = the student's first academic year
classes = course[course.Course_Prefix != ""]
grade = pd.to_numeric(classes.Grade, errors="coerce")
earned = num(classes.Number_of_Credits_Earned)
ttc = num(cohort.Time_to_Credential)
first_cred = pd.concat([num(cohort.First_Year_to_A_or_C_at_cohort), num(cohort.First_Year_to_Bachelors_at_coh)],
                       axis=1).replace(0, float("nan")).min(axis=1)


def first_gen_disagrees():
    both = cohort[(cohort.First_Gen != "") & (cohort.NASPAFirstGeneration != "-1")]
    agree = ((both.First_Gen == "N") & (both.NASPAFirstGeneration == "0")) | (
        (both.First_Gen == "Y") & both.NASPAFirstGeneration.isin(["1", "2"]))
    return (~agree).sum()


def future_credit_zeros():
    return sum(((year(cohort.Cohort) + n - 1 > CUTOFF) & (cohort[f"Number_of_Credits_Attempted_Yr_{n}"] == "0")).sum()
               for n in (3, 4))


def persistence_misses_elsewhere():
    elsewhere = course[(course.Enrolled_at_Other_Institution_s_ == "Y") & year_n.isin([1, 2])][KEY]
    return ((cohort.Retention == "1") & in_rows(elsewhere) & (cohort.Persistence == "0")).sum()


def classes_with_terms():
    """Class rows with the student's term numbers: Fall starters use the academic-year label as year 1,
    others the four terms from their first term (the reading that matches the cohort file best)."""
    c = classes.drop_duplicates().merge(cohort[KEY + ["Cohort_Term"]], on=KEY, suffixes=("", "_cohort"))
    c["term_n"] = year(c.Academic_Year) * 4 + c.Academic_Term.map(TERM_ORDER)
    c["start_n"] = year(c.Cohort) * 4 + c.Cohort_Term_cohort.map(TERM_ORDER)
    c["att"] = num(c.Number_of_Credits_Attempted)
    rolling = (c.term_n >= c.start_n) & (c.term_n < c.start_n + 4)
    c["in_y1"] = (year(c.Academic_Year) == year(c.Cohort)).where(c.Cohort_Term_cohort == "FALL", rolling)
    return c


def yr1_credit_mismatch():
    c, x = classes_with_terms(), cohort.set_index(KEY)
    reported = num(x.Number_of_Credits_Attempted_Yr_1)
    from_courses = c[c.in_y1].groupby(KEY).att.sum().reindex(x.index).fillna(0)
    return (reported.notna() & ((from_courses - reported).abs() >= 0.01)).sum()


def full_time_under_12():
    c, x = classes_with_terms(), cohort.set_index(KEY)
    first_term = c[c.term_n == c.start_n].groupby(KEY).att.sum().reindex(x.index)
    return ((x.Enrollment_Intensity_First_Term == "Full-Time") & (first_term < 12)).sum()


def codes_with_several_names():
    code = classes.Course_Prefix + " " + classes.Course_Number
    return (classes.groupby(code).Course_Name.nunique() > 1).sum()


def other_institution_blank():
    pairs = {"Years_to_BA_at_other_inst": "S_Most_Recent_Bachelors_at_O_I",
             "Years_to_A_or_C_at_other_inst": "S_Most_Recent_Associates_or_C",
             "Years_of_Last_Enrollment_at_othe": "S_Most_Recent_Last_Enroll_at_O"}
    return sum(((cohort[y] != "0") & (cohort[s] == "")).sum() for y, s in pairs.items())


def cohort_term_disagrees():
    j = course[KEY + ["Cohort_Term"]].merge(cohort[KEY + ["Cohort_Term"]], on=KEY, how="left", suffixes=("", "_c"))
    return (j.Cohort_Term != j.Cohort_Term_c).sum()


def years_past_cutoff():
    cols = [c for c in cohort.columns if c.startswith("Years_") and not c.startswith("Years_to_Latest")]
    years = cohort[cols].apply(num)
    return ((years > 0) & years.add(year(cohort.Cohort) - 1, axis=0).gt(CUTOFF)).sum().sum()


def gateway_conflicts():
    total = 0
    for subj in SUBJECTS:
        att, done = cohort[f"AttemptedGateway{subj}Year1"], cohort[f"CompletedGateway{subj}Year1"]
        g = cohort[f"Gateway{subj}GradeY1"]
        total += (((att.isin(["N", "UK"])) & (done == "C"))
                  | ((done == "C") & ((pd.to_numeric(g, errors="coerce") < 1) | g.isin(["F", "W", "I"])))
                  | ((cohort[f"Gateway_{subj}_Status"] == "R") & (att == ""))).sum()
    return total


def gateway_attempt_without_row():
    gw_y1 = classes[year_n[classes.index] == 1]
    return sum(((cohort[f"AttemptedGateway{s}Year1"] == "Y")
                & ~in_rows(gw_y1[gw_y1.Math_or_English_Gateway == code])).sum() for s, code in SUBJECTS.items())


def wrong_term_month():
    month = pd.to_datetime(classes.Course_Begin_Date, format="%Y%m%d", errors="coerce").dt.month
    return sum(pd.notna(m) and m not in TERM_MONTHS.get(t, []) for t, m in zip(classes.Academic_Term, month))


def first_class_before_cohort_term():
    own = classes[classes.Enrolled_at_Other_Institution_s_.isin(["N", "Y"])]
    first = (year(own.Academic_Year) * 10 + own.Academic_Term.map(TERM_ORDER)).groupby(
        [own.Student_GUID, own.Cohort]).min().rename("first_n")
    f = cohort.merge(first, left_on=KEY, right_index=True)
    start = year(f.Cohort) * 10 + f.Cohort_Term.map(TERM_ORDER)
    return ((f.first_n < start) & (f.first_n // 10 == year(f.Cohort))).sum()


def c_out_of_line():
    other = course[course.S_Enrollment_Record_at_other != ""]
    return (other.S_Enrollment_Record_at_other.str.count(r"\|") != other.C_Enrollment_Record_at_other.str.count(r"\|")).sum()


CHECKS = {
    "1": first_gen_disagrees,
    "2": future_credit_zeros,
    "3": persistence_misses_elsewhere,
    "4": yr1_credit_mismatch,
    "5": codes_with_several_names,
    "6": lambda: (cohort.Race.isin(SPECIFIC_RACE) & (cohort.Ethnicity == "UK")).sum(),
    "7a": lambda: (cohort.Pell_Status_First_Year == "U").sum(),
    "7b": lambda: (classes.Math_or_English_Gateway == "NA").sum(),
    "7c": lambda: cohort.Credential_Type_Sought_Year_1.str.contains("Teach Certification", regex=False).sum(),
    "8": lambda: (ttc > CUTOFF + 1 - year(cohort.Cohort)).sum(),
    "9": lambda: classes.duplicated(["Student_GUID", "Course_Prefix", "Course_Number", "Section_ID",
                                     "Academic_Year", "Academic_Term", "Course_Name"]).sum(),
    "10": other_institution_blank,
    "11": cohort_term_disagrees,
    "12": lambda: (course.Academic_Year == "").sum(),
    "13a": lambda: cohort.Race.isin(["American Indian or Alaska", "Native Hawaiian or Other"]).sum(),
    "13b": lambda: classes.Course_CIP.str.fullmatch(r"\d(\.\d+)?").sum(),
    "13c": lambda: (cohort.Program_of_Study_Term_1.str.len() == 5).sum(),
    "13d": lambda: course.Section_ID.str.contains(r"E\+").sum(),
    "13e": lambda: (course.C_Enrollment_Record_at_other.str.len() == 50).sum(),
    "14": lambda: (course.Course_Prefix.ne("") & (course_year < year(course.Cohort))).sum(),
    "15": lambda: cohort.Student_GUID.duplicated().sum(),
    "J1": lambda: len(course.merge(cohort[["Student_GUID"]], on="Student_GUID")) - len(course),
    "J2": lambda: cohort.duplicated(KEY).sum(),
    "J3": lambda: (~in_rows(cohort, course)).sum() + (~in_rows(course)).sum(),
    "S1": lambda: ((cohort.Time_to_Credential == ".") & first_cred.notna()).sum(),
    "S2": years_past_cutoff,
    "S3": lambda: ((classes.Grade == "F") & (earned > 0)).sum(),
    "S4": lambda: classes.Course_End_Date.str.startswith("2029").sum(),
    "S5": lambda: (classes.Core_Course_Type.str.len() == 1).sum(),
    "S6": full_time_under_12,
    "N1": lambda: sum(((cohort[f"AttemptedGateway{s}Year1"] == "UK") & (cohort[f"CompletedGateway{s}Year1"] == "D")).sum()
                      for s in SUBJECTS),
    "N2": gateway_conflicts,
    "N3": gateway_attempt_without_row,
    "N4": lambda: (classes.Math_or_English_Gateway.isin(["M", "E"]) & classes.Course_Type.isin(["CC", "CD"])).sum(),
    "N5": lambda: sum(((cohort[f"AttemptedDev{s}Y1"] == "N") & cohort[f"CompletedDev{s}Y1"].isin(["Y", "N"])).sum()
                      for s in SUBJECTS),
    "N6": lambda: (~cohort.Attendance_Status_Term_1.isin(ATTENDANCE)).sum(),
    "N7": lambda: (course.Course_CIP == "MISSING").sum(),
    "N8": lambda: (course.Course_Prefix == "NA").sum(),
    "N9": lambda: ((cohort.Race == "Nonresident alien") & (cohort.Ethnicity == "H")).sum(),
    "N10": lambda: ((course.Enrolled_at_Other_Institution_s_ == "Y") & (course.S_Enrollment_Record_at_other == "")).sum(),
    "N11": c_out_of_line,
    "N12": lambda: classes.Course_CIP.str.fullmatch(r"\d{2}").sum(),
    "N13": lambda: (((grade >= 1) | (classes.Grade == "P")) & (num(classes.Number_of_Credits_Attempted) > 0)
                    & (earned == 0)).sum(),
    "N14": wrong_term_month,
    "N15": lambda: ((cohort.Retention == "0") & in_rows(classes[year_n[classes.index] == 2])).sum(),
    "N16": lambda: (ttc > first_cred + 1).sum(),
    "N17": lambda: (~in_rows(classes) & (num(cohort.Number_of_Credits_Attempted_Yr_1) > 0)).sum(),
    "N18": first_class_before_cohort_term,
    "N19": lambda: ((num(cohort.Number_of_Credits_Earned_Yr_1) > 0) & (num(cohort.GPA_Group_Year_1) == 0)).sum(),
    "N20": lambda: (num(cohort.Number_of_Credits_Attempted_Yr_1) < 1).sum(),
    "N21": lambda: (classes.Co_requisite_Course == "").sum(),
    "N22": lambda: classes.Course_CIP.str.fullmatch(r"\d{1,2}\.\d{3}|\d{2}\.\d").sum(),
}


def documented_codes() -> dict:
    """Each column's listed codes and their meaning, read from its entry in the data dictionary:
    the "- CODE = meaning" lines under its heading. A column with no list documents no codes."""
    lookup = pd.read_csv(DICTIONARIES / "column_lookup.csv", dtype=str, keep_default_na=False)
    codes = {}
    for name in ("cohort", "course"):
        lines = (DICTIONARIES / f"arf_{name}_data_dictionary.md").read_text(encoding="utf-8").replace("−", "-").splitlines()
        rows = lookup[lookup.file == f"pdp_{name}_data.csv"]
        headings = set(rows.dictionary_name) - {""}
        for col, entry in zip(rows.column_in_csv, rows.dictionary_name):
            start = next((i for i, line in enumerate(lines) if line.strip() == entry), None)
            listed = {}
            for line in lines[start + 1:] if start is not None else []:
                if line.strip() in headings:
                    break
                code, eq, meaning = line.removeprefix("- ").partition("=")
                if line.startswith("- "):  # "- UK = Unknown", or a bare value such as "- Unknown"
                    listed[code.strip()] = (meaning if eq else code).strip()
            codes[(name, col)] = listed
    return codes


def missing_report() -> pd.DataFrame:
    """Per column, each kind of "no value" counted apart, then split by the dictionary: a documented
    unknown is a code the column's entry lists with a meaning such as Unknown, Missing or Not
    applicable (so 0 = None/Unknown counts, and 0 = No stays a valid zero); an undocumented marker is
    '.', UK, NA, MISSING or -1 where the entry doesn't list it."""
    markers = {"blank": [""], "dot": ["."], "UK": ["UK", "Unknown", "UNKNOWN"], "NA": ["NA"],
               "MISSING": ["MISSING"], "minus_1": ["-1"], "zero": ["0"]}
    others = {v for k, vs in markers.items() if k not in ("blank", "zero") for v in vs}
    no_value = r"(none/)?unknown( or missing)?|missing|not applicable|n/a"  # the whole meaning, not a word in it
    documented = documented_codes()
    rows = []
    for name, df in [("cohort", cohort), ("course", course)]:
        for col in df.columns:
            listed = documented.get((name, col), {})
            doc = {c for c, meaning in listed.items() if re.fullmatch(no_value, meaning.rstrip("."), re.IGNORECASE)}
            rows.append({"file": name, "column": col, **{k: df[col].isin(v).sum() for k, v in markers.items()},
                         "documented_unknown": "; ".join(f"{c} = {listed[c]}" for c in sorted(doc)),
                         "documented_unknown_cells": df[col].isin(doc).sum(),
                         "undocumented_markers": df[col].isin(others - doc).sum()})
    report = pd.DataFrame(rows)
    counts = [*markers, "documented_unknown_cells", "undocumented_markers"]
    total = report.file.map({"cohort": len(cohort), "course": len(course)})
    for k in counts:
        report[f"pct_{k}"] = (report[k] / total * 100).round(1)
    return report.sort_values(["file", "pct_blank"], ascending=[True, False])


def main(argv: list[str]) -> int:
    if "--missing" in argv:
        print(missing_report().to_string(index=False))
        return 0
    log = pd.read_csv(FINDINGS, dtype=str, keep_default_na=False)
    unchecked = set(log.id) ^ set(CHECKS)
    if unchecked:
        print(f"Findings and checks don't match one to one: {sorted(unchecked)}")
        return 1
    log["now"] = [int(CHECKS[i]()) for i in log.id]
    if "--update" in argv:
        log["count"] = log.pop("now").astype(str)
        log.to_csv(FINDINGS, index=False, lineterminator="\n")
        print(f"Updated {len(log)} counts in {FINDINGS.relative_to(ROOT).as_posix()}.")
        return 0
    changed = log[log["count"].astype(int) != log.now]
    for _, row in log.iterrows():
        print(f"{'OK ' if row.now == int(row['count']) else 'DIFF'} {row.id:>4}  {row.now:>7,}  {row.finding}")
    print(f"\n{len(log) - len(changed)} of {len(log)} counts match findings.csv.")
    return 1 if len(changed) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
