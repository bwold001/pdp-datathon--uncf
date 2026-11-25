"""Release B evaluation expectations stay distinct from scripted execution evidence."""

import json

from analytics.tests.test_defined_operations import defined_data as defined_data  # noqa: F401

from app.chat.provider import ToolCall
from scripts.evaluate_release_a import assess
from scripts.evaluate_release_b import CASES
from tests.scripted_provider import ScriptedModel
from tests.test_chat_v2 import proposal, run
from tests.test_chat_v2 import runtime as runtime  # noqa: F401


def test_release_b_inventory_and_critical_cases():
    """Keep a fixed set above thirty prompts with supported exploration and honest refusals."""
    cases = json.loads(CASES.read_text())["cases"]
    assert len(cases) == 41
    assert len({case["id"] for case in cases}) == 41
    assert {op for c in cases for op in c["operations"]} >= {
        "grouped_summary",
        "mean_comparison",
        "correlation",
        "legacy.graduation",
    }
    assert any(
        "fewer than 10" in c["prompt"] and c["expected_status"] == "confirmation" for c in cases
    )
    assert any("causes" in c["prompt"] and c["expected_status"] == "unsupported" for c in cases)


def test_shared_scorer_checks_exploration_selector_and_constraints(runtime):
    """Correct operation selection cannot compensate for silently changing count into share."""
    case = next(c for c in json.loads(CASES.read_text())["cases"] if c["id"] == "a20")
    for x, expected in (
        ("online_enrollment_count_y1", True),
        ("online_enrollment_share_y1", False),
    ):
        step = {
            "kind": "exploratory_analysis",
            "operation": "correlation",
            "dataset_id": "student_year1",
            "step_id": "relationship",
            "parameters": {"cohort": "2023-24", "x": x, "y": "credits_earned_y1"},
        }
        model = ScriptedModel([ToolCall("1", "propose_plan", proposal(runtime, step))])
        score = assess(case, run(runtime, model))
        assert score["routing_correct"] and score["passed"] == expected
