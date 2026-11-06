"""Checks the validator: modes, run id, report, failed records and the full mock data."""

import builtins
import csv
import hashlib
import shutil
from pathlib import Path

import pytest
import yaml

from src.fixer.fix import fix
from src.mapper.map import map_files
from src.validator import validate as v
from src.validator.validate import validate

BUILD = Path(__file__).resolve().parents[2]
CONFIG = BUILD / "config"
SAMPLE = BUILD / "data/input/sample"
AR = dict(cohort_config=CONFIG / "cohort_mapping.yaml", course_config=CONFIG / "course_mapping.yaml")


def read(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def staged(tmp_path, run_id="r", **files):
    """Map and fix the files into tmp_path/staging/<run_id>/, as the steps before the validator do."""
    map_files(**files, config_dir=CONFIG, staging_dir=tmp_path / "staging", run_id=run_id)
    fix(tmp_path / "staging" / run_id, config_dir=CONFIG, fixes=CONFIG / "data_fixes.yaml")
    return tmp_path / "staging" / run_id


def write(path, rows):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return path


@pytest.fixture
def broken_files(tmp_path):
    """Sample rows with one error and one warning planted in each file."""
    cohort, course = read(SAMPLE / "pdp_cohort_data.csv"), read(SAMPLE / "pdp_course_data.csv")
    bad_student = cohort[1]["Student_GUID"]
    cohort[1]["Student_GUID"] = "not-a-guid"                        # error: pattern
    cohort[2]["Pell_Status_First_Year"] = "U"                       # warning: yes_no
    graded = next(i for i, r in enumerate(course) if r["Number_of_Credits_Attempted"] not in (".", ""))
    course[graded]["Number_of_Credits_Earned"] = "25"               # error: maximum 20
    orphan = next(i for i, r in enumerate(course) if r["Student_GUID"] == bad_student)
    return {"cohort": write(tmp_path / "cohort.csv", cohort), "course": write(tmp_path / "course.csv", course),
            "graded_row": graded + 1, "orphan_row": orphan + 1, "course_rows": len(course), "cohort_rows": len(cohort)}


def test_only_public_api_is_validate():
    public = [n for n, f in vars(v).items() if not n.startswith("_") and callable(f)
              and getattr(f, "__module__", None) == v.__name__]
    assert public == ["validate"]
    assert v.__all__ == ["validate"]


# Module

def test_a_clean_run_passes_every_row(tmp_path):
    summary = validate(staged(tmp_path, cohort=SAMPLE / "pdp_cohort_data.csv", course=SAMPLE / "pdp_course_data.csv", **AR), config_dir=CONFIG, logs_dir=tmp_path)
    for name, result in summary["results"].items():
        assert result["rows_failed"] == 0, name
        assert len(summary["passed_rows"][name]) == result["rows_read"]
    assert summary["failed_records"] is None


def test_error_rows_are_held_back_and_warning_rows_pass(tmp_path, broken_files):
    f = broken_files
    summary = validate(staged(tmp_path, cohort=f["cohort"], course=f["course"], **AR), config_dir=CONFIG, logs_dir=tmp_path)
    cohort, course = summary["results"]["cohort.csv"], summary["results"]["course.csv"]
    assert cohort["rows_failed"] == 1 and 2 not in summary["passed_rows"]["cohort.csv"]
    assert 3 in summary["passed_rows"]["cohort.csv"]  # warning only
    assert cohort["failures"]["student.student_id#0 pattern"]["error"] == 1
    assert cohort["failures"]["cohort_membership.pell_status_first_year#0 value_set"]["warning"] == 1
    # The orphaned student's course rows fail must_exist, because its cohort row was held back.
    assert f["orphan_row"] not in summary["passed_rows"]["course.csv"]
    assert course["failures"]["student must_exist"]["error"] >= 1
    assert f["graded_row"] not in summary["passed_rows"]["course.csv"]


def test_a_blank_student_and_cohort_is_an_error(tmp_path):
    cohort = read(SAMPLE / "pdp_cohort_data.csv")
    cohort[1]["Student_GUID"] = cohort[1]["Cohort"] = ""
    summary = validate(staged(tmp_path, cohort=write(tmp_path / "cohort.csv", cohort), course=SAMPLE / "pdp_course_data.csv", **AR),
                       config_dir=CONFIG, logs_dir=tmp_path)
    failures = summary["results"]["cohort.csv"]["failures"]
    assert 2 not in summary["passed_rows"]["cohort.csv"]
    assert failures["student.student_id required"]["error"] == 1
    assert failures["cohort_membership.cohort required"]["error"] == 1


def test_a_used_run_id_is_rejected_before_anything_is_written(tmp_path, broken_files):
    f, run = broken_files, "20261025T000000Z-abcdef"
    validate(staged(tmp_path, cohort=f["cohort"], course=f["course"], **AR), config_dir=CONFIG, logs_dir=tmp_path, run_id=run)
    written = {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file() and run in str(p)}
    again = staged(tmp_path, "other", cohort=SAMPLE / "pdp_cohort_data.csv", course=SAMPLE / "pdp_course_data.csv", **AR)
    with pytest.raises(ValueError, match="already has a report"):
        validate(again, config_dir=CONFIG, logs_dir=tmp_path, run_id=run)
    assert {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file() and run in str(p)} == written


def test_report_and_failed_records_link_to_each_other(tmp_path, broken_files):
    f = broken_files
    summary = validate(staged(tmp_path, cohort=f["cohort"], course=f["course"], **AR), config_dir=CONFIG, logs_dir=tmp_path,
                       run_id="20261025T000000Z-abcdef")
    run = "20261025T000000Z-abcdef"
    failures = read(tmp_path / "validation_report" / run / "failures.csv")
    failed = read(tmp_path / "failed_records" / run / "cohort.csv") + read(tmp_path / "failed_records" / run / "course.csv")
    by_id = {r["failure_id"]: r for r in failures}
    assert all(r["run_id"] == run for r in failures + failed)
    for row in failed:
        for failure_id in row["failure_ids"].split("|"):
            line = by_id[failure_id]
            assert line["source_row_number"] == row["source_row_number"]
            assert (tmp_path / line["failed_record"]).name == line["source_file"]
    errors = [r for r in failures if r["severity"] == "error"]
    assert all(r["failed_record"] for r in errors)
    held = {(Path(r["failed_record"]).name, r["source_row_number"]) for r in errors}
    assert held == {(name, r["source_row_number"]) for name in ("cohort.csv", "course.csv")
                    for r in read(tmp_path / "failed_records" / run / name)}
    original = read(f["cohort"])[1]
    assert {k: failed[0][k] for k in original} == original  # the source row, unchanged


def test_summary_records_what_was_checked(tmp_path):
    summary = validate(staged(tmp_path, cohort=SAMPLE / "pdp_cohort_data.csv", course=SAMPLE / "pdp_course_data.csv", **AR), config_dir=CONFIG, logs_dir=tmp_path)
    written = yaml.safe_load(open(Path(summary["report"]) / "summary.yaml"))
    assert written["run_id"] == summary["run_id"] and written["started_at"] <= written["finished_at"]
    files = {Path(f["path"]).name: f for f in written["files"]}
    assert set(files) >= {"pdp_cohort_data.csv", "pdp_course_data.csv", "destination_schema.yaml",
                          "value_sets.yaml", "cohort_mapping.yaml", "course_mapping.yaml"}
    for f in files.values():
        assert f["sha256"] == hashlib.sha256(Path(f["path"]).read_bytes()).hexdigest()
    assert files["pdp_course_data.csv"]["role"] == "input" and files["value_sets.yaml"]["role"] == "config"


def test_summary_counts_repairs_unknowns_and_no_values_apart(tmp_path):
    cohort = read(SAMPLE / "pdp_cohort_data.csv")
    cohort[0]["Race"] = "American Indian or Alaska"
    cohort[0]["GPA_Group_Term_1"] = "UK"
    cohort[1]["GPA_Group_Term_1"] = ""
    path = write(tmp_path / "cohort.csv", cohort)
    summary = validate(staged(tmp_path, cohort=path, course=SAMPLE / "pdp_course_data.csv", **AR), config_dir=CONFIG, logs_dir=tmp_path)
    result = summary["results"]["cohort.csv"]
    assert result["fixes"]["changed"]["race_cut_at_25_characters"] >= 1  # a mock-data fix, not a mapping repair
    assert result["unknown"]["cohort_membership.gpa_group_term_1"] >= 1
    assert result["no_value"]["cohort_membership.gpa_group_term_1"] >= 1


def test_enrichment_mode_does_not_check_foreign_keys(tmp_path):
    housing = read(BUILD / "data/input/enrichment/on_campus_housing.csv")[:5]
    housing[0]["Student_GUID"] = "F" * 32  # no such student
    path = write(tmp_path / "housing.csv", housing)
    summary = validate(staged(tmp_path, enrichment=path, enrichment_config=CONFIG / "on_campus_housing_mapping.yaml"),
                       config_dir=CONFIG, logs_dir=tmp_path)
    assert summary["results"]["housing.csv"]["rows_failed"] == 0
    assert summary["foreign_keys"].startswith("not checked")


def test_enrichment_rules_run(tmp_path):
    events = read(BUILD / "data/input/enrichment/institution_events.csv")
    events[0]["End_Date"] = "20251001"  # before its start date
    events[1]["Event_Type"] = "parade"  # a new type: loads, with a warning
    events.append(dict(events[1], Event_Type="Pow Wow", Event_Name="Malformed type"))  # held back
    path = write(tmp_path / "events.csv", events)
    summary = validate(staged(tmp_path, enrichment=path, enrichment_config=CONFIG / "institution_events_mapping.yaml"),
                       config_dir=CONFIG, logs_dir=tmp_path)
    failures = summary["results"]["events.csv"]["failures"]
    assert failures["institution_event.end_date#0 not_before"]["error"] == 1
    assert failures["institution_event.event_type#0 pattern"]["error"] == 1
    assert failures["institution_event.event_type#1 value_set"]["warning"] == 2
    assert summary["results"]["events.csv"]["rows_failed"] == 2


def test_summary_says_which_rule_failed_on_which_field_and_why(tmp_path):
    housing = read(BUILD / "data/input/enrichment/on_campus_housing.csv")[:8]
    for row in housing[:7]:
        row["Uses_On_Campus_Housing"] = "maybe"
    path = write(tmp_path / "housing.csv", housing)
    summary = validate(staged(tmp_path, enrichment=path, enrichment_config=CONFIG / "on_campus_housing_mapping.yaml"),
                       config_dir=CONFIG, logs_dir=tmp_path)
    written = yaml.safe_load(open(Path(summary["report"]) / "summary.yaml"))
    assert written["results"]["housing.csv"]["failures"]["student_attribute.attribute_value#0 enum"] == {
        "error": 7, "field": "student_attribute.attribute_value", "source_column": "Uses_On_Campus_Housing",
        "why": "must be one of true, false, when attribute_key is uses_on_campus_housing",
        "examples": [{"source_row": n, "value": "maybe"} for n in range(1, 6)]}  # the first 5; failures.csv has all 7


def test_summary_explains_a_failure_that_isnt_a_schema_rule(tmp_path, broken_files):
    f = broken_files
    summary = validate(staged(tmp_path, cohort=f["cohort"], course=f["course"], **AR), config_dir=CONFIG, logs_dir=tmp_path)
    failure = summary["results"]["course.csv"]["failures"]["student must_exist"]
    assert failure["field"] == "student.student_id" and failure["source_column"] == "Student_GUID"
    assert failure["why"] == "must already be in student, written by another file in the same run"


def test_a_bad_config_stops_before_reading_data(tmp_path):
    staging = staged(tmp_path, enrichment=BUILD / "data/input/enrichment/on_campus_housing.csv",
                     enrichment_config=CONFIG / "on_campus_housing_mapping.yaml")
    bad = tmp_path / "config"
    bad.mkdir()
    (bad / "destination_schema.yaml").write_text("t: {a: {type: text, nullable: true}}\n")
    with pytest.raises(v.ConfigError):
        validate(staging, config_dir=bad, logs_dir=tmp_path)
    assert not (tmp_path / "validation_report").exists()


def test_a_run_the_fixer_hasnt_fixed_is_refused(tmp_path):
    map_files(**AR, cohort=SAMPLE / "pdp_cohort_data.csv", course=SAMPLE / "pdp_course_data.csv",
              config_dir=CONFIG, staging_dir=tmp_path / "staging", run_id="r")
    with pytest.raises(ValueError, match="run the Fixer first"):
        validate(tmp_path / "staging/r", config_dir=CONFIG, logs_dir=tmp_path)
    assert not (tmp_path / "validation_report").exists()
    assert not (tmp_path / "staging/r/validated").exists()


def test_tables_the_fixer_didnt_write_are_refused(tmp_path):
    staging = tmp_path / "staging"
    files = dict(AR, cohort=SAMPLE / "pdp_cohort_data.csv", course=SAMPLE / "pdp_course_data.csv")
    map_files(**files, config_dir=CONFIG, staging_dir=staging, run_id="copied")
    shutil.copytree(staging / "copied/mapped", staging / "copied/fixed")  # by hand, with no Fixer
    with pytest.raises(ValueError, match="run the Fixer first"):
        validate(staging / "copied", config_dir=CONFIG, logs_dir=tmp_path / "logs")
    map_files(**files, config_dir=CONFIG, staging_dir=staging, run_id="half")
    fix(staging / "half", ["pdp_cohort_data.csv"], config_dir=CONFIG, fixes=CONFIG / "data_fixes.yaml")
    shutil.copytree(staging / "half/mapped/pdp_course_data.csv", staging / "half/fixed/pdp_course_data.csv")
    with pytest.raises(ValueError, match="pdp_course_data.csv that the Fixer didn't write"):
        validate(staging / "half", config_dir=CONFIG, logs_dir=tmp_path / "logs")
    assert not (tmp_path / "logs").exists()


def test_a_mapped_source_the_fixer_hasnt_fixed_is_refused(tmp_path):
    """The cohort and course files are checked together, so one fixed without the other is refused."""
    staging = tmp_path / "staging"
    map_files(**AR, cohort=SAMPLE / "pdp_cohort_data.csv", course=SAMPLE / "pdp_course_data.csv",
              config_dir=CONFIG, staging_dir=staging, run_id="r")
    fix(staging / "r", ["pdp_cohort_data.csv"], config_dir=CONFIG, fixes=CONFIG / "data_fixes.yaml")
    with pytest.raises(ValueError, match="pdp_course_data.csv mapped too"):
        validate(staging / "r", config_dir=CONFIG, logs_dir=tmp_path / "logs")
    assert not (tmp_path / "logs").exists()


def test_failures_show_the_value_checked_and_failed_records_the_files_row(tmp_path):
    fixes = tmp_path / "fixes.yaml"
    fixes.write_text(yaml.safe_dump({"fixes": [{"name": "f_becomes_q", "bug": "a test", "decision": "a test",
                                                "enabled": True, "table": "student", "column": "gender",
                                                "replace": {"F": "Q"}}]}))
    map_files(**AR, cohort=SAMPLE / "pdp_cohort_data.csv", course=SAMPLE / "pdp_course_data.csv",
              config_dir=CONFIG, staging_dir=tmp_path / "staging", run_id="r")
    fix(tmp_path / "staging/r", config_dir=CONFIG, fixes=fixes)
    validate(tmp_path / "staging/r", config_dir=CONFIG, logs_dir=tmp_path / "logs")
    failures = [f for f in read(tmp_path / "logs/validation_report/r/failures.csv") if f["rule"] == "student.gender#0 enum"]
    assert failures and {f["value"] for f in failures} == {"Q"}  # what the rule checked, after the fix
    failed = read(tmp_path / "logs/failed_records/r/pdp_cohort_data.csv")
    assert failed and {r["Gender"] for r in failed} == {"F"}  # the file's own row, as it wrote it


def test_a_clean_run_reads_the_source_file_only_for_its_sha256(tmp_path, monkeypatch):
    cohort = SAMPLE / "pdp_cohort_data.csv"
    staging = staged(tmp_path, cohort=cohort, course=SAMPLE / "pdp_course_data.csv", **AR)
    opened, real_open = [], builtins.open
    monkeypatch.setattr(builtins, "open", lambda path, *a, **k: opened.append(Path(path)) or real_open(path, *a, **k))
    summary = validate(staging, config_dir=CONFIG, logs_dir=tmp_path / "logs")
    assert summary["results"]["pdp_cohort_data.csv"]["rows_failed"] == 0
    assert [p for p in opened if p.resolve() == cohort.resolve()] == [cohort]


# End to end

# Rows that break each column's rules in the full mock data, counted by hand from the raw files.
EXPECTED = {
    "student.student_age": 0, "student.race": 0, "student.ethnicity": 0,
    "course_enrollment.math_or_english_gateway": 0,  # NA is fixed to N before the check
    "course_enrollment.course_cip": 2276,  # such as 24, 24.01 or 09.01; 2,342 rows get zeros back first, and 401 of them (09.01, 45.10, 01) still warn
    "course_enrollment.course_instructor_rank": 77800, "course_enrollment.course_begin_date": 0,
    "course_enrollment.course_end_date": 0, "course_enrollment.number_of_credits_attempted": 0,
    "course_enrollment.number_of_credits_earned": 0, "course.course_prefix": 0, "course.course_number": 0,
    "course_enrollment.course_name": 0,
}


@pytest.mark.slow
def test_full_mock_data_matches_the_field_audit(tmp_path):
    summary = validate(staged(tmp_path, cohort=BUILD.parent / "data/raw/pdp_cohort_data.csv",
                              course=BUILD.parent / "data/raw/pdp_course_data.csv", **AR),
                       config_dir=CONFIG, logs_dir=tmp_path)
    course = summary["results"]["pdp_course_data.csv"]
    counts = {column: sum(c.get("error", 0) + c.get("warning", 0) for rule, c in course["failures"].items() if rule.startswith(column + "#")
                          or rule.startswith(column + " "))
              for column in EXPECTED}
    assert counts == EXPECTED
    fixed = lambda name: summary["results"][name]["fixes"]["changed"]
    assert fixed("pdp_course_data.csv") == {"race_cut_at_25_characters": 1798, "gateway_na_is_n": 75504,
                                            "cip_lost_its_zeros": 1239, "cip_lost_its_trailing_zero": 702,
                                            "cip_series_lost_its_zeros": 332, "cip_family_lost_its_zero": 69,
                                            "term_program_of_study_lost_its_zero": 605}
    assert fixed("pdp_cohort_data.csv") == {"race_cut_at_25_characters": 225, "credential_labels_are_codes": 9678,
                                            "program_of_study_term_1_lost_its_zero": 96,
                                            "program_of_study_year_1_lost_its_zero": 113,
                                            "dev_math_completion_is_c_d": 969, "dev_english_completion_is_c_d": 688,
                                            "future_credit_years_are_blank": 2 * (2520 + 5039)}
    credits = summary["results"]["pdp_cohort_data.csv"]["fixes"]["details"]["future_credit_years_are_blank"]
    assert credits["blanked"] == {f"number_of_credits_{kind}_yr_{year}": count for kind in ("attempted", "earned")
                                  for year, count in ((3, 2520), (4, 5039))}
    assert credits["kept_because_not_zero"] == [] and credits["cohort_not_a_year"] == 0
    assert course["repairs"] == {}  # no mapping repairs any more: they're fixes
    with open(BUILD.parent / "data/raw/pdp_cohort_data.csv", newline="") as f:  # labels with no code stay, and warn
        uncoded = sum(r["Credential_Type_Sought_Year_1"] in ("Degree Seeking(N)", "Degree Seeking(Y)") for r in csv.DictReader(f))
    credential = summary["results"]["pdp_cohort_data.csv"]["failures"]["cohort_membership.credential_type_sought_year_1#0 enum"]
    assert uncoded == 240 and credential["warning"] == uncoded


def test_command_line_end_to_end(tmp_path, capsys):
    staging = staged(tmp_path, cohort=SAMPLE / "pdp_cohort_data.csv", course=SAMPLE / "pdp_course_data.csv", **AR)
    code = v._main(["--staging", str(staging), "--config_dir", str(CONFIG), "--logs_dir", str(tmp_path),
                    "--run_id", "20261025T000000Z-000001"])
    out = capsys.readouterr().out
    assert code == 0
    assert "run id: 20261025T000000Z-000001" in out
    assert (tmp_path / "validation_report/20261025T000000Z-000001/summary.yaml").exists()


def test_command_line_exits_2_on_a_bad_config(tmp_path, capsys):
    staging = staged(tmp_path, enrichment=BUILD / "data/input/enrichment/on_campus_housing.csv",
                     enrichment_config=CONFIG / "on_campus_housing_mapping.yaml")
    bad = tmp_path / "config"
    bad.mkdir()
    (bad / "destination_schema.yaml").write_text("t: {a: {type: text, nullable: true}}\n")
    code = v._main(["--staging", str(staging), "--config_dir", str(bad), "--logs_dir", str(tmp_path)])
    assert code == 2
    assert "invalid config" in capsys.readouterr().err
