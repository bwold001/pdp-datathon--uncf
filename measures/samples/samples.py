"""Shows a sample input and the output it gives.

Run it from the repo root:
    python measures/samples/samples.py                              made-up rows, no database needed
    python measures/samples/samples.py --input path/to/pdp.sqlite   real rows from a loaded database
    python measures/samples/samples.py --save                       also save the rows shown
                                                                            (made-up rows go to success_measures_sample.sqlite)

The database comes from the loader: cd normalized-data-model, then python -m src.loader.load
"""
import argparse
import sqlite3
import sys
from pathlib import Path

# Lets this file run directly and still find the measures package at the repo root.
sys.path.insert(0, str(Path(__file__).parents[2]))

from measures.models import (  # noqa: E402
    EVERYONE,
    Cohort,
    ExclusionReason,
    Group,
    GroupBy,
    GroupDimension,
    Measure,
    MeasureResult,
    Status,
)
from measures.run_measures import run_measure  # noqa: E402
from measures.save_results import RESULTS_DATABASE, SAMPLE_RESULTS_DATABASE, save_results  # noqa: E402

ENROLLMENT_TYPE = GroupDimension.ENROLLMENT_TYPE
PELL = GroupDimension.PELL
INTENSITY = GroupDimension.ENROLLMENT_INTENSITY
COURSE = GroupDimension.COURSE

# A run grouped by course returns a row for every course, so only this many rows are printed.
ROW_LIMIT = 15

NOTE = "SAMPLE ONLY. Students in the cohort who came back the next year."


GATEWAY_MATH_NOTE = "SAMPLE ONLY. Students required to take gateway math who completed it in their first academic year."
GATEWAY_ENGLISH_NOTE = "SAMPLE ONLY. Students required to take gateway English who completed it in their first academic year."
DFW_NOTE = "SAMPLE ONLY. Course enrollments of the cohort's students that ended in a D, F or withdrawal, out of those with a final grade."
CREDIT_NOTE = "SAMPLE ONLY. Average of each student's year 1 credits earned / credits attempted, for first-time and transfer-in students."


def sample_row(
    cohort: Cohort,
    group: Group,
    numerator,
    denominator,
    metric_rate,
    measure: Measure = Measure.RETENTION,
    note: str = NOTE,
    n_excluded: int = 0,
    n_out_of_scope: int = 0,
    reason: ExclusionReason = ExclusionReason.UNKNOWN_REQUIREMENT_OR_OUTCOME,
    exclusions: dict[ExclusionReason, int] | None = None,
) -> MeasureResult:
    """A shown row, or a hidden one when the counts are None."""
    hidden = denominator is None
    return MeasureResult(
        measure=measure,
        cohort=cohort,
        group=group,
        numerator=numerator,
        denominator=denominator,
        metric_rate=metric_rate,
        status=Status.SUPPRESSED if hidden else Status.OK,
        n_excluded=None if hidden else n_excluded,
        n_out_of_scope=None if hidden else n_out_of_scope,
        exclusion_reason=None if hidden or not n_excluded else reason,
        note=note,
        exclusions={} if hidden or not n_excluded else (exclusions or {reason: n_excluded}),
    )


# Sample 1: one cohort. A GroupBy with several dimensions asks for their combinations.
COHORT_2022_23 = Cohort.of("2022-23")
COHORT_2023_24 = Cohort.of("2023-24")

SAMPLE_INPUT = dict(
    measure=Measure.RETENTION,
    cohorts=[COHORT_2022_23],
    group_by=[GroupBy.of(ENROLLMENT_TYPE), GroupBy.of(PELL, INTENSITY)],
)

# Made-up output: everyone, each enrollment type, then each Pell x intensity pair.
# Re-admit has eight students; its count and rate remain visible.
SAMPLE_OUTPUT = [
    sample_row(COHORT_2022_23, EVERYONE, 610, 1000, 0.61),
    sample_row(COHORT_2022_23, Group.of((ENROLLMENT_TYPE, "First-time")), 380, 600, 0.6333),
    sample_row(COHORT_2022_23, Group.of((ENROLLMENT_TYPE, "Re-admit")), 5, 8, 0.625),
    sample_row(COHORT_2022_23, Group.of((ENROLLMENT_TYPE, "Transfer-in")), 225, 392, 0.574),
    sample_row(COHORT_2022_23, Group.of((PELL, "N"), (INTENSITY, "Full-time")), 190, 250, 0.76),
    sample_row(COHORT_2022_23, Group.of((PELL, "N"), (INTENSITY, "Part-time")), 150, 250, 0.6),
    sample_row(COHORT_2022_23, Group.of((PELL, "Y"), (INTENSITY, "Full-time")), 100, 150, 0.6667),
    sample_row(COHORT_2022_23, Group.of((PELL, "Y"), (INTENSITY, "Part-time")), 170, 350, 0.4857),
]

# Sample 2: two cohorts counted together. A Cohort with several years is pooled.
POOLED_COHORT = Cohort.of("2021-22", "2022-23")

POOLED_INPUT = dict(
    measure=Measure.RETENTION,
    cohorts=[POOLED_COHORT],
    group_by=[GroupBy.of(ENROLLMENT_TYPE)],
)

# Made-up output. Both small Re-admit cohorts are visible individually.
# Together they have 14 students: 3 + 5 = 8 came back.
POOLED_OUTPUT = [
    sample_row(POOLED_COHORT, EVERYONE, 1163, 1950, 0.5964),
    sample_row(POOLED_COHORT, Group.of((ENROLLMENT_TYPE, "First-time")), 730, 1170, 0.6239),
    sample_row(POOLED_COHORT, Group.of((ENROLLMENT_TYPE, "Re-admit")), 8, 14, 0.5714),
    sample_row(POOLED_COHORT, Group.of((ENROLLMENT_TYPE, "Transfer-in")), 425, 766, 0.5548),
]

# Samples 3 and 4: gateway completion, for math and for English. Same call, a different measure.
GATEWAY_MATH_INPUT = dict(
    measure=Measure.GATEWAY_MATH,
    cohorts=[COHORT_2022_23],
    group_by=[GroupBy.of(PELL)],
)

# Made-up output: everyone, then pell = N and pell = Y.
GATEWAY_MATH_OUTPUT = [
    sample_row(COHORT_2022_23, EVERYONE, 300, 1000, 0.3, Measure.GATEWAY_MATH, GATEWAY_MATH_NOTE, 120, 450),
    sample_row(COHORT_2022_23, Group.of((PELL, "N")), 210, 600, 0.35, Measure.GATEWAY_MATH, GATEWAY_MATH_NOTE, 70, 270),
    sample_row(COHORT_2022_23, Group.of((PELL, "Y")), 90, 400, 0.225, Measure.GATEWAY_MATH, GATEWAY_MATH_NOTE, 50, 180),
]

GATEWAY_ENGLISH_INPUT = dict(
    measure=Measure.GATEWAY_ENGLISH,
    cohorts=[COHORT_2022_23],
    group_by=[GroupBy.of(PELL)],
)

GATEWAY_ENGLISH_OUTPUT = [
    sample_row(COHORT_2022_23, EVERYONE, 520, 1100, 0.4727, Measure.GATEWAY_ENGLISH, GATEWAY_ENGLISH_NOTE, 90, 400),
    sample_row(COHORT_2022_23, Group.of((PELL, "N")), 300, 600, 0.5, Measure.GATEWAY_ENGLISH, GATEWAY_ENGLISH_NOTE, 50, 220),
    sample_row(COHORT_2022_23, Group.of((PELL, "Y")), 220, 500, 0.44, Measure.GATEWAY_ENGLISH, GATEWAY_ENGLISH_NOTE, 40, 180),
]

# Sample 5: DFW rate. The counts are course enrollments, not students.
DFW_INPUT = dict(
    measure=Measure.DFW_RATE,
    cohorts=[COHORT_2022_23],
    group_by=[GroupBy.of(PELL)],
)

# Made-up output: everyone, then pell = N and pell = Y. n_excluded is enrollments with no final grade.
DFW_OUTPUT = [
    sample_row(
        COHORT_2022_23, EVERYONE, 5200, 21000, 0.2476, Measure.DFW_RATE, DFW_NOTE, 1300, 0, ExclusionReason.OTHER_GRADE,
        {ExclusionReason.OTHER_GRADE: 800, ExclusionReason.UNKNOWN_GRADE: 380, ExclusionReason.INCOMPLETE: 90, ExclusionReason.AUDIT: 30},
    ),
    sample_row(
        COHORT_2022_23, Group.of((PELL, "N")), 2400, 11000, 0.2182, Measure.DFW_RATE, DFW_NOTE, 800, 0, ExclusionReason.OTHER_GRADE,
        {ExclusionReason.OTHER_GRADE: 480, ExclusionReason.UNKNOWN_GRADE: 230, ExclusionReason.INCOMPLETE: 60, ExclusionReason.AUDIT: 30},
    ),
    sample_row(
        COHORT_2022_23, Group.of((PELL, "Y")), 2800, 10000, 0.28, Measure.DFW_RATE, DFW_NOTE, 500, 0, ExclusionReason.OTHER_GRADE,
        {ExclusionReason.OTHER_GRADE: 320, ExclusionReason.UNKNOWN_GRADE: 150, ExclusionReason.INCOMPLETE: 30},
    ),
]

# Sample 6: DFW rate by course. The courses come from the data, so a real run returns a row for every course.
DFW_COURSE_INPUT = dict(
    measure=Measure.DFW_RATE,
    cohorts=[COHORT_2023_24],
    group_by=[GroupBy.of(COURSE)],
)

# Made-up output: everyone, then three courses, including a three-enrollment course.
DFW_COURSE_OUTPUT = [
    sample_row(COHORT_2023_24, EVERYONE, 5200, 21000, 0.2476, Measure.DFW_RATE, DFW_NOTE, 1300, 0, ExclusionReason.OTHER_GRADE),
    sample_row(COHORT_2023_24, Group.of((COURSE, "ENGL 1302")), 900, 3000, 0.3, Measure.DFW_RATE, DFW_NOTE, 120, 0, ExclusionReason.OTHER_GRADE),
    sample_row(COHORT_2023_24, Group.of((COURSE, "MATH 1314")), 700, 1500, 0.4667, Measure.DFW_RATE, DFW_NOTE, 60, 0, ExclusionReason.OTHER_GRADE),
    sample_row(COHORT_2023_24, Group.of((COURSE, "BIOL 1101")), 1, 3, 0.3333, Measure.DFW_RATE, DFW_NOTE),
]


# Sample 7: credit completion. The numerator adds up each student's own ratio, so it can have decimals.
CREDIT_INPUT = dict(
    measure=Measure.CREDIT_COMPLETION,
    cohorts=[COHORT_2022_23],
    group_by=[GroupBy.of(PELL)],
)

# Made-up output: everyone, then pell = N and pell = Y. n_excluded is students with no credits recorded,
# none attempted, or an unknown full- or part-time status. n_out_of_scope is re-admit and continuing students.
CREDIT_OUTPUT = [
    sample_row(
        COHORT_2022_23, EVERYONE, 712.5, 1000, 0.7125, Measure.CREDIT_COMPLETION, CREDIT_NOTE, 60, 40, ExclusionReason.UNKNOWN_OUTCOME,
        {ExclusionReason.UNKNOWN_OUTCOME: 30, ExclusionReason.NO_CREDITS_ATTEMPTED: 20, ExclusionReason.UNKNOWN_ATTENDANCE_TYPE: 10},
    ),
    sample_row(
        COHORT_2022_23, Group.of((PELL, "N")), 468.5, 600, 0.7808, Measure.CREDIT_COMPLETION, CREDIT_NOTE, 35, 25, ExclusionReason.UNKNOWN_OUTCOME,
        {ExclusionReason.UNKNOWN_OUTCOME: 20, ExclusionReason.NO_CREDITS_ATTEMPTED: 10, ExclusionReason.UNKNOWN_ATTENDANCE_TYPE: 5},
    ),
    sample_row(
        COHORT_2022_23, Group.of((PELL, "Y")), 244, 400, 0.61, Measure.CREDIT_COMPLETION, CREDIT_NOTE, 25, 15, ExclusionReason.UNKNOWN_OUTCOME,
        {ExclusionReason.UNKNOWN_OUTCOME: 10, ExclusionReason.NO_CREDITS_ATTEMPTED: 10, ExclusionReason.UNKNOWN_ATTENDANCE_TYPE: 5},
    ),
]


def cohort_code(cohort: Cohort) -> str:
    """Write a Cohort the way a consumer would type it."""
    years = ", ".join(f'"{year}"' for year in sorted(cohort.years))
    return f"Cohort.of({years})"


def group_by_code(group_by: GroupBy) -> str:
    """Write a GroupBy the way a consumer would type it."""
    names = ", ".join(f"GroupDimension.{d.name}" for d in sorted(group_by.dimensions, key=lambda d: d.name))
    return f"GroupBy.of({names})"


def show_input(sample: dict, title: str, save: bool, database: Path | None) -> None:
    """Print the call a consumer makes."""
    print(title)
    print("  INPUT: what you pass to run_measure")
    print("    run_measure(")
    print(f"        measure=Measure.{sample['measure'].name},")
    print(f"        cohorts=[{', '.join(cohort_code(c) for c in sample['cohorts'])}],")
    print(f"        group_by=[{', '.join(group_by_code(g) for g in sample['group_by'])}],")
    if database:
        print(f'        database="{database.as_posix()}",')
    if save:
        print("        save=True,")
    print("    )")


def show_output(rows: list[MeasureResult]) -> None:
    """Print the rows you get back, one per cohort and group."""
    if len(rows) > ROW_LIMIT:
        # Most of a by-course run is hidden, so show the rows with numbers first, busiest first.
        rows = sorted(rows, key=lambda r: (r.status != Status.OK, -(r.denominator or 0)))
    print("  OUTPUT: one MeasureResult per cohort and group")
    print(f"    {'cohort':<20} {'group':<45} {'numerator':>9} {'denominator':>11} {'metric_rate':>11}  {'excluded':>8} {'out_of_scope':>12}  status")
    for r in rows[:ROW_LIMIT]:
        numerator = "-" if r.numerator is None else r.numerator
        denominator = "-" if r.denominator is None else r.denominator
        metric_rate = "-" if r.metric_rate is None else f"{r.metric_rate:.4f}"
        excluded = "-" if r.n_excluded is None else r.n_excluded
        out_of_scope = "-" if r.n_out_of_scope is None else r.n_out_of_scope
        print(
            f"    {r.cohort.label:<20} {r.group.label:<45} {numerator:>9} {denominator:>11} {metric_rate:>11}  "
            f"{excluded:>8} {out_of_scope:>12}  {r.status.value}"
        )
    if len(rows) > ROW_LIMIT:
        print(f"    ... and {len(rows) - ROW_LIMIT} more rows")
    print(f"    note: {rows[0].note}")
    for r in rows[:ROW_LIMIT]:
        if len(r.exclusions) > 1:
            reasons = ", ".join(f"{reason.value} {n}" for reason, n in sorted(r.exclusions.items(), key=lambda item: -item[1]))
            print(f"    left out, {r.group.label}: {reasons}")


def show_saved(measures: list[Measure], database: Path) -> None:
    """Print what a results database holds for these measures."""
    names = ", ".join(sorted({f"'{m.value}'" for m in measures}))
    connection = sqlite3.connect(database)
    rows = connection.execute(
        "SELECT measure, cohort, group_dimensions, group_values, numerator, denominator, metric_rate, status, data_loaded_at "
        f"FROM success_measures WHERE measure IN ({names}) ORDER BY measure, cohort, group_dimensions, group_values"
    ).fetchall()
    connection.close()
    print(f"SAVED: {len(rows)} rows for {names} in {database}")
    print(f"  {'measure':<12} {'cohort':<18} {'dimensions':<28} {'values':<22} {'num':>6} {'den':>6} {'metric_rate':>11} status      data loaded")
    for measure, cohort, dimensions, values, numerator, denominator, metric_rate, status, loaded_at in rows:
        numerator = "-" if numerator is None else numerator
        denominator = "-" if denominator is None else denominator
        metric_rate = "-" if metric_rate is None else metric_rate
        print(
            f"  {measure:<12} {cohort:<18} {dimensions:<28} {values:<22} {numerator:>6} "
            f"{denominator:>6} {metric_rate:>11} {status:<10}  {loaded_at}"
        )


def main() -> None:
    """Print the samples: made up by default, real when --input is given. Save them if asked."""
    parser = argparse.ArgumentParser(description="Show a sample input and the output it gives.")
    parser.add_argument("--input", type=Path, help="a loaded pdp.sqlite to run on. Without it, made-up rows are shown")
    parser.add_argument("--save", action="store_true", help="also save the rows shown to the results database")
    args = parser.parse_args()

    if args.input and not args.input.exists():
        sys.exit(f"{args.input} not found. Load the data first: cd normalized-data-model, then python -m src.loader.load")

    samples = (
        (SAMPLE_INPUT, SAMPLE_OUTPUT, "Sample 1: one cohort"),
        (POOLED_INPUT, POOLED_OUTPUT, "Sample 2: pooled cohorts (a Cohort with several years counts them together)"),
        (GATEWAY_MATH_INPUT, GATEWAY_MATH_OUTPUT, "Sample 3: gateway math, by Pell status"),
        (GATEWAY_ENGLISH_INPUT, GATEWAY_ENGLISH_OUTPUT, "Sample 4: gateway English, by Pell status"),
        (DFW_INPUT, DFW_OUTPUT, "Sample 5: DFW rate, by Pell status (counts are course enrollments)"),
        (DFW_COURSE_INPUT, DFW_COURSE_OUTPUT, "Sample 6: DFW rate, by course"),
        (CREDIT_INPUT, CREDIT_OUTPUT, "Sample 7: credit completion, by Pell status (the numerator adds up student ratios)"),
    )
    if args.input:
        print(f"INPUT SOURCE: {args.input.as_posix()}")
    else:
        print("INPUT SOURCE: made-up rows typed in samples.py (no database is read)")
    print()
    for sample, made_up_output, title in samples:
        show_input(sample, title, args.save, args.input)
        print()
        if args.input:
            rows = run_measure(**sample, database=args.input, save=args.save)
        else:
            rows = made_up_output
            if args.save:
                save_results(rows, "made-up sample", SAMPLE_RESULTS_DATABASE)
        show_output(rows)
        print()

    if args.input:
        print("Every nonempty group is shown; missing evidence has no rate, never a fabricated zero.")
        print("The data is mock, so the numbers mean nothing.")
    else:
        print("These rows are made up. Add --input path/to/pdp.sqlite to run on a loaded database.")
    if args.save:
        print()
        saved_to = RESULTS_DATABASE if args.input else SAMPLE_RESULTS_DATABASE
        show_saved([sample["measure"] for sample, _, _ in samples], saved_to)


if __name__ == "__main__":
    main()
