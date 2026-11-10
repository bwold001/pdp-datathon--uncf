// Real answers from the shared API (GET /uncf/gateway) on the synthetic sample data (pdp.sqlite), saved for stories
// and tests with the queries the tab sends. Retention is the API's default (the PDP flag) unless the name says
// federal. Regenerate them from the running API (measures/breakdowns/gateway_courses.py); don't edit the numbers by hand.
import type { GatewayResponse } from "./gateway-data";

/** 2023-24, every student who entered. */
export const gateway2023: GatewayResponse = {
  "meta": {
    "cohort": "2023-24",
    "filters": {},
    "retention_type": "school",
    "provisional": false,
    "min_students": 10,
    "source": "PDP analysis-ready cohort and course files (synthetic sample)",
    "loaded_at": "2026-11-10T06:18:59",
    "flagged": true,
    "retention_term": "next academic year",
    "retention_observed": true,
    "first_term": null,
    "min_pair_students": 10
  },
  "status": "ok",
  "students": 2580,
  "cohort_retention": {
    "type": "school",
    "status": "ok",
    "retained": 1345,
    "students": 2580,
    "numerator": 1345,
    "denominator": 2580,
    "rate": 0.5213,
    "n_excluded": 0,
    "n_out_of_scope": 0
  },
  "courses": [
    {
      "course": "ENG 101",
      "name": "ENG-101",
      "subject": "E",
      "students": 380,
      "passed": 277,
      "d": 17,
      "f": 59,
      "df": 76,
      "w": 27,
      "other": 14,
      "shares": {
        "passed": 0.7289,
        "d": 0.0447,
        "f": 0.1553,
        "w": 0.0711
      },
      "retained_if_passed": {
        "students": 277,
        "retained": 218,
        "rate": 0.787
      },
      "retained_if_not_passed": {
        "students": 103,
        "retained": 39,
        "rate": 0.3786
      }
    },
    {
      "course": "ENGL 101",
      "name": "ENGLISH COMPOSITION I",
      "subject": "E",
      "students": 63,
      "passed": 45,
      "d": 5,
      "f": 5,
      "df": 10,
      "w": 8,
      "other": 0,
      "shares": {
        "passed": 0.7143,
        "d": 0.0794,
        "f": 0.0794,
        "w": 0.127
      },
      "retained_if_passed": {
        "students": 45,
        "retained": 35,
        "rate": 0.7778
      },
      "retained_if_not_passed": {
        "students": 18,
        "retained": 8,
        "rate": 0.4444
      }
    },
    {
      "course": "ENG 121",
      "name": "ENGLISH COMPOSITION I",
      "subject": "E",
      "students": 51,
      "passed": 36,
      "d": 0,
      "f": 8,
      "df": 8,
      "w": 7,
      "other": null,
      "shares": {
        "passed": 0.7059,
        "d": 0.0,
        "f": 0.1569,
        "w": 0.1373
      },
      "retained_if_passed": {
        "students": 36,
        "retained": 31,
        "rate": 0.8611
      },
      "retained_if_not_passed": {
        "students": 15,
        "retained": 6,
        "rate": 0.4
      }
    },
    {
      "course": "ENG 111",
      "name": "COLLEGE COMPOSITION I",
      "subject": "E",
      "students": 36,
      "passed": 27,
      "d": 1,
      "f": 3,
      "df": 4,
      "w": 5,
      "other": null,
      "shares": {
        "passed": 0.75,
        "d": 0.0278,
        "f": 0.0833,
        "w": 0.1389
      },
      "retained_if_passed": {
        "students": 27,
        "retained": 20,
        "rate": 0.7407
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
      "d": 0,
      "f": 0,
      "df": 0,
      "w": 0,
      "other": 0,
      "shares": {
        "passed": 1.0,
        "d": 0.0,
        "f": 0.0,
        "w": 0.0
      },
      "retained_if_passed": {
        "students": 22,
        "retained": 11,
        "rate": 0.5
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
      "d": 4,
      "f": 2,
      "df": 6,
      "w": 0,
      "other": 0,
      "shares": {
        "passed": 0.7143,
        "d": 0.1905,
        "f": 0.0952,
        "w": 0.0
      },
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
      "course": "ENGL 121",
      "name": "COLLEGE COMPOSITION",
      "subject": "E",
      "students": 21,
      "passed": 21,
      "d": 0,
      "f": 0,
      "df": 0,
      "w": 0,
      "other": 0,
      "shares": {
        "passed": 1.0,
        "d": 0.0,
        "f": 0.0,
        "w": 0.0
      },
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
      "d": 1,
      "f": 4,
      "df": 5,
      "w": 1,
      "other": 0,
      "shares": {
        "passed": 0.6667,
        "d": 0.0556,
        "f": 0.2222,
        "w": 0.0556
      },
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
      "d": 1,
      "f": 1,
      "df": 2,
      "w": 0,
      "other": 0,
      "shares": {
        "passed": 0.8824,
        "d": 0.0588,
        "f": 0.0588,
        "w": 0.0
      },
      "retained_if_passed": {
        "students": 15,
        "retained": 12,
        "rate": 0.8
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
      "d": 0,
      "f": 1,
      "df": 1,
      "w": 0,
      "other": null,
      "shares": {
        "passed": 0.9,
        "d": 0.0,
        "f": 0.1,
        "w": 0.0
      },
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
      "d": 0,
      "f": 13,
      "df": 13,
      "w": 4,
      "other": 0,
      "shares": {
        "passed": 0.6964,
        "d": 0.0,
        "f": 0.2321,
        "w": 0.0714
      },
      "retained_if_passed": {
        "students": 39,
        "retained": 28,
        "rate": 0.7179
      },
      "retained_if_not_passed": {
        "students": 17,
        "retained": 5,
        "rate": 0.2941
      }
    },
    {
      "course": "MTH 165",
      "name": "ELEMENTARY STATISTICS",
      "subject": "M",
      "students": 23,
      "passed": 14,
      "d": 2,
      "f": 2,
      "df": 4,
      "w": 5,
      "other": 0,
      "shares": {
        "passed": 0.6087,
        "d": 0.087,
        "f": 0.087,
        "w": 0.2174
      },
      "retained_if_passed": {
        "students": 14,
        "retained": 13,
        "rate": 0.9286
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
      "d": 1,
      "f": 6,
      "df": 7,
      "w": 3,
      "other": 0,
      "shares": {
        "passed": 0.5,
        "d": 0.05,
        "f": 0.3,
        "w": 0.15
      },
      "retained_if_passed": {
        "students": 10,
        "retained": 9,
        "rate": 0.9
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
      "d": 2,
      "f": 0,
      "df": 2,
      "w": 6,
      "other": 0,
      "shares": {
        "passed": 0.5294,
        "d": 0.1176,
        "f": 0.0,
        "w": 0.3529
      },
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
      "d": 0,
      "f": 5,
      "df": 5,
      "w": 2,
      "other": 0,
      "shares": {
        "passed": 0.5,
        "d": 0.0,
        "f": 0.3571,
        "w": 0.1429
      },
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
      "d": 2,
      "f": 2,
      "df": 4,
      "w": 0,
      "other": null,
      "shares": {
        "passed": 0.7143,
        "d": 0.1429,
        "f": 0.1429,
        "w": 0.0
      },
      "retained_if_passed": {
        "students": 10,
        "retained": 9,
        "rate": 0.9
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
      "d": 1,
      "f": 2,
      "df": 3,
      "w": 0,
      "other": 0,
      "shares": {
        "passed": 0.7857,
        "d": 0.0714,
        "f": 0.1429,
        "w": 0.0
      },
      "retained_if_passed": {
        "students": 11,
        "retained": 7,
        "rate": 0.6364
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
      "d": 2,
      "f": 2,
      "df": 4,
      "w": 3,
      "other": 0,
      "shares": {
        "passed": 0.4615,
        "d": 0.1538,
        "f": 0.1538,
        "w": 0.2308
      },
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
      "d": 0,
      "f": 3,
      "df": 3,
      "w": 1,
      "other": 0,
      "shares": {
        "passed": 0.6923,
        "d": 0.0,
        "f": 0.2308,
        "w": 0.0769
      },
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
      "d": 2,
      "f": 1,
      "df": 3,
      "w": 1,
      "other": null,
      "shares": {
        "passed": 0.6667,
        "d": 0.1667,
        "f": 0.0833,
        "w": 0.0833
      },
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
      "d": 1,
      "f": 1,
      "df": 2,
      "w": 2,
      "other": 0,
      "shares": {
        "passed": 0.6667,
        "d": 0.0833,
        "f": 0.0833,
        "w": 0.1667
      },
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
      "d": 4,
      "f": 3,
      "df": 7,
      "w": 0,
      "other": null,
      "shares": {
        "passed": 0.3636,
        "d": 0.3636,
        "f": 0.2727,
        "w": 0.0
      },
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
      "d": 1,
      "f": 1,
      "df": 2,
      "w": 2,
      "other": 0,
      "shares": {
        "passed": 0.6364,
        "d": 0.0909,
        "f": 0.0909,
        "w": 0.1818
      },
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
      "d": 0,
      "f": 0,
      "df": 0,
      "w": 4,
      "other": null,
      "shares": {
        "passed": 0.6364,
        "d": 0.0,
        "f": 0.0,
        "w": 0.3636
      },
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
      "d": 0,
      "f": 0,
      "df": 0,
      "w": 0,
      "other": 0,
      "shares": {
        "passed": 1.0,
        "d": 0.0,
        "f": 0.0,
        "w": 0.0
      },
      "retained_if_passed": {
        "students": 10,
        "retained": 6,
        "rate": 0.6
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
      "d": 2,
      "f": 3,
      "df": 5,
      "w": 0,
      "other": null,
      "shares": {
        "passed": 0.5,
        "d": 0.2,
        "f": 0.3,
        "w": 0.0
      },
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
      "d": 0,
      "f": 3,
      "df": 3,
      "w": 0,
      "other": 0,
      "shares": {
        "passed": 0.7,
        "d": 0.0,
        "f": 0.3,
        "w": 0.0
      },
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
  "left_out": 29,
  "pairs": [
    {
      "courses": [
        "ENG 111",
        "SDV 101"
      ],
      "students": 13,
      "retained": 6,
      "rate": 0.4615,
      "gap": -6.0
    },
    {
      "courses": [
        "ENG 101",
        "ENG 11"
      ],
      "students": 18,
      "retained": 9,
      "rate": 0.5,
      "gap": -2.1
    },
    {
      "courses": [
        "BIO 120",
        "SSC 100"
      ],
      "students": 14,
      "retained": 7,
      "rate": 0.5,
      "gap": -2.1
    }
  ],
  "pairs_considered": 61
};

/** 2023-24 with fall to fall retention (Retention: Back next fall). */
export const gatewayFederal2023: GatewayResponse = {
  "meta": {
    "cohort": "2023-24",
    "filters": {},
    "retention_type": "federal",
    "provisional": false,
    "min_students": 10,
    "source": "PDP analysis-ready cohort and course files (synthetic sample)",
    "loaded_at": "2026-11-10T06:18:59",
    "flagged": true,
    "retention_term": "Fall 2024",
    "retention_observed": true,
    "first_term": null,
    "min_pair_students": 10
  },
  "status": "ok",
  "students": 2580,
  "cohort_retention": {
    "type": "federal",
    "status": "ok",
    "retained": 1074,
    "students": 2580,
    "numerator": 1074,
    "denominator": 2580,
    "rate": 0.4163,
    "n_excluded": 0,
    "n_out_of_scope": 0
  },
  "courses": [
    {
      "course": "ENG 101",
      "name": "ENG-101",
      "subject": "E",
      "students": 380,
      "passed": 277,
      "d": 17,
      "f": 59,
      "df": 76,
      "w": 27,
      "other": 14,
      "shares": {
        "passed": 0.7289,
        "d": 0.0447,
        "f": 0.1553,
        "w": 0.0711
      },
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
      "d": 5,
      "f": 5,
      "df": 10,
      "w": 8,
      "other": 0,
      "shares": {
        "passed": 0.7143,
        "d": 0.0794,
        "f": 0.0794,
        "w": 0.127
      },
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
      "d": 0,
      "f": 8,
      "df": 8,
      "w": 7,
      "other": null,
      "shares": {
        "passed": 0.7059,
        "d": 0.0,
        "f": 0.1569,
        "w": 0.1373
      },
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
      "d": 1,
      "f": 3,
      "df": 4,
      "w": 5,
      "other": null,
      "shares": {
        "passed": 0.75,
        "d": 0.0278,
        "f": 0.0833,
        "w": 0.1389
      },
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
      "d": 0,
      "f": 0,
      "df": 0,
      "w": 0,
      "other": 0,
      "shares": {
        "passed": 1.0,
        "d": 0.0,
        "f": 0.0,
        "w": 0.0
      },
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
      "d": 4,
      "f": 2,
      "df": 6,
      "w": 0,
      "other": 0,
      "shares": {
        "passed": 0.7143,
        "d": 0.1905,
        "f": 0.0952,
        "w": 0.0
      },
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
      "d": 0,
      "f": 0,
      "df": 0,
      "w": 0,
      "other": 0,
      "shares": {
        "passed": 1.0,
        "d": 0.0,
        "f": 0.0,
        "w": 0.0
      },
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
      "d": 1,
      "f": 4,
      "df": 5,
      "w": 1,
      "other": 0,
      "shares": {
        "passed": 0.6667,
        "d": 0.0556,
        "f": 0.2222,
        "w": 0.0556
      },
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
      "d": 1,
      "f": 1,
      "df": 2,
      "w": 0,
      "other": 0,
      "shares": {
        "passed": 0.8824,
        "d": 0.0588,
        "f": 0.0588,
        "w": 0.0
      },
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
      "d": 0,
      "f": 1,
      "df": 1,
      "w": 0,
      "other": null,
      "shares": {
        "passed": 0.9,
        "d": 0.0,
        "f": 0.1,
        "w": 0.0
      },
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
      "d": 0,
      "f": 13,
      "df": 13,
      "w": 4,
      "other": 0,
      "shares": {
        "passed": 0.6964,
        "d": 0.0,
        "f": 0.2321,
        "w": 0.0714
      },
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
      "d": 2,
      "f": 2,
      "df": 4,
      "w": 5,
      "other": 0,
      "shares": {
        "passed": 0.6087,
        "d": 0.087,
        "f": 0.087,
        "w": 0.2174
      },
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
      "d": 1,
      "f": 6,
      "df": 7,
      "w": 3,
      "other": 0,
      "shares": {
        "passed": 0.5,
        "d": 0.05,
        "f": 0.3,
        "w": 0.15
      },
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
      "d": 2,
      "f": 0,
      "df": 2,
      "w": 6,
      "other": 0,
      "shares": {
        "passed": 0.5294,
        "d": 0.1176,
        "f": 0.0,
        "w": 0.3529
      },
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
      "d": 0,
      "f": 5,
      "df": 5,
      "w": 2,
      "other": 0,
      "shares": {
        "passed": 0.5,
        "d": 0.0,
        "f": 0.3571,
        "w": 0.1429
      },
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
      "d": 2,
      "f": 2,
      "df": 4,
      "w": 0,
      "other": null,
      "shares": {
        "passed": 0.7143,
        "d": 0.1429,
        "f": 0.1429,
        "w": 0.0
      },
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
      "d": 1,
      "f": 2,
      "df": 3,
      "w": 0,
      "other": 0,
      "shares": {
        "passed": 0.7857,
        "d": 0.0714,
        "f": 0.1429,
        "w": 0.0
      },
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
      "d": 2,
      "f": 2,
      "df": 4,
      "w": 3,
      "other": 0,
      "shares": {
        "passed": 0.4615,
        "d": 0.1538,
        "f": 0.1538,
        "w": 0.2308
      },
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
      "d": 0,
      "f": 3,
      "df": 3,
      "w": 1,
      "other": 0,
      "shares": {
        "passed": 0.6923,
        "d": 0.0,
        "f": 0.2308,
        "w": 0.0769
      },
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
      "d": 2,
      "f": 1,
      "df": 3,
      "w": 1,
      "other": null,
      "shares": {
        "passed": 0.6667,
        "d": 0.1667,
        "f": 0.0833,
        "w": 0.0833
      },
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
      "d": 1,
      "f": 1,
      "df": 2,
      "w": 2,
      "other": 0,
      "shares": {
        "passed": 0.6667,
        "d": 0.0833,
        "f": 0.0833,
        "w": 0.1667
      },
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
      "d": 4,
      "f": 3,
      "df": 7,
      "w": 0,
      "other": null,
      "shares": {
        "passed": 0.3636,
        "d": 0.3636,
        "f": 0.2727,
        "w": 0.0
      },
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
      "d": 1,
      "f": 1,
      "df": 2,
      "w": 2,
      "other": 0,
      "shares": {
        "passed": 0.6364,
        "d": 0.0909,
        "f": 0.0909,
        "w": 0.1818
      },
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
      "d": 0,
      "f": 0,
      "df": 0,
      "w": 4,
      "other": null,
      "shares": {
        "passed": 0.6364,
        "d": 0.0,
        "f": 0.0,
        "w": 0.3636
      },
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
      "d": 0,
      "f": 0,
      "df": 0,
      "w": 0,
      "other": 0,
      "shares": {
        "passed": 1.0,
        "d": 0.0,
        "f": 0.0,
        "w": 0.0
      },
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
      "d": 2,
      "f": 3,
      "df": 5,
      "w": 0,
      "other": null,
      "shares": {
        "passed": 0.5,
        "d": 0.2,
        "f": 0.3,
        "w": 0.0
      },
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
      "d": 0,
      "f": 3,
      "df": 3,
      "w": 0,
      "other": 0,
      "shares": {
        "passed": 0.7,
        "d": 0.0,
        "f": 0.3,
        "w": 0.0
      },
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
  "left_out": 29,
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
    "retention_type": "school",
    "provisional": false,
    "min_students": 10,
    "source": "PDP analysis-ready cohort and course files (synthetic sample)",
    "loaded_at": "2026-11-10T06:18:59",
    "flagged": true,
    "retention_term": "next academic year",
    "retention_observed": true,
    "first_term": "Fall 2023",
    "min_pair_students": 10
  },
  "status": "ok",
  "students": 1584,
  "cohort_retention": {
    "type": "school",
    "status": "ok",
    "retained": 913,
    "students": 1584,
    "numerator": 913,
    "denominator": 1584,
    "rate": 0.5764,
    "n_excluded": 0,
    "n_out_of_scope": 0
  },
  "courses": [
    {
      "course": "ENG 101",
      "name": "ENG-101",
      "subject": "E",
      "students": 316,
      "passed": 222,
      "d": 15,
      "f": 56,
      "df": 71,
      "w": 23,
      "other": 12,
      "shares": {
        "passed": 0.7025,
        "d": 0.0475,
        "f": 0.1772,
        "w": 0.0728
      },
      "retained_if_passed": {
        "students": 222,
        "retained": 180,
        "rate": 0.8108
      },
      "retained_if_not_passed": {
        "students": 94,
        "retained": 36,
        "rate": 0.383
      }
    },
    {
      "course": "ENG 121",
      "name": "ENGLISH COMPOSITION I",
      "subject": "E",
      "students": 51,
      "passed": 36,
      "d": 0,
      "f": 8,
      "df": 8,
      "w": 7,
      "other": null,
      "shares": {
        "passed": 0.7059,
        "d": 0.0,
        "f": 0.1569,
        "w": 0.1373
      },
      "retained_if_passed": {
        "students": 36,
        "retained": 31,
        "rate": 0.8611
      },
      "retained_if_not_passed": {
        "students": 15,
        "retained": 6,
        "rate": 0.4
      }
    },
    {
      "course": "ENGL 101",
      "name": "ENGLISH COMPOSITION I",
      "subject": "E",
      "students": 45,
      "passed": 31,
      "d": 5,
      "f": 4,
      "df": 9,
      "w": 5,
      "other": 0,
      "shares": {
        "passed": 0.6889,
        "d": 0.1111,
        "f": 0.0889,
        "w": 0.1111
      },
      "retained_if_passed": {
        "students": 31,
        "retained": 25,
        "rate": 0.8065
      },
      "retained_if_not_passed": {
        "students": 14,
        "retained": 7,
        "rate": 0.5
      }
    },
    {
      "course": "ENG 111",
      "name": "COLLEGE COMPOSITION I",
      "subject": "E",
      "students": 27,
      "passed": 20,
      "d": 0,
      "f": 3,
      "df": 3,
      "w": 4,
      "other": null,
      "shares": {
        "passed": 0.7407,
        "d": 0.0,
        "f": 0.1111,
        "w": 0.1481
      },
      "retained_if_passed": {
        "students": 20,
        "retained": 14,
        "rate": 0.7
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
      "d": 0,
      "f": 0,
      "df": 0,
      "w": 0,
      "other": 0,
      "shares": {
        "passed": 1.0,
        "d": 0.0,
        "f": 0.0,
        "w": 0.0
      },
      "retained_if_passed": {
        "students": 20,
        "retained": 9,
        "rate": 0.45
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
      "d": 4,
      "f": 1,
      "df": 5,
      "w": 0,
      "other": 0,
      "shares": {
        "passed": 0.7368,
        "d": 0.2105,
        "f": 0.0526,
        "w": 0.0
      },
      "retained_if_passed": {
        "students": 14,
        "retained": 11,
        "rate": 0.7857
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
      "d": 0,
      "f": 0,
      "df": 0,
      "w": 0,
      "other": 0,
      "shares": {
        "passed": 1.0,
        "d": 0.0,
        "f": 0.0,
        "w": 0.0
      },
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
      "d": 1,
      "f": 4,
      "df": 5,
      "w": 1,
      "other": 0,
      "shares": {
        "passed": 0.6471,
        "d": 0.0588,
        "f": 0.2353,
        "w": 0.0588
      },
      "retained_if_passed": {
        "students": 11,
        "retained": 11,
        "rate": 1.0
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
      "d": 1,
      "f": 0,
      "df": 1,
      "w": 0,
      "other": 0,
      "shares": {
        "passed": 0.9286,
        "d": 0.0714,
        "f": 0.0,
        "w": 0.0
      },
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
      "course": "MAT 152",
      "name": "QUANTITATIVE REASONING",
      "subject": "M",
      "students": 39,
      "passed": 25,
      "d": 0,
      "f": 10,
      "df": 10,
      "w": 4,
      "other": 0,
      "shares": {
        "passed": 0.641,
        "d": 0.0,
        "f": 0.2564,
        "w": 0.1026
      },
      "retained_if_passed": {
        "students": 25,
        "retained": 21,
        "rate": 0.84
      },
      "retained_if_not_passed": {
        "students": 14,
        "retained": 5,
        "rate": 0.3571
      }
    },
    {
      "course": "MTH 165",
      "name": "ELEMENTARY STATISTICS",
      "subject": "M",
      "students": 19,
      "passed": 13,
      "d": 0,
      "f": 1,
      "df": 1,
      "w": 5,
      "other": 0,
      "shares": {
        "passed": 0.6842,
        "d": 0.0,
        "f": 0.0526,
        "w": 0.2632
      },
      "retained_if_passed": {
        "students": 13,
        "retained": 13,
        "rate": 1.0
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
      "d": 2,
      "f": 0,
      "df": 2,
      "w": 5,
      "other": 0,
      "shares": {
        "passed": 0.5333,
        "d": 0.1333,
        "f": 0.0,
        "w": 0.3333
      },
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
      "d": 1,
      "f": 3,
      "df": 4,
      "w": 1,
      "other": 0,
      "shares": {
        "passed": 0.6154,
        "d": 0.0769,
        "f": 0.2308,
        "w": 0.0769
      },
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
      "d": 2,
      "f": 2,
      "df": 4,
      "w": 0,
      "other": null,
      "shares": {
        "passed": 0.6923,
        "d": 0.1538,
        "f": 0.1538,
        "w": 0.0
      },
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
      "d": 0,
      "f": 3,
      "df": 3,
      "w": 1,
      "other": 0,
      "shares": {
        "passed": 0.6667,
        "d": 0.0,
        "f": 0.25,
        "w": 0.0833
      },
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
      "d": 2,
      "f": 2,
      "df": 4,
      "w": 2,
      "other": 0,
      "shares": {
        "passed": 0.4545,
        "d": 0.1818,
        "f": 0.1818,
        "w": 0.1818
      },
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
      "d": 1,
      "f": 2,
      "df": 3,
      "w": 0,
      "other": 0,
      "shares": {
        "passed": 0.7273,
        "d": 0.0909,
        "f": 0.1818,
        "w": 0.0
      },
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
      "d": 1,
      "f": 0,
      "df": 1,
      "w": 1,
      "other": 0,
      "shares": {
        "passed": 0.8,
        "d": 0.1,
        "f": 0.0,
        "w": 0.1
      },
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
      "d": 0,
      "f": 0,
      "df": 0,
      "w": 4,
      "other": null,
      "shares": {
        "passed": 0.6,
        "d": 0.0,
        "f": 0.0,
        "w": 0.4
      },
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
  "left_out": 20,
  "pairs": [
    {
      "courses": [
        "ENG 111",
        "SDV 101"
      ],
      "students": 10,
      "retained": 3,
      "rate": 0.3,
      "gap": -27.6
    },
    {
      "courses": [
        "ENG 101",
        "ENG 11"
      ],
      "students": 18,
      "retained": 9,
      "rate": 0.5,
      "gap": -7.6
    },
    {
      "courses": [
        "SOC 111",
        "SSC 100"
      ],
      "students": 13,
      "retained": 7,
      "rate": 0.5385,
      "gap": -3.8
    }
  ],
  "pairs_considered": 43
};

/** 2024-25: its second year is only partly in the data. */
export const gateway2024: GatewayResponse = {
  "meta": {
    "cohort": "2024-25",
    "filters": {},
    "retention_type": "school",
    "provisional": true,
    "min_students": 10,
    "source": "PDP analysis-ready cohort and course files (synthetic sample)",
    "loaded_at": "2026-11-10T06:18:59",
    "flagged": true,
    "retention_term": "next academic year",
    "retention_observed": true,
    "first_term": null,
    "min_pair_students": 10
  },
  "status": "ok",
  "students": 2612,
  "cohort_retention": {
    "type": "school",
    "status": "ok",
    "retained": 989,
    "students": 2612,
    "numerator": 989,
    "denominator": 2612,
    "rate": 0.3786,
    "n_excluded": 0,
    "n_out_of_scope": 0
  },
  "courses": [
    {
      "course": "ENG 101",
      "name": "COMPOSITION I",
      "subject": "E",
      "students": 362,
      "passed": 272,
      "d": 14,
      "f": 58,
      "df": 72,
      "w": 18,
      "other": 24,
      "shares": {
        "passed": 0.7514,
        "d": 0.0387,
        "f": 0.1602,
        "w": 0.0497
      },
      "retained_if_passed": {
        "students": 272,
        "retained": 195,
        "rate": 0.7169
      },
      "retained_if_not_passed": {
        "students": 90,
        "retained": 38,
        "rate": 0.4222
      }
    },
    {
      "course": "ENGL 101",
      "name": "ENGLISH COMPOSITION I",
      "subject": "E",
      "students": 76,
      "passed": 54,
      "d": 5,
      "f": 13,
      "df": 18,
      "w": 4,
      "other": 0,
      "shares": {
        "passed": 0.7105,
        "d": 0.0658,
        "f": 0.1711,
        "w": 0.0526
      },
      "retained_if_passed": {
        "students": 54,
        "retained": 34,
        "rate": 0.6296
      },
      "retained_if_not_passed": {
        "students": 22,
        "retained": 1,
        "rate": 0.0455
      }
    },
    {
      "course": "ENGL 121",
      "name": "COLLEGE COMPOSITION",
      "subject": "E",
      "students": 28,
      "passed": 28,
      "d": 0,
      "f": 0,
      "df": 0,
      "w": 0,
      "other": 0,
      "shares": {
        "passed": 1.0,
        "d": 0.0,
        "f": 0.0,
        "w": 0.0
      },
      "retained_if_passed": {
        "students": 28,
        "retained": 20,
        "rate": 0.7143
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
      "d": 0,
      "f": 2,
      "df": 2,
      "w": 0,
      "other": 0,
      "shares": {
        "passed": 0.913,
        "d": 0.0,
        "f": 0.087,
        "w": 0.0
      },
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
      "d": 1,
      "f": 2,
      "df": 3,
      "w": 0,
      "other": null,
      "shares": {
        "passed": 0.8421,
        "d": 0.0526,
        "f": 0.1053,
        "w": 0.0
      },
      "retained_if_passed": {
        "students": 16,
        "retained": 10,
        "rate": 0.625
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
      "d": 1,
      "f": 3,
      "df": 4,
      "w": 2,
      "other": 0,
      "shares": {
        "passed": 0.6842,
        "d": 0.0526,
        "f": 0.1579,
        "w": 0.1053
      },
      "retained_if_passed": {
        "students": 13,
        "retained": 9,
        "rate": 0.6923
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
      "d": 1,
      "f": 2,
      "df": 3,
      "w": 2,
      "other": null,
      "shares": {
        "passed": 0.7059,
        "d": 0.0588,
        "f": 0.1176,
        "w": 0.1176
      },
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
      "course": "ENGL 1110",
      "name": "COMPOSITION I",
      "subject": "E",
      "students": 17,
      "passed": 8,
      "d": 0,
      "f": 8,
      "df": 8,
      "w": 1,
      "other": 0,
      "shares": {
        "passed": 0.4706,
        "d": 0.0,
        "f": 0.4706,
        "w": 0.0588
      },
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
      "d": 0,
      "f": 1,
      "df": 1,
      "w": 2,
      "other": 0,
      "shares": {
        "passed": 0.7857,
        "d": 0.0,
        "f": 0.0714,
        "w": 0.1429
      },
      "retained_if_passed": {
        "students": 11,
        "retained": 7,
        "rate": 0.6364
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
      "d": 0,
      "f": 3,
      "df": 3,
      "w": 0,
      "other": 0,
      "shares": {
        "passed": 0.7273,
        "d": 0.0,
        "f": 0.2727,
        "w": 0.0
      },
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
      "d": 0,
      "f": 16,
      "df": 16,
      "w": 2,
      "other": 0,
      "shares": {
        "passed": 0.6604,
        "d": 0.0,
        "f": 0.3019,
        "w": 0.0377
      },
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
      "d": 0,
      "f": 8,
      "df": 8,
      "w": 3,
      "other": 0,
      "shares": {
        "passed": 0.6207,
        "d": 0.0,
        "f": 0.2759,
        "w": 0.1034
      },
      "retained_if_passed": {
        "students": 18,
        "retained": 10,
        "rate": 0.5556
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
      "d": 1,
      "f": 6,
      "df": 7,
      "w": 2,
      "other": null,
      "shares": {
        "passed": 0.5909,
        "d": 0.0455,
        "f": 0.2727,
        "w": 0.0909
      },
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
      "d": 2,
      "f": 4,
      "df": 6,
      "w": 1,
      "other": 0,
      "shares": {
        "passed": 0.6111,
        "d": 0.1111,
        "f": 0.2222,
        "w": 0.0556
      },
      "retained_if_passed": {
        "students": 11,
        "retained": 7,
        "rate": 0.6364
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
      "d": 1,
      "f": 2,
      "df": 3,
      "w": 2,
      "other": 0,
      "shares": {
        "passed": 0.7059,
        "d": 0.0588,
        "f": 0.1176,
        "w": 0.1176
      },
      "retained_if_passed": {
        "students": 12,
        "retained": 8,
        "rate": 0.6667
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
      "d": 2,
      "f": 2,
      "df": 4,
      "w": 1,
      "other": 0,
      "shares": {
        "passed": 0.7059,
        "d": 0.1176,
        "f": 0.1176,
        "w": 0.0588
      },
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
      "d": 0,
      "f": 2,
      "df": 2,
      "w": 4,
      "other": 0,
      "shares": {
        "passed": 0.6,
        "d": 0.0,
        "f": 0.1333,
        "w": 0.2667
      },
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
      "d": 1,
      "f": 4,
      "df": 5,
      "w": 1,
      "other": null,
      "shares": {
        "passed": 0.5385,
        "d": 0.0769,
        "f": 0.3077,
        "w": 0.0769
      },
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
      "d": 0,
      "f": 0,
      "df": 0,
      "w": 3,
      "other": 0,
      "shares": {
        "passed": 0.7692,
        "d": 0.0,
        "f": 0.0,
        "w": 0.2308
      },
      "retained_if_passed": {
        "students": 10,
        "retained": 7,
        "rate": 0.7
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
      "d": 1,
      "f": 0,
      "df": 1,
      "w": 0,
      "other": 0,
      "shares": {
        "passed": 0.9167,
        "d": 0.0833,
        "f": 0.0,
        "w": 0.0
      },
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
      "course": "MATH 314",
      "name": "COLLEGE ALGEBRA MATH PATHWAY",
      "subject": "M",
      "students": 12,
      "passed": 12,
      "d": 0,
      "f": 0,
      "df": 0,
      "w": 0,
      "other": null,
      "shares": {
        "passed": 1.0,
        "d": 0.0,
        "f": 0.0,
        "w": 0.0
      },
      "retained_if_passed": {
        "students": 12,
        "retained": 3,
        "rate": 0.25
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
      "d": 0,
      "f": 5,
      "df": 5,
      "w": 2,
      "other": 0,
      "shares": {
        "passed": 0.4167,
        "d": 0.0,
        "f": 0.4167,
        "w": 0.1667
      },
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
      "d": 1,
      "f": 1,
      "df": 2,
      "w": 3,
      "other": 0,
      "shares": {
        "passed": 0.5833,
        "d": 0.0833,
        "f": 0.0833,
        "w": 0.25
      },
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
      "d": 1,
      "f": 1,
      "df": 2,
      "w": 5,
      "other": 0,
      "shares": {
        "passed": 0.3636,
        "d": 0.0909,
        "f": 0.0909,
        "w": 0.4545
      },
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
      "d": 1,
      "f": 2,
      "df": 3,
      "w": 1,
      "other": 0,
      "shares": {
        "passed": 0.6,
        "d": 0.1,
        "f": 0.2,
        "w": 0.1
      },
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
  "left_out": 36,
  "pairs": [
    {
      "courses": [
        "MA 119",
        "MA 121"
      ],
      "students": 11,
      "retained": 0,
      "rate": 0.0,
      "gap": -37.9
    },
    {
      "courses": [
        "FYS 100",
        "ST 100"
      ],
      "students": 11,
      "retained": 0,
      "rate": 0.0,
      "gap": -37.9
    },
    {
      "courses": [
        "ENGL 101",
        "SP 211"
      ],
      "students": 11,
      "retained": 0,
      "rate": 0.0,
      "gap": -37.9
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
    "retention_type": "school",
    "provisional": false,
    "min_students": 10,
    "source": "PDP analysis-ready cohort and course files (synthetic sample)",
    "loaded_at": "2026-11-10T06:18:59",
    "flagged": true,
    "retention_term": "next academic year",
    "retention_observed": true,
    "first_term": "Fall 2023",
    "min_pair_students": 10
  },
  "status": "suppressed",
  "students": null,
  "cohort_retention": null,
  "courses": [],
  "hidden_courses": 0,
  "left_out": null,
  "pairs": [],
  "pairs_considered": 0
};
