"""Capture actual stage implementation/configuration identity without reading raw input rows."""

import hashlib
import json
import platform
from importlib.metadata import version
from pathlib import Path
from uuid import uuid4

import yaml

_ROOT = Path(__file__).resolve().parents[1]


def _digest(value):
    """Hash canonical JSON values rather than process-dependent object representations."""
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def file_digest(path):
    """Fingerprint a configuration file at the stage where it is actually consumed."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def configuration_digest(files):
    """Use logical config names and bytes, independent of checkout location."""
    return _digest(sorted((Path(p).name, file_digest(p)) for p in files))


def pipeline_version():
    """Include implementation, model package declaration and actual transformation runtimes."""
    files = sorted((*(_ROOT / "src").rglob("*.py"), *(_ROOT / "pdp_model").rglob("*.py"), _ROOT / "pyproject.toml"))
    return _digest({"files": [(p.relative_to(_ROOT).as_posix(), file_digest(p)) for p in files],
                    "python": platform.python_version(), "pyyaml": version("PyYAML"), "pyarrow": version("pyarrow")})


def build_manifest(settings, folders, rules):
    """Persist stage evidence, including staged runs; legacy stages remain explicitly unidentified."""
    stages = []
    for source, folder in zip(settings["sources"], folders):
        meta = yaml.safe_load((folder / "source.yaml").read_text()) or {}
        fixes = yaml.safe_load((folder / "fixes.yaml").read_text()) or {}
        mapped, fixed, validated = meta.get("mapping_identity"), fixes.get("build_identity"), meta.get("validation_identity")
        if not all(isinstance(value, dict) for value in (mapped, fixed, validated)):
            return None
        stages.append({"mapping": mapped, "fixes": fixed, "validation": validated,
                       "mapping_name": meta.get("config"), "mapping_mode": meta.get("mode"),
                       "kind": source["kind"], "provider": source["provider"],
                       "order_by": source.get("order_by"), "on_conflict": source.get("on_conflict")})
    pipeline = _digest({"loader": pipeline_version(), "stages": [
        [s[k]["pipeline_version"] for k in ("mapping", "fixes", "validation")] for s in stages]})
    normalization = _digest({"loader_rules": configuration_digest(rules["files"]),
                             "stages": stages, "on_error_rows": settings["on_error_rows"]})
    return json.dumps({"schema_version": 1, "load_generation": str(uuid4()),
                       "pipeline_version": pipeline, "normalization_digest": normalization}, sort_keys=True)
