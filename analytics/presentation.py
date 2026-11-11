"""Calculation text shared by browser and model."""

from analytics.schemas import CalculationRow


def rate_row(
    label: str,
    numerator: int,
    denominator: int,
    *,
    kind="rate",
    exclusions=None,
    note="",
    group=None,
    horizon=None,
    provisional=False,
) -> CalculationRow:
    """Build a rate only when an eligible known population exists."""
    if denominator == 0:
        return CalculationRow(
            label=label,
            kind=kind,
            group=group or {},
            horizon=horizon,
            status="unknown",
            note=note or "No eligible known outcomes; this is not a zero rate.",
        )
    rate = round(numerator / denominator, 4)
    return CalculationRow(
        label=label,
        kind=kind,
        group=group or {},
        horizon=horizon,
        status="provisional" if provisional else "ok",
        numerator=numerator,
        denominator=denominator,
        rate=rate,
        exclusions=exclusions or {},
        note=note,
        calculation=f"{numerator} / {denominator} = {rate:.2%}",
    )
