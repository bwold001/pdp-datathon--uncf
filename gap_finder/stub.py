"""Hand-written rows in the final shape, so the UI kit and other squads can build before the real calculation lands.

The counts are retention by race from the synthetic mock data, as the shared measures count it (#61). The
comparison columns were worked out from those counts once and typed in. Nothing here reads a database.
"""
from __future__ import annotations

from .models import NOISE_Q, GapResult, GapStatus

MEASURE = "retention"
POOLED = "2021-22 + 2022-23 + 2023-24"
NEWEST = "2024-25"
DATA_LOADED_AT = "stub"

NOTE = (
    "STUB. Hand-written from synthetic mock data, not computed, and not a finding about real students. "
    "Retention: students who came back the next year, compared with everyone else in the same cohort. "
    "A gap shows a difference, not its cause."
)
UNKNOWN_NOTE = NOTE + " Unknown values stay in everyone else, but aren't compared or ranked."
HIDDEN_NOTE = NOTE + " Historical suppressed fixture; current calculations show every nonempty group."
TOO_NEW_NOTE = NOTE + " Hidden: the cohort is too new for retention."

RACES = (
    "American Indian or Alaska Native",
    "Asian",
    "Black or African American",
    "Hispanic",
    "Native Hawaiian or Other Pacific Islander",
    "Nonresident alien",
    "Two or More Races",
    "White",
    "UNKNOWN",
)

# Everyone in the pooled cohorts: 4,125 of 7,701 retained.
EVERYONE_NUMERATOR = 4125
EVERYONE_DENOMINATOR = 7701

# Pooled cohorts, by race, most students behind first. Columns: race, numerator, denominator, metric_rate,
# comparison numerator, denominator and rate, gap_pts, students_affected, ci_low, ci_high, p_value, q_value,
# rank_by_affected, rank_by_gap.
COMPARED = (
    ("Black or African American", 565, 1218, 0.4639, 3560, 6483, 0.5491, -8.53, -103.8, -11.56, -5.47,
     4.4059024806359754e-08, 3.5247219845087803e-07, 1, 3),
    ("American Indian or Alaska Native", 61, 148, 0.4122, 4064, 7553, 0.5381, -12.59, -18.6, -20.28, -4.46,
     0.0023540875217095227, 0.006277566724558727, 2, 2),
    ("Native Hawaiian or Other Pacific Islander", 6, 23, 0.2609, 4119, 7678, 0.5365, -27.56, -6.3, -41.14, -7.15,
     0.008139490434714862, 0.013023184695543779, 3, 1),
    ("Two or More Races", 104, 196, 0.5306, 4021, 7505, 0.5358, -0.52, -1.0, -7.59, 6.44,
     0.8862099640464226, 0.8862099640464226, 4, 4),
    ("Hispanic", 1082, 2014, 0.5372, 3043, 5687, 0.5351, 0.22, 4.3, -2.32, 2.74,
     0.8673899411062108, 0.8862099640464226, 5, 5),
    ("Nonresident alien", 97, 155, 0.6258, 4028, 7546, 0.5338, 9.2, 14.3, 1.29, 16.52,
     0.02298198990832058, 0.030642653211094106, 6, 8),
    ("Asian", 341, 561, 0.6078, 3784, 7140, 0.53, 7.79, 43.7, 3.53, 11.91,
     0.0003694684742348702, 0.0014778738969394808, 7, 7),
    ("White", 1704, 3068, 0.5554, 2421, 4633, 0.5226, 3.29, 100.8, 1.01, 5.55,
     0.004651183069352605, 0.00930236613870521, 8, 6),
)


# No comparison: the columns a hidden or unknown row leaves blank.
NO_COMPARISON = dict(
    comparison_numerator=None, comparison_denominator=None, comparison_rate=None,
    gap_pts=None, students_affected=None, ci_low=None, ci_high=None, p_value=None, q_value=None,
    likely_noise=None, rank_by_affected=None, rank_by_gap=None,
)


def compared_row(race, numerator, denominator, rate, comparison_numerator, comparison_denominator, comparison_rate,
                 gap_pts, affected, ci_low, ci_high, p_value, q_value, rank_by_affected, rank_by_gap) -> GapResult:
    """An ok row: one race compared with everyone else in the pooled cohorts."""
    return GapResult(
        measure=MEASURE, cohort=POOLED, group_dimensions=("race",), group_values=(race,),
        numerator=numerator, denominator=denominator, metric_rate=rate,
        suppressed=False, status=GapStatus.OK, n_excluded=0, n_out_of_scope=0, exclusion_reason=None,
        note=NOTE, data_loaded_at=DATA_LOADED_AT,
        comparison_numerator=comparison_numerator, comparison_denominator=comparison_denominator,
        comparison_rate=comparison_rate, gap_pts=gap_pts, students_affected=affected,
        ci_low=ci_low, ci_high=ci_high, p_value=p_value, q_value=q_value, likely_noise=q_value >= NOISE_Q,
        rank_by_affected=rank_by_affected, rank_by_gap=rank_by_gap,
    )


def blank_row(cohort: str, dimensions: tuple[str, ...], values: tuple[str, ...], status: GapStatus, note: str) -> GapResult:
    """A hidden row: every number blank."""
    return GapResult(
        measure=MEASURE, cohort=cohort, group_dimensions=dimensions, group_values=values,
        numerator=None, denominator=None, metric_rate=None,
        suppressed=True, status=status, n_excluded=None, n_out_of_scope=None, exclusion_reason=None,
        note=note, data_loaded_at=DATA_LOADED_AT, **NO_COMPARISON,
    )


def unknown_row() -> GapResult:
    """Unknown race in the pooled cohorts: its own counts, but no comparison or rank."""
    return GapResult(
        measure=MEASURE, cohort=POOLED, group_dimensions=("race",), group_values=("UNKNOWN",),
        numerator=165, denominator=318, metric_rate=0.5189,
        suppressed=False, status=GapStatus.UNKNOWN_GROUP, n_excluded=0, n_out_of_scope=0, exclusion_reason=None,
        note=UNKNOWN_NOTE, data_loaded_at=DATA_LOADED_AT, **NO_COMPARISON,
    )


def stub_rows() -> list[GapResult]:
    """Every stub row: at least one per status, and one two-way group."""
    rows = [compared_row(*values) for values in COMPARED]
    rows.append(unknown_row())
    # Historical suppressed evidence remains a contract fixture; current calculations show this group.
    rows.append(blank_row(POOLED, ("gender", "race"), ("X", "Two or More Races"), GapStatus.SUPPRESSED, HIDDEN_NOTE))
    # 2024-25 students can't have come back a year later yet.
    rows.extend(blank_row(NEWEST, ("race",), (race,), GapStatus.NOT_YET_OBSERVABLE, TOO_NEW_NOTE) for race in RACES)
    return rows
