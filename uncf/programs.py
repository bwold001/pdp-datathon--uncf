"""Curated program aliases and conservative final-semester attribution."""

from __future__ import annotations

import re

# NCES CIP 2020: https://nces.ed.gov/ipeds/cipcode/cipdetail.aspx?y=56&cipid=90775
PROGRAMS = {
    "chemistry_general": {"label": "Chemistry, General (40.0501)", "codes": {"400501"}},
    "chemistry_family": {
        "label": "Chemistry family (40.05)",
        "codes": {
            "400501",
            "400502",
            "400503",
            "400504",
            "400506",
            "400507",
            "400508",
            "400509",
            "400510",
            "400599",
        },
    },
}


def normalize_program(value: object) -> str | None:
    """Preserve full CIP codes without guessing truncated values."""
    text = str(value or "").strip()
    if re.fullmatch(r"\d{2}\.\d{4}", text):
        text = text.replace(".", "")
    return text if re.fullmatch(r"\d{6}", text) else None


def resolve_program(alias: str) -> set[str]:
    """Resolve a curated name; arbitrary course subjects are not majors."""
    if alias not in PROGRAMS:
        raise ValueError("Choose chemistry_general or chemistry_family")
    return set(PROGRAMS[alias]["codes"])


def final_program(terms: list[dict], award_term_id: int | None) -> str | None:
    """Infer a major only when evidence resolves a unique relevant award semester."""
    if award_term_id is None:
        return None
    award_terms = [
        t
        for t in terms
        if t["term_id"] == award_term_id
        and t["academic_year"] != "UNKNOWN"
        and t["academic_term"] != "UNKNOWN"
    ]
    if not award_terms:
        return None
    bound = award_terms[0]["sort_order"]
    candidates = [
        t
        for t in terms
        if t["sort_order"] <= bound
        and t["academic_year"] != "UNKNOWN"
        and t["academic_term"] != "UNKNOWN"
    ]
    latest = max(t["sort_order"] for t in candidates)
    programs = {
        normalize_program(t["term_program_of_study"])
        for t in candidates
        if t["sort_order"] == latest
    }
    return next(iter(programs)) if len(programs) == 1 and None not in programs else None
