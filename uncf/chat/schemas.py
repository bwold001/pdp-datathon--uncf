"""Chat transport with receipts and one pending clarification, not session memory."""

from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_core import PydanticCustomError

from uncf.analytics.schemas import (
    AnalysisReceipt,
    AnalysisRequest,
    Clarification,
    Contract,
)


class Selection(Contract):
    """One explicit choice for the current unresolved parameter."""

    field: Literal["cohort", "credential", "program"]
    value: str = Field(min_length=1, max_length=100)


class ChatRequest(Contract):
    """A question, or a validated selection resuming a single pending analysis."""

    prompt: str = Field(min_length=1, max_length=4000)
    pending: AnalysisRequest | None = None
    selection: Selection | None = None
    proposals: list[AnalysisRequest] = Field(default_factory=list, max_length=36)
    confirmed: list[AnalysisRequest] | None = Field(default=None, min_length=1, max_length=36)

    @field_validator("prompt")
    @classmethod
    def nonempty_prompt(cls, value: str) -> str:
        """Reject whitespace-only questions before any provider call."""
        value = value.strip()
        if not value:
            raise PydanticCustomError("invalid_parameters", "Enter a question")
        return value

    @model_validator(mode="after")
    def pending_needs_selection(self):
        """A clarification exchange carries both request and selected answer."""
        if (self.pending is None) != (self.selection is None):
            raise PydanticCustomError(
                "invalid_parameters", "pending and selection must be supplied together"
            )
        if self.confirmed is not None and (self.pending or self.proposals):
            raise PydanticCustomError("invalid_parameters", "Confirm a complete scope separately")
        if self.proposals and self.pending is None:
            raise PydanticCustomError("invalid_parameters", "Prior proposals require clarification")
        return self


class ChatResponse(Contract):
    """Deterministic numerical evidence with a bounded status message."""

    status: Literal["answer", "clarification", "confirmation", "unsupported"]
    message: str
    proposals: list[AnalysisRequest] = Field(default_factory=list, max_length=36)
    receipts: list[AnalysisReceipt] = Field(default_factory=list)
    clarification: Clarification | None = None
    source: Literal["synthetic"] = "synthetic"
