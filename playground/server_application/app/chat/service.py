"""Bounded provider tool loop; all displayed numbers come from deterministic receipts."""

import asyncio
import json

from analytics.schemas import AnalysisRequest, AnalysisResponse
from analytics.service import AnalyticsService
from app.chat.schemas import ChatRequest, ChatResponse
from app.chat.tools import TOOLS, dispatch

MAX_TOOL_ROUNDS = 6
MAX_TOOLS_PER_ROUND = 6
RULES = """Answer only graduation by chemistry program, retention overall/by entry major, and
annual enrollment by ethnicity/program. Use get_analysis_catalog to learn choices and coverage.
Use run_analysis to propose a scope. It never executes numerical calculations. Never choose a cohort, credential or chemistry definition
when the question leaves it unspecified: omit that parameter so the tool requests clarification.
Chemistry alone is ambiguous between chemistry_general and chemistry_family. Do not use course
subjects as majors. For retention all majors, omit program and request the cohort.
Annual enrollment uses the latest two certified complete years across all entry cohorts.
Graduation returns all horizons and entrant/completion-program perspectives; preserve them all.
No SQL, student records, causal claims or other analyses are supported. Data is synthetic.
Do not execute a different analysis to substitute for an unsupported request.
Numerical answers and calculation text are rendered directly from receipts, not your prose."""


class ChatFailed(Exception):
    """The provider is unconfigured or exhausted its bounded tool loop."""


def response_for(result: AnalysisResponse) -> ChatResponse:
    """Project a service result into the chat contract without model-written numbers."""
    if result.clarification:
        return ChatResponse(
            status="clarification",
            message=result.clarification.message,
            clarification=result.clarification,
        )
    return ChatResponse(
        status="answer",
        message="Results and calculation details are below. These describe synthetic data, not real students or institutions.",
        receipts=result.receipts,
    )


def confirmation(proposals: list[AnalysisRequest]) -> ChatResponse:
    """Require the user to approve the full scope before any calculation."""
    return ChatResponse(
        status="confirmation", proposals=proposals,
        message="Review the complete scope below. No additional filters will be applied. "
                "If it omits a filter from your question, do not confirm; start over.",
    )


async def answer(
    payload: ChatRequest, client, model: str, service: AnalyticsService
) -> ChatResponse:
    """The model proposes; only explicit user confirmation executes calculations."""
    if payload.confirmed is not None:
        receipts = []
        # Validate every scope before executing any of the batch.
        for request in payload.confirmed:
            if await asyncio.to_thread(service.clarify, request):
                raise ValueError("Resolve all required parameters before confirming")
        for request in payload.confirmed:
            result = await asyncio.to_thread(service.analyze, request)
            receipts.extend(result.receipts)
        return response_for(AnalysisResponse(receipts=receipts))
    if payload.pending:
        current = await asyncio.to_thread(service.clarify, payload.pending)
        selection = payload.selection
        if (not current or selection.field != current.field
                or selection.value not in {c["value"] for c in current.choices}):
            raise ValueError("Choose one of the current clarification options")
        request = AnalysisRequest.model_validate(
            {**payload.pending.model_dump(), selection.field: selection.value}
        )
        unresolved = await asyncio.to_thread(service.clarify, request)
        if unresolved:
            return ChatResponse(status="clarification", message=unresolved.message,
                                clarification=unresolved, proposals=payload.proposals)
        return confirmation([*payload.proposals, request])
    if client is None:
        raise ChatFailed("UNCF chat needs ANTHROPIC_API_KEY in the server environment.")
    messages = [{"role": "user", "content": payload.prompt}]
    proposals = []
    for _ in range(MAX_TOOL_ROUNDS):
        response = await client.messages.create(
            model=model, max_tokens=1500, system=RULES, tools=TOOLS, messages=messages
        )
        uses = [b for b in response.content if b.type == "tool_use"]
        if not uses:
            if proposals:
                return confirmation(proposals)
            return ChatResponse(status="unsupported", message=(
                "I can propose graduation by chemistry program, retention by entry major, "
                "and enrollment by ethnicity/program. No supported scope was returned."))
        if len(uses) > MAX_TOOLS_PER_ROUND:
            raise ChatFailed("The assistant requested too many tools in one round.")
        messages.append({"role": "assistant", "content": list(response.content)})
        outputs = []
        clarification = None
        additional_analyses = set()
        for use in uses:
            try:
                result = await asyncio.to_thread(dispatch, service, use.name, dict(use.input or {}))
                if isinstance(result, AnalysisRequest):
                    unresolved = await asyncio.to_thread(service.clarify, result)
                    if unresolved:
                        if clarification is None:
                            clarification = unresolved
                        else:
                            additional_analyses.add(unresolved.pending.analysis)
                        result = {"clarification": unresolved.model_dump(mode="json")}
                    else:
                        if result not in proposals:
                            proposals.append(result)
                        result = {"confirmation_required": True,
                                  "proposal": result.model_dump(mode="json")}
                error = False
            except (ValueError, TypeError):
                result, error = {"error": "Unsupported tool or scope parameters."}, True
            outputs.append({"type": "tool_result", "tool_use_id": use.id,
                            "content": json.dumps(result), "is_error": error})
        if clarification:
            message = clarification.message
            if additional_analyses:
                names = ", ".join(sorted(additional_analyses))
                message += f" Also requested: {names}. Please ask these as separate questions."
            return ChatResponse(status="clarification", message=message,
                                clarification=clarification, proposals=proposals)
        messages.append({"role": "user", "content": outputs})
    raise ChatFailed("The assistant reached its tool-round limit. Try one supported question.")
