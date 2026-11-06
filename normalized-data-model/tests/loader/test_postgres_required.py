"""Checks that PDP_REQUIRE_POSTGRES=1 turns a skipped PostgreSQL test, and only a PostgreSQL test, into a failure (conftest.py)."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

BUILD = Path(__file__).resolve().parents[2]


def run_postgres_tests(**environ):
    env = {k: v for k, v in os.environ.items() if k not in ("PDP_TEST_POSTGRES_URL", "PDP_REQUIRE_POSTGRES")}
    env.update(environ)
    return subprocess.run([sys.executable, "-m", "pytest", "-q", "-m", "postgres", "-p", "no:cacheprovider",
                           "tests/loader/test_load.py"], cwd=BUILD, env=env, capture_output=True, text=True)


def run_with_postgres_required(tmp_path, test_file, *args):
    """Runs test_file's text as a test file next to a copy of conftest.py, with PDP_REQUIRE_POSTGRES=1."""
    shutil.copy(BUILD / "conftest.py", tmp_path / "conftest.py")
    (tmp_path / "test_other.py").write_text("import pytest\n\n\n" + test_file)
    env = {k: v for k, v in os.environ.items() if k != "PDP_TEST_POSTGRES_URL"}
    env["PDP_REQUIRE_POSTGRES"] = "1"
    return subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *args, "test_other.py"],
                          cwd=tmp_path, env=env, capture_output=True, text=True)


def test_without_a_database_the_postgres_tests_skip():
    result = run_postgres_tests()
    assert result.returncode == 0, result.stdout
    assert "failed" not in result.stdout


def test_with_postgres_required_and_no_database_they_fail_instead_of_skipping():
    result = run_postgres_tests(PDP_REQUIRE_POSTGRES="1")
    assert result.returncode == 1, result.stdout
    assert "PDP_REQUIRE_POSTGRES=1, but this PostgreSQL test skipped" in result.stdout
    assert "skipped" not in result.stdout.splitlines()[-1]


def test_with_postgres_required_a_skip_that_isnt_a_postgres_test_still_skips(tmp_path):
    result = run_with_postgres_required(
        tmp_path, "@pytest.mark.skip(reason='not a PostgreSQL test')\ndef test_other():\n    pass\n")
    assert result.returncode == 0, result.stdout
    assert "1 skipped" in result.stdout.splitlines()[-1]


def test_with_postgres_required_a_test_using_the_postgres_fixture_fails_without_the_marker(tmp_path):
    result = run_with_postgres_required(
        tmp_path, "@pytest.fixture\ndef postgres():\n    pytest.skip('no server')\n\n\n"
                  "def test_other(postgres):\n    pass\n", "-m", "postgres")
    assert result.returncode == 1, result.stdout
    assert "PDP_REQUIRE_POSTGRES=1, but this PostgreSQL test skipped" in result.stdout
    assert "1 error" in result.stdout.splitlines()[-1]  # the fixture skips during setup, so pytest says error


def test_with_postgres_required_an_expected_failure_stays_one(tmp_path):
    result = run_with_postgres_required(
        tmp_path, "@pytest.mark.postgres\n@pytest.mark.xfail(reason='known')\ndef test_other():\n    assert False\n")
    assert result.returncode == 0, result.stdout
    assert "1 xfailed" in result.stdout.splitlines()[-1]
