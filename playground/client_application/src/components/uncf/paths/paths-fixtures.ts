// Real answers from the shared API (GET /uncf/student-paths and /uncf/cohort-options) on the synthetic sample data
// (pdp.sqlite), saved for stories and tests with the queries the tab sends. Regenerate them from the running API
// (measures/breakdowns/student_paths.py); don't edit the numbers by hand.
import type { CohortOptions } from "@/components/uncf/layout/explorer-api";

import type { PathsResponse } from "./paths-data";

/** 2023-24, first-time Fall starters. */
export const fallStarters2023: PathsResponse = {
  "meta": {
    "cohort": "2023-24",
    "filters": {
      "cohort_term": "Fall",
      "enrollment_type": "First-time"
    },
    "retention_type": "school",
    "provisional": false,
    "min_students": 10,
    "source": "PDP analysis-ready cohort and course files (synthetic sample)",
    "loaded_at": "2026-11-10T06:18:59",
    "terms": {
      "entered": "Fall 2023",
      "next": "Spring 2024",
      "year2": "Fall 2024"
    },
    "term_labels": [
      "Fall 2023",
      "Spring 2024",
      "Fall 2024"
    ],
    "group_by": null
  },
  "status": "ok",
  "students": 1114,
  "retention": {
    "type": "school",
    "status": "ok",
    "retained": 664,
    "students": 1114,
    "numerator": 664,
    "denominator": 1114,
    "rate": 0.5961,
    "n_excluded": 0,
    "n_out_of_scope": 0
  },
  "left_out": 0,
  "columns": {
    "next": {
      "position": 1,
      "label": "Spring 2024",
      "here": 642,
      "credential": 0,
      "elsewhere": 33,
      "stopped": 439,
      "anywhere": 675,
      "not_observed": 0,
      "shares": {
        "here": 0.5763,
        "credential": 0.0,
        "elsewhere": 0.0296,
        "stopped": 0.3941,
        "anywhere": 0.6059
      }
    },
    "year2": {
      "position": 2,
      "label": "Fall 2024",
      "here": 522,
      "credential": 27,
      "elsewhere": 60,
      "stopped": 505,
      "anywhere": 582,
      "not_observed": 0,
      "shares": {
        "here": 0.4686,
        "credential": 0.0242,
        "elsewhere": 0.0539,
        "stopped": 0.4533,
        "anywhere": 0.5224
      }
    }
  },
  "path": [
    {
      "position": 1,
      "label": "Spring 2024",
      "here": 642,
      "credential": 0,
      "elsewhere": 33,
      "stopped": 439,
      "anywhere": 675,
      "not_observed": 0,
      "shares": {
        "here": 0.5763,
        "credential": 0.0,
        "elsewhere": 0.0296,
        "stopped": 0.3941,
        "anywhere": 0.6059
      }
    },
    {
      "position": 2,
      "label": "Fall 2024",
      "here": 522,
      "credential": 27,
      "elsewhere": 60,
      "stopped": 505,
      "anywhere": 582,
      "not_observed": 0,
      "shares": {
        "here": 0.4686,
        "credential": 0.0242,
        "elsewhere": 0.0539,
        "stopped": 0.4533,
        "anywhere": 0.5224
      }
    }
  ],
  "moves": [
    {
      "from": "here",
      "to": "here",
      "students": 423
    },
    {
      "from": "here",
      "to": "credential",
      "students": 13
    },
    {
      "from": "here",
      "to": "elsewhere",
      "students": 23
    },
    {
      "from": "here",
      "to": "stopped",
      "students": 183
    },
    {
      "from": "credential",
      "to": "here",
      "students": 0
    },
    {
      "from": "credential",
      "to": "credential",
      "students": 0
    },
    {
      "from": "credential",
      "to": "elsewhere",
      "students": 0
    },
    {
      "from": "credential",
      "to": "stopped",
      "students": 0
    },
    {
      "from": "elsewhere",
      "to": "here",
      "students": null
    },
    {
      "from": "elsewhere",
      "to": "credential",
      "students": null
    },
    {
      "from": "elsewhere",
      "to": "elsewhere",
      "students": 22
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
      "to": "credential",
      "students": 13
    },
    {
      "from": "stopped",
      "to": "elsewhere",
      "students": 15
    },
    {
      "from": "stopped",
      "to": "stopped",
      "students": 315
    }
  ],
  "moves_by_step": [
    {
      "from_position": 1,
      "to_position": 2,
      "moves": [
        {
          "from": "here",
          "to": "here",
          "students": 423
        },
        {
          "from": "here",
          "to": "credential",
          "students": 13
        },
        {
          "from": "here",
          "to": "elsewhere",
          "students": 23
        },
        {
          "from": "here",
          "to": "stopped",
          "students": 183
        },
        {
          "from": "credential",
          "to": "here",
          "students": 0
        },
        {
          "from": "credential",
          "to": "credential",
          "students": 0
        },
        {
          "from": "credential",
          "to": "elsewhere",
          "students": 0
        },
        {
          "from": "credential",
          "to": "stopped",
          "students": 0
        },
        {
          "from": "elsewhere",
          "to": "here",
          "students": null
        },
        {
          "from": "elsewhere",
          "to": "credential",
          "students": null
        },
        {
          "from": "elsewhere",
          "to": "elsewhere",
          "students": 22
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
          "to": "credential",
          "students": 13
        },
        {
          "from": "stopped",
          "to": "elsewhere",
          "students": 15
        },
        {
          "from": "stopped",
          "to": "stopped",
          "students": 315
        }
      ]
    }
  ],
  "transfers": {
    "students": 60,
    "four_year": 35,
    "two_year": 16,
    "other": null
  },
  "groups": []
};

/** 2023-24, first-time students of every starting term. */
export const allStarters2023: PathsResponse = {
  "meta": {
    "cohort": "2023-24",
    "filters": {
      "enrollment_type": "First-time"
    },
    "retention_type": "school",
    "provisional": false,
    "min_students": 10,
    "source": "PDP analysis-ready cohort and course files (synthetic sample)",
    "loaded_at": "2026-11-10T06:18:59",
    "terms": null,
    "term_labels": null,
    "group_by": null
  },
  "status": "ok",
  "students": 1627,
  "retention": {
    "type": "school",
    "status": "ok",
    "retained": 917,
    "students": 1627,
    "numerator": 917,
    "denominator": 1627,
    "rate": 0.5636,
    "n_excluded": 0,
    "n_out_of_scope": 0
  },
  "left_out": 0,
  "columns": {
    "next": {
      "position": 1,
      "label": null,
      "here": 867,
      "credential": 22,
      "elsewhere": 92,
      "stopped": 646,
      "anywhere": 959,
      "not_observed": 0,
      "shares": {
        "here": 0.5329,
        "credential": 0.0135,
        "elsewhere": 0.0565,
        "stopped": 0.397,
        "anywhere": 0.5894
      }
    },
    "year2": {
      "position": 2,
      "label": null,
      "here": 714,
      "credential": 52,
      "elsewhere": 121,
      "stopped": 740,
      "anywhere": 835,
      "not_observed": 0,
      "shares": {
        "here": 0.4388,
        "credential": 0.032,
        "elsewhere": 0.0744,
        "stopped": 0.4548,
        "anywhere": 0.5132
      }
    }
  },
  "path": [
    {
      "position": 1,
      "label": null,
      "here": 867,
      "credential": 22,
      "elsewhere": 92,
      "stopped": 646,
      "anywhere": 959,
      "not_observed": 0,
      "shares": {
        "here": 0.5329,
        "credential": 0.0135,
        "elsewhere": 0.0565,
        "stopped": 0.397,
        "anywhere": 0.5894
      }
    },
    {
      "position": 2,
      "label": null,
      "here": 714,
      "credential": 52,
      "elsewhere": 121,
      "stopped": 740,
      "anywhere": 835,
      "not_observed": 0,
      "shares": {
        "here": 0.4388,
        "credential": 0.032,
        "elsewhere": 0.0744,
        "stopped": 0.4548,
        "anywhere": 0.5132
      }
    }
  ],
  "moves": [
    {
      "from": "here",
      "to": "here",
      "students": 584
    },
    {
      "from": "here",
      "to": "credential",
      "students": 16
    },
    {
      "from": "here",
      "to": "elsewhere",
      "students": 33
    },
    {
      "from": "here",
      "to": "stopped",
      "students": 234
    },
    {
      "from": "credential",
      "to": "here",
      "students": 0
    },
    {
      "from": "credential",
      "to": "credential",
      "students": 22
    },
    {
      "from": "credential",
      "to": "elsewhere",
      "students": 0
    },
    {
      "from": "credential",
      "to": "stopped",
      "students": 0
    },
    {
      "from": "elsewhere",
      "to": "here",
      "students": null
    },
    {
      "from": "elsewhere",
      "to": "credential",
      "students": null
    },
    {
      "from": "elsewhere",
      "to": "elsewhere",
      "students": 72
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
      "to": "credential",
      "students": 13
    },
    {
      "from": "stopped",
      "to": "elsewhere",
      "students": 16
    },
    {
      "from": "stopped",
      "to": "stopped",
      "students": 493
    }
  ],
  "moves_by_step": [
    {
      "from_position": 1,
      "to_position": 2,
      "moves": [
        {
          "from": "here",
          "to": "here",
          "students": 584
        },
        {
          "from": "here",
          "to": "credential",
          "students": 16
        },
        {
          "from": "here",
          "to": "elsewhere",
          "students": 33
        },
        {
          "from": "here",
          "to": "stopped",
          "students": 234
        },
        {
          "from": "credential",
          "to": "here",
          "students": 0
        },
        {
          "from": "credential",
          "to": "credential",
          "students": 22
        },
        {
          "from": "credential",
          "to": "elsewhere",
          "students": 0
        },
        {
          "from": "credential",
          "to": "stopped",
          "students": 0
        },
        {
          "from": "elsewhere",
          "to": "here",
          "students": null
        },
        {
          "from": "elsewhere",
          "to": "credential",
          "students": null
        },
        {
          "from": "elsewhere",
          "to": "elsewhere",
          "students": 72
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
          "to": "credential",
          "students": 13
        },
        {
          "from": "stopped",
          "to": "elsewhere",
          "students": 16
        },
        {
          "from": "stopped",
          "to": "stopped",
          "students": 493
        }
      ]
    }
  ],
  "transfers": {
    "students": 121,
    "four_year": 73,
    "two_year": 30,
    "other": 18
  },
  "groups": []
};

/** 2023-24 Fall starters of every enrollment type (Enrollment type: All). */
export const everyEnrollmentType2023: PathsResponse = {
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
    "terms": {
      "entered": "Fall 2023",
      "next": "Spring 2024",
      "year2": "Fall 2024"
    },
    "term_labels": [
      "Fall 2023",
      "Spring 2024",
      "Fall 2024"
    ],
    "group_by": null
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
  "left_out": 0,
  "columns": {
    "next": {
      "position": 1,
      "label": "Spring 2024",
      "here": 876,
      "credential": 0,
      "elsewhere": 85,
      "stopped": 623,
      "anywhere": 961,
      "not_observed": 0,
      "shares": {
        "here": 0.553,
        "credential": 0.0,
        "elsewhere": 0.0537,
        "stopped": 0.3933,
        "anywhere": 0.6067
      }
    },
    "year2": {
      "position": 2,
      "label": "Fall 2024",
      "here": 699,
      "credential": 51,
      "elsewhere": 133,
      "stopped": 701,
      "anywhere": 832,
      "not_observed": 0,
      "shares": {
        "here": 0.4413,
        "credential": 0.0322,
        "elsewhere": 0.084,
        "stopped": 0.4426,
        "anywhere": 0.5253
      }
    }
  },
  "path": [
    {
      "position": 1,
      "label": "Spring 2024",
      "here": 876,
      "credential": 0,
      "elsewhere": 85,
      "stopped": 623,
      "anywhere": 961,
      "not_observed": 0,
      "shares": {
        "here": 0.553,
        "credential": 0.0,
        "elsewhere": 0.0537,
        "stopped": 0.3933,
        "anywhere": 0.6067
      }
    },
    {
      "position": 2,
      "label": "Fall 2024",
      "here": 699,
      "credential": 51,
      "elsewhere": 133,
      "stopped": 701,
      "anywhere": 832,
      "not_observed": 0,
      "shares": {
        "here": 0.4413,
        "credential": 0.0322,
        "elsewhere": 0.084,
        "stopped": 0.4426,
        "anywhere": 0.5253
      }
    }
  ],
  "moves": [
    {
      "from": "here",
      "to": "here",
      "students": 554
    },
    {
      "from": "here",
      "to": "credential",
      "students": 29
    },
    {
      "from": "here",
      "to": "elsewhere",
      "students": 39
    },
    {
      "from": "here",
      "to": "stopped",
      "students": 254
    },
    {
      "from": "credential",
      "to": "here",
      "students": 0
    },
    {
      "from": "credential",
      "to": "credential",
      "students": 0
    },
    {
      "from": "credential",
      "to": "elsewhere",
      "students": 0
    },
    {
      "from": "credential",
      "to": "stopped",
      "students": 0
    },
    {
      "from": "elsewhere",
      "to": "here",
      "students": null
    },
    {
      "from": "elsewhere",
      "to": "credential",
      "students": null
    },
    {
      "from": "elsewhere",
      "to": "elsewhere",
      "students": 67
    },
    {
      "from": "elsewhere",
      "to": "stopped",
      "students": 13
    },
    {
      "from": "stopped",
      "to": "here",
      "students": 141
    },
    {
      "from": "stopped",
      "to": "credential",
      "students": 21
    },
    {
      "from": "stopped",
      "to": "elsewhere",
      "students": 27
    },
    {
      "from": "stopped",
      "to": "stopped",
      "students": 434
    }
  ],
  "moves_by_step": [
    {
      "from_position": 1,
      "to_position": 2,
      "moves": [
        {
          "from": "here",
          "to": "here",
          "students": 554
        },
        {
          "from": "here",
          "to": "credential",
          "students": 29
        },
        {
          "from": "here",
          "to": "elsewhere",
          "students": 39
        },
        {
          "from": "here",
          "to": "stopped",
          "students": 254
        },
        {
          "from": "credential",
          "to": "here",
          "students": 0
        },
        {
          "from": "credential",
          "to": "credential",
          "students": 0
        },
        {
          "from": "credential",
          "to": "elsewhere",
          "students": 0
        },
        {
          "from": "credential",
          "to": "stopped",
          "students": 0
        },
        {
          "from": "elsewhere",
          "to": "here",
          "students": null
        },
        {
          "from": "elsewhere",
          "to": "credential",
          "students": null
        },
        {
          "from": "elsewhere",
          "to": "elsewhere",
          "students": 67
        },
        {
          "from": "elsewhere",
          "to": "stopped",
          "students": 13
        },
        {
          "from": "stopped",
          "to": "here",
          "students": 141
        },
        {
          "from": "stopped",
          "to": "credential",
          "students": 21
        },
        {
          "from": "stopped",
          "to": "elsewhere",
          "students": 27
        },
        {
          "from": "stopped",
          "to": "stopped",
          "students": 434
        }
      ]
    }
  ],
  "transfers": {
    "students": 133,
    "four_year": 85,
    "two_year": 27,
    "other": 21
  },
  "groups": []
};

/** 2024-25, first-time Fall starters: their second year is only partly in the data. */
export const fallStarters2024: PathsResponse = {
  "meta": {
    "cohort": "2024-25",
    "filters": {
      "cohort_term": "Fall",
      "enrollment_type": "First-time"
    },
    "retention_type": "school",
    "provisional": true,
    "min_students": 10,
    "source": "PDP analysis-ready cohort and course files (synthetic sample)",
    "loaded_at": "2026-11-10T06:18:59",
    "terms": {
      "entered": "Fall 2024",
      "next": "Spring 2025",
      "year2": "Fall 2025"
    },
    "term_labels": [
      "Fall 2024",
      "Spring 2025",
      "Fall 2025"
    ],
    "group_by": null
  },
  "status": "ok",
  "students": 1080,
  "retention": {
    "type": "school",
    "status": "ok",
    "retained": 559,
    "students": 1080,
    "numerator": 559,
    "denominator": 1080,
    "rate": 0.5176,
    "n_excluded": 0,
    "n_out_of_scope": 0
  },
  "left_out": 0,
  "columns": {
    "next": {
      "position": 1,
      "label": "Spring 2025",
      "here": 700,
      "credential": 0,
      "elsewhere": 37,
      "stopped": 343,
      "anywhere": 737,
      "not_observed": 0,
      "shares": {
        "here": 0.6481,
        "credential": 0.0,
        "elsewhere": 0.0343,
        "stopped": 0.3176,
        "anywhere": 0.6824
      }
    },
    "year2": {
      "position": 2,
      "label": "Fall 2025",
      "here": 376,
      "credential": 27,
      "elsewhere": 90,
      "stopped": 587,
      "anywhere": 466,
      "not_observed": 0,
      "shares": {
        "here": 0.3481,
        "credential": 0.025,
        "elsewhere": 0.0833,
        "stopped": 0.5435,
        "anywhere": 0.4315
      }
    }
  },
  "path": [
    {
      "position": 1,
      "label": "Spring 2025",
      "here": 700,
      "credential": 0,
      "elsewhere": 37,
      "stopped": 343,
      "anywhere": 737,
      "not_observed": 0,
      "shares": {
        "here": 0.6481,
        "credential": 0.0,
        "elsewhere": 0.0343,
        "stopped": 0.3176,
        "anywhere": 0.6824
      }
    },
    {
      "position": 2,
      "label": "Fall 2025",
      "here": 376,
      "credential": 27,
      "elsewhere": 90,
      "stopped": 587,
      "anywhere": 466,
      "not_observed": 0,
      "shares": {
        "here": 0.3481,
        "credential": 0.025,
        "elsewhere": 0.0833,
        "stopped": 0.5435,
        "anywhere": 0.4315
      }
    }
  ],
  "moves": [
    {
      "from": "here",
      "to": "here",
      "students": 341
    },
    {
      "from": "here",
      "to": "credential",
      "students": 14
    },
    {
      "from": "here",
      "to": "elsewhere",
      "students": 45
    },
    {
      "from": "here",
      "to": "stopped",
      "students": 300
    },
    {
      "from": "credential",
      "to": "here",
      "students": 0
    },
    {
      "from": "credential",
      "to": "credential",
      "students": 0
    },
    {
      "from": "credential",
      "to": "elsewhere",
      "students": 0
    },
    {
      "from": "credential",
      "to": "stopped",
      "students": 0
    },
    {
      "from": "elsewhere",
      "to": "here",
      "students": null
    },
    {
      "from": "elsewhere",
      "to": "credential",
      "students": null
    },
    {
      "from": "elsewhere",
      "to": "elsewhere",
      "students": 27
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
      "to": "credential",
      "students": 12
    },
    {
      "from": "stopped",
      "to": "elsewhere",
      "students": 18
    },
    {
      "from": "stopped",
      "to": "stopped",
      "students": 281
    }
  ],
  "moves_by_step": [
    {
      "from_position": 1,
      "to_position": 2,
      "moves": [
        {
          "from": "here",
          "to": "here",
          "students": 341
        },
        {
          "from": "here",
          "to": "credential",
          "students": 14
        },
        {
          "from": "here",
          "to": "elsewhere",
          "students": 45
        },
        {
          "from": "here",
          "to": "stopped",
          "students": 300
        },
        {
          "from": "credential",
          "to": "here",
          "students": 0
        },
        {
          "from": "credential",
          "to": "credential",
          "students": 0
        },
        {
          "from": "credential",
          "to": "elsewhere",
          "students": 0
        },
        {
          "from": "credential",
          "to": "stopped",
          "students": 0
        },
        {
          "from": "elsewhere",
          "to": "here",
          "students": null
        },
        {
          "from": "elsewhere",
          "to": "credential",
          "students": null
        },
        {
          "from": "elsewhere",
          "to": "elsewhere",
          "students": 27
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
          "to": "credential",
          "students": 12
        },
        {
          "from": "stopped",
          "to": "elsewhere",
          "students": 18
        },
        {
          "from": "stopped",
          "to": "stopped",
          "students": 281
        }
      ]
    }
  ],
  "transfers": {
    "students": 90,
    "four_year": 51,
    "two_year": 26,
    "other": 13
  },
  "groups": []
};

/** A filter combination with fewer than 10 students: everything hidden. */
export const tooFewStudents: PathsResponse = {
  "meta": {
    "cohort": "2023-24",
    "filters": {
      "enrollment_type": "First-time",
      "gender": "M",
      "race": "Native Hawaiian or Other Pacific Islander"
    },
    "retention_type": "school",
    "provisional": false,
    "min_students": 10,
    "source": "PDP analysis-ready cohort and course files (synthetic sample)",
    "loaded_at": "2026-11-10T06:18:59",
    "terms": {
      "entered": "Fall 2023",
      "next": "Spring 2024",
      "year2": "Fall 2024"
    },
    "term_labels": [
      "Fall 2023",
      "Spring 2024",
      "Fall 2024"
    ],
    "group_by": null
  },
  "status": "suppressed",
  "students": null,
  "retention": null,
  "left_out": null,
  "columns": null,
  "path": [],
  "moves": null,
  "transfers": null,
  "groups": []
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
      "Summer": 319,
      "Winter": 21,
      "UNKNOWN": 0,
      "Fall": 1584,
      "Spring": 656
    },
    "enrollment_intensity": {
      "Part-time": 1501,
      "UNKNOWN": 72,
      "Full-time": 1007
    },
    "enrollment_type": {
      "UNKNOWN": null,
      "First-time": 1627,
      "Re-admit": 115,
      "Transfer-in": 837
    },
    "pell": {
      "N": 1496,
      "UNKNOWN": 211,
      "Y": 873
    },
    "gender": {
      "X": 0,
      "F": 1397,
      "M": 1051,
      "UNKNOWN": 132,
      "P": 0
    },
    "race": {
      "Hispanic": 710,
      "Native Hawaiian or Other Pacific Islander": null,
      "Two or More Races": 73,
      "UNKNOWN": 91,
      "Black or African American": 391,
      "Asian": 196,
      "American Indian or Alaska Native": 45,
      "White": 1011,
      "Nonresident alien": 54
    },
    "ethnicity": {
      "N": 314,
      "H": 729,
      "UNKNOWN": 1537
    },
    "age_band": {
      "Older than 24": 804,
      "UNKNOWN": 0,
      "20 and younger": 1233,
      "> 20-24": 543
    }
  },
  "labels": {
    "cohort_term": "Starting term",
    "enrollment_intensity": "Full or part time",
    "enrollment_type": "Enrollment type",
    "pell": "Pell grant",
    "gender": "Gender",
    "race": "Race",
    "ethnicity": "Ethnicity",
    "age_band": "Age"
  },
  "retention_types": [
    "school",
    "federal"
  ],
  "min_students": 10,
  "source": "PDP analysis-ready cohort and course files (synthetic sample)",
  "loaded_at": "2026-11-10T06:18:59"
};
