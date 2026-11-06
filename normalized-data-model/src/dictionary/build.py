"""Build config/column_dictionary.yaml: what each normalized column means, from the ARF data dictionaries.

One record per normalized table and column that the cohort or course mapping config writes. Its
description, dictionary codes and notes come from the markdown dictionary of one source file (the
cohort file's when it writes the column), and its sources list every source column with the
column_lookup.csv text, which holds the mock-data specifics.

The markdown and column_lookup.csv are the files people edit. This file is rebuilt from them, and a test
fails if the committed copy is stale. The public API is build_dictionary() and render().

Run from normalized-data-model/:
    python -m src.dictionary.build
"""

import argparse
import csv
from pathlib import Path

import yaml

from src.rules.rules import ConfigError, load_rules

__all__ = ["build_dictionary", "render", "DictionaryError"]

_BUILD = Path(__file__).resolve().parents[2]
_REPO = _BUILD.parent
_LOOKUP = "data/dictionaries/column_lookup.csv"
_OUTPUT = "config/column_dictionary.yaml"

# Source file, its mapping config and its markdown dictionary, in the order a description is chosen:
# the cohort file's wins when both files write a column.
_SOURCES = [
    ("pdp_cohort_data.csv", "cohort_mapping.yaml", "data/dictionaries/arf_cohort_data_dictionary.md"),
    ("pdp_course_data.csv", "course_mapping.yaml", "data/dictionaries/arf_course_data_dictionary.md"),
]

# Dictionary entries no mock-file column uses. The markdown has no headings, so these are listed to
# end the entry before them; otherwise their text would run into it.
_UNUSED_ENTRIES = {
    "pdp_cohort_data.csv": [
        "First Name", "Middle Name", "Last Name", "SSN", "Date of Birth", "Institution ID",
        "Most Recent Bachelors at Other Institution OPEID",
        "Most Recent Associates or Certificate at Other Institution OPEID",
        "Most Recent Last Enrollment at Other Institution OPEID",
        "First Bachelors at Other Institution OPEID",
        "First Associates or Certificate at Other Institution OPEID",
    ],
    "pdp_course_data.csv": [
        "First Name", "Middle Name", "Last Name", "SSN", "Date of Birth", "Institution ID",
        "Enrollment Record at Other Institution(s) OPEID(s)",
    ],
}

# A note written once in the markdown that describes every entry whose name contains the word, not
# the entry it happens to sit in.
_SHARED_NOTES = {"**LOCALE Values:**": "LOCALE"}

_HEADER = """\
# What each normalized column means, from the ARF data dictionaries. GENERATED: don't edit by hand.
# Edit data/dictionaries/arf_*_data_dictionary.md or data/dictionaries/column_lookup.csv, then run
# from normalized-data-model/:
#     python -m src.dictionary.build
#
# One record per table and column that the cohort or course mapping config writes:
#   dictionary_name, description, dictionary_values, notes
#       from the dictionary of description_source: the cohort file's when both files write the column.
#   dictionary_values   the dictionary's codes as it writes them; meaning is null where it gives none.
#                       Stored codes can differ (UK is stored as UNKNOWN): they're in destination_schema.yaml.
#   sources             every source column, with column_lookup.csv's description, which has the
#                       mock-data specifics.
# The data is synthetic: these describe the mock files' fields, not real students.

"""


class DictionaryError(ValueError):
    """A dictionary, the lookup or a mapping config doesn't line up, so the build stops."""


def build_dictionary(repo_root=_REPO, config_dir=None):
    """The column dictionary's records, in destination_schema.yaml's table and column order."""
    repo_root = Path(repo_root)
    config_dir = Path(config_dir) if config_dir else repo_root / "normalized-data-model/config"
    rules = load_rules(config_dir, [config_dir / config for _, config, _ in _SOURCES])
    lookup = _read_lookup(repo_root / _LOOKUP)

    entries, sources = {}, {}
    for source_file, config, dictionary_file in _SOURCES:
        names = [row["dictionary_name"] for (file, _), row in lookup.items() if file == source_file]
        text = (repo_root / dictionary_file).read_text(encoding="utf-8")
        entries[source_file] = _parse(text, [n for n in names if n], _UNUSED_ENTRIES[source_file], dictionary_file)
        for mapping in rules["mappings"][config]:
            if "source" not in mapping or "destination_table" not in mapping:
                continue
            row = lookup.get((source_file, mapping["source"]))
            if row is None:
                raise DictionaryError(f"{_LOOKUP} has no row for {source_file} {mapping['source']}")
            key = (mapping["destination_table"], mapping["destination_column"])
            sources.setdefault(key, []).append({
                "source_file": source_file,
                "source_column": mapping["source"],
                "dictionary_file": dictionary_file if row["dictionary_name"] else None,
                "lookup_description": row["description"] or None,
            })

    records = []
    for table, columns in rules["schema"].items():
        for column in columns:
            if (table, column) in sources:
                records.append(_record(table, column, sources[(table, column)], lookup, entries))
    return records


def render(records):
    """The YAML file's text for these records."""
    body = yaml.dump(records, Dumper=_PlainDumper, sort_keys=False, allow_unicode=True, width=100)
    return _HEADER + body


class _PlainDumper(yaml.SafeDumper):
    """A safe dumper that writes a repeated value out in full, never as an &anchor and *alias."""

    def ignore_aliases(self, data):
        return True


def _record(table, column, sources, lookup, entries):
    """One normalized column's record, its description from the first source the dictionary has."""
    primary = next((s for s in sources if lookup[(s["source_file"], s["source_column"])]["dictionary_name"]), None)
    entry, name = {}, None
    if primary:
        name = lookup[(primary["source_file"], primary["source_column"])]["dictionary_name"]
        entry = entries[primary["source_file"]][name]
    return {
        "table": table,
        "column": column,
        "dictionary_name": name,
        "description_source": primary["source_file"] if primary else None,
        "description": entry.get("description"),
        "dictionary_values": entry.get("dictionary_values", []),
        "notes": entry.get("notes"),
        "sources": sources,
    }


def _read_lookup(path):
    """{(file, column_in_csv): row} from column_lookup.csv."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        return {(row["file"], row["column_in_csv"]): row for row in csv.DictReader(f)}


def _parse(text, names, unused, where):
    """{name: {description, dictionary_values, notes}} for each name in one markdown dictionary."""
    lines = text.replace("\r\n", "\n").split("\n")
    known = {_name(n): n for n in names}
    ends = {_name(n) for n in unused}
    starts = [(i, _name(line)) for i, line in enumerate(lines) if _name(line) in known or _name(line) in ends]

    seen = [key for _, key in starts if key in known]
    missing = sorted(known[k] for k in set(known) - set(seen))
    repeated = sorted({known[k] for k in seen if seen.count(k) > 1})
    if missing or repeated:
        raise DictionaryError(f"{where}: entries not found {missing}, entries found more than once {repeated}")

    parsed, shared = {}, []
    for (start, key), (end, _) in zip(starts, starts[1:] + [(len(lines), None)]):
        if key not in known:
            continue
        entry = _parse_entry(lines[start + 1:end])
        for prefix, word in _SHARED_NOTES.items():
            kept = [p for p in entry["notes"] if not p.startswith(prefix)]
            shared += [(word, p) for p in entry["notes"] if p.startswith(prefix)]
            entry["notes"] = kept
        parsed[known[key]] = entry

    for word, paragraph in shared:
        for name, entry in parsed.items():
            if word in name:
                entry["notes"].append(paragraph)
    for entry in parsed.values():
        entry["notes"] = "\n\n".join(entry["notes"]) or None
    return parsed


def _parse_entry(lines):
    """One entry's text: paragraphs before the first list are the description, the list right after
    them is the codes, and everything else (bold-labelled notes, later paragraphs) is notes."""
    description, values, notes = [], [], []
    for block in _blocks(lines):
        is_list = all(line.startswith("- ") for line in block)
        if is_list and not values and not notes:
            values = [_value(line[2:]) for line in block]
        elif not is_list and not values and not notes and not block[0].startswith("**"):
            description.append(" ".join(block))
        else:
            notes.append("\n".join(block) if is_list else " ".join(block))
    return {"description": "\n\n".join(description) or None, "dictionary_values": values, "notes": notes}


def _blocks(lines):
    """The non-blank runs of lines, each line stripped."""
    blocks, current = [], []
    for line in lines + [""]:
        if line.strip():
            current.append(line.strip())
        elif current:
            blocks.append(current)
            current = []
    return blocks


def _value(bullet):
    """{code, meaning} from one bullet: `C = College ready`, or just `20 and younger`."""
    code, separator, meaning = bullet.partition("=")
    if not separator:
        return {"code": bullet.strip(), "meaning": None}
    return {"code": code.strip(), "meaning": meaning.strip()}


def _name(line):
    """A line as an entry name: trimmed, without a trailing period (`Years to ... Inst.`)."""
    return line.strip().rstrip(".").strip()


def _main(argv=None):
    parser = argparse.ArgumentParser(description="Build config/column_dictionary.yaml from the ARF data dictionaries.")
    parser.add_argument("--output", default=str(_BUILD / _OUTPUT), help="where to write it (default: %(default)s)")
    args = parser.parse_args(argv)
    try:
        records = build_dictionary()
    except (ConfigError, DictionaryError) as error:
        parser.error(str(error))
    Path(args.output).write_text(render(records), encoding="utf-8")
    print(f"wrote {len(records)} columns to {args.output}")


if __name__ == "__main__":
    _main()
