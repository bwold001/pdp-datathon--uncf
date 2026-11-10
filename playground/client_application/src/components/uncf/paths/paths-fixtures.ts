// Real answers from GET /uncf/student-paths on the synthetic sample data (pdp.sqlite), saved for stories and tests.
// Regenerate them with uncf/student_paths.py if the data or the endpoint changes; don't edit the numbers by hand.
import type { CohortOptions } from "@/components/uncf/layout/explorer-api";

import type { PathsResponse } from "./paths-data";

/** 2023-24, first-time Fall starters. */
export const fallStarters2023: PathsResponse = {
  "meta": {
    "cohort": "2023-24",
    "filters": {
      "cohort_term": "Fall"
    },
    "terms": {
      "entered": "Fall 2023",
      "next": "Spring 2024",
      "year2": "Fall 2024"
    },
    "provisional": false,
    "min_students": 10,
    "source": "PDP analysis-ready cohort and course files (synthetic sample)",
    "loaded_at": "2026-11-10T06:18:59"
  },
  "status": "ok",
  "students": 1114,
  "left_out": 0,
  "columns": {
    "next": {
      "here": 642,
      "elsewhere": 33,
      "anywhere": 675,
      "stopped": 439,
      "not_observed": 0
    },
    "year2": {
      "here": 522,
      "elsewhere": 64,
      "anywhere": 586,
      "stopped": 528,
      "not_observed": 0
    }
  },
  "moves": [
    {
      "from": "here",
      "to": "here",
      "students": 423
    },
    {
      "from": "here",
      "to": "elsewhere",
      "students": 26
    },
    {
      "from": "here",
      "to": "stopped",
      "students": 193
    },
    {
      "from": "elsewhere",
      "to": "here",
      "students": null
    },
    {
      "from": "elsewhere",
      "to": "elsewhere",
      "students": 23
    },
    {
      "from": "elsewhere",
      "to": "stopped",
      "students": null
    },
    {
      "from": "stopped",
      "to": "here",
      "students": 96
    },
    {
      "from": "stopped",
      "to": "elsewhere",
      "students": 15
    },
    {
      "from": "stopped",
      "to": "stopped",
      "students": 328
    }
  ],
  "transfers": {
    "students": 64,
    "four_year": 38,
    "two_year": 17,
    "other": null
  }
};

/** 2023-24, first-time students of every starting term. */
export const allStarters2023: PathsResponse = {
  "meta": {
    "cohort": "2023-24",
    "filters": {},
    "terms": null,
    "provisional": false,
    "min_students": 10,
    "source": "PDP analysis-ready cohort and course files (synthetic sample)",
    "loaded_at": "2026-11-10T06:18:59"
  },
  "status": "ok",
  "students": 1627,
  "left_out": 0,
  "columns": {
    "next": {
      "here": 867,
      "elsewhere": 92,
      "anywhere": 959,
      "stopped": 668,
      "not_observed": 0
    },
    "year2": {
      "here": 714,
      "elsewhere": 125,
      "anywhere": 839,
      "stopped": 788,
      "not_observed": 0
    }
  },
  "moves": [
    {
      "from": "here",
      "to": "here",
      "students": 584
    },
    {
      "from": "here",
      "to": "elsewhere",
      "students": 36
    },
    {
      "from": "here",
      "to": "stopped",
      "students": 247
    },
    {
      "from": "elsewhere",
      "to": "here",
      "students": null
    },
    {
      "from": "elsewhere",
      "to": "elsewhere",
      "students": 73
    },
    {
      "from": "elsewhere",
      "to": "stopped",
      "students": 13
    },
    {
      "from": "stopped",
      "to": "here",
      "students": 124
    },
    {
      "from": "stopped",
      "to": "elsewhere",
      "students": 16
    },
    {
      "from": "stopped",
      "to": "stopped",
      "students": 528
    }
  ],
  "transfers": {
    "students": 125,
    "four_year": 76,
    "two_year": 31,
    "other": 18
  }
};

/** 2024-25, first-time Fall starters: their second year is only partly in the data. */
export const fallStarters2024: PathsResponse = {
  "meta": {
    "cohort": "2024-25",
    "filters": {
      "cohort_term": "Fall"
    },
    "terms": {
      "entered": "Fall 2024",
      "next": "Spring 2025",
      "year2": "Fall 2025"
    },
    "provisional": true,
    "min_students": 10,
    "source": "PDP analysis-ready cohort and course files (synthetic sample)",
    "loaded_at": "2026-11-10T06:18:59"
  },
  "status": "ok",
  "students": 1080,
  "left_out": 0,
  "columns": {
    "next": {
      "here": 700,
      "elsewhere": 37,
      "anywhere": 737,
      "stopped": 343,
      "not_observed": 0
    },
    "year2": {
      "here": 376,
      "elsewhere": 96,
      "anywhere": 472,
      "stopped": 608,
      "not_observed": 0
    }
  },
  "moves": [
    {
      "from": "here",
      "to": "here",
      "students": 341
    },
    {
      "from": "here",
      "to": "elsewhere",
      "students": 50
    },
    {
      "from": "here",
      "to": "stopped",
      "students": 309
    },
    {
      "from": "elsewhere",
      "to": "here",
      "students": null
    },
    {
      "from": "elsewhere",
      "to": "elsewhere",
      "students": 28
    },
    {
      "from": "elsewhere",
      "to": "stopped",
      "students": null
    },
    {
      "from": "stopped",
      "to": "here",
      "students": 32
    },
    {
      "from": "stopped",
      "to": "elsewhere",
      "students": 18
    },
    {
      "from": "stopped",
      "to": "stopped",
      "students": 293
    }
  ],
  "transfers": {
    "students": 96,
    "four_year": 55,
    "two_year": 27,
    "other": 14
  }
};

/** A filter combination with fewer than 10 students: everything hidden. */
export const tooFewStudents: PathsResponse = {
  "meta": {
    "cohort": "2023-24",
    "filters": {
      "gender": "M",
      "race": "Native Hawaiian or Other Pacific Islander"
    },
    "terms": {
      "entered": "Fall 2023",
      "next": "Spring 2024",
      "year2": "Fall 2024"
    },
    "provisional": false,
    "min_students": 10,
    "source": "PDP analysis-ready cohort and course files (synthetic sample)",
    "loaded_at": "2026-11-10T06:18:59"
  },
  "status": "suppressed",
  "students": null,
  "left_out": null,
  "columns": null,
  "moves": null,
  "transfers": null
};

/** The cohort bar's counts for 2023-24. */
export const cohortOptions2023: CohortOptions = {
  "cohort": "2023-24",
  "cohorts": {
    "2021-22": 2504,
    "2022-23": 2617,
    "2023-24": 2580,
    "2024-25": 2612
  },
  "filters": {
    "cohort_term": {
      "Spring": 656,
      "Summer": 319,
      "Fall": 1584,
      "Winter": 21,
      "UNKNOWN": 0
    },
    "enrollment_intensity": {
      "Full-time": 1007,
      "UNKNOWN": 72,
      "Part-time": 1501
    },
    "pell": {
      "Y": 873,
      "N": 1496,
      "UNKNOWN": 211
    },
    "gender": {
      "P": 0,
      "F": 1397,
      "M": 1051,
      "X": 0,
      "UNKNOWN": 132
    },
    "race": {
      "Hispanic": 710,
      "Nonresident alien": 54,
      "Two or More Races": 73,
      "Native Hawaiian or Other Pacific Islander": null,
      "Asian": 196,
      "White": 1011,
      "American Indian or Alaska Native": 45,
      "Black or African American": 391,
      "UNKNOWN": 91
    },
    "age_band": {
      "Older than 24": 804,
      "> 20-24": 543,
      "UNKNOWN": 0,
      "20 and younger": 1233
    }
  },
  "min_students": 10,
  "source": "PDP analysis-ready cohort and course files (synthetic sample)",
  "loaded_at": "2026-11-10T06:18:59"
};
