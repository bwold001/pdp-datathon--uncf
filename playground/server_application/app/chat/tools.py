"""The model's entire allowlist; no SQL or student-level operation is exposed."""

from analytics.definitions import DEFINITIONS
from analytics.schemas import AnalysisRequest
from analytics.service import AnalyticsService

TOOL_DEFINITIONS = [
    {
        "name": "get_analysis_catalog",
        "description": "Get supported analyses, cohorts, program aliases and data coverage.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
    {
        "name": "get_analysis_definition",
        "description": "Read the shared calculation definition for an approved analysis.",
        "input_schema": {
            "type": "object",
            "properties": {"analysis": {"type": "string", "enum": list(DEFINITIONS)}},
            "required": ["analysis"],
            "additionalProperties": False,
        },
    },
    {
        "name": "run_analysis",
        "description": (
            "Propose an analysis for user confirmation. No numbers are calculated. "
            "Missing parameters require clarification; "
            "graduation includes all perspectives and horizons."
        ),
        "input_schema": AnalysisRequest.model_json_schema(),
    },
]


# LiteLLM translates these function definitions for the selected provider.
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": tool["name"],
            "description": tool["description"],
            "parameters": tool["input_schema"],
        },
    }
    for tool in TOOL_DEFINITIONS
]


def dispatch(service: AnalyticsService, name: str, arguments: dict) -> dict | AnalysisRequest:
    """Validate each tool's narrow arguments before touching the data service."""
    if name == "get_analysis_catalog" and not arguments:
        return service.catalog()
    if (
        name == "get_analysis_definition"
        and set(arguments) == {"analysis"}
        and arguments["analysis"] in DEFINITIONS
    ):
        return DEFINITIONS[arguments["analysis"]].model_dump()
    if name == "run_analysis":
        return AnalysisRequest.model_validate(arguments)
    raise ValueError("Unsupported tool or arguments")
