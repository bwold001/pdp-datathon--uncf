"""Checks the measure definitions (#3)."""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

from measures.definitions import DEFINITIONS, FINDINGS, definition_for
from measures.models import Measure

FINDINGS_CSV = Path(__file__).parents[2] / "data" / "quality" / "findings.csv"
EXPLORER_MEASURES = ["retention", "persistence", "gateway_math", "gateway_english"]
TEXT_FIELDS = ["name", "pdp_name", "what", "how", "who"]


def test_every_explorer_measure_has_a_definition() -> None:
    """The four outcomes the Explorer shows all have a definition."""
    assert set(EXPLORER_MEASURES) <= set(DEFINITIONS)


# Definitions that aren't a measure of their own: the Explorer's other key terms.
EXPLORER_TERMS = {"credit_milestones", "student_paths"}


def test_every_key_is_a_real_measure_or_explorer_term() -> None:
    """No definition for a measure the measures package doesn't have, and every measure has one."""
    assert set(DEFINITIONS) - EXPLORER_TERMS == {m.value for m in Measure}


@pytest.mark.parametrize("measure", sorted(DEFINITIONS))
def test_definition_has_every_field_filled_in(measure: str) -> None:
    """Each definition has the six fields the client reads, none of them empty."""
    definition = DEFINITIONS[measure]
    assert set(definition) == {*TEXT_FIELDS, "limits"}
    for field in TEXT_FIELDS:
        assert isinstance(definition[field], str) and definition[field].strip(), field
    assert definition["limits"] and all(line.strip() for line in definition["limits"])


def test_names_are_unique() -> None:
    """Two measures never share a label on screen."""
    names = [d["name"] for d in DEFINITIONS.values()]
    assert len(names) == len(set(names))


def test_no_em_dashes() -> None:
    """House style: no em dashes in anything staff read."""
    for definition in DEFINITIONS.values():
        text = " ".join([*(definition[f] for f in TEXT_FIELDS), *definition["limits"]])
        assert "—" not in text


def test_cited_findings_exist() -> None:
    """Every findings.csv row a caveat points to is a real row."""
    with FINDINGS_CSV.open(newline="", encoding="utf-8") as file:
        ids = {row["id"] for row in csv.DictReader(file)}
    for measure, cited in FINDINGS.items():
        assert measure in DEFINITIONS
        assert set(cited) <= ids, measure


def test_definition_for_unknown_measure_raises() -> None:
    """Asking for a measure with no definition is an error, not an empty answer."""
    assert definition_for("retention")["pdp_name"] == "Retention"
    with pytest.raises(KeyError):
        definition_for("graduation")


def test_a_school_can_use_its_own_name(monkeypatch) -> None:
    """With UNCF_SCHOOL set, a school's own name replaces the label and the PDP name stays."""
    from measures import definitions

    monkeypatch.setitem(definitions.LOCAL_NAMES, "fmu", {"retention": "Returned to FMU"})
    monkeypatch.setenv("UNCF_SCHOOL", "fmu")
    assert definition_for("retention")["name"] == "Returned to FMU"
    assert definition_for("retention")["pdp_name"] == "Retention"
    monkeypatch.delenv("UNCF_SCHOOL")
    assert definition_for("retention")["name"] == "Returned here"
