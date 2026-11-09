"""Plain-language definitions for each measure (#3). The Results API (#5) attaches one to every response.

Written for campus staff, not engineers. The shape matches the Explorer's MeasureDefinition in
playground/client_application/src/app/(app)/uncf/data.ts: name, pdp_name, what, how, who, limits.
Change the wording here only, so the Explorer, CSV export, insight card and chat all say the same thing.
"""
from __future__ import annotations

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
}

# Where each practice-data caveat comes from, by row id in data/quality/findings.csv. For reviewers, not shown to staff.
FINDINGS: dict[str, list[str]] = {
    "retention": ["N15"],
    "persistence": ["3"],
    "gateway_math": ["N1"],
    "gateway_english": ["N1"],
}


def definition_for(measure: str) -> Definition:
    """The definition for one measure. Raises KeyError for a measure with no definition yet."""
    return DEFINITIONS[measure]
