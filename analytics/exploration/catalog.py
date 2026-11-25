"""Executable feature and grouping semantics for student/cohort exploration."""

from dataclasses import dataclass
from types import MappingProxyType

DATASET_VERSION = "student_year1-1"
MISSINGNESS_VERSION = "complete-cases-1"
METHOD_VERSION = "pearson-1"
COVERAGE = "Observed year-one course records; whole-year exposure completeness is not certified."


@dataclass(frozen=True)
class FeatureSpec:
    """Bind a stable feature to its normalized source, units and eligibility rule."""

    source: str
    unit: str
    missing_rule: str
    version: str = "1"


FEATURES = MappingProxyType({
    "credits_earned_y1": FeatureSpec("cohort_membership.number_of_credits_earned_yr_1", "credits", "Missing cohort credits remain missing; course sums are not substituted."),
    "credits_attempted_y1": FeatureSpec("cohort_membership.number_of_credits_attempted_yr_1", "credits", "Missing cohort credits remain missing; independent of earned-credit eligibility."),
    "online_enrollment_count_y1": FeatureSpec("course_enrollment.delivery_method", "enrollments", "Exclude no records, unresolved terms and unknown delivery; count attempts separately."),
    "online_enrollment_share_y1": FeatureSpec("course_enrollment.delivery_method", "share of observed enrollments", "Same complete exposure rule; positive observed enrollment denominator required."),
    "retained_school": FeatureSpec("measures.retention", "student outcome", "Unknown outcomes are excluded, never not retained."),
    "retained_federal": FeatureSpec("measures.federal_retention", "student outcome", "Unobserved next fall is not_yet_observable, never not retained."),
})
GROUPS = MappingProxyType({
    "online_count_0_1to2_3plus": ("zero", "one_to_two", "three_plus"),
    "retention_outcome_school": ("retained", "not_retained"),
    "retention_outcome_federal": ("retained", "not_retained"),
})
# Only these symmetric pairs are supported; count and share are different exposures.
PAIRS = frozenset(frozenset(pair) for pair in (
    ("credits_earned_y1", "credits_attempted_y1"),
    ("online_enrollment_count_y1", "credits_earned_y1"),
    ("online_enrollment_count_y1", "credits_attempted_y1"),
    ("online_enrollment_share_y1", "credits_earned_y1"),
    ("online_enrollment_share_y1", "credits_attempted_y1"),
))


def group_for(row, grouping):
    """Resolve one registered grouping, retaining the exact exclusion reason."""
    if grouping == "online_count_0_1to2_3plus":
        value = row.online_enrollment_count_y1
        if value is None:
            return None, row.online_reasons
        return ("zero" if value == 0 else "one_to_two" if value <= 2 else "three_plus"), ()
    feature = "retained_school" if grouping == "retention_outcome_school" else "retained_federal"
    value = getattr(row, feature)
    if value is None:
        return None, (getattr(row, feature + "_reason"),)
    return ("retained" if value else "not_retained"), ()


def metadata():
    """Publish executable feature/pair/order metadata without private rows or identifiers."""
    from dataclasses import asdict

    return {
        "dataset": {"id": "student_year1", "version": DATASET_VERSION, "grain": "student and entry cohort", "coverage": COVERAGE},
        "missingness_version": MISSINGNESS_VERSION,
        "features": {key: asdict(value) for key, value in FEATURES.items()},
        "groupings": {key: list(values) for key, values in GROUPS.items()},
        "numeric_pairs": sorted(sorted(pair) for pair in PAIRS),
        "ordered_differences": {key: [[values[j], values[i]] for i in range(len(values)) for j in range(i + 1, len(values))]
            for key, values in GROUPS.items()},
        "gateway_variant": {"available": False, "missing_prerequisite": "Reconciled completion/highest-grade evidence and validated non-attempter eligibility for the same baseline cohort denominator."},
    }
