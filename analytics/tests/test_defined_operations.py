"""Hand-counted synthetic acceptance cases for the registered operation adapters."""

import json
import sqlite3

import pytest

from analytics.analysis_service import AnalysisService, OperationError
from analytics.coverage import Coverage
from analytics.data_access import sqlite_snapshot
from analytics.tests.test_snapshots import add_identity
from measures.tests.explorer_fixture import here, make_database, student


@pytest.fixture
def defined_data(tmp_path):
    """Twelve students, 24 final grades, six retained, and a fractional credit numerator."""
    students = [
        student(f"s{i}", retention=int(i < 6), attempted=3, earned=1.5 if i < 11 else 1)
        for i in range(12)
    ]
    courses = [
        here(
            f"s{i}",
            "2023-24",
            "FALL",
            grade=grade,
            attempted=3,
            earned=1.5,
            gateway="E",
        )
        for i in range(12)
        for grade in ("2.0", "1.0")
    ]
    path = make_database(tmp_path / "defined.sqlite", students, courses)
    with sqlite3.connect(path) as db:
        db.execute(
            "UPDATE cohort_membership SET persistence=1, gateway_math_status='R', gateway_english_status='R', completed_gateway_math_year1='D', completed_gateway_english_year1='D'"
        )
        db.execute(
            "UPDATE cohort_membership SET completed_gateway_math_year1='C', completed_gateway_english_year1='C' WHERE retention=1"
        )
    add_identity(path)
    return path


def request(operation, **parameters):
    """Build a concrete step without a provider or HTTP adapter."""
    return {
        "kind": "defined_measure",
        "step_id": "result",
        "operation_id": operation,
        "parameters": {"cohort": "2023-24", **parameters},
    }


@pytest.mark.parametrize(
    "operation,parameters,numerator,denominator,value",
    [
        ("retention.rate", {"retention_type": "school"}, 6, 12, 0.5),
        ("persistence.rate", {}, 12, 12, 1),
        ("dfw.rate", {}, 12, 24, 0.5),
        ("credit_completion.ratio", {}, 35 / 6, 12, 0.4861),
        ("gateway.math_completion", {}, 6, 12, 0.5),
        ("gateway.english_completion", {}, 6, 12, 0.5),
    ],
)
def test_scalar_operations_preserve_owner_counts(
    defined_data, operation, parameters, numerator, denominator, value
):
    """Expected arithmetic is fixed here rather than obtained from the measure under test."""
    with sqlite_snapshot(defined_data) as snapshot:
        result = (
            AnalysisService(Coverage())
            .execute(request(operation, **parameters), snapshot)
            .result
        )
        assert result.status == "ok"
        assert result.payload.numerator == pytest.approx(numerator)
        assert result.payload.denominator == denominator
        assert result.payload.value == value
        assert result.payload.n_students == 12
        if operation == "dfw.rate":
            assert result.payload.denominator_unit == "classifiable course enrollments"
            assert result.payload.split.model_dump() == {"D": 12, "F": 0, "W": 0}


@pytest.mark.parametrize(
    "operation,parameters,field,expected",
    [
        ("dfw.course_list", {}, "everyone.den", 24),
        ("dfw.course_detail", {"course": "ENG 101"}, "den", 24),
        (
            "credit_momentum.summary",
            {"retention_type": "school"},
            "milestones[0].credits",
            12,
        ),
        (
            "gateway.course_outcomes",
            {"retention_type": "school"},
            "courses[0].first_pass",
            12,
        ),
        ("student_paths.summary", {"retention_type": "school"}, "students", 12),
    ],
)
def test_every_page_returns_bounded_typed_evidence(
    defined_data, operation, parameters, field, expected
):
    """Page components retain their own names and values without recomputing their formulas."""
    with sqlite_snapshot(defined_data) as snapshot:
        result = (
            AnalysisService(Coverage())
            .execute(request(operation, **parameters), snapshot)
            .result
        )
        assert result.payload.kind == "table"
        rows = {
            row.cells[0]: row.cells
            for row in result.payload.rows
            if row.status in ("ok", "provisional")
        }
        assert rows[field][1] == expected
        assert "student_id" not in result.model_dump_json()
        assert snapshot.positional.execute(
            "SELECT COUNT(*) FROM student"
        ).fetchone() == (12,)


def test_hidden_and_grouped_results_preserve_status_and_student_counts(defined_data):
    """Hidden inputs never become zero, and grouping keeps every returned owner row."""
    service = AnalysisService(Coverage())
    with sqlite_snapshot(defined_data) as snapshot:
        result = service.execute(
            request("dfw.rate", group_by=["gender"]), snapshot
        ).result
        visible = [row for row in result.payload.breakdowns if row.status == "ok"]
        assert len(visible) == 1 and visible[0].group.gender == "F"
        assert visible[0].denominator == 24 and visible[0].n_students == 12
        hidden = service.execute(
            request("retention.rate", retention_type="school", filters={"pell": "N"}),
            snapshot,
        ).result
        assert hidden.status in ("suppressed", "not_yet_observable")
        assert set(json.loads(hidden.model_dump_json())) == {"status", "reason"}


def test_invalid_requests_are_refused_before_any_database_access():
    """The registry refuses unsupported filters, groupings and exploration at its boundary."""
    for raw in [
        request("gateway.course_outcomes", retention_type="school", group_by=["pell"]),
        request("dfw.rate", filters={"first_gen": "Y"}),
        request("dfw.rate", group_by=["course"]),
        request("unknown"),
        request("retention.rate"),
    ]:
        with pytest.raises(OperationError):
            AnalysisService(Coverage()).execute(raw, None)


def test_gateway_nonreporting_and_missing_course_are_typed_hidden_evidence(
    defined_data,
):
    """Missing gateway reporting and undisclosed course scope cannot appear as numeric zero."""
    with sqlite3.connect(defined_data) as db:
        db.execute(
            "UPDATE cohort_membership SET gateway_math_status=NULL, completed_gateway_math_year1=NULL"
        )
    with sqlite_snapshot(defined_data) as snapshot:
        service = AnalysisService(Coverage())
        gateway = service.execute(request("gateway.math_completion"), snapshot).result
        course = service.execute(
            request("dfw.course_detail", course="NOT DISCLOSED"), snapshot
        ).result
        assert gateway.model_dump() == {
            "status": "not_reported",
            "reason": "not_reported",
        }
        assert course.model_dump() == {"status": "unavailable", "reason": "no_evidence"}


def test_school_and_federal_retention_follow_the_selected_definition(defined_data):
    """A credential/PDP flag does not substitute for observed next-fall enrollment."""
    with sqlite3.connect(defined_data) as db:
        db.execute("INSERT INTO term VALUES (2, '2024-25', 'FALL', 20241)")
        db.execute(
            "INSERT INTO course_enrollment VALUES (100, 's11', '2023-24', 1, 2, '01', NULL, '2.0', 'F', 'N', 'CU', 3, 3, 'N', NULL)"
        )
    with sqlite_snapshot(defined_data) as snapshot:
        service = AnalysisService(Coverage())
        school = service.execute(
            request("retention.rate", retention_type="school"), snapshot
        ).result
        federal = service.execute(
            request("retention.rate", retention_type="federal"), snapshot
        ).result
        assert school.payload.numerator == 6
        assert federal.payload.numerator == 1 and federal.payload.denominator == 12


def test_provisional_status_and_grouped_hidden_evidence_survive_serialization(
    defined_data,
):
    """Provisional is not complete follow-up; hidden group values never survive JSON projection."""
    coverage = Coverage(provisional_retention_cohorts=["2023-24"])
    with sqlite_snapshot(defined_data) as snapshot:
        result = (
            AnalysisService(coverage)
            .execute(
                request("retention.rate", retention_type="school", group_by=["gender"]),
                snapshot,
            )
            .result
        )
        assert result.status == "provisional"
        raw = json.loads(result.model_dump_json())
        hidden = [
            row
            for row in raw["payload"]["breakdowns"]
            if row["status"] not in ("ok", "provisional")
        ]
        assert hidden and all(
            set(row) == {"status", "reason", "group"} for row in hidden
        )


def test_page_limits_refuse_whole_result_and_explicit_hidden_components_are_scrubbed():
    """Projection cannot truncate an oversized page or retain hidden component inputs."""
    from analytics.analysis_service import _page_result

    hidden = _page_result(
        {"status": "ok", "secret": {"status": "suppressed", "numerator": 8}},
        "credit_momentum.summary",
        False,
    )
    assert hidden.payload.rows[0].model_dump() == {"status": "suppressed"}
    empty = _page_result({"pairs": []}, "gateway.course_outcomes", False)
    assert empty.payload.rows[0].cells == (
        "pairs",
        None,
        "no entries",
        "empty collection",
    )
    with pytest.raises(OperationError) as error:
        _page_result({"values": list(range(201))}, "credit_momentum.summary", False)
    assert error.value.code == "limit_exceeded"
