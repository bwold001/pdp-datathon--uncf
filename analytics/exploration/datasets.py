"""Build one private unit per student/cohort before any aggregate leaves analytics."""

from dataclasses import dataclass
from math import isfinite

from analytics.execution import checked
from analytics.exploration.catalog import COVERAGE, DATASET_VERSION, MISSINGNESS_VERSION
from measures.breakdowns.common import select_students
from measures.models import Measure
from measures.requests import Scope, filter_group
from measures.run_measures import read_answers

MAX_SOURCE_ROWS = 500_000


class ExplorationRefusal(ValueError):
    """Identify a safe refusal that leaves a borrowed snapshot usable."""

    def __init__(self, code):
        """Carry a fixed public validation code without source details."""
        self.code = code
        super().__init__(code)


@dataclass(frozen=True, repr=False)
class StudentYear1:
    """Keep private keys and independent feature eligibility inside the executor."""

    student_id: str
    cohort: str
    credits_earned_y1: float | None
    credits_attempted_y1: float | None
    online_enrollment_count_y1: int | None
    online_enrollment_share_y1: float | None
    retained_school: int | None
    retained_federal: int | None
    retained_school_reason: str | None
    retained_federal_reason: str | None
    online_reasons: tuple[str, ...]


@dataclass(frozen=True, repr=False)
class Dataset:
    """Contain internal rows and safe aggregate metadata without a serialization method."""

    rows: tuple[StudentYear1, ...]
    source_rows: int
    version: str = DATASET_VERSION
    missingness_version: str = MISSINGNESS_VERSION
    coverage: str = COVERAGE


def credit(value):
    """Accept finite nonnegative normalized credits and preserve missing evidence."""
    if value is None:
        return None
    number = float(value)
    if not isfinite(number) or number < 0:
        raise ExplorationRefusal("data_unavailable")
    return number


def build(snapshot, cohort, filters):
    """Preaggregate actual enrollments by both keys and reuse dashboard filters/outcomes."""
    scope = Scope(cohort=cohort, filters=filters)
    cohort, filters = scope.cohort, scope.filters
    connection = snapshot.named
    # Equal duplicates are harmless; conflicting cohort values cannot be chosen arbitrarily.
    records = connection.execute(
        "SELECT DISTINCT *, number_of_credits_earned_yr_1 AS earned, "
        "number_of_credits_attempted_yr_1 AS attempted "
        f"FROM cohort_membership WHERE cohort = '{cohort}'"
    ).fetchall()
    credits = {}
    for row in checked(records):
        key = row["student_id"]
        if key in credits:
            raise ExplorationRefusal("data_unavailable")
        if row["retention"] not in (None, 0, 1):
            raise ExplorationRefusal("data_unavailable")
        credits[key] = credit(row["earned"]), credit(row["attempted"])
    selected = select_students(connection, cohort, filter_group(filters))
    source_rows = connection.execute(
        f"SELECT COUNT(*) AS n FROM course_enrollment WHERE cohort = '{cohort}'"
    ).fetchone()["n"]
    if source_rows > MAX_SOURCE_ROWS:
        raise ExplorationRefusal("limit_exceeded")
    exposure = connection.execute(f"""
        SELECT ce.student_id, ce.cohort,
          SUM(CASE WHEN t.academic_year = ce.cohort THEN 1 ELSE 0 END) AS observed,
          SUM(CASE WHEN t.academic_year = ce.cohort AND UPPER(TRIM(ce.delivery_method)) = 'O' THEN 1 ELSE 0 END) AS online,
          SUM(CASE WHEN t.academic_year IS NULL OR t.academic_year = '' OR UPPER(TRIM(t.academic_year)) IN ('UNKNOWN', 'UK') OR LENGTH(t.academic_year) <> 7 OR SUBSTR(t.academic_year, 5, 1) <> '-' OR t.academic_term IS NULL
            OR UPPER(TRIM(t.academic_term)) NOT IN ('FALL','WINTER','SPRING','SUMMER') THEN 1 ELSE 0 END) AS unresolved,
          SUM(CASE WHEN t.academic_year = ce.cohort AND (ce.delivery_method IS NULL
            OR UPPER(TRIM(ce.delivery_method)) NOT IN ('O','F','H')) THEN 1 ELSE 0 END) AS unknown_delivery
        FROM course_enrollment ce LEFT JOIN term t ON t.term_id = ce.term_id
        WHERE ce.cohort = '{cohort}' AND ce.course_id IS NOT NULL
        GROUP BY ce.student_id, ce.cohort
    """).fetchall()
    exposures = {r["student_id"]: r for r in exposure}
    school, _ = read_answers(Measure.RETENTION, cohort, snapshot.positional)
    federal, observable = read_answers(Measure.FEDERAL_RETENTION, cohort, snapshot.positional)
    rows = []
    for sid in checked(selected):
        record = exposures.get(sid)
        reasons = []
        if record is None or not record["observed"]:
            reasons.append("no_year1_records")
        if record is not None and record["unresolved"]:
            reasons.append("unresolved_term")
        if record is not None and record["unknown_delivery"]:
            reasons.append("unknown_delivery")
        online = None if reasons else int(record["online"])
        share = None if reasons else online / record["observed"]
        earned, attempted = credits[sid]
        rows.append(StudentYear1(sid, cohort, earned, attempted, online, share,
            school.get(sid), federal.get(sid),
            "unknown" if school.get(sid) is None else None,
            ("not_yet_observable" if not observable else "unknown") if federal.get(sid) is None else None,
            tuple(reasons)))
    return Dataset(tuple(rows), source_rows)
