"""A school's own data without code changes: where the data lives, how it loads, and which cohorts it has.

Covers UNCF_DATABASE, UNCF_SOURCE, cohorts read from the loaded data, provisional cohorts read from the analytics
config, and `python -m api load` with a school's files (paths or https links). See docs/integration.md.
"""
from __future__ import annotations

import io
import os
import sqlite3
import urllib.request
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api import __main__ as entry
from api import data, load, route
from api.route import create_app
from measures.run_measures import BUILT_IN_DATABASE, configured_database
from measures.tests.explorer_fixture import make_database, student

PREFIX = "/api/v1/uncf"
SAMPLE_INPUT = Path(__file__).resolve().parents[2] / "normalized-data-model" / "data" / "input" / "sample"


@pytest.fixture
def older_school(tmp_path, monkeypatch):
    """A school whose files hold the 2019-20 and 2020-21 classes only, none of the sample's years."""
    students = [student(f"a{n}", "2019-20", pell="Y", retention=int(n < 3)) for n in range(4)]
    students += [student(f"b{n}", "2020-21", retention=1) for n in range(6)]
    path = make_database(tmp_path / "pdp.sqlite", students)
    monkeypatch.setattr(data, "data_path", lambda: path)
    route.clear_cache()
    yield path
    route.clear_cache()


@pytest.fixture
def client() -> TestClient:
    """A test client for the standalone app."""
    return TestClient(create_app())


def write_config(path: Path, provisional: list[str]) -> Path:
    """An analytics config that declares the given provisional cohorts."""
    path.write_text(f"provisional_retention_cohorts: {provisional}\n")
    return path


# Where the data lives -------------------------------------------------------------------------------------------


def test_database_setting_names_the_file(tmp_path, monkeypatch) -> None:
    """UNCF_DATABASE points every reader at another file; unset, the built-in path stays."""
    monkeypatch.setenv("UNCF_DATABASE", str(tmp_path / "school.sqlite"))
    assert configured_database() == (tmp_path / "school.sqlite").resolve()
    monkeypatch.delenv("UNCF_DATABASE")
    assert configured_database() == BUILT_IN_DATABASE


def test_source_setting_names_the_school_files(older_school, client, monkeypatch) -> None:
    """Every answer names UNCF_SOURCE as its source, not the synthetic sample."""
    monkeypatch.setenv("UNCF_SOURCE", "FMU PDP files, fall 2026")
    assert client.get(f"{PREFIX}/gateway").json()["meta"]["source"] == "FMU PDP files, fall 2026"
    measure = client.get(f"{PREFIX}/measures/retention", params={"cohort": "2019-20"}).json()
    assert measure["meta"]["source"] == "FMU PDP files, fall 2026"
    monkeypatch.delenv("UNCF_SOURCE")
    route.clear_cache()  # settings are read once per cached answer, as when the API restarts
    assert client.get(f"{PREFIX}/gateway").json()["meta"]["source"] == data.SOURCE


# Cohorts come from the data -------------------------------------------------------------------------------------


def test_cohorts_come_from_the_loaded_data(older_school, client) -> None:
    """A school's own years are offered and answered; a year not in its data is a 422 with our error body."""
    assert client.get(f"{PREFIX}/options").json()["cohorts"] == ["2019-20", "2020-21"]
    options = client.get(f"{PREFIX}/cohort-options").json()
    assert options["cohort"] == "2020-21" and options["cohorts"] == {"2019-20": 4, "2020-21": 6}
    assert client.get(f"{PREFIX}/gateway", params={"cohort": "2019-20"}).status_code == 200
    rows = client.get(f"{PREFIX}/measures/retention", params={"cohort": "2019-20"}).json()["rows"]
    assert rows[0]["denominator"] == 4
    refused = client.get(f"{PREFIX}/gateway", params={"cohort": "2023-24"})
    assert refused.status_code == 422 and refused.json()["error"]["code"] == "invalid_filter"


def test_default_cohort_is_the_latest_complete_one(older_school, client, tmp_path, monkeypatch) -> None:
    """With no cohort named, a page shows the latest class that isn't provisional."""
    assert client.get(f"{PREFIX}/gateway").json()["meta"]["cohort"] == "2020-21"
    monkeypatch.setenv("UNCF_ANALYTICS_CONFIG", str(write_config(tmp_path / "analytics.yaml", ["2020-21"])))
    route.clear_cache()
    assert client.get(f"{PREFIX}/gateway").json()["meta"]["cohort"] == "2019-20"


def test_provisional_cohorts_come_from_the_analytics_config(older_school, client, tmp_path, monkeypatch) -> None:
    """The one provisional list the chat reads also marks the API's year 2 answers."""
    monkeypatch.setenv("UNCF_ANALYTICS_CONFIG", str(write_config(tmp_path / "analytics.yaml", ["2020-21"])))
    newest = client.get(f"{PREFIX}/measures/retention", params={"cohort": "2020-21"}).json()
    older = client.get(f"{PREFIX}/measures/retention", params={"cohort": "2019-20"}).json()
    assert newest["meta"]["provisional"] is True and older["meta"]["provisional"] is False


def test_reloaded_data_brings_its_own_cohorts(older_school, client) -> None:
    """A reload with a new class shows it without a restart: the cohort list follows the file's version."""
    assert client.get(f"{PREFIX}/options").json()["cohorts"] == ["2019-20", "2020-21"]
    connection = sqlite3.connect(older_school)
    connection.execute("UPDATE cohort_membership SET cohort = '2021-22' WHERE student_id LIKE 'b%'")
    connection.commit()
    connection.close()
    later = os.stat(older_school).st_mtime + 5
    os.utime(older_school, (later, later))
    assert client.get(f"{PREFIX}/options").json()["cohorts"] == ["2019-20", "2021-22"]


def test_unreadable_config_is_a_503(older_school, client, tmp_path, monkeypatch) -> None:
    """A bad UNCF_ANALYTICS_CONFIG says so in our error body instead of failing without one."""
    monkeypatch.setenv("UNCF_ANALYTICS_CONFIG", str(tmp_path / "missing.yaml"))
    response = client.get(f"{PREFIX}/gateway")
    assert response.status_code == 503 and response.json()["error"]["code"] == "config_invalid"
    measure = client.get(f"{PREFIX}/measures/retention", params={"cohort": "2019-20"})
    assert measure.status_code == 503 and measure.json()["error"]["code"] == "config_invalid"


def test_no_data_offers_no_cohorts(tmp_path, client, monkeypatch) -> None:
    """Before a load, /options lists no cohorts and pages answer 503 data_missing."""
    monkeypatch.setattr(data, "data_path", lambda: tmp_path / "missing.sqlite")
    assert client.get(f"{PREFIX}/options").json()["cohorts"] == []
    response = client.get(f"{PREFIX}/gateway")
    assert response.status_code == 503 and response.json()["error"]["code"] == "data_missing"
    assert client.get(f"{PREFIX}/cohort-options").json()["error"]["code"] == "data_missing"


# python -m api load ---------------------------------------------------------------------------------------------


@pytest.fixture
def loader_calls(tmp_path, monkeypatch):
    """The loader commands ensure_data_loaded runs, without running them, with the database at tmp_path."""
    monkeypatch.setenv("UNCF_DATABASE", str(tmp_path / "out" / "pdp.sqlite"))
    for name in ("UNCF_COHORT_URL", "UNCF_COURSE_URL"):
        monkeypatch.delenv(name, raising=False)
    calls: list[list[str]] = []
    monkeypatch.setattr(load.subprocess, "run", lambda command, cwd, check: calls.append(command))
    return calls


def school_files(tmp_path: Path) -> tuple[Path, Path]:
    """Two stand-in school files on disk."""
    cohort, course = tmp_path / "fmu_cohort.csv", tmp_path / "fmu_course.csv"
    cohort.write_text("a\n")
    course.write_text("b\n")
    return cohort, course


def option(command: list[str], name: str) -> str:
    """The value after one option in a command."""
    return command[command.index(name) + 1]


def test_plain_load_builds_the_sample_once(loader_calls, tmp_path) -> None:
    """`python -m api load` builds the sample when no database exists, and leaves an existing one alone."""
    assert load.ensure_data_loaded() is True
    assert option(loader_calls[0], "--sqlite_path") == str((tmp_path / "out" / "pdp.sqlite").resolve())
    assert "--cohort" not in loader_calls[0]
    (tmp_path / "out" / "pdp.sqlite").write_text("")
    assert load.ensure_data_loaded() is False and len(loader_calls) == 1
    assert load.ensure_data_loaded(replace=True) is True and len(loader_calls) == 2


def test_school_files_load_with_the_school_pipeline(loader_calls, tmp_path) -> None:
    """A school's two files always rebuild, through the pipeline without the sample's enrichment files."""
    (tmp_path / "out").mkdir()
    (tmp_path / "out" / "pdp.sqlite").write_text("")
    cohort, course = school_files(tmp_path)
    assert load.ensure_data_loaded(cohort=str(cohort), course=str(course)) is True
    command = loader_calls[0]
    assert option(command, "--config") == str(load.SCHOOL_PIPELINE)
    assert option(command, "--cohort") == str(cohort.resolve()) and option(command, "--course") == str(course.resolve())


def test_load_needs_both_files_that_exist(loader_calls, tmp_path) -> None:
    """One file alone, or a path with no file, stops before the loader runs."""
    cohort, _ = school_files(tmp_path)
    with pytest.raises(load.LoadError, match="both files"):
        load.ensure_data_loaded(cohort=str(cohort))
    with pytest.raises(load.LoadError, match="No course file"):
        load.ensure_data_loaded(cohort=str(cohort), course=str(tmp_path / "nope.csv"))
    assert loader_calls == []


def test_links_from_settings_are_downloaded(loader_calls, tmp_path, monkeypatch) -> None:
    """UNCF_COHORT_URL and UNCF_COURSE_URL download each file, keeping its extension, for a hosted build."""
    monkeypatch.setenv("UNCF_COHORT_URL", "https://storage.example.edu/pdp/cohort.csv?sig=secret")
    monkeypatch.setenv("UNCF_COURSE_URL", "https://storage.example.edu/pdp/course.csv?sig=secret")
    seen: dict[str, bytes] = {}

    def fetch(location):
        """Answer with the link's own name as the file's bytes."""
        return io.BytesIO(location.split("/")[-1].encode())

    def record(command, cwd, check):
        """Read the downloaded files while they still exist."""
        seen["cohort"] = Path(option(command, "--cohort")).read_bytes()
        seen["suffix"] = Path(option(command, "--course")).suffix.encode()

    monkeypatch.setattr(load, "open_link", fetch)
    monkeypatch.setattr(load.subprocess, "run", record)
    assert load.ensure_data_loaded() is True
    assert seen == {"cohort": b"cohort.csv?sig=secret", "suffix": b".csv"}


def test_only_https_links_load(loader_calls, tmp_path) -> None:
    """A plain http link is refused, so a file with student records never travels unencrypted."""
    with pytest.raises(load.LoadError, match="https"):
        load.ensure_data_loaded(cohort="http://example.edu/c.csv", course="http://example.edu/d.csv")


class Response(io.BytesIO):
    """A redirect response's body, which the redirect handler closes."""


@pytest.mark.parametrize("target", ["http://storage.example.edu/pdp/cohort.csv", "ftp://storage.example.edu/c.csv"])
def test_a_redirect_away_from_https_stops_the_download(target) -> None:
    """An https link that redirects to http (or anything but https) is refused before that request is made."""
    request = urllib.request.Request("https://storage.example.edu/pdp/cohort.csv?sig=secret")
    body = Response(b"")
    with pytest.raises(load.LoadError, match="non-https") as refused:
        load.HttpsOnlyRedirects().redirect_request(request, body, 302, "Found", {}, target)
    assert body.closed and "secret" not in str(refused.value)


def test_a_redirect_to_another_https_address_is_followed() -> None:
    """Storage that redirects to another https address (a signed download URL, say) still works."""
    request = urllib.request.Request("https://storage.example.edu/pdp/cohort.csv")
    target = "https://download.example.edu/signed/cohort.csv"
    followed = load.HttpsOnlyRedirects().redirect_request(request, Response(b""), 302, "Found", {}, target)
    assert followed.full_url == target


def test_downloads_use_the_https_only_redirects(monkeypatch) -> None:
    """open_link builds its opener with the https only rule, which replaces urllib's default redirects."""
    built = []
    real = urllib.request.build_opener

    def record(*handlers):
        """Build the real opener, keep it, and stop before any network request."""
        built.append(real(*handlers))
        raise OSError("no network in tests")

    monkeypatch.setattr(load.urllib.request, "build_opener", record)
    with pytest.raises(OSError):
        load.open_link("https://storage.example.edu/pdp/cohort.csv")
    redirects = [h for h in built[0].handlers if isinstance(h, urllib.request.HTTPRedirectHandler)]
    assert [type(h) for h in redirects] == [load.HttpsOnlyRedirects]


def test_entry_point_passes_the_school_files(monkeypatch) -> None:
    """`python -m api load --cohort F --course F` hands both files to the load; a problem exits with its message."""
    calls: list[dict] = []
    monkeypatch.setattr(entry, "ensure_data_loaded", lambda **options: calls.append(options))
    entry.main(["load", "--cohort", "c.csv", "--course", "d.csv"])
    entry.main(["load", "--replace"])
    assert calls == [{"cohort": "c.csv", "course": "d.csv"}, {"replace": True}]

    def refuse(**options):
        """Stand in for a load that finds a problem."""
        raise load.LoadError("Give both files")

    monkeypatch.setattr(entry, "ensure_data_loaded", refuse)
    with pytest.raises(SystemExit, match="Give both files"):
        entry.main(["load", "--cohort", "c.csv"])


@pytest.mark.slow
def test_school_pipeline_loads_and_the_api_reads_it(tmp_path, monkeypatch, client) -> None:
    """End to end: the data model's 10 sample students load as a school's files, and the API answers from them."""
    target = tmp_path / "school.sqlite"
    monkeypatch.setenv("UNCF_DATABASE", str(target))
    assert load.ensure_data_loaded(
        cohort=str(SAMPLE_INPUT / "pdp_cohort_data.csv"), course=str(SAMPLE_INPUT / "pdp_course_data.csv")
    )
    connection = sqlite3.connect(target)
    (students,) = connection.execute("SELECT COUNT(*) FROM student").fetchone()
    (attributes,) = connection.execute("SELECT COUNT(*) FROM student_attribute").fetchone()
    connection.close()
    assert students == 10 and attributes == 0  # no synthetic housing rows on a school's students
    monkeypatch.setattr(data, "data_path", lambda: target)
    route.clear_cache()
    cohorts = client.get(f"{PREFIX}/options").json()["cohorts"]
    assert cohorts and client.get(f"{PREFIX}/gateway", params={"cohort": cohorts[0]}).status_code == 200
