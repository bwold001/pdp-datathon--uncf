"""Evaluate fixed Release A interpretation cases without ever confirming or executing plans."""

import argparse
import asyncio
import hashlib
import json
import os
import subprocess
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from analytics.coverage import DEFAULT_CONFIG, load_coverage
from analytics.plan_contracts import CatalogResponse
from analytics.plan_service import PlanService
from analytics.service import AnalyticsService
from measures.breakdowns.gateway_courses import gateway_passed
from openrouter import OpenRouter

from app.chat.provider import OpenRouterClient
from app.chat.v2 import ChatRequestV2, answer_v2

CASES = Path(__file__).resolve().parents[1] / "tests/fixtures/release_a_prompts.json"


def contains(actual, expected):
    """Require explicit constraints, including exact empty filters and ordered lists."""
    if isinstance(expected, dict) and expected:
        return isinstance(actual, dict) and all(
            (
                key in actual
                and (actual[key] == value if key == "filters" else contains(actual[key], value))
            )
            for key, value in expected.items()
        )
    return actual == expected


def assess(case, response):
    """Score routing, constraints and necessary versus unnecessary clarification separately."""
    raw = response.model_dump(mode="json", exclude_none=True)
    steps = raw.get("plan", {}).get("steps", []) if raw.get("plan") else []
    operations = [step.get("operation_id") for step in steps]
    issues = {issue["code"] for issue in raw.get("issues", [])}
    unsupported = "unsupported_operation" in issues
    expected = case["expected_status"]
    constraints = all(
        any(
            step.get("operation_id") == operation and contains(step["parameters"], parameters)
            for step in steps
        )
        for operation, parameters in case["constraints"].items()
    )
    field = (raw.get("clarification") or {}).get("parameter")
    routing = operations == case["operations"] if expected != "unsupported" else unsupported
    necessary = expected == "clarification"
    clarification = raw["status"] == "clarification"
    status = unsupported if expected == "unsupported" else raw["status"] == expected
    correct_field = not necessary or field in case["clarification_fields"]
    safe = not raw.get("receipts") and raw.get("outcome") is None
    return {
        "id": case["id"],
        "critical": case["critical"],
        "passed": routing and constraints and status and correct_field and safe,
        "routing_correct": routing,
        "constraints_preserved": constraints,
        "necessary_clarification": necessary and clarification and correct_field,
        "missed_clarification": necessary and not (clarification and correct_field),
        "unnecessary_clarification": not necessary and clarification,
        "unsupported": unsupported,
        "execution_absent": safe,
        "status": raw["status"],
        "operations": operations,
        "clarification_field": field,
        "issue_codes": sorted(issues),
    }


async def evaluate(runtime, model, key, cases):
    """Bound each production-provider interpretation and close its SDK before the next case."""
    results = []
    for case in cases:
        async with OpenRouter(api_key=key) as sdk:
            try:
                response = await asyncio.wait_for(
                    answer_v2(
                        ChatRequestV2(
                            protocol_version=2,
                            prompt=case["prompt"],
                            dashboard_context=case.get("dashboard_context"),
                        ),
                        OpenRouterClient(sdk),
                        model,
                        runtime,
                    ),
                    timeout=75,
                )
                results.append(assess(case, response))
            except TimeoutError:
                results.append({"id": case["id"], "passed": False, "status": "timeout"})
    return results


def gateway_boundary_check():
    """Compare the course owner with independently specified Release A pass boundaries."""
    grades = ("0.69", "0.70", "1.99", "2.00", "P", "W", "I", "unknown")
    expected = (False, False, False, True, True, False, None, None)
    actual = tuple(gateway_passed(grade) for grade in grades)
    return {"grades": grades, "expected": expected, "actual": actual, "passed": actual == expected}


def main():
    """Write explicit unverified evidence when credentials or source prerequisites are missing."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, help="Configured production OpenRouter model ID")
    parser.add_argument(
        "--database", required=True, type=Path, help="Known synthetic SQLite snapshot"
    )
    parser.add_argument(
        "--coverage",
        type=Path,
        default=Path(os.environ.get("UNCF_ANALYTICS_CONFIG", DEFAULT_CONFIG)),
    )
    parser.add_argument("--output", required=True, type=Path, help="Untracked JSON evidence path")
    args = parser.parse_args()
    suite = CASES.read_bytes()
    cases = json.loads(suite)["cases"]
    root = Path(__file__).resolve().parents[3]
    report = {
        "synthetic": True,
        "revision": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True
        ).strip(),
        "worktree_dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=root)),
        "model": args.model,
        "suite_sha256": hashlib.sha256(suite).hexdigest(),
        "recorded_at": datetime.now(UTC).isoformat(),
        "cases": len(cases),
        "status": "unverified",
        "results": [],
        "gateway_course_boundary": gateway_boundary_check(),
    }
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        report["reason"] = "OPENROUTER_API_KEY absent; no production-model evaluation ran"
    else:
        runtime = AnalyticsService(args.database, load_coverage(args.coverage))
        catalog = PlanService(runtime).catalog()
        if not isinstance(catalog, CatalogResponse):
            report["reason"] = "Synthetic snapshot/catalog prerequisites unavailable"
        else:
            report["catalog"] = catalog.model_dump(mode="json")
            report["results"] = asyncio.run(evaluate(runtime, args.model, key, cases))
            report["summary"] = dict(Counter(r["status"] for r in report["results"]))
            report["status"] = "passed" if all(r["passed"] for r in report["results"]) else "failed"
    report["gate_passed"] = (
        report["status"] == "passed" and report["gateway_course_boundary"]["passed"]
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(
        f"Release A interpretation evaluation: {report['status']} "
        f"({len(report['results'])}/{len(cases)} cases)"
    )
    return 0 if report["gate_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
