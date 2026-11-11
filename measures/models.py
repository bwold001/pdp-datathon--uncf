"""One row of a measure result: the contract every success measure follows.

It refuses rows that break the rules, so a bad result fails when it is built.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

SUPPRESSION_THRESHOLD = 10  # groups with fewer students are hidden
UNKNOWN = "UNKNOWN"  # how the data model stores a value nobody knows


class Measure(str, Enum):
    """The success measures."""

    RETENTION = "retention"
    FEDERAL_RETENTION = "federal_retention"  # fall to fall: took a course here the fall after year 1
    PERSISTENCE = "persistence"
    GATEWAY_MATH = "gateway_math"
    GATEWAY_ENGLISH = "gateway_english"
    DFW_RATE = "dfw_rate"
    CREDIT_COMPLETION = "credit_completion"


class Status(str, Enum):
    """Whether a row's numbers are shown, and if not, why."""

    OK = "ok"
    SUPPRESSED = "suppressed"  # too few students, so the group is hidden
    NOT_YET_OBSERVABLE = "not_yet_observable"  # nobody in the cohort has an answer yet


class ExclusionReason(str, Enum):
    """Why students were left out of a group's counts."""

    UNKNOWN_OUTCOME = "unknown_outcome"  # the student has no answer for the measure
    UNKNOWN_REQUIREMENT_OR_OUTCOME = "unknown_requirement_or_outcome"  # gateway: the requirement or the outcome is unknown
    INCOMPLETE = "incomplete"  # DFW: the grade is incomplete, so there is no final grade yet
    AUDIT = "audit"  # DFW: the student audited the course
    MISSING_GRADE = "missing_grade"  # DFW: the grade is marked missing
    OTHER_GRADE = "other_grade"  # DFW: the grade is marked other
    UNKNOWN_GRADE = "unknown_grade"  # DFW: nobody knows the grade
    UNLISTED_GRADE = "unlisted_grade"  # DFW: a grade code the dictionary doesn't list, or no grade
    NO_CREDITS_ATTEMPTED = "no_credits_attempted"  # credit completion: the student attempted no credits in year 1
    UNKNOWN_ENROLLMENT_TYPE = "unknown_enrollment_type"  # credit completion: first-time, transfer-in or other is unknown
    UNKNOWN_ATTENDANCE_TYPE = "unknown_attendance_type"  # credit completion: full- or part-time is unknown


class GroupDimension(str, Enum):
    """A way to split students into groups."""

    RACE = "race"
    ETHNICITY = "ethnicity"
    GENDER = "gender"
    FIRST_GEN = "first_gen"
    PELL = "pell"
    AGE_BAND = "age_band"
    ENROLLMENT_TYPE = "enrollment_type"
    ENROLLMENT_INTENSITY = "enrollment_intensity"
    COHORT_TERM = "cohort_term"
    COURSE = "course"  # DFW only: the values are the courses in the data
    TERM = "term"  # DFW only: the season the course was taken (Fall, Winter, Spring, Summer)
    DELIVERY = "delivery"  # DFW only: how the course was taught, as the course file codes it (F, H, O or UNKNOWN)


# The values each dimension can take: the PDP dictionary's values, plus UNKNOWN for anything blank or not listed.
ALLOWED_VALUES: dict[GroupDimension, frozenset[str]] = {
    GroupDimension.RACE: frozenset({
        "White",
        "Hispanic",
        "American Indian or Alaska Native",
        "Native Hawaiian or Other Pacific Islander",
        "Two or More Races",
        "Black or African American",
        "Nonresident alien",
        "Asian",
        UNKNOWN,
    }),
    GroupDimension.ETHNICITY: frozenset({"H", "N", UNKNOWN}),
    GroupDimension.GENDER: frozenset({"M", "F", "P", "X", UNKNOWN}),
    GroupDimension.FIRST_GEN: frozenset({"N", "P", "C", "A", "B", "E", UNKNOWN}),
    GroupDimension.PELL: frozenset({"Y", "N", UNKNOWN}),
    GroupDimension.AGE_BAND: frozenset({"20 and younger", "> 20-24", "Older than 24", UNKNOWN}),
    GroupDimension.ENROLLMENT_TYPE: frozenset({"First-time", "Re-admit", "Transfer-in", UNKNOWN}),
    GroupDimension.ENROLLMENT_INTENSITY: frozenset({"Full-time", "Part-time", UNKNOWN}),
    GroupDimension.COHORT_TERM: frozenset({"Fall", "Winter", "Spring", "Summer", UNKNOWN}),
}

# Dimensions with no fixed list of values: the data says which values exist. A measure lists the ones it supports.
OPEN_DIMENSIONS = frozenset({GroupDimension.COURSE, GroupDimension.TERM, GroupDimension.DELIVERY})


@dataclass(frozen=True)
class GroupPart:
    """One condition on students, e.g. pell = Y."""

    dimension: GroupDimension
    value: str

    def __post_init__(self) -> None:
        # Refuse a value the dimension doesn't have, e.g. pell = Maybe. An open dimension takes any text.
        if self.dimension in OPEN_DIMENSIONS:
            if not self.value.strip():
                raise ValueError(f"a {self.dimension.value} needs a name")
        elif self.value not in ALLOWED_VALUES[self.dimension]:
            raise ValueError(f"{self.value!r} is not a value of {self.dimension.value}")


@dataclass(frozen=True)
class Group:
    """Which students a row is about: all conditions at once. No conditions means everyone."""

    parts: frozenset[GroupPart] = frozenset()

    def __post_init__(self) -> None:
        # A group can't name the same dimension twice, e.g. pell = Y and pell = N.
        dimensions = [part.dimension for part in self.parts]
        if len(dimensions) != len(set(dimensions)):
            raise ValueError("a group can use each dimension only once")

    @classmethod
    def of(cls, *conditions: tuple[GroupDimension, str]) -> Group:
        """Build a group from (dimension, value) pairs, e.g. Group.of((PELL, "Y"), (GENDER, "F"))."""
        return cls(frozenset(GroupPart(dimension, value) for dimension, value in conditions))

    @property
    def label(self) -> str:
        """Readable name, e.g. 'gender=F, pell=Y', or 'everyone'."""
        if not self.parts:
            return "everyone"
        return ", ".join(sorted(f"{p.dimension.value}={p.value}" for p in self.parts))


EVERYONE = Group()


@dataclass(frozen=True)
class GroupBy:
    """A request to split students by one dimension, or by a combination, e.g. pell and gender."""

    dimensions: frozenset[GroupDimension]

    def __post_init__(self) -> None:
        if not self.dimensions:
            raise ValueError("group by needs at least one dimension")

    @classmethod
    def of(cls, *dimensions: GroupDimension) -> GroupBy:
        """Build from dimensions, e.g. GroupBy.of(PELL, GENDER). Each can be used only once."""
        if len(dimensions) != len(set(dimensions)):
            raise ValueError("group by can use each dimension only once")
        return cls(frozenset(dimensions))


@dataclass(frozen=True)
class Cohort:
    """One cohort year, or several counted together (pooled)."""

    years: frozenset[str]

    def __post_init__(self) -> None:
        if not self.years:
            raise ValueError("a cohort needs at least one year")

    @classmethod
    def of(cls, *years: str) -> Cohort:
        """Build from cohort years, e.g. Cohort.of("2021-22", "2022-23"). Each can be used only once."""
        if len(years) != len(set(years)):
            raise ValueError("a cohort can't repeat a year")
        return cls(frozenset(years))

    @property
    def label(self) -> str:
        """Readable name, oldest first, e.g. '2022-23' or '2021-22 + 2022-23'."""
        return " + ".join(sorted(self.years))


@dataclass(frozen=True)
class MeasureResult:
    """One result row: a measure for one cohort (or pooled cohorts) and one group."""

    measure: Measure
    cohort: Cohort
    group: Group
    numerator: int | float | None
    denominator: int | float | None
    metric_rate: float | None
    status: Status
    n_excluded: int | None  # students the measure applies to but couldn't count
    n_out_of_scope: int | None  # students the measure doesn't apply to, such as not required to take a gateway course
    exclusion_reason: ExclusionReason | None  # the reason with the most students (or enrollments) left out
    note: str
    exclusions: dict[ExclusionReason, int] = field(default_factory=dict)  # students (or enrollments, for DFW) left out, by reason
    split: dict[str, int] | None = None  # DFW only: how many of the numerator were a D+, D, D-, F and W
    n_students: int | None = None  # distinct students counted (for DFW, a student with several grades counts once)

    @property
    def suppressed(self) -> bool:
        """True whenever the status isn't ok: the numbers are hidden."""
        return self.status != Status.OK

    def __post_init__(self) -> None:
        # Counts can't be negative. A hidden row is all blank, a shown row has all three numbers.
        if self.numerator is not None and self.numerator < 0:
            raise ValueError("numerator cannot be negative")
        if self.denominator is not None and self.denominator <= 0:
            raise ValueError("denominator must be above 0")
        if self.metric_rate is not None and self.metric_rate < 0:
            raise ValueError("metric_rate cannot be negative")
        if self.n_excluded is not None and self.n_excluded < 0:
            raise ValueError("n_excluded cannot be negative")
        if self.n_out_of_scope is not None and self.n_out_of_scope < 0:
            raise ValueError("n_out_of_scope cannot be negative")

        if any(n <= 0 for n in self.exclusions.values()):
            raise ValueError("each exclusion count must be above 0")

        counts = [self.numerator, self.denominator, self.metric_rate]
        if self.suppressed:
            if any(v is not None for v in counts + [self.n_excluded, self.n_out_of_scope, self.n_students]) or self.exclusions or self.split:
                raise ValueError("a hidden group must have blank counts, metric_rate, n_excluded, n_out_of_scope, exclusions and split")
        elif any(v is None for v in counts):
            raise ValueError("a shown group needs numerator, denominator and metric_rate")
        else:
            # Credit completion adds up each student's ratio (at most 1), so the numerator still can't pass the denominator.
            if self.numerator > self.denominator:
                raise ValueError("numerator cannot be above the denominator")
            if self.split is not None and sum(self.split.values()) != self.numerator:
                raise ValueError("D + F + W must add up to the numerator")
            if self.metric_rate != round(self.numerator / self.denominator, 4):
                raise ValueError("metric_rate must be numerator / denominator, rounded to 4 places")
            if sum(self.exclusions.values()) != self.n_excluded:
                raise ValueError("the exclusions must add up to n_excluded")


@dataclass(frozen=True)
class Counts:
    """What a measure's calculation hands back for one cohort and group, before hiding and rounding."""

    numerator: int | float
    denominator: int | float
    n_students: int  # distinct students counted; groups under the threshold are hidden
    n_excluded: int = 0
    n_out_of_scope: int = 0
    exclusion_reason: ExclusionReason | None = None  # the reason with the most students (or enrollments) left out
    not_yet_observable: bool = False  # a year in the cohort has no answers yet
    exclusions: dict[ExclusionReason, int] = field(default_factory=dict)  # students (or enrollments, for DFW) left out, by reason
    split: dict[str, int] | None = None  # DFW only: the numerator as D+, D, D-, F and W counts


def check_unique(results: list[MeasureResult]) -> None:
    """One row per measure, cohort and group."""
    seen = set()
    for r in results:
        key = (r.measure, r.cohort, r.group)
        if key in seen:
            raise ValueError(f"duplicate row for {key}")
        seen.add(key)
