// Real answers from the shared API (GET /uncf/credit-momentum) on the synthetic sample data (pdp.sqlite), saved for
// stories and tests with the queries the tab sends. Retention is the API's default (the PDP flag) unless the name says
// federal. Regenerate them from the running API (measures/breakdowns/credit_momentum.py); don't edit the numbers by hand.
import type { CreditsResponse } from "./credits-data";

/** 2022-23, Fall starters: the class in the Credit momentum design. */
export const creditsFall2022: CreditsResponse = {
  "meta": {
    "cohort": "2022-23",
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
  "students": 1589,
  "retention": {
    "type": "school",
    "status": "ok",
    "retained": 931,
    "students": 1589,
    "numerator": 931,
    "denominator": 1589,
    "rate": 0.5859,
    "n_excluded": 0,
    "n_out_of_scope": 0
  },
  "progress": {
    "settings": {
      "minimum": 24,
      "degree_credits": 120,
      "years": 4,
      "pace": 30.0,
      "higher_degree_credits": 125,
      "higher_pace": 31.25,
      "counting_course_types": [
        "CU",
        "CC"
      ]
    },
    "next_term": "Spring 2023",
    "year_two": "2023-24",
    "minimum": {
      "students": 305,
      "share": 0.1919
    },
    "pace": {
      "students": 133,
      "share": 0.0837
    },
    "higher_pace": {
      "students": 78,
      "share": 0.0491
    },
    "two_year_pace": {
      "status": "ok",
      "students": 70,
      "share": 0.0441
    },
    "bands": [
      {
        "key": "pace",
        "students": 133,
        "share": 0.0837,
        "retention": {
          "students": 133,
          "retained": 126,
          "rate": 0.9474
        }
      },
      {
        "key": "minimum",
        "students": 172,
        "share": 0.1082,
        "retention": {
          "students": 172,
          "retained": 154,
          "rate": 0.8953
        }
      },
      {
        "key": "below",
        "students": 763,
        "share": 0.4802,
        "retention": {
          "students": 763,
          "retained": 521,
          "rate": 0.6828
        }
      },
      {
        "key": "stopped",
        "students": 521,
        "share": 0.3279,
        "retention": {
          "students": 521,
          "retained": 130,
          "rate": 0.2495
        }
      }
    ],
    "unsorted": 0,
    "below": {
      "students": 763,
      "reasons": [
        {
          "key": "under",
          "students": 539,
          "share": 0.7064
        },
        {
          "key": "failed",
          "students": 110,
          "share": 0.1442
        },
        {
          "key": "withdrew",
          "students": 66,
          "share": 0.0865
        },
        {
          "key": "not_counted",
          "students": 31,
          "share": 0.0406
        }
      ],
      "unexplained": 17
    },
    "year_two_follow_up": {
      "status": "ok",
      "students": 305,
      "again": {
        "students": 123,
        "share": 0.4033
      },
      "kept_taking_courses": {
        "students": 99,
        "share": 0.3246
      },
      "no_courses": {
        "students": 83,
        "share": 0.2721
      }
    },
    "both_years": {
      "students": 123,
      "share": 0.0774
    }
  },
  "credits": {
    "counted": 1566,
    "left_out": 23,
    "avg_attempted": 17.2,
    "avg_earned": 12.7
  },
  "completion": {
    "counted": 1501,
    "ratio": 0.699,
    "status": "ok"
  },
  "milestones": [
    {
      "credits": 12,
      "students": 744,
      "share": 0.4751
    },
    {
      "credits": 24,
      "students": 310,
      "share": 0.198
    },
    {
      "credits": 30,
      "students": 153,
      "share": 0.0977
    }
  ],
  "terms": [
    {
      "label": "Fall 2022",
      "enrolled": 1567,
      "avg_attempted": 10.0,
      "avg_earned": 7.1
    },
    {
      "label": "Spring 2023",
      "enrolled": 1070,
      "avg_attempted": 10.2,
      "avg_earned": 7.9
    }
  ],
  "tiers": [
    {
      "key": "under_15",
      "label": "Under 15",
      "students": 978,
      "share": 0.6245,
      "retained": 415,
      "rate": 0.4243
    },
    {
      "key": "15_29",
      "label": "15–29",
      "students": 435,
      "share": 0.2778,
      "retained": 372,
      "rate": 0.8552
    },
    {
      "key": "30_plus",
      "label": "30 or more",
      "students": 153,
      "share": 0.0977,
      "retained": 144,
      "rate": 0.9412
    }
  ]
};

/** 2022-23 Fall starters with Pell: a filtered view. */
export const creditsFall2022Pell: CreditsResponse = {
  "meta": {
    "cohort": "2022-23",
    "filters": {
      "cohort_term": "Fall",
      "pell": "Y"
    },
    "retention_type": "school",
    "provisional": false,
    "min_students": 10,
    "source": "PDP analysis-ready cohort and course files (synthetic sample)",
    "loaded_at": "2026-11-10T06:18:59",
    "retention_term": "next academic year"
  },
  "status": "ok",
  "students": 623,
  "retention": {
    "type": "school",
    "status": "ok",
    "retained": 378,
    "students": 623,
    "numerator": 378,
    "denominator": 623,
    "rate": 0.6067,
    "n_excluded": 0,
    "n_out_of_scope": 0
  },
  "progress": {
    "settings": {
      "minimum": 24,
      "degree_credits": 120,
      "years": 4,
      "pace": 30.0,
      "higher_degree_credits": 125,
      "higher_pace": 31.25,
      "counting_course_types": [
        "CU",
        "CC"
      ]
    },
    "next_term": "Spring 2023",
    "year_two": "2023-24",
    "minimum": {
      "students": 129,
      "share": 0.2071
    },
    "pace": {
      "students": 67,
      "share": 0.1075
    },
    "higher_pace": {
      "students": 43,
      "share": 0.069
    },
    "two_year_pace": {
      "status": "ok",
      "students": 34,
      "share": 0.0546
    },
    "bands": [
      {
        "key": "pace",
        "students": 67,
        "share": 0.1075,
        "retention": {
          "students": 67,
          "retained": 65,
          "rate": 0.9701
        }
      },
      {
        "key": "minimum",
        "students": 62,
        "share": 0.0995,
        "retention": {
          "students": 62,
          "retained": 55,
          "rate": 0.8871
        }
      },
      {
        "key": "below",
        "students": 325,
        "share": 0.5217,
        "retention": {
          "students": 325,
          "retained": 219,
          "rate": 0.6738
        }
      },
      {
        "key": "stopped",
        "students": 169,
        "share": 0.2713,
        "retention": {
          "students": 169,
          "retained": 39,
          "rate": 0.2308
        }
      }
    ],
    "unsorted": 0,
    "below": {
      "students": 325,
      "reasons": [
        {
          "key": "under",
          "students": 210,
          "share": 0.6462
        },
        {
          "key": "failed",
          "students": 59,
          "share": 0.1815
        },
        {
          "key": "withdrew",
          "students": 37,
          "share": 0.1138
        },
        {
          "key": "not_counted",
          "students": 13,
          "share": 0.04
        }
      ],
      "unexplained": null
    },
    "year_two_follow_up": {
      "status": "ok",
      "students": 129,
      "again": {
        "students": 55,
        "share": 0.4264
      },
      "kept_taking_courses": {
        "students": 40,
        "share": 0.3101
      },
      "no_courses": {
        "students": 34,
        "share": 0.2636
      }
    },
    "both_years": {
      "students": 55,
      "share": 0.0883
    }
  },
  "credits": {
    "counted": 619,
    "left_out": null,
    "avg_attempted": 19.4,
    "avg_earned": 13.7
  },
  "completion": {
    "counted": 594,
    "ratio": 0.6455,
    "status": "ok"
  },
  "milestones": [
    {
      "credits": 12,
      "students": 326,
      "share": 0.5267
    },
    {
      "credits": 24,
      "students": 132,
      "share": 0.2132
    },
    {
      "credits": 30,
      "students": 73,
      "share": 0.1179
    }
  ],
  "terms": [
    {
      "label": "Fall 2022",
      "enrolled": 620,
      "avg_attempted": 11.2,
      "avg_earned": 7.6
    },
    {
      "label": "Spring 2023",
      "enrolled": 455,
      "avg_attempted": 11.0,
      "avg_earned": 8.0
    }
  ],
  "tiers": [
    {
      "key": "under_15",
      "label": "Under 15",
      "students": 359,
      "share": 0.58,
      "retained": 148,
      "rate": 0.4123
    },
    {
      "key": "15_29",
      "label": "15–29",
      "students": 187,
      "share": 0.3021,
      "retained": 160,
      "rate": 0.8556
    },
    {
      "key": "30_plus",
      "label": "30 or more",
      "students": 73,
      "share": 0.1179,
      "retained": 70,
      "rate": 0.9589
    }
  ]
};

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
  "progress": {
    "settings": {
      "minimum": 24,
      "degree_credits": 120,
      "years": 4,
      "pace": 30.0,
      "higher_degree_credits": 125,
      "higher_pace": 31.25,
      "counting_course_types": [
        "CU",
        "CC"
      ]
    },
    "next_term": "Spring 2024",
    "year_two": "2024-25",
    "minimum": {
      "students": 285,
      "share": 0.1799
    },
    "pace": {
      "students": 124,
      "share": 0.0783
    },
    "higher_pace": {
      "students": 75,
      "share": 0.0473
    },
    "two_year_pace": {
      "status": "ok",
      "students": 53,
      "share": 0.0335
    },
    "bands": [
      {
        "key": "pace",
        "students": 124,
        "share": 0.0783,
        "retention": {
          "students": 124,
          "retained": 116,
          "rate": 0.9355
        }
      },
      {
        "key": "minimum",
        "students": 161,
        "share": 0.1016,
        "retention": {
          "students": 161,
          "retained": 144,
          "rate": 0.8944
        }
      },
      {
        "key": "below",
        "students": 599,
        "share": 0.3782,
        "retention": {
          "students": 599,
          "retained": 420,
          "rate": 0.7012
        }
      },
      {
        "key": "stopped",
        "students": 700,
        "share": 0.4419,
        "retention": {
          "students": 700,
          "retained": 233,
          "rate": 0.3329
        }
      }
    ],
    "unsorted": 0,
    "below": {
      "students": 599,
      "reasons": [
        {
          "key": "under",
          "students": 405,
          "share": 0.6761
        },
        {
          "key": "failed",
          "students": 96,
          "share": 0.1603
        },
        {
          "key": "withdrew",
          "students": 53,
          "share": 0.0885
        },
        {
          "key": "not_counted",
          "students": 24,
          "share": 0.0401
        }
      ],
      "unexplained": 21
    },
    "year_two_follow_up": {
      "status": "ok",
      "students": 285,
      "again": {
        "students": 117,
        "share": 0.4105
      },
      "kept_taking_courses": {
        "students": 117,
        "share": 0.4105
      },
      "no_courses": {
        "students": 51,
        "share": 0.1789
      }
    },
    "both_years": {
      "students": 117,
      "share": 0.0739
    }
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
  "progress": {
    "settings": {
      "minimum": 24,
      "degree_credits": 120,
      "years": 4,
      "pace": 30.0,
      "higher_degree_credits": 125,
      "higher_pace": 31.25,
      "counting_course_types": [
        "CU",
        "CC"
      ]
    },
    "next_term": "Spring 2024",
    "year_two": "2024-25",
    "minimum": {
      "students": 285,
      "share": 0.1799
    },
    "pace": {
      "students": 124,
      "share": 0.0783
    },
    "higher_pace": {
      "students": 75,
      "share": 0.0473
    },
    "two_year_pace": {
      "status": "ok",
      "students": 53,
      "share": 0.0335
    },
    "bands": [
      {
        "key": "pace",
        "students": 124,
        "share": 0.0783,
        "retention": {
          "students": 124,
          "retained": 96,
          "rate": 0.7742
        }
      },
      {
        "key": "minimum",
        "students": 161,
        "share": 0.1016,
        "retention": {
          "students": 161,
          "retained": 126,
          "rate": 0.7826
        }
      },
      {
        "key": "below",
        "students": 599,
        "share": 0.3782,
        "retention": {
          "students": 599,
          "retained": 339,
          "rate": 0.5659
        }
      },
      {
        "key": "stopped",
        "students": 700,
        "share": 0.4419,
        "retention": {
          "students": 700,
          "retained": 138,
          "rate": 0.1971
        }
      }
    ],
    "unsorted": 0,
    "below": {
      "students": 599,
      "reasons": [
        {
          "key": "under",
          "students": 405,
          "share": 0.6761
        },
        {
          "key": "failed",
          "students": 96,
          "share": 0.1603
        },
        {
          "key": "withdrew",
          "students": 53,
          "share": 0.0885
        },
        {
          "key": "not_counted",
          "students": 24,
          "share": 0.0401
        }
      ],
      "unexplained": 21
    },
    "year_two_follow_up": {
      "status": "ok",
      "students": 285,
      "again": {
        "students": 117,
        "share": 0.4105
      },
      "kept_taking_courses": {
        "students": 117,
        "share": 0.4105
      },
      "no_courses": {
        "students": 51,
        "share": 0.1789
      }
    },
    "both_years": {
      "students": 117,
      "share": 0.0739
    }
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
  "progress": {
    "settings": {
      "minimum": 24,
      "degree_credits": 120,
      "years": 4,
      "pace": 30.0,
      "higher_degree_credits": 125,
      "higher_pace": 31.25,
      "counting_course_types": [
        "CU",
        "CC"
      ]
    },
    "next_term": null,
    "year_two": "2024-25",
    "minimum": {
      "students": 302,
      "share": 0.1171
    },
    "pace": {
      "students": 131,
      "share": 0.0508
    },
    "higher_pace": {
      "students": 78,
      "share": 0.0302
    },
    "two_year_pace": {
      "status": "ok",
      "students": 55,
      "share": 0.0213
    },
    "bands": [
      {
        "key": "pace",
        "students": 131,
        "share": 0.0508,
        "retention": {
          "students": 131,
          "retained": 123,
          "rate": 0.9389
        }
      },
      {
        "key": "minimum",
        "students": 171,
        "share": 0.0663,
        "retention": {
          "students": 171,
          "retained": 150,
          "rate": 0.8772
        }
      },
      {
        "key": "below",
        "students": 962,
        "share": 0.3729,
        "retention": {
          "students": 962,
          "retained": 688,
          "rate": 0.7152
        }
      },
      {
        "key": "stopped",
        "students": 1316,
        "share": 0.5101,
        "retention": {
          "students": 1316,
          "retained": 384,
          "rate": 0.2918
        }
      }
    ],
    "unsorted": 0,
    "below": {
      "students": 962,
      "reasons": [
        {
          "key": "under",
          "students": 762,
          "share": 0.7921
        },
        {
          "key": "failed",
          "students": 97,
          "share": 0.1008
        },
        {
          "key": "withdrew",
          "students": 55,
          "share": 0.0572
        },
        {
          "key": "not_counted",
          "students": 26,
          "share": 0.027
        }
      ],
      "unexplained": 22
    },
    "year_two_follow_up": {
      "status": "ok",
      "students": 302,
      "again": {
        "students": 119,
        "share": 0.394
      },
      "kept_taking_courses": {
        "students": 127,
        "share": 0.4205
      },
      "no_courses": {
        "students": 56,
        "share": 0.1854
      }
    },
    "both_years": {
      "students": 119,
      "share": 0.0461
    }
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
  "progress": {
    "settings": {
      "minimum": 24,
      "degree_credits": 120,
      "years": 4,
      "pace": 30.0,
      "higher_degree_credits": 125,
      "higher_pace": 31.25,
      "counting_course_types": [
        "CU",
        "CC"
      ]
    },
    "next_term": null,
    "year_two": "2025-26",
    "minimum": {
      "students": 340,
      "share": 0.1302
    },
    "pace": {
      "students": 123,
      "share": 0.0471
    },
    "higher_pace": {
      "students": 73,
      "share": 0.0279
    },
    "two_year_pace": {
      "status": "ok",
      "students": 14,
      "share": 0.0054
    },
    "bands": [
      {
        "key": "pace",
        "students": 123,
        "share": 0.0471,
        "retention": {
          "students": 123,
          "retained": 100,
          "rate": 0.813
        }
      },
      {
        "key": "minimum",
        "students": 217,
        "share": 0.0831,
        "retention": {
          "students": 217,
          "retained": 164,
          "rate": 0.7558
        }
      },
      {
        "key": "below",
        "students": 895,
        "share": 0.3426,
        "retention": {
          "students": 895,
          "retained": 480,
          "rate": 0.5363
        }
      },
      {
        "key": "stopped",
        "students": 1377,
        "share": 0.5272,
        "retention": {
          "students": 1377,
          "retained": 245,
          "rate": 0.1779
        }
      }
    ],
    "unsorted": 0,
    "below": {
      "students": 895,
      "reasons": [
        {
          "key": "under",
          "students": 686,
          "share": 0.7665
        },
        {
          "key": "failed",
          "students": 100,
          "share": 0.1117
        },
        {
          "key": "withdrew",
          "students": 51,
          "share": 0.057
        },
        {
          "key": "not_counted",
          "students": 47,
          "share": 0.0525
        }
      ],
      "unexplained": 11
    },
    "year_two_follow_up": {
      "status": "ok",
      "students": 340,
      "again": {
        "students": 26,
        "share": 0.0765
      },
      "kept_taking_courses": {
        "students": 182,
        "share": 0.5353
      },
      "no_courses": {
        "students": 132,
        "share": 0.3882
      }
    },
    "both_years": {
      "students": 26,
      "share": 0.01
    }
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
  "progress": {
    "settings": {
      "minimum": 24,
      "degree_credits": 120,
      "years": 4,
      "pace": 30.0,
      "higher_degree_credits": 125,
      "higher_pace": 31.25,
      "counting_course_types": [
        "CU",
        "CC"
      ]
    },
    "next_term": null,
    "year_two": "2024-25",
    "minimum": {
      "students": 13,
      "share": 0.197
    },
    "pace": {
      "students": null,
      "share": null
    },
    "higher_pace": {
      "students": null,
      "share": null
    },
    "two_year_pace": {
      "status": "ok",
      "students": null,
      "share": null
    },
    "bands": [
      {
        "key": "pace",
        "students": null,
        "share": null,
        "retention": {
          "students": null,
          "retained": null,
          "rate": null
        }
      },
      {
        "key": "minimum",
        "students": null,
        "share": null,
        "retention": {
          "students": null,
          "retained": null,
          "rate": null
        }
      },
      {
        "key": "below",
        "students": 32,
        "share": 0.4848,
        "retention": {
          "students": 32,
          "retained": 26,
          "rate": 0.8125
        }
      },
      {
        "key": "stopped",
        "students": 21,
        "share": 0.3182,
        "retention": {
          "students": 21,
          "retained": 14,
          "rate": 0.6667
        }
      }
    ],
    "unsorted": 0,
    "below": {
      "students": 32,
      "reasons": [
        {
          "key": "under",
          "students": 21,
          "share": 0.6562
        },
        {
          "key": "failed",
          "students": null,
          "share": null
        },
        {
          "key": "withdrew",
          "students": null,
          "share": null
        },
        {
          "key": "not_counted",
          "students": null,
          "share": null
        }
      ],
      "unexplained": null
    },
    "year_two_follow_up": {
      "status": "ok",
      "students": 13,
      "again": {
        "students": null,
        "share": null
      },
      "kept_taking_courses": {
        "students": null,
        "share": null
      },
      "no_courses": {
        "students": 0,
        "share": 0.0
      }
    },
    "both_years": {
      "students": null,
      "share": null
    }
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
  "progress": null,
  "credits": null,
  "completion": null,
  "milestones": [],
  "terms": [],
  "tiers": []
};
