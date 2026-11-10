"""Read-only normalized-data service supplying the same receipts to API and chat."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime
from hashlib import sha256
from pathlib import Path

from analytics import enrollment, graduation, retention
from analytics.definitions import DEFINITIONS
from analytics.presentation import suppress
from analytics.schemas import (
    AnalysisReceipt,
    AnalysisRequest,
    AnalysisResponse,
    CalculationRow,
    Clarification,
)
from analytics.coverage import Coverage
from analytics.programs import PROGRAMS, resolve_program


class DataUnavailable(Exception):
    """A configured database failed without exposing connection details."""


class AnalyticsService:
    """Own deterministic analyses and serialize evidence only after suppression."""

    def __init__(self, database: Path | None, coverage: Coverage, *, connection_factory=None):
        """Use an explicit connection provider or the standalone normalized extract."""
        self.database = database
        self.coverage = coverage
        self.connection_factory = connection_factory

    @contextmanager
    def connect(self):
        """Read one snapshot from the explicit provider or the standalone extract."""
        if self.connection_factory is not None:
            with self.connection_factory() as connection:
                yield connection
            return
        if self.database is None:
            raise DataUnavailable("No database is configured")
        db = sqlite3.connect(f"{self.database.resolve().as_uri()}?mode=ro", uri=True)
        db.row_factory = sqlite3.Row
        try:
            db.execute("PRAGMA query_only = ON")
            db.execute("BEGIN")
            yield db
        finally:
            db.rollback()
            db.close()

    def catalog(self) -> dict:
        """Advertise approved operations, parameter choices and evidence limitations."""
        cohorts = []
        try:
            with self.connect() as db:
                cohorts = [
                    r["cohort"]
                    for r in db.execute(
                        "SELECT DISTINCT cohort FROM cohort_membership ORDER BY cohort"
                    )
                ]
        except (sqlite3.Error, OSError, DataUnavailable):
            pass
        return {
            "analyses": {key: value.model_dump() for key, value in DEFINITIONS.items()},
            "cohorts": cohorts,
            "credentials": [
                {"value": "B", "label": "Bachelor's degree"},
                {"value": "A", "label": "Associate degree"},
                {"value": "C", "label": "Certificate"},
            ],
            "programs": [
                {"value": key, "label": value["label"], "codes": sorted(value["codes"])}
                for key, value in PROGRAMS.items()
            ],
            "complete_academic_years": self.coverage.complete_academic_years,
            "cutoff": self.coverage.cutoff,
            "coverage_provenance": self.coverage.provenance,
            "graduation_major_evidence": "Exact award semesters are not present in the starter extract; completion-major results remain unknown.",
            "source": "synthetic",
        }

    def clarify(self, request: AnalysisRequest) -> Clarification | None:
        """Require every parameter that materially changes a numerical answer."""
        catalog = self.catalog()
        fields = []
        if request.analysis in ("graduation", "retention"):
            fields.append(
                (
                    "cohort",
                    "Which entry cohort?",
                    [{"value": c, "label": c} for c in catalog["cohorts"]],
                )
            )
        if request.analysis == "graduation":
            fields.extend(
                [
                    (
                        "credential",
                        "Which credential should completion mean?",
                        catalog["credentials"],
                    ),
                    ("program", "Which chemistry definition?", catalog["programs"]),
                ]
            )
        for field, message, choices in fields:
            if getattr(request, field) is None:
                return Clarification(
                    field=field,
                    message=message,
                    choices=[
                        {"value": c["value"], "label": c["label"]} for c in choices
                    ],
                    pending=request,
                )
        if (
            request.cohort is not None
            and catalog["cohorts"]
            and request.cohort not in catalog["cohorts"]
        ):
            raise ValueError("The selected cohort is not in the loaded extract")
        if request.program:
            resolve_program(request.program)
        return None

    def analyze(self, parameters: AnalysisRequest | dict) -> AnalysisResponse:
        """Return a clarification or fully projected deterministic receipts."""
        request = AnalysisRequest.model_validate(parameters)
        clarification = self.clarify(request)
        if clarification:
            return AnalysisResponse(clarification=clarification)
        definition = DEFINITIONS[request.analysis]
        receipt = AnalysisReceipt(
            analysis=request.analysis,
            parameters=request,
            definition=definition,
            rows=[],
            cutoff=self.coverage.cutoff,
            coverage_provenance=self.coverage.provenance,
            limitations=list(definition.limitations),
        )
        try:
            with self.connect() as db:
                loaded = db.execute(
                    "SELECT MAX(loaded_at) AS loaded_at FROM data_provider"
                ).fetchone()["loaded_at"]
                loaded = loaded.isoformat() if isinstance(loaded, (date, datetime)) else loaded
                receipt.loaded_at = loaded
                providers = [dict(row) for row in db.execute(
                    "SELECT provider_id, loaded_at, source_file, file_sha256 "
                    "FROM data_provider ORDER BY provider_id"
                )]
                providers = [
                    {key: value.isoformat() if isinstance(value, (date, datetime)) else value
                     for key, value in provider.items()} for provider in providers
                ]
                fingerprint = sha256(json.dumps(providers, sort_keys=True).encode()).hexdigest()
                receipt.source_stamp = f"{loaded}:{fingerprint}"
                if request.analysis == "enrollment":
                    receipt.academic_years = self.coverage.latest_two_years()
                    if not receipt.academic_years:
                        return self.unavailable(
                            receipt,
                            "Two complete academic years have not been certified in analytics.yaml.",
                        )
                    courses = self.enrollments(db, receipt.academic_years)
                    receipt.rows = enrollment.calculate(courses, receipt.academic_years)
                    if not receipt.rows:
                        return self.unavailable(
                            receipt,
                            "No actual course enrollments are available in the declared years.",
                        )
                else:
                    students = [
                        dict(r)
                        for r in db.execute(
                            (
                                "SELECT program_of_study_term_1, retention FROM cohort_membership WHERE cohort = ?"
                                if request.analysis == "retention"
                                else "SELECT * FROM cohort_membership WHERE cohort = ?"
                            ),
                            (request.cohort,),
                        )
                    ]
                    if not students:
                        return self.unavailable(
                            receipt, "No students are available for this entry cohort."
                        )
                    if request.analysis == "retention":
                        provisional = (
                            request.cohort
                            in self.coverage.provisional_retention_cohorts
                        )
                        receipt.rows = retention.calculate(students, provisional)
                    else:
                        for student in students:
                            student["graduation_program"] = None
                        receipt.program_definition = PROGRAMS[request.program]["label"]
                        receipt.rows = graduation.calculate(
                            students,
                            request.cohort,
                            request.credential,
                            resolve_program(request.program),
                            self.coverage,
                        )
                        receipt.limitations.append(
                            "The extract has no exact award semester. Inferred completion-program attribution is unknown."
                        )
                receipt.rows = suppress(
                    receipt.rows, self.coverage.suppression_threshold
                )
        except (sqlite3.Error, OSError, DataUnavailable):
            return self.unavailable(
                receipt,
                "Normalized data is missing or incompatible. Load cohort and course files into the configured database and check its schema.",
            )
        return AnalysisResponse(receipts=[receipt])

    @staticmethod
    def enrollments(db, years: list[str]) -> list[dict]:
        """Join on student and cohort so repeated cohorts cannot multiply rows."""
        return [
            dict(r)
            for r in db.execute(
                """
            SELECT e.student_id, e.course_id, e.term_program_of_study, s.ethnicity, t.academic_year
            FROM course_enrollment e
            JOIN cohort_membership m ON m.student_id=e.student_id AND m.cohort=e.cohort
            JOIN student s ON s.student_id=e.student_id
            JOIN term t ON t.term_id=e.term_id
            WHERE e.course_id IS NOT NULL AND t.academic_year IN (?, ?)
        """,
                tuple(years),
            )
        ]

    @staticmethod
    def unavailable(receipt: AnalysisReceipt, reason: str) -> AnalysisResponse:
        """Represent missing evidence without manufacturing a numerical result."""
        receipt.rows = [
            CalculationRow(
                label=receipt.definition.name,
                kind="count" if receipt.analysis == "enrollment" else "rate",
                status="unavailable",
                note=reason,
            )
        ]
        return AnalysisResponse(receipts=[receipt])
