"""/sandbox/chat: the question in, and the assistant's grounded answer out."""

from typing import Annotated, Any, Literal

from pydantic import BaseModel, StringConstraints

Prompt = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]


class SuggestRequest(BaseModel):
    """One staff question."""

    prompt: Prompt


class ToolResult(BaseModel):
    """One tool call the assistant made, with its result or MCP-shaped error."""

    tool: str
    input: dict[str, Any]
    output: dict[str, Any]
    is_error: bool = False


class SuggestResponse(BaseModel):
    """The assistant's answer, plus the tool results it was grounded on."""

    message: str
    definitions: ToolResult | None = None
    # The last aggregate query: only groups of 10 or more students.
    query: ToolResult | None = None
    tools_used: list[str]
    # Definitions and query results come from the synthetic shared model, never real students.
    source: Literal["synthetic"] = "synthetic"
