// Real answers from GET /uncf/gateway on the synthetic sample data (pdp.sqlite), saved for stories and tests before
// the API moved to measures/ (#36). Their retention is fall to fall, which is now retention_type=federal. Regenerate
// them from the running API (measures/breakdowns/gateway_courses.py); don't edit the numbers by hand.
import type { GatewayResponse } from "./gateway-data";

/** 2023-24, every student who entered. */
export const gateway2023: GatewayResponse = {
  "meta": {
    "cohort": "2023-24",
    "filters": {},
    "provisional": false,
    "flagged": true,
    "retention_term": "Fall 2024",
    "retention_observed": true,
    "first_term": null,
    "min_pair_students": 10,
    "min_students": 10,
    "source": "PDP analysis-ready cohort and course files (synthetic sample)",
    "loaded_at": "2026-11-10T06:18:59"
  },
  "status": "ok",
  "students": 2580,
  "cohort_retention": {
    "students": 2580,
    "retained": 1074,
    "rate": 0.4163
  },
  "courses": [
    {
      "course": "ENG 101",
      "name": "ENG-101",
      "subject": "E",
      "students": 380,
      "passed": 277,
      "df": 76,
      "w": 27,
      "other": 14,
      "retained_if_passed": {
        "students": 277,
        "retained": 211,
        "rate": 0.7617
      },
      "retained_if_not_passed": {
        "students": 103,
        "retained": 35,
        "rate": 0.3398
      }
    },
    {
      "course": "ENGL 101",
      "name": "ENGLISH COMPOSITION I",
      "subject": "E",
      "students": 63,
      "passed": 45,
      "df": 10,
      "w": 8,
      "other": 0,
      "retained_if_passed": {
        "students": 45,
        "retained": 33,
        "rate": 0.7333
      },
      "retained_if_not_passed": {
        "students": 18,
        "retained": 5,
        "rate": 0.2778
      }
    },
    {
      "course": "ENG 121",
      "name": "ENGLISH COMPOSITION I",
      "subject": "E",
      "students": 51,
      "passed": 36,
      "df": 8,
      "w": 7,
      "other": null,
      "retained_if_passed": {
        "students": 36,
        "retained": 31,
        "rate": 0.8611
      },
      "retained_if_not_passed": {
        "students": 15,
        "retained": 5,
        "rate": 0.3333
      }
    },
    {
      "course": "ENG 111",
      "name": "COLLEGE COMPOSITION I",
      "subject": "E",
      "students": 36,
      "passed": 27,
      "df": 4,
      "w": 5,
      "other": null,
      "retained_if_passed": {
        "students": 27,
        "retained": 3,
        "rate": 0.1111
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "ENGL 112",
      "name": "COMPOSITION I",
      "subject": "E",
      "students": 22,
      "passed": 22,
      "df": 0,
      "w": 0,
      "other": 0,
      "retained_if_passed": {
        "students": 22,
        "retained": 9,
        "rate": 0.4091
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "ENGL 1110",
      "name": "COMPOSITION I",
      "subject": "E",
      "students": 21,
      "passed": 15,
      "df": 6,
      "w": 0,
      "other": 0,
      "retained_if_passed": {
        "students": 15,
        "retained": 5,
        "rate": 0.3333
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "ENGL 121",
      "name": "COLLEGE COMPOSITION",
      "subject": "E",
      "students": 21,
      "passed": 21,
      "df": 0,
      "w": 0,
      "other": 0,
      "retained_if_passed": {
        "students": 21,
        "retained": 16,
        "rate": 0.7619
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "ENGL 161",
      "name": "COLLEGE COMPOSITION I",
      "subject": "E",
      "students": 18,
      "passed": 12,
      "df": 5,
      "w": 1,
      "other": 0,
      "retained_if_passed": {
        "students": 12,
        "retained": 11,
        "rate": 0.9167
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "ENG 102",
      "name": "FIRST-YEAR COMPOSITION",
      "subject": "E",
      "students": 17,
      "passed": 15,
      "df": 2,
      "w": 0,
      "other": 0,
      "retained_if_passed": {
        "students": 15,
        "retained": 11,
        "rate": 0.7333
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "INRW 385",
      "name": "INTEGRATED READING AND WRITING",
      "subject": "E",
      "students": 10,
      "passed": 9,
      "df": 1,
      "w": 0,
      "other": null,
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "MAT 152",
      "name": "QUANTITATIVE REASONING",
      "subject": "M",
      "students": 56,
      "passed": 39,
      "df": 13,
      "w": 4,
      "other": 0,
      "retained_if_passed": {
        "students": 39,
        "retained": 29,
        "rate": 0.7436
      },
      "retained_if_not_passed": {
        "students": 17,
        "retained": 3,
        "rate": 0.1765
      }
    },
    {
      "course": "MTH 165",
      "name": "ELEMENTARY STATISTICS",
      "subject": "M",
      "students": 23,
      "passed": 14,
      "df": 4,
      "w": 5,
      "other": 0,
      "retained_if_passed": {
        "students": 14,
        "retained": 12,
        "rate": 0.8571
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "MATH 103",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 20,
      "passed": 10,
      "df": 7,
      "w": 3,
      "other": 0,
      "retained_if_passed": {
        "students": 10,
        "retained": 8,
        "rate": 0.8
      },
      "retained_if_not_passed": {
        "students": 10,
        "retained": 4,
        "rate": 0.4
      }
    },
    {
      "course": "MTH 103",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 17,
      "passed": 9,
      "df": 2,
      "w": 6,
      "other": 0,
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "MAT 162",
      "name": "STATISTICAL REASONING",
      "subject": "M",
      "students": 14,
      "passed": 7,
      "df": 5,
      "w": 2,
      "other": 0,
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "MATH 120",
      "name": "MATH-120",
      "subject": "M",
      "students": 14,
      "passed": 10,
      "df": 4,
      "w": 0,
      "other": null,
      "retained_if_passed": {
        "students": 10,
        "retained": 8,
        "rate": 0.8
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "MTH 101",
      "name": "QUANTITATIVE LITERACY",
      "subject": "M",
      "students": 14,
      "passed": 11,
      "df": 3,
      "w": 0,
      "other": 0,
      "retained_if_passed": {
        "students": 11,
        "retained": 6,
        "rate": 0.5455
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "MATH 202",
      "name": "INTRODUCTION TO STATISTICS",
      "subject": "M",
      "students": 13,
      "passed": 6,
      "df": 4,
      "w": 3,
      "other": 0,
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "MTH 152",
      "name": "STATISTICS (MA)",
      "subject": "M",
      "students": 13,
      "passed": 9,
      "df": 3,
      "w": 1,
      "other": 0,
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "MTH 107",
      "name": "BASIC STATISTICS",
      "subject": "M",
      "students": 12,
      "passed": 8,
      "df": 3,
      "w": 1,
      "other": null,
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "MTH 140",
      "name": "PRECALCULUS",
      "subject": "M",
      "students": 12,
      "passed": 8,
      "df": 2,
      "w": 2,
      "other": 0,
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "MATH 116",
      "name": "MATH-116",
      "subject": "M",
      "students": 11,
      "passed": 4,
      "df": 7,
      "w": 0,
      "other": null,
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "MATH 130",
      "name": "INTRODUCTION TO STATISTICS",
      "subject": "M",
      "students": 11,
      "passed": 7,
      "df": 2,
      "w": 2,
      "other": 0,
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "MTH 161",
      "name": "PRECALCULUS I",
      "subject": "M",
      "students": 11,
      "passed": 7,
      "df": 0,
      "w": 4,
      "other": null,
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "MAT 151",
      "name": "COLLEGE ALGEBRA/FUNCTIONS",
      "subject": "M",
      "students": 10,
      "passed": 10,
      "df": 0,
      "w": 0,
      "other": 0,
      "retained_if_passed": {
        "students": 10,
        "retained": 5,
        "rate": 0.5
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "MATH 104B",
      "name": "MATH-104B",
      "subject": "M",
      "students": 10,
      "passed": 5,
      "df": 5,
      "w": 0,
      "other": null,
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "MTH 129",
      "name": "PRECALCULUS I",
      "subject": "M",
      "students": 10,
      "passed": 7,
      "df": 3,
      "w": 0,
      "other": 0,
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    }
  ],
  "hidden_courses": 86,
  "pairs": [
    {
      "courses": [
        "ENG 111",
        "SDV 101"
      ],
      "students": 13,
      "retained": 1,
      "rate": 0.0769,
      "gap": -33.9
    },
    {
      "courses": [
        "ENG 111",
        "MTH 161"
      ],
      "students": 11,
      "retained": 1,
      "rate": 0.0909,
      "gap": -32.5
    },
    {
      "courses": [
        "ACC 201",
        "COM 101"
      ],
      "students": 10,
      "retained": 4,
      "rate": 0.4,
      "gap": -1.6
    }
  ],
  "pairs_considered": 61
};

/** 2023-24, Fall starters: their first term has a name. */
export const gatewayFall2023: GatewayResponse = {
  "meta": {
    "cohort": "2023-24",
    "filters": {
      "cohort_term": "Fall"
    },
    "provisional": false,
    "flagged": true,
    "retention_term": "Fall 2024",
    "retention_observed": true,
    "first_term": "Fall 2023",
    "min_pair_students": 10,
    "min_students": 10,
    "source": "PDP analysis-ready cohort and course files (synthetic sample)",
    "loaded_at": "2026-11-10T06:18:59"
  },
  "status": "ok",
  "students": 1584,
  "cohort_retention": {
    "students": 1584,
    "retained": 699,
    "rate": 0.4413
  },
  "courses": [
    {
      "course": "ENG 101",
      "name": "ENG-101",
      "subject": "E",
      "students": 316,
      "passed": 222,
      "df": 71,
      "w": 23,
      "other": 12,
      "retained_if_passed": {
        "students": 222,
        "retained": 168,
        "rate": 0.7568
      },
      "retained_if_not_passed": {
        "students": 94,
        "retained": 32,
        "rate": 0.3404
      }
    },
    {
      "course": "ENG 121",
      "name": "ENGLISH COMPOSITION I",
      "subject": "E",
      "students": 51,
      "passed": 36,
      "df": 8,
      "w": 7,
      "other": null,
      "retained_if_passed": {
        "students": 36,
        "retained": 31,
        "rate": 0.8611
      },
      "retained_if_not_passed": {
        "students": 15,
        "retained": 5,
        "rate": 0.3333
      }
    },
    {
      "course": "ENGL 101",
      "name": "ENGLISH COMPOSITION I",
      "subject": "E",
      "students": 45,
      "passed": 31,
      "df": 9,
      "w": 5,
      "other": 0,
      "retained_if_passed": {
        "students": 31,
        "retained": 22,
        "rate": 0.7097
      },
      "retained_if_not_passed": {
        "students": 14,
        "retained": 5,
        "rate": 0.3571
      }
    },
    {
      "course": "ENG 111",
      "name": "COLLEGE COMPOSITION I",
      "subject": "E",
      "students": 27,
      "passed": 20,
      "df": 3,
      "w": 4,
      "other": null,
      "retained_if_passed": {
        "students": 20,
        "retained": 1,
        "rate": 0.05
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "ENGL 112",
      "name": "COMPOSITION I",
      "subject": "E",
      "students": 20,
      "passed": 20,
      "df": 0,
      "w": 0,
      "other": 0,
      "retained_if_passed": {
        "students": 20,
        "retained": 7,
        "rate": 0.35
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "ENGL 1110",
      "name": "COMPOSITION I",
      "subject": "E",
      "students": 19,
      "passed": 14,
      "df": 5,
      "w": 0,
      "other": 0,
      "retained_if_passed": {
        "students": 14,
        "retained": 5,
        "rate": 0.3571
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "ENGL 121",
      "name": "COLLEGE COMPOSITION",
      "subject": "E",
      "students": 17,
      "passed": 17,
      "df": 0,
      "w": 0,
      "other": 0,
      "retained_if_passed": {
        "students": 17,
        "retained": 13,
        "rate": 0.7647
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "ENGL 161",
      "name": "COLLEGE COMPOSITION I",
      "subject": "E",
      "students": 17,
      "passed": 11,
      "df": 5,
      "w": 1,
      "other": 0,
      "retained_if_passed": {
        "students": 11,
        "retained": 10,
        "rate": 0.9091
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "ENG 102",
      "name": "FIRST-YEAR COMPOSITION",
      "subject": "E",
      "students": 14,
      "passed": 13,
      "df": 1,
      "w": 0,
      "other": 0,
      "retained_if_passed": {
        "students": 13,
        "retained": 11,
        "rate": 0.8462
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "MAT 152",
      "name": "QUANTITATIVE REASONING",
      "subject": "M",
      "students": 39,
      "passed": 25,
      "df": 10,
      "w": 4,
      "other": 0,
      "retained_if_passed": {
        "students": 25,
        "retained": 20,
        "rate": 0.8
      },
      "retained_if_not_passed": {
        "students": 14,
        "retained": 3,
        "rate": 0.2143
      }
    },
    {
      "course": "MTH 165",
      "name": "ELEMENTARY STATISTICS",
      "subject": "M",
      "students": 19,
      "passed": 13,
      "df": 1,
      "w": 5,
      "other": 0,
      "retained_if_passed": {
        "students": 13,
        "retained": 12,
        "rate": 0.9231
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "MTH 103",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 15,
      "passed": 8,
      "df": 2,
      "w": 5,
      "other": 0,
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "MATH 103",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 13,
      "passed": 8,
      "df": 4,
      "w": 1,
      "other": 0,
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "MATH 120",
      "name": "MATH-120",
      "subject": "M",
      "students": 13,
      "passed": 9,
      "df": 4,
      "w": 0,
      "other": null,
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "MTH 152",
      "name": "STATISTICS (MA)",
      "subject": "M",
      "students": 12,
      "passed": 8,
      "df": 3,
      "w": 1,
      "other": 0,
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "MATH 202",
      "name": "INTRODUCTION TO STATISTICS",
      "subject": "M",
      "students": 11,
      "passed": 5,
      "df": 4,
      "w": 2,
      "other": 0,
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "MTH 101",
      "name": "QUANTITATIVE LITERACY",
      "subject": "M",
      "students": 11,
      "passed": 8,
      "df": 3,
      "w": 0,
      "other": 0,
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "MTH 140",
      "name": "PRECALCULUS",
      "subject": "M",
      "students": 10,
      "passed": 8,
      "df": 1,
      "w": 1,
      "other": 0,
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "MTH 161",
      "name": "PRECALCULUS I",
      "subject": "M",
      "students": 10,
      "passed": 6,
      "df": 0,
      "w": 4,
      "other": null,
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    }
  ],
  "hidden_courses": 85,
  "pairs": [
    {
      "courses": [
        "ENG 111",
        "SDV 101"
      ],
      "students": 10,
      "retained": 0,
      "rate": 0.0,
      "gap": -44.1
    },
    {
      "courses": [
        "ENG 111",
        "MTH 161"
      ],
      "students": 10,
      "retained": 1,
      "rate": 0.1,
      "gap": -34.1
    },
    {
      "courses": [
        "MATH 126E",
        "MATH 26"
      ],
      "students": 12,
      "retained": 5,
      "rate": 0.4167,
      "gap": -2.5
    }
  ],
  "pairs_considered": 43
};

/** 2024-25: next fall (Fall 2025) is only partly in the data. */
export const gateway2024: GatewayResponse = {
  "meta": {
    "cohort": "2024-25",
    "filters": {},
    "provisional": true,
    "flagged": true,
    "retention_term": "Fall 2025",
    "retention_observed": true,
    "first_term": null,
    "min_pair_students": 10,
    "min_students": 10,
    "source": "PDP analysis-ready cohort and course files (synthetic sample)",
    "loaded_at": "2026-11-10T06:18:59"
  },
  "status": "ok",
  "students": 2612,
  "cohort_retention": {
    "students": 2612,
    "retained": 774,
    "rate": 0.2963
  },
  "courses": [
    {
      "course": "ENG 101",
      "name": "COMPOSITION I",
      "subject": "E",
      "students": 362,
      "passed": 272,
      "df": 72,
      "w": 18,
      "other": 24,
      "retained_if_passed": {
        "students": 272,
        "retained": 175,
        "rate": 0.6434
      },
      "retained_if_not_passed": {
        "students": 90,
        "retained": 28,
        "rate": 0.3111
      }
    },
    {
      "course": "ENGL 101",
      "name": "ENGLISH COMPOSITION I",
      "subject": "E",
      "students": 76,
      "passed": 54,
      "df": 18,
      "w": 4,
      "other": 0,
      "retained_if_passed": {
        "students": 54,
        "retained": 40,
        "rate": 0.7407
      },
      "retained_if_not_passed": {
        "students": 22,
        "retained": 3,
        "rate": 0.1364
      }
    },
    {
      "course": "ENGL 121",
      "name": "COLLEGE COMPOSITION",
      "subject": "E",
      "students": 28,
      "passed": 28,
      "df": 0,
      "w": 0,
      "other": 0,
      "retained_if_passed": {
        "students": 28,
        "retained": 24,
        "rate": 0.8571
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "ENGL 100",
      "name": "COMPOSITION I",
      "subject": "E",
      "students": 23,
      "passed": 21,
      "df": 2,
      "w": 0,
      "other": 0,
      "retained_if_passed": {
        "students": 21,
        "retained": 10,
        "rate": 0.4762
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "ENG 102",
      "name": "FIRST-YEAR COMPOSITION",
      "subject": "E",
      "students": 19,
      "passed": 16,
      "df": 3,
      "w": 0,
      "other": null,
      "retained_if_passed": {
        "students": 16,
        "retained": 0,
        "rate": 0.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "ENGL 161",
      "name": "\"COLLEGE COMPOSITION I\"",
      "subject": "E",
      "students": 19,
      "passed": 13,
      "df": 4,
      "w": 2,
      "other": 0,
      "retained_if_passed": {
        "students": 13,
        "retained": 10,
        "rate": 0.7692
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "ENG 111",
      "name": "COLLEGE COMPOSITION I",
      "subject": "E",
      "students": 17,
      "passed": 12,
      "df": 3,
      "w": 2,
      "other": null,
      "retained_if_passed": {
        "students": 12,
        "retained": 4,
        "rate": 0.3333
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "ENGL 1110",
      "name": "COMPOSITION I",
      "subject": "E",
      "students": 17,
      "passed": 8,
      "df": 8,
      "w": 1,
      "other": 0,
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "ENGL 162",
      "name": "\"COLLEGE COMPOSITION II\"",
      "subject": "E",
      "students": 14,
      "passed": 11,
      "df": 1,
      "w": 2,
      "other": 0,
      "retained_if_passed": {
        "students": 11,
        "retained": 8,
        "rate": 0.7273
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "ENG 11103",
      "name": "COMPOSITION I",
      "subject": "E",
      "students": 11,
      "passed": 8,
      "df": 3,
      "w": 0,
      "other": 0,
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "MAT 152",
      "name": "QUANTITATIVE REASONING",
      "subject": "M",
      "students": 53,
      "passed": 35,
      "df": 16,
      "w": 2,
      "other": 0,
      "retained_if_passed": {
        "students": 35,
        "retained": 27,
        "rate": 0.7714
      },
      "retained_if_not_passed": {
        "students": 18,
        "retained": 2,
        "rate": 0.1111
      }
    },
    {
      "course": "MAT 162",
      "name": "STATISTICAL REASONING",
      "subject": "M",
      "students": 29,
      "passed": 18,
      "df": 8,
      "w": 3,
      "other": 0,
      "retained_if_passed": {
        "students": 18,
        "retained": 14,
        "rate": 0.7778
      },
      "retained_if_not_passed": {
        "students": 11,
        "retained": 5,
        "rate": 0.4545
      }
    },
    {
      "course": "MATH 116",
      "name": "MATH-116",
      "subject": "M",
      "students": 22,
      "passed": 13,
      "df": 7,
      "w": 2,
      "other": null,
      "retained_if_passed": {
        "students": 13,
        "retained": 11,
        "rate": 0.8462
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "MATH 130",
      "name": "INTRODUCTION TO STATISTICS",
      "subject": "M",
      "students": 18,
      "passed": 11,
      "df": 6,
      "w": 1,
      "other": 0,
      "retained_if_passed": {
        "students": 11,
        "retained": 5,
        "rate": 0.4545
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "MATH 103",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 17,
      "passed": 12,
      "df": 3,
      "w": 2,
      "other": 0,
      "retained_if_passed": {
        "students": 12,
        "retained": 9,
        "rate": 0.75
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "MATH 140",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 17,
      "passed": 12,
      "df": 4,
      "w": 1,
      "other": 0,
      "retained_if_passed": {
        "students": 12,
        "retained": 5,
        "rate": 0.4167
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "MTH 103",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 15,
      "passed": 9,
      "df": 2,
      "w": 4,
      "other": 0,
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "MATH 104B",
      "name": "MATH-104B",
      "subject": "M",
      "students": 13,
      "passed": 7,
      "df": 5,
      "w": 1,
      "other": null,
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "MATH 202",
      "name": "INTRODUCTION TO STATISTICS",
      "subject": "M",
      "students": 13,
      "passed": 10,
      "df": 0,
      "w": 3,
      "other": 0,
      "retained_if_passed": {
        "students": 10,
        "retained": 8,
        "rate": 0.8
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "MATH 150",
      "name": "PRE-CALCULUS",
      "subject": "M",
      "students": 12,
      "passed": 11,
      "df": 1,
      "w": 0,
      "other": 0,
      "retained_if_passed": {
        "students": 11,
        "retained": 5,
        "rate": 0.4545
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "MATH 314",
      "name": "COLLEGE ALGEBRA MATH PATHWAY",
      "subject": "M",
      "students": 12,
      "passed": 12,
      "df": 0,
      "w": 0,
      "other": null,
      "retained_if_passed": {
        "students": 12,
        "retained": 0,
        "rate": 0.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "MTH 165",
      "name": "ELEMENTARY STATISTICS",
      "subject": "M",
      "students": 12,
      "passed": 5,
      "df": 5,
      "w": 2,
      "other": 0,
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "MTHM 168",
      "name": "\"STATISTICS\"",
      "subject": "M",
      "students": 12,
      "passed": 7,
      "df": 2,
      "w": 3,
      "other": 0,
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "MTH 200",
      "name": "CALCULUS I",
      "subject": "M",
      "students": 11,
      "passed": 4,
      "df": 2,
      "w": 5,
      "other": 0,
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    },
    {
      "course": "MTH 101",
      "name": "QUANTITATIVE LITERACY",
      "subject": "M",
      "students": 10,
      "passed": 6,
      "df": 3,
      "w": 1,
      "other": 0,
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      }
    }
  ],
  "hidden_courses": 76,
  "pairs": [
    {
      "courses": [
        "ENGL 101",
        "MA 119"
      ],
      "students": 41,
      "retained": 0,
      "rate": 0.0,
      "gap": -29.6
    },
    {
      "courses": [
        "ENGL 101",
        "ST 100"
      ],
      "students": 22,
      "retained": 0,
      "rate": 0.0,
      "gap": -29.6
    },
    {
      "courses": [
        "ENGL 101",
        "SOCY 101"
      ],
      "students": 17,
      "retained": 0,
      "rate": 0.0,
      "gap": -29.6
    }
  ],
  "pairs_considered": 61
};

/** A filter combination with fewer than 10 students. */
export const gatewayTooFew: GatewayResponse = {
  "meta": {
    "cohort": "2023-24",
    "filters": {
      "gender": "M",
      "race": "Native Hawaiian or Other Pacific Islander"
    },
    "provisional": false,
    "flagged": true,
    "retention_term": "Fall 2024",
    "retention_observed": true,
    "first_term": "Fall 2023",
    "min_pair_students": 10,
    "min_students": 10,
    "source": "PDP analysis-ready cohort and course files (synthetic sample)",
    "loaded_at": "2026-11-10T06:18:59"
  },
  "status": "suppressed",
  "students": null,
  "cohort_retention": null,
  "courses": [],
  "hidden_courses": 0,
  "pairs": [],
  "pairs_considered": 0
};
