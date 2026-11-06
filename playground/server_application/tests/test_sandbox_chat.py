"""Sandbox chat, with a scripted fake in place of Anthropic. No test calls a real model."""

from collections.abc import Iterator
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app
from app.sandbox.chat import llm, query_tool
from app.sandbox.chat.routes import get_chat_client

URL = "/api/v1/sandbox/chat/suggest"
RETENTION_QUESTION = "How do we analyze first-year student drop-off between fall and spring?"


def tool_use(name: str, arguments: dict[str, Any], use_id: str = "toolu_1") -> SimpleNamespace:
    """A tool_use content block, shaped like the SDK's."""
    return SimpleNamespace(type="tool_use", id=use_id, name=name, input=arguments)


def reply(*blocks: SimpleNamespace) -> SimpleNamespace:
    """One Messages API response."""
    return SimpleNamespace(content=list(blocks))


def text(value: str) -> SimpleNamespace:
    """A text content block."""
    return SimpleNamespace(type="text", text=value)


class FakeAnthropic:
    """Returns scripted responses in order and records every request."""

    def __init__(self, *responses: SimpleNamespace):
        self.responses = list(responses)
        self.requests: list[dict[str, Any]] = []
        self.messages = self

    async def create(self, **request: Any) -> SimpleNamespace:
        """Record the request and return the next scripted response."""
        self.requests.append(request)
        return self.responses.pop(0)


@pytest.fixture
def use_fake() -> Iterator[Any]:
    """Install a FakeAnthropic for the request; returns a function that sets its script."""

    def install(*responses: SimpleNamespace) -> FakeAnthropic:
        fake = FakeAnthropic(*responses)
        app.dependency_overrides[get_chat_client] = lambda: fake
        return fake

    yield install
    app.dependency_overrides.pop(get_chat_client, None)


def test_system_prompt_carries_the_metadata_advisor_skill(client: TestClient, use_fake) -> None:
    fake = use_fake(reply(text("Use retention, not persistence. Run the query below locally.")))

    body = client.post(URL, json={"prompt": RETENTION_QUESTION}).json()

    assert body["message"].startswith("Use retention")
    assert body["tools_used"] == []
    assert body["source"] == "synthetic"
    [system] = fake.requests[0]["system"]
    assert system["cache_control"] == {"type": "ephemeral"}
    assert system["text"].startswith(llm.CHAT_RULES)
    assert "Cartesian Product" in system["text"]
    assert "HAVING COUNT(*) >= 10" in system["text"]
    # The skill's YAML frontmatter is for agent tools, not the model.
    assert "name: metadata-advisor" not in system["text"]


def test_tool_result_goes_back_under_the_id_it_was_asked_with(client: TestClient, use_fake) -> None:
    fake = use_fake(
        reply(tool_use("list_tables", {})),
        reply(text("These are the tables.")),
    )

    body = client.post(URL, json={"prompt": "What tables are there?"}).json()

    assert body["tools_used"] == ["list_tables"]
    result = fake.requests[1]["messages"][-1]["content"][0]
    assert (result["type"], result["tool_use_id"], result["is_error"]) == (
        "tool_result",
        "toolu_1",
        False,
    )


def test_thinking_blocks_go_back_to_the_model_unchanged(client: TestClient, use_fake) -> None:
    thinking = SimpleNamespace(type="thinking", thinking="Retention fits.", signature="sig")
    fake = use_fake(
        reply(thinking, tool_use("list_tables", {})),
        reply(thinking, text("Use retention.")),
    )

    response = client.post(URL, json={"prompt": RETENTION_QUESTION})

    assert response.status_code == 200
    assert response.json()["message"] == "Use retention."
    assistant_turn = fake.requests[1]["messages"][1]
    assert assistant_turn["role"] == "assistant"
    assert assistant_turn["content"][0] is thinking


def test_model_is_offered_the_mcp_dictionary_and_query_tools(client: TestClient, use_fake) -> None:
    fake = use_fake(reply(text("Hello.")))

    client.post(URL, json={"prompt": "hi"})

    names = {tool["name"] for tool in fake.requests[0]["tools"]}
    assert names == {
        "list_tables",
        "describe_table",
        "get_column_definition",
        "get_database_info",
        "get_column_dictionary",
        "run_aggregate_query",
    }
    assert fake.requests[0]["model"] == settings.SANDBOX_CHAT_MODEL


def test_dictionary_result_is_returned_as_definitions(client: TestClient, use_fake) -> None:
    arguments = {"table": "cohort_membership", "column": "retention"}
    use_fake(
        reply(tool_use("get_column_dictionary", arguments)),
        reply(text("retention is 1 when the student was retained.")),
    )

    body = client.post(URL, json={"prompt": "What does retention mean?"}).json()

    assert body["definitions"]["tool"] == "get_column_dictionary"
    assert body["definitions"]["output"]["column"] == "retention"
    assert body["query"] is None


def test_query_result_is_returned_as_query(
    client: TestClient, use_fake, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = {"columns": ["intensity", "n"], "rows": [["Full-Time", 12]], "suppressed_rows": 1}
    monkeypatch.setattr(query_tool, "call", lambda arguments: output)
    sql = "SELECT intensity, COUNT(DISTINCT student_id) AS n FROM cohort_membership GROUP BY 1"
    use_fake(
        reply(tool_use("run_aggregate_query", {"sql": sql})),
        reply(text("12 full-time students; one group was too small to show.")),
    )

    body = client.post(URL, json={"prompt": "How many students by intensity?"}).json()

    assert body["query"] == {
        "tool": "run_aggregate_query",
        "input": {"sql": sql},
        "output": output,
        "is_error": False,
    }
    assert body["definitions"] is None


def test_schema_question_returns_the_describe_table_result(client: TestClient, use_fake) -> None:
    use_fake(
        reply(tool_use("describe_table", {"table": "cohort_membership"})),
        reply(text("cohort_membership has one row per student and cohort.")),
    )

    body = client.post(URL, json={"prompt": "What's in cohort_membership?"}).json()

    definitions = body["definitions"]
    assert definitions["tool"] == "describe_table"
    assert definitions["is_error"] is False
    assert definitions["output"]["name"] == "cohort_membership"
    assert {"student_id", "cohort"} <= {c["name"] for c in definitions["output"]["columns"]}


def test_unknown_table_goes_back_to_the_model_as_not_found(client: TestClient, use_fake) -> None:
    fake = use_fake(
        reply(tool_use("describe_table", {"table": "cohort"})),
        reply(text("Did you mean cohort_membership?")),
    )

    body = client.post(URL, json={"prompt": "Describe the cohort table"}).json()

    assert body["definitions"]["is_error"] is True
    assert body["definitions"]["output"]["error"]["code"] == "not_found"
    assert "cohort_membership" in body["definitions"]["output"]["error"]["details"]["suggestions"]
    assert fake.requests[1]["messages"][-1]["content"][0]["is_error"] is True


def test_tool_loop_stops_at_the_round_cap(client: TestClient, use_fake) -> None:
    use_fake(*[reply(tool_use("list_tables", {})) for _ in range(llm.MAX_TOOL_ROUNDS)])

    response = client.post(URL, json={"prompt": "Keep going"})

    assert response.status_code == 502
    assert str(llm.MAX_TOOL_ROUNDS) in response.json()["error"]["message"]


@pytest.mark.parametrize("prompt", ["", "   "])
def test_empty_prompt_is_rejected(client: TestClient, use_fake, prompt: str) -> None:
    use_fake()

    assert client.post(URL, json={"prompt": prompt}).status_code == 422


def test_missing_api_key_is_503(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", None)

    response = client.post(URL, json={"prompt": RETENTION_QUESTION})

    assert response.status_code == 503
    assert "ANTHROPIC_API_KEY" in response.json()["error"]["message"]


def test_bad_prompt_is_422_even_without_an_api_key(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", None)

    assert client.post(URL, json={"prompt": " "}).status_code == 422
