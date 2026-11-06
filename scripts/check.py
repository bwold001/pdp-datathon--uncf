"""Check that the shared data files have not changed by accident.

Compares every CSV in data/raw/ with its entry in data/manifest.json (checksum, rows, columns,
column names), and checks that the README's data table matches the manifest.

Uses only the Python standard library, so it runs on Mac, Windows, and Linux with nothing to
install.

    python scripts/check.py           # check (also: make check)
    python scripts/check.py --update  # rewrite the manifest after a deliberate data change
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
MANIFEST = ROOT / "data" / "manifest.json"
README = ROOT / "README.md"

# A README data-table row looks like: | [name.csv](data/raw/name.csv) | 10,313 | 85 | ... |
README_ROW = re.compile(r"^\|\s*\[[^\]]+\]\((data/raw/[^)]+\.csv)\)\s*\|\s*([\d,]+)\s*\|\s*(\d+)\s*\|")


def describe(path: Path) -> dict:
    """Return the manifest entry for one CSV."""
    sha = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            sha.update(chunk)
    with open(path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.reader(fh)
        names = next(reader)
        rows = sum(1 for _ in reader)
    return {"sha256": sha.hexdigest(), "rows": rows, "columns": len(names), "column_names": names}


def data_files() -> dict:
    return {p.relative_to(ROOT).as_posix(): p for p in sorted(RAW.glob("*.csv"))}


def update() -> int:
    manifest = {"files": {key: describe(path) for key, path in data_files().items()}}
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {MANIFEST.relative_to(ROOT).as_posix()} for {len(manifest['files'])} files.")
    print("Commit it in the same pull request as the data change, and update the README table.")
    return 0


def check_data(expected: dict, problems: list) -> None:
    files = data_files()
    for key in sorted(set(expected) - set(files)):
        problems.append(f"{key}: listed in data/manifest.json but the file is missing.")
    for key in sorted(set(files) - set(expected)):
        problems.append(f"{key}: new file, not in data/manifest.json.")
    for key in sorted(set(files) & set(expected)):
        want, got = expected[key], describe(files[key])
        if got == want:
            continue
        details = []
        added = [c for c in got["column_names"] if c not in want["column_names"]]
        removed = [c for c in want["column_names"] if c not in got["column_names"]]
        if added:
            details.append(f"new columns {added}")
        if removed:
            details.append(f"missing columns {removed}")
        if not added and not removed and got["column_names"] != want["column_names"]:
            details.append("columns are in a different order")
        if got["rows"] != want["rows"]:
            details.append(f"rows {want['rows']:,} -> {got['rows']:,}")
        if not details:
            details.append("contents changed (same rows and columns, so at least one value changed)")
        problems.append(f"{key}: does not match data/manifest.json: " + "; ".join(details) + ".")


def check_readme(expected: dict, problems: list) -> None:
    found = {}
    for line in README.read_text(encoding="utf-8").splitlines():
        m = README_ROW.match(line)
        if m:
            found[m.group(1)] = (int(m.group(2).replace(",", "")), int(m.group(3)))
    for key, entry in sorted(expected.items()):
        if key not in found:
            problems.append(f"README.md: the data table has no row for {key}.")
            continue
        rows, cols = found[key]
        if (rows, cols) != (entry["rows"], entry["columns"]):
            problems.append(
                f"README.md: the data table says {key} has {rows:,} rows and {cols} columns; "
                f"the manifest says {entry['rows']:,} and {entry['columns']}."
            )


def check() -> int:
    if not MANIFEST.exists():
        print("FAIL: data/manifest.json is missing. Run: python scripts/check.py --update")
        return 1
    expected = json.loads(MANIFEST.read_text(encoding="utf-8"))["files"]
    problems: list = []
    check_data(expected, problems)
    check_readme(expected, problems)
    if problems:
        for p in problems:
            print(f"FAIL: {p}")
        print()
        print("If the data change is on purpose: run `python scripts/check.py --update`, update the")
        print("README data table, and commit both in this pull request so the Reviewer sees it.")
        return 1
    print(f"OK: {len(expected)} data files match data/manifest.json, and the README table matches.")
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if args not in ([], ["--update"]):
        print(__doc__)
        sys.exit(2)
    sys.exit(update() if args else check())
