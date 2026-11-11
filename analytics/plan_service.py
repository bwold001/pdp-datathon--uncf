"""Validate complete plans and coordinate existing owners on one read snapshot, without metric formulas."""

from datetime import datetime, timezone
from functools import lru_cache, wraps
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

from pydantic import TypeAdapter, ValidationError

from analytics.analysis_service import AnalysisService, OperationError
from analytics.contracts_v2 import (
    AnalysisIssue,
    Choice,
    Clarification,
    Cohort,
    ExecutablePlan,
    ProposedPlan,
    Receipt,
    Source,
    StepOutcome,
    UnresolvedChoice,
    VersionReference,
    Versions,
    VisibleResult,
    to_executable,
)
from analytics.disclosure import disclose_plan, stage_defined
from analytics.execution import CURRENT, CalculationCancelled, check_cancelled
from analytics.plan_contracts import (
    CatalogChoices,
    CatalogOperation,
    CatalogResponse,
    CoverageDeclaration,
    ExecutionInfo,
    PlanResponse,
)
from analytics.provenance import (
    DataUnavailable,
    ReplaySpec,
    VersionUnavailable,
    coverage_digest,
    digest,
    make_replay_spec,
    step_fingerprint,
    validate_replay,
)
from measures.disclosure import dashboard_scope, profile
from measures.registry import CATALOG_VERSION

_TABLES = (
    "student",
    "cohort_membership",
    "course",
    "course_enrollment",
    "term",
    "data_provider",
)
_QUESTIONS = {
    "cohort": "Which entry cohort?",
    "retention_type": "Which retention definition?",
    "course": "Which course?",
    "credential": "Which credential?",
    "program": "Which program definition?",
    "terms": "How many terms?",
}


def _configuration_snapshot(function):
    """Keep one server-selected dashboard threshold for metadata, all steps and disclosure."""

    @wraps(function)
    def invoke(*args, **kwargs):
        """Release the threshold context after the source owner and final evidence projection finish."""
        with dashboard_scope():
            return function(*args, **kwargs)

    return invoke


@lru_cache(maxsize=1)
def implementation_version():
    """Fingerprint shipped owner/orchestration/adapter source without exposing checkout paths."""
    root = Path(__file__).resolve().parents[1]
    files = sorted(
        p
        for folder in ("analytics", "measures", "gap_finder", "api")
        for p in (root / folder).rglob("*.py")
        if "tests" not in p.parts and p.name != "conftest.py"
    )
    return digest(
        [
            (p.relative_to(root).as_posix(), sha256(p.read_bytes()).hexdigest())
            for p in files
        ]
    )


def issue(code, step_id=None):
    """Use fixed application messages rather than raw driver, validation or configuration errors."""
    messages = {
        "invalid_plan": "The plan is invalid or incomplete.",
        "unsupported_operation": "The operation is not registered for execution.",
        "unsupported_parameter": "A parameter is unsupported or outside the current catalog choices.",
        "data_unavailable": "The configured data cannot support this execution.",
        "snapshot_unavailable": "The requested snapshot is unavailable. Read the catalog and review the updated scope.",
        "stale_plan": "The catalog changed. Read the catalog and review the updated scope.",
        "version_unavailable": "The required computation versions or build identity are unavailable.",
        "limit_exceeded": "The request exceeds the supported result or execution limit.",
        "timeout": "The execution deadline was reached after transaction cleanup.",
        "dependency_unavailable": "Required evidence from an earlier step is unavailable.",
        "clarification_required": "A material parameter still requires a supported choice.",
    }
    return AnalysisIssue(
        code=code,
        step_id=step_id,
        message=messages.get(code, messages["data_unavailable"]),
    )


def refusal(code, plan=None, step_id=None):
    """Return an unexecuted typed refusal with no numerical evidence."""
    return PlanResponse(
        protocol_version=2,
        status="error",
        plan=plan,
        issues=(issue(code, step_id),),
        message="The plan was not executed.",
    )


def _schema(snapshot):
    """Inspect fixed normalized-table metadata without poisoning a transaction on absent columns."""
    if snapshot.backend == "postgresql":
        rows = snapshot.named.execute(
            "SELECT table_name, column_name FROM information_schema.columns WHERE table_schema = current_schema()"
        ).fetchall()
        return {
            table: {row["column_name"] for row in rows if row["table_name"] == table}
            for table in _TABLES
        }
    return {
        table: {
            row["name"]
            for row in snapshot.named.execute(
                f'PRAGMA table_info("{table}")'
            ).fetchall()
        }
        for table in _TABLES
    }


def _requirements(spec, parameters=None):
    """Describe executor input capabilities, leaving actual evidence/coverage outcomes to owners."""
    needs = {
        "data_provider": {"loaded_at", "source_file", "file_sha256", "provider_id"},
        "cohort_membership": {"student_id", "cohort"},
    }
    if spec.kind == "defined_measure":
        needs["student"] = {"student_id", "gender", "race", "ethnicity", "student_age"}
        needs["cohort_membership"] |= {
            "cohort_term",
            "enrollment_type",
            "enrollment_intensity_first_term",
            "pell_status_first_year",
        }
        columns = {
            "retention.rate": {"retention"},
            "persistence.rate": {"persistence"},
            "credit_completion.ratio": {
                "number_of_credits_attempted_yr_1",
                "number_of_credits_earned_yr_1",
            },
            "gateway.math_completion": {
                "gateway_math_status",
                "completed_gateway_math_year1",
            },
            "gateway.english_completion": {
                "gateway_english_status",
                "completed_gateway_english_year1",
            },
        }
        needs["cohort_membership"] |= columns.get(spec.id, set())
        if (
            spec.measure is None
            or spec.id == "dfw.rate"
            or getattr(parameters, "retention_type", None) == "federal"
        ):
            needs.update(
                course_enrollment={"student_id", "cohort", "course_id", "term_id"},
                course={"course_id", "course_prefix", "course_number"},
                term={"term_id", "academic_year", "academic_term"},
            )
        if spec.id.startswith("dfw."):
            needs["course_enrollment"] |= {
                "grade",
                "delivery_method",
                "course_name",
                "math_or_english_gateway",
            }
        if spec.measure is None:
            needs["term"].add("sort_order")
            needs["course_enrollment"] |= {
                "enrollment_id",
                "section_id",
                "course_name",
                "grade",
                "delivery_method",
                "math_or_english_gateway",
                "course_type",
            }
        if spec.id in (
            "credit_momentum.summary",
            "gateway.course_outcomes",
            "student_paths.summary",
        ):
            needs["cohort_membership"].add("retention")
        if spec.id == "credit_momentum.summary":
            needs["cohort_membership"] |= {
                "number_of_credits_attempted_yr_1",
                "number_of_credits_earned_yr_1",
            }
            needs["course_enrollment"] |= {
                "number_of_credits_attempted",
                "number_of_credits_earned",
            }
        if spec.id == "student_paths.summary":
            needs["cohort_membership"] |= {
                "first_year_to_bachelors_at_coh",
                "first_year_to_a_or_c_at_cohort",
            }
            needs["course_enrollment"] |= {
                "enrolled_at_other_institution_s",
                "c_enrollment_record_at_other",
            }
    elif spec.id == "legacy.entry_major_retention":
        needs["cohort_membership"] |= {"retention", "program_of_study_term_1"}
    elif spec.id == "legacy.graduation":
        needs["cohort_membership"] |= {
            "program_of_study_term_1",
            "credential_type_sought_year_1",
            "first_year_to_bachelors_at_coh",
        }
    else:
        needs.update(
            student={"student_id", "ethnicity"},
            term={"term_id", "academic_year"},
            course_enrollment={
                "student_id",
                "cohort",
                "course_id",
                "term_id",
                "term_program_of_study",
            },
        )
    return needs


def _available(spec, schema, parameters=None):
    """Refuse unsupported source shapes before any requested operation runs."""
    return all(
        columns <= schema.get(table, set())
        for table, columns in _requirements(spec, parameters).items()
    )


def _usable(result):
    """A dependency requires actual visible evidence rather than a hidden-only table or status."""
    if not isinstance(result, VisibleResult):
        return False
    if result.payload.kind == "table":
        return any(
            row.status in ("ok", "provisional")
            and any(type(cell) in (int, float) for cell in row.cells)
            for row in result.payload.rows
        )
    return True


class PlanService:
    """Own deterministic metadata, validation, execution, disclosure and receipt assembly."""

    def __init__(self, runtime):
        """Use the exact configured legacy runtime factory and explicit shared coverage."""
        self.runtime = runtime
        self.owner = AnalysisService(runtime.coverage)

    def _configuration(self):
        """Resolve active server-only policies and coverage for stable version references."""
        try:
            policies = {
                spec.disclosure_profile: profile(spec.disclosure_profile)
                for spec in self.owner.operations.values()
            }
            return digest(
                {
                    "policies": {
                        key: {"version": value.version, "minimum": value.minimum}
                        for key, value in policies.items()
                    },
                    "coverage": coverage_digest(self.runtime.coverage),
                }
            )
        except (OSError, ValueError) as error:
            raise VersionUnavailable(
                "Computation configuration is unavailable."
            ) from error

    def _catalog(self, snapshot):
        """Read safe choices and schema capabilities within the caller's pinned transaction."""
        schema = _schema(snapshot)
        configuration = self._configuration()
        implementation = implementation_version()
        version = digest(
            {
                "catalog": CATALOG_VERSION,
                "configuration": configuration,
                "implementation": implementation,
                "operations": [
                    (s.id, s.version, s.disclosure_profile)
                    for s in self.owner.operations.values()
                ],
                "schema": {table: sorted(columns) for table, columns in schema.items()},
            }
        )
        cohorts = []
        if "cohort" in schema["cohort_membership"]:
            for row in snapshot.named.execute(
                "SELECT DISTINCT cohort FROM cohort_membership ORDER BY cohort"
            ).fetchall():
                try:
                    cohorts.append(TypeAdapter(Cohort).validate_python(row["cohort"]))
                except ValidationError:
                    continue
        if len(cohorts) > 100:
            raise OperationError(
                "limit_exceeded", "Catalog cohort choices exceed the supported limit."
            )
        courses = []
        if {"course_prefix", "course_number"} <= schema["course"]:
            rows = snapshot.named.execute(
                "SELECT DISTINCT UPPER(TRIM(course_prefix)) || ' ' || UPPER(TRIM(course_number)) AS code FROM course ORDER BY code LIMIT 101"
            ).fetchall()
            courses = [
                row["code"]
                for row in rows
                if isinstance(row["code"], str) and 0 < len(row["code"].strip()) <= 500
            ]
        source = Source(
            label="synthetic",
            snapshot_ref=snapshot.identity.snapshot_ref,
            fingerprint=snapshot.identity.source_fingerprint,
            loaded_at=snapshot.identity.loaded_at,
            coverage=self.runtime.coverage.provenance
            or "Synthetic extract; completeness is not certified.",
        )
        operations = []
        for spec in self.owner.operations.values():
            policy = profile(spec.disclosure_profile)
            available = _available(spec, schema)
            operations.append(
                CatalogOperation(
                    id=spec.id,
                    version=spec.version,
                    kind=spec.kind,
                    label=spec.label,
                    purpose=spec.purpose,
                    available=available,
                    unavailable_reason=None if available else "data_unavailable",
                    parameters_schema=spec.parameters.model_json_schema(),
                    supported_filters=spec.supported_filters,
                    supported_breakdowns=spec.supported_breakdowns,
                    grain=spec.grain,
                    population=spec.population,
                    time_semantics=spec.time_semantics,
                    exclusions=spec.exclusions,
                    required_coverage=spec.required_coverage,
                    units=spec.units,
                    component_denominators=spec.component_denominators,
                    limitations=spec.limitations,
                    disclosure_profile=VersionReference(
                        id=policy.id, version=policy.version
                    ),
                    minimum_sample=self.runtime.coverage.suppression_threshold
                    if policy.id == "legacy_analytics_v1"
                    else policy.minimum,
                )
            )
        return CatalogResponse(
            catalog_version=version,
            snapshot_ref=snapshot.identity.snapshot_ref,
            snapshot=snapshot.identity,
            source=source,
            coverage=CoverageDeclaration(
                complete_academic_years=sorted(
                    set(self.runtime.coverage.complete_academic_years)
                ),
                cohort_followup=[
                    {"cohort": cohort, "years": years}
                    for cohort, years in sorted(
                        self.runtime.coverage.cohort_followup_years.items()
                    )
                ],
                cutoff=self.runtime.coverage.cutoff,
                provenance=source.coverage,
                provisional_retention_cohorts=sorted(
                    set(self.runtime.coverage.provisional_retention_cohorts)
                ),
            ),
            operations=operations,
            choices=CatalogChoices(
                cohorts=cohorts, courses=courses[:100], more_courses=len(courses) > 100
            ),
            configuration_version=configuration,
            implementation_version=implementation,
        ), schema

    @_configuration_snapshot
    def catalog(self):
        """Open one source for metadata only, with cleanup before any public catalog response."""
        try:
            with self.runtime.snapshot() as snapshot:
                result, _ = self._catalog(snapshot)
            return result
        except CalculationCancelled:
            return refusal("timeout")
        except (DataUnavailable, OperationError) as error:
            return refusal(error.code)
        except (OSError, ValueError):
            return refusal("version_unavailable")

    def _check(self, plan, catalog, schema):
        """Validate the entire plan's references/capabilities before any step calculation."""
        if plan.snapshot_ref != catalog.snapshot_ref:
            return (issue("snapshot_unavailable"),)
        if plan.catalog_version != catalog.catalog_version:
            return (issue("stale_plan"),)
        issues = []
        for step in plan.steps:
            operation = getattr(step, "operation_id", None)
            spec = self.owner.operations.get(operation)
            if spec is None or spec.kind != step.kind:
                issues.append(issue("unsupported_operation", step.step_id))
                continue
            cohort = getattr(step.parameters, "cohort", None)
            if isinstance(cohort, str) and cohort not in catalog.choices.cohorts:
                issues.append(issue("unsupported_parameter", step.step_id))
            if not _available(spec, schema, step.parameters):
                issues.append(issue("data_unavailable", step.step_id))
        return tuple(issues)

    def _proposal(self, plan, catalog):
        """Replace untrusted question/options text with current canonical server choices."""
        raw = plan.model_dump(mode="python")
        choices = {
            "cohort": tuple(Choice(value=c, label=c) for c in catalog.choices.cohorts),
            "retention_type": catalog.choices.retention_types,
            "credential": catalog.choices.credentials,
            "program": catalog.choices.programs,
            "course": tuple(Choice(value=c, label=c) for c in catalog.choices.courses),
            "terms": tuple(Choice(value=n, label=f"{n} terms") for n in range(2, 7)),
        }
        for typed, copied in zip(plan.steps, raw["steps"]):
            for key in type(typed.parameters).model_fields:
                if isinstance(getattr(typed.parameters, key), UnresolvedChoice):
                    if key not in choices or not choices[key]:
                        raise OperationError(
                            "data_unavailable", "No current choices are available."
                        )
                    copied["parameters"][key] = UnresolvedChoice(
                        unresolved=True, question=_QUESTIONS[key], choices=choices[key]
                    ).model_dump()
        return ProposedPlan.model_validate(raw)

    @_configuration_snapshot
    def validate(self, plan):
        """Return full clarification or canonical confirmation without executing any operation."""
        try:
            with self.runtime.snapshot() as snapshot:
                catalog, schema = self._catalog(snapshot)
                problems = self._check(plan, catalog, schema)
                if problems:
                    return PlanResponse(
                        protocol_version=2,
                        status="error",
                        plan=plan,
                        issues=problems,
                        message="The plan was not executed.",
                    )
                if isinstance(plan, ProposedPlan):
                    plan = self._proposal(plan, catalog)
                    for step in plan.steps:
                        for key in type(step.parameters).model_fields:
                            pending = getattr(step.parameters, key)
                            if isinstance(pending, UnresolvedChoice):
                                return PlanResponse(
                                    protocol_version=2,
                                    status="clarification",
                                    plan=plan,
                                    clarification=Clarification(
                                        step_id=step.step_id,
                                        parameter=key,
                                        question=pending.question,
                                        choices=pending.choices,
                                    ),
                                    message="Choose the scope for this step.",
                                )
                    plan = to_executable(plan)
            return PlanResponse(
                protocol_version=2,
                status="confirmation",
                plan=plan,
                message="Review the complete explicit scope before execution.",
            )
        except CalculationCancelled:
            return refusal("timeout", plan)
        except (DataUnavailable, OperationError) as error:
            return refusal(error.code, plan)
        except (OSError, ValueError):
            return refusal("version_unavailable", plan)

    def _versions(self, plan, catalog, identity):
        """Resolve current operation/policy/implementation/configuration versions, without substitution."""
        policies = {
            self.owner.operations[step.operation_id].disclosure_profile
            for step in plan.steps
        }
        references = tuple(
            VersionReference(id=key, version=profile(key).version)
            for key in sorted(policies)
        )
        versions = Versions(
            catalog=catalog.catalog_version,
            pipeline=identity.pipeline_version,
            configuration=catalog.configuration_version,
            coverage=coverage_digest(self.runtime.coverage),
            implementation=catalog.implementation_version,
            disclosure=digest([p.model_dump() for p in references]),
        )
        operations = tuple(
            VersionReference(id=key, version=self.owner.operations[key].version)
            for key in sorted({step.operation_id for step in plan.steps})
        )
        return versions, operations, references

    @_configuration_snapshot
    def execute_plan(self, plan: ExecutablePlan, replay: ReplaySpec | None = None):
        """Run sequential steps on one worker/source, and project only after transaction cleanup."""
        plan = ExecutablePlan.model_validate(plan)
        evidence, outcomes, times = {}, {}, {}
        identity = catalog = versions = operations = policies = None
        execution_id, started = uuid4().hex, datetime.now(timezone.utc)
        current, begun, halt = None, False, None
        try:
            with self.runtime.snapshot() as snapshot:
                catalog, schema = self._catalog(snapshot)
                problems = self._check(plan, catalog, schema)
                if problems:
                    if replay is not None and problems[0].code == "stale_plan":
                        return refusal("version_unavailable", plan)
                    return PlanResponse(
                        protocol_version=2,
                        status="error",
                        plan=plan,
                        issues=problems,
                        message="The plan was not executed.",
                    )
                identity = snapshot.identity
                versions, operations, policies = self._versions(plan, catalog, identity)
                if replay is not None:
                    if (
                        replay.versions != versions
                        or tuple(sorted(replay.operations, key=lambda v: v.id))
                        != operations
                        or tuple(sorted(replay.policies, key=lambda v: v.id))
                        != policies
                    ):
                        raise VersionUnavailable(
                            "The original computation versions are unavailable."
                        )
                    try:
                        validate_replay(
                            replay,
                            identity,
                            versions,
                            operations,
                            self.runtime.coverage,
                            policies,
                        )
                    except ValueError as error:
                        raise OperationError(
                            "invalid_plan", "Replay fingerprint is inconsistent."
                        ) from error
                begun = True
                for step in plan.steps:
                    current = step.step_id
                    if any(
                        dep not in evidence or not _usable(evidence[dep].result)
                        for dep in step.depends_on
                    ):
                        outcomes[current] = StepOutcome(
                            step_id=current,
                            outcome="not_executed",
                            issue=issue("dependency_unavailable", current),
                        )
                        continue
                    check_cancelled()
                    before = datetime.now(timezone.utc)
                    try:
                        evidence[current] = self.owner.execute(step, snapshot)
                    except OperationError as error:
                        outcomes[current] = StepOutcome(
                            step_id=current,
                            outcome="failed",
                            issue=issue(error.code, current),
                        )
                        continue
                    times[current] = before, datetime.now(timezone.utc)
                    outcomes[current] = StepOutcome(
                        step_id=current, outcome="completed"
                    )
        except CalculationCancelled:
            halt = "timeout"
        except OperationError as error:
            halt = error.code
        except DataUnavailable as error:
            halt = error.code
        except (OSError, ValueError):
            halt = "version_unavailable" if not begun else "data_unavailable"
        except Exception:
            halt = "data_unavailable"
        if not begun:
            return refusal(halt or "data_unavailable", plan)
        if (
            halt
            and current
            and (current not in outcomes or outcomes[current].outcome == "completed")
        ):
            evidence.pop(current, None)
            times.pop(current, None)
            outcomes[current] = StepOutcome(
                step_id=current, outcome="failed", issue=issue(halt, current)
            )
        for step in plan.steps:
            if step.step_id not in outcomes:
                dependent = any(
                    dep not in evidence or not _usable(evidence[dep].result)
                    for dep in step.depends_on
                )
                code = (
                    "dependency_unavailable"
                    if dependent
                    else halt or "data_unavailable"
                )
                outcomes[step.step_id] = StepOutcome(
                    step_id=step.step_id,
                    outcome="not_executed",
                    issue=issue(code, step.step_id),
                )
        # No connection is passed into finalization; an expired query budget cannot discard staged partial evidence.
        token = CURRENT.set(None)
        try:
            return self._finalize(
                plan,
                evidence,
                outcomes,
                times,
                identity,
                catalog,
                versions,
                operations,
                policies,
                execution_id,
                started,
                halt,
            )
        finally:
            CURRENT.reset(token)

    def _finalize(
        self,
        plan,
        evidence,
        outcomes,
        times,
        identity,
        catalog,
        versions,
        operations,
        policies,
        execution_id,
        started,
        halt,
    ):
        """Apply whole-response disclosure and assemble safe, fingerprinted receipts from bounded memory only."""
        ordered = tuple(outcomes[s.step_id] for s in plan.steps)
        completed = tuple(s for s in plan.steps if s.step_id in evidence)
        context = (
            digest(
                [
                    (
                        state.step_id,
                        state.outcome,
                        state.issue.code if state.issue else None,
                    )
                    for state in ordered
                ]
            ),
        )
        replay = make_replay_spec(
            plan,
            identity,
            versions,
            operations,
            self.runtime.coverage,
            context,
            policies,
        )
        projected = (
            disclose_plan(
                tuple(
                    stage_defined(
                        s.step_id,
                        self.owner.operations[s.operation_id],
                        evidence[s.step_id],
                    )
                    for s in completed
                )
            )
            if completed
            else ()
        )
        receipts = []
        for step, disclosed in zip(completed, projected):
            spec = self.owner.operations[step.operation_id]
            before, after = times[step.step_id]
            receipts.append(
                Receipt(
                    schema_version=2,
                    step_id=step.step_id,
                    request=step,
                    operation_id=spec.id,
                    operation_version=spec.version,
                    disclosure_profile=disclosed.profile,
                    population=spec.population,
                    time_window=spec.time_semantics,
                    grain=spec.grain,
                    definitions=tuple(
                        VersionReference(id=key, version=spec.version)
                        for key in spec.definitions
                    ),
                    assumptions=(
                        "All results are synthetic.",
                        *evidence[step.step_id].context,
                    ),
                    limitations=spec.limitations,
                    source=catalog.source,
                    versions=versions,
                    computation_fingerprint=step_fingerprint(replay, step.step_id),
                    execution_id=execution_id,
                    started_at=before,
                    completed_at=after,
                    result=disclosed.result,
                )
            )
        outcome = (
            "complete"
            if len(receipts) == len(plan.steps)
            else "partial"
            if receipts
            else "failed"
        )
        return PlanResponse(
            protocol_version=2,
            status="answer" if receipts else "error",
            plan=plan,
            outcome=outcome,
            step_outcomes=ordered,
            receipts=receipts,
            issues=tuple(state.issue for state in ordered if state.issue),
            replay=replay,
            execution=ExecutionInfo(
                execution_id=execution_id,
                started_at=started,
                completed_at=datetime.now(timezone.utc),
            ),
            message="Synthetic execution completed."
            if outcome == "complete"
            else "Synthetic execution returned partial evidence."
            if receipts
            else "The execution did not complete any result.",
        )
