"""The model's entire allowlist; no SQL or student-level operation is exposed."""

from uncf.analytics.definitions import DEFINITIONS
from uncf.analytics.schemas import AnalysisRequest, AnalysisResponse
from uncf.analytics.service import AnalyticsService

TOOLS = [
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
        "description": "Run a deterministic analysis. Missing material parameters return clarification. Graduation returns every perspective and horizon.",
        "input_schema": AnalysisRequest.model_json_schema(),
    },
]


def dispatch(
    service: AnalyticsService, name: str, arguments: dict
) -> dict | AnalysisResponse:
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
        return service.analyze(AnalysisRequest.model_validate(arguments))
    raise ValueError("Unsupported tool or arguments")
