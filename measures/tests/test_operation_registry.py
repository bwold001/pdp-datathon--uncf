"""Catalog capabilities must agree with executable schemas and the dashboard vocabulary."""

import ast
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from measures.models import ALLOWED_VALUES, GroupDimension
from measures.registry import OPERATIONS
from measures.requests import FILTER_NAMES, Filters, InvalidFilter, validate_filters


def test_eleven_entries_have_complete_metadata_and_executable_schemas():
    """Every operation declares scope, units, coverage, disclosure and its actual executor owner."""
    assert set(OPERATIONS) == {
        "retention.rate",
        "persistence.rate",
        "dfw.rate",
        "dfw.course_list",
        "dfw.course_detail",
        "credit_completion.ratio",
        "credit_momentum.summary",
        "gateway.math_completion",
        "gateway.english_completion",
        "gateway.course_outcomes",
        "student_paths.summary",
    }
    for spec in OPERATIONS.values():
        details = spec.details()
        assert all(
            details[key]
            for key in (
                "id",
                "version",
                "label",
                "purpose",
                "grain",
                "population",
                "time_semantics",
                "exclusions",
                "required_coverage",
                "executor",
                "disclosure_profile",
                "limitations",
                "units",
                "distinctions",
                "definitions",
            )
        )
        assert spec.supported_filters == FILTER_NAMES
        assert details["request_schema"]["additionalProperties"] is False
        parameters = {"cohort": "2023-24"}
        if "retention_type" in spec.parameters.model_fields:
            parameters["retention_type"] = "school"
        if "course" in spec.parameters.model_fields:
            parameters["course"] = "ENG 101"
        assert spec.parameters.model_validate(parameters)
        with pytest.raises(ValidationError):
            spec.parameters.model_validate(
                {**parameters, "arbitrary_expression": "earned / attempted"}
            )


def test_filter_values_and_grouping_capabilities_match_the_existing_dashboard():
    """Only the eight supported cohort-bar dimensions appear in schemas and advertised grouping."""
    schema = Filters.model_json_schema()["properties"]
    assert set(schema) == set(FILTER_NAMES)
    for name, field in schema.items():
        assert set(field["anyOf"][0]["enum"]) == ALLOWED_VALUES[GroupDimension(name)]
    for spec in OPERATIONS.values():
        fields = spec.parameters.model_fields
        if spec.supported_breakdowns:
            assert "group_by" in fields
            assert set(spec.supported_breakdowns) == set(FILTER_NAMES)
        else:
            assert "group_by" not in fields
    with pytest.raises(InvalidFilter, match="only once"):
        validate_filters((("pell", "Y"), ("pell", "N")))


def test_gateway_catalog_keeps_grade_threshold_population_and_attempt_rules_distinct():
    """Cohort completion flags cannot be advertised as first-attempt course outcomes."""
    cohort = OPERATIONS["gateway.math_completion"]
    course = OPERATIONS["gateway.course_outcomes"]
    assert cohort.definitions != course.definitions
    assert "1.0" in json.dumps(cohort.details())
    assert "2.0" in course.purpose and "First attempt" in course.time_semantics
    assert "requirement" in " ".join(course.component_denominators)


def test_measure_request_and_dispatch_modules_do_not_import_http_or_orchestration():
    """Domain validation/dispatch remain usable outside FastAPI and the provider runtime."""
    for name in ("requests.py", "registry.py", "service.py"):
        tree = ast.parse((Path(__file__).parents[1] / name).read_text())
        imports = [
            node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
        ]
        assert not any(
            module
            and module.split(".")[0] in {"analytics", "api", "fastapi", "playground"}
            for module in imports
        )
