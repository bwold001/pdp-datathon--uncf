// The real answer from GET /uncf/definitions: the shared dictionary in uncf/definitions.py, saved for stories.
// Regenerate it from that file if the wording changes; don't edit it here.
import type { DefinitionsResponse } from "./pdp-key-terms";

export const pdpDefinitions: DefinitionsResponse = {
  "definitions": {
    "retention": {
      "name": "Returned here",
      "pdp_name": "Retention",
      "what": "Enrolled at this college again in the next academic year, or earned a credential here by then.",
      "how": "Students who returned or earned a credential here, out of the entering class.",
      "who": "Everyone who entered that year: every start term (fall, winter, spring and summer) and every enrollment type (first time, transfer in and readmitted).",
      "limits": [
        "Students who moved to another college count as not returned here. See At another college.",
        "Spring and summer starters have less time to come back than fall starters, which pulls the rate down.",
        "In the practice data, some students with classes here in their second year are marked as not returned, so the rate may read low.",
        "The newest entering class may not have its full second year in the data yet, so its rate can still change."
      ]
    },
    "persistence": {
      "name": "At another college",
      "pdp_name": "Persistence",
      "what": "Enrolled at a different college by the second academic year, or earned a credential there.",
      "how": "Students enrolled at, or with a credential from, another college, out of the entering class.",
      "who": "Everyone who entered that year: every start term (fall, winter, spring and summer) and every enrollment type (first time, transfer in and readmitted).",
      "limits": [
        "In PDP, persistence means other colleges only. It is not the same as still enrolled anywhere.",
        "A student can count in both Returned here and At another college, so the two rates can't be added.",
        "In the practice data, some students with classes at another college are marked as not persisting, so the rate may read low.",
        "The newest entering class may not have its full second year in the data yet, so its rate can still change."
      ]
    },
    "gateway_math": {
      "name": "Gateway math",
      "pdp_name": "Gateway math completion",
      "what": "Passed the first required college level math course in the first academic year.",
      "how": "Students who passed (a grade of 1.0 or higher, or a pass), out of students required to take it.",
      "who": "Students the college marked as required to take college level math when they entered. Students marked as not required are outside the measure.",
      "limits": [
        "A required student who never took the course counts as not passing.",
        "Students whose requirement or result is unknown are left out of the count.",
        "In the practice data, many students with an unknown attempt are recorded as not passing, which lowers the rate.",
        "Each college chooses its gateway courses. Until they are mapped in the data, this shows Not reported."
      ]
    },
    "gateway_english": {
      "name": "Gateway English",
      "pdp_name": "Gateway English completion",
      "what": "Passed the first required college level English course in the first academic year.",
      "how": "Students who passed (a grade of 1.0 or higher, or a pass), out of students required to take it.",
      "who": "Students the college marked as required to take college level English when they entered. Students marked as not required are outside the measure.",
      "limits": [
        "A required student who never took the course counts as not passing.",
        "Students whose requirement or result is unknown are left out of the count.",
        "In the practice data, many students with an unknown attempt are recorded as not passing, which lowers the rate.",
        "Each college chooses its gateway courses. Until they are mapped in the data, this shows Not reported."
      ]
    }
  }
};
