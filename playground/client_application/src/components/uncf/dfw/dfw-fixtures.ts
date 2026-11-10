// Real answers from the shared API (GET /uncf/dfw and /uncf/dfw/course) on the synthetic sample data (pdp.sqlite), for
// stories and tests. The course list keeps 29 of the 310 courses (the top by DFW count and by rate) to stay small;
// every number is as the API sent it. Regenerate from the running API (measures/breakdowns/dfw_courses.py); don't edit
// the numbers by hand.
import type { DfwCourseDetail, DfwList } from "./dfw-data";

/** 2023-24, every student who entered: the DFW list. */
export const dfwList2023: DfwList = {
  "meta": {
    "cohort": "2023-24",
    "filters": {},
    "retention_type": "school",
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
      "D": 608,
      "F": 2262,
      "W": 1477,
      "DF": 2870,
      "total": 18883,
      "shares": {
        "D": 0.0322,
        "F": 0.1198,
        "W": 0.0782
      }
    }
  },
  "courses": [
    {
      "students": 439,
      "num": 135,
      "den": 492,
      "rate": 0.2744,
      "split": {
        "D": 19,
        "F": 69,
        "W": 47,
        "DF": 88,
        "total": 492,
        "shares": {
          "D": 0.0386,
          "F": 0.1402,
          "W": 0.0955
        }
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
      "gateway": {
        "M": 0,
        "E": 492
      }
    },
    {
      "students": 310,
      "num": 79,
      "den": 347,
      "rate": 0.2277,
      "split": {
        "D": 15,
        "F": 34,
        "W": 30,
        "DF": 49,
        "total": 347,
        "shares": {
          "D": 0.0432,
          "F": 0.098,
          "W": 0.0865
        }
      },
      "course": "ENG 102",
      "names": {
        "top": [
          "COMPOSITION II",
          "ENGLISH COMP 2",
          "ENG-102"
        ],
        "distinct": 9
      },
      "gateway": {
        "M": 0,
        "E": 29
      }
    },
    {
      "students": 178,
      "num": 73,
      "den": 210,
      "rate": 0.3476,
      "split": {
        "D": 7,
        "F": 40,
        "W": 26,
        "DF": 47,
        "total": 210,
        "shares": {
          "D": 0.0333,
          "F": 0.1905,
          "W": 0.1238
        }
      },
      "course": "ENGL 101",
      "names": {
        "top": [
          "ENGLISH COMPOSITION I",
          "COMPOSITION II"
        ],
        "distinct": 2
      },
      "gateway": {
        "M": 0,
        "E": 85
      }
    },
    {
      "students": 127,
      "num": 50,
      "den": 131,
      "rate": 0.3817,
      "split": {
        "D": 5,
        "F": 32,
        "W": 13,
        "DF": 37,
        "total": 131,
        "shares": {
          "D": 0.0382,
          "F": 0.2443,
          "W": 0.0992
        }
      },
      "course": "COM 101",
      "names": {
        "top": [
          "COM-101",
          "FOUNDATIONS OF COMMUNICATION",
          "INTRODUCTION TO PUBLIC SPEAKING"
        ],
        "distinct": 3
      },
      "gateway": {
        "M": 0,
        "E": 0
      }
    },
    {
      "students": 76,
      "num": 49,
      "den": 103,
      "rate": 0.4757,
      "split": {
        "D": 0,
        "F": 29,
        "W": 20,
        "DF": 29,
        "total": 103,
        "shares": {
          "D": 0.0,
          "F": 0.2816,
          "W": 0.1942
        }
      },
      "course": "MA 119",
      "names": {
        "top": [
          "COLLEGE ALGEBRA"
        ],
        "distinct": 1
      },
      "gateway": {
        "M": 0,
        "E": 0
      }
    },
    {
      "students": 94,
      "num": 44,
      "den": 120,
      "rate": 0.3667,
      "split": {
        "D": 0,
        "F": 18,
        "W": 26,
        "DF": 18,
        "total": 120,
        "shares": {
          "D": 0.0,
          "F": 0.15,
          "W": 0.2167
        }
      },
      "course": "ENG 121",
      "names": {
        "top": [
          "ENGLISH COMPOSITION I"
        ],
        "distinct": 1
      },
      "gateway": {
        "M": 0,
        "E": 60
      }
    },
    {
      "students": 218,
      "num": 44,
      "den": 227,
      "rate": 0.1938,
      "split": {
        "D": 4,
        "F": 32,
        "W": 8,
        "DF": 36,
        "total": 227,
        "shares": {
          "D": 0.0176,
          "F": 0.141,
          "W": 0.0352
        }
      },
      "course": "PSY 101",
      "names": {
        "top": [
          "PSY-101",
          "INTRODUCTION TO PSYCHOLOGY",
          "INTRO PSYCHOLOGY"
        ],
        "distinct": 4
      },
      "gateway": {
        "M": 0,
        "E": 0
      }
    },
    {
      "students": 119,
      "num": 43,
      "den": 130,
      "rate": 0.3308,
      "split": {
        "D": 7,
        "F": 25,
        "W": 11,
        "DF": 32,
        "total": 130,
        "shares": {
          "D": 0.0538,
          "F": 0.1923,
          "W": 0.0846
        }
      },
      "course": "PSYC 101",
      "names": {
        "top": [
          "GENERAL PSYCHOLOGY",
          "PSYCHOLOGY"
        ],
        "distinct": 2
      },
      "gateway": {
        "M": 0,
        "E": 0
      }
    },
    {
      "students": 106,
      "num": 34,
      "den": 118,
      "rate": 0.2881,
      "split": {
        "D": 0,
        "F": 23,
        "W": 11,
        "DF": 23,
        "total": 118,
        "shares": {
          "D": 0.0,
          "F": 0.1949,
          "W": 0.0932
        }
      },
      "course": "PSY 121",
      "names": {
        "top": [
          "INTRODUCTION TO PSYCHOLOGY",
          "GENERAL PSYCHOLOGY"
        ],
        "distinct": 2
      },
      "gateway": {
        "M": 0,
        "E": 0
      }
    },
    {
      "students": 66,
      "num": 33,
      "den": 75,
      "rate": 0.44,
      "split": {
        "D": 7,
        "F": 18,
        "W": 8,
        "DF": 25,
        "total": 75,
        "shares": {
          "D": 0.0933,
          "F": 0.24,
          "W": 0.1067
        }
      },
      "course": "ENG 100",
      "names": {
        "top": [
          "ENG-100",
          "ENGLISH COMPOSITION SUPPORT",
          "COMPOSITION SKILLS"
        ],
        "distinct": 3
      },
      "gateway": {
        "M": 0,
        "E": 0
      }
    },
    {
      "students": 44,
      "num": 32,
      "den": 64,
      "rate": 0.5,
      "split": {
        "D": 2,
        "F": 20,
        "W": 10,
        "DF": 22,
        "total": 64,
        "shares": {
          "D": 0.0312,
          "F": 0.3125,
          "W": 0.1562
        }
      },
      "course": "ENGL 121",
      "names": {
        "top": [
          "COLLEGE COMPOSITION"
        ],
        "distinct": 1
      },
      "gateway": {
        "M": 0,
        "E": 28
      }
    },
    {
      "students": 102,
      "num": 32,
      "den": 120,
      "rate": 0.2667,
      "split": {
        "D": 0,
        "F": 32,
        "W": 0,
        "DF": 32,
        "total": 120,
        "shares": {
          "D": 0.0,
          "F": 0.2667,
          "W": 0.0
        }
      },
      "course": "SSC 100",
      "names": {
        "top": [
          "FIRST YEAR SEMINAR",
          "FIRST YEAR SEMINAR - ITN"
        ],
        "distinct": 2
      },
      "gateway": {
        "M": 0,
        "E": 0
      }
    },
    {
      "students": 116,
      "num": 28,
      "den": 122,
      "rate": 0.2295,
      "split": {
        "D": 3,
        "F": 20,
        "W": 5,
        "DF": 23,
        "total": 122,
        "shares": {
          "D": 0.0246,
          "F": 0.1639,
          "W": 0.041
        }
      },
      "course": "SOC 101",
      "names": {
        "top": [
          "SOC-101",
          "INTRODUCTION TO SOCIOLOGY",
          "INTRO SOCIOLOGY"
        ],
        "distinct": 6
      },
      "gateway": {
        "M": 0,
        "E": 0
      }
    },
    {
      "students": 89,
      "num": 26,
      "den": 97,
      "rate": 0.268,
      "split": {
        "D": 0,
        "F": 14,
        "W": 12,
        "DF": 14,
        "total": 97,
        "shares": {
          "D": 0.0,
          "F": 0.1443,
          "W": 0.1237
        }
      },
      "course": "ENGL 102",
      "names": {
        "top": [
          "ENGLISH COMPOSITION II"
        ],
        "distinct": 1
      },
      "gateway": {
        "M": 0,
        "E": 0
      }
    },
    {
      "students": 75,
      "num": 25,
      "den": 80,
      "rate": 0.3125,
      "split": {
        "D": 2,
        "F": 18,
        "W": 5,
        "DF": 20,
        "total": 80,
        "shares": {
          "D": 0.025,
          "F": 0.225,
          "W": 0.0625
        }
      },
      "course": "BUS 101",
      "names": {
        "top": [
          "BUS-101",
          "INTRODUCTION TO BUSINESS",
          "INTRO TO BUSINESS"
        ],
        "distinct": 5
      },
      "gateway": {
        "M": 0,
        "E": 0
      }
    },
    {
      "students": 99,
      "num": 25,
      "den": 116,
      "rate": 0.2155,
      "split": {
        "D": 0,
        "F": 8,
        "W": 17,
        "DF": 8,
        "total": 116,
        "shares": {
          "D": 0.0,
          "F": 0.069,
          "W": 0.1466
        }
      },
      "course": "CLC 120",
      "names": {
        "top": [
          "COLLEGE SUCCESS SEMINAR"
        ],
        "distinct": 1
      },
      "gateway": {
        "M": 0,
        "E": 0
      }
    },
    {
      "students": 72,
      "num": 24,
      "den": 75,
      "rate": 0.32,
      "split": {
        "D": 3,
        "F": 14,
        "W": 7,
        "DF": 17,
        "total": 75,
        "shares": {
          "D": 0.04,
          "F": 0.1867,
          "W": 0.0933
        }
      },
      "course": "PSC 101",
      "names": {
        "top": [
          "PSC-101",
          "AMERICAN POLITICS/GOVERNMENT"
        ],
        "distinct": 2
      },
      "gateway": {
        "M": 0,
        "E": 0
      }
    },
    {
      "students": 77,
      "num": 23,
      "den": 88,
      "rate": 0.2614,
      "split": {
        "D": 3,
        "F": 7,
        "W": 13,
        "DF": 10,
        "total": 88,
        "shares": {
          "D": 0.0341,
          "F": 0.0795,
          "W": 0.1477
        }
      },
      "course": "BIO 110",
      "names": {
        "top": [
          "INTRO BIO SCIENCE",
          "PRINCIPLES OF BIOLOGY",
          "ESSENTLS-ANATOMY & PHYSIOLOGY"
        ],
        "distinct": 7
      },
      "gateway": {
        "M": 0,
        "E": 0
      }
    },
    {
      "students": 106,
      "num": 23,
      "den": 115,
      "rate": 0.2,
      "split": {
        "D": 5,
        "F": 14,
        "W": 4,
        "DF": 19,
        "total": 115,
        "shares": {
          "D": 0.0435,
          "F": 0.1217,
          "W": 0.0348
        }
      },
      "course": "PSY 100",
      "names": {
        "top": [
          "INTRODUCTION TO PSYCHOLOGY",
          "INTRO TO PSYCHOLOGY",
          "HUMAN RELATIONS"
        ],
        "distinct": 5
      },
      "gateway": {
        "M": 0,
        "E": 0
      }
    },
    {
      "students": 65,
      "num": 22,
      "den": 75,
      "rate": 0.2933,
      "split": {
        "D": 0,
        "F": 15,
        "W": 7,
        "DF": 15,
        "total": 75,
        "shares": {
          "D": 0.0,
          "F": 0.2,
          "W": 0.0933
        }
      },
      "course": "MAT 152",
      "names": {
        "top": [
          "QUANTITATIVE REASONING",
          "STATISTICAL METHODS I"
        ],
        "distinct": 2
      },
      "gateway": {
        "M": 75,
        "E": 0
      }
    },
    {
      "students": 36,
      "num": 19,
      "den": 39,
      "rate": 0.4872,
      "split": {
        "D": 3,
        "F": 15,
        "W": 1,
        "DF": 18,
        "total": 39,
        "shares": {
          "D": 0.0769,
          "F": 0.3846,
          "W": 0.0256
        }
      },
      "course": "ACC 201",
      "names": {
        "top": [
          "ACC-201",
          "INTER ACCOUNT 1"
        ],
        "distinct": 2
      },
      "gateway": {
        "M": 0,
        "E": 0
      }
    },
    {
      "students": 60,
      "num": 19,
      "den": 69,
      "rate": 0.2754,
      "split": {
        "D": 1,
        "F": 7,
        "W": 11,
        "DF": 8,
        "total": 69,
        "shares": {
          "D": 0.0145,
          "F": 0.1014,
          "W": 0.1594
        }
      },
      "course": "BIO 120",
      "names": {
        "top": [
          "ANATOMY AND PHYSIOLOGY I",
          "ENVIRONMENTAL BIOLOGY",
          "PRINCIPLES OF BIOLOGY I"
        ],
        "distinct": 4
      },
      "gateway": {
        "M": 0,
        "E": 0
      }
    },
    {
      "students": 27,
      "num": 18,
      "den": 35,
      "rate": 0.5143,
      "split": {
        "D": 1,
        "F": 10,
        "W": 7,
        "DF": 11,
        "total": 35,
        "shares": {
          "D": 0.0286,
          "F": 0.2857,
          "W": 0.2
        }
      },
      "course": "MATH 103",
      "names": {
        "top": [
          "COLLEGE ALGEBRA",
          "CONTEMPORARY MATH"
        ],
        "distinct": 2
      },
      "gateway": {
        "M": 35,
        "E": 0
      }
    },
    {
      "students": 35,
      "num": 18,
      "den": 40,
      "rate": 0.45,
      "split": {
        "D": 2,
        "F": 5,
        "W": 11,
        "DF": 7,
        "total": 40,
        "shares": {
          "D": 0.05,
          "F": 0.125,
          "W": 0.275
        }
      },
      "course": "CHM 121",
      "names": {
        "top": [
          "GENERAL CHEMISTRY I",
          "GENERAL CHEMISTRY",
          "GENERAL CHEMISTRY I/HONORS"
        ],
        "distinct": 3
      },
      "gateway": {
        "M": 0,
        "E": 0
      }
    },
    {
      "students": 51,
      "num": 18,
      "den": 56,
      "rate": 0.3214,
      "split": {
        "D": 8,
        "F": 4,
        "W": 6,
        "DF": 12,
        "total": 56,
        "shares": {
          "D": 0.1429,
          "F": 0.0714,
          "W": 0.1071
        }
      },
      "course": "BIO 101",
      "names": {
        "top": [
          "BIOLOGY SURVEY",
          "INTRO TO BIOLOGY LABORATORY",
          "GENERAL BIOLOGY I"
        ],
        "distinct": 6
      },
      "gateway": {
        "M": 0,
        "E": 0
      }
    },
    {
      "students": 29,
      "num": 17,
      "den": 33,
      "rate": 0.5152,
      "split": {
        "D": 0,
        "F": 7,
        "W": 10,
        "DF": 7,
        "total": 33,
        "shares": {
          "D": 0.0,
          "F": 0.2121,
          "W": 0.303
        }
      },
      "course": "BI 301",
      "names": {
        "top": [
          "ANATOMY AND PHYSIOLOGY I"
        ],
        "distinct": 1
      },
      "gateway": {
        "M": 0,
        "E": 0
      }
    },
    {
      "students": 22,
      "num": 17,
      "den": 35,
      "rate": 0.4857,
      "split": {
        "D": 5,
        "F": 3,
        "W": 9,
        "DF": 8,
        "total": 35,
        "shares": {
          "D": 0.1429,
          "F": 0.0857,
          "W": 0.2571
        }
      },
      "course": "MTH 103",
      "names": {
        "top": [
          "COLLEGE ALGEBRA",
          "TECHNICAL MATHEMATICS"
        ],
        "distinct": 2
      },
      "gateway": {
        "M": 35,
        "E": 0
      }
    },
    {
      "students": 37,
      "num": 17,
      "den": 40,
      "rate": 0.425,
      "split": {
        "D": 0,
        "F": 13,
        "W": 4,
        "DF": 13,
        "total": 40,
        "shares": {
          "D": 0.0,
          "F": 0.325,
          "W": 0.1
        }
      },
      "course": "CIS 107",
      "names": {
        "top": [
          "INTRO TO COMPUTERS/APPLICATION",
          "INFO TECHNOLOGY FUNDAMENTALS"
        ],
        "distinct": 2
      },
      "gateway": {
        "M": 0,
        "E": 0
      }
    },
    {
      "students": 30,
      "num": 15,
      "den": 39,
      "rate": 0.3846,
      "split": {
        "D": 1,
        "F": 11,
        "W": 3,
        "DF": 12,
        "total": 39,
        "shares": {
          "D": 0.0256,
          "F": 0.2821,
          "W": 0.0769
        }
      },
      "course": "MATH 138",
      "names": {
        "top": [
          "STATISTICS"
        ],
        "distinct": 1
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
  "students": 439,
  "num": 135,
  "den": 492,
  "rate": 0.2744,
  "split": {
    "D": 19,
    "F": 69,
    "W": 47,
    "DF": 88,
    "total": 492,
    "shares": {
      "D": 0.0386,
      "F": 0.1402,
      "W": 0.0955
    }
  },
  "meta": {
    "cohort": "2023-24",
    "filters": {},
    "retention_type": "school",
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
  "terms": [
    {
      "value": "Fall",
      "students": 286,
      "num": 92,
      "den": 295,
      "rate": 0.3119,
      "split": {
        "D": 12,
        "F": 53,
        "W": 27,
        "DF": 65,
        "total": 295,
        "shares": {
          "D": 0.0407,
          "F": 0.1797,
          "W": 0.0915
        }
      },
      "rest_rate": 0.2183,
      "gap": 9.4
    },
    {
      "value": "Spring",
      "students": 146,
      "num": 34,
      "den": 149,
      "rate": 0.2282,
      "split": {
        "D": 5,
        "F": 12,
        "W": 17,
        "DF": 17,
        "total": 149,
        "shares": {
          "D": 0.0336,
          "F": 0.0805,
          "W": 0.1141
        }
      },
      "rest_rate": 0.2945,
      "gap": -6.6
    },
    {
      "value": "Summer",
      "students": 46,
      "num": 9,
      "den": 48,
      "rate": 0.1875,
      "split": {
        "D": 2,
        "F": 4,
        "W": 3,
        "DF": 6,
        "total": 48,
        "shares": {
          "D": 0.0417,
          "F": 0.0833,
          "W": 0.0625
        }
      },
      "rest_rate": 0.2838,
      "gap": -9.6
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
        "D": 6,
        "F": 25,
        "W": 19,
        "DF": 31,
        "total": 185,
        "shares": {
          "D": 0.0324,
          "F": 0.1351,
          "W": 0.1027
        }
      },
      "rest_rate": 0.2769,
      "gap": -0.7
    },
    {
      "value": "Hybrid",
      "students": 60,
      "num": 11,
      "den": 61,
      "rate": 0.1803,
      "split": {
        "D": 1,
        "F": 6,
        "W": 4,
        "DF": 7,
        "total": 61,
        "shares": {
          "D": 0.0164,
          "F": 0.0984,
          "W": 0.0656
        }
      },
      "rest_rate": 0.2877,
      "gap": -10.7
    },
    {
      "value": "Online",
      "students": 126,
      "num": 49,
      "den": 137,
      "rate": 0.3577,
      "split": {
        "D": 9,
        "F": 25,
        "W": 15,
        "DF": 34,
        "total": 137,
        "shares": {
          "D": 0.0657,
          "F": 0.1825,
          "W": 0.1095
        }
      },
      "rest_rate": 0.2423,
      "gap": 11.5
    },
    {
      "value": "Blank",
      "students": 100,
      "num": 25,
      "den": 109,
      "rate": 0.2294,
      "split": {
        "D": 3,
        "F": 13,
        "W": 9,
        "DF": 16,
        "total": 109,
        "shares": {
          "D": 0.0275,
          "F": 0.1193,
          "W": 0.0826
        }
      },
      "rest_rate": 0.2872,
      "gap": -5.8
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
          "D": 8,
          "F": 26,
          "W": 20,
          "DF": 34,
          "total": 217,
          "shares": {
            "D": 0.0369,
            "F": 0.1198,
            "W": 0.0922
          }
        },
        "rest_rate": 0.2945,
        "gap": -4.6
      },
      {
        "value": "UNKNOWN",
        "students": 16,
        "num": 5,
        "den": 17,
        "rate": 0.2941,
        "split": {
          "D": 2,
          "F": 2,
          "W": 1,
          "DF": 4,
          "total": 17,
          "shares": {
            "D": 0.1176,
            "F": 0.1176,
            "W": 0.0588
          }
        },
        "rest_rate": 0.2737,
        "gap": 2.0
      },
      {
        "value": "Y",
        "students": 227,
        "num": 76,
        "den": 258,
        "rate": 0.2946,
        "split": {
          "D": 9,
          "F": 41,
          "W": 26,
          "DF": 50,
          "total": 258,
          "shares": {
            "D": 0.0349,
            "F": 0.1589,
            "W": 0.1008
          }
        },
        "rest_rate": 0.2521,
        "gap": 4.2
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
          "D": 6,
          "F": 44,
          "W": 25,
          "DF": 50,
          "total": 278,
          "shares": {
            "D": 0.0216,
            "F": 0.1583,
            "W": 0.0899
          }
        },
        "rest_rate": 0.2804,
        "gap": -1.1
      },
      {
        "value": "M",
        "students": 175,
        "num": 52,
        "den": 193,
        "rate": 0.2694,
        "split": {
          "D": 13,
          "F": 17,
          "W": 22,
          "DF": 30,
          "total": 193,
          "shares": {
            "D": 0.0674,
            "F": 0.0881,
            "W": 0.114
          }
        },
        "rest_rate": 0.2776,
        "gap": -0.8
      },
      {
        "value": "UNKNOWN",
        "students": 18,
        "num": 8,
        "den": 21,
        "rate": 0.381,
        "split": {
          "D": 0,
          "F": 8,
          "W": 0,
          "DF": 8,
          "total": 21,
          "shares": {
            "D": 0.0,
            "F": 0.381,
            "W": 0.0
          }
        },
        "rest_rate": 0.2696,
        "gap": 11.1
      }
    ],
    "race": [
      {
        "value": "American Indian or Alaska Native",
        "students": null,
        "num": null,
        "den": null,
        "rate": null,
        "split": null,
        "rest_rate": null,
        "gap": null
      },
      {
        "value": "Asian",
        "students": 34,
        "num": 6,
        "den": 38,
        "rate": 0.1579,
        "split": {
          "D": 1,
          "F": 3,
          "W": 2,
          "DF": 4,
          "total": 38,
          "shares": {
            "D": 0.0263,
            "F": 0.0789,
            "W": 0.0526
          }
        },
        "rest_rate": 0.2841,
        "gap": -12.6
      },
      {
        "value": "Black or African American",
        "students": 73,
        "num": 33,
        "den": 87,
        "rate": 0.3793,
        "split": {
          "D": 2,
          "F": 21,
          "W": 10,
          "DF": 23,
          "total": 87,
          "shares": {
            "D": 0.023,
            "F": 0.2414,
            "W": 0.1149
          }
        },
        "rest_rate": 0.2519,
        "gap": 12.7
      },
      {
        "value": "Hispanic",
        "students": 130,
        "num": 40,
        "den": 141,
        "rate": 0.2837,
        "split": {
          "D": 8,
          "F": 19,
          "W": 13,
          "DF": 27,
          "total": 141,
          "shares": {
            "D": 0.0567,
            "F": 0.1348,
            "W": 0.0922
          }
        },
        "rest_rate": 0.2707,
        "gap": 1.3
      },
      {
        "value": "Native Hawaiian or Other Pacific Islander",
        "students": null,
        "num": null,
        "den": null,
        "rate": null,
        "split": null,
        "rest_rate": null,
        "gap": null
      },
      {
        "value": "Nonresident alien",
        "students": 11,
        "num": 5,
        "den": 13,
        "rate": 0.3846,
        "split": {
          "D": 1,
          "F": 1,
          "W": 3,
          "DF": 2,
          "total": 13,
          "shares": {
            "D": 0.0769,
            "F": 0.0769,
            "W": 0.2308
          }
        },
        "rest_rate": 0.2714,
        "gap": 11.3
      },
      {
        "value": "Two or More Races",
        "students": 13,
        "num": 4,
        "den": 13,
        "rate": 0.3077,
        "split": {
          "D": 0,
          "F": 2,
          "W": 2,
          "DF": 2,
          "total": 13,
          "shares": {
            "D": 0.0,
            "F": 0.1538,
            "W": 0.1538
          }
        },
        "rest_rate": 0.2735,
        "gap": 3.4
      },
      {
        "value": "UNKNOWN",
        "students": 16,
        "num": 5,
        "den": 19,
        "rate": 0.2632,
        "split": {
          "D": 2,
          "F": 2,
          "W": 1,
          "DF": 4,
          "total": 19,
          "shares": {
            "D": 0.1053,
            "F": 0.1053,
            "W": 0.0526
          }
        },
        "rest_rate": 0.2748,
        "gap": -1.2
      },
      {
        "value": "White",
        "students": 156,
        "num": 39,
        "den": 175,
        "rate": 0.2229,
        "split": {
          "D": 5,
          "F": 18,
          "W": 16,
          "DF": 23,
          "total": 175,
          "shares": {
            "D": 0.0286,
            "F": 0.1029,
            "W": 0.0914
          }
        },
        "rest_rate": 0.3028,
        "gap": -8.0
      }
    ],
    "ethnicity": [
      {
        "value": "H",
        "students": 140,
        "num": 44,
        "den": 152,
        "rate": 0.2895,
        "split": {
          "D": 9,
          "F": 19,
          "W": 16,
          "DF": 28,
          "total": 152,
          "shares": {
            "D": 0.0592,
            "F": 0.125,
            "W": 0.1053
          }
        },
        "rest_rate": 0.2676,
        "gap": 2.2
      },
      {
        "value": "N",
        "students": 62,
        "num": 32,
        "den": 72,
        "rate": 0.4444,
        "split": {
          "D": 1,
          "F": 21,
          "W": 10,
          "DF": 22,
          "total": 72,
          "shares": {
            "D": 0.0139,
            "F": 0.2917,
            "W": 0.1389
          }
        },
        "rest_rate": 0.2452,
        "gap": 19.9
      },
      {
        "value": "UNKNOWN",
        "students": 237,
        "num": 59,
        "den": 268,
        "rate": 0.2201,
        "split": {
          "D": 9,
          "F": 29,
          "W": 21,
          "DF": 38,
          "total": 268,
          "shares": {
            "D": 0.0336,
            "F": 0.1082,
            "W": 0.0784
          }
        },
        "rest_rate": 0.3393,
        "gap": -11.9
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
          "D": 14,
          "F": 53,
          "W": 36,
          "DF": 67,
          "total": 338,
          "shares": {
            "D": 0.0414,
            "F": 0.1568,
            "W": 0.1065
          }
        },
        "rest_rate": 0.2078,
        "gap": 9.7
      },
      {
        "value": "> 20-24",
        "students": 69,
        "num": 20,
        "den": 74,
        "rate": 0.2703,
        "split": {
          "D": 2,
          "F": 12,
          "W": 6,
          "DF": 14,
          "total": 74,
          "shares": {
            "D": 0.027,
            "F": 0.1622,
            "W": 0.0811
          }
        },
        "rest_rate": 0.2751,
        "gap": -0.5
      },
      {
        "value": "Older than 24",
        "students": 77,
        "num": 12,
        "den": 80,
        "rate": 0.15,
        "split": {
          "D": 3,
          "F": 4,
          "W": 5,
          "DF": 7,
          "total": 80,
          "shares": {
            "D": 0.0375,
            "F": 0.05,
            "W": 0.0625
          }
        },
        "rest_rate": 0.2985,
        "gap": -14.9
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
          "D": 13,
          "F": 35,
          "W": 29,
          "DF": 48,
          "total": 305,
          "shares": {
            "D": 0.0426,
            "F": 0.1148,
            "W": 0.0951
          }
        },
        "rest_rate": 0.3102,
        "gap": -5.8
      },
      {
        "value": "Part-time",
        "students": 167,
        "num": 58,
        "den": 187,
        "rate": 0.3102,
        "split": {
          "D": 6,
          "F": 34,
          "W": 18,
          "DF": 40,
          "total": 187,
          "shares": {
            "D": 0.0321,
            "F": 0.1818,
            "W": 0.0963
          }
        },
        "rest_rate": 0.2525,
        "gap": 5.8
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
          "D": 16,
          "F": 54,
          "W": 36,
          "DF": 70,
          "total": 397,
          "shares": {
            "D": 0.0403,
            "F": 0.136,
            "W": 0.0907
          }
        },
        "rest_rate": 0.3053,
        "gap": -3.8
      },
      {
        "value": "Transfer-in",
        "students": 88,
        "num": 29,
        "den": 95,
        "rate": 0.3053,
        "split": {
          "D": 3,
          "F": 15,
          "W": 11,
          "DF": 18,
          "total": 95,
          "shares": {
            "D": 0.0316,
            "F": 0.1579,
            "W": 0.1158
          }
        },
        "rest_rate": 0.267,
        "gap": 3.8
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
          "D": 17,
          "F": 65,
          "W": 39,
          "DF": 82,
          "total": 397,
          "shares": {
            "D": 0.0428,
            "F": 0.1637,
            "W": 0.0982
          }
        },
        "rest_rate": 0.1474,
        "gap": 15.7
      },
      {
        "value": "Spring",
        "students": 77,
        "num": 13,
        "den": 81,
        "rate": 0.1605,
        "split": {
          "D": 1,
          "F": 4,
          "W": 8,
          "DF": 5,
          "total": 81,
          "shares": {
            "D": 0.0123,
            "F": 0.0494,
            "W": 0.0988
          }
        },
        "rest_rate": 0.2968,
        "gap": -13.6
      },
      {
        "value": "Summer",
        "students": 13,
        "num": 1,
        "den": 14,
        "rate": 0.0714,
        "split": {
          "D": 1,
          "F": 0,
          "W": 0,
          "DF": 1,
          "total": 14,
          "shares": {
            "D": 0.0714,
            "F": 0.0,
            "W": 0.0
          }
        },
        "rest_rate": 0.2803,
        "gap": -20.9
      }
    ]
  }
};
