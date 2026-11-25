"""Deterministic answer wording from disclosed results, never provider-generated numbers."""

from analytics.contracts_v2 import AnswerPresentation, HiddenTableRow, VisibleResult
from analytics.explanations import REASON_MESSAGES
from analytics.programs import PROGRAMS

HORIZONS = {
    "four_year": "Within four years",
    "six_year": "Within six years",
    "to_date": "Completion to date",
}
CREDENTIALS = {"B": "Bachelor's degree", "A": "Associate degree", "C": "Certificate"}


def describe_scope(step):
    """Translate all executed parameters while keeping every filter explicit."""
    parts = []
    for key, value in step.parameters.model_dump(mode="json").items():
        if value is None:
            continue
        if key == "credential":
            parts.append(CREDENTIALS[value])
        elif key == "program":
            parts.append(PROGRAMS[value]["label"])
        elif key == "cohort":
            parts.append(f"{value} entry cohort")
        elif key == "filters":
            selected = [
                f"{name.replace('_', ' ')}: {item}"
                for name, item in value.items()
                if item is not None
            ]
            parts.extend(selected or ["No additional filters"])
        elif key == "group_by":
            parts.append(
                "Grouped by " + ", ".join(value) if value else "Overall result"
            )
        else:
            parts.append(f"{key.replace('_', ' ')}: {value}")
    return " · ".join(parts) or "All students covered by the selected definition"


def present_answer(step, spec, result):
    """Format existing units, values and reasons after disclosure without calculating metrics."""
    titles = {
        "legacy.graduation": "Graduation results",
        "legacy.entry_major_retention": "Retention by entry major",
        "legacy.annual_enrollment": "Enrollment by ethnicity and program",
        "dfw.course_list": "DFW course results",
        "dfw.course_detail": "DFW course details",
        "credit_momentum.summary": "First-year credit momentum",
        "gateway.course_outcomes": "Gateway course outcomes",
        "student_paths.summary": "Student paths",
    }
    summary = "Your results are ready."
    items, caveats = [], []
    if not isinstance(result, VisibleResult):
        summary = {
            "unknown": "There isn't enough usable information to calculate this result.",
            "unavailable": "Information needed to calculate this result is missing.",
            "not_yet_observable": "Follow-up is incomplete for this result.",
            "not_reported": "The source does not report this result.",
            "suppressed": "This result has no displayed value. Usable evidence is needed before a number can be reported.",
        }[result.status]
        if result.reason == "unsupported_evidence":
            summary = "The available evidence does not support this calculation."
        elif result.reason == "zero_variance":
            summary = "A relationship cannot be calculated because one of the values does not vary."
    elif result.payload.kind == "table":
        payload = result.payload
        all_rows = (
            *payload.rows,
            *(row for page in payload.pages for row in page.rows),
        )
        visible = [row for row in all_rows if not isinstance(row, HiddenTableRow)]
        if not visible:
            summary = (
                "A graduation rate isn't available for this selection."
                if spec.id == "legacy.graduation"
                else "A result isn't available for this selection."
            )
        else:
            summary = "Results are shown below. Open calculation details to see every group and supporting count."
        for row in all_rows:
            if isinstance(row, HiddenTableRow):
                if row.explanation is not None:
                    detail = row.explanation
                    window = HORIZONS.get(detail.horizon, detail.label)
                    text = f"{window}: {REASON_MESSAGES[detail.reason]}"
                    if text not in items:
                        items.append(text)
                continue
            if not spec.id.startswith("legacy."):
                cells = dict(zip((column.id for column in payload.columns), row.cells))
                labels = {
                    "students": "Students in this selection",
                    "credits.avg_earned": "Average first-year credits earned",
                    "credits.avg_attempted": "Average first-year credits attempted",
                    "retention.rate": "Retention rate",
                    "everyone.rate": "DFW rate for all selected course enrollments",
                }
                component = cells.get("component")
                number = cells.get("number")
                if component in labels and number is not None:
                    value = (
                        f"{number:.2%}"
                        if cells["unit"] == "ratio"
                        else f"{number} {cells['unit']}"
                    )
                    sample = (
                        f" (eligible n={cells['applicable_n']})"
                        if cells.get("applicable_n") is not None
                        else ""
                    )
                    items.append(f"{labels[component]}: {value}{sample}.")
                continue
            cells = dict(zip((column.id for column in payload.columns), row.cells))
            if cells["kind"] == "exclusion":
                continue
            window = HORIZONS.get(cells["horizon"], "")
            label = f"{window} — {cells['label']}" if window else cells["label"]
            if cells["rate"] is not None:
                items.append(
                    f"{label}: {cells['rate']:.2%} ({cells['numerator']} of {cells['denominator']} students)."
                )
            elif cells["count"] is not None:
                items.append(f"{label} · {cells['group']}: {cells['count']} students.")
        if spec.id == "legacy.graduation":
            caveats.extend(
                (
                    "An unavailable rate does not mean that nobody graduated or that the rate is 0%.",
                    "Completion to date describes the available follow-up; it is not a four-year or six-year graduation rate.",
                    "Graduating specifically in the selected program requires award-program information; this extract has no exact award semester.",
                )
            )
    elif result.payload.kind == "rate":
        value = result.payload
        summary = f"{value.value:.2%}: {value.numerator} {value.numerator_unit} out of {value.denominator} {value.denominator_unit}."
    elif result.payload.kind == "count":
        summary = f"{result.payload.count} {result.payload.unit}."
    elif result.payload.kind == "mean":
        summary = f"Average: {result.payload.value} {result.payload.unit}, based on {result.payload.n} observed values."
    elif result.payload.kind == "correlation":
        summary = "The observed relationship is shown below. A relationship does not establish cause and effect."
    else:
        summary = "Group averages and differences are shown below, with the number of usable observations for each group."
    if result.status == "provisional":
        caveats.append("This result is provisional. Follow-up is incomplete.")
    return AnswerPresentation(
        title=titles.get(spec.id, spec.label),
        scope=describe_scope(step),
        summary=summary,
        items=items,
        caveats=caveats,
    )
