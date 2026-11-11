"""Scripted proposals and exact confirmation over independently counted synthetic evidence."""

import asyncio

import pytest
from analytics.coverage import Coverage
from analytics.plan_service import PlanService
from analytics.service import AnalyticsService
from analytics.tests.test_defined_operations import defined_data as defined_data  # noqa: F401
from analytics.tests.test_defined_operations import request

from app.chat.provider import ToolCall
from app.chat.v2 import ChatRequestV2, answer_v2
from tests.test_student_success_tools import ScriptedModel


@pytest.fixture
def runtime(defined_data):
    """Use twelve synthetic students with twelve DFW enrollments among twenty-four grades."""
    return AnalyticsService(defined_data, Coverage())


def proposal(runtime, *steps):
    """Bind complete proposals to the real fixture metadata."""
    catalog = PlanService(runtime).catalog()
    return {
        "kind": "proposed",
        "snapshot_ref": catalog.snapshot_ref,
        "catalog_version": catalog.catalog_version,
        "steps": list(steps),
    }


def run(runtime, model=None, **payload):
    """Drive the production chat owner with a bounded scripted provider."""
    return asyncio.run(
        answer_v2(
            ChatRequestV2(
                protocol_version=2, prompt="DFW for Pell and credit-tier retention", **payload
            ),
            model,
            "scripted",
            runtime,
        )
    )


def test_proposal_then_exact_execution_without_provider(runtime, monkeypatch):
    """Pell DFW and tier retention are proposed without calculating; confirmation executes once."""
    from measures import service

    original = service.execute

    def forbidden(*args, **kwargs):
        """Ensure metadata and proposal tools cannot execute formulas."""
        pytest.fail("calculated before confirmation")

    monkeypatch.setattr(service, "execute", forbidden)
    first = request("dfw.rate", filters={"pell": "Y"})
    second = {**request("credit_momentum.summary", retention_type="school"), "step_id": "tiers"}
    model = ScriptedModel([ToolCall("1", "propose_plan", proposal(runtime, first, second))])
    result = run(runtime, model)
    assert result.status == "confirmation" and not result.receipts
    assert result.plan.steps[0].parameters.filters.pell == "Y"
    monkeypatch.setattr(service, "execute", original)
    executed = run(runtime, confirmed=result.plan)
    assert len(model.requests) == 1
    assert executed.status == "answer" and executed.outcome == "complete"
    assert executed.receipts[0].result.payload.value == 0.5
    assert executed.receipts[0].result.payload.denominator == 24
    assert executed.receipts[0].request == result.plan.steps[0]
    assert executed.protocol_version == 2


def test_clarification_preserves_every_step_and_filter(runtime):
    """The server replaces offered choices and resolves only the addressed step parameter."""
    pending = {
        "unresolved": True,
        "question": "provider question",
        "choices": [{"value": "2020-21", "label": "provider choice"}],
    }
    first = request("dfw.rate", cohort=pending, filters={"pell": "Y"})
    second = {**request("credit_momentum.summary", retention_type="school"), "step_id": "tiers"}
    model = ScriptedModel([ToolCall("1", "propose_plan", proposal(runtime, first, second))])
    result = run(runtime, model)
    assert result.status == "clarification"
    assert result.clarification.choices[0].value == "2023-24"
    selected = run(
        runtime,
        plan=result.plan,
        selection={"step_id": "result", "parameter": "cohort", "value": "2023-24"},
    )
    assert selected.status == "confirmation"
    assert selected.plan.steps[0].parameters.filters.pell == "Y"
    assert selected.plan.steps[1].model_dump() == result.plan.steps[1].model_dump()
    bad = run(
        runtime,
        plan=result.plan,
        selection={"step_id": "result", "parameter": "cohort", "value": "2020-21"},
    )
    assert bad.issues[0].code == "unsupported_parameter"


def test_stale_confirmation_requires_updated_review(runtime):
    """A stale snapshot produces review state without silently calculating a new snapshot."""
    plan = (
        PlanService(runtime)
        .validate(proposal_to_model(proposal(runtime, request("dfw.rate"))))
        .plan
    )
    stale = plan.model_copy(update={"snapshot_ref": "old"})
    result = run(runtime, confirmed=stale)
    assert result.status == "confirmation" and not result.receipts
    assert result.plan.snapshot_ref == plan.snapshot_ref
    assert "changed" in result.message


def proposal_to_model(raw):
    """Parse fixture proposals through the public strict contract."""
    from analytics.contracts_v2 import ProposedPlan

    return ProposedPlan.model_validate(raw)


def test_provider_prose_failure_limits_and_exploration(runtime):
    """Numerical provider prose and unsupported operations never produce evidence."""
    from app.chat.provider import ProviderFailed

    class Failed:
        """Fail without exposing provider details."""

        async def complete(self, **kwargs):
            """Represent a sanitized provider outage."""
            raise ProviderFailed("unsafe provider body")

    assert run(runtime, Failed()).issues[0].code == "provider_failed"
    assert run(runtime, ScriptedModel(["99.9 percent"])).receipts == ()
    calls = [ToolCall(str(i), "search_catalog", {"query": "DFW"}) for i in range(7)]
    assert run(runtime, ScriptedModel(calls)).issues[0].code == "limit_exceeded"
    raw = proposal(
        runtime,
        {
            "step_id": "explore",
            "kind": "exploratory_analysis",
            "dataset_id": "student_year1",
            "operation": "correlation",
            "parameters": {
                "cohort": "2023-24",
                "x": "credits_earned_y1",
                "y": "online_enrollment_count_y1",
            },
        },
    )
    result = run(runtime, ScriptedModel([ToolCall("1", "propose_plan", raw)]))
    assert result.issues[0].code == "unsupported_operation" and not result.receipts


def test_http_v2_dispatch_and_invalid_input(client, runtime):
    """Explicit v2 serialization preserves small evidence and sanitizes rejected paths."""
    from api.analyses import get_service

    from app.chat.routes import get_chat_client
    from app.main import app

    app.dependency_overrides[get_service] = lambda: runtime
    app.dependency_overrides[get_chat_client] = lambda: None
    try:
        confirmed = (
            PlanService(runtime)
            .validate(proposal_to_model(proposal(runtime, request("dfw.rate"))))
            .plan
        )
        response = client.post(
            "/api/v1/uncf/chat",
            json={
                "protocol_version": 2,
                "prompt": "confirm",
                "confirmed": confirmed.model_dump(mode="json"),
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["protocol_version"] == 2 and body["outcome"] == "complete"
        assert body["receipts"][0]["result"]["payload"]["value"] == 0.5
        bad = client.post(
            "/api/v1/uncf/chat",
            json={
                "protocol_version": 2,
                "prompt": "question",
                "selection": {
                    "step_id": "dfw",
                    "parameter": "filters.pell",
                    "value": "unsafe-value",
                },
            },
        )
        assert bad.status_code == 422 and bad.json()["protocol_version"] == 2
        assert "unsafe-value" not in bad.text
    finally:
        app.dependency_overrides.pop(get_service, None)
        app.dependency_overrides.pop(get_chat_client, None)


@pytest.mark.parametrize("size", range(1, 10))
@pytest.mark.parametrize("old_threshold", [10, 100])
def test_small_zero_rates_serialize_without_hiding(tmp_path, size, old_threshold, monkeypatch):
    """Every nonempty size keeps zero rates and overlapping sibling evidence under old settings."""
    from analytics.tests.test_snapshots import add_identity
    from measures.tests.explorer_fixture import here, make_database, student

    monkeypatch.setenv("UNCF_MIN_STUDENTS", str(old_threshold))
    path = make_database(
        tmp_path / "small.sqlite",
        [student(f"s{i}", retention=0) for i in range(size)],
        [here(f"s{i}", "2023-24", "FALL", grade="2.0") for i in range(size)],
    )
    add_identity(path)
    runtime = AnalyticsService(path, Coverage())
    first = request("retention.rate", retention_type="school")
    second = {**request("dfw.rate"), "step_id": "dfw"}
    ready = PlanService(runtime).validate(proposal_to_model(proposal(runtime, first, second)))
    result = run(runtime, confirmed=ready.plan).model_dump(mode="json")
    assert result["outcome"] == "complete"
    for receipt in result["receipts"]:
        payload = receipt["result"]["payload"]
        assert payload["value"] == 0
        assert payload["denominator"] == size and payload["n_students"] == size
    assert "small_group" not in str(result)


def test_catalog_tools_and_round_budget(runtime):
    """Catalog tools expose only Release A, and metadata-only conversations are bounded."""
    import json

    from app.chat.v2 import tools

    proposal_schema = tools()[2]["function"]["parameters"]
    serialized = json.dumps(proposal_schema)
    assert "exploratory_analysis" not in serialized
    assert "legacy.annual_enrollment" in serialized
    for operation in PlanService(runtime).owner.operations:
        assert operation in serialized
    scripted = ScriptedModel(
        [ToolCall("1", "search_catalog", {"query": "Pell DFW"})],
        [ToolCall("2", "operation_details", {"operation_id": "dfw.rate"})],
        [
            ToolCall(
                "3", "propose_plan", proposal(runtime, request("dfw.rate", filters={"pell": "Y"}))
            )
        ],
    )
    assert run(runtime, scripted).status == "confirmation"
    assert len(scripted.requests) == 3
    exhausted = ScriptedModel(
        *[[ToolCall(str(i), "search_catalog", {"query": "DFW"})] for i in range(6)]
    )
    assert run(runtime, exhausted).issues[0].code == "limit_exceeded"
    assert len(exhausted.requests) == 6


def test_confirmation_dependency_needs_no_provider_configuration(monkeypatch):
    """The confirmation dependency bypasses provider keys, SDK setup and model selection."""
    from app.chat.routes import get_chat_client
    from app.core.config import settings

    monkeypatch.setattr(settings, "OPENROUTER_API_KEY", None)
    payload = ChatRequestV2(
        protocol_version=2,
        prompt="confirm",
        confirmed={
            "kind": "executable",
            "catalog_version": "2",
            "snapshot_ref": "fixture",
            "steps": [request("dfw.rate")],
        },
    )

    async def check():
        """Consume and close the actual request dependency."""
        dependency = get_chat_client(payload)
        assert await anext(dependency) is None
        await dependency.aclose()

    asyncio.run(check())
