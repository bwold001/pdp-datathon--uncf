"""Writes the Explorer's fixture from the saved results, so the UI can be built before the #5 API exists.

Run it after the precompute: `python -m uncf.explorer_fixture`. Delete it once the Explorer reads the API.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from measures.save_results import RESULTS_DATABASE
from uncf.paths_mock import build_paths

# Served as a static file by the client. Git-ignored: it is a generated output (see AGENTS.md).
FIXTURE = Path(__file__).parent.parent / "playground/client_application/public/uncf/explorer-fixture.json"
# The groupings the Explorer offers. Ethnicity is left out because race already lists Hispanic.
DIMENSIONS = ["pell", "enrollment_intensity", "cohort_term", "enrollment_type", "age_band", "gender", "race"]

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


def main() -> None:
    """Write the fixture where the Explorer page loads it from."""
    fixture = build_fixture()
    # MOCK: year-2 paths have no endpoint or owner yet. The Explorer labels this chart as mock data.
    fixture["paths"] = build_paths()
    FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    FIXTURE.write_text(json.dumps(fixture, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"wrote {FIXTURE} ({FIXTURE.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
