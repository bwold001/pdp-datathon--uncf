"""Calculation text and conservative suppression shared by browser and model."""

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


def has_small_cell(row: CalculationRow, threshold: int) -> bool:
    """Detect small values or recoverable complements before serializing evidence."""
    return row.status in ("ok", "provisional") and (
        (row.count is not None and 0 < row.count < threshold)
        or (row.denominator is not None and row.denominator < threshold)
        or (row.numerator is not None and 0 < row.numerator < threshold)
        or (
            row.denominator is not None
            and row.numerator is not None
            and 0 < row.denominator - row.numerator < threshold
        )
        or any(0 < n < threshold for n in row.exclusions.values())
    )


def suppress(rows: list[CalculationRow], threshold: int) -> list[CalculationRow]:
    """Hide linked small cells, preserving a safe overall result only with all groups hidden."""
    if not any(has_small_cell(row, threshold) for row in rows):
        return rows
    totals = [row for row in rows if not row.group and row.horizon is None]
    safe_total = (
        totals[0]
        if len(totals) == 1
        and any(row.group for row in rows)
        and not has_small_cell(totals[0], threshold)
        else None
    )
    return [
        CalculationRow(
            label=row.label,
            kind=row.kind,
            group=row.group,
            horizon=row.horizon,
            status="suppressed",
            note="Linked results hidden to prevent small-cell disclosure.",
        )
        if row is not safe_total and row.status in ("ok", "provisional")
        else row
        for row in rows
    ]
