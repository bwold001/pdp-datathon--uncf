"""Checks the Fixer: what it changes, what it reports, and the fixes file's format."""

import csv
import sqlite3
from pathlib import Path

import pytest
import yaml

from src.fixer import fix as fx
from src.fixer.fix import fix, load_fixes
from src.mapper.map import map_files
from src.pipeline.run import run
from src.rules.rules import ConfigError, load_rules
from src.validator.validate import validate

BUILD = Path(__file__).resolve().parents[2]
CONFIG = BUILD / "config"
SAMPLE = BUILD / "data/input/sample"
AR = {"cohort": SAMPLE / "pdp_cohort_data.csv", "course": SAMPLE / "pdp_course_data.csv",
      "cohort_config": CONFIG / "cohort_mapping.yaml", "course_config": CONFIG / "course_mapping.yaml"}
SCHEMA = load_rules(CONFIG)["schema"]
FIXES = yaml.safe_load((CONFIG / "data_fixes.yaml").read_text())["fixes"]


def staged(tmp_path, run_id="r"):
    """The sample files mapped into tmp_path/staging/<run_id>/, with one cut Race label planted in each."""
    files = dict(AR)
    for kind in ("cohort", "course"):
        rows = list(csv.DictReader(open(AR[kind], newline="")))
        rows[0]["Race"] = "American Indian or Alaska"
        files[kind] = tmp_path / AR[kind].name
        with open(files[kind], "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    map_files(**files, config_dir=CONFIG, staging_dir=tmp_path / "staging", run_id=run_id)
    return tmp_path / "staging" / run_id


def column(folder, table, name):
    with open(folder / f"{table}.csv", newline="") as f:
        return [row[name] for row in csv.DictReader(f)]


def fixes_file(tmp_path, fixes):
    path = tmp_path / "fixes.yaml"
    path.write_text(yaml.safe_dump({"fixes": fixes}, sort_keys=False))
    return path


def test_only_public_api_is_fix_and_load_fixes():
    assert fx.__all__ == ["fix", "load_fixes"]


def test_every_fix_names_its_bug_and_its_decision():
    for entry in FIXES:
        assert entry["bug"].startswith("https://docs.google.com/document/"), entry["name"]
        assert entry["decision"], entry["name"]


def test_fixed_has_the_same_layout_plus_what_each_fix_changed(tmp_path):
    staging = staged(tmp_path)
    result = fix(staging, config_dir=CONFIG, fixes=CONFIG / "data_fixes.yaml")
    for name in ("pdp_cohort_data.csv", "pdp_course_data.csv"):
        mapped, fixed = staging / "mapped" / name, staging / "fixed" / name
        assert {p.name for p in fixed.iterdir()} == {p.name for p in mapped.iterdir()} | {"fixes.yaml"}
        assert (fixed / "source.yaml").read_text() == (mapped / "source.yaml").read_text()
    for name in ("pdp_cohort_data.csv", "pdp_course_data.csv"):
        report = yaml.safe_load((staging / "fixed" / name / "fixes.yaml").read_text())
        assert report["changed"]["race_cut_at_25_characters"] == 1 and "race_cut_at_25_characters" not in report["changed_nothing"]
        assert column(staging / "fixed" / name, "student", "race")[0] == "American Indian or Alaska Native"
        assert column(staging / "mapped" / name, "student", "race")[0] == "American Indian or Alaska"  # mapped/ is kept
    assert result["changed"]["race_cut_at_25_characters"] == 2


def test_a_switched_off_fix_changes_nothing(tmp_path):
    staging = staged(tmp_path)
    off = [dict(f, enabled=False) if f["name"] == "race_cut_at_25_characters" else f for f in FIXES]
    result = fix(staging, config_dir=CONFIG, fixes=fixes_file(tmp_path, off))
    assert "race_cut_at_25_characters" not in result["changed"]
    assert column(staging / "fixed/pdp_course_data.csv", "student", "race") == \
        column(staging / "mapped/pdp_course_data.csv", "student", "race")


def test_a_fix_that_changes_nothing_is_listed(tmp_path):
    staging = staged(tmp_path)
    stale = FIXES + [{"name": "stale", "bug": "https://docs.google.com/document/x", "decision": "test", "enabled": True,
                      "table": "student", "column": "gender", "replace": {"no such value": "F"}}]
    fix(staging, config_dir=CONFIG, fixes=fixes_file(tmp_path, stale))
    report = yaml.safe_load((staging / "fixed/pdp_cohort_data.csv/fixes.yaml").read_text())
    assert report["changed"]["stale"] == 0 and "stale" in report["changed_nothing"]


def test_a_source_already_fixed_is_refused(tmp_path):
    staging = staged(tmp_path)
    fix(staging, config_dir=CONFIG, fixes=CONFIG / "data_fixes.yaml")
    with pytest.raises(ValueError, match="already fixed"):
        fix(staging, config_dir=CONFIG, fixes=CONFIG / "data_fixes.yaml")


@pytest.mark.parametrize("change,message", [
    ({"enabled": "yes"}, "enabled must be true or false"),
    ({"bug": ""}, "bug must say where it comes from"),
    ({"column": "nope"}, "no column student.nope"),
    ({"table": "nope"}, "no column nope.race"),
    ({"replace": []}, "replace must map old values to new ones"),
    ({"multiply": 2}, "unknown properties"),
])
def test_a_bad_fix_is_a_config_error(tmp_path, change, message):
    entry = dict(FIXES[0], **change)
    with pytest.raises(ConfigError, match=message):
        load_fixes(fixes_file(tmp_path, [entry]), SCHEMA)


@pytest.mark.parametrize("key", ["bug", "decision"])
def test_a_fix_without_its_bug_or_decision_is_a_config_error(tmp_path, key):
    entry = {k: v for k, v in FIXES[0].items() if k != key}
    with pytest.raises(ConfigError, match=f"needs \\['{key}'\\]"):
        load_fixes(fixes_file(tmp_path, [entry]), SCHEMA)


def test_the_command_line_exits_2_on_an_invalid_fixes_file(tmp_path, capsys):
    staging = staged(tmp_path)
    bad = fixes_file(tmp_path, [dict(FIXES[0], column="nope")])
    assert fx._main(["--staging", str(staging), "--config_dir", str(CONFIG), "--fixes", str(bad)]) == 2
    assert "no column student.nope" in capsys.readouterr().err
    assert not (staging / "fixed").exists()


def test_a_fix_with_no_kind_or_a_missing_field_is_a_config_error(tmp_path):
    entry = {k: v for k, v in FIXES[0].items() if k not in ("replace", "decision")}
    with pytest.raises(ConfigError, match="needs \\['decision'\\][\\s\\S]*exactly one kind"):
        load_fixes(fixes_file(tmp_path, [entry]), SCHEMA)


def test_a_team_names_its_own_copy_in_its_settings(tmp_path):
    own = FIXES + [{"name": "gender_f_is_female", "bug": "https://docs.google.com/document/x", "decision": "a team's own",
                    "enabled": True, "table": "student", "column": "gender", "replace": {"F": "Female"}}]
    sources = [{"kind": k, "path": str(AR[k]), "config": f"{k}_mapping.yaml", "provider": "test"} for k in ("cohort", "course")]
    (tmp_path / "pipeline.yaml").write_text(yaml.safe_dump({
        "backend": "sqlite", "sqlite": {"path": str(tmp_path / "pdp.sqlite")}, "logs_dir": str(tmp_path / "logs"),
        "staging_dir": str(tmp_path / "staging"), "tables": {"path": str(tmp_path / "tables")}, "fixes": str(fixes_file(tmp_path, own)), "sources": sources}))
    summary = run(tmp_path / "pipeline.yaml", run_id="r")
    raw = [r for kind in ("cohort", "course") for r in csv.DictReader(open(AR[kind]))]
    assert summary["fixes"]["gender_f_is_female"] == sum(r["Gender"] == "F" for r in raw)  # both files write gender
    # Female isn't a gender code, so the rule holds those students back: the team's fix is checked like any value.
    gender = {g for (g,) in sqlite3.connect(tmp_path / "pdp.sqlite").execute("SELECT DISTINCT gender FROM student")}
    assert "F" not in gender


def test_gateway_na_becomes_n_and_credential_labels_become_codes(tmp_path):
    staging = staged(tmp_path)
    result = fix(staging, config_dir=CONFIG, fixes=CONFIG / "data_fixes.yaml")
    course = list(csv.DictReader(open(SAMPLE / "pdp_course_data.csv")))
    assert result["changed"]["gateway_na_is_n"] == sum(r["Math_or_English_Gateway"] == "NA" for r in course)
    gateway = column(staging / "fixed/pdp_course_data.csv", "course_enrollment", "math_or_english_gateway")
    assert set(gateway) <= {"M", "E", "N", ""}
    assert {v for v, r in zip(gateway, course) if r["Math_or_English_Gateway"] == "NA"} == {"N"}
    codes = next(f for f in FIXES if f["name"] == "credential_labels_are_codes")["replace"]
    cohort = list(csv.DictReader(open(SAMPLE / "pdp_cohort_data.csv")))
    assert result["changed"]["credential_labels_are_codes"] == sum(r["Credential_Type_Sought_Year_1"] in codes for r in cohort)
    fixed = column(staging / "fixed/pdp_cohort_data.csv", "cohort_membership", "credential_type_sought_year_1")
    assert [v for v, r in zip(fixed, cohort) if r["Credential_Type_Sought_Year_1"] in codes] == \
        [codes[r["Credential_Type_Sought_Year_1"]] for r in cohort if r["Credential_Type_Sought_Year_1"] in codes]


def test_codes_written_as_numbers_get_their_zeros_back_and_dev_completion_becomes_c_or_d(tmp_path):
    files = dict(AR)
    planted = {"cohort": [{"Program_of_Study_Term_1": "90702", "CompletedDevMathY1": "Y", "CompletedDevEnglishY1": "N"}],
               "course": [{"Course_CIP": c} for c in ("5.0202", "24.01", "24", "24.0101", "13.121", "9.01", "45.1", "1")]}
    for kind, changes in planted.items():
        rows = list(csv.DictReader(open(AR[kind], newline="")))
        for row, change in zip(rows, changes):
            row.update(change)
        files[kind] = tmp_path / AR[kind].name
        with open(files[kind], "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    map_files(**files, config_dir=CONFIG, staging_dir=tmp_path / "staging", run_id="r")
    result = fix(tmp_path / "staging/r", config_dir=CONFIG, fixes=CONFIG / "data_fixes.yaml")
    cohort, course = tmp_path / "staging/r/fixed/pdp_cohort_data.csv", tmp_path / "staging/r/fixed/pdp_course_data.csv"
    assert column(cohort, "cohort_membership", "program_of_study_term_1")[0] == "090702"
    assert column(cohort, "cohort_membership", "completed_dev_math_y1")[0] == "C"
    assert column(cohort, "cohort_membership", "completed_dev_english_y1")[0] == "D"
    cips = column(course, "course_enrollment", "course_cip")
    assert cips[:8] == ["05.0202", "24.01", "24", "24.0101", "13.1210", "09.01", "45.10", "01"]  # only zeros read one way
    raw = [r["Course_CIP"] for r in csv.DictReader(open(files["course"], newline=""))]
    cip_fixes = ("cip_lost_its_zeros", "cip_lost_its_trailing_zero", "cip_series_lost_its_zeros", "cip_family_lost_its_zero")
    assert sum(result["changed"][n] for n in cip_fixes) == sum(a != b for a, b in zip(raw, cips))  # only real changes count


@pytest.mark.parametrize("spec, error", [({"match": "(", "format": "{:07.4f}"}, "number_format: missing \\)"),
                                         ({"match": None, "format": "{:07.4f}"}, "each a string"),
                                         ({"match": "[0-9]", "format": None}, "each a string")])
def test_a_bad_number_format_is_a_config_error(tmp_path, spec, error):
    entry = dict(next(f for f in FIXES if f["name"] == "cip_lost_its_zeros"), number_format=spec)
    with pytest.raises(ConfigError, match=error):
        load_fixes(fixes_file(tmp_path, [entry]), SCHEMA)


# The credential labels and the dictionary code each becomes, written out here rather than read from
# data_fixes.yaml, so a wrong code in that file fails this test. Where the dictionary gives a letter or a
# number for the same credential, the letter is used. Degree Seeking(N), Degree Seeking(Y) and UNKNOWN
# have no code and stay as written.
CREDENTIAL_CODES = {
    "Associate's Degree": "A",
    "Non Credential Program (Preparatory Coursework / Teach Certification)": "NC",
    "Less than 1-year certificate, less than Associates degree": "C1",
    "1-2 year certificate, less than Associates degree": "C2",
    "Non Credential Program (Preparatory Coursework / Teacher Certification)": "NC",
    "Bachelor's Degree": "B",
    "Graduate/Professional Certificate": "PC",
    "Undergraduate Certificate or Diploma Program": "01",
    "2-4 year certificate, less than Bachelors degree": "C4",
}


def test_each_credential_label_becomes_its_dictionary_code():
    entry = next(f for f in FIXES if f["name"] == "credential_labels_are_codes")
    assert entry["replace"] == CREDENTIAL_CODES
    assert (entry["table"], entry["column"]) == ("cohort_membership", "credential_type_sought_year_1")


def test_without_the_gateway_fix_its_na_rows_are_held_back(tmp_path):
    no_gateway = [f for f in FIXES if f["name"] != "gateway_na_is_n"]
    sources = [{"kind": k, "path": str(AR[k]), "config": f"{k}_mapping.yaml", "provider": "test"} for k in ("cohort", "course")]
    (tmp_path / "pipeline.yaml").write_text(yaml.safe_dump({
        "backend": "sqlite", "sqlite": {"path": str(tmp_path / "pdp.sqlite")}, "logs_dir": str(tmp_path / "logs"),
        "staging_dir": str(tmp_path / "staging"), "tables": {"path": str(tmp_path / "tables")}, "fixes": str(fixes_file(tmp_path, no_gateway)), "sources": sources}))
    summary = run(tmp_path / "pipeline.yaml", run_id="r")
    assert "gateway_na_is_n" not in summary["fixes"] and summary["fixes"]["credential_labels_are_codes"] > 0
    # Without that fix, NA isn't a code, so the gateway rule holds those course rows back.
    raw = list(csv.DictReader(open(SAMPLE / "pdp_course_data.csv")))
    assert summary["validation"]["pdp_course_data.csv"]["rows_failed"] == sum(r["Math_or_English_Gateway"] == "NA" for r in raw)
    gateway = {g for (g,) in sqlite3.connect(tmp_path / "pdp.sqlite").execute(
        "SELECT DISTINCT math_or_english_gateway FROM course_enrollment")}
    assert "NA" not in gateway


def cutoff_fix(**changes):
    entry = next(f for f in FIXES if f["name"] == "future_credit_years_are_blank")
    return dict(entry, blank_after_cutoff=dict(entry["blank_after_cutoff"], **changes))


def test_credit_years_after_the_cutoff_are_blank_and_counted_by_cohort(tmp_path):
    rows = list(csv.DictReader(open(SAMPLE / "pdp_cohort_data.csv")))
    fieldnames = list(rows[0])
    rows[0].update(Cohort="2024-25", Number_of_Credits_Attempted_Yr_3="0", Number_of_Credits_Attempted_Yr_4="6")
    path = tmp_path / "cohort.csv"
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    map_files(**dict(AR, cohort=path), config_dir=CONFIG, staging_dir=tmp_path / "staging", run_id="r")
    fix(tmp_path / "staging/r", config_dir=CONFIG, fixes=fixes_file(tmp_path, [cutoff_fix()]))
    folder = tmp_path / "staging/r/fixed/cohort.csv"
    with open(folder / "cohort_membership.csv", newline="") as f:
        first = next(csv.DictReader(f))
    assert (first["credit_years_observed"], first["number_of_credits_attempted_yr_3"]) == ("2", "")
    assert first["number_of_credits_attempted_yr_4"] == "6.0"  # not a 0, so kept, and listed
    details = yaml.safe_load((folder / "fixes.yaml").read_text())["details"]["future_credit_years_are_blank"]
    assert {"source_row": 1, "table": "cohort_membership", "column": "number_of_credits_attempted_yr_4",
            "value": 6.0} in details["kept_because_not_zero"]
    summary = validate(tmp_path / "staging/r", config_dir=CONFIG, logs_dir=tmp_path / "logs")  # loads, with a warning
    warned = [f for f in csv.DictReader(open(tmp_path / "logs/validation_report/r/failures.csv"))
              if "not 0 after the cutoff" in f["rule"]]
    assert [(w["source_file"], w["source_row_number"], w["destination_column"], w["value"], w["severity"]) for w in warned] \
        == [("cohort.csv", "1", "number_of_credits_attempted_yr_4", "6.0", "warning")]
    assert 1 in summary["passed_rows"]["cohort.csv"]
    observed = {(r["cohort"], r["credit_years_observed"]) for r in csv.DictReader(open(folder / "cohort_membership.csv"))}
    assert {c: o for c, o in observed} == {"2021-22": "4", "2022-23": "4", "2023-24": "3", "2024-25": "2"}


def test_a_cohort_that_isnt_a_year_is_left_for_the_validator(tmp_path):
    rows = [{"source_row": 1, "cohort": "UK", "number_of_credits_attempted_yr_4": 0.0}]
    count, details = fx._blank_after_cutoff(rows, "credit_years_observed", cutoff_fix()["blank_after_cutoff"],
                                            "cohort_membership")
    assert count == 0 and details["cohort_not_a_year"] == 1
    assert rows[0]["number_of_credits_attempted_yr_4"] == 0.0 and rows[0]["credit_years_observed"] is None


@pytest.mark.parametrize("cutoff,observed", [
    ("2024-25", {"2021-22": "4", "2022-23": "3", "2023-24": "2", "2024-25": "1"}),
    ("2022-23", {"2021-22": "2", "2022-23": "1", "2023-24": "0", "2024-25": "0"}),  # a cohort after the cutoff saw none
])
def test_the_cutoff_in_the_fixes_file_decides_the_years_observed(tmp_path, cutoff, observed):
    staging = staged(tmp_path)
    fix(staging, config_dir=CONFIG, fixes=fixes_file(tmp_path, [cutoff_fix(cutoff=cutoff)]))
    rows = list(csv.DictReader(open(staging / "fixed/pdp_cohort_data.csv/cohort_membership.csv", newline="")))
    assert {r["cohort"]: r["credit_years_observed"] for r in rows} == observed
    for r in rows:  # a year above it is blank wherever the file said 0
        assert all(r[f"number_of_credits_attempted_yr_{y}"] != "0.0" for y in range(int(observed[r["cohort"]]) + 1, 5))


def test_a_cohort_that_isnt_a_year_is_kept_by_the_fixer_and_failed_by_the_validator(tmp_path):
    rows = list(csv.DictReader(open(SAMPLE / "pdp_cohort_data.csv")))
    rows[0].update(Cohort="Fall 2024", Number_of_Credits_Attempted_Yr_4="0")
    path = tmp_path / "cohort.csv"
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    map_files(**dict(AR, cohort=path), config_dir=CONFIG, staging_dir=tmp_path / "staging", run_id="r")
    fix(tmp_path / "staging/r", config_dir=CONFIG, fixes=CONFIG / "data_fixes.yaml")
    first = next(csv.DictReader(open(tmp_path / "staging/r/fixed/cohort.csv/cohort_membership.csv", newline="")))
    assert (first["credit_years_observed"], first["number_of_credits_attempted_yr_4"]) == ("", "0.0")  # left alone
    summary = validate(tmp_path / "staging/r", config_dir=CONFIG, logs_dir=tmp_path / "logs")
    assert 1 not in summary["passed_rows"]["cohort.csv"]  # the validator's own rule fails the cohort
    assert summary["results"]["cohort.csv"]["failures"]["cohort_membership.cohort#0 academic_year"]["error"] == 1


def test_with_the_cutoff_fix_off_credit_years_observed_is_blank(tmp_path):
    staging = staged(tmp_path)
    fix(staging, config_dir=CONFIG, fixes=fixes_file(tmp_path, [dict(cutoff_fix(), enabled=False)]))
    with open(staging / "fixed/pdp_cohort_data.csv/cohort_membership.csv", newline="") as f:
        assert "credit_years_observed" not in next(csv.DictReader(f))


@pytest.mark.parametrize("change,message", [
    ({"cutoff": "2025"}, "cutoff must be an academic year"),
    ({"years": {"three": ["number_of_credits_attempted_yr_3"]}}, "years must map each year number"),
    ({"cohort_column": "nope"}, "no column \\['nope'\\]"),
])
def test_a_bad_cutoff_fix_is_a_config_error(tmp_path, change, message):
    with pytest.raises(ConfigError, match=message):
        load_fixes(fixes_file(tmp_path, [cutoff_fix(**change)]), SCHEMA)
