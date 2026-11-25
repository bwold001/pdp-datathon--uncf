"""Suggestions reflect catalog capabilities without claiming unexecuted results are available."""

from types import SimpleNamespace

from analytics.chat_guidance import (
    QUESTION_TEMPLATES,
    scope_guidance,
    suggested_questions,
)
from analytics.coverage import Coverage
from analytics.tests.analytics_fixtures import fixture_coverage
from analytics.tests.test_answer_presentation import graduation_step


def operations(*ids):
    """Supply explicit catalog capabilities without constructing numerical evidence."""
    return [SimpleNamespace(id=key, available=True) for key in ids]


def test_suggestions_filter_missing_operations_and_uncertified_coverage():
    """Uncertified graduation/enrollment and unavailable schema capabilities are excluded."""
    offered = operations(*QUESTION_TEMPLATES)
    offered.append(SimpleNamespace(id="measure_variant", available=False))
    suggestions = suggested_questions(offered, Coverage(), ["2022-23"])
    ids = {item.operation_id for item in suggestions}
    assert "legacy.graduation" not in ids and "legacy.annual_enrollment" not in ids
    assert "retention.rate" in ids
    assert all(item.availability == "not_checked" for item in suggestions)
    assert not suggested_questions([], fixture_coverage(), ["2022-23"])
    assert not suggested_questions(offered, fixture_coverage(), [])


def test_certified_coverage_allows_questions_without_promising_eligible_outcomes():
    """Coverage clears a known blocker but numerical eligibility still awaits confirmation."""
    suggestions = suggested_questions(
        operations("legacy.graduation", "legacy.annual_enrollment"),
        fixture_coverage(),
        ["2022-23"],
    )
    assert {item.operation_id for item in suggestions} == {
        "legacy.graduation",
        "legacy.annual_enrollment",
    }
    assert all(item.availability == "not_checked" for item in suggestions)


def test_scope_guidance_distinguishes_unverified_from_insufficient_followup():
    """Metadata guidance changes with declared coverage without calculating any outcomes."""
    plan = SimpleNamespace(steps=[graduation_step()])
    missing = scope_guidance(plan, Coverage())
    assert any("haven't verified" in item.message for item in missing)
    mature = scope_guidance(plan, fixture_coverage())
    assert any(
        "six-year" in item.message and "long enough" in item.message for item in mature
    )
    assert not any("Four-year and six-year" in item.message for item in mature)
