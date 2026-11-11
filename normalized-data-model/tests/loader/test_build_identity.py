"""Persist actual build evidence in the same transaction as normalized data."""

import json
import sqlite3

import pytest
import yaml

from src.loader import backends
from src.loader.load import load
from tests.loader.test_load import make_config, staged_run


def manifest(tmp_path):
    """Read only the internal build artifact from the synthetic test database."""
    with sqlite3.connect(tmp_path / "output/pdp.sqlite") as db:
        return json.loads(db.execute("SELECT build_manifest FROM load_run").fetchone()[0])


def test_reloading_same_sources_changes_generation_not_pipeline_or_normalization(tmp_path):
    """Independent loads of identical bytes must not impersonate one historical generation."""
    config = make_config(tmp_path)
    load(config, run_id="one")
    first = manifest(tmp_path)
    load(config, run_id="two")
    second = manifest(tmp_path)
    assert first["load_generation"] != second["load_generation"]
    assert first["pipeline_version"] == second["pipeline_version"]
    assert first["normalization_digest"] == second["normalization_digest"]


def test_staged_load_retains_fix_configuration_evidence_and_legacy_stages_are_unidentified(tmp_path):
    """The fixes that actually ran are retained even if today's fixes file differs."""
    config = staged_run(tmp_path)
    folders = sorted((tmp_path / "staging/r/validated").iterdir())
    original = yaml.safe_load((folders[0] / "fixes.yaml").read_text())["build_identity"]
    assert len(original["configuration_digest"]) == 64
    load(config, staging=tmp_path / "staging/r", run_id="first")
    first = manifest(tmp_path)
    recorded = folders[0] / "fixes.yaml"
    value = yaml.safe_load(recorded.read_text())
    value["build_identity"]["configuration_digest"] = "f" * 64
    recorded.write_text(yaml.safe_dump(value))
    load(config, staging=tmp_path / "staging/r", run_id="second")
    assert manifest(tmp_path)["normalization_digest"] != first["normalization_digest"]
    value.pop("build_identity")
    recorded.write_text(yaml.safe_dump(value))
    load(config, staging=tmp_path / "staging/r", run_id="legacy")
    with sqlite3.connect(tmp_path / "output/pdp.sqlite") as db:
        assert db.execute("SELECT build_manifest FROM load_run").fetchone()[0] is None


def test_failed_commit_preserves_previous_rows_and_manifest(tmp_path, monkeypatch):
    """A load cannot publish a new build identity while rolling back its data."""
    config = make_config(tmp_path)
    load(config, run_id="before")
    before = manifest(tmp_path)

    def refused(connection):
        """Fail at the commit boundary after the new rows and manifest were written."""
        raise sqlite3.OperationalError("synthetic commit failure")

    monkeypatch.setattr(backends.BACKENDS["sqlite"], "commit", refused)
    with pytest.raises(RuntimeError):
        load(config, run_id="failed")
    assert manifest(tmp_path) == before
    with sqlite3.connect(tmp_path / "output/pdp.sqlite") as db:
        assert db.execute("SELECT run_id FROM load_run").fetchone() == ("before",)
