// Real answers from GET /uncf/dfw and /uncf/dfw/course on the synthetic sample data (pdp.sqlite), for stories and tests.
// The course list keeps 29 of the 310 courses (the top by DFW count and by rate) to stay small; every
// number is as the API sent it. Regenerate with uncf/dfw_courses.py; don't edit the numbers by hand.
import type { DfwCourseDetail, DfwList } from "./dfw-data";

/** 2023-24, every student who entered: the DFW list. */
export const dfwList2023: DfwList = {
  "meta": {
    "cohort": "2023-24",
    "filters": {},
    "provisional": false,
    "min_students": 10,
    "source": "PDP analysis-ready cohort and course files (synthetic sample)",
    "loaded_at": "2026-11-10T06:18:59"
  },
  "status": "ok",
  "everyone": {
    "students": 2332,
    "num": 4347,
    "den": 18883,
    "rate": 0.2302,
    "split": {
      "DF": 2870,
      "W": 1477,
      "total": 18883
    }
  },
  "courses": [
    {
      "course": "ENG 101",
      "names": {
        "top": [
          "COMPOSITION I",
          "ENG-101",
          "ENGLISH COMP 1"
        ],
        "distinct": 11
      },
      "students": 439,
      "num": 135,
      "den": 492,
      "rate": 0.2744,
      "split": {
        "DF": 88,
        "W": 47,
        "total": 492
      },
      "gateway": {
        "M": 0,
        "E": 492
      }
    },
    {
      "course": "ENG 102",
      "names": {
        "top": [
          "COMPOSITION II",
          "ENGLISH COMP 2",
          "ENG-102"
        ],
        "distinct": 9
      },
      "students": 310,
      "num": 79,
      "den": 347,
      "rate": 0.2277,
      "split": {
        "DF": 49,
        "W": 30,
        "total": 347
      },
      "gateway": {
        "M": 0,
        "E": 29
      }
    },
    {
      "course": "ENGL 101",
      "names": {
        "top": [
          "ENGLISH COMPOSITION I",
          "COMPOSITION II"
        ],
        "distinct": 2
      },
      "students": 178,
      "num": 73,
      "den": 210,
      "rate": 0.3476,
      "split": {
        "DF": 47,
        "W": 26,
        "total": 210
      },
      "gateway": {
        "M": 0,
        "E": 85
      }
    },
    {
      "course": "COM 101",
      "names": {
        "top": [
          "COM-101",
          "FOUNDATIONS OF COMMUNICATION",
          "INTRODUCTION TO PUBLIC SPEAKING"
        ],
        "distinct": 3
      },
      "students": 127,
      "num": 50,
      "den": 131,
      "rate": 0.3817,
      "split": {
        "DF": 37,
        "W": 13,
        "total": 131
      },
      "gateway": {
        "M": 0,
        "E": 0
      }
    },
    {
      "course": "MA 119",
      "names": {
        "top": [
          "COLLEGE ALGEBRA"
        ],
        "distinct": 1
      },
      "students": 76,
      "num": 49,
      "den": 103,
      "rate": 0.4757,
      "split": {
        "DF": 29,
        "W": 20,
        "total": 103
      },
      "gateway": {
        "M": 0,
        "E": 0
      }
    },
    {
      "course": "ENG 121",
      "names": {
        "top": [
          "ENGLISH COMPOSITION I"
        ],
        "distinct": 1
      },
      "students": 94,
      "num": 44,
      "den": 120,
      "rate": 0.3667,
      "split": {
        "DF": 18,
        "W": 26,
        "total": 120
      },
      "gateway": {
        "M": 0,
        "E": 60
      }
    },
    {
      "course": "PSY 101",
      "names": {
        "top": [
          "PSY-101",
          "INTRODUCTION TO PSYCHOLOGY",
          "INTRO PSYCHOLOGY"
        ],
        "distinct": 4
      },
      "students": 218,
      "num": 44,
      "den": 227,
      "rate": 0.1938,
      "split": {
        "DF": 36,
        "W": 8,
        "total": 227
      },
      "gateway": {
        "M": 0,
        "E": 0
      }
    },
    {
      "course": "PSYC 101",
      "names": {
        "top": [
          "GENERAL PSYCHOLOGY",
          "PSYCHOLOGY"
        ],
        "distinct": 2
      },
      "students": 119,
      "num": 43,
      "den": 130,
      "rate": 0.3308,
      "split": {
        "DF": 32,
        "W": 11,
        "total": 130
      },
      "gateway": {
        "M": 0,
        "E": 0
      }
    },
    {
      "course": "PSY 121",
      "names": {
        "top": [
          "INTRODUCTION TO PSYCHOLOGY",
          "GENERAL PSYCHOLOGY"
        ],
        "distinct": 2
      },
      "students": 106,
      "num": 34,
      "den": 118,
      "rate": 0.2881,
      "split": {
        "DF": 23,
        "W": 11,
        "total": 118
      },
      "gateway": {
        "M": 0,
        "E": 0
      }
    },
    {
      "course": "ENG 100",
      "names": {
        "top": [
          "ENG-100",
          "ENGLISH COMPOSITION SUPPORT",
          "COMPOSITION SKILLS"
        ],
        "distinct": 3
      },
      "students": 66,
      "num": 33,
      "den": 75,
      "rate": 0.44,
      "split": {
        "DF": 25,
        "W": 8,
        "total": 75
      },
      "gateway": {
        "M": 0,
        "E": 0
      }
    },
    {
      "course": "ENGL 121",
      "names": {
        "top": [
          "COLLEGE COMPOSITION"
        ],
        "distinct": 1
      },
      "students": 44,
      "num": 32,
      "den": 64,
      "rate": 0.5,
      "split": {
        "DF": 22,
        "W": 10,
        "total": 64
      },
      "gateway": {
        "M": 0,
        "E": 28
      }
    },
    {
      "course": "SSC 100",
      "names": {
        "top": [
          "FIRST YEAR SEMINAR",
          "FIRST YEAR SEMINAR - ITN"
        ],
        "distinct": 2
      },
      "students": 102,
      "num": 32,
      "den": 120,
      "rate": 0.2667,
      "split": {
        "DF": 32,
        "W": 0,
        "total": 120
      },
      "gateway": {
        "M": 0,
        "E": 0
      }
    },
    {
      "course": "SOC 101",
      "names": {
        "top": [
          "SOC-101",
          "INTRODUCTION TO SOCIOLOGY",
          "INTRO SOCIOLOGY"
        ],
        "distinct": 6
      },
      "students": 116,
      "num": 28,
      "den": 122,
      "rate": 0.2295,
      "split": {
        "DF": 23,
        "W": 5,
        "total": 122
      },
      "gateway": {
        "M": 0,
        "E": 0
      }
    },
    {
      "course": "ENGL 102",
      "names": {
        "top": [
          "ENGLISH COMPOSITION II"
        ],
        "distinct": 1
      },
      "students": 89,
      "num": 26,
      "den": 97,
      "rate": 0.268,
      "split": {
        "DF": 14,
        "W": 12,
        "total": 97
      },
      "gateway": {
        "M": 0,
        "E": 0
      }
    },
    {
      "course": "BUS 101",
      "names": {
        "top": [
          "BUS-101",
          "INTRODUCTION TO BUSINESS",
          "INTRO TO BUSINESS"
        ],
        "distinct": 5
      },
      "students": 75,
      "num": 25,
      "den": 80,
      "rate": 0.3125,
      "split": {
        "DF": 20,
        "W": 5,
        "total": 80
      },
      "gateway": {
        "M": 0,
        "E": 0
      }
    },
    {
      "course": "CLC 120",
      "names": {
        "top": [
          "COLLEGE SUCCESS SEMINAR"
        ],
        "distinct": 1
      },
      "students": 99,
      "num": 25,
      "den": 116,
      "rate": 0.2155,
      "split": {
        "DF": 8,
        "W": 17,
        "total": 116
      },
      "gateway": {
        "M": 0,
        "E": 0
      }
    },
    {
      "course": "PSC 101",
      "names": {
        "top": [
          "PSC-101",
          "AMERICAN POLITICS/GOVERNMENT"
        ],
        "distinct": 2
      },
      "students": 72,
      "num": 24,
      "den": 75,
      "rate": 0.32,
      "split": {
        "DF": 17,
        "W": 7,
        "total": 75
      },
      "gateway": {
        "M": 0,
        "E": 0
      }
    },
    {
      "course": "BIO 110",
      "names": {
        "top": [
          "INTRO BIO SCIENCE",
          "PRINCIPLES OF BIOLOGY",
          "ESSENTLS-ANATOMY & PHYSIOLOGY"
        ],
        "distinct": 7
      },
      "students": 77,
      "num": 23,
      "den": 88,
      "rate": 0.2614,
      "split": {
        "DF": 10,
        "W": 13,
        "total": 88
      },
      "gateway": {
        "M": 0,
        "E": 0
      }
    },
    {
      "course": "PSY 100",
      "names": {
        "top": [
          "INTRODUCTION TO PSYCHOLOGY",
          "INTRO TO PSYCHOLOGY",
          "HUMAN RELATIONS"
        ],
        "distinct": 5
      },
      "students": 106,
      "num": 23,
      "den": 115,
      "rate": 0.2,
      "split": {
        "DF": 19,
        "W": 4,
        "total": 115
      },
      "gateway": {
        "M": 0,
        "E": 0
      }
    },
    {
      "course": "MAT 152",
      "names": {
        "top": [
          "QUANTITATIVE REASONING",
          "STATISTICAL METHODS I"
        ],
        "distinct": 2
      },
      "students": 65,
      "num": 22,
      "den": 75,
      "rate": 0.2933,
      "split": {
        "DF": 15,
        "W": 7,
        "total": 75
      },
      "gateway": {
        "M": 75,
        "E": 0
      }
    },
    {
      "course": "ACC 201",
      "names": {
        "top": [
          "ACC-201",
          "INTER ACCOUNT 1"
        ],
        "distinct": 2
      },
      "students": 36,
      "num": 19,
      "den": 39,
      "rate": 0.4872,
      "split": {
        "DF": 18,
        "W": 1,
        "total": 39
      },
      "gateway": {
        "M": 0,
        "E": 0
      }
    },
    {
      "course": "BIO 120",
      "names": {
        "top": [
          "ANATOMY AND PHYSIOLOGY I",
          "ENVIRONMENTAL BIOLOGY",
          "PRINCIPLES OF BIOLOGY I"
        ],
        "distinct": 4
      },
      "students": 60,
      "num": 19,
      "den": 69,
      "rate": 0.2754,
      "split": {
        "DF": 8,
        "W": 11,
        "total": 69
      },
      "gateway": {
        "M": 0,
        "E": 0
      }
    },
    {
      "course": "MATH 103",
      "names": {
        "top": [
          "COLLEGE ALGEBRA",
          "CONTEMPORARY MATH"
        ],
        "distinct": 2
      },
      "students": 27,
      "num": 18,
      "den": 35,
      "rate": 0.5143,
      "split": {
        "DF": 11,
        "W": 7,
        "total": 35
      },
      "gateway": {
        "M": 35,
        "E": 0
      }
    },
    {
      "course": "CHM 121",
      "names": {
        "top": [
          "GENERAL CHEMISTRY I",
          "GENERAL CHEMISTRY",
          "GENERAL CHEMISTRY I/HONORS"
        ],
        "distinct": 3
      },
      "students": 35,
      "num": 18,
      "den": 40,
      "rate": 0.45,
      "split": {
        "DF": 7,
        "W": 11,
        "total": 40
      },
      "gateway": {
        "M": 0,
        "E": 0
      }
    },
    {
      "course": "BIO 101",
      "names": {
        "top": [
          "BIOLOGY SURVEY",
          "INTRO TO BIOLOGY LABORATORY",
          "GENERAL BIOLOGY I"
        ],
        "distinct": 6
      },
      "students": 51,
      "num": 18,
      "den": 56,
      "rate": 0.3214,
      "split": {
        "DF": 12,
        "W": 6,
        "total": 56
      },
      "gateway": {
        "M": 0,
        "E": 0
      }
    },
    {
      "course": "BI 301",
      "names": {
        "top": [
          "ANATOMY AND PHYSIOLOGY I"
        ],
        "distinct": 1
      },
      "students": 29,
      "num": 17,
      "den": 33,
      "rate": 0.5152,
      "split": {
        "DF": 7,
        "W": 10,
        "total": 33
      },
      "gateway": {
        "M": 0,
        "E": 0
      }
    },
    {
      "course": "MTH 103",
      "names": {
        "top": [
          "COLLEGE ALGEBRA",
          "TECHNICAL MATHEMATICS"
        ],
        "distinct": 2
      },
      "students": 22,
      "num": 17,
      "den": 35,
      "rate": 0.4857,
      "split": {
        "DF": 8,
        "W": 9,
        "total": 35
      },
      "gateway": {
        "M": 35,
        "E": 0
      }
    },
    {
      "course": "CIS 107",
      "names": {
        "top": [
          "INTRO TO COMPUTERS/APPLICATION",
          "INFO TECHNOLOGY FUNDAMENTALS"
        ],
        "distinct": 2
      },
      "students": 37,
      "num": 17,
      "den": 40,
      "rate": 0.425,
      "split": {
        "DF": 13,
        "W": 4,
        "total": 40
      },
      "gateway": {
        "M": 0,
        "E": 0
      }
    },
    {
      "course": "MATH 138",
      "names": {
        "top": [
          "STATISTICS"
        ],
        "distinct": 1
      },
      "students": 30,
      "num": 15,
      "den": 39,
      "rate": 0.3846,
      "split": {
        "DF": 12,
        "W": 3,
        "total": 39
      },
      "gateway": {
        "M": 14,
        "E": 0
      }
    }
  ],
  "hidden_courses": 4485
};

/** 2023-24: ENG 101 in detail. */
export const eng101Detail2023: DfwCourseDetail = {
  "meta": {
    "cohort": "2023-24",
    "filters": {},
    "provisional": false,
    "min_students": 10,
    "source": "PDP analysis-ready cohort and course files (synthetic sample)",
    "loaded_at": "2026-11-10T06:18:59"
  },
  "course": "ENG 101",
  "names": {
    "top": [
      "COMPOSITION I",
      "ENG-101",
      "ENGLISH COMP 1"
    ],
    "distinct": 11
  },
  "students": 439,
  "num": 135,
  "den": 492,
  "rate": 0.2744,
  "split": {
    "DF": 88,
    "W": 47,
    "total": 492
  },
  "terms": [
    {
      "value": "Fall",
      "students": 286,
      "num": 92,
      "den": 295,
      "rate": 0.3119,
      "split": {
        "DF": 65,
        "W": 27,
        "total": 295
      }
    },
    {
      "value": "Spring",
      "students": 146,
      "num": 34,
      "den": 149,
      "rate": 0.2282,
      "split": {
        "DF": 17,
        "W": 17,
        "total": 149
      }
    },
    {
      "value": "Summer",
      "students": 46,
      "num": 9,
      "den": 48,
      "rate": 0.1875,
      "split": {
        "DF": 6,
        "W": 3,
        "total": 48
      }
    }
  ],
  "delivery": [
    {
      "value": "Face-to-face",
      "students": 170,
      "num": 50,
      "den": 185,
      "rate": 0.2703,
      "split": {
        "DF": 31,
        "W": 19,
        "total": 185
      }
    },
    {
      "value": "Hybrid",
      "students": 60,
      "num": 11,
      "den": 61,
      "rate": 0.1803,
      "split": {
        "DF": 7,
        "W": 4,
        "total": 61
      }
    },
    {
      "value": "Online",
      "students": 126,
      "num": 49,
      "den": 137,
      "rate": 0.3577,
      "split": {
        "DF": 34,
        "W": 15,
        "total": 137
      }
    },
    {
      "value": "Blank",
      "students": 100,
      "num": 25,
      "den": 109,
      "rate": 0.2294,
      "split": {
        "DF": 16,
        "W": 9,
        "total": 109
      }
    }
  ],
  "groups": {
    "pell": [
      {
        "value": "N",
        "students": 196,
        "num": 54,
        "den": 217,
        "rate": 0.2488,
        "split": {
          "DF": 34,
          "W": 20,
          "total": 217
        }
      },
      {
        "value": "UNKNOWN",
        "students": 16,
        "num": 5,
        "den": 17,
        "rate": 0.2941,
        "split": {
          "DF": 4,
          "W": 1,
          "total": 17
        }
      },
      {
        "value": "Y",
        "students": 227,
        "num": 76,
        "den": 258,
        "rate": 0.2946,
        "split": {
          "DF": 50,
          "W": 26,
          "total": 258
        }
      }
    ],
    "gender": [
      {
        "value": "F",
        "students": 246,
        "num": 75,
        "den": 278,
        "rate": 0.2698,
        "split": {
          "DF": 50,
          "W": 25,
          "total": 278
        }
      },
      {
        "value": "M",
        "students": 175,
        "num": 52,
        "den": 193,
        "rate": 0.2694,
        "split": {
          "DF": 30,
          "W": 22,
          "total": 193
        }
      },
      {
        "value": "UNKNOWN",
        "students": 18,
        "num": 8,
        "den": 21,
        "rate": 0.381,
        "split": {
          "DF": 8,
          "W": 0,
          "total": 21
        }
      }
    ],
    "race": [
      {
        "value": "American Indian or Alaska Native",
        "students": null,
        "num": null,
        "den": null,
        "rate": null,
        "split": null
      },
      {
        "value": "Asian",
        "students": 34,
        "num": 6,
        "den": 38,
        "rate": 0.1579,
        "split": {
          "DF": 4,
          "W": 2,
          "total": 38
        }
      },
      {
        "value": "Black or African American",
        "students": 73,
        "num": 33,
        "den": 87,
        "rate": 0.3793,
        "split": {
          "DF": 23,
          "W": 10,
          "total": 87
        }
      },
      {
        "value": "Hispanic",
        "students": 130,
        "num": 40,
        "den": 141,
        "rate": 0.2837,
        "split": {
          "DF": 27,
          "W": 13,
          "total": 141
        }
      },
      {
        "value": "Native Hawaiian or Other Pacific Islander",
        "students": null,
        "num": null,
        "den": null,
        "rate": null,
        "split": null
      },
      {
        "value": "Nonresident alien",
        "students": 11,
        "num": 5,
        "den": 13,
        "rate": 0.3846,
        "split": {
          "DF": 2,
          "W": 3,
          "total": 13
        }
      },
      {
        "value": "Two or More Races",
        "students": 13,
        "num": 4,
        "den": 13,
        "rate": 0.3077,
        "split": {
          "DF": 2,
          "W": 2,
          "total": 13
        }
      },
      {
        "value": "UNKNOWN",
        "students": 16,
        "num": 5,
        "den": 19,
        "rate": 0.2632,
        "split": {
          "DF": 4,
          "W": 1,
          "total": 19
        }
      },
      {
        "value": "White",
        "students": 156,
        "num": 39,
        "den": 175,
        "rate": 0.2229,
        "split": {
          "DF": 23,
          "W": 16,
          "total": 175
        }
      }
    ],
    "age_band": [
      {
        "value": "20 and younger",
        "students": 293,
        "num": 103,
        "den": 338,
        "rate": 0.3047,
        "split": {
          "DF": 67,
          "W": 36,
          "total": 338
        }
      },
      {
        "value": "> 20-24",
        "students": 69,
        "num": 20,
        "den": 74,
        "rate": 0.2703,
        "split": {
          "DF": 14,
          "W": 6,
          "total": 74
        }
      },
      {
        "value": "Older than 24",
        "students": 77,
        "num": 12,
        "den": 80,
        "rate": 0.15,
        "split": {
          "DF": 7,
          "W": 5,
          "total": 80
        }
      }
    ],
    "enrollment_intensity": [
      {
        "value": "Full-time",
        "students": 272,
        "num": 77,
        "den": 305,
        "rate": 0.2525,
        "split": {
          "DF": 48,
          "W": 29,
          "total": 305
        }
      },
      {
        "value": "Part-time",
        "students": 167,
        "num": 58,
        "den": 187,
        "rate": 0.3102,
        "split": {
          "DF": 40,
          "W": 18,
          "total": 187
        }
      }
    ],
    "enrollment_type": [
      {
        "value": "First-time",
        "students": 351,
        "num": 106,
        "den": 397,
        "rate": 0.267,
        "split": {
          "DF": 70,
          "W": 36,
          "total": 397
        }
      },
      {
        "value": "Transfer-in",
        "students": 88,
        "num": 29,
        "den": 95,
        "rate": 0.3053,
        "split": {
          "DF": 18,
          "W": 11,
          "total": 95
        }
      }
    ],
    "cohort_term": [
      {
        "value": "Fall",
        "students": 349,
        "num": 121,
        "den": 397,
        "rate": 0.3048,
        "split": {
          "DF": 82,
          "W": 39,
          "total": 397
        }
      },
      {
        "value": "Spring",
        "students": 77,
        "num": 13,
        "den": 81,
        "rate": 0.1605,
        "split": {
          "DF": 5,
          "W": 8,
          "total": 81
        }
      },
      {
        "value": "Summer",
        "students": 13,
        "num": 1,
        "den": 14,
        "rate": 0.0714,
        "split": {
          "DF": 1,
          "W": 0,
          "total": 14
        }
      }
    ]
  }
};
