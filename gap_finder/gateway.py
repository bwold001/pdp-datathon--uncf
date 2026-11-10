"""The Gateway page's comparisons, on top of the counts measures/breakdowns/gateway_courses.py returns.

measures is the bottom layer and the gap finder builds on it, so the breakdown only counts and this module compares
with compare() below; api/ only calls it:
- each course: the filtered students' first-try pass rate against everyone else who took it;
- each course pair: its retention against everyone else in the filtered cohort, the three furthest behind kept.
"""
from __future__ import annotations

from measures.models import SUPPRESSION_THRESHOLD

from .compare import CountRow, compare

TOP_PAIRS = 3


def count_row(measure: str, cohort: str, value: str | None, numerator: int, denominator: int) -> CountRow:
    """A gap finder input row: everyone when value is None, else one group named value."""
    dimensions, values = ((), ()) if value is None else (("group",), (value,))
    status = "ok" if denominator >= SUPPRESSION_THRESHOLD else "suppressed"
    return CountRow(measure, cohort, dimensions, values, numerator, denominator, status, 0, 0, None, f"Gateway page: {measure}.", "gateway page")


def course_gap(cohort: str, course: dict) -> dict:
    """The filtered students' first-try pass rate against everyone else who took the course."""
    everyone = course["all_takers"]
    rows = [
        count_row("gateway_first_try", cohort, None, everyone["first_pass"], everyone["students"]),
        count_row("gateway_first_try", cohort, "selected", course["first_pass"], course["students"]),
    ]
    (gap,) = [g for g in compare(rows) if g.group_values]
    if gap.status.value != "ok":
        return {"status": "hidden", "rate": None, "others_rate": None, "gap": None, "likely_noise": None}
    return {"status": "ok", "rate": gap.metric_rate, "others_rate": gap.comparison_rate, "gap": gap.gap_pts, "likely_noise": gap.likely_noise}


def pair_gaps(cohort: str, cohort_retention: dict, pair_counts: list[dict]) -> list[dict]:
    """The course pairs furthest behind everyone else on retention, by how many students the gap is worth."""
    if not pair_counts or cohort_retention["students"] is None:
        return []
    rows = [count_row("gateway_pair_retention", cohort, None, cohort_retention["retained"], cohort_retention["students"])]
    rows += [count_row("gateway_pair_retention", cohort, " + ".join(p["courses"]), p["retained"], p["students"]) for p in pair_counts]
    behind = [g for g in compare(rows) if g.group_values and g.status.value == "ok" and g.gap_pts < 0]
    behind.sort(key=lambda g: g.rank_by_affected)
    return [
        {
            "courses": g.group_values[0].split(" + "),
            "students": g.denominator,
            "retained": g.numerator,
            "rate": g.metric_rate,
            "others_rate": g.comparison_rate,
            "gap": g.gap_pts,
            "affected": g.students_affected,
            "likely_noise": g.likely_noise,
        }
        for g in behind[:TOP_PAIRS]
    ]


def add_gateway_gaps(body: dict) -> dict:
    """The breakdown's answer with each course's group gap and the riskiest pairs in place of the raw counts."""
    cohort = body["context"]["year_one"]
    courses = []
    for course in body["courses"]:
        takers = course.pop("all_takers")
        course["group"] = course_gap(cohort, {**course, "all_takers": takers}) if takers else None
        courses.append(course)
    pair_counts = body.pop("pair_counts")
    body["pairs"] = pair_gaps(cohort, body["cohort_retention"], pair_counts) if body["status"] == "ok" else []
    return {**body, "courses": courses}
