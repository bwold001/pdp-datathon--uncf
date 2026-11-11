"""The grade scale as staff read it: each grade's points, and whether the DFW and Gateway pages count it.

Built from the rules themselves (grades.LETTER_SCALE and GATEWAY_PASS_AT, dfw.DFW_GRADES), so the
table on a page can never disagree with the numbers above it.
"""
from __future__ import annotations

from ..calculations.dfw import DFW_GRADES
from ..calculations.grades import LETTER_SCALE, letter_passes_gateway

# The grades in the course file that aren't final, so neither page counts them (dfw.GRADE_REASONS has the codes).
LEFT_OUT = (
    "I (incomplete), A (audit), M or MIS (missing), O or OTH (other), and any code the PDP dictionary doesn't list, "
    "such as UW, aren't final grades, so neither page counts them."
)


def grade_scale() -> dict:
    """Each final grade, best first: its grade points, whether it is a DFW, and whether it passes a gateway course."""
    rows = []
    higher = None
    for letter, lowest in LETTER_SCALE:
        points = f"{lowest:.1f}" if higher is None else f"{lowest:.1f} to under {higher:.1f}"
        rows.append({"grade": letter, "points": points, "dfw": letter in DFW_GRADES, "gateway_pass": letter_passes_gateway(letter)})
        higher = lowest
    codes = {"F": f"under {higher:.1f}, or the code F", "P": "the code P (pass)", "W": "the code W (withdrew)"}
    for code, points in codes.items():
        rows.append({"grade": code, "points": points, "dfw": code in DFW_GRADES, "gateway_pass": letter_passes_gateway(code)})
    return {"grades": rows, "left_out": LEFT_OUT}
