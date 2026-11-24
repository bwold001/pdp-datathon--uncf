"""The release scorer rejects dropped constraints and keeps model tests separate from execution."""

import json

from analytics.plan_service import refusal
from analytics.tests.test_defined_operations import defined_data, request  # noqa: F401

from app.chat.provider import ToolCall
from scripts.evaluate_release_a import CASES, assess
from tests.test_chat_v2 import proposal, run
from tests.test_chat_v2 import runtime as runtime  # noqa: F401
from tests.test_student_success_tools import ScriptedModel


def test_fixed_suite_covers_every_adapter_and_unsupported_exploration():
    """Keep at least thirty fixed cases and the exact Release A inventory in the evaluation."""
    from analytics.analysis_service import AnalysisService
    from analytics.coverage import Coverage

    cases = json.loads(CASES.read_text())["cases"]
    assert len(cases) >= 30 and len({case["id"] for case in cases}) == len(cases)
    expected = {operation for case in cases for operation in case["operations"]}
    assert expected == set(AnalysisService(Coverage()).operations)
    assert any(
        "online course count" in c["prompt"] and c["expected_status"] == "unsupported"
        for c in cases
    )
    assert any(
        "online course share" in c["prompt"] and c["expected_status"] == "unsupported"
        for c in cases
    )


def test_scorer_detects_dropped_pell_and_unnecessary_clarification(runtime):
    """A plausible proposal cannot pass by choosing the right operation but dropping Pell."""
    case = json.loads(CASES.read_text())["cases"][0]
    for filters, passed in (({"pell": "Y"}, True), ({}, False)):
        model = ScriptedModel(
            [ToolCall("1", "propose_plan", proposal(runtime, request("dfw.rate", filters=filters)))]
        )
        scored = assess(case, run(runtime, model))
        assert scored["routing_correct"] and scored["passed"] == passed
        assert scored["constraints_preserved"] == passed
    pending = {
        "unresolved": True,
        "question": "cohort?",
        "choices": [{"value": "2023-24", "label": "cohort"}],
    }
    model = ScriptedModel(
        [
            ToolCall(
                "1",
                "propose_plan",
                proposal(runtime, request("dfw.rate", cohort=pending, filters={"pell": "Y"})),
            )
        ]
    )
    scored = assess(case, run(runtime, model))
    assert scored["unnecessary_clarification"] and not scored["passed"]


def test_scorer_distinguishes_unsupported_from_provider_failure():
    """A missing provider key cannot count as a successful unsupported refusal."""
    case = next(
        c for c in json.loads(CASES.read_text())["cases"] if c["expected_status"] == "unsupported"
    )
    assert assess(case, refusal("unsupported_operation"))["passed"]
    assert not assess(case, refusal("provider_failed"))["passed"]


def test_missing_key_writes_unverified_evidence_without_opening_a_provider(tmp_path, monkeypatch):
    """A missing key produces an actionable artifact and a failing release exit code."""
    import sys

    from scripts import evaluate_release_a

    output = tmp_path / "evaluation.json"
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "evaluate_release_a",
            "--model",
            "configured/model",
            "--database",
            "absent.sqlite",
            "--output",
            str(output),
        ],
    )
    assert evaluate_release_a.main() == 1
    report = json.loads(output.read_text())
    assert report["status"] == "unverified" and not report["gate_passed"]
    assert report["results"] == [] and report["model"] == "configured/model"
    assert report["cases"] >= 30 and report["suite_sha256"]


def test_gateway_boundary_gate_rejects_the_lower_course_threshold(monkeypatch):
    """A catalog claim of C-or-better cannot pass when course arithmetic accepts 1.99."""
    from scripts import evaluate_release_a

    expected = {
        "0.69": False,
        "0.70": False,
        "1.99": False,
        "2.00": True,
        "P": True,
        "W": False,
        "I": None,
        "unknown": None,
    }
    monkeypatch.setattr(evaluate_release_a, "gateway_passed", expected.get)
    assert evaluate_release_a.gateway_boundary_check()["passed"]
    monkeypatch.setattr(
        evaluate_release_a,
        "gateway_passed",
        lambda grade: True if grade == "1.99" else expected[grade],
    )
    assert not evaluate_release_a.gateway_boundary_check()["passed"]
