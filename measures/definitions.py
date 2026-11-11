"""Staff-facing definitions shared by every API route, the Explorer pages and the chat."""
from __future__ import annotations

import os
from typing import TypedDict


class Definition(TypedDict):
    """One measure's definition, as the client reads it."""

    name: str  # the short label the Explorer shows
    pdp_name: str  # the Postsecondary Data Partnership's name for it
    what: str  # what the number means
    how: str  # how it is worked out
    who: str  # which students are counted
    limits: list[str]  # what to keep in mind when reading it


EVERYONE_WHO_ENTERED = (
    "Everyone who entered that year: every start term (fall, winter, spring and summer) and every "
    "enrollment type (first time, transfer in and readmitted)."
)
NEWEST_CLASS = "The newest entering class may not have its full second year in the data yet, so its rate can still change."
GATEWAY_NOT_MAPPED = "Each college chooses its gateway courses. Until they are mapped in the data, this shows Not reported."
GATEWAY_UNKNOWN_ATTEMPT = (
    "In the practice data, many students with an unknown attempt are recorded as not passing, which lowers the rate."
)

DEFINITIONS: dict[str, Definition] = {
    "retention": {
        "name": "Returned here",
        "pdp_name": "Retention",
        "what": "Enrolled at this college again in the next academic year, or earned a credential here by then.",
        "how": "Students who returned or earned a credential here, out of the entering class.",
        "who": EVERYONE_WHO_ENTERED,
        "limits": [
            "Students who moved to another college count as not returned here. See At another college.",
            "Spring and summer starters have less time to come back than fall starters, which pulls the rate down.",
            "In the practice data, some students with classes here in their second year are marked as not "
            "returned, so the rate may read low.",
            NEWEST_CLASS,
        ],
    },
    "persistence": {
        "name": "At another college",
        "pdp_name": "Persistence",
        "what": "Enrolled at a different college by the second academic year, or earned a credential there.",
        "how": "Students enrolled at, or with a credential from, another college, out of the entering class.",
        "who": EVERYONE_WHO_ENTERED,
        "limits": [
            "In PDP, persistence means other colleges only. It is not the same as still enrolled anywhere.",
            "A student can count in both Returned here and At another college, so the two rates can't be added.",
            "In the practice data, some students with classes at another college are marked as not "
            "persisting, so the rate may read low.",
            NEWEST_CLASS,
        ],
    },
    "gateway_math": {
        "name": "Gateway math",
        "pdp_name": "Gateway math completion",
        "what": "Passed the first required college level math course in the first academic year.",
        "how": "Students who passed (a grade of 1.0 or higher, or a pass), out of students required to take it.",
        "who": "Students the college marked as required to take college level math when they entered. "
        "Students marked as not required are outside the measure.",
        "limits": [
            "A required student who never took the course counts as not passing.",
            "Students whose requirement or result is unknown are left out of the count.",
            GATEWAY_UNKNOWN_ATTEMPT,
            GATEWAY_NOT_MAPPED,
        ],
    },
    "gateway_english": {
        "name": "Gateway English",
        "pdp_name": "Gateway English completion",
        "what": "Passed the first required college level English course in the first academic year.",
        "how": "Students who passed (a grade of 1.0 or higher, or a pass), out of students required to take it.",
        "who": "Students the college marked as required to take college level English when they entered. "
        "Students marked as not required are outside the measure.",
        "limits": [
            "A required student who never took the course counts as not passing.",
            "Students whose requirement or result is unknown are left out of the count.",
            GATEWAY_UNKNOWN_ATTEMPT,
            GATEWAY_NOT_MAPPED,
        ],
    },
    "federal_retention": {
        "name": "Back next fall",
        "pdp_name": "Fall to fall retention (federal)",
        "what": "Enrolled at this college in the fall term after the first academic year.",
        "how": "Students who took a course here that fall, out of the entering class.",
        "who": EVERYONE_WHO_ENTERED,
        "limits": [
            "This is not the PDP retention flag (Returned here), which counts any term of the next year and credentials, so it reads lower.",
            "IPEDS counts first time students only. Whether to do the same here is still open, so every enrollment type is counted for now.",
            "A credential earned before next fall doesn't count as retained yet. That rule is still open.",
            NEWEST_CLASS,
        ],
    },
    "dfw_rate": {
        "name": "DFW rate",
        "pdp_name": "DFW rate",
        "what": "The share of final grades that were a D, an F or a withdrawal.",
        "how": "D, F and W grades, out of every final grade the entering class got here, in any term.",
        "who": "Every final grade of the students who entered that year. One student finishing one course counts once.",
        "limits": [
            "F is an F or a numeric grade under 0.7. D is 0.7 to under 2.0, so a C minus counts. W is a withdrawal.",
            "Incomplete, audit, missing and other grades aren't final, so they are left out.",
        ],
    },
    "credit_completion": {
        "name": "Credit completion",
        "pdp_name": "Credit completion ratio",
        "what": "On average, the share of attempted credits that students earned in their first academic year.",
        "how": "Each student's year 1 credits earned divided by credits attempted, averaged over the students.",
        "who": "First time and transfer in students who attempted at least one credit. Readmitted and continuing "
        "students are outside the measure.",
        "limits": [
            "Students with an unknown enrollment type or full or part time status are left out.",
            "A ratio above 1 (more earned than attempted) is counted as 1.",
        ],
    },
    "credit_milestones": {
        "name": "Credit milestones",
        "pdp_name": "Credit accumulation (12, 24, 30 credits)",
        "what": "How many students earned at least 12, 24 or 30 credits in their first academic year.",
        "how": "Students at or above each milestone, out of students whose year 1 credits are known.",
        "who": EVERYONE_WHO_ENTERED,
        "limits": ["Students with blank year 1 credits are left out and counted apart."],
    },
    "student_paths": {
        "name": "Student paths",
        "pdp_name": "Term enrollment status",
        "what": "Where each entering student is in each fall or spring term after they start.",
        "how": "Enrolled here: took a course here that term. Credential: not here, but earned a credential here in an "
        "earlier year. At another college: neither, but enrolled at another college. Stopped out: no record that term.",
        "who": EVERYONE_WHO_ENTERED,
        "limits": [
            "These come from term records, so they can differ from the retention numbers.",
            "Students whose starting term is unknown can't be followed, so they are left out and counted apart.",
            NEWEST_CLASS,
        ],
    },
}

# Where each practice-data caveat comes from, by row id in data/quality/findings.csv. For reviewers, not shown to staff.
FINDINGS: dict[str, list[str]] = {
    "retention": ["N15"],
    "persistence": ["3"],
    "gateway_math": ["N1"],
    "gateway_english": ["N1"],
}


# What each school calls a metric, by definition key. Empty until FMU and Benedict say; then the PDP name is kept
# as pdp_name and the local one shown as name. The school comes from UNCF_SCHOOL (fmu or benedict).
LOCAL_NAMES: dict[str, dict[str, str]] = {
    "fmu": {},
    "benedict": {},
}


def school() -> str | None:
    """The school this deployment serves, from UNCF_SCHOOL, or None for the PDP names."""
    value = os.environ.get("UNCF_SCHOOL", "").strip().lower()
    return value if value in LOCAL_NAMES else None


def definition_for(measure: str) -> Definition:
    """The definition for one measure, with the school's own name when it has one. KeyError if there is none."""
    definition = {**DEFINITIONS[measure], "limits": list(DEFINITIONS[measure]["limits"])}
    local = LOCAL_NAMES.get(school() or "", {}).get(measure)
    return {**definition, "name": local} if local else definition


def all_definitions() -> dict[str, Definition]:
    """Every definition, with the school's own names applied."""
    return {key: definition_for(key) for key in DEFINITIONS}
