"""Provider-free HTTP acceptance tests use explicit, hand-counted synthetic evidence."""

import json
import sqlite3

import pytest
from fastapi.testclient import TestClient

from analytics.coverage import Coverage
from analytics.service import AnalyticsService
from analytics.tests.test_defined_operations import defined_data as defined_data  # noqa: PLC0414 - pytest fixture
from analytics.tests.test_defined_operations import request
from analytics.tests.test_snapshots import add_identity
from api.analysis_v2 import get_runtime_factory, get_timeout
from api.route import create_app

PREFIX = "/api/v1/uncf/analysis-v2"


@pytest.fixture
def client(defined_data, monkeypatch):
    """Mount deterministic routes with a real normalized fixture and no provider key."""
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    app = create_app()
    runtime = AnalyticsService(defined_data, Coverage())
    app.dependency_overrides[get_runtime_factory] = lambda: lambda: runtime
    with TestClient(app) as browser:
        yield browser


def plan(client, *steps):
    """Bind an explicit plan to server-issued source/catalog references."""
    catalog = client.get(PREFIX + "/catalog").json()
    return {
        "kind": "executable",
        "catalog_version": catalog["catalog_version"],
        "snapshot_ref": catalog["snapshot_ref"],
        "steps": list(steps or (request("retention.rate", retention_type="school"),)),
    }


def test_catalog_and_validate_do_not_execute_metrics(client, monkeypatch):
    """Catalog choices and canonical confirmation are deterministic metadata reads only."""
    from measures import service

    def forbidden(*args, **kwargs):
        """Calculation is forbidden during catalog and validation."""
        pytest.fail("validation executed a metric")

    monkeypatch.setattr(service, "execute", forbidden)
    catalog = client.get(PREFIX + "/catalog")
    assert catalog.status_code == 200
    body = catalog.json()
    assert body["choices"]["cohorts"] == ["2023-24"]
    assert len(body["operations"]) == 14
    assert any(
        row["id"] == "retention.rate" and row["available"] for row in body["operations"]
    )
    assert any(
        row["id"] == "legacy.entry_major_retention" and not row["available"]
        for row in body["operations"]
    )
    response = client.post(PREFIX + "/validate", json=plan(client))
    assert response.status_code == 200 and response.json()["status"] == "confirmation"
    assert response.json()["plan"]["steps"][0]["parameters"]["group_by"] == []
    assert response.json()["receipts"] == []


def test_provider_free_execution_and_replay_preserve_counts(client):
    """Six of twelve retained and twelve of twenty-four DFW enrollments need no model provider."""
    steps = [
        request("retention.rate", retention_type="school"),
        {**request("dfw.rate"), "step_id": "dfw"},
    ]
    response = client.post(PREFIX + "/execute", json=plan(client, *steps))
    assert response.status_code == 200
    body = response.json()
    assert (body["status"], body["outcome"]) == ("answer", "complete")
    first, second = body["receipts"]
    assert (
        first["result"]["payload"]["numerator"],
        first["result"]["payload"]["denominator"],
    ) == (6, 12)
    assert second["result"]["payload"]["denominator"] == 24
    assert first["source"]["snapshot_ref"] == second["source"]["snapshot_ref"]
    assert first["versions"]["pipeline"] == second["versions"]["pipeline"]
    repeated = client.post(PREFIX + "/execute", json=body["replay"]).json()
    assert repeated["outcome"] == "complete"
    assert (
        repeated["receipts"][0]["computation_fingerprint"]
        == first["computation_fingerprint"]
    )
    assert repeated["execution"]["execution_id"] != body["execution"]["execution_id"]


@pytest.mark.parametrize("change", ["proposed", "cycle", "extra", "too_many"])
def test_invalid_plans_fail_before_calculation(client, monkeypatch, change):
    """Only a bounded complete executable plan can enter the execution owner."""
    from measures import service

    called = []
    monkeypatch.setattr(service, "execute", lambda *args: called.append(True))
    raw = plan(client)
    if change == "proposed":
        raw["kind"] = "proposed"
    elif change == "cycle":
        raw["steps"][0]["depends_on"] = ["result"]
    elif change == "extra":
        raw["steps"][0]["parameters"]["sql"] = "SELECT student_id FROM student"
    else:
        raw["steps"] = [{**raw["steps"][0], "step_id": f"s{i}"} for i in range(5)]
    response = client.post(PREFIX + "/execute", json=raw)
    assert response.status_code == 422 and not called
    assert response.json()["status"] == "error" and response.json()["outcome"] is None
    assert response.json()["receipts"] == []


def test_clarification_replaces_provider_options_and_preserves_other_steps(client):
    """One unresolved field is clarified while another complete operation stays intact."""
    raw = plan(
        client,
        request(
            "retention.rate",
            retention_type={
                "unresolved": True,
                "question": "model text",
                "choices": [{"value": "school", "label": "model text"}],
            },
        ),
        {**request("dfw.rate"), "step_id": "dfw"},
    )
    raw["kind"] = "proposed"
    body = client.post(PREFIX + "/validate", json=raw).json()
    assert (
        body["status"] == "clarification"
        and body["clarification"]["step_id"] == "result"
    )
    assert {c["value"] for c in body["clarification"]["choices"]} == {
        "school",
        "federal",
    }
    assert "model text" not in json.dumps(body)
    assert len(body["plan"]["steps"]) == 2 and body["receipts"] == []


def test_stale_generation_and_unavailable_versions_are_not_substituted(
    client, defined_data
):
    """Neither a reload nor a missing old implementation can silently replay on current inputs."""
    old = plan(client)
    executed = client.post(PREFIX + "/execute", json=old).json()
    replay = executed["replay"]
    replay["versions"]["implementation"] = "missing-version"
    refused = client.post(PREFIX + "/execute", json=replay).json()
    assert (
        refused["issues"][0]["code"] == "version_unavailable"
        and refused["outcome"] is None
    )
    add_identity(defined_data, "00000000-0000-4000-8000-000000000099")
    refused = client.post(PREFIX + "/execute", json=old).json()
    assert (
        refused["issues"][0]["code"] == "snapshot_unavailable"
        and refused["receipts"] == []
    )


def test_hidden_parent_is_completed_and_dependent_step_is_not_executed(client):
    """Legitimate suppressed evidence is retained while dependencies cannot substitute a broader scope."""
    parent = request("retention.rate", retention_type="school", filters={"pell": "N"})
    child = {**request("dfw.rate"), "step_id": "child", "depends_on": ["result"]}
    body = client.post(PREFIX + "/execute", json=plan(client, parent, child)).json()
    assert body["outcome"] == "partial"
    assert body["receipts"][0]["result"] == {
        "status": "suppressed",
        "reason": "small_group",
    }
    assert body["step_outcomes"][1]["issue"]["code"] == "dependency_unavailable"


@pytest.mark.parametrize("first", [False, True])
def test_timeout_preserves_completed_receipt_and_cleans_up(
    client, defined_data, monkeypatch, first
):
    """A real interrupted query cannot run a later step or abandon the transaction."""
    from measures import service

    owner = service.execute
    calls = []

    def slow(operation, parameters, snapshot):
        """The second operation runs trusted synthetic SQL longer than the execution budget."""
        calls.append(operation)
        if operation == ("retention.rate" if first else "dfw.rate"):
            snapshot.named.execute(
                "WITH RECURSIVE n(x) AS (SELECT 1 UNION ALL SELECT x+1 FROM n WHERE x<1000000000) SELECT SUM(x) FROM n"
            ).fetchone()
        return owner(operation, parameters, snapshot)

    monkeypatch.setattr(service, "execute", slow)
    client.app.dependency_overrides[get_timeout] = lambda: 0.1
    steps = [
        request("retention.rate", retention_type="school"),
        {**request("dfw.rate"), "step_id": "slow"},
        {**request("persistence.rate"), "step_id": "last"},
    ]
    body = client.post(PREFIX + "/execute", json=plan(client, *steps)).json()
    assert body["outcome"] == ("failed" if first else "partial")
    assert len(body["receipts"]) == (0 if first else 1)
    assert body["step_outcomes"][0 if first else 1]["issue"]["code"] == "timeout"
    assert body["step_outcomes"][2]["outcome"] == "not_executed"
    assert calls == (["retention.rate"] if first else ["retention.rate", "dfw.rate"])
    with sqlite3.connect(defined_data, timeout=0.1) as writer:
        writer.execute("UPDATE cohort_membership SET retention=0")


def test_missing_manifest_is_typed_and_legacy_endpoint_remains_compatible(
    client, defined_data
):
    """V2 requires build identity while old extracts remain readable through existing analyses."""
    raw = plan(client)
    with sqlite3.connect(defined_data) as db:
        db.execute("DELETE FROM load_run")
    response = client.post(PREFIX + "/execute", json=raw)
    assert response.json()["issues"][0]["code"] == "version_unavailable"
    legacy = client.post("/api/v1/uncf/analyses", json={"analysis": "retention"})
    assert legacy.status_code == 200 and legacy.json()["clarification"] is not None


def test_entire_plan_is_checked_before_any_supported_step_runs(client, monkeypatch):
    """A later exploratory request cannot cause an earlier defined step to run first."""
    from measures import service

    calls = []
    monkeypatch.setattr(service, "execute", lambda *args: calls.append(True))
    exploratory = {
        "kind": "exploratory_analysis",
        "step_id": "explore",
        "operation": "correlation",
        "dataset_id": "student_year1",
        "parameters": {
            "cohort": "2023-24",
            "x": "credits_earned_y1",
            "y": "online_enrollment_share_y1",
        },
    }
    response = client.post(
        PREFIX + "/execute",
        json=plan(
            client, request("retention.rate", retention_type="school"), exploratory
        ),
    )
    assert response.json()["issues"][0]["code"] == "unsupported_operation"
    assert response.json()["outcome"] is None and not calls


@pytest.mark.parametrize("fail_first", [True, False])
def test_database_failure_stops_remaining_work_and_retains_only_completed_evidence(
    client, monkeypatch, fail_first
):
    """A real invalid SQL statement poisons the snapshot; no retry or later independent execution is allowed."""
    from measures import service

    owner = service.execute
    calls = []

    def fail(operation, parameters, snapshot):
        """Trigger a driver failure on the selected operation."""
        calls.append(operation)
        if (operation == "retention.rate") == fail_first:
            snapshot.named.execute(
                "SELECT internal_secret_column FROM missing_internal_table"
            )
        return owner(operation, parameters, snapshot)

    monkeypatch.setattr(service, "execute", fail)
    raw = plan(
        client,
        request("retention.rate", retention_type="school"),
        {**request("dfw.rate"), "step_id": "dfw"},
        {**request("persistence.rate"), "step_id": "last"},
    )
    response = client.post(PREFIX + "/execute", json=raw)
    body = response.json()
    assert body["outcome"] == ("failed" if fail_first else "partial")
    assert len(body["receipts"]) == (0 if fail_first else 1)
    assert body["step_outcomes"][-1]["outcome"] == "not_executed"
    assert len(calls) == (1 if fail_first else 2)
    assert (
        "internal_secret" not in response.text
        and "missing_internal" not in response.text
    )


def test_bounded_application_refusal_can_continue_independent_steps(
    client, monkeypatch
):
    """A declared result-limit refusal differs from an interrupted database transaction."""
    from analytics.analysis_service import OperationError
    from measures import service

    owner = service.execute

    def refuse(operation, parameters, snapshot):
        """Refuse a bounded result without touching the driver, then allow the next operation."""
        if operation == "dfw.rate":
            raise OperationError("limit_exceeded", "safe internal refusal")
        return owner(operation, parameters, snapshot)

    monkeypatch.setattr(service, "execute", refuse)
    body = client.post(
        PREFIX + "/execute",
        json=plan(
            client,
            request("dfw.rate"),
            {**request("retention.rate", retention_type="school"), "step_id": "next"},
        ),
    ).json()
    assert body["outcome"] == "partial" and body["receipts"][0]["step_id"] == "next"
    assert body["step_outcomes"][0]["issue"]["code"] == "limit_exceeded"


@pytest.mark.parametrize("setting", ["1", "10", "100", "obsolete"])
def test_obsolete_display_setting_preserves_catalog_replay_and_small_groups(
    client, monkeypatch, defined_data, setting
):
    """Old settings cannot alter policy identity or hide a one-student result."""
    raw = plan(client)
    first = client.post(PREFIX + "/execute", json=raw).json()
    monkeypatch.setenv("UNCF_MIN_STUDENTS", setting)
    response = client.post(PREFIX + "/execute", json=raw).json()
    repeated = client.post(PREFIX + "/execute", json=first["replay"]).json()
    assert response["outcome"] == repeated["outcome"] == "complete"
    assert (
        repeated["replay"]["computation_fingerprint"]
        == first["replay"]["computation_fingerprint"]
    )
    catalog = client.get(PREFIX + "/catalog").json()
    assert catalog["catalog_version"] == raw["catalog_version"]
    assert all(op["minimum_sample"] == 1 for op in catalog["operations"])
    assert all(
        op["disclosure_profile"]["version"] == "2" for op in catalog["operations"]
    )
    with sqlite3.connect(defined_data) as db:
        db.execute("UPDATE student SET gender='M' WHERE student_id='s0'")
    grouped = client.post(
        PREFIX + "/execute",
        json=plan(
            client,
            request("retention.rate", retention_type="school", group_by=["gender"]),
        ),
    ).json()
    male = next(
        row
        for row in grouped["receipts"][0]["result"]["payload"]["breakdowns"]
        if row["group"]["gender"] == "M"
    )
    assert male["status"] == "ok" and male["n_students"] == 1
    assert male["numerator"] == male["denominator"] == 1


def test_empty_source_does_not_fall_back_and_invalid_json_is_typed(client, tmp_path):
    """A missing explicitly configured database cannot borrow another extract or echo raw input."""
    raw = plan(client)
    client.app.dependency_overrides[get_runtime_factory] = lambda: (
        lambda: AnalyticsService(tmp_path / "missing.sqlite", Coverage())
    )
    body = client.post(PREFIX + "/execute", json=raw).json()
    assert body["issues"][0]["code"] == "data_unavailable" and body["outcome"] is None
    response = client.post(
        PREFIX + "/execute",
        content='{"private":"sensitive-path",',
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422 and "sensitive-path" not in response.text


@pytest.mark.parametrize("size", range(1, 10))
def test_nonempty_small_groups_retain_exact_http_evidence(client, defined_data, size):
    """Every group of one through nine retains its hand-counted retention evidence."""
    with sqlite3.connect(defined_data) as db:
        db.executemany(
            "UPDATE student SET gender='M' WHERE student_id=?",
            [(f"s{i}",) for i in range(size)],
        )
    body = client.post(
        PREFIX + "/execute",
        json=plan(
            client,
            request("retention.rate", retention_type="school", group_by=["gender"]),
        ),
    ).json()
    male = next(
        row
        for row in body["receipts"][0]["result"]["payload"]["breakdowns"]
        if row["group"]["gender"] == "M"
    )
    assert male["status"] == "ok"
    assert male["n_students"] == male["denominator"] == size
    assert male["numerator"] == min(size, 6)


def test_catalog_ignores_legacy_threshold_and_replay_rejects_old_policy(
    client, defined_data, monkeypatch
):
    """Legacy threshold metadata stays one and old policy references cannot execute."""
    from measures import service

    client.app.dependency_overrides[get_runtime_factory] = lambda: (
        lambda: AnalyticsService(defined_data, Coverage(suppression_threshold=100))
    )
    catalog = client.get(PREFIX + "/catalog").json()
    assert all(op["minimum_sample"] == 1 for op in catalog["operations"])
    replay = client.post(PREFIX + "/execute", json=plan(client)).json()["replay"]
    replay["policies"][0]["version"] = "1"

    def forbidden(*args, **kwargs):
        """An old policy must be refused before any calculation starts."""
        pytest.fail("stale policy executed a metric")

    monkeypatch.setattr(service, "execute", forbidden)
    refused = client.post(PREFIX + "/execute", json=replay)
    assert refused.status_code == 409
    assert refused.json()["issues"][0]["code"] == "version_unavailable"
    assert refused.json()["receipts"] == []


@pytest.mark.parametrize("bounded_failure", [False, True])
def test_owner_cleanup_failure_preserves_completed_evidence(
    client, defined_data, monkeypatch, bounded_failure
):
    """Cleanup reports its failure after close without discarding completed in-memory evidence."""
    from contextlib import contextmanager

    from analytics.data_access import connection_snapshot

    events = []

    class FailedCleanup(sqlite3.Connection):
        """Observe actual close after a synthetic rollback failure."""

        def rollback(self):
            """Fail transaction release so the response must not claim successful completion."""
            events.append("rollback")
            raise sqlite3.OperationalError("private cleanup failure")

        def close(self):
            """Finish connection cleanup before returning control to the HTTP caller."""
            events.append("close")
            super().close()

    @contextmanager
    def source():
        """Open the real source on the worker that owns and closes it."""
        with connection_snapshot(
            sqlite3.connect(defined_data, factory=FailedCleanup)
        ) as snapshot:
            yield snapshot

    raw = plan(client)
    if bounded_failure:
        from analytics.analysis_service import OperationError
        from measures import service

        owner = service.execute

        def refuse(operation, parameters, snapshot):
            """Leave the transaction usable after a bounded refusal of the second operation."""
            if operation == "dfw.rate":
                raise OperationError("limit_exceeded", "bounded refusal")
            return owner(operation, parameters, snapshot)

        monkeypatch.setattr(service, "execute", refuse)
        raw["steps"].append({**request("dfw.rate"), "step_id": "dfw"})
    client.app.dependency_overrides[get_runtime_factory] = lambda: (
        lambda: AnalyticsService(None, Coverage(), snapshot_factory=source)
    )
    body = client.post(PREFIX + "/execute", json=raw).json()
    assert body["outcome"] == ("partial" if bounded_failure else "complete")
    assert body["receipts"][0]["result"]["payload"]["numerator"] == 6
    assert body["receipts"][0]["result"]["payload"]["denominator"] == 12
    assert body["step_outcomes"][:1] == [
        {"step_id": "result", "outcome": "completed", "issue": None}
    ]
    assert body["issues"][-1]["code"] == "data_unavailable"
    assert body["issues"][-1]["step_id"] is None
    assert "cleanup" in body["message"]
    assert "private cleanup failure" not in json.dumps(body)
    assert events == ["rollback", "close"]


def test_published_openapi_keeps_operation_and_body_restrictions(client):
    """The complete schema is valid OpenAPI, including operation unions and replay input."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert PREFIX + "/execute" in schema["paths"]

    def visit(node):
        """Require string refs for every OpenAPI discriminator mapping."""
        if isinstance(node, dict):
            if "discriminator" in node:
                assert all(
                    isinstance(value, str)
                    for value in node["discriminator"].get("mapping", {}).values()
                )
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for value in node:
                visit(value)

    visit(schema)
    assert (
        schema["components"]["schemas"]["ExecutablePlan"]["additionalProperties"]
        is False
    )


def test_plan_steps_keep_one_snapshot_during_an_atomic_reload(
    client, defined_data, monkeypatch
):
    """A committed new generation between callbacks cannot mix six-retained and zero-retained evidence."""
    from measures import service

    with sqlite3.connect(defined_data) as db:
        db.execute("PRAGMA journal_mode=WAL")
    owner = service.execute
    calls = []

    def reload(operation, parameters, snapshot):
        """Publish a generation after the first completed callback while the plan remains pinned."""
        result = owner(operation, parameters, snapshot)
        calls.append(operation)
        if len(calls) == 1:
            with sqlite3.connect(defined_data) as writer:
                manifest = json.loads(
                    writer.execute("SELECT build_manifest FROM load_run").fetchone()[0]
                )
                manifest["load_generation"] = "00000000-0000-4000-8000-000000000099"
                writer.execute("UPDATE cohort_membership SET retention=0")
                writer.execute(
                    "UPDATE load_run SET build_manifest=?", (json.dumps(manifest),)
                )
        return result

    raw = plan(
        client,
        request("retention.rate", retention_type="school"),
        {**request("retention.rate", retention_type="school"), "step_id": "second"},
    )
    monkeypatch.setattr(service, "execute", reload)
    body = client.post(PREFIX + "/execute", json=raw).json()
    assert body["outcome"] == "complete"
    assert [
        receipt["result"]["payload"]["numerator"] for receipt in body["receipts"]
    ] == [6, 6]
    assert {receipt["source"]["snapshot_ref"] for receipt in body["receipts"]} == {
        raw["snapshot_ref"]
    }
    assert client.get(PREFIX + "/catalog").json()["snapshot_ref"] != raw["snapshot_ref"]


def test_all_steps_keep_small_groups_visible_during_obsolete_setting_changes(
    client, defined_data, monkeypatch
):
    """An in-flight obsolete setting cannot hide either step or change policy identity."""
    from measures import service

    with sqlite3.connect(defined_data) as db:
        db.execute("UPDATE student SET gender='M' WHERE student_id='s0'")
    owner, calls = service.execute, []

    def change_setting(operation, parameters, snapshot):
        """Raise the obsolete threshold after each callback to test the following step."""
        result = owner(operation, parameters, snapshot)
        calls.append(operation)
        monkeypatch.setenv("UNCF_MIN_STUDENTS", "100")
        return result

    request_one = request(
        "retention.rate", retention_type="school", group_by=["gender"]
    )
    raw = plan(client, request_one, {**request_one, "step_id": "second"})
    monkeypatch.setattr(service, "execute", change_setting)
    body = client.post(PREFIX + "/execute", json=raw).json()
    assert body["outcome"] == "complete"
    for receipt in body["receipts"]:
        male = next(
            row
            for row in receipt["result"]["payload"]["breakdowns"]
            if row["group"]["gender"] == "M"
        )
        assert male["status"] == "ok" and male["n_students"] == 1
        assert male["numerator"] == male["denominator"] == 1
    assert (
        client.get(PREFIX + "/catalog").json()["catalog_version"]
        == raw["catalog_version"]
    )


@pytest.mark.parametrize("threshold", [10, 100])
def test_legacy_threshold_changes_do_not_stale_catalog_or_replay(
    client, defined_data, threshold
):
    """Ignored legacy settings cannot pin catalog/configuration or computation identities."""
    raw = plan(client)
    first = client.post(PREFIX + "/execute", json=raw).json()
    client.app.dependency_overrides[get_runtime_factory] = lambda: (
        lambda: AnalyticsService(
            defined_data, Coverage(suppression_threshold=threshold)
        )
    )
    assert (
        client.get(PREFIX + "/catalog").json()["catalog_version"]
        == raw["catalog_version"]
    )
    repeated = client.post(PREFIX + "/execute", json=first["replay"]).json()
    assert repeated["outcome"] == "complete"
    assert repeated["replay"] == first["replay"]
    assert repeated["receipts"][0]["result"]["payload"]["numerator"] == 6


def test_partial_execution_does_not_change_computation_identity(client, monkeypatch):
    """A bounded sibling failure changes outcomes, never the requested computation identity."""
    from analytics.analysis_service import OperationError
    from measures import service

    raw = plan(
        client,
        request("retention.rate", retention_type="school"),
        {**request("dfw.rate"), "step_id": "dfw"},
    )
    complete = client.post(PREFIX + "/execute", json=raw).json()
    owner = service.execute

    def refuse(operation, parameters, snapshot):
        """Fail one sibling without changing the successfully calculated retention evidence."""
        if operation == "dfw.rate":
            raise OperationError("limit_exceeded", "bounded refusal")
        return owner(operation, parameters, snapshot)

    monkeypatch.setattr(service, "execute", refuse)
    partial = client.post(PREFIX + "/execute", json=raw).json()
    assert partial["outcome"] == "partial"
    assert partial["replay"] == complete["replay"]
    assert partial["replay"]["fingerprint_schema"] == 2
    assert "disclosure_context" not in partial["replay"]
    assert (
        partial["receipts"][0]["computation_fingerprint"]
        == complete["receipts"][0]["computation_fingerprint"]
    )
    monkeypatch.setattr(service, "execute", owner)
    repeated = client.post(PREFIX + "/execute", json=partial["replay"]).json()
    assert repeated["outcome"] == "complete"
    assert repeated["replay"] == complete["replay"]


def test_obsolete_fingerprint_inputs_are_refused_before_calculation(
    client, monkeypatch
):
    """Old fingerprint semantics and suppression-context fields cannot be silently upgraded."""
    from measures import service

    replay = client.post(PREFIX + "/execute", json=plan(client)).json()["replay"]

    def forbidden(*args, **kwargs):
        """Invalid replay inputs must not enter a calculation owner."""
        pytest.fail("obsolete replay executed a metric")

    monkeypatch.setattr(service, "execute", forbidden)
    for changed in (
        {**replay, "fingerprint_schema": 1},
        {**replay, "disclosure_context": ["obsolete"]},
    ):
        refused = client.post(PREFIX + "/execute", json=changed)
        assert refused.status_code == 422
        assert refused.json()["issues"][0]["code"] == "invalid_plan"
        assert refused.json()["receipts"] == []


def test_catalog_names_missing_schema_prerequisites(client):
    """Capabilities explain registered missing columns and preserve distinct definition metadata."""
    operations = {
        op["id"]: op for op in client.get(PREFIX + "/catalog").json()["operations"]
    }
    retention = operations["retention.rate"]
    assert retention["available"] and retention["missing_prerequisites"] == []
    assert retention["executor"] and retention["aliases"]
    legacy = operations["legacy.entry_major_retention"]
    assert legacy["missing_prerequisites"] == [
        "cohort_membership.program_of_study_term_1"
    ]
    raw = plan(
        client,
        {
            "kind": "legacy_analysis",
            "step_id": "legacy",
            "operation_id": "legacy.entry_major_retention",
            "parameters": {"cohort": "2023-24"},
        },
    )
    refused = client.post(PREFIX + "/validate", json=raw).json()
    assert refused["issues"][0]["step_id"] == "legacy"
    assert refused["issues"][0]["code"] == "data_unavailable"
    assert (
        "cohort_membership.program_of_study_term_1" in refused["issues"][0]["message"]
    )


@pytest.mark.parametrize("threshold", [10, 100])
def test_overlapping_zero_rates_and_small_exclusions_survive_http(
    client, defined_data, threshold
):
    """Twelve synthetic entrants include one missing outcome and one nonretained male student."""
    with sqlite3.connect(defined_data) as db:
        db.execute("UPDATE student SET gender='M' WHERE student_id='s11'")
        db.execute("UPDATE cohort_membership SET retention=NULL WHERE student_id='s0'")
    client.app.dependency_overrides[get_runtime_factory] = lambda: (
        lambda: AnalyticsService(
            defined_data, Coverage(suppression_threshold=threshold)
        )
    )
    raw = plan(
        client,
        request("retention.rate", retention_type="school", group_by=["gender"]),
        {
            **request(
                "retention.rate", retention_type="school", filters={"gender": "M"}
            ),
            "step_id": "male",
        },
        {
            **request(
                "retention.rate", retention_type="school", filters={"gender": "F"}
            ),
            "step_id": "female",
        },
    )
    body = client.post(PREFIX + "/execute", json=raw).json()
    assert body["outcome"] == "complete"
    overall, male, female = [
        receipt["result"]["payload"] for receipt in body["receipts"]
    ]
    assert (overall["numerator"], overall["denominator"], overall["n_excluded"]) == (
        5,
        11,
        1,
    )
    assert (male["numerator"], male["denominator"], male["value"]) == (0, 1, 0)
    assert (female["numerator"], female["denominator"], female["n_excluded"]) == (
        5,
        10,
        1,
    )
    grouped_male = next(
        row for row in overall["breakdowns"] if row["group"]["gender"] == "M"
    )
    assert grouped_male["status"] == "ok"
    assert (
        grouped_male["numerator"],
        grouped_male["denominator"],
        grouped_male["value"],
    ) == (0, 1, 0)


def test_many_missing_schema_columns_keep_bounded_typed_errors(client, defined_data):
    """A large missing schema retains its exact catalog list without overflowing issue text."""
    with sqlite3.connect(defined_data) as db:
        for table in ("student", "course", "course_enrollment", "term"):
            db.execute(f'DROP TABLE "{table}"')
    catalog = client.get(PREFIX + "/catalog").json()
    operation = next(
        op for op in catalog["operations"] if op["id"] == "student_paths.summary"
    )
    assert not operation["available"] and len(operation["missing_prerequisites"]) > 20
    raw = plan(client, request("student_paths.summary", retention_type="school"))
    refused = client.post(PREFIX + "/validate", json=raw).json()
    assert refused["issues"][0]["code"] == "data_unavailable"
    assert operation["missing_prerequisites"][0] in refused["issues"][0]["message"]
    assert len(refused["issues"][0]["message"]) <= 500
