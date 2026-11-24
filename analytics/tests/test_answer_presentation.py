"""Plain-language evidence must distinguish missing data, empty groups and valid zeros."""

import sqlite3

import pytest

from analytics.analysis_service import AnalysisService, legacy_step
from analytics.answer_presentation import present_answer
from analytics.coverage import Coverage
from analytics.data_access import sqlite_snapshot
from analytics.plan_service import PlanService
from analytics.service import AnalyticsService
from analytics.tests.analytics_fixtures import build_database, fixture_coverage
from analytics.tests.test_snapshots import add_identity


@pytest.fixture
def database(tmp_path):
    """Three synthetic students include two Chemistry entrants and one unknown entry major."""
    path = build_database(tmp_path / "answers.sqlite")
    add_identity(path)
    return path


def graduation_step():
    """Use the user's exact cohort, degree and Chemistry-family scope."""
    return legacy_step(
        {
            "analysis": "graduation",
            "cohort": "2022-23",
            "credential": "B",
            "program": "chemistry_family",
        }
    )


def answer(database, coverage):
    """Present only the deterministic adapter's disclosed result."""
    owner = AnalysisService(coverage)
    step = graduation_step()
    with sqlite_snapshot(database) as snapshot:
        evidence = owner.execute(step, snapshot)
    return evidence, present_answer(
        step, owner.operations[step.operation_id], evidence.result
    )


def test_exact_chemistry_selection_explains_unverified_followup(database):
    """Absent certification is never described as no students or a zero graduation rate."""
    evidence, presentation = answer(database, Coverage())
    rows = evidence.result.payload.rows
    assert len(rows) == 15
    assert all(row.explanation.label and row.explanation.horizon for row in rows)
    assert {row.explanation.reason for row in rows} == {"followup_not_verified"}
    assert all(not hasattr(row, "cells") for row in rows)
    assert (
        presentation.summary == "A graduation rate isn't available for this selection."
    )
    assert "2022-23 entry cohort" in presentation.scope
    assert (
        "Bachelor's degree" in presentation.scope
        and "Chemistry family" in presentation.scope
    )
    assert any("haven't verified" in line for line in presentation.items)
    assert all("No students match" not in line for line in presentation.items)
    assert any("does not mean" in line for line in presentation.caveats)


def test_mature_and_immature_horizons_keep_values_and_reasons_separate(database):
    """Four-year and to-date results stay visible while six-year follow-up is incomplete."""
    evidence, presentation = answer(database, fixture_coverage())
    assert any("50.00% (1 of 2 students)" in item for item in presentation.items)
    assert any(
        "Within six years" in item and "long enough" in item
        for item in presentation.items
    )
    assert any(
        row.explanation and row.explanation.reason == "completion_program_missing"
        for row in evidence.result.payload.rows
        if not hasattr(row, "cells")
    )


def test_verified_empty_population_differs_from_unknown_eligibility(database):
    """Empty is asserted only when both credential and entry-program eligibility are known."""
    with sqlite3.connect(database) as db:
        db.execute("UPDATE cohort_membership SET program_of_study_term_1='520201'")
    _, presentation = answer(database, fixture_coverage())
    assert any("No students match" in item for item in presentation.items)
    with sqlite3.connect(database) as db:
        db.execute(
            "UPDATE cohort_membership SET program_of_study_term_1=NULL WHERE student_id='c'"
        )
    _, presentation = answer(database, fixture_coverage())
    assert all("No students match" not in item for item in presentation.items)


@pytest.mark.parametrize("n", range(1, 10))
def test_valid_zero_and_small_populations_keep_counts(database, n):
    """A valid zero is rendered as a numerical rate for every population size from one to nine."""
    with sqlite3.connect(database) as db:
        db.execute("DELETE FROM cohort_membership")
        db.executemany(
            "INSERT INTO cohort_membership (student_id,cohort,program_of_study_term_1,credential_type_sought_year_1,first_year_to_bachelors_at_coh,years_to_ba_at_cohort_inst) VALUES (?, '2022-23', '400501', 'B', 0, 0)",
            [(f"s{i}",) for i in range(n)],
        )
    _, presentation = answer(database, fixture_coverage())
    assert any(f"0.00% (0 of {n} students)" in line for line in presentation.items)


def test_missing_outcomes_do_not_become_zero_or_empty(database):
    """Known entrants with missing timing get an outcome-information explanation."""
    with sqlite3.connect(database) as db:
        db.execute(
            "UPDATE cohort_membership SET first_year_to_bachelors_at_coh=NULL, years_to_ba_at_cohort_inst=NULL"
        )
    _, presentation = answer(database, fixture_coverage())
    assert any("usable outcome information" in item for item in presentation.items)
    assert all(
        "0.00%" not in item and "No students match" not in item
        for item in presentation.items
    )


def test_confirmed_plan_receipt_and_replay_include_same_presentation(database):
    """Finalization presents disclosed evidence and exact replay reproduces the same answer."""
    from analytics.contracts_v2 import ProposedPlan

    service = PlanService(AnalyticsService(database, Coverage()))
    catalog = service.catalog()
    proposal = ProposedPlan(
        kind="proposed",
        catalog_version=catalog.catalog_version,
        snapshot_ref=catalog.snapshot_ref,
        steps=[graduation_step().model_dump()],
    )
    review = service.validate(proposal)
    assert review.status == "confirmation" and not review.receipts
    assert any("haven't verified" in item.message for item in review.guidance)
    assert review.plan.steps[0].parameters == graduation_step().parameters
    result = service.execute_plan(review.plan)
    assert result.status == "answer"
    assert (
        result.receipts[0].presentation.summary
        == "A graduation rate isn't available for this selection."
    )
    repeated = service.execute_plan(review.plan, result.replay)
    assert repeated.receipts[0].presentation == result.receipts[0].presentation
