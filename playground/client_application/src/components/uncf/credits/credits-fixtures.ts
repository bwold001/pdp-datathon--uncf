// Real answers from GET /uncf/credit-momentum on the synthetic sample data (pdp.sqlite), saved for stories and tests
// before the API moved to measures/ (#36). Their tier retention is fall to fall, which is now retention_type=federal.
// Regenerate them from the running API (measures/breakdowns/credit_momentum.py); don't edit the numbers by hand.
import type { CreditsResponse } from "./credits-data";

/** 2023-24, Fall starters: the terms have names. */
export const creditsFall2023: CreditsResponse = {
  "meta": {
    "cohort": "2023-24",
    "filters": {
      "cohort_term": "Fall"
    },
    "provisional": false,
    "retention_term": "Fall 2024",
    "min_students": 10,
    "source": "PDP analysis-ready cohort and course files (synthetic sample)",
    "loaded_at": "2026-11-10T06:18:59"
  },
  "status": "ok",
  "students": 1584,
  "credits": {
    "counted": 1537,
    "left_out": 47,
    "avg_attempted": 17.8,
    "avg_earned": 13.1
  },
  "completion": {
    "counted": 1470,
    "ratio": 0.6852
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
    "provisional": false,
    "retention_term": "Fall 2024",
    "min_students": 10,
    "source": "PDP analysis-ready cohort and course files (synthetic sample)",
    "loaded_at": "2026-11-10T06:18:59"
  },
  "status": "ok",
  "students": 2580,
  "credits": {
    "counted": 2519,
    "left_out": 61,
    "avg_attempted": 15.5,
    "avg_earned": 11.6
  },
  "completion": {
    "counted": 2412,
    "ratio": 0.7132
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
      "retained": 463,
      "rate": 0.2749
    },
    {
      "key": "15_29",
      "label": "15–29",
      "students": 654,
      "share": 0.2596,
      "retained": 473,
      "rate": 0.7232
    },
    {
      "key": "30_plus",
      "label": "30 or more",
      "students": 181,
      "share": 0.0719,
      "retained": 137,
      "rate": 0.7569
    }
  ]
};

/** 2024-25: next fall (Fall 2025) is only partly in the data. */
export const credits2024: CreditsResponse = {
  "meta": {
    "cohort": "2024-25",
    "filters": {},
    "provisional": true,
    "retention_term": "Fall 2025",
    "min_students": 10,
    "source": "PDP analysis-ready cohort and course files (synthetic sample)",
    "loaded_at": "2026-11-10T06:18:59"
  },
  "status": "ok",
  "students": 2612,
  "credits": {
    "counted": 2520,
    "left_out": 92,
    "avg_attempted": 14.8,
    "avg_earned": 11.4
  },
  "completion": {
    "counted": 2417,
    "ratio": 0.7266
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
      "retained": 340,
      "rate": 0.1995
    },
    {
      "key": "15_29",
      "label": "15–29",
      "students": 653,
      "share": 0.2591,
      "retained": 334,
      "rate": 0.5115
    },
    {
      "key": "30_plus",
      "label": "30 or more",
      "students": 163,
      "share": 0.0647,
      "retained": 97,
      "rate": 0.5951
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
    "provisional": false,
    "retention_term": "Fall 2024",
    "min_students": 10,
    "source": "PDP analysis-ready cohort and course files (synthetic sample)",
    "loaded_at": "2026-11-10T06:18:59"
  },
  "status": "suppressed",
  "students": null,
  "credits": null,
  "completion": null,
  "milestones": [],
  "terms": [],
  "tiers": []
};
