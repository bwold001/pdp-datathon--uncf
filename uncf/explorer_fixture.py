"""Writes the Explorer's fixture from the saved results, so the UI can be built before the #5 API exists.

Run it after the precompute: `python -m uncf.explorer_fixture`. Delete it once the Explorer reads the API.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from measures.models import Cohort, Measure
from measures.run_measures import run_measure
from measures.save_results import RESULTS_DATABASE, group_columns
from uncf.paths_mock import build_paths
from uncf.precompute import COHORT_YEARS, group_bys

# Served as a static file by the client. Git-ignored: it is a generated output (see AGENTS.md).
FIXTURE = Path(__file__).parent.parent / "playground/client_application/public/uncf/explorer-fixture.json"
# The groupings the Explorer offers. Ethnicity is left out because race already lists Hispanic.
DIMENSIONS = ["pell", "enrollment_intensity", "cohort_term", "enrollment_type", "age_band", "gender", "race"]
# Outcomes the Explorer shows. Any the precompute doesn't save yet (persistence, today) are calculated here
# with the same measures code, so the UI can be built now. Once the precompute saves them, its rows are used.
EXPLORER_MEASURES = [Measure.RETENTION, Measure.PERSISTENCE, Measure.GATEWAY_MATH, Measure.GATEWAY_ENGLISH]

SQL = """
SELECT measure, cohort, group_dimensions, group_values, numerator, denominator, status, n_excluded, data_loaded_at
FROM success_measures
ORDER BY measure, cohort, group_dimensions, group_values
"""


def is_offered(group_dimensions: str) -> bool:
    """True for everyone, or a grouping made only of the dimensions the Explorer offers."""
    return group_dimensions == "all" or all(d in DIMENSIONS for d in group_dimensions.split(" x "))


def whole(value: float | None) -> int | float | None:
    """Counts come back as floats from SQLite; keep them as whole numbers when they are."""
    if value is None:
        return None
    return int(value) if float(value).is_integer() else value


def build_fixture(database: Path = RESULTS_DATABASE) -> dict:
    """Every saved row for the offered groupings, keyed by measure, then cohort, then grouping."""
    rows: dict = {}
    loaded_at = ""
    with sqlite3.connect(database) as connection:
        for measure, cohort, dimensions, values, numerator, denominator, status, n_excluded, loaded in connection.execute(SQL):
            if not is_offered(dimensions):
                continue
            # A hidden row keeps nulls and its status. It is never written as 0.
            row = [values, whole(numerator), whole(denominator), status, n_excluded]
            rows.setdefault(measure, {}).setdefault(cohort, {}).setdefault(dimensions, []).append(row)
            loaded_at = max(loaded_at, loaded)
    return {"loaded_at": loaded_at, "dimensions": DIMENSIONS, "rows": rows}


def calculated_rows(measure: Measure, run=run_measure) -> dict:
    """One measure for every class and offered grouping, calculated now instead of read from the saved results."""
    rows: dict = {}
    for result in run(measure, [Cohort.of(year) for year in COHORT_YEARS], group_bys()):
        dimensions, values = group_columns(result.group)
        if not is_offered(dimensions):
            continue
        status = result.status.value if hasattr(result.status, "value") else result.status
        row = [values, whole(result.numerator), whole(result.denominator), status, result.n_excluded]
        rows.setdefault(next(iter(result.cohort.years)), {}).setdefault(dimensions, []).append(row)
    return rows


def add_missing_measures(fixture: dict, run=run_measure) -> list[str]:
    """Calculate any Explorer outcome the saved results don't have yet. Returns the ones it added."""
    added = []
    for measure in EXPLORER_MEASURES:
        if measure.value not in fixture["rows"]:
            fixture["rows"][measure.value] = calculated_rows(measure, run)
            added.append(measure.value)
    return added


def main() -> None:
    """Write the fixture where the Explorer page loads it from."""
    fixture = build_fixture()
    added = add_missing_measures(fixture)
    if added:
        print(f"not in the saved results yet, calculated here: {', '.join(added)}")
    # MOCK: year-2 paths have no endpoint or owner yet. The Explorer labels this chart as mock data.
    fixture["paths"] = build_paths()
    FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    FIXTURE.write_text(json.dumps(fixture, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"wrote {FIXTURE} ({FIXTURE.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
