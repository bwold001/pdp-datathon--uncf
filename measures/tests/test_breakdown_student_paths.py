"""Checks the Student paths numbers against a tiny made-up database with known answers, plus the real data."""
from __future__ import annotations

import pytest

from measures.breakdowns.common import next_main_term, term_label
from measures.breakdowns.student_paths import college_kind, student_paths
from measures.models import GroupDimension
from measures.run_measures import DEFAULT_DATABASE
from measures.tests.explorer_fixture import ask, elsewhere, here, make_database, student


def fall_starters(prefix: str, count: int, *terms: str, **values: str) -> tuple[list[dict], list[dict]]:
    """count Fall 2023 starters and their records: terms gives each of their three terms as here, elsewhere or none."""
    students, records = [], []
    for n in range(count):
        student_id = f"{prefix}{n}"
        students.append(student(student_id, **values))
        for (year, season), status in zip([("2023-24", "FALL"), ("2023-24", "SPRING"), ("2024-25", "FALL")], terms):
            if status == "here":
                records.append(here(student_id, year, season))
            elif status.startswith("elsewhere"):
                carnegie = status.split(":", 1)[1] if ":" in status else "Doctoral Universities"
                records.append(elsewhere(student_id, year, season, carnegie))
    return students, records


COUNTS = ("here", "elsewhere", "anywhere", "stopped", "not_observed")


def counts(column: dict) -> dict:
    """A term's counts without its shares or the credential status, to compare with known answers."""
    return {key: column[key] for key in COUNTS}


def build(tmp_path, *groups):
    """A database from groups made by fall_starters."""
    students = [s for group in groups for s in group[0]]
    records = [r for group in groups for r in group[1]]
    return make_database(tmp_path / "pdp.sqlite", students, records)


def test_terms_follow_the_next_fall_or_spring():
    """Fall and winter lead to spring; spring and summer to the next fall. Names use the calendar year."""
    assert next_main_term(("2023-24", "FALL")) == ("2023-24", "SPRING")
    assert next_main_term(("2023-24", "WINTER")) == ("2023-24", "SPRING")
    assert next_main_term(("2023-24", "SPRING")) == ("2024-25", "FALL")
    assert next_main_term(("2023-24", "SUMMER")) == ("2024-25", "FALL")
    assert [term_label(t) for t in [("2023-24", "FALL"), ("2023-24", "SPRING"), ("2024-25", "FALL")]] == [
        "Fall 2023",
        "Spring 2024",
        "Fall 2024",
    ]


def test_college_kind_reads_cut_off_carnegie_classes():
    """Four-year and two-year classes, cut-off values, blanks and a mix of kinds."""
    assert college_kind("Doctoral Universities") == "four_year"
    assert college_kind("Master's Colleges & Universit") == "four_year"
    assert college_kind("Associate's Colleges|Associat") == "two_year"
    assert college_kind("Special Focus Two-Year") == "two_year"
    assert college_kind("Associate's Colleges|Doctoral Universities") == "other"
    assert college_kind("Tribal Colleges") == "other"
    assert college_kind(None) == "other"


def test_statuses_moves_and_transfers(tmp_path):
    """Each term's counts, the moves between the 2nd and 3rd term, returns, and where transfers went."""
    database = build(
        tmp_path,
        fall_starters("stay", 12, "here", "here", "here"),
        fall_starters("back", 10, "here", "none", "here"),
        fall_starters("away", 10, "here", "elsewhere", "elsewhere:Associate's Colleges"),
        fall_starters("left", 3, "here", "here", "none"),
    )
    paths = student_paths(**ask("2023-24"), database=database)
    assert paths["status"] == "ok"
    assert paths["students"] == 35
    assert paths["context"]["terms"] == {"entered": "Fall 2023", "next": "Spring 2024", "year2": "Fall 2024"}
    assert counts(paths["columns"]["next"]) == {"here": 15, "elsewhere": 10, "anywhere": 25, "stopped": 10, "not_observed": 0}
    # 3 stopped out by year 2: hidden, never 0.
    assert counts(paths["columns"]["year2"]) == {"here": 22, "elsewhere": 10, "anywhere": 32, "stopped": None, "not_observed": 0}
    moves = {(m["from"], m["to"]): m["students"] for m in paths["moves"]}
    assert moves[("here", "here")] == 12
    assert moves[("stopped", "here")] == 10
    assert moves[("elsewhere", "elsewhere")] == 10
    assert moves[("here", "stopped")] is None
    assert moves[("here", "elsewhere")] == 0
    assert paths["transfers"] == {"students": 10, "four_year": 0, "two_year": 10, "other": 0}


def test_enrollment_type_is_a_filter_and_filters_combine(tmp_path):
    """Every enrollment type is followed unless the filter picks one, and the cohort bar's filters combine with AND."""
    database = build(
        tmp_path,
        fall_starters("pell", 12, "here", "here", "here", pell="Y"),
        fall_starters("nopell", 11, "here", "here", "here", pell="N"),
        fall_starters("transfer", 15, "here", "here", "here", enrollment_type="Transfer-In"),
    )
    assert student_paths(**ask("2023-24"), database=database)["students"] == 38
    assert student_paths(**ask("2023-24", enrollment_type="First-time"), database=database)["students"] == 23
    assert student_paths(**ask("2023-24", pell="Y"), database=database)["students"] == 27
    assert student_paths(**ask("2023-24", pell="Y", enrollment_type="First-time"), database=database)["students"] == 12
    assert student_paths(**ask("2023-24", pell="N", gender="M"), database=database)["status"] == "suppressed"


def test_fewer_than_ten_students_hides_everything(tmp_path):
    """Nine students: no numbers at all, not even the count."""
    database = build(tmp_path, fall_starters("few", 9, "here", "here", "here"))
    paths = student_paths(**ask("2023-24"), database=database)
    assert paths["status"] == "suppressed"
    assert paths["students"] is None
    assert paths["columns"] is None


def test_course_here_counts_even_when_also_elsewhere(tmp_path):
    """A student with a course here and enrollment elsewhere in the same term counts as here."""
    students, records = fall_starters("both", 10, "here", "here", "here")
    records += [elsewhere(s["student_id"], "2023-24", "SPRING") for s in students]
    paths = student_paths(**ask("2023-24"), database=make_database(tmp_path / "pdp.sqlite", students, records))
    assert paths["columns"]["next"]["here"] == 10
    assert paths["columns"]["next"]["elsewhere"] == 0


def test_mixed_start_terms_and_terms_not_yet_in_the_data(tmp_path):
    """With fall and spring starters, terms aren't named; a term with no rows yet is counted apart."""
    students, records = fall_starters("fall", 10, "here", "here", "here")
    for n in range(10):
        # Spring 2024 starters: next term Fall 2024 is in the data, Spring 2025 (their third) isn't.
        students.append(student(f"spring{n}", cohort_term="SPRING"))
        records.append(here(f"spring{n}", "2023-24", "SPRING"))
    paths = student_paths(**ask("2023-24"), database=make_database(tmp_path / "pdp.sqlite", students, records))
    assert paths["context"]["terms"] is None
    assert paths["columns"]["next"]["here"] == 10  # the fall starters in Spring 2024
    assert paths["columns"]["next"]["stopped"] == 10  # the spring starters, no record in Fall 2024
    assert paths["columns"]["year2"]["not_observed"] == 10


def test_shares_and_retention_by_type(tmp_path):
    """Each term's shares of the class, and retention from the shared metrics by the chosen type."""
    stay = fall_starters("stay", 12, "here", "here", "here", retention=1)
    left = fall_starters("left", 13, "here", "none", "none", retention=0)
    database = build(tmp_path, stay, left)
    paths = student_paths(**ask("2023-24"), database=database)
    assert paths["columns"]["year2"]["shares"]["here"] == 0.48
    assert (paths["retention"]["type"], paths["retention"]["retained"], paths["retention"]["students"]) == ("school", 12, 25)
    federal = student_paths(**ask("2023-24", "federal"), database=database)["retention"]
    assert (federal["type"], federal["retained"], federal["students"]) == ("federal", 12, 25)


def test_credential_earned_counts_from_the_next_year(tmp_path):
    """A student who earned a credential here in year 1 and isn't here in year 2 is credential, not stopped."""
    done = fall_starters("done", 10, "here", "here", "none", credential_year=1)
    stay = fall_starters("stay", 10, "here", "here", "here")
    paths = student_paths(**ask("2023-24"), database=build(tmp_path, done, stay))
    assert paths["columns"]["next"]["credential"] == 0  # still in year 1
    assert paths["columns"]["year2"]["credential"] == 10
    assert paths["columns"]["year2"]["stopped"] == 0


def test_more_terms_and_group_breakdowns(tmp_path):
    """terms follows students further; group_by gives each value's own path, small groups hidden."""
    pell = fall_starters("pell", 12, "here", "here", "here", pell="Y")
    nopell = fall_starters("nopell", 5, "here", "here", "here", pell="N")
    paths = student_paths(**ask("2023-24"), terms=4, group_by=GroupDimension.PELL, database=build(tmp_path, pell, nopell))
    assert [column["position"] for column in paths["path"]] == [1, 2, 3]
    assert paths["path"][2]["not_observed"] == 17  # Spring 2025 isn't in the data
    groups = {group["value"]: group for group in paths["groups"]}
    assert groups["Y"]["students"] == 12
    assert groups["N"]["students"] is None
    with pytest.raises(ValueError):
        student_paths(**ask("2023-24"), terms=9, database=build(tmp_path / "..", pell))


@pytest.mark.slow
@pytest.mark.skipif(not DEFAULT_DATABASE.exists(), reason="the normalized data isn't loaded")
def test_real_data_known_answers():
    """2023-24 first-time Fall starters, checked by hand with SQL on pdp.sqlite (synthetic data)."""
    paths = student_paths(**ask("2023-24", cohort_term="Fall", enrollment_type="First-time"))
    assert paths["students"] == 1114
    assert paths["columns"]["next"]["here"] == 642
    assert paths["columns"]["next"]["elsewhere"] == 33
    assert paths["columns"]["year2"]["here"] == 522
    # 27 earned a credential here in year 1 and aren't here in Fall 2024: 4 were elsewhere, 23 had no record.
    assert paths["columns"]["year2"]["credential"] == 27
    assert paths["columns"]["year2"]["elsewhere"] == 60
    assert paths["columns"]["year2"]["stopped"] == 505
