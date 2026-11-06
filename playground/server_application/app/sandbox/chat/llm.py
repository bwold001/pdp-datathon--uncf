"""The Anthropic tool loop behind sandbox chat.

The model sees only the staff question, these instructions (chat rules plus the metadata-advisor
skill), and tool results. The definitions tools read repo metadata; run_aggregate_query reads the
Playground database read-only and returns only groups of 10 or more students, never student records.
"""

import asyncio
import json
import logging
from functools import cache
from typing import Any, Protocol

from . import dictionary_tool, metadata_tools, query_tool
from .repo import repo_root
from .schemas import SuggestResponse, ToolResult

logger = logging.getLogger(__name__)

MAX_TOOL_ROUNDS = 8
MAX_TOKENS = 2000
SKILL_PATH = ".agents/skills/metadata-advisor/SKILL.md"
DEFINITION_TOOLS = (*metadata_tools.TOOL_NAMES, dictionary_tool.NAME)

CHAT_RULES = """\
You are answering in the PDP datathon's Sandbox chat. Follow the metadata-advisor skill below, plus
these chat rules. Where they differ from the skill, these rules win.

1. You never see student records. You know only what your tools return.
2. You may run aggregate queries on the data model loaded into this Playground with
   run_aggregate_query. It only returns groups of 10 or more students. This replaces the skill's
   rule that you never touch data: you still never ask for or show individual students.
3. Only state numbers that a run_aggregate_query result returned in this chat. If it fails (for
   example, the data isn't loaded), say so and give the query for staff to run locally instead.
4. Before querying, check table and column names and codes with describe_table and
   get_column_dictionary. Never guess a column or a code. Stored codes can differ in case from
   the dictionary's (Part-Time, not Part-time), so compare text case-insensitively on both sides:
   LOWER(column) = LOWER('Part-time'), or LOWER(column) IN ('part-time', 'full-time').
5. When a group is missing because it had fewer than 10 students (suppressed_rows > 0), say so,
   and apply the skill's complementary suppression before showing totals or the other groups.
6. The data in this repository is synthetic. Numbers from it are not findings about real students
   or institutions; say so whenever you report one.
7. The tables list_tables returns are the data model. A dataset marked "(supplementary)" or with
   status "supplementary_proposed" is a proposed outside dataset that isn't in this repository:
   say so, and say its query only runs once a campus loads that data.
8. Each chat is a single question with no follow-up turn. Where the skill says to ask the user to
   confirm fields, list the candidate fields and state your assumptions instead of waiting.

Answer in a few short paragraphs. Put SQL in a fenced code block, and results in a small table."""


class ChatClient(Protocol):
    """The part of anthropic.AsyncAnthropic chat uses, so tests can pass a fake."""

    messages: Any


class ChatFailed(Exception):
    """The assistant didn't finish an answer."""


@cache
def system_prompt() -> str:
    """The chat rules followed by the metadata-advisor skill, without its YAML frontmatter."""
    skill = (repo_root() / SKILL_PATH).read_text(encoding="utf-8")
    return f"{CHAT_RULES}\n\n---\n\n{_strip_frontmatter(skill)}"


def _strip_frontmatter(markdown: str) -> str:
    """The markdown after a leading `---` ... `---` block, or all of it when there is none."""
    if markdown.startswith("---"):
        _, _, body = markdown[3:].partition("\n---")
        return body.strip()
    return markdown.strip()


def tool_definitions() -> list[dict[str, Any]]:
    """Every tool the model may call: the four MCP definitions tools, the dictionary, the query."""
    return [*metadata_tools.tool_schemas(), dictionary_tool.TOOL, query_tool.TOOL]


async def answer(client: ChatClient, model: str, prompt: str) -> SuggestResponse:
    """Run the tool loop for one question and return the grounded answer."""
    messages: list[dict[str, Any]] = [{"role": "user", "content": prompt}]
    tools = tool_definitions()
    # The prompt is the same on every round and request, so cache it.
    system = [{"type": "text", "text": system_prompt(), "cache_control": {"type": "ephemeral"}}]
    definitions: ToolResult | None = None
    query: ToolResult | None = None
    tools_used: list[str] = []

    for _ in range(MAX_TOOL_ROUNDS):
        response = await client.messages.create(
            model=model,
            max_tokens=MAX_TOKENS,
            system=system,
            tools=tools,
            messages=messages,
        )
        tool_uses = [block for block in response.content if block.type == "tool_use"]
        if not tool_uses:
            text = "\n\n".join(b.text for b in response.content if b.type == "text").strip()
            return SuggestResponse(
                message=text or "The assistant returned no answer.",
                definitions=definitions,
                query=query,
                tools_used=tools_used,
            )

        # Sent back unchanged: thinking blocks must keep their signatures between tool rounds.
        messages.append({"role": "assistant", "content": list(response.content)})
        results = []
        for use in tool_uses:
            tools_used.append(use.name)
            arguments = dict(use.input or {})
            # A thread, so a slow query doesn't hold up other requests.
            output, is_error = await asyncio.to_thread(_run_tool, use.name, arguments)
            call = ToolResult(tool=use.name, input=arguments, output=output, is_error=is_error)
            if use.name in DEFINITION_TOOLS:
                definitions = call
            elif use.name == query_tool.NAME:
                query = call
            results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": use.id,
                    "content": json.dumps(output),
                    "is_error": is_error,
                }
            )
        messages.append({"role": "user", "content": results})

    raise ChatFailed(f"The assistant used more than {MAX_TOOL_ROUNDS} rounds of tool calls.")


def _run_tool(name: str, arguments: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    """(result, is_error) for one tool call. Failures go back to the model, not the user."""
    try:
        if name == dictionary_tool.NAME:
            return dictionary_tool.call(arguments), False
        if name == query_tool.NAME:
            return query_tool.call(arguments), False
        return metadata_tools.call(name, arguments), False
    except metadata_tools.ToolError as exc:
        return exc.body, True
    except Exception:
        logger.exception("Sandbox chat tool %s failed", name)
        message = f"The {name} tool hit an unexpected error."
        return {"error": {"code": "internal_error", "message": message, "details": None}}, True
