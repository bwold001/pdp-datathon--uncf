"""Checks the loader: settings, both databases, held-back rows, full refresh, rollback and the full mock data.

The PostgreSQL tests need a server. They run when PDP_TEST_POSTGRES_URL holds a connection URL to
a database the tests may create schemas in, and are skipped otherwise. Each test uses its own
schema and drops it afterwards.
"""

import csv
import os
import shutil
import sqlite3
from datetime import date, datetime
from pathlib import Path

import pytest
import yaml

from src.loader import backends
from src.loader import load as l
from src.loader.load import load
from src.rules.rules import ConfigError, check_value, load_rules

BUILD = Path(__file__).resolve().parents[2]
CONFIG = BUILD / "config"
SAMPLE = BUILD / "data/input/sample"
SAMPLE_OUTPUT = BUILD / "data/output/sample"
RAW = BUILD.parent / "data/raw"
RULES = load_rules(CONFIG)
SCHEMA, FOREIGN_KEYS = RULES["schema"], RULES["foreign_keys"]
POSTGRES_URL = os.environ.get("PDP_TEST_POSTGRES_URL")


def needs_postgres(test):
    """A PostgreSQL test: skipped without a server, and a failure when PDP_REQUIRE_POSTGRES=1 (see conftest.py)."""
    skip = pytest.mark.skipif(not POSTGRES_URL, reason="set PDP_TEST_POSTGRES_URL to run the PostgreSQL tests")
    return pytest.mark.postgres(skip(test))


def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return path


def sample_sources(cohort=SAMPLE / "pdp_cohort_data.csv", course=SAMPLE / "pdp_course_data.csv",
                   housing=SAMPLE / "enrichment/on_campus_housing.csv"):
    return [
        {"kind": "cohort", "path": str(cohort), "config": "cohort_mapping.yaml", "provider": "Achieving the Dream"},
        {"kind": "course", "path": str(course), "config": "course_mapping.yaml", "provider": "Achieving the Dream"},
        {"kind": "enrichment", "path": str(housing), "config": "on_campus_housing_mapping.yaml",
         "provider": "synthetic: on-campus housing generator"},
        {"kind": "enrichment", "path": str(SAMPLE / "enrichment/institution_events.csv"),
         "config": "institution_events_mapping.yaml", "provider": "public: institution events"},
    ]


def make_config(tmp_path, **changes):
    """A pipeline.yaml in tmp_path reading the sample files, with the database and logs in tmp_path."""
    settings = {"mode": "full_refresh", "backend": "sqlite", "sqlite": {"path": str(tmp_path / "output/pdp.sqlite")},
                "postgres": {"url_env": "PDP_TEST_POSTGRES_URL"}, "on_error_rows": "skip",
                "batch_size": 7, "logs_dir": str(tmp_path / "logs"), "staging_dir": str(tmp_path / "staging"),
                "tables": {"path": str(tmp_path / "output/tables")}, "sources": sample_sources()}
    settings.update(changes)
    with open(tmp_path / "pipeline.yaml", "w") as f:
        yaml.safe_dump(settings, f, sort_keys=False)
    return tmp_path / "pipeline.yaml"


def run(config, **kwargs):
    kwargs.setdefault("environ", {"PDP_TEST_POSTGRES_URL": POSTGRES_URL} if POSTGRES_URL else {})
    return load(config, **kwargs)


def _normalize(type_name, value):
    """A database value as text, the way the sample CSVs write it, so the two databases compare."""
    if value is None:
        return ""
    if type_name == "bool":
        return "true" if value else "false"
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if type_name == "float":
        return str(float(value))
    return str(value)


def _in_key_order(table, rows):
    """Sorted by primary key here, not by the database, whose text collation may differ."""
    pk = [i for i, f in enumerate(SCHEMA[table].values()) if f.get("primary_key")]
    return sorted(rows, key=lambda r: tuple(int(r[i]) if r[i].isdigit() else r[i] for i in pk))


def read_database(connection):
    """{table: [row tuples as text]} for every table in the schema, in primary key order."""
    tables = {}
    cursor = connection.cursor()
    for table, fields in SCHEMA.items():
        cursor.execute(f'SELECT {", ".join(fields)} FROM "{table}"')
        tables[table] = _in_key_order(table, [tuple(_normalize(f["type"], v) for f, v in zip(fields.values(), row))
                                              for row in cursor.fetchall()])
    return tables


def read_sqlite(path):
    with sqlite3.connect(path) as connection:
        return read_database(connection)


def read_postgres(url):
    import psycopg
    with psycopg.connect(url) as connection:
        return read_database(connection)


def sample_tables():
    """The published sample output, as the loader should write it, without loaded_at (the load time)."""
    tables = {}
    for table, fields in SCHEMA.items():
        tables[table] = _in_key_order(table, [tuple(_normalize(f["type"], _typed(f["type"], r[c]))
                                                    for c, f in fields.items())
                                              for r in read_csv(SAMPLE_OUTPUT / f"{table}.csv")])
    return without_load_time(tables)


def _typed(type_name, text):
    if text == "":
        return None
    return {"float": float, "bool": lambda t: t == "true"}.get(type_name, str)(text)


def without_load_time(tables):
    """Without what each load writes for itself: data_provider.loaded_at, and the load_run row's run id, times,
    backend and paths. Its file format and credit cutoff stay, since every load of the same files gives the same."""
    position = list(SCHEMA["data_provider"]).index("loaded_at")
    kept = [list(SCHEMA["load_run"]).index(c) for c in ("file_format", "credit_cutoff")]
    return dict(tables, data_provider=[r[:position] + r[position + 1:] for r in tables["data_provider"]],
                load_run=[tuple(r[i] for i in kept) for r in tables["load_run"]])


def test_only_public_api_is_load():
    public = [n for n, f in vars(l).items() if not n.startswith("_") and callable(f)
              and getattr(f, "__module__", None) == l.__name__]
    assert public == ["load"]
    assert l.__all__ == ["load"]


# Settings

@pytest.mark.parametrize("changes, message", [
    ({"backend": "duckdb"}, "backend must be one of"),
    ({"mode": "incremental"}, "mode must be full_refresh"),
    ({"on_error_rows": "ignore"}, "on_error_rows must be skip or fail"),
    ({"batch_size": 0}, "batch_size must be a whole number"),
    ({"batch_size": "lots"}, "batch_size must be a whole number"),
    ({"surprise": 1}, "unknown setting 'surprise'"),
    ({"sources": sample_sources()[1:]}, "one cohort, one course"),
    ({"sources": sample_sources() + sample_sources()[:1]}, "one cohort, one course"),
    ({"sources": [dict(sample_sources()[0], path="nowhere.csv")] + sample_sources()[1:]}, "no file at"),
    ({"sources": [dict(sample_sources()[0], config="nowhere.yaml")] + sample_sources()[1:]}, "no mapping config at"),
    ({"sources": [{"kind": "cohort"}] + sample_sources()[1:]}, "needs exactly"),
    ({"sources": [dict(sample_sources()[0], path=None)] + sample_sources()[1:]}, "each a non-empty text"),
    ({"logs_dir": 3}, "logs_dir and staging_dir are paths"),
    ({"staging_dir": ["a"]}, "logs_dir and staging_dir are paths"),
    ({"fixes": "nowhere.yaml"}, "fixes must name the fixes file"),
])
def test_bad_settings_stop_before_anything_is_written(tmp_path, changes, message):
    with pytest.raises(ConfigError, match=message):
        run(make_config(tmp_path, **changes))
    assert not (tmp_path / "logs").exists() and not (tmp_path / "output").exists()


def test_two_sources_with_the_same_file_name_are_rejected(tmp_path):
    copy = tmp_path / "elsewhere" / "pdp_cohort_data.csv"
    copy.parent.mkdir()
    shutil.copy(SAMPLE / "pdp_cohort_data.csv", copy)
    housing = dict(sample_sources()[2], path=str(copy))
    with pytest.raises(ConfigError, match="share a file name"):
        run(make_config(tmp_path, sources=sample_sources()[:2] + [housing]))


def test_two_sources_with_the_same_content_are_rejected(tmp_path):
    copy = shutil.copy(SAMPLE / "enrichment/institution_events.csv", tmp_path / "events_again.csv")
    again = dict(sample_sources()[3], path=str(copy))
    with pytest.raises(ConfigError, match="same file"):
        run(make_config(tmp_path, sources=sample_sources() + [again]))


def test_settings_that_are_not_a_map_are_rejected(tmp_path):
    (tmp_path / "pipeline.yaml").write_text("- backend: sqlite\n")
    with pytest.raises(ConfigError, match="must be a map"):
        run(tmp_path / "pipeline.yaml")


def test_postgres_without_its_environment_variable_names_the_variable(tmp_path):
    with pytest.raises(ConfigError, match="environment variable PDP_TEST_POSTGRES_URL"):
        load(make_config(tmp_path), backend="postgres", environ={})


@pytest.mark.postgres  # needs psycopg, not a server
def test_postgres_with_a_malformed_url_is_a_settings_error(tmp_path):
    pytest.importorskip("psycopg")
    with pytest.raises(ConfigError, match="not a valid connection URL"):
        load(make_config(tmp_path), backend="postgres", environ={"PDP_TEST_POSTGRES_URL": "not a url"})


def test_a_missing_settings_file_is_a_settings_error(tmp_path):
    with pytest.raises(ConfigError):
        load(tmp_path / "missing.yaml")


def test_overrides_replace_the_settings_file(tmp_path):
    cohort, course = tmp_path / "in" / "cohort.csv", tmp_path / "in" / "course.csv"
    write_csv(cohort, read_csv(SAMPLE / "pdp_cohort_data.csv"))
    write_csv(course, read_csv(SAMPLE / "pdp_course_data.csv"))
    summary = run(make_config(tmp_path, backend="postgres"), backend="sqlite", sqlite_path=tmp_path / "other.sqlite",
                  cohort=cohort, course=course)
    assert summary["backend"] == "sqlite" and summary["target"] == str(tmp_path / "other.sqlite")
    assert set(summary["validation"]) >= {"cohort.csv", "course.csv"}
    assert read_sqlite(tmp_path / "other.sqlite")["course_enrollment"]


def test_a_reused_run_id_is_rejected(tmp_path):
    config = make_config(tmp_path)
    run(config, run_id="fixed")
    with pytest.raises(ConfigError, match="already has a report"):
        run(config, run_id="fixed")
    (tmp_path / "logs/validation_report/validated-institution_events").mkdir(parents=True)  # an earlier validator run
    with pytest.raises(ConfigError, match="already has a report"):
        run(config, run_id="validated")
    assert not (tmp_path / "logs/load_report/validated").exists()


# Schema

def test_tables_are_created_in_foreign_key_order():
    order = backends.table_order(SCHEMA, FOREIGN_KEYS)
    assert set(order) == set(SCHEMA)
    for table, keys in FOREIGN_KEYS.items():
        for _, parent, _ in keys:
            assert order.index(parent) < order.index(table)


def test_table_order_follows_a_two_column_key_whatever_order_the_schema_lists_tables():
    backwards = dict(reversed(list(SCHEMA.items())))  # course_enrollment now comes before cohort_membership
    order = backends.table_order(backwards, FOREIGN_KEYS)
    assert order.index("cohort_membership") < order.index("course_enrollment")


@pytest.mark.parametrize("backend", sorted(backends.BACKENDS))
def test_create_table_carries_every_key_from_the_schema(backend):
    sql = backends.create_table_sql(backends.BACKENDS[backend], SCHEMA, "course_enrollment", FOREIGN_KEYS)
    assert 'UNIQUE ("provider_id", "source_row_number")' in sql
    assert ('FOREIGN KEY ("student_id", "cohort") REFERENCES "cohort_membership" ("student_id", "cohort")') in sql
    assert 'FOREIGN KEY ("course_id") REFERENCES "course" ("course_id")' in sql
    assert '"student_id" TEXT NOT NULL' in sql
    assert '"course_id" ' + backends.BACKENDS[backend].types["int"] + "," in sql  # nullable: no record on some rows
    sql = backends.create_table_sql(backends.BACKENDS[backend], SCHEMA, "cohort_membership", FOREIGN_KEYS)
    assert 'PRIMARY KEY ("student_id", "cohort")' in sql


# SQLite

def test_sqlite_load_matches_the_published_samples(tmp_path):
    summary = run(make_config(tmp_path))
    assert summary["status"] == "loaded"
    assert without_load_time(read_sqlite(tmp_path / "output/pdp.sqlite")) == sample_tables()
    assert summary["tables"] == {t: len(rows) for t, rows in sample_tables().items()}
    assert (tmp_path / "logs/load_report" / summary["run_id"] / "summary.yaml").is_file()


def test_sqlite_enforces_keys(tmp_path):
    run(make_config(tmp_path))
    connection = sqlite3.connect(tmp_path / "output/pdp.sqlite")
    connection.execute("PRAGMA foreign_keys = ON")
    assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
    student = connection.execute("SELECT student_id FROM student LIMIT 1").fetchone()[0]
    with pytest.raises(sqlite3.IntegrityError, match="UNIQUE"):  # a primary key
        connection.execute("INSERT INTO student (student_id, institution_id) VALUES (?, 1)", (student,))
    with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY"):
        connection.execute("INSERT INTO student_attribute (student_id, attribute_key, attribute_value, source) "
                           "VALUES ('nobody', 'tribal_affiliation', 'example', 'test')")
    with pytest.raises(sqlite3.IntegrityError, match="NOT NULL"):
        connection.execute("INSERT INTO course (course_prefix) VALUES ('ENG')")
    with pytest.raises(sqlite3.IntegrityError, match="UNIQUE"):  # a unique group: one row per file row
        connection.execute("INSERT INTO course_enrollment (provider_id, source_row_number, student_id, cohort, "
                           "course_file_cohort_term, term_id) SELECT provider_id, source_row_number, student_id, cohort, "
                           "course_file_cohort_term, term_id FROM course_enrollment LIMIT 1")
    with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY"):  # two columns: a cohort the student isn't in
        connection.execute("INSERT INTO course_enrollment (provider_id, source_row_number, student_id, cohort, "
                           "course_file_cohort_term, term_id) SELECT provider_id, -1, student_id, '1999-00', "
                           "course_file_cohort_term, term_id FROM course_enrollment LIMIT 1")
    connection.execute("INSERT INTO student_attribute (student_id, attribute_key, attribute_value, source) "
                       "VALUES (?, 'tribal_affiliation', 'example', 'test')", (student,))
    added = connection.execute("SELECT attribute_id FROM student_attribute WHERE source = 'test'").fetchone()[0]
    assert added == len(sample_tables()["student_attribute"]) + 1  # a row added without an id gets the next one


def test_sqlite_full_refresh_replaces_everything_and_repeats_exactly(tmp_path):
    config = make_config(tmp_path)
    run(config)
    first = without_load_time(read_sqlite(tmp_path / "output/pdp.sqlite"))
    with sqlite3.connect(tmp_path / "output/pdp.sqlite") as connection:
        connection.execute("INSERT INTO institution VALUES (2, 'Added by hand', 0)")
    run(config)
    assert without_load_time(read_sqlite(tmp_path / "output/pdp.sqlite")) == first


def _break_one_reference(monkeypatch):
    """Make the build hand the database a course_enrollment row whose student doesn't exist."""
    build = l.build_tables

    def broken(*args, **kwargs):
        tables, report = build(*args, **kwargs)
        tables["course_enrollment"][-1]["student_id"] = "0" * 32
        return tables, report
    monkeypatch.setattr(l, "build_tables", broken)


def test_sqlite_failed_load_rolls_back_to_the_previous_database(tmp_path, monkeypatch):
    config = make_config(tmp_path)
    run(config)
    before = read_sqlite(tmp_path / "output/pdp.sqlite")
    _break_one_reference(monkeypatch)
    with pytest.raises(RuntimeError, match="not changed.*FOREIGN KEY"):
        run(config, run_id="broken")
    assert read_sqlite(tmp_path / "output/pdp.sqlite") == before
    report = yaml.safe_load(open(tmp_path / "logs/load_report/broken/summary.yaml"))
    assert report["status"] == "failed" and "FOREIGN KEY" in report["error"]


def test_a_failed_first_load_leaves_no_tables(tmp_path, monkeypatch):
    _break_one_reference(monkeypatch)
    with pytest.raises(RuntimeError):
        run(make_config(tmp_path))
    with sqlite3.connect(tmp_path / "output/pdp.sqlite") as connection:
        assert connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall() == []


@pytest.mark.parametrize("on_delete", ["ON DELETE CASCADE", "ON DELETE SET NULL", ""])
def test_sqlite_refresh_stops_when_a_squad_table_points_at_the_model(tmp_path, on_delete):
    """Dropping a table in SQLite deletes its rows first, which would cascade into the squad's table."""
    config = make_config(tmp_path)
    run(config)
    with sqlite3.connect(tmp_path / "output/pdp.sqlite") as connection:
        connection.execute(f"CREATE TABLE squad_notes (student_id TEXT REFERENCES student (student_id) {on_delete}, "
                           f"note TEXT)")
        connection.execute("INSERT INTO squad_notes SELECT student_id, 'keep me' FROM student")
        notes = connection.execute("SELECT * FROM squad_notes ORDER BY student_id").fetchall()
    before = read_sqlite(tmp_path / "output/pdp.sqlite")
    with pytest.raises(RuntimeError, match=r"not changed.*squad_notes\.student_id -> student"):
        run(config)
    assert read_sqlite(tmp_path / "output/pdp.sqlite") == before
    with sqlite3.connect(tmp_path / "output/pdp.sqlite") as connection:
        assert connection.execute("SELECT * FROM squad_notes ORDER BY student_id").fetchall() == notes


def test_sqlite_refresh_stops_when_a_squad_table_points_at_a_two_column_key(tmp_path):
    """SQLite lists a two-column key as two lines; the check reads only table names, so it still stops."""
    config = make_config(tmp_path)
    run(config)
    with sqlite3.connect(tmp_path / "output/pdp.sqlite") as connection:
        connection.execute("CREATE TABLE squad_cohort_notes (student_id TEXT, cohort TEXT, note TEXT, FOREIGN KEY "
                           "(student_id, cohort) REFERENCES cohort_membership (student_id, cohort))")
        connection.execute("INSERT INTO squad_cohort_notes SELECT student_id, cohort, 'keep me' FROM cohort_membership")
        notes = connection.execute("SELECT * FROM squad_cohort_notes ORDER BY student_id, cohort").fetchall()
    before = read_sqlite(tmp_path / "output/pdp.sqlite")
    with pytest.raises(RuntimeError, match=r"not changed.*squad_cohort_notes\.\w+ -> cohort_membership"):
        run(config)
    assert read_sqlite(tmp_path / "output/pdp.sqlite") == before
    with sqlite3.connect(tmp_path / "output/pdp.sqlite") as connection:
        assert connection.execute("SELECT * FROM squad_cohort_notes ORDER BY student_id, cohort").fetchall() == notes


# What gets loaded

@pytest.fixture
def broken_files(tmp_path):
    """Sample files with one error and one warning planted in the cohort file, and one housing row
    for a student who isn't in it."""
    cohort, course = read_csv(SAMPLE / "pdp_cohort_data.csv"), read_csv(SAMPLE / "pdp_course_data.csv")
    housing = read_csv(SAMPLE / "enrichment/on_campus_housing.csv")
    bad_student = cohort[1]["Student_GUID"]
    cohort[1]["Student_GUID"] = "not-a-guid"                      # error: pattern
    cohort[2]["Pell_Status_First_Year"] = "U"                     # warning: yes_no
    housing[0]["Student_GUID"] = "f" * 32                         # not in the cohort file
    return {"cohort": write_csv(tmp_path / "in/cohort.csv", cohort), "course": write_csv(tmp_path / "in/course.csv", course),
            "housing": write_csv(tmp_path / "in/housing.csv", housing), "bad_student": bad_student,
            "warned": (cohort[2]["Student_GUID"], cohort[2]["Cohort"]),
            "bad_course_rows": sum(r["Student_GUID"] == bad_student for r in course),
            "bad_housing_rows": [n for n, r in enumerate(housing, start=1) if r["Student_GUID"] == bad_student]}


def test_error_rows_are_held_back_and_warning_rows_load(tmp_path, broken_files):
    summary = run(make_config(tmp_path, sources=sample_sources(broken_files["cohort"], broken_files["course"],
                                                               broken_files["housing"])))
    assert summary["validation"]["cohort.csv"]["rows_failed"] == 1
    assert summary["validation"]["course.csv"]["rows_failed"] == broken_files["bad_course_rows"]  # its student is gone
    connection = sqlite3.connect(tmp_path / "output/pdp.sqlite")
    students = {r[0] for r in connection.execute("SELECT student_id FROM student")}
    assert broken_files["bad_student"] not in students and "not-a-guid" not in students
    assert connection.execute("SELECT COUNT(*) FROM course_enrollment").fetchone()[0] == \
        len(read_csv(broken_files["course"])) - broken_files["bad_course_rows"]
    assert connection.execute("SELECT pell_status_first_year FROM cohort_membership WHERE student_id = ? AND cohort = ?",
                              broken_files["warned"]).fetchone() == ("U",)
    # The unknown student's housing row, and the housing rows of the student held back above.
    assert summary["held_back"][0] == {"source_file": "housing.csv", "source_row_number": 1,
                                       "missing": ["student_attribute.student_id '" + "f" * 32 + "' is not in student"]}
    assert [h["source_row_number"] for h in summary["held_back"][1:]] == broken_files["bad_housing_rows"]
    assert connection.execute("SELECT COUNT(*) FROM student_attribute").fetchone()[0] == \
        len(read_csv(broken_files["housing"])) - len(summary["held_back"])


def test_a_load_with_no_students_keeps_the_last_load(tmp_path):
    config = make_config(tmp_path)
    run(config)
    before = read_sqlite(tmp_path / "output/pdp.sqlite")
    cohort = [dict(row, Student_GUID="not-a-guid") for row in read_csv(SAMPLE / "pdp_cohort_data.csv")]
    sources = sample_sources(cohort=write_csv(tmp_path / "in/cohort.csv", cohort))
    with pytest.raises(RuntimeError, match="not changed.*no student rows"):
        run(make_config(tmp_path, sources=sources), run_id="empty")
    assert read_sqlite(tmp_path / "output/pdp.sqlite") == before
    report = yaml.safe_load(open(tmp_path / "logs/load_report/empty/summary.yaml"))
    assert report["status"] == "failed" and report["validation"]["cohort.csv"]["rows_passed"] == 0


def test_on_error_rows_fail_stops_before_the_database(tmp_path, broken_files):
    config = make_config(tmp_path, on_error_rows="fail",
                         sources=sample_sources(broken_files["cohort"], broken_files["course"]))
    with pytest.raises(RuntimeError, match="on_error_rows is fail"):
        run(config)
    assert not (tmp_path / "output/pdp.sqlite").exists()
    assert list((tmp_path / "logs/failed_records").iterdir())  # the validator still wrote the held-back rows


def test_duplicate_identities_follow_on_conflict(tmp_path):
    summary = run(make_config(tmp_path))
    connection = sqlite3.connect(tmp_path / "output/pdp.sqlite")
    cohort = read_csv(SAMPLE / "pdp_cohort_data.csv")
    # A student in two cohorts: one student row, two memberships.
    assert connection.execute("SELECT COUNT(*) FROM student").fetchone()[0] == len({r["Student_GUID"] for r in cohort})
    assert connection.execute("SELECT COUNT(*) FROM cohort_membership").fetchone()[0] == len(cohort)
    # Each file's Cohort_Term has its own column: the membership keeps the cohort file's, and each
    # enrollment keeps the course file's, so nothing collides.
    stored = dict(((s, c), t) for s, c, t in connection.execute("SELECT student_id, cohort, cohort_term FROM cohort_membership"))
    assert stored == {(r["Student_GUID"], r["Cohort"]): r["Cohort_Term"] for r in cohort}
    course = read_csv(SAMPLE / "pdp_course_data.csv")
    enrolled = [tuple(r) for r in connection.execute(
        "SELECT student_id, cohort, course_file_cohort_term FROM course_enrollment ORDER BY source_row_number")]
    assert enrolled == [(r["Student_GUID"], r["Cohort"], r["Cohort_Term"]) for r in course]
    assert summary["collisions"] == {}
    # Joined on both columns, each enrollment meets one membership, also for the student in two cohorts.
    joined = connection.execute("SELECT COUNT(*) FROM course_enrollment e JOIN cohort_membership m "
                                "ON m.student_id = e.student_id AND m.cohort = e.cohort").fetchone()[0]
    assert joined == len(course)


def test_retakes_and_rows_without_a_course_record_load(tmp_path):
    run(make_config(tmp_path))
    connection = sqlite3.connect(tmp_path / "output/pdp.sqlite")
    course = read_csv(SAMPLE / "pdp_course_data.csv")
    # One row per course-file row, found again by file and row number.
    rows = connection.execute("SELECT d.source_file, e.source_row_number FROM course_enrollment e "
                              "JOIN data_provider d ON d.provider_id = e.provider_id").fetchall()
    assert sorted(n for _, n in rows) == list(range(1, len(course) + 1))
    assert {f for f, _ in rows} == {"normalized-data-model/data/input/sample/pdp_course_data.csv"}
    assert connection.execute("SELECT MAX(attempt_number) FROM course_enrollment").fetchone()[0] >= 2
    no_record = sum(not r["Course_Prefix"] for r in course)
    assert connection.execute("SELECT COUNT(*) FROM course_enrollment WHERE course_id IS NULL "
                              "AND section_id IS NULL AND attempt_number IS NULL").fetchone()[0] == no_record
    unknown = sum(not r["Academic_Year"] for r in course)
    assert connection.execute("SELECT COUNT(*) FROM course_enrollment e JOIN term t ON t.term_id = e.term_id "
                              "WHERE t.academic_year = 'UNKNOWN'").fetchone()[0] == unknown
    assert connection.execute("SELECT academic_year FROM term ORDER BY sort_order DESC LIMIT 1").fetchone() == ("UNKNOWN",)


# PostgreSQL, against a real server

@needs_postgres
def test_postgres_load_matches_the_published_samples_and_sqlite(tmp_path, postgres):
    config = make_config(tmp_path)
    summary = run(config, backend="postgres", environ={"PDP_TEST_POSTGRES_URL": postgres})
    assert summary["status"] == "loaded" and summary["target"].startswith("postgresql://")
    assert "password" not in summary["target"]
    loaded = read_postgres(postgres)
    assert without_load_time(loaded) == sample_tables()
    run(config)
    assert without_load_time(loaded) == without_load_time(read_sqlite(tmp_path / "output/pdp.sqlite"))


@needs_postgres
def test_postgres_enforces_keys_and_continues_ids(tmp_path, postgres):
    import psycopg
    run(make_config(tmp_path), backend="postgres", environ={"PDP_TEST_POSTGRES_URL": postgres})
    with psycopg.connect(postgres, autocommit=True) as connection:
        student = connection.execute("SELECT student_id FROM student LIMIT 1").fetchone()[0]
        with pytest.raises(psycopg.errors.UniqueViolation):
            connection.execute("INSERT INTO student (student_id, institution_id) VALUES (%s, 1)", (student,))
        with pytest.raises(psycopg.errors.ForeignKeyViolation):
            connection.execute("INSERT INTO student_attribute (student_id, attribute_key, attribute_value, source) "
                               "VALUES ('nobody', 'tribal_affiliation', 'example', 'test')")
        with pytest.raises(psycopg.errors.UniqueViolation):  # a unique group: one row per file row
            connection.execute("INSERT INTO course_enrollment (provider_id, source_row_number, student_id, cohort, "
                               "course_file_cohort_term, term_id) SELECT provider_id, source_row_number, student_id, "
                               "cohort, course_file_cohort_term, term_id FROM course_enrollment LIMIT 1")
        with pytest.raises(psycopg.errors.ForeignKeyViolation):  # two columns: a cohort the student isn't in
            connection.execute("INSERT INTO course_enrollment (provider_id, source_row_number, student_id, cohort, "
                               "course_file_cohort_term, term_id) SELECT provider_id, -1, student_id, '1999-00', "
                               "course_file_cohort_term, term_id FROM course_enrollment LIMIT 1")
        with pytest.raises(psycopg.errors.NotNullViolation):
            connection.execute("INSERT INTO course (course_prefix) VALUES ('ENG')")
        added = connection.execute("INSERT INTO student_attribute (student_id, attribute_key, attribute_value, source) "
                                   "VALUES (%s, 'tribal_affiliation', 'example', 'test') RETURNING attribute_id",
                                   (student,)).fetchone()[0]
        # A new id past every loaded one. Not always the very next: the failed insert above used one up.
        assert added > len(sample_tables()["student_attribute"])


@needs_postgres
def test_postgres_full_refresh_repeats_and_failed_load_rolls_back(tmp_path, postgres, monkeypatch):
    import psycopg
    config = make_config(tmp_path)
    environ = {"PDP_TEST_POSTGRES_URL": postgres}
    run(config, backend="postgres", environ=environ)
    first = read_postgres(postgres)
    with psycopg.connect(postgres) as connection:
        connection.execute("INSERT INTO institution VALUES (2, 'Added by hand', false)")
    run(config, backend="postgres", environ=environ)
    second = read_postgres(postgres)
    assert without_load_time(second) == without_load_time(first)
    _break_one_reference(monkeypatch)
    with pytest.raises(RuntimeError, match="not changed.*ForeignKeyViolation"):
        run(config, backend="postgres", environ=environ)
    assert read_postgres(postgres) == second


@needs_postgres
def test_postgres_refresh_stops_when_a_squad_table_points_at_the_model(tmp_path, postgres):
    import psycopg
    config = make_config(tmp_path)
    environ = {"PDP_TEST_POSTGRES_URL": postgres}
    run(config, backend="postgres", environ=environ)
    with psycopg.connect(postgres) as connection:
        connection.execute("CREATE TABLE squad_notes (student_id TEXT REFERENCES student (student_id) "
                           "ON DELETE CASCADE, note TEXT)")
        connection.execute("INSERT INTO squad_notes SELECT student_id, 'keep me' FROM student")
    before = read_postgres(postgres)
    with pytest.raises(RuntimeError, match="(?s)not changed.*squad_notes"):
        run(config, backend="postgres", environ=environ)
    assert read_postgres(postgres) == before
    with psycopg.connect(postgres) as connection:
        assert connection.execute("SELECT COUNT(*) FROM squad_notes").fetchone()[0] == len(before["student"])


# Command line

def test_command_line_exit_codes(tmp_path, monkeypatch, capsys):
    config = make_config(tmp_path)
    assert l._main(["--config", str(config)]) == 0
    out = capsys.readouterr().out
    assert "course_enrollment: " in out and "held back for a missing reference: 0 rows" in out
    monkeypatch.delenv("PDP_TEST_POSTGRES_URL", raising=False)
    assert l._main(["--config", str(config), "--backend", "postgres"]) == 2
    _break_one_reference(monkeypatch)
    assert l._main(["--config", str(config)]) == 1
    assert "the database was not changed" in capsys.readouterr().err


# The full mock data

@pytest.mark.slow
def test_full_mock_data_reconciles_with_the_raw_files(tmp_path):
    """Every table's row count follows from the raw files and its grain, and each student's
    demographics are stored once and match the cohort file."""
    sources = sample_sources(RAW / "pdp_cohort_data.csv", RAW / "pdp_course_data.csv",
                             BUILD / "data/input/enrichment/on_campus_housing.csv")
    sources[3]["path"] = str(BUILD / "data/input/enrichment/institution_events.csv")
    summary = run(make_config(tmp_path, batch_size=5000, sources=sources))
    cohort, course = read_csv(RAW / "pdp_cohort_data.csv"), read_csv(RAW / "pdp_course_data.csv")
    housing = read_csv(BUILD / "data/input/enrichment/on_campus_housing.csv")
    failed = {name: v["rows_failed"] for name, v in summary["validation"].items()}
    assert failed == dict.fromkeys(failed, 0) and summary["held_back"] == []
    assert summary["tables"] == {
        "institution": 1,
        "data_provider": 4,
        "student": len({r["Student_GUID"] for r in cohort}),
        "cohort_membership": len({(r["Student_GUID"], r["Cohort"]) for r in cohort}),
        "term": len({(r["Academic_Year"] or "UNKNOWN", r["Academic_Term"] or "UNKNOWN") for r in course + housing}),
        "course": len({(r["Course_Prefix"], r["Course_Number"]) for r in course if r["Course_Prefix"]}),
        "course_enrollment": len(course),
        "student_attribute": len(housing),
        "institution_event": len(read_csv(BUILD / "data/input/enrichment/institution_events.csv")),
        "load_run": 1,
    }
    mapping = {e["source"]: e for e in yaml.safe_load(open(CONFIG / "cohort_mapping.yaml"))
               if e.get("destination_table") == "student"}

    race_fix = next(f for f in yaml.safe_load((CONFIG / "data_fixes.yaml").read_text())["fixes"]
                    if f["name"] == "race_cut_at_25_characters")["replace"]

    def stored(column, raw):
        entry = mapping[column]
        value = None if raw == "" else "UNKNOWN" if raw in entry.get("unknown_values", []) else raw
        return race_fix.get(value, value) if column == "Race" else value

    expected = {r["Student_GUID"]: tuple(stored(c, r[c]) for c in ("Gender", "Race", "Ethnicity", "Student_Age"))
                for r in cohort}
    connection = sqlite3.connect(tmp_path / "output/pdp.sqlite")
    loaded = {s: rest for s, *rest in connection.execute(
        "SELECT student_id, gender, race, ethnicity, student_age FROM student")}
    assert {s: tuple(v) for s, v in loaded.items()} == expected
    # Every enrollment meets exactly one membership on student and cohort, and each keeps the
    # course file's own Cohort_Term, which differs from the cohort file's on some rows.
    assert connection.execute("SELECT COUNT(*) FROM course_enrollment e JOIN cohort_membership m "
                              "ON m.student_id = e.student_id AND m.cohort = e.cohort").fetchone()[0] == len(course)
    terms = {(r["Student_GUID"], r["Cohort"]): r["Cohort_Term"] for r in cohort}
    differ = sum(1 for r in course if r["Cohort_Term"] != terms[(r["Student_GUID"], r["Cohort"])])
    assert connection.execute("SELECT COUNT(*) FROM course_enrollment e JOIN cohort_membership m "
                              "ON m.student_id = e.student_id AND m.cohort = e.cohort "
                              "WHERE e.course_file_cohort_term <> m.cohort_term").fetchone()[0] == differ == 4307
    # Credit years after the 2025-26 cutoff are blank, and each cohort says how many it can see.
    assert dict(connection.execute("SELECT DISTINCT cohort, credit_years_observed FROM cohort_membership").fetchall()) == \
        {"2021-22": 4, "2022-23": 4, "2023-24": 3, "2024-25": 2}
    assert connection.execute("SELECT COUNT(*) FROM cohort_membership WHERE cohort = '2024-25' "
                              "AND number_of_credits_attempted_yr_3 = 0").fetchone()[0] == 0


# The loaded tables as files

def test_a_load_writes_every_table_as_a_file_like_the_samples(tmp_path):
    summary = run(make_config(tmp_path))
    folder = tmp_path / "output/tables"
    assert summary["table_files"] == str(folder)
    for table in SCHEMA:
        loaded, published = read_csv(folder / f"{table}.csv"), read_csv(SAMPLE_OUTPUT / f"{table}.csv")
        if table == "data_provider":  # only the load time differs
            loaded = [dict(r, loaded_at="") for r in loaded]
            published = [dict(r, loaded_at="") for r in published]
        if table == "load_run":  # each load's own row; the samples' is run id sample
            assert [(r["file_format"], r["credit_cutoff"]) for r in loaded] == [("csv", "2025-26")]
            continue
        assert loaded == published, table


def test_parquet_files_with_format_parquet(tmp_path):
    run(make_config(tmp_path), fmt="parquet")
    assert sorted(p.name for p in (tmp_path / "output/tables").iterdir()) == sorted(f"{t}.parquet" for t in SCHEMA)


def test_a_failed_load_leaves_the_last_files(tmp_path, monkeypatch):
    config = make_config(tmp_path)
    run(config)
    before = {p.name: p.read_bytes() for p in (tmp_path / "output/tables").iterdir()}
    monkeypatch.setattr(l, "refresh", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("database down")))
    with pytest.raises(RuntimeError, match="database was not changed"):
        run(config)
    assert {p.name: p.read_bytes() for p in (tmp_path / "output/tables").iterdir()} == before


def test_a_failed_write_after_the_commit_is_reported_and_keeps_the_last_files(tmp_path, monkeypatch):
    config = make_config(tmp_path)
    run(config)
    before = {p.name: p.read_bytes() for p in (tmp_path / "output/tables").iterdir()}

    def full_disk(*args, **kwargs):
        raise OSError("No space left on device")

    monkeypatch.setattr(l, "write_tables", full_disk)
    with pytest.raises(RuntimeError, match="committed to the database, but the table files"):
        run(config, run_id="second")
    report = yaml.safe_load((tmp_path / "logs/load_report/second/summary.yaml").read_text())
    assert report["status"] == "loaded, tables not written" and "No space left" in report["error"]
    assert {p.name: p.read_bytes() for p in (tmp_path / "output/tables").iterdir()} == before
    assert l._main(["--config", str(config), "--run_id", "third"]) == 1


def test_a_write_that_fails_partway_leaves_the_last_files_whole(tmp_path, monkeypatch):
    config = make_config(tmp_path)
    run(config)
    before = {p.name: p.read_bytes() for p in (tmp_path / "output/tables").iterdir()}
    real = l.write_tables

    def one_file_then_fail(schema, tables, folder, fmt):
        first = next(iter(tables))
        real(schema, {first: tables[first]}, folder, fmt)
        raise OSError("No space left on device")

    monkeypatch.setattr(l, "write_tables", one_file_then_fail)
    with pytest.raises(RuntimeError, match="committed to the database, but the table files"):
        run(config, run_id="second")
    assert {p.name: p.read_bytes() for p in (tmp_path / "output/tables").iterdir()} == before


def test_a_failed_swap_puts_the_last_files_back(tmp_path, monkeypatch):
    config = make_config(tmp_path)
    run(config)
    before = {p.name: p.read_bytes() for p in (tmp_path / "output/tables").iterdir()}
    real = Path.rename

    def fail_the_swap(self, target):
        if self.name.endswith(".writing"):
            raise OSError("Device busy")
        return real(self, target)

    monkeypatch.setattr(Path, "rename", fail_the_swap)
    with pytest.raises(RuntimeError, match="committed to the database, but the table files"):
        run(config, run_id="second")
    assert {p.name: p.read_bytes() for p in (tmp_path / "output/tables").iterdir()} == before


def test_the_files_go_to_output_tables_unless_the_settings_say_otherwise(tmp_path):
    settings = yaml.safe_load(make_config(tmp_path).read_text())
    del settings["tables"]
    (tmp_path / "pipeline.yaml").write_text(yaml.safe_dump(settings))
    assert l._settings(tmp_path / "pipeline.yaml", None, None, None, None, {})["tables_dir"] == l._BUILD / "output/tables"
    override = l._settings(tmp_path / "pipeline.yaml", None, None, None, None, {}, tables_dir=tmp_path / "mine")
    assert override["tables_dir"] == tmp_path / "mine"
    settings["tables"] = {"path": "output/tables", "format": "parquet"}
    (tmp_path / "pipeline.yaml").write_text(yaml.safe_dump(settings))
    with pytest.raises(ConfigError, match="tables takes only path.*comes from --format"):
        l._settings(tmp_path / "pipeline.yaml", None, None, None, None, {})


@needs_postgres
def test_a_postgres_load_writes_the_files_too(tmp_path, postgres):
    run(make_config(tmp_path, backend="postgres"), environ={"PDP_TEST_POSTGRES_URL": postgres})
    assert len(read_csv(tmp_path / "output/tables/course_enrollment.csv")) == len(sample_tables()["course_enrollment"])


# load_run

def test_load_run_says_which_run_built_the_database(tmp_path):
    summary = run(make_config(tmp_path), run_id="20261029T000000Z-abcdef")
    connection = sqlite3.connect(tmp_path / "output/pdp.sqlite")
    connection.row_factory = sqlite3.Row
    rows = [dict(r) for r in connection.execute("SELECT * FROM load_run")]
    assert len(rows) == 1
    row = rows[0]
    assert (row["run_id"], row["backend"], row["file_format"], row["credit_cutoff"]) == (
        summary["run_id"], "sqlite", "csv", "2025-26")
    assert row["started_at"] <= row["finished_at"]
    assert row["started_at"] == connection.execute("SELECT DISTINCT loaded_at FROM data_provider").fetchone()[0]
    assert Path(row["load_report"]).is_file() and Path(row["staging_folder"]).is_dir()
    assert sorted(row["validation_reports"].split("|")) == sorted({v["report"] for v in summary["validation"].values()})
    # With one row, every row in the database belongs to it.
    assert connection.execute("SELECT COUNT(*) FROM course_enrollment CROSS JOIN load_run").fetchone()[0] == \
        len(sample_tables()["course_enrollment"])


def staged_run(tmp_path, fmt="csv", run_id="r"):
    """Every step but the load, by run_steps, into tmp_path/staging/<run_id>/. Returns the settings file."""
    from src.pipeline.run import run_steps
    config = make_config(tmp_path)
    run_steps(l._settings(config, None, None, None, None, {}), run_id, {"steps": [], "validation": {}}, fmt)
    return config


def test_load_run_reads_the_run_from_validated_alone(tmp_path):
    """A staged load records the cutoff, the format and the validation reports from validated/, so fixed/ can go."""
    config = staged_run(tmp_path, fmt="parquet")
    shutil.rmtree(tmp_path / "staging/r/fixed")
    load(config, staging=tmp_path / "staging/r")
    row = sqlite3.connect(tmp_path / "output/pdp.sqlite").execute(
        "SELECT file_format, credit_cutoff, validation_reports FROM load_run").fetchone()
    assert row[:2] == ("parquet", "2025-26")
    assert sorted(row[2].split("|")) == sorted(str(tmp_path / "logs/validation_report" / i)
                                               for i in ("r", "r-institution_events", "r-on_campus_housing"))
    assert sorted(p.suffix for p in (tmp_path / "output/tables").iterdir()) == [".parquet"] * len(SCHEMA)


def test_a_format_that_isnt_the_staged_runs_is_refused(tmp_path):
    config = staged_run(tmp_path, fmt="parquet")
    with pytest.raises(ConfigError, match="staged in parquet, so --format csv doesn't apply"):
        load(config, staging=tmp_path / "staging/r", fmt="csv")
    assert l._main(["--config", str(config), "--staging", str(tmp_path / "staging/r"), "--format", "csv"]) == 2


def test_load_run_finished_at_is_when_the_rows_were_written(tmp_path, monkeypatch):
    written = datetime(2030, 1, 2, 3, 4, 5)
    monkeypatch.setattr(backends, "_now", lambda: written)  # the clock refresh() reads just before the commit
    run(make_config(tmp_path))
    row = sqlite3.connect(tmp_path / "output/pdp.sqlite").execute("SELECT started_at, finished_at FROM load_run").fetchone()
    assert row[1] == written.isoformat() and row[0] != row[1]
    assert read_csv(tmp_path / "output/tables/load_run.csv")[0]["finished_at"] == written.isoformat()


def test_load_run_paths_are_from_the_build_folder_when_they_are_inside_it():
    assert l._local(l._BUILD / "logs/load_report/r/summary.yaml") == "logs/load_report/r/summary.yaml"
    assert l._local(Path("/somewhere/else/summary.yaml")) == "/somewhere/else/summary.yaml"


def test_load_run_values_follow_the_schemas_rules():
    rules = load_rules(CONFIG)
    assert check_value(rules, "load_run", "file_format", "xlsx") and check_value(rules, "load_run", "backend", "duckdb")
    assert not check_value(rules, "load_run", "file_format", "parquet") and not check_value(rules, "load_run", "backend", "sqlite")


def test_load_run_credit_cutoff_is_blank_when_that_fix_is_off(tmp_path):
    fixes = yaml.safe_load((CONFIG / "data_fixes.yaml").read_text())
    for entry in fixes["fixes"]:
        if entry["name"] == "future_credit_years_are_blank":
            entry["enabled"] = False
    (tmp_path / "fixes.yaml").write_text(yaml.safe_dump(fixes))
    run(make_config(tmp_path, fixes=str(tmp_path / "fixes.yaml")))
    assert sqlite3.connect(tmp_path / "output/pdp.sqlite").execute("SELECT credit_cutoff FROM load_run").fetchone() == (None,)

