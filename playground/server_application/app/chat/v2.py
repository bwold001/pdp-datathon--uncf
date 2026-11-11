"""Bounded planning tools over the shared deterministic plan service."""

import json
from typing import Annotated, Literal, Union

from analytics.contracts_v2 import (
    DEFINED_REQUESTS,
    LEGACY_REQUESTS,
    Contract,
    ExecutablePlan,
    Identifier,
    ParameterKey,
    ProposedPlan,
    proposal_model,
    resolve_choice,
)
from analytics.execution import run_sync
from analytics.plan_contracts import CatalogResponse
from analytics.plan_service import PlanService, refusal
from measures.requests import Cohort, Filters, RetentionType
from pydantic import Field, StrictInt, StrictStr, model_validator

from app.chat.provider import ProviderFailed
from app.chat.service import MAX_TOOL_ROUNDS, MAX_TOOLS_PER_ROUND

ReleaseAOperations = Union[  # noqa: UP007 - runtime operation union
    tuple(proposal_model(step) for step in (*DEFINED_REQUESTS, *LEGACY_REQUESTS))
]
ReleaseAStep = Annotated[
    ReleaseAOperations,
    Field(discriminator="operation_id"),
]


class ReleaseAProposal(ProposedPlan):
    """Advertise only implemented registered operation schemas to the provider."""

    steps: Annotated[tuple[ReleaseAStep, ...], Field(min_length=1, max_length=4)]


class Selection(Contract):
    """Address one allowed parameter in one preserved step."""

    step_id: Identifier
    parameter: ParameterKey
    value: StrictStr | StrictInt


class DashboardContext(Contract):
    """Carry only explicitly transmitted dashboard scope."""

    cohort: Cohort
    filters: Filters = Field(default_factory=Filters)
    retention_type: RetentionType | None = None


class ChatRequestV2(Contract):
    """Separate new questions, complete-plan clarification and exact confirmation."""

    protocol_version: Literal[2]
    prompt: str = Field(min_length=1, max_length=4000)
    plan: ProposedPlan | None = None
    selection: Selection | None = None
    confirmed: ExecutablePlan | None = None
    dashboard_context: DashboardContext | None = None

    @model_validator(mode="after")
    def exchange(self):
        """Reject mixed exchanges and empty questions before contacting a provider."""
        if not self.prompt.strip() or (self.plan is None) != (self.selection is None):
            raise ValueError("Supply a question or a complete clarification exchange")
        if self.confirmed is not None and (self.plan or self.dashboard_context):
            raise ValueError("Confirm the exact executable plan separately")
        return self


RULES = """Propose a complete typed plan using propose_plan; never calculate or answer with numbers.
Search the catalog and read operation details to distinguish definitions and populations.
Release A supports only the fourteen registered defined/legacy operations. Never substitute
another definition or broaden filters. Keep every requested step and filter in one plan.
For missing cohort, retention_type, course, terms, credential or program, use an unresolved
choice with a valid placeholder option; the server replaces choices with its current choices.
Do not assume a cohort or dashboard context absent from this conversation. Context explicitly
provided by the application may be inherited; question-specific scope overrides it visibly.
School and federal retention differ. Credit-tier retention uses credit_momentum.summary.
No SQL, Python, expressions, student rows, causal claims or unregistered exploration.
All evidence is synthetic. Use supplied catalog_version and snapshot_ref on the proposal.
"""


def tools():
    """Expose metadata and a typed proposal only, with no calculation tool."""
    definitions = [
        (
            "search_catalog",
            "Search compact registered operation candidates.",
            {
                "type": "object",
                "properties": {"query": {"type": "string", "maxLength": 500}},
                "required": ["query"],
                "additionalProperties": False,
            },
        ),
        (
            "operation_details",
            "Read a registered operation's exact semantics and schema.",
            {
                "type": "object",
                "properties": {"operation_id": {"type": "string"}},
                "required": ["operation_id"],
                "additionalProperties": False,
            },
        ),
        (
            "propose_plan",
            "Propose all steps for deterministic validation; never executes.",
            ReleaseAProposal.model_json_schema(),
        ),
    ]
    return [
        {
            "type": "function",
            "function": {"name": name, "description": description, "parameters": schema},
        }
        for name, description, schema in definitions
    ]


async def review(service, plan):
    """Refresh stale references into an explicit review without executing changed scope."""
    result = await run_sync(service.validate, plan)
    if any(i.code in ("snapshot_unavailable", "stale_plan") for i in result.issues):
        catalog = await run_sync(service.catalog)
        if not isinstance(catalog, CatalogResponse):
            return catalog
        raw = plan.model_dump(mode="python")
        raw.update(catalog_version=catalog.catalog_version, snapshot_ref=catalog.snapshot_ref)
        refreshed = type(plan).model_validate(raw)
        result = await run_sync(service.validate, refreshed)
        if result.status == "confirmation":
            result = result.model_copy(
                update={
                    "message": (
                        "The source or catalog changed. "
                        "Review this updated scope before confirming again."
                    )
                }
            )
    return result


async def answer_v2(payload, client, model, runtime):
    """Propose through the provider; resolve and execute only through shared application owners."""
    service = PlanService(runtime)
    if payload.confirmed is not None:
        checked = await review(service, payload.confirmed)
        if checked.status != "confirmation" or checked.plan != payload.confirmed:
            return checked
        result = await run_sync(service.execute_plan, payload.confirmed, check_completion=False)
        if result.outcome is None and any(
            i.code in ("snapshot_unavailable", "stale_plan") for i in result.issues
        ):
            return await review(service, payload.confirmed)
        return result
    if payload.plan is not None:
        # Rebuild server-owned choices before accepting a client selection.
        checked = await review(service, payload.plan)
        if checked.status != "clarification":
            return checked
        selection = payload.selection
        try:
            plan = resolve_choice(
                checked.plan, selection.step_id, selection.parameter, selection.value
            )
        except ValueError:
            return refusal("unsupported_parameter", checked.plan)
        return await review(service, plan)
    if client is None:
        return refusal("provider_failed")
    catalog = await run_sync(service.catalog)
    if not isinstance(catalog, CatalogResponse):
        return catalog
    context = {"catalog_version": catalog.catalog_version, "snapshot_ref": catalog.snapshot_ref}
    if payload.dashboard_context is not None:
        context["dashboard_context"] = payload.dashboard_context.model_dump(mode="json")
    messages = [
        {"role": "user", "content": payload.prompt},
        {"role": "user", "content": "Application context: " + json.dumps(context)},
    ]
    for _ in range(MAX_TOOL_ROUNDS):
        try:
            response = await client.complete(
                model=model, system=RULES, tools=tools(), messages=messages
            )
        except ProviderFailed:
            return refusal("provider_failed")
        if len(response.calls) > MAX_TOOLS_PER_ROUND:
            return refusal("limit_exceeded")
        if not response.calls:
            return refusal("unsupported_operation")
        messages.append(response.message)
        proposal = None
        for call in response.calls:
            args = call.arguments
            try:
                if (
                    call.name == "search_catalog"
                    and set(args) == {"query"}
                    and isinstance(args["query"], str)
                    and len(args["query"]) <= 500
                ):
                    output = service.owner.catalog(args["query"])
                elif call.name == "operation_details" and set(args) == {"operation_id"}:
                    output = service.owner.details(args["operation_id"])
                elif call.name == "propose_plan" and proposal is None:
                    if any(
                        s.get("kind") == "exploratory_analysis"
                        for s in args.get("steps", ())
                        if isinstance(s, dict)
                    ):
                        return refusal("unsupported_operation")
                    proposal = ReleaseAProposal.model_validate(
                        {**args, **context_without_dashboard(context)}
                    )
                    output = {"proposed": True, "executed": False}
                else:
                    return refusal("invalid_plan")
            except ValueError, TypeError:
                return refusal("invalid_plan")
            messages.append(
                {"role": "tool", "tool_call_id": call.id, "content": json.dumps(output)}
            )
        if proposal is not None:
            return await review(service, proposal)
    return refusal("limit_exceeded")


def context_without_dashboard(context):
    """Pin provider proposals to application-issued references only."""
    return {key: context[key] for key in ("catalog_version", "snapshot_ref")}
