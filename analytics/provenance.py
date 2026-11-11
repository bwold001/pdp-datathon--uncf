"""Versioned snapshot identity and replay specifications, separate from execution timestamps."""

import hashlib
import json
import re
from datetime import date, datetime, timezone
from typing import Literal
from uuid import UUID

from pydantic import Field

from analytics.contracts_v2 import (
    Contract, ExecutablePlan, Fingerprint, VersionReference, Versions,
)
from analytics.coverage import Coverage


class DataUnavailable(RuntimeError):
    """A configured source cannot be used; the public message contains no connection details."""

    code = "data_unavailable"


class SnapshotUnavailable(DataUnavailable):
    """The exact requested data generation is not currently available."""

    code = "snapshot_unavailable"


class VersionUnavailable(DataUnavailable):
    """Required build, operation or policy versions cannot be resolved exactly."""

    code = "version_unavailable"


class BuildManifest(Contract):
    """Read the build artifact persisted atomically with normalized rows in load_run."""

    schema_version: Literal[1]
    load_generation: UUID
    pipeline_version: Fingerprint
    normalization_digest: Fingerprint


class SnapshotIdentity(Contract):
    """Carry safe source stamps without exposing internal source paths or provider rows."""

    snapshot_ref: Fingerprint
    source_fingerprint: Fingerprint
    load_generation: UUID
    pipeline_version: Fingerprint
    normalization_digest: Fingerprint
    loaded_at: str


def digest(value) -> str:
    """Hash a version-independent canonical JSON value without lossy fallback conversions."""
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(encoded.encode()).hexdigest()


def _timestamp(value) -> str:
    """Normalize loader UTC timestamps consistently across SQLite and PostgreSQL."""
    if isinstance(value, str):
        value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if isinstance(value, date) and not isinstance(value, datetime):
        value = datetime.combine(value, datetime.min.time())
    return value.replace(tzinfo=value.tzinfo or timezone.utc).astimezone(timezone.utc).isoformat()


def read_snapshot_identity(connection) -> SnapshotIdentity:
    """Pin provider rows and build metadata through the same read transaction as execution."""
    try:
        runs = connection.execute("SELECT * FROM load_run").fetchall()
    except DataUnavailable as error:
        cause = error.__cause__
        if getattr(cause, "sqlstate", None) == "42P01" or "no such table" in str(cause):
            raise VersionUnavailable("Extract lacks build identity; reload it with the current loader.") from error
        raise
    try:
        if len(runs) != 1 or not runs[0].get("build_manifest"):
            raise ValueError("missing build manifest")
        manifest = BuildManifest.model_validate_json(runs[0]["build_manifest"])
    except (ValueError, TypeError) as error:
        raise VersionUnavailable("Extract lacks supported build identity; reload it with the current loader.") from error
    providers = connection.execute("SELECT source_file, file_sha256, loaded_at FROM data_provider").fetchall()
    if not providers:
        raise DataUnavailable("The configured snapshot has no source manifest.")
    sources = [(row["source_file"], row["file_sha256"]) for row in providers]
    if any(not isinstance(v, str) or not v for row in sources for v in row) or any(not re.fullmatch(r"[a-f0-9]{64}", sha) for _, sha in sources):
        raise DataUnavailable("The configured source manifest is invalid.")
    sources.sort()
    source_stamp = digest(sources)
    payload = {"identity_schema": 1, "sources": sources, **manifest.model_dump(mode="json")}
    try:
        loaded = max(_timestamp(row["loaded_at"]) for row in providers)
    except (ValueError, TypeError, AttributeError) as error:
        raise DataUnavailable("The configured source load time is invalid.") from error
    return SnapshotIdentity(snapshot_ref=digest(payload), source_fingerprint=source_stamp,
        load_generation=manifest.load_generation, pipeline_version=manifest.pipeline_version,
        normalization_digest=manifest.normalization_digest, loaded_at=loaded)


def coverage_digest(coverage: Coverage) -> str:
    """Canonicalize declared set-like coverage lists without changing their meaning."""
    raw = coverage.model_dump(mode="json", exclude={"suppression_threshold"})
    for key in ("complete_academic_years", "provisional_retention_cohorts"):
        raw[key] = sorted(set(raw[key]))
    return digest(raw)


class ReplaySpec(Contract):
    """Export the exact computation inputs without accepting execution IDs or timestamps."""

    fingerprint_schema: Literal[2] = 2
    plan: ExecutablePlan
    versions: Versions
    operations: tuple[VersionReference, ...] = Field(min_length=1, max_length=4)
    policies: tuple[VersionReference, ...] = Field(default=(), max_length=4)
    coverage_digest: Fingerprint
    normalization_digest: Fingerprint
    computation_fingerprint: Fingerprint


def _material(spec: ReplaySpec) -> dict:
    """Preserve meaningful plan order while canonicalizing version-reference sets."""
    raw = spec.model_dump(mode="json", exclude={"computation_fingerprint"})
    raw["operations"] = sorted(raw["operations"], key=lambda r: r["id"])
    raw["policies"] = sorted(raw["policies"], key=lambda r: r["id"])
    raw["versions"]["features"] = sorted(raw["versions"]["features"], key=lambda r: r["id"])
    return raw


def _check_operations(plan, operations):
    """Require one unambiguous version for every operation in the whole plan."""
    ids = [v.id for v in operations]
    requested = {s.operation if s.kind == "exploratory_analysis" else s.operation_id for s in plan.steps}
    if len(ids) != len(set(ids)) or set(ids) != requested:
        raise ValueError("operation versions must cover exactly the requested operations")


def make_replay_spec(plan: ExecutablePlan, identity: SnapshotIdentity, versions: Versions,
                     operations: tuple[VersionReference, ...], coverage: Coverage, policies=()) -> ReplaySpec:
    """Build a fingerprint from all computation inputs, never from a unique execution identity."""
    plan = ExecutablePlan.model_validate(plan)
    _check_operations(plan, operations)
    feature_ids = [v.id for v in versions.features]
    if len(feature_ids) != len(set(feature_ids)):
        raise ValueError("feature versions must be unique")
    for step in plan.steps:
        if step.kind == "exploratory_analysis" and step.operation == "correlation":
            if not {step.parameters.x, step.parameters.y} <= set(feature_ids):
                raise VersionUnavailable("The requested feature versions are unavailable.")
            if versions.method is None or versions.method.id != step.parameters.method:
                raise VersionUnavailable("The requested method version is unavailable.")
    if plan.snapshot_ref != identity.snapshot_ref:
        raise SnapshotUnavailable("The requested snapshot is unavailable.")
    if versions.catalog != plan.catalog_version or versions.pipeline != identity.pipeline_version:
        raise VersionUnavailable("The requested computation versions are unavailable.")
    if len({p.id for p in policies}) != len(policies):
        raise ValueError("policy versions must be unique")
    spec = ReplaySpec(plan=plan, versions=versions, operations=operations, policies=policies,
        coverage_digest=coverage_digest(coverage), normalization_digest=identity.normalization_digest,
        computation_fingerprint="0" * 64)
    return spec.model_copy(update={"computation_fingerprint": digest(_material(spec))})


def validate_replay(spec: ReplaySpec, identity: SnapshotIdentity, versions: Versions,
                    operations: tuple[VersionReference, ...], coverage: Coverage, policies=()) -> None:
    """Refuse stale data or absent versions without substituting current inputs."""
    spec = ReplaySpec.model_validate(spec)
    if spec.plan.snapshot_ref != identity.snapshot_ref:
        raise SnapshotUnavailable("The requested snapshot is unavailable.")
    expected = make_replay_spec(spec.plan, identity, versions, operations, coverage, policies)
    if digest(_material(spec)) != spec.computation_fingerprint:
        raise ValueError("replay specification fingerprint is inconsistent")
    if expected.computation_fingerprint != spec.computation_fingerprint:
        raise VersionUnavailable("The original computation versions or configuration are unavailable.")


def step_fingerprint(spec: ReplaySpec, step_id: str) -> str:
    """Bind a step to the whole ordered plan, including ordered siblings and dependencies."""
    spec = ReplaySpec.model_validate(spec)
    if step_id not in {step.step_id for step in spec.plan.steps}:
        raise ValueError("step ID is absent from the replay plan")
    if digest(_material(spec)) != spec.computation_fingerprint:
        raise ValueError("replay specification fingerprint is inconsistent")
    return digest({"fingerprint_schema": 2, "step_id": step_id, "plan": spec.computation_fingerprint})
