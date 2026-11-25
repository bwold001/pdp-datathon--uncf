"""The Chemistry chat flow explains missing coverage without model-generated result prose."""

import asyncio

from analytics.analysis_service import AnalysisService
from analytics.coverage import Coverage
from analytics.plan_service import PlanService
from analytics.service import AnalyticsService
from analytics.tests.test_answer_presentation import database as database  # noqa: PLC0414

from app.chat.provider import ToolCall
from app.chat.v2 import ChatRequestV2, answer_v2
from tests.scripted_provider import ScriptedModel


def test_chemistry_clarification_confirmation_and_answer(database, monkeypatch):
    """All three selections survive and no calculation runs before explicit confirmation."""
    runtime = AnalyticsService(database, Coverage())
    catalog = PlanService(runtime).catalog()

    def choice(value):
        """Use valid placeholder options whose labels the server will replace."""
        return {
            "unresolved": True,
            "question": "Provider placeholder",
            "choices": [{"value": value, "label": "placeholder"}],
        }

    proposal = {
        "kind": "proposed",
        "catalog_version": catalog.catalog_version,
        "snapshot_ref": catalog.snapshot_ref,
        "steps": [
            {
                "kind": "legacy_analysis",
                "operation_id": "legacy.graduation",
                "step_id": "graduation",
                "parameters": {
                    "cohort": choice("2022-23"),
                    "credential": choice("B"),
                    "program": choice("chemistry_family"),
                },
            }
        ],
    }
    model = ScriptedModel([ToolCall("1", "propose_plan", proposal)])
    original = AnalysisService.execute

    def forbidden(*args, **kwargs):
        """Keep every pre-confirmation exchange metadata-only."""
        raise AssertionError("Calculated before confirmation")

    monkeypatch.setattr(AnalysisService, "execute", forbidden)
    prompt = "What is the graduation rate for chemistry majors?"
    result = asyncio.run(
        answer_v2(ChatRequestV2(protocol_version=2, prompt=prompt), model, "scripted", runtime)
    )
    for parameter, value in (
        ("cohort", "2022-23"),
        ("credential", "B"),
        ("program", "chemistry_family"),
    ):
        assert result.status == "clarification"
        assert result.clarification.parameter == parameter
        assert any(item.value == value for item in result.clarification.choices)
        assert not result.receipts
        result = asyncio.run(
            answer_v2(
                ChatRequestV2(
                    protocol_version=2,
                    prompt=prompt,
                    plan=result.plan,
                    selection={"step_id": "graduation", "parameter": parameter, "value": value},
                ),
                None,
                "",
                runtime,
            )
        )
    assert result.status == "confirmation" and not result.receipts
    assert any("haven't verified" in item.message for item in result.guidance)
    monkeypatch.setattr(AnalysisService, "execute", original)
    confirmed = result.plan
    result = asyncio.run(
        answer_v2(
            ChatRequestV2(protocol_version=2, prompt=prompt, confirmed=confirmed), None, "", runtime
        )
    )
    assert result.status == "answer"
    receipt = result.receipts[0]
    assert receipt.request == confirmed.steps[0]
    assert receipt.presentation.summary == "A graduation rate isn't available for this selection."
    assert "Bachelor's degree" in receipt.presentation.scope
    assert len(receipt.result.payload.rows) == 15
