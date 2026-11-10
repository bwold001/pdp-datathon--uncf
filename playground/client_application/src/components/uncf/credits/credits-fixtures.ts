// Real answers from the shared API (GET /uncf/credit-momentum) on the synthetic sample data (pdp.sqlite), saved for
// stories and tests with the queries the tab sends. Retention is the API's default (the PDP flag) unless the name says
// federal. Regenerate them from the running API (measures/breakdowns/credit_momentum.py); don't edit the numbers by hand.
import type { CreditsResponse } from "./credits-data";

/** 2023-24, Fall starters: the terms have names. */
export const creditsFall2023: CreditsResponse = {
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
    "retention_term": "next academic year"
  },
  "status": "ok",
  "students": 1584,
  "retention": {
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
  "credits": {
    "counted": 1537,
    "left_out": 47,
    "avg_attempted": 17.8,
    "avg_earned": 13.1
  },
  "completion": {
    "counted": 1470,
    "ratio": 0.6852,
    "status": "ok"
  },
  "milestones": [
    {
      "credits": 12,
      "students": 778,
      "share": 0.5062
    },
    {
      "credits": 24,
      "students": 316,
      "share": 0.2056
    },
    {
      "credits": 30,
      "students": 140,
      "share": 0.0911
    }
  ],
  "terms": [
    {
      "label": "Fall 2023",
      "enrolled": 1440,
      "avg_attempted": 10.3,
      "avg_earned": 7.3
    },
    {
      "label": "Spring 2024",
      "enrolled": 876,
      "avg_attempted": 10.6,
      "avg_earned": 8.4
    }
  ],
  "tiers": [
    {
      "key": "under_15",
      "label": "Under 15",
      "students": 929,
      "share": 0.6044,
      "retained": 379,
      "rate": 0.408
    },
    {
      "key": "15_29",
      "label": "15–29",
      "students": 468,
      "share": 0.3045,
      "retained": 401,
      "rate": 0.8568
    },
    {
      "key": "30_plus",
      "label": "30 or more",
      "students": 140,
      "share": 0.0911,
      "retained": 132,
      "rate": 0.9429
    }
  ]
};

/** 2023-24 Fall starters with fall to fall retention (Retention: Back next fall). */
export const creditsFederalFall2023: CreditsResponse = {
  "meta": {
    "cohort": "2023-24",
    "filters": {
      "cohort_term": "Fall"
    },
    "retention_type": "federal",
    "provisional": false,
    "min_students": 10,
    "source": "PDP analysis-ready cohort and course files (synthetic sample)",
    "loaded_at": "2026-11-10T06:18:59",
    "retention_term": "Fall 2024"
  },
  "status": "ok",
  "students": 1584,
  "retention": {
    "type": "federal",
    "status": "ok",
    "retained": 699,
    "students": 1584,
    "numerator": 699,
    "denominator": 1584,
    "rate": 0.4413,
    "n_excluded": 0,
    "n_out_of_scope": 0
  },
  "credits": {
    "counted": 1537,
    "left_out": 47,
    "avg_attempted": 17.8,
    "avg_earned": 13.1
  },
  "completion": {
    "counted": 1470,
    "ratio": 0.6852,
    "status": "ok"
  },
  "milestones": [
    {
      "credits": 12,
      "students": 778,
      "share": 0.5062
    },
    {
      "credits": 24,
      "students": 316,
      "share": 0.2056
    },
    {
      "credits": 30,
      "students": 140,
      "share": 0.0911
    }
  ],
  "terms": [
    {
      "label": "Fall 2023",
      "enrolled": 1440,
      "avg_attempted": 10.3,
      "avg_earned": 7.3
    },
    {
      "label": "Spring 2024",
      "enrolled": 876,
      "avg_attempted": 10.6,
      "avg_earned": 8.4
    }
  ],
  "tiers": [
    {
      "key": "under_15",
      "label": "Under 15",
      "students": 929,
      "share": 0.6044,
      "retained": 274,
      "rate": 0.2949
    },
    {
      "key": "15_29",
      "label": "15–29",
      "students": 468,
      "share": 0.3045,
      "retained": 321,
      "rate": 0.6859
    },
    {
      "key": "30_plus",
      "label": "30 or more",
      "students": 140,
      "share": 0.0911,
      "retained": 103,
      "rate": 0.7357
    }
  ]
};

/** 2023-24, every starting term: the terms are named by position. */
export const credits2023: CreditsResponse = {
  "meta": {
    "cohort": "2023-24",
    "filters": {},
    "retention_type": "school",
    "provisional": false,
    "min_students": 10,
    "source": "PDP analysis-ready cohort and course files (synthetic sample)",
    "loaded_at": "2026-11-10T06:18:59",
    "retention_term": "next academic year"
  },
  "status": "ok",
  "students": 2580,
  "retention": {
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
  "credits": {
    "counted": 2519,
    "left_out": 61,
    "avg_attempted": 15.5,
    "avg_earned": 11.6
  },
  "completion": {
    "counted": 2412,
    "ratio": 0.7132,
    "status": "ok"
  },
  "milestones": [
    {
      "credits": 12,
      "students": 1099,
      "share": 0.4363
    },
    {
      "credits": 24,
      "students": 408,
      "share": 0.162
    },
    {
      "credits": 30,
      "students": 181,
      "share": 0.0719
    }
  ],
  "terms": [
    {
      "label": "First term",
      "enrolled": 2339,
      "avg_attempted": 9.1,
      "avg_earned": 6.6
    },
    {
      "label": "Second term",
      "enrolled": 1252,
      "avg_attempted": 10.1,
      "avg_earned": 8.0
    }
  ],
  "tiers": [
    {
      "key": "under_15",
      "label": "Under 15",
      "students": 1684,
      "share": 0.6685,
      "retained": 622,
      "rate": 0.3694
    },
    {
      "key": "15_29",
      "label": "15–29",
      "students": 654,
      "share": 0.2596,
      "retained": 555,
      "rate": 0.8486
    },
    {
      "key": "30_plus",
      "label": "30 or more",
      "students": 181,
      "share": 0.0719,
      "retained": 167,
      "rate": 0.9227
    }
  ]
};

/** 2024-25: its second year is only partly in the data. */
export const credits2024: CreditsResponse = {
  "meta": {
    "cohort": "2024-25",
    "filters": {},
    "retention_type": "school",
    "provisional": true,
    "min_students": 10,
    "source": "PDP analysis-ready cohort and course files (synthetic sample)",
    "loaded_at": "2026-11-10T06:18:59",
    "retention_term": "next academic year"
  },
  "status": "ok",
  "students": 2612,
  "retention": {
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
  "credits": {
    "counted": 2520,
    "left_out": 92,
    "avg_attempted": 14.8,
    "avg_earned": 11.4
  },
  "completion": {
    "counted": 2417,
    "ratio": 0.7266,
    "status": "ok"
  },
  "milestones": [
    {
      "credits": 12,
      "students": 1069,
      "share": 0.4242
    },
    {
      "credits": 24,
      "students": 397,
      "share": 0.1575
    },
    {
      "credits": 30,
      "students": 163,
      "share": 0.0647
    }
  ],
  "terms": [
    {
      "label": "First term",
      "enrolled": 2292,
      "avg_attempted": 9.1,
      "avg_earned": 6.9
    },
    {
      "label": "Second term",
      "enrolled": 1225,
      "avg_attempted": 10.1,
      "avg_earned": 8.0
    }
  ],
  "tiers": [
    {
      "key": "under_15",
      "label": "Under 15",
      "students": 1704,
      "share": 0.6762,
      "retained": 419,
      "rate": 0.2459
    },
    {
      "key": "15_29",
      "label": "15–29",
      "students": 653,
      "share": 0.2591,
      "retained": 442,
      "rate": 0.6769
    },
    {
      "key": "30_plus",
      "label": "30 or more",
      "students": 163,
      "share": 0.0647,
      "retained": 127,
      "rate": 0.7791
    }
  ]
};

/** Asian Pell recipients, 2023-24: 66 students, so a milestone 1 to 9 reached is hidden. */
export const creditsSmallGroup: CreditsResponse = {
  "meta": {
    "cohort": "2023-24",
    "filters": {
      "pell": "Y",
      "race": "Asian"
    },
    "retention_type": "school",
    "provisional": false,
    "min_students": 10,
    "source": "PDP analysis-ready cohort and course files (synthetic sample)",
    "loaded_at": "2026-11-10T06:18:59",
    "retention_term": "next academic year"
  },
  "status": "ok",
  "students": 66,
  "retention": {
    "type": "school",
    "status": "ok",
    "retained": 53,
    "students": 66,
    "numerator": 53,
    "denominator": 66,
    "rate": 0.803,
    "n_excluded": 0,
    "n_out_of_scope": 0
  },
  "credits": {
    "counted": 66,
    "left_out": 0,
    "avg_attempted": 19.9,
    "avg_earned": 15.1
  },
  "completion": {
    "counted": 66,
    "ratio": 0.7413,
    "status": "ok"
  },
  "milestones": [
    {
      "credits": 12,
      "students": 43,
      "share": 0.6515
    },
    {
      "credits": 24,
      "students": 15,
      "share": 0.2273
    },
    {
      "credits": 30,
      "students": null,
      "share": null
    }
  ],
  "terms": [
    {
      "label": "First term",
      "enrolled": 66,
      "avg_attempted": 11.3,
      "avg_earned": 8.4
    },
    {
      "label": "Second term",
      "enrolled": 44,
      "avg_attempted": 10.9,
      "avg_earned": 8.6
    }
  ],
  "tiers": [
    {
      "key": "under_15",
      "label": "Under 15",
      "students": 39,
      "share": 0.5909,
      "retained": 27,
      "rate": 0.6923
    },
    {
      "key": "15_29",
      "label": "15–29",
      "students": 21,
      "share": 0.3182,
      "retained": 20,
      "rate": 0.9524
    },
    {
      "key": "30_plus",
      "label": "30 or more",
      "students": null,
      "share": null,
      "retained": null,
      "rate": null
    }
  ]
};

/** A filter combination with fewer than 10 students. */
export const creditsTooFew: CreditsResponse = {
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
    "retention_term": "next academic year"
  },
  "status": "suppressed",
  "students": null,
  "retention": null,
  "credits": null,
  "completion": null,
  "milestones": [],
  "terms": [],
  "tiers": []
};
