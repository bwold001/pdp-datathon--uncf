"""The extended rate contract preserves counting units without weakening hidden evidence."""

import copy

import pytest
from pydantic import ValidationError

from analytics.contracts_v2 import RatePayload, Receipt
from analytics.tests.test_contracts_v2 import receipt, step


def payload():
    """Specify one overall enrollment rate and a categorical rate with explicit student counts."""
    return {
        "kind": "rate",
        "numerator": 10,
        "denominator": 20,
        "value": 0.5,
        "numerator_unit": "DFW course enrollments",
        "denominator_unit": "classifiable course enrollments",
        "n_students": 12,
        "split": {"D": 8, "F": 1, "W": 1},
        "breakdowns": [
            {
                "status": "ok",
                "group": {"pell": "Y"},
                "numerator": 10,
                "denominator": 20,
                "value": 0.5,
                "numerator_unit": "DFW course enrollments",
                "denominator_unit": "classifiable course enrollments",
            },
            {"status": "suppressed", "reason": "small_group", "group": {"pell": "N"}},
        ],
    }


def test_grouped_rate_roundtrips_and_retains_immutable_dfw_counts():
    """Group metadata and immutable grade counts survive JSON without exposing hidden inputs."""
    parsed = RatePayload.model_validate(payload())
    assert RatePayload.model_validate_json(parsed.model_dump_json()) == parsed
    with pytest.raises(ValidationError):
        parsed.split.D = 9
    raw = parsed.model_dump(mode="json")["breakdowns"][1]
    assert set(raw) == {"status", "reason", "group"}


@pytest.mark.parametrize(
    "change", ["hidden_number", "duplicate", "empty_group", "bad_split"]
)
def test_invalid_grouped_evidence_is_refused(change):
    """Hidden numeric data, ambiguous groups and inconsistent grade totals fail at the boundary."""
    raw = payload()
    if change == "hidden_number":
        raw["breakdowns"][1]["numerator"] = 3
    elif change == "duplicate":
        raw["breakdowns"].append(copy.deepcopy(raw["breakdowns"][0]))
    elif change == "empty_group":
        raw["breakdowns"][0]["group"] = {}
    else:
        raw["split"]["D"] = 9
    with pytest.raises(ValidationError):
        RatePayload.model_validate(raw)


def test_receipt_grouping_must_match_the_executed_request():
    """A valid grouped payload cannot be attached to a differently scoped request."""
    raw = receipt(
        request=step(parameters={"cohort": "2023-24", "group_by": ["pell"]}),
        result={"status": "ok", "payload": payload()},
    )
    assert Receipt.model_validate(raw)
    raw["request"]["parameters"]["group_by"] = ["gender"]
    with pytest.raises(ValidationError, match="grouping"):
        Receipt.model_validate(raw)
