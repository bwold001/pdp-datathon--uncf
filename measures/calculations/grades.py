"""The letter grade scale: which letter each grade in the course file is, so pages can show every grade apart.

The PDP course file has grade points (0 to 4) and a few codes, not letters. This is the standard 4.0 plus/minus
scale. A letter covers its own grade points up to the next letter's, so 1.5 is a D+ and 3.6 is a B+. Anything
under the lowest letter (D-) is an F, whatever the number. A school with another scale changes LETTER_SCALE only.
"""
from __future__ import annotations

from functools import cache

# Each letter and the lowest grade points it covers, highest first.
LETTER_SCALE = (
    ("A", 4.0),
    ("A-", 3.7),
    ("B+", 3.3),
    ("B", 3.0),
    ("B-", 2.7),
    ("C+", 2.3),
    ("C", 2.0),
    ("C-", 1.7),
    ("D+", 1.3),
    ("D", 1.0),
    ("D-", 0.7),
)
# Codes that are a final grade on their own (the dictionary's P = pass, F = fail, W = withdraw).
FINAL_CODES = ("P", "F", "W")
# The PDP's gateway pass line (CompletedGatewayMathYear1 and CompletedGatewayEnglishYear1): 1.0 or higher, or a P.
GATEWAY_PASS_AT = 1.0
# Every final grade in the order pages list them: the letters down to F, then pass and withdrawal.
GRADE_ORDER = (*(letter for letter, _ in LETTER_SCALE), "F", "P", "W")


def letter_for(points: float) -> str:
    """The letter for a number of grade points: the highest letter whose lowest points it reaches, else F."""
    hundredths = round(points * 100)
    for letter, lowest in LETTER_SCALE:
        if hundredths >= round(lowest * 100):
            return letter
    return "F"


def lowest_points(letter: str) -> float:
    """The fewest grade points that still earn a letter on the scale."""
    return dict(LETTER_SCALE)[letter]


def letter_passes_gateway(letter: str) -> bool:
    """Whether a letter passes a gateway course: P, or a letter whose lowest points reach the pass line."""
    if letter == "P":
        return True
    return letter in dict(LETTER_SCALE) and lowest_points(letter) >= GATEWAY_PASS_AT


def numeric_letters() -> dict[str, str]:
    """Every grade point from 0 to 4 in hundredths, written each way it appears ('1', '1.0', '1.00', '3.67'), mapped to its letter."""
    letters = {}
    for hundredths in range(0, 401):
        points = hundredths / 100
        spellings = {f"{points:g}", f"{points:.2f}"}
        if hundredths % 10 == 0:
            spellings.add(f"{points:.1f}")
        for spelling in spellings:
            letters[spelling] = letter_for(points)
    return letters


@cache
def known_letters() -> dict[str, str]:
    """Every final grade as written in the course file (numbers and codes, in capitals), mapped to its letter."""
    return {**numeric_letters(), **{code: code for code in FINAL_CODES}}


def grade_letter(grade: str | None) -> str | None:
    """A final grade's letter (A to D-, F), or P or W; None for a grade that isn't final or isn't listed."""
    return known_letters().get((grade or "").strip().upper())
