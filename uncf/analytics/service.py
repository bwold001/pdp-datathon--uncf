"""Read-only normalized-data service supplying the same receipts to API and chat."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path

from uncf.analytics import enrollment, graduation, retention
from uncf.analytics.definitions import DEFINITIONS
from uncf.analytics.presentation import suppress
from uncf.analytics.schemas import (
    AnalysisReceipt,
    AnalysisRequest,
    AnalysisResponse,
    CalculationRow,
    Clarification,
)
from uncf.coverage import Coverage
from uncf.programs import PROGRAMS, resolve_program


class AnalyticsService:
    """Own deterministic analyses and serialize evidence only after suppression."""

    def __init__(self, database: Path, coverage: Coverage):
        """Use the normalized SQLite extract and explicit completeness declarations."""
        self.database = database
        self.coverage = coverage

    def connect(self):
        """Open an existing normalized database without creating or mutating it."""
        db = sqlite3.connect(f"{self.database.resolve().as_uri()}?mode=ro", uri=True)
        db.row_factory = sqlite3.Row
        return db

    def catalog(self) -> dict:
        """Advertise approved operations, parameter choices and evidence limitations."""
        cohorts = []
        try:
            with closing(self.connect()) as db:
                cohorts = [
                    r[0]
                    for r in db.execute(
                        "SELECT DISTINCT cohort FROM cohort_membership ORDER BY cohort"
                    )
                ]
        except sqlite3.Error:
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
            with closing(self.connect()) as db:
                loaded = db.execute(
                    "SELECT MAX(loaded_at) FROM data_provider"
                ).fetchone()[0]
                stamp = self.database.stat()
                receipt.loaded_at = loaded
                receipt.source_stamp = f"{loaded}:{stamp.st_mtime_ns}:{stamp.st_size}"
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
        except (sqlite3.Error, OSError):
            return self.unavailable(
                receipt,
                "Normalized data is missing or incompatible. Run python -m uncf load and check its schema.",
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
