"""How the pages group grades, and the tables that tell staff what each group holds.

Pages don't show + and - letters. They show groups cut only where a rule draws a line: the DFW line (DFW_BELOW,
1.7: a C- passes) and the PDP's gateway pass line (GATEWAY_PASS_AT, 1.0: a D passes, a D- doesn't). Every group
and every range in the tables comes from those settings and the letter scale, so the tables can never disagree
with the numbers, whatever grades a school's data holds.
"""
from __future__ import annotations

from ..calculations.dfw import DFW_BELOW, DFW_GROUPS
from ..calculations.grades import GATEWAY_PASS_AT, LETTER_SCALE, lowest_points

# The gateway page's groups, best first. The failing group is named for the pass line, e.g. "Under 1.0".
UNDER_PASS = f"Under {GATEWAY_PASS_AT:.1f}"
GATEWAY_GROUPS = ("C or higher", "D", UNDER_PASS, "P", "W")
# The lowest grade points any letter needs; under this is an F (0.7, the lowest D).
F_BELOW = min(points for _, points in LETTER_SCALE)

# The grades in the course file that aren't final, so neither page counts them (dfw.GRADE_REASONS has the codes).
LEFT_OUT = (
    "I (incomplete), A (audit), M or MIS (missing), O or OTH (other), and any code the PDP dictionary doesn't list, "
    "such as UW, aren't final grades, so neither page counts them."
)


def gateway_group(letter: str) -> str:
    """A letter's gateway group: C or higher (passes the DFW line), D (passes the gateway line), under it, P or W."""
    if letter in ("P", "W"):
        return letter
    if letter == "F":
        return UNDER_PASS
    points = lowest_points(letter)
    if points >= DFW_BELOW:
        return "C or higher"
    if points >= GATEWAY_PASS_AT:
        return "D"
    return UNDER_PASS


def letters_between(low: float, high: float | None = None) -> str:
    """The scale's letters from low points up to under high, lowest first, e.g. 'D-, D, D+'."""
    letters = [letter for letter, points in LETTER_SCALE if points >= low and (high is None or points < high)]
    return ", ".join(reversed(letters))


def dfw_scale() -> dict:
    """The DFW page's table: each group it shows, its grade points, and whether it counts as a DFW."""
    passed_letters = [letter for letter, _ in LETTER_SCALE if letter not in DFW_GROUPS]
    rows = [
        {"grade": "C or higher", "points": f"{DFW_BELOW:.1f} and up ({passed_letters[-1]} and up)", "counted": False},
        {"grade": "D", "points": f"{F_BELOW:.1f} to under {DFW_BELOW:.1f} ({letters_between(F_BELOW, DFW_BELOW)})", "counted": True},
        {"grade": "F", "points": f"under {F_BELOW:.1f}, or the code F", "counted": True},
        {"grade": "P", "points": "the code P (pass)", "counted": False},
        {"grade": "W", "points": "the code W (withdrew)", "counted": True},
    ]
    return {"grades": rows, "left_out": LEFT_OUT}


def gateway_scale() -> dict:
    """The Gateway page's table: each group it shows, its grade points, and whether it passes the course."""
    rows = [
        {"grade": "C or higher", "points": f"{DFW_BELOW:.1f} and up", "counted": True},
        {"grade": "D", "points": f"{GATEWAY_PASS_AT:.1f} to under {DFW_BELOW:.1f} ({letters_between(GATEWAY_PASS_AT, DFW_BELOW)})", "counted": True},
        {"grade": UNDER_PASS, "points": f"under {GATEWAY_PASS_AT:.1f} ({letters_between(F_BELOW, GATEWAY_PASS_AT)} or F), or the code F", "counted": False},
        {"grade": "P", "points": "the code P (pass)", "counted": True},
        {"grade": "W", "points": "the code W (withdrew)", "counted": False},
    ]
    return {"grades": rows, "left_out": LEFT_OUT}
