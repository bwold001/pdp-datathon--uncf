"""Scripted model tests exercise the real analytics database and receipts."""

import asyncio
from types import SimpleNamespace as Block

import pytest
from analytics.service import AnalyticsService
from analytics.tests.analytics_fixtures import build_database, fixture_coverage

from app.chat.schemas import ChatRequest
from app.chat.service import MAX_TOOL_ROUNDS, ChatFailed, answer


class ScriptedModel:
    """Return SDK-shaped responses without calling a provider."""

    def __init__(self, *responses):
        """Record calls and consume a finite response script."""
        self.responses = list(responses)
        self.requests = []
        self.messages = self

    async def create(self, **request):
        """Return the next response, preserving tool result messages for assertions."""
        self.requests.append(request)
        return Block(content=self.responses.pop(0))


def call(analysis, **parameters):
    """A tool call requesting actual calculations."""
    return Block(
        type="tool_use",
        name="run_analysis",
        input={"analysis": analysis, **parameters},
        id="tool_1",
    )


def finish():
    """Model prose must never overwrite or replace deterministic numerical evidence."""
    return Block(type="text", text="The rate is 99.9% and 123 students graduated.")


@pytest.mark.parametrize(
    "analysis,parameters,question",
    [
        (
            "retention",
            {"cohort": "2022-23"},
            "What is the retention rate for all majors in 2022-23?",
        ),
        (
            "graduation",
            {"cohort": "2022-23", "credential": "B", "program": "chemistry_general"},
            "What is the graduation rate for chemistry majors?",
        ),
        (
            "enrollment",
            {},
            "What is enrollment ethnicity by academic program over the past 2 years?",
        ),
    ],
)
def test_three_questions_return_real_receipts(tmp_path, analysis, parameters, question):
    """The agent dispatches approved operations rather than calculating in prose."""
    service = AnalyticsService(build_database(tmp_path / "data.sqlite"), fixture_coverage())
    model = ScriptedModel([call(analysis, **parameters)], [finish()])
    reply = asyncio.run(answer(ChatRequest(prompt=question), model, "test-model", service))
    assert reply.status == "confirmation" and not reply.receipts
    reply = asyncio.run(
        answer(ChatRequest(prompt=question, confirmed=reply.proposals), None, "test", service)
    )
    direct = service.analyze({"analysis": analysis, **parameters})
    assert reply.receipts == direct.receipts
    assert "99.9" not in reply.message and "123" not in reply.message
    assert {t["name"] for t in model.requests[0]["tools"]} == {
        "get_analysis_catalog",
        "get_analysis_definition",
        "run_analysis",
    }


def test_all_receipts_survive_multiple_tools(tmp_path):
    """A later call cannot overwrite the earlier calculation evidence."""
    service = AnalyticsService(build_database(tmp_path / "data.sqlite"), fixture_coverage())
    model = ScriptedModel([call("retention", cohort="2022-23")], [call("enrollment")], [finish()])
    reply = asyncio.run(
        answer(ChatRequest(prompt="Show retention and enrollment"), model, "test-model", service)
    )
    reply = asyncio.run(
        answer(ChatRequest(prompt="confirmed", confirmed=reply.proposals), None, "test", service)
    )
    assert [r.analysis for r in reply.receipts] == ["retention", "enrollment"]


def test_clarification_resumes_only_the_pending_request(tmp_path):
    """A cohort selection resumes the original analysis without model memory."""
    service = AnalyticsService(build_database(tmp_path / "data.sqlite"), fixture_coverage())
    model = ScriptedModel([call("retention")])
    reply = asyncio.run(
        answer(ChatRequest(prompt="What is retention?"), model, "test-model", service)
    )
    assert not reply.receipts and reply.clarification.field == "cohort"
    resumed = asyncio.run(
        answer(
            ChatRequest(
                prompt="2022-23",
                pending=reply.clarification.pending,
                selection={"field": "cohort", "value": "2022-23"},
            ),
            None,
            "test-model",
            service,
        )
    )
    assert resumed.status == "confirmation" and not resumed.receipts
    resumed = asyncio.run(
        answer(ChatRequest(prompt="confirmed", confirmed=resumed.proposals), None, "test", service)
    )
    assert resumed.receipts[0].rows[0].rate == 0.5
    with pytest.raises(ValueError):
        asyncio.run(
            answer(
                ChatRequest(
                    prompt="bad choice",
                    pending=reply.clarification.pending,
                    selection={"field": "program", "value": "anything"},
                ),
                None,
                "test",
                service,
            )
        )


def test_ungrounded_prose_and_sql_are_not_displayed(tmp_path):
    """A provider's fluent unsupported answer is never treated as a calculation."""
    service = AnalyticsService(build_database(tmp_path / "data.sqlite"), fixture_coverage())
    model = ScriptedModel(
        [
            Block(
                type="tool_use",
                name="run_analysis",
                id="bad",
                input={"analysis": "retention", "sql": "SELECT *"},
            )
        ],
        [finish()],
    )
    reply = asyncio.run(
        answer(ChatRequest(prompt="Show individual student records"), model, "test", service)
    )
    assert not reply.receipts and reply.status == "unsupported"
    assert "99.9" not in reply.message


def test_loop_cap_and_missing_key(tmp_path):
    """Provider configuration and bounded execution fail visibly."""
    service = AnalyticsService(build_database(tmp_path / "data.sqlite"), fixture_coverage())
    model = ScriptedModel(
        *[
            [Block(type="tool_use", name="unknown_tool", input={}, id="bad")]
            for _ in range(MAX_TOOL_ROUNDS)
        ]
    )
    with pytest.raises(ChatFailed):
        asyncio.run(answer(ChatRequest(prompt="Keep going"), model, "test", service))
    with pytest.raises(ChatFailed, match="ANTHROPIC_API_KEY"):
        asyncio.run(answer(ChatRequest(prompt="Retention?"), None, "test", service))


def test_clarification_keeps_independent_results_from_the_same_tool_batch(tmp_path):
    """An unresolved cohort must not discard a complete enrollment request beside it."""
    service = AnalyticsService(build_database(tmp_path / "data.sqlite"), fixture_coverage())
    model = ScriptedModel([call("retention"), call("enrollment")])
    reply = asyncio.run(
        answer(ChatRequest(prompt="Show retention and enrollment"), model, "test", service)
    )
    assert reply.clarification.field == "cohort"
    assert not reply.receipts
    assert [request.analysis for request in reply.proposals] == ["enrollment"]
    resumed = asyncio.run(
        answer(
            ChatRequest(
                prompt="original question",
                pending=reply.clarification.pending,
                selection={"field": "cohort", "value": "2022-23"},
                proposals=reply.proposals,
            ),
            None,
            "test",
            service,
        )
    )
    assert [request.analysis for request in resumed.proposals] == ["enrollment", "retention"]
    result = asyncio.run(
        answer(ChatRequest(prompt="confirmed", confirmed=resumed.proposals), None, "test", service)
    )
    assert [r.analysis for r in result.receipts] == ["enrollment", "retention"]
    assert sum(row.count for row in result.receipts[0].rows) == 3


def test_multiple_ambiguous_analyses_explicitly_explain_the_single_pending_scope(tmp_path):
    """A second unresolved analysis is disclosed instead of silently dropped."""
    service = AnalyticsService(build_database(tmp_path / "data.sqlite"), fixture_coverage())
    model = ScriptedModel([call("retention"), call("graduation")])
    reply = asyncio.run(
        answer(ChatRequest(prompt="Show retention and graduation"), model, "test", service)
    )
    assert reply.clarification.pending.analysis == "retention"
    assert "graduation" in reply.message
    assert "separate" in reply.message


def test_dropped_filter_cannot_trigger_an_unconfirmed_calculation(tmp_path, monkeypatch):
    """A model omitting Pell cannot turn a narrower question into a numerical answer."""
    service = AnalyticsService(build_database(tmp_path / "data.sqlite"), fixture_coverage())

    def forbidden(*args):
        raise AssertionError("Numerical execution before user confirmation")

    monkeypatch.setattr(service, "analyze", forbidden)
    model = ScriptedModel([call("retention", cohort="2022-23")], [finish()])
    reply = asyncio.run(
        answer(ChatRequest(prompt="Only Pell recipients in 2022-23"), model, "test", service)
    )
    assert reply.status == "confirmation"
    assert not reply.receipts and len(reply.proposals) == 1
    assert "No additional filters" in reply.message


def test_model_tool_dispatch_only_returns_a_proposal(tmp_path, monkeypatch):
    """There is no numerical back door in the tool dispatcher."""
    from analytics.schemas import AnalysisRequest

    from app.chat.tools import dispatch

    service = AnalyticsService(build_database(tmp_path / "data.sqlite"), fixture_coverage())
    monkeypatch.setattr(service, "analyze", lambda request: pytest.fail("Executed numerical tool"))
    proposed = dispatch(service, "run_analysis", {"analysis": "retention", "cohort": "2022-23"})
    assert isinstance(proposed, AnalysisRequest)
