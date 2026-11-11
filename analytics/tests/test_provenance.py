"""Computation identity and replay tests use explicit synthetic inputs, not wall-clock assumptions."""

import json

import pytest

from analytics.contracts_v2 import ExecutablePlan, VersionReference, Versions
from analytics.coverage import Coverage
from analytics.data_access import sqlite_snapshot
from analytics.provenance import SnapshotUnavailable, VersionUnavailable, make_replay_spec, step_fingerprint, validate_replay
from analytics.tests.test_snapshots import add_identity, database as database


def inputs(identity):
    """Specify stable calculation inputs independently of any execution ID or timestamp."""
    plan = ExecutablePlan.model_validate({"kind": "executable", "catalog_version": "1", "snapshot_ref": identity.snapshot_ref,
        "steps": [{"kind": "defined_measure", "step_id": "retention", "operation_id": "retention.rate",
                   "parameters": {"cohort": "2023-24", "filters": {"pell": "Y"}, "retention_type": "school"}}]})
    versions = Versions(catalog="1", pipeline=identity.pipeline_version, configuration="1", coverage="1", implementation="1", disclosure="dashboard_v1")
    operations = (VersionReference(id="retention.rate", version="1"),)
    return plan, versions, operations, Coverage(provenance="Synthetic fixture")


def test_same_snapshot_and_request_have_stable_computation_identity(database):
    """Pure computation fingerprints are repeatable and export no run timestamps or IDs."""
    with sqlite_snapshot(database) as snapshot:
        plan, versions, operations, coverage = inputs(snapshot.identity)
        one = make_replay_spec(plan, snapshot.identity, versions, operations, coverage)
        two = make_replay_spec(plan, snapshot.identity, versions, operations, coverage)
        assert one == two
        assert not {"execution_id", "started_at", "completed_at", "duration"} & one.model_dump().keys()
        validate_replay(one, snapshot.identity, versions, operations, coverage)
        assert make_replay_spec(plan, snapshot.identity, versions, operations, coverage,
            ("linked-partition",)).computation_fingerprint != one.computation_fingerprint


@pytest.mark.parametrize("field", ["implementation", "configuration", "coverage", "disclosure"])
def test_missing_original_versions_cannot_silently_replay_on_new_versions(database, field):
    """Changing any computation version changes identity and rejects the original replay."""
    with sqlite_snapshot(database) as snapshot:
        plan, versions, operations, coverage = inputs(snapshot.identity)
        original = make_replay_spec(plan, snapshot.identity, versions, operations, coverage)
        newer = Versions.model_validate({**versions.model_dump(), field: "2"})
        assert make_replay_spec(plan, snapshot.identity, newer, operations, coverage).computation_fingerprint != original.computation_fingerprint
        with pytest.raises(VersionUnavailable):
            validate_replay(original, snapshot.identity, newer, operations, coverage)


def test_reload_is_a_different_snapshot_even_when_source_bytes_are_unchanged(database):
    """The generation is authoritative; identical source hashes do not identify a historical load."""
    with sqlite_snapshot(database) as snapshot:
        first = snapshot.identity
        plan, versions, operations, coverage = inputs(first)
        replay = make_replay_spec(plan, first, versions, operations, coverage)
    add_identity(database, "00000000-0000-4000-8000-000000000099")
    with sqlite_snapshot(database) as snapshot:
        assert first.source_fingerprint == snapshot.identity.source_fingerprint
        assert first.snapshot_ref != snapshot.identity.snapshot_ref
        with pytest.raises(SnapshotUnavailable):
            validate_replay(replay, snapshot.identity, versions, operations, coverage)


def test_coverage_and_operation_changes_affect_the_fingerprint(database):
    """Operation versions and actual coverage values are inputs, not presentation metadata."""
    with sqlite_snapshot(database) as snapshot:
        plan, versions, operations, coverage = inputs(snapshot.identity)
        first = make_replay_spec(plan, snapshot.identity, versions, operations, coverage)
        changed = Coverage(provenance="Another certified synthetic declaration")
        assert first.computation_fingerprint != make_replay_spec(plan, snapshot.identity, versions, operations, changed).computation_fingerprint
        with pytest.raises(VersionUnavailable):
            validate_replay(first, snapshot.identity, versions, operations, changed)
        newer = (VersionReference(id="retention.rate", version="2"),)
        with pytest.raises(VersionUnavailable):
            validate_replay(first, snapshot.identity, versions, newer, coverage)
        altered = json.loads(first.model_dump_json())
        altered["computation_fingerprint"] = "0" * 64
        with pytest.raises(ValueError, match="fingerprint"):
            validate_replay(type(first).model_validate(altered), snapshot.identity, versions, operations, coverage)


def test_ordered_siblings_and_dependencies_change_step_identity(database):
    """A step cannot reuse its isolated identity when the returned disclosure set changes."""
    with sqlite_snapshot(database) as snapshot:
        plan, versions, operations, coverage = inputs(snapshot.identity)
        original = make_replay_spec(plan, snapshot.identity, versions, operations, coverage)
        raw = plan.model_dump(mode="json")
        raw["steps"].append({**raw["steps"][0], "step_id": "sibling"})
        together = make_replay_spec(ExecutablePlan.model_validate(raw), snapshot.identity, versions, operations, coverage)
        assert step_fingerprint(original, "retention") != step_fingerprint(together, "retention")
        raw["steps"].reverse()
        reordered = make_replay_spec(ExecutablePlan.model_validate(raw), snapshot.identity, versions, operations, coverage)
        assert reordered.computation_fingerprint != together.computation_fingerprint
        raw["steps"][1]["depends_on"] = ["sibling"]
        dependent = make_replay_spec(ExecutablePlan.model_validate(raw), snapshot.identity, versions, operations, coverage)
        assert dependent.computation_fingerprint != reordered.computation_fingerprint
        with pytest.raises(ValueError, match="absent"):
            step_fingerprint(dependent, "missing")


def test_correlation_requires_feature_and_method_versions_and_canonicalizes_reference_sets(database):
    """Missing feature/method evidence is refused; equivalent reference ordering is stable."""
    with sqlite_snapshot(database) as snapshot:
        plan, versions, _, coverage = inputs(snapshot.identity)
        raw = plan.model_dump(mode="json")
        raw["steps"] = [{"kind": "exploratory_analysis", "step_id": "relationship", "operation": "correlation",
                         "dataset_id": "student_year1", "parameters": {"cohort": "2023-24",
                         "x": "credits_earned_y1", "y": "online_enrollment_share_y1"}}]
        plan = ExecutablePlan.model_validate(raw)
        operations = (VersionReference(id="correlation", version="1"),)
        with pytest.raises(VersionUnavailable, match="feature"):
            make_replay_spec(plan, snapshot.identity, versions, operations, coverage)
        raw_versions = versions.model_dump(mode="json")
        raw_versions["features"] = [{"id": key, "version": "1"} for key in ("credits_earned_y1", "online_enrollment_share_y1")]
        with pytest.raises(VersionUnavailable, match="method"):
            make_replay_spec(plan, snapshot.identity, Versions.model_validate(raw_versions), operations, coverage)
        raw_versions["method"] = {"id": "pearson", "version": "1"}
        original = make_replay_spec(plan, snapshot.identity, Versions.model_validate(raw_versions), operations, coverage, ("a", "b"))
        raw_versions["features"].reverse()
        reordered = make_replay_spec(plan, snapshot.identity, Versions.model_validate(raw_versions), operations, coverage, ("b", "a"))
        assert original.computation_fingerprint == reordered.computation_fingerprint
