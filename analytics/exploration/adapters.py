"""Bind statistical evidence to the existing receipt and result-policy pipeline."""

from analytics.analysis_service import OperationEvidence
from analytics.contracts_v2 import VersionReference
from analytics.exploration.operations import OPERATIONS
from measures.disclosure import profile


def adapt(operation, evidence):
    """Return ordinary owner evidence with counting metadata for the existing policy stage."""
    spec = OPERATIONS[operation]
    policy = profile(spec.disclosure_profile)
    return OperationEvidence(operation_id=operation, operation_version=spec.version,
        disclosure_profile=VersionReference(id=policy.id, version=policy.version),
        result=evidence.result, context=evidence.context, distinct_units=evidence.distinct_units, group_units=evidence.group_units)
