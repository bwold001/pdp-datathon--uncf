// Real answers from GET /uncf/gateway on the synthetic sample data (pdp.sqlite), with the default (school)
// retention type. Regenerate them from the running API (measures/breakdowns/gateway_courses.py); don't edit the
// numbers by hand.
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
    "loaded_at": "2026-11-07T17:01:14",
    "flagged": true,
    "year_one": "2023-24",
    "retention_term": "next academic year",
    "retention_observed": true,
    "first_term": null,
    "compared": false,
    "min_pair_students": 10,
    "grade_scale": {
      "grades": [
        {
          "grade": "A",
          "points": "4.0",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "A-",
          "points": "3.7 to under 4.0",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "B+",
          "points": "3.3 to under 3.7",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "B",
          "points": "3.0 to under 3.3",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "B-",
          "points": "2.7 to under 3.0",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "C+",
          "points": "2.3 to under 2.7",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "C",
          "points": "2.0 to under 2.3",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "C-",
          "points": "1.7 to under 2.0",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "D+",
          "points": "1.3 to under 1.7",
          "dfw": true,
          "gateway_pass": true
        },
        {
          "grade": "D",
          "points": "1.0 to under 1.3",
          "dfw": true,
          "gateway_pass": true
        },
        {
          "grade": "D-",
          "points": "0.7 to under 1.0",
          "dfw": true,
          "gateway_pass": false
        },
        {
          "grade": "F",
          "points": "under 0.7, or the code F",
          "dfw": true,
          "gateway_pass": false
        },
        {
          "grade": "P",
          "points": "the code P (pass)",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "W",
          "points": "the code W (withdrew)",
          "dfw": true,
          "gateway_pass": false
        }
      ],
      "left_out": "I (incomplete), A (audit), M or MIS (missing), O or OTH (other), and any code the PDP dictionary doesn't list, such as UW, aren't final grades, so neither page counts them."
    }
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
      "students": 384,
      "first_pass": 297,
      "passed": 313,
      "path": {
        "first": 297,
        "retook_passed": 16,
        "retook_not": null,
        "no_retake": 64
      },
      "grades": {
        "A": 120,
        "A-": 13,
        "B+": 10,
        "B": 53,
        "B-": 6,
        "C+": 7,
        "C": 40,
        "C-": 2,
        "D+": 2,
        "D": 13,
        "D-": 1,
        "F": 64,
        "P": 50,
        "W": 31
      },
      "retained_if_passed": {
        "students": 313,
        "retained": 244,
        "rate": 0.7796
      },
      "retained_if_not_passed": {
        "students": 71,
        "retained": 16,
        "rate": 0.2254
      },
      "group": null
    },
    {
      "course": "ENGL 101",
      "name": "ENGLISH COMPOSITION I",
      "subject": "E",
      "students": 63,
      "first_pass": 50,
      "passed": 52,
      "path": {
        "first": 50,
        "retook_passed": null,
        "retook_not": null,
        "no_retake": 10
      },
      "grades": {
        "A": 21,
        "A-": 0,
        "B+": 0,
        "B": 15,
        "B-": 0,
        "C+": 0,
        "C": 12,
        "C-": 0,
        "D+": 0,
        "D": 6,
        "D-": 0,
        "F": 6,
        "P": 0,
        "W": 8
      },
      "retained_if_passed": {
        "students": 52,
        "retained": 39,
        "rate": 0.75
      },
      "retained_if_not_passed": {
        "students": 11,
        "retained": 4,
        "rate": 0.3636
      },
      "group": null
    },
    {
      "course": "MAT 152",
      "name": "QUANTITATIVE REASONING",
      "subject": "M",
      "students": 56,
      "first_pass": 39,
      "passed": 41,
      "path": {
        "first": 39,
        "retook_passed": null,
        "retook_not": null,
        "no_retake": 14
      },
      "grades": {
        "A": 14,
        "A-": 0,
        "B+": 0,
        "B": 15,
        "B-": 0,
        "C+": 0,
        "C": 13,
        "C-": 0,
        "D+": 0,
        "D": 0,
        "D-": 0,
        "F": 14,
        "P": 0,
        "W": 4
      },
      "retained_if_passed": {
        "students": 41,
        "retained": 30,
        "rate": 0.7317
      },
      "retained_if_not_passed": {
        "students": 15,
        "retained": 3,
        "rate": 0.2
      },
      "group": null
    },
    {
      "course": "ENG 121",
      "name": "ENGLISH COMPOSITION I",
      "subject": "E",
      "students": 51,
      "first_pass": 36,
      "passed": 36,
      "path": {
        "first": 36,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 15
      },
      "grades": {
        "A": 0,
        "A-": 0,
        "B+": 0,
        "B": 0,
        "B-": 0,
        "C+": 0,
        "C": 0,
        "C-": 0,
        "D+": 0,
        "D": 0,
        "D-": 0,
        "F": 8,
        "P": 36,
        "W": 7
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
      },
      "group": null
    },
    {
      "course": "ENG 111",
      "name": "COLLEGE COMPOSITION I",
      "subject": "E",
      "students": 36,
      "first_pass": 28,
      "passed": 30,
      "path": {
        "first": 28,
        "retook_passed": null,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 18,
        "A-": 0,
        "B+": 0,
        "B": 7,
        "B-": 0,
        "C+": 0,
        "C": 4,
        "C-": 0,
        "D+": 0,
        "D": 1,
        "D-": 0,
        "F": 3,
        "P": 0,
        "W": 5
      },
      "retained_if_passed": {
        "students": 30,
        "retained": 22,
        "rate": 0.7333
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTH 165",
      "name": "ELEMENTARY STATISTICS",
      "subject": "M",
      "students": 23,
      "first_pass": 16,
      "passed": 17,
      "path": {
        "first": 16,
        "retook_passed": null,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 7,
        "A-": 0,
        "B+": 0,
        "B": 3,
        "B-": 0,
        "C+": 0,
        "C": 5,
        "C-": 0,
        "D+": 0,
        "D": 2,
        "D-": 0,
        "F": 2,
        "P": 0,
        "W": 5
      },
      "retained_if_passed": {
        "students": 17,
        "retained": 16,
        "rate": 0.9412
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "ENGL 112",
      "name": "COMPOSITION I",
      "subject": "E",
      "students": 22,
      "first_pass": 22,
      "passed": 22,
      "path": {
        "first": 22,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "A": 5,
        "A-": 2,
        "B+": 1,
        "B": 9,
        "B-": 2,
        "C+": 0,
        "C": 3,
        "C-": 0,
        "D+": 0,
        "D": 0,
        "D-": 0,
        "F": 0,
        "P": 0,
        "W": 0
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
      },
      "group": null
    },
    {
      "course": "ENGL 1110",
      "name": "COMPOSITION I",
      "subject": "E",
      "students": 21,
      "first_pass": 19,
      "passed": 19,
      "path": {
        "first": 19,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 7,
        "A-": 0,
        "B+": 0,
        "B": 4,
        "B-": 1,
        "C+": 0,
        "C": 5,
        "C-": 2,
        "D+": 0,
        "D": 3,
        "D-": 0,
        "F": 2,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 19,
        "retained": 15,
        "rate": 0.7895
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "ENGL 121",
      "name": "COLLEGE COMPOSITION",
      "subject": "E",
      "students": 21,
      "first_pass": 21,
      "passed": 21,
      "path": {
        "first": 21,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "A": 10,
        "A-": 0,
        "B+": 0,
        "B": 10,
        "B-": 0,
        "C+": 0,
        "C": 1,
        "C-": 0,
        "D+": 0,
        "D": 0,
        "D-": 0,
        "F": 0,
        "P": 0,
        "W": 0
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
      },
      "group": null
    },
    {
      "course": "MATH 103",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 20,
      "first_pass": 11,
      "passed": 11,
      "path": {
        "first": 11,
        "retook_passed": 0,
        "retook_not": null,
        "no_retake": null
      },
      "grades": {
        "A": 1,
        "A-": 0,
        "B+": 0,
        "B": 4,
        "B-": 0,
        "C+": 0,
        "C": 5,
        "C-": 0,
        "D+": 0,
        "D": 1,
        "D-": 0,
        "F": 6,
        "P": 0,
        "W": 4
      },
      "retained_if_passed": {
        "students": 11,
        "retained": 10,
        "rate": 0.9091
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "ENGL 161",
      "name": "COLLEGE COMPOSITION I",
      "subject": "E",
      "students": 18,
      "first_pass": 13,
      "passed": 15,
      "path": {
        "first": 13,
        "retook_passed": null,
        "retook_not": null,
        "no_retake": null
      },
      "grades": {
        "A": 3,
        "A-": 0,
        "B+": 0,
        "B": 7,
        "B-": 0,
        "C+": 0,
        "C": 4,
        "C-": 0,
        "D+": 0,
        "D": 1,
        "D-": 0,
        "F": 4,
        "P": 0,
        "W": 2
      },
      "retained_if_passed": {
        "students": 15,
        "retained": 14,
        "rate": 0.9333
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "ENG 102",
      "name": "FIRST-YEAR COMPOSITION",
      "subject": "E",
      "students": 17,
      "first_pass": 16,
      "passed": 16,
      "path": {
        "first": 16,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 9,
        "A-": 0,
        "B+": 0,
        "B": 5,
        "B-": 0,
        "C+": 0,
        "C": 1,
        "C-": 0,
        "D+": 0,
        "D": 1,
        "D-": 0,
        "F": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 16,
        "retained": 12,
        "rate": 0.75
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTH 103",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 17,
      "first_pass": 11,
      "passed": 12,
      "path": {
        "first": 11,
        "retook_passed": null,
        "retook_not": null,
        "no_retake": null
      },
      "grades": {
        "A": 2,
        "A-": 0,
        "B+": 0,
        "B": 5,
        "B-": 0,
        "C+": 0,
        "C": 2,
        "C-": 0,
        "D+": 0,
        "D": 3,
        "D-": 0,
        "F": 2,
        "P": 0,
        "W": 6
      },
      "retained_if_passed": {
        "students": 12,
        "retained": 9,
        "rate": 0.75
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MAT 162",
      "name": "STATISTICAL REASONING",
      "subject": "M",
      "students": 14,
      "first_pass": 7,
      "passed": 7,
      "path": {
        "first": null,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 3,
        "A-": 0,
        "B+": 0,
        "B": 2,
        "B-": 0,
        "C+": 0,
        "C": 2,
        "C-": 0,
        "D+": 0,
        "D": 0,
        "D-": 0,
        "F": 5,
        "P": 0,
        "W": 2
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
      },
      "group": null
    },
    {
      "course": "MATH 120",
      "name": "MATH-120",
      "subject": "M",
      "students": 14,
      "first_pass": 12,
      "passed": 12,
      "path": {
        "first": 12,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 6,
        "A-": 1,
        "B+": 1,
        "B": 0,
        "B-": 0,
        "C+": 0,
        "C": 2,
        "C-": 0,
        "D+": 0,
        "D": 3,
        "D-": 0,
        "F": 2,
        "P": 0,
        "W": 0
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
      },
      "group": null
    },
    {
      "course": "MTH 101",
      "name": "QUANTITATIVE LITERACY",
      "subject": "M",
      "students": 14,
      "first_pass": 12,
      "passed": 12,
      "path": {
        "first": 12,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 2,
        "A-": 0,
        "B+": 0,
        "B": 4,
        "B-": 0,
        "C+": 0,
        "C": 5,
        "C-": 0,
        "D+": 0,
        "D": 1,
        "D-": 0,
        "F": 2,
        "P": 0,
        "W": 0
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
      },
      "group": null
    },
    {
      "course": "MATH 202",
      "name": "INTRODUCTION TO STATISTICS",
      "subject": "M",
      "students": 13,
      "first_pass": 8,
      "passed": 8,
      "path": {
        "first": null,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 2,
        "A-": 0,
        "B+": 0,
        "B": 0,
        "B-": 0,
        "C+": 0,
        "C": 4,
        "C-": 0,
        "D+": 0,
        "D": 2,
        "D-": 0,
        "F": 2,
        "P": 0,
        "W": 3
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
      },
      "group": null
    },
    {
      "course": "MTH 107",
      "name": "BASIC STATISTICS",
      "subject": "M",
      "students": 13,
      "first_pass": 11,
      "passed": 11,
      "path": {
        "first": 11,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 6,
        "A-": 0,
        "B+": 0,
        "B": 2,
        "B-": 0,
        "C+": 0,
        "C": 1,
        "C-": 0,
        "D+": 0,
        "D": 2,
        "D-": 0,
        "F": 2,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 11,
        "retained": 9,
        "rate": 0.8182
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTH 152",
      "name": "STATISTICS (MA)",
      "subject": "M",
      "students": 13,
      "first_pass": 9,
      "passed": 9,
      "path": {
        "first": null,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 0,
        "A-": 0,
        "B+": 0,
        "B": 0,
        "B-": 0,
        "C+": 0,
        "C": 0,
        "C-": 0,
        "D+": 0,
        "D": 0,
        "D-": 0,
        "F": 3,
        "P": 9,
        "W": 1
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
      },
      "group": null
    },
    {
      "course": "MTH 140",
      "name": "PRECALCULUS",
      "subject": "M",
      "students": 12,
      "first_pass": 9,
      "passed": 10,
      "path": {
        "first": null,
        "retook_passed": null,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 0,
        "A-": 0,
        "B+": 0,
        "B": 5,
        "B-": 0,
        "C+": 0,
        "C": 3,
        "C-": 0,
        "D+": 0,
        "D": 1,
        "D-": 0,
        "F": 1,
        "P": 2,
        "W": 2
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
      },
      "group": null
    },
    {
      "course": "MTH 161",
      "name": "PRECALCULUS I",
      "subject": "M",
      "students": 12,
      "first_pass": 8,
      "passed": 9,
      "path": {
        "first": null,
        "retook_passed": null,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 2,
        "A-": 0,
        "B+": 0,
        "B": 4,
        "B-": 0,
        "C+": 0,
        "C": 2,
        "C-": 0,
        "D+": 0,
        "D": 1,
        "D-": 0,
        "F": 0,
        "P": 0,
        "W": 4
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
      },
      "group": null
    },
    {
      "course": "INRW 385",
      "name": "INTEGRATED READING AND WRITING",
      "subject": "E",
      "students": 11,
      "first_pass": 9,
      "passed": 9,
      "path": {
        "first": null,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 4,
        "A-": 0,
        "B+": 0,
        "B": 3,
        "B-": 0,
        "C+": 0,
        "C": 2,
        "C-": 0,
        "D+": 0,
        "D": 0,
        "D-": 0,
        "F": 3,
        "P": 0,
        "W": 0
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
      },
      "group": null
    },
    {
      "course": "MATH 116",
      "name": "MATH-116",
      "subject": "M",
      "students": 11,
      "first_pass": 8,
      "passed": 8,
      "path": {
        "first": null,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 3,
        "A-": 0,
        "B+": 1,
        "B": 0,
        "B-": 0,
        "C+": 0,
        "C": 0,
        "C-": 0,
        "D+": 1,
        "D": 3,
        "D-": 0,
        "F": 3,
        "P": 0,
        "W": 0
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
      },
      "group": null
    },
    {
      "course": "MATH 130",
      "name": "INTRODUCTION TO STATISTICS",
      "subject": "M",
      "students": 11,
      "first_pass": 8,
      "passed": 9,
      "path": {
        "first": null,
        "retook_passed": null,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 0,
        "A-": 3,
        "B+": 1,
        "B": 3,
        "B-": 0,
        "C+": 0,
        "C": 1,
        "C-": 0,
        "D+": 1,
        "D": 2,
        "D-": 0,
        "F": 1,
        "P": 0,
        "W": 2
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
      },
      "group": null
    },
    {
      "course": "MAT 151",
      "name": "COLLEGE ALGEBRA/FUNCTIONS",
      "subject": "M",
      "students": 10,
      "first_pass": 10,
      "passed": 10,
      "path": {
        "first": 10,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "A": 3,
        "A-": 0,
        "B+": 0,
        "B": 2,
        "B-": 0,
        "C+": 0,
        "C": 5,
        "C-": 0,
        "D+": 0,
        "D": 0,
        "D-": 0,
        "F": 0,
        "P": 0,
        "W": 0
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
      },
      "group": null
    },
    {
      "course": "MATH 104B",
      "name": "MATH-104B",
      "subject": "M",
      "students": 10,
      "first_pass": 7,
      "passed": 7,
      "path": {
        "first": null,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 3,
        "A-": 0,
        "B+": 0,
        "B": 0,
        "B-": 0,
        "C+": 0,
        "C": 2,
        "C-": 0,
        "D+": 0,
        "D": 2,
        "D-": 0,
        "F": 3,
        "P": 0,
        "W": 0
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
      },
      "group": null
    },
    {
      "course": "MTH 129",
      "name": "PRECALCULUS I",
      "subject": "M",
      "students": 10,
      "first_pass": 7,
      "passed": 7,
      "path": {
        "first": null,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 1,
        "A-": 0,
        "B+": 0,
        "B": 3,
        "B-": 0,
        "C+": 0,
        "C": 3,
        "C-": 0,
        "D+": 0,
        "D": 0,
        "D-": 0,
        "F": 3,
        "P": 0,
        "W": 0
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
      },
      "group": null
    }
  ],
  "hidden_courses": 82,
  "left_out": 22,
  "pairs_considered": 35,
  "pairs": [
    {
      "courses": [
        "ENG 111",
        "SDV 101"
      ],
      "students": 13,
      "retained": 6,
      "rate": 0.4615,
      "others_rate": 0.5216,
      "gap": -6.01,
      "affected": -0.8,
      "likely_noise": true
    },
    {
      "courses": [
        "ENG 101",
        "ENG 11"
      ],
      "students": 18,
      "retained": 9,
      "rate": 0.5,
      "others_rate": 0.5215,
      "gap": -2.15,
      "affected": -0.4,
      "likely_noise": true
    },
    {
      "courses": [
        "ENG 101",
        "MATH 120E"
      ],
      "students": 10,
      "retained": 5,
      "rate": 0.5,
      "others_rate": 0.5214,
      "gap": -2.14,
      "affected": -0.2,
      "likely_noise": true
    }
  ]
};

/** 2023-24 with fall to fall retention (Back next fall). */
export const gatewayFederal2023: GatewayResponse = {
  "meta": {
    "cohort": "2023-24",
    "filters": {},
    "retention_type": "federal",
    "provisional": false,
    "min_students": 10,
    "source": "PDP analysis-ready cohort and course files (synthetic sample)",
    "loaded_at": "2026-11-07T17:01:14",
    "flagged": true,
    "year_one": "2023-24",
    "retention_term": "Fall 2024",
    "retention_observed": true,
    "first_term": null,
    "compared": false,
    "min_pair_students": 10,
    "grade_scale": {
      "grades": [
        {
          "grade": "A",
          "points": "4.0",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "A-",
          "points": "3.7 to under 4.0",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "B+",
          "points": "3.3 to under 3.7",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "B",
          "points": "3.0 to under 3.3",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "B-",
          "points": "2.7 to under 3.0",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "C+",
          "points": "2.3 to under 2.7",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "C",
          "points": "2.0 to under 2.3",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "C-",
          "points": "1.7 to under 2.0",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "D+",
          "points": "1.3 to under 1.7",
          "dfw": true,
          "gateway_pass": true
        },
        {
          "grade": "D",
          "points": "1.0 to under 1.3",
          "dfw": true,
          "gateway_pass": true
        },
        {
          "grade": "D-",
          "points": "0.7 to under 1.0",
          "dfw": true,
          "gateway_pass": false
        },
        {
          "grade": "F",
          "points": "under 0.7, or the code F",
          "dfw": true,
          "gateway_pass": false
        },
        {
          "grade": "P",
          "points": "the code P (pass)",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "W",
          "points": "the code W (withdrew)",
          "dfw": true,
          "gateway_pass": false
        }
      ],
      "left_out": "I (incomplete), A (audit), M or MIS (missing), O or OTH (other), and any code the PDP dictionary doesn't list, such as UW, aren't final grades, so neither page counts them."
    }
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
      "students": 384,
      "first_pass": 297,
      "passed": 313,
      "path": {
        "first": 297,
        "retook_passed": 16,
        "retook_not": null,
        "no_retake": 64
      },
      "grades": {
        "A": 120,
        "A-": 13,
        "B+": 10,
        "B": 53,
        "B-": 6,
        "C+": 7,
        "C": 40,
        "C-": 2,
        "D+": 2,
        "D": 13,
        "D-": 1,
        "F": 64,
        "P": 50,
        "W": 31
      },
      "retained_if_passed": {
        "students": 313,
        "retained": 236,
        "rate": 0.754
      },
      "retained_if_not_passed": {
        "students": 71,
        "retained": 14,
        "rate": 0.1972
      },
      "group": null
    },
    {
      "course": "ENGL 101",
      "name": "ENGLISH COMPOSITION I",
      "subject": "E",
      "students": 63,
      "first_pass": 50,
      "passed": 52,
      "path": {
        "first": 50,
        "retook_passed": null,
        "retook_not": null,
        "no_retake": 10
      },
      "grades": {
        "A": 21,
        "A-": 0,
        "B+": 0,
        "B": 15,
        "B-": 0,
        "C+": 0,
        "C": 12,
        "C-": 0,
        "D+": 0,
        "D": 6,
        "D-": 0,
        "F": 6,
        "P": 0,
        "W": 8
      },
      "retained_if_passed": {
        "students": 52,
        "retained": 37,
        "rate": 0.7115
      },
      "retained_if_not_passed": {
        "students": 11,
        "retained": 1,
        "rate": 0.0909
      },
      "group": null
    },
    {
      "course": "MAT 152",
      "name": "QUANTITATIVE REASONING",
      "subject": "M",
      "students": 56,
      "first_pass": 39,
      "passed": 41,
      "path": {
        "first": 39,
        "retook_passed": null,
        "retook_not": null,
        "no_retake": 14
      },
      "grades": {
        "A": 14,
        "A-": 0,
        "B+": 0,
        "B": 15,
        "B-": 0,
        "C+": 0,
        "C": 13,
        "C-": 0,
        "D+": 0,
        "D": 0,
        "D-": 0,
        "F": 14,
        "P": 0,
        "W": 4
      },
      "retained_if_passed": {
        "students": 41,
        "retained": 30,
        "rate": 0.7317
      },
      "retained_if_not_passed": {
        "students": 15,
        "retained": 2,
        "rate": 0.1333
      },
      "group": null
    },
    {
      "course": "ENG 121",
      "name": "ENGLISH COMPOSITION I",
      "subject": "E",
      "students": 51,
      "first_pass": 36,
      "passed": 36,
      "path": {
        "first": 36,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 15
      },
      "grades": {
        "A": 0,
        "A-": 0,
        "B+": 0,
        "B": 0,
        "B-": 0,
        "C+": 0,
        "C": 0,
        "C-": 0,
        "D+": 0,
        "D": 0,
        "D-": 0,
        "F": 8,
        "P": 36,
        "W": 7
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
      },
      "group": null
    },
    {
      "course": "ENG 111",
      "name": "COLLEGE COMPOSITION I",
      "subject": "E",
      "students": 36,
      "first_pass": 28,
      "passed": 30,
      "path": {
        "first": 28,
        "retook_passed": null,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 18,
        "A-": 0,
        "B+": 0,
        "B": 7,
        "B-": 0,
        "C+": 0,
        "C": 4,
        "C-": 0,
        "D+": 0,
        "D": 1,
        "D-": 0,
        "F": 3,
        "P": 0,
        "W": 5
      },
      "retained_if_passed": {
        "students": 30,
        "retained": 4,
        "rate": 0.1333
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTH 165",
      "name": "ELEMENTARY STATISTICS",
      "subject": "M",
      "students": 23,
      "first_pass": 16,
      "passed": 17,
      "path": {
        "first": 16,
        "retook_passed": null,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 7,
        "A-": 0,
        "B+": 0,
        "B": 3,
        "B-": 0,
        "C+": 0,
        "C": 5,
        "C-": 0,
        "D+": 0,
        "D": 2,
        "D-": 0,
        "F": 2,
        "P": 0,
        "W": 5
      },
      "retained_if_passed": {
        "students": 17,
        "retained": 15,
        "rate": 0.8824
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "ENGL 112",
      "name": "COMPOSITION I",
      "subject": "E",
      "students": 22,
      "first_pass": 22,
      "passed": 22,
      "path": {
        "first": 22,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "A": 5,
        "A-": 2,
        "B+": 1,
        "B": 9,
        "B-": 2,
        "C+": 0,
        "C": 3,
        "C-": 0,
        "D+": 0,
        "D": 0,
        "D-": 0,
        "F": 0,
        "P": 0,
        "W": 0
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
      },
      "group": null
    },
    {
      "course": "ENGL 1110",
      "name": "COMPOSITION I",
      "subject": "E",
      "students": 21,
      "first_pass": 19,
      "passed": 19,
      "path": {
        "first": 19,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 7,
        "A-": 0,
        "B+": 0,
        "B": 4,
        "B-": 1,
        "C+": 0,
        "C": 5,
        "C-": 2,
        "D+": 0,
        "D": 3,
        "D-": 0,
        "F": 2,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 19,
        "retained": 6,
        "rate": 0.3158
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "ENGL 121",
      "name": "COLLEGE COMPOSITION",
      "subject": "E",
      "students": 21,
      "first_pass": 21,
      "passed": 21,
      "path": {
        "first": 21,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "A": 10,
        "A-": 0,
        "B+": 0,
        "B": 10,
        "B-": 0,
        "C+": 0,
        "C": 1,
        "C-": 0,
        "D+": 0,
        "D": 0,
        "D-": 0,
        "F": 0,
        "P": 0,
        "W": 0
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
      },
      "group": null
    },
    {
      "course": "MATH 103",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 20,
      "first_pass": 11,
      "passed": 11,
      "path": {
        "first": 11,
        "retook_passed": 0,
        "retook_not": null,
        "no_retake": null
      },
      "grades": {
        "A": 1,
        "A-": 0,
        "B+": 0,
        "B": 4,
        "B-": 0,
        "C+": 0,
        "C": 5,
        "C-": 0,
        "D+": 0,
        "D": 1,
        "D-": 0,
        "F": 6,
        "P": 0,
        "W": 4
      },
      "retained_if_passed": {
        "students": 11,
        "retained": 9,
        "rate": 0.8182
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "ENGL 161",
      "name": "COLLEGE COMPOSITION I",
      "subject": "E",
      "students": 18,
      "first_pass": 13,
      "passed": 15,
      "path": {
        "first": 13,
        "retook_passed": null,
        "retook_not": null,
        "no_retake": null
      },
      "grades": {
        "A": 3,
        "A-": 0,
        "B+": 0,
        "B": 7,
        "B-": 0,
        "C+": 0,
        "C": 4,
        "C-": 0,
        "D+": 0,
        "D": 1,
        "D-": 0,
        "F": 4,
        "P": 0,
        "W": 2
      },
      "retained_if_passed": {
        "students": 15,
        "retained": 14,
        "rate": 0.9333
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "ENG 102",
      "name": "FIRST-YEAR COMPOSITION",
      "subject": "E",
      "students": 17,
      "first_pass": 16,
      "passed": 16,
      "path": {
        "first": 16,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 9,
        "A-": 0,
        "B+": 0,
        "B": 5,
        "B-": 0,
        "C+": 0,
        "C": 1,
        "C-": 0,
        "D+": 0,
        "D": 1,
        "D-": 0,
        "F": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 16,
        "retained": 11,
        "rate": 0.6875
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTH 103",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 17,
      "first_pass": 11,
      "passed": 12,
      "path": {
        "first": 11,
        "retook_passed": null,
        "retook_not": null,
        "no_retake": null
      },
      "grades": {
        "A": 2,
        "A-": 0,
        "B+": 0,
        "B": 5,
        "B-": 0,
        "C+": 0,
        "C": 2,
        "C-": 0,
        "D+": 0,
        "D": 3,
        "D-": 0,
        "F": 2,
        "P": 0,
        "W": 6
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
      },
      "group": null
    },
    {
      "course": "MAT 162",
      "name": "STATISTICAL REASONING",
      "subject": "M",
      "students": 14,
      "first_pass": 7,
      "passed": 7,
      "path": {
        "first": null,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 3,
        "A-": 0,
        "B+": 0,
        "B": 2,
        "B-": 0,
        "C+": 0,
        "C": 2,
        "C-": 0,
        "D+": 0,
        "D": 0,
        "D-": 0,
        "F": 5,
        "P": 0,
        "W": 2
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
      },
      "group": null
    },
    {
      "course": "MATH 120",
      "name": "MATH-120",
      "subject": "M",
      "students": 14,
      "first_pass": 12,
      "passed": 12,
      "path": {
        "first": 12,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 6,
        "A-": 1,
        "B+": 1,
        "B": 0,
        "B-": 0,
        "C+": 0,
        "C": 2,
        "C-": 0,
        "D+": 0,
        "D": 3,
        "D-": 0,
        "F": 2,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 12,
        "retained": 10,
        "rate": 0.8333
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTH 101",
      "name": "QUANTITATIVE LITERACY",
      "subject": "M",
      "students": 14,
      "first_pass": 12,
      "passed": 12,
      "path": {
        "first": 12,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 2,
        "A-": 0,
        "B+": 0,
        "B": 4,
        "B-": 0,
        "C+": 0,
        "C": 5,
        "C-": 0,
        "D+": 0,
        "D": 1,
        "D-": 0,
        "F": 2,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 12,
        "retained": 7,
        "rate": 0.5833
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MATH 202",
      "name": "INTRODUCTION TO STATISTICS",
      "subject": "M",
      "students": 13,
      "first_pass": 8,
      "passed": 8,
      "path": {
        "first": null,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 2,
        "A-": 0,
        "B+": 0,
        "B": 0,
        "B-": 0,
        "C+": 0,
        "C": 4,
        "C-": 0,
        "D+": 0,
        "D": 2,
        "D-": 0,
        "F": 2,
        "P": 0,
        "W": 3
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
      },
      "group": null
    },
    {
      "course": "MTH 107",
      "name": "BASIC STATISTICS",
      "subject": "M",
      "students": 13,
      "first_pass": 11,
      "passed": 11,
      "path": {
        "first": 11,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 6,
        "A-": 0,
        "B+": 0,
        "B": 2,
        "B-": 0,
        "C+": 0,
        "C": 1,
        "C-": 0,
        "D+": 0,
        "D": 2,
        "D-": 0,
        "F": 2,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 11,
        "retained": 8,
        "rate": 0.7273
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTH 152",
      "name": "STATISTICS (MA)",
      "subject": "M",
      "students": 13,
      "first_pass": 9,
      "passed": 9,
      "path": {
        "first": null,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 0,
        "A-": 0,
        "B+": 0,
        "B": 0,
        "B-": 0,
        "C+": 0,
        "C": 0,
        "C-": 0,
        "D+": 0,
        "D": 0,
        "D-": 0,
        "F": 3,
        "P": 9,
        "W": 1
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
      },
      "group": null
    },
    {
      "course": "MTH 140",
      "name": "PRECALCULUS",
      "subject": "M",
      "students": 12,
      "first_pass": 9,
      "passed": 10,
      "path": {
        "first": null,
        "retook_passed": null,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 0,
        "A-": 0,
        "B+": 0,
        "B": 5,
        "B-": 0,
        "C+": 0,
        "C": 3,
        "C-": 0,
        "D+": 0,
        "D": 1,
        "D-": 0,
        "F": 1,
        "P": 2,
        "W": 2
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
      },
      "group": null
    },
    {
      "course": "MTH 161",
      "name": "PRECALCULUS I",
      "subject": "M",
      "students": 12,
      "first_pass": 8,
      "passed": 9,
      "path": {
        "first": null,
        "retook_passed": null,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 2,
        "A-": 0,
        "B+": 0,
        "B": 4,
        "B-": 0,
        "C+": 0,
        "C": 2,
        "C-": 0,
        "D+": 0,
        "D": 1,
        "D-": 0,
        "F": 0,
        "P": 0,
        "W": 4
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
      },
      "group": null
    },
    {
      "course": "INRW 385",
      "name": "INTEGRATED READING AND WRITING",
      "subject": "E",
      "students": 11,
      "first_pass": 9,
      "passed": 9,
      "path": {
        "first": null,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 4,
        "A-": 0,
        "B+": 0,
        "B": 3,
        "B-": 0,
        "C+": 0,
        "C": 2,
        "C-": 0,
        "D+": 0,
        "D": 0,
        "D-": 0,
        "F": 3,
        "P": 0,
        "W": 0
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
      },
      "group": null
    },
    {
      "course": "MATH 116",
      "name": "MATH-116",
      "subject": "M",
      "students": 11,
      "first_pass": 8,
      "passed": 8,
      "path": {
        "first": null,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 3,
        "A-": 0,
        "B+": 1,
        "B": 0,
        "B-": 0,
        "C+": 0,
        "C": 0,
        "C-": 0,
        "D+": 1,
        "D": 3,
        "D-": 0,
        "F": 3,
        "P": 0,
        "W": 0
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
      },
      "group": null
    },
    {
      "course": "MATH 130",
      "name": "INTRODUCTION TO STATISTICS",
      "subject": "M",
      "students": 11,
      "first_pass": 8,
      "passed": 9,
      "path": {
        "first": null,
        "retook_passed": null,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 0,
        "A-": 3,
        "B+": 1,
        "B": 3,
        "B-": 0,
        "C+": 0,
        "C": 1,
        "C-": 0,
        "D+": 1,
        "D": 2,
        "D-": 0,
        "F": 1,
        "P": 0,
        "W": 2
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
      },
      "group": null
    },
    {
      "course": "MAT 151",
      "name": "COLLEGE ALGEBRA/FUNCTIONS",
      "subject": "M",
      "students": 10,
      "first_pass": 10,
      "passed": 10,
      "path": {
        "first": 10,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "A": 3,
        "A-": 0,
        "B+": 0,
        "B": 2,
        "B-": 0,
        "C+": 0,
        "C": 5,
        "C-": 0,
        "D+": 0,
        "D": 0,
        "D-": 0,
        "F": 0,
        "P": 0,
        "W": 0
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
      },
      "group": null
    },
    {
      "course": "MATH 104B",
      "name": "MATH-104B",
      "subject": "M",
      "students": 10,
      "first_pass": 7,
      "passed": 7,
      "path": {
        "first": null,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 3,
        "A-": 0,
        "B+": 0,
        "B": 0,
        "B-": 0,
        "C+": 0,
        "C": 2,
        "C-": 0,
        "D+": 0,
        "D": 2,
        "D-": 0,
        "F": 3,
        "P": 0,
        "W": 0
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
      },
      "group": null
    },
    {
      "course": "MTH 129",
      "name": "PRECALCULUS I",
      "subject": "M",
      "students": 10,
      "first_pass": 7,
      "passed": 7,
      "path": {
        "first": null,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 1,
        "A-": 0,
        "B+": 0,
        "B": 3,
        "B-": 0,
        "C+": 0,
        "C": 3,
        "C-": 0,
        "D+": 0,
        "D": 0,
        "D-": 0,
        "F": 3,
        "P": 0,
        "W": 0
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
      },
      "group": null
    }
  ],
  "hidden_courses": 82,
  "left_out": 22,
  "pairs_considered": 35,
  "pairs": [
    {
      "courses": [
        "ENG 111",
        "SDV 101"
      ],
      "students": 13,
      "retained": 1,
      "rate": 0.0769,
      "others_rate": 0.418,
      "gap": -34.11,
      "affected": -4.4,
      "likely_noise": false
    },
    {
      "courses": [
        "ENG 111",
        "MTH 161"
      ],
      "students": 11,
      "retained": 1,
      "rate": 0.0909,
      "others_rate": 0.4177,
      "gap": -32.68,
      "affected": -3.6,
      "likely_noise": true
    }
  ]
};

/** 2023-24 Pell recipients: each course compares them with everyone else. */
export const gatewayPell2023: GatewayResponse = {
  "meta": {
    "cohort": "2023-24",
    "filters": {
      "pell": "Y"
    },
    "retention_type": "school",
    "provisional": false,
    "min_students": 10,
    "source": "PDP analysis-ready cohort and course files (synthetic sample)",
    "loaded_at": "2026-11-07T17:01:14",
    "flagged": true,
    "year_one": "2023-24",
    "retention_term": "next academic year",
    "retention_observed": true,
    "first_term": null,
    "compared": true,
    "min_pair_students": 10,
    "grade_scale": {
      "grades": [
        {
          "grade": "A",
          "points": "4.0",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "A-",
          "points": "3.7 to under 4.0",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "B+",
          "points": "3.3 to under 3.7",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "B",
          "points": "3.0 to under 3.3",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "B-",
          "points": "2.7 to under 3.0",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "C+",
          "points": "2.3 to under 2.7",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "C",
          "points": "2.0 to under 2.3",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "C-",
          "points": "1.7 to under 2.0",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "D+",
          "points": "1.3 to under 1.7",
          "dfw": true,
          "gateway_pass": true
        },
        {
          "grade": "D",
          "points": "1.0 to under 1.3",
          "dfw": true,
          "gateway_pass": true
        },
        {
          "grade": "D-",
          "points": "0.7 to under 1.0",
          "dfw": true,
          "gateway_pass": false
        },
        {
          "grade": "F",
          "points": "under 0.7, or the code F",
          "dfw": true,
          "gateway_pass": false
        },
        {
          "grade": "P",
          "points": "the code P (pass)",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "W",
          "points": "the code W (withdrew)",
          "dfw": true,
          "gateway_pass": false
        }
      ],
      "left_out": "I (incomplete), A (audit), M or MIS (missing), O or OTH (other), and any code the PDP dictionary doesn't list, such as UW, aren't final grades, so neither page counts them."
    }
  },
  "status": "ok",
  "students": 873,
  "cohort_retention": {
    "type": "school",
    "status": "ok",
    "retained": 532,
    "students": 873,
    "numerator": 532,
    "denominator": 873,
    "rate": 0.6094,
    "n_excluded": 0,
    "n_out_of_scope": 0
  },
  "courses": [
    {
      "course": "ENG 101",
      "name": "ENG-101",
      "subject": "E",
      "students": 199,
      "first_pass": 148,
      "passed": 155,
      "path": {
        "first": 148,
        "retook_passed": null,
        "retook_not": null,
        "no_retake": 37
      },
      "grades": {
        "A": 51,
        "A-": 9,
        "B+": 6,
        "B": 29,
        "B-": 5,
        "C+": 4,
        "C": 25,
        "C-": 1,
        "D+": 2,
        "D": 4,
        "D-": 1,
        "F": 38,
        "P": 19,
        "W": 20
      },
      "retained_if_passed": {
        "students": 155,
        "retained": 122,
        "rate": 0.7871
      },
      "retained_if_not_passed": {
        "students": 44,
        "retained": 10,
        "rate": 0.2273
      },
      "group": {
        "status": "ok",
        "rate": 0.7437,
        "others_rate": 0.8054,
        "gap": -6.17,
        "likely_noise": true
      }
    },
    {
      "course": "MAT 152",
      "name": "QUANTITATIVE REASONING",
      "subject": "M",
      "students": 34,
      "first_pass": 24,
      "passed": 26,
      "path": {
        "first": 24,
        "retook_passed": null,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 8,
        "A-": 0,
        "B+": 0,
        "B": 9,
        "B-": 0,
        "C+": 0,
        "C": 9,
        "C-": 0,
        "D+": 0,
        "D": 0,
        "D-": 0,
        "F": 8,
        "P": 0,
        "W": 2
      },
      "retained_if_passed": {
        "students": 26,
        "retained": 18,
        "rate": 0.6923
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": {
        "status": "ok",
        "rate": 0.7059,
        "others_rate": 0.6818,
        "gap": 2.41,
        "likely_noise": true
      }
    },
    {
      "course": "ENGL 101",
      "name": "ENGLISH COMPOSITION I",
      "subject": "E",
      "students": 31,
      "first_pass": 24,
      "passed": 25,
      "path": {
        "first": 24,
        "retook_passed": null,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 9,
        "A-": 0,
        "B+": 0,
        "B": 7,
        "B-": 0,
        "C+": 0,
        "C": 7,
        "C-": 0,
        "D+": 0,
        "D": 3,
        "D-": 0,
        "F": 1,
        "P": 0,
        "W": 6
      },
      "retained_if_passed": {
        "students": 25,
        "retained": 19,
        "rate": 0.76
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": {
        "status": "ok",
        "rate": 0.7742,
        "others_rate": 0.8125,
        "gap": -3.83,
        "likely_noise": true
      }
    },
    {
      "course": "ENG 121",
      "name": "ENGLISH COMPOSITION I",
      "subject": "E",
      "students": 23,
      "first_pass": 14,
      "passed": 14,
      "path": {
        "first": 14,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 0,
        "A-": 0,
        "B+": 0,
        "B": 0,
        "B-": 0,
        "C+": 0,
        "C": 0,
        "C-": 0,
        "D+": 0,
        "D": 0,
        "D-": 0,
        "F": 6,
        "P": 14,
        "W": 3
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
      },
      "group": {
        "status": "ok",
        "rate": 0.6087,
        "others_rate": 0.7857,
        "gap": -17.7,
        "likely_noise": true
      }
    },
    {
      "course": "ENGL 1110",
      "name": "COMPOSITION I",
      "subject": "E",
      "students": 19,
      "first_pass": 17,
      "passed": 17,
      "path": {
        "first": 17,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 6,
        "A-": 0,
        "B+": 0,
        "B": 3,
        "B-": 1,
        "C+": 0,
        "C": 5,
        "C-": 2,
        "D+": 0,
        "D": 3,
        "D-": 0,
        "F": 2,
        "P": 0,
        "W": 0
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
      },
      "group": {
        "status": "hidden",
        "rate": null,
        "others_rate": null,
        "gap": null,
        "likely_noise": null
      }
    },
    {
      "course": "ENG 111",
      "name": "COLLEGE COMPOSITION I",
      "subject": "E",
      "students": 16,
      "first_pass": 11,
      "passed": 11,
      "path": {
        "first": 11,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 6,
        "A-": 0,
        "B+": 0,
        "B": 3,
        "B-": 0,
        "C+": 0,
        "C": 1,
        "C-": 0,
        "D+": 0,
        "D": 1,
        "D-": 0,
        "F": 1,
        "P": 0,
        "W": 4
      },
      "retained_if_passed": {
        "students": 11,
        "retained": 9,
        "rate": 0.8182
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": {
        "status": "ok",
        "rate": 0.6875,
        "others_rate": 0.85,
        "gap": -16.25,
        "likely_noise": true
      }
    },
    {
      "course": "ENG 102",
      "name": "FIRST-YEAR COMPOSITION",
      "subject": "E",
      "students": 11,
      "first_pass": 11,
      "passed": 11,
      "path": {
        "first": 11,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "A": 7,
        "A-": 0,
        "B+": 0,
        "B": 2,
        "B-": 0,
        "C+": 0,
        "C": 1,
        "C-": 0,
        "D+": 0,
        "D": 1,
        "D-": 0,
        "F": 0,
        "P": 0,
        "W": 0
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
      },
      "group": {
        "status": "hidden",
        "rate": null,
        "others_rate": null,
        "gap": null,
        "likely_noise": null
      }
    },
    {
      "course": "ENGL 112",
      "name": "COMPOSITION I",
      "subject": "E",
      "students": 10,
      "first_pass": 10,
      "passed": 10,
      "path": {
        "first": 10,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "A": 4,
        "A-": 0,
        "B+": 0,
        "B": 4,
        "B-": 0,
        "C+": 0,
        "C": 2,
        "C-": 0,
        "D+": 0,
        "D": 0,
        "D-": 0,
        "F": 0,
        "P": 0,
        "W": 0
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
      },
      "group": {
        "status": "ok",
        "rate": 1.0,
        "others_rate": 1.0,
        "gap": 0.0,
        "likely_noise": true
      }
    }
  ],
  "hidden_courses": 101,
  "left_out": 11,
  "pairs_considered": 14,
  "pairs": [
    {
      "courses": [
        "COM 101",
        "ENG 101"
      ],
      "students": 20,
      "retained": 10,
      "rate": 0.5,
      "others_rate": 0.612,
      "gap": -11.2,
      "affected": -2.2,
      "likely_noise": true
    },
    {
      "courses": [
        "ENG 101",
        "ENG 11"
      ],
      "students": 14,
      "retained": 7,
      "rate": 0.5,
      "others_rate": 0.6112,
      "gap": -11.12,
      "affected": -1.6,
      "likely_noise": true
    },
    {
      "courses": [
        "ENG 101",
        "SSC 100"
      ],
      "students": 23,
      "retained": 13,
      "rate": 0.5652,
      "others_rate": 0.6106,
      "gap": -4.54,
      "affected": -1.0,
      "likely_noise": true
    }
  ]
};

/** 2024-25: its next year is only partly in the data. */
export const gateway2024: GatewayResponse = {
  "meta": {
    "cohort": "2024-25",
    "filters": {},
    "retention_type": "school",
    "provisional": true,
    "min_students": 10,
    "source": "PDP analysis-ready cohort and course files (synthetic sample)",
    "loaded_at": "2026-11-07T17:01:14",
    "flagged": true,
    "year_one": "2024-25",
    "retention_term": "next academic year",
    "retention_observed": true,
    "first_term": null,
    "compared": false,
    "min_pair_students": 10,
    "grade_scale": {
      "grades": [
        {
          "grade": "A",
          "points": "4.0",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "A-",
          "points": "3.7 to under 4.0",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "B+",
          "points": "3.3 to under 3.7",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "B",
          "points": "3.0 to under 3.3",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "B-",
          "points": "2.7 to under 3.0",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "C+",
          "points": "2.3 to under 2.7",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "C",
          "points": "2.0 to under 2.3",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "C-",
          "points": "1.7 to under 2.0",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "D+",
          "points": "1.3 to under 1.7",
          "dfw": true,
          "gateway_pass": true
        },
        {
          "grade": "D",
          "points": "1.0 to under 1.3",
          "dfw": true,
          "gateway_pass": true
        },
        {
          "grade": "D-",
          "points": "0.7 to under 1.0",
          "dfw": true,
          "gateway_pass": false
        },
        {
          "grade": "F",
          "points": "under 0.7, or the code F",
          "dfw": true,
          "gateway_pass": false
        },
        {
          "grade": "P",
          "points": "the code P (pass)",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "W",
          "points": "the code W (withdrew)",
          "dfw": true,
          "gateway_pass": false
        }
      ],
      "left_out": "I (incomplete), A (audit), M or MIS (missing), O or OTH (other), and any code the PDP dictionary doesn't list, such as UW, aren't final grades, so neither page counts them."
    }
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
      "students": 366,
      "first_pass": 289,
      "passed": 295,
      "path": {
        "first": 289,
        "retook_passed": null,
        "retook_not": null,
        "no_retake": 66
      },
      "grades": {
        "A": 115,
        "A-": 8,
        "B+": 7,
        "B": 44,
        "B-": 5,
        "C+": 6,
        "C": 45,
        "C-": 3,
        "D+": 2,
        "D": 10,
        "D-": 1,
        "F": 63,
        "P": 53,
        "W": 20
      },
      "retained_if_passed": {
        "students": 295,
        "retained": 211,
        "rate": 0.7153
      },
      "retained_if_not_passed": {
        "students": 71,
        "retained": 25,
        "rate": 0.3521
      },
      "group": null
    },
    {
      "course": "ENGL 101",
      "name": "ENGLISH COMPOSITION I",
      "subject": "E",
      "students": 76,
      "first_pass": 59,
      "passed": 59,
      "path": {
        "first": 59,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 17
      },
      "grades": {
        "A": 29,
        "A-": 0,
        "B+": 0,
        "B": 19,
        "B-": 0,
        "C+": 0,
        "C": 6,
        "C-": 0,
        "D+": 0,
        "D": 5,
        "D-": 0,
        "F": 13,
        "P": 0,
        "W": 4
      },
      "retained_if_passed": {
        "students": 59,
        "retained": 34,
        "rate": 0.5763
      },
      "retained_if_not_passed": {
        "students": 17,
        "retained": 1,
        "rate": 0.0588
      },
      "group": null
    },
    {
      "course": "MAT 152",
      "name": "QUANTITATIVE REASONING",
      "subject": "M",
      "students": 53,
      "first_pass": 35,
      "passed": 36,
      "path": {
        "first": 35,
        "retook_passed": null,
        "retook_not": 0,
        "no_retake": 17
      },
      "grades": {
        "A": 13,
        "A-": 0,
        "B+": 0,
        "B": 14,
        "B-": 0,
        "C+": 0,
        "C": 9,
        "C-": 0,
        "D+": 0,
        "D": 0,
        "D-": 0,
        "F": 16,
        "P": 0,
        "W": 2
      },
      "retained_if_passed": {
        "students": 36,
        "retained": 27,
        "rate": 0.75
      },
      "retained_if_not_passed": {
        "students": 17,
        "retained": 2,
        "rate": 0.1176
      },
      "group": null
    },
    {
      "course": "MAT 162",
      "name": "STATISTICAL REASONING",
      "subject": "M",
      "students": 29,
      "first_pass": 18,
      "passed": 20,
      "path": {
        "first": 18,
        "retook_passed": null,
        "retook_not": null,
        "no_retake": null
      },
      "grades": {
        "A": 9,
        "A-": 0,
        "B+": 0,
        "B": 4,
        "B-": 0,
        "C+": 0,
        "C": 7,
        "C-": 0,
        "D+": 0,
        "D": 0,
        "D-": 0,
        "F": 9,
        "P": 0,
        "W": 3
      },
      "retained_if_passed": {
        "students": 20,
        "retained": 12,
        "rate": 0.6
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "ENGL 121",
      "name": "COLLEGE COMPOSITION",
      "subject": "E",
      "students": 28,
      "first_pass": 28,
      "passed": 28,
      "path": {
        "first": 28,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "A": 13,
        "A-": 0,
        "B+": 0,
        "B": 7,
        "B-": 0,
        "C+": 0,
        "C": 8,
        "C-": 0,
        "D+": 0,
        "D": 0,
        "D-": 0,
        "F": 0,
        "P": 0,
        "W": 0
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
      },
      "group": null
    },
    {
      "course": "ENGL 100",
      "name": "COMPOSITION I",
      "subject": "E",
      "students": 23,
      "first_pass": 21,
      "passed": 21,
      "path": {
        "first": 21,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 5,
        "A-": 7,
        "B+": 0,
        "B": 5,
        "B-": 1,
        "C+": 0,
        "C": 3,
        "C-": 0,
        "D+": 0,
        "D": 0,
        "D-": 0,
        "F": 2,
        "P": 0,
        "W": 0
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
      },
      "group": null
    },
    {
      "course": "MATH 116",
      "name": "MATH-116",
      "subject": "M",
      "students": 22,
      "first_pass": 14,
      "passed": 15,
      "path": {
        "first": 14,
        "retook_passed": null,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 9,
        "A-": 1,
        "B+": 0,
        "B": 0,
        "B-": 1,
        "C+": 1,
        "C": 2,
        "C-": 1,
        "D+": 0,
        "D": 1,
        "D-": 0,
        "F": 7,
        "P": 0,
        "W": 2
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
      },
      "group": null
    },
    {
      "course": "ENG 102",
      "name": "FIRST-YEAR COMPOSITION",
      "subject": "E",
      "students": 19,
      "first_pass": 17,
      "passed": 17,
      "path": {
        "first": 17,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 11,
        "A-": 0,
        "B+": 0,
        "B": 4,
        "B-": 0,
        "C+": 0,
        "C": 1,
        "C-": 0,
        "D+": 0,
        "D": 1,
        "D-": 0,
        "F": 2,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 17,
        "retained": 11,
        "rate": 0.6471
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "ENGL 161",
      "name": "\"COLLEGE COMPOSITION I\"",
      "subject": "E",
      "students": 19,
      "first_pass": 14,
      "passed": 15,
      "path": {
        "first": 14,
        "retook_passed": null,
        "retook_not": null,
        "no_retake": null
      },
      "grades": {
        "A": 8,
        "A-": 0,
        "B+": 0,
        "B": 3,
        "B-": 0,
        "C+": 0,
        "C": 4,
        "C-": 0,
        "D+": 0,
        "D": 1,
        "D-": 0,
        "F": 3,
        "P": 0,
        "W": 3
      },
      "retained_if_passed": {
        "students": 15,
        "retained": 10,
        "rate": 0.6667
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MATH 130",
      "name": "INTRODUCTION TO STATISTICS",
      "subject": "M",
      "students": 18,
      "first_pass": 12,
      "passed": 13,
      "path": {
        "first": 12,
        "retook_passed": null,
        "retook_not": null,
        "no_retake": null
      },
      "grades": {
        "A": 1,
        "A-": 1,
        "B+": 1,
        "B": 2,
        "B-": 1,
        "C+": 0,
        "C": 5,
        "C-": 0,
        "D+": 0,
        "D": 2,
        "D-": 1,
        "F": 5,
        "P": 0,
        "W": 3
      },
      "retained_if_passed": {
        "students": 13,
        "retained": 7,
        "rate": 0.5385
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "ENG 111",
      "name": "COLLEGE COMPOSITION I",
      "subject": "E",
      "students": 17,
      "first_pass": 13,
      "passed": 13,
      "path": {
        "first": 13,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 9,
        "A-": 0,
        "B+": 0,
        "B": 3,
        "B-": 0,
        "C+": 0,
        "C": 0,
        "C-": 0,
        "D+": 0,
        "D": 1,
        "D-": 0,
        "F": 2,
        "P": 0,
        "W": 3
      },
      "retained_if_passed": {
        "students": 13,
        "retained": 5,
        "rate": 0.3846
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "ENGL 1110",
      "name": "COMPOSITION I",
      "subject": "E",
      "students": 17,
      "first_pass": 8,
      "passed": 8,
      "path": {
        "first": null,
        "retook_passed": 0,
        "retook_not": null,
        "no_retake": null
      },
      "grades": {
        "A": 2,
        "A-": 0,
        "B+": 0,
        "B": 4,
        "B-": 0,
        "C+": 0,
        "C": 2,
        "C-": 0,
        "D+": 0,
        "D": 0,
        "D-": 0,
        "F": 11,
        "P": 0,
        "W": 1
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
      },
      "group": null
    },
    {
      "course": "MATH 103",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 17,
      "first_pass": 13,
      "passed": 13,
      "path": {
        "first": 13,
        "retook_passed": 0,
        "retook_not": null,
        "no_retake": null
      },
      "grades": {
        "A": 9,
        "A-": 0,
        "B+": 0,
        "B": 3,
        "B-": 0,
        "C+": 0,
        "C": 0,
        "C-": 0,
        "D+": 0,
        "D": 1,
        "D-": 0,
        "F": 3,
        "P": 0,
        "W": 2
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
      },
      "group": null
    },
    {
      "course": "MATH 140",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 17,
      "first_pass": 14,
      "passed": 14,
      "path": {
        "first": 14,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 5,
        "A-": 1,
        "B+": 0,
        "B": 2,
        "B-": 2,
        "C+": 2,
        "C": 0,
        "C-": 1,
        "D+": 0,
        "D": 1,
        "D-": 0,
        "F": 2,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 14,
        "retained": 5,
        "rate": 0.3571
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTH 103",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 15,
      "first_pass": 9,
      "passed": 9,
      "path": {
        "first": null,
        "retook_passed": 0,
        "retook_not": null,
        "no_retake": null
      },
      "grades": {
        "A": 1,
        "A-": 0,
        "B+": 0,
        "B": 5,
        "B-": 0,
        "C+": 0,
        "C": 3,
        "C-": 0,
        "D+": 0,
        "D": 0,
        "D-": 0,
        "F": 4,
        "P": 0,
        "W": 4
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
      },
      "group": null
    },
    {
      "course": "ENGL 162",
      "name": "\"COLLEGE COMPOSITION II\"",
      "subject": "E",
      "students": 14,
      "first_pass": 11,
      "passed": 11,
      "path": {
        "first": 11,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 6,
        "A-": 0,
        "B+": 0,
        "B": 5,
        "B-": 0,
        "C+": 0,
        "C": 0,
        "C-": 0,
        "D+": 0,
        "D": 0,
        "D-": 0,
        "F": 1,
        "P": 0,
        "W": 2
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
      },
      "group": null
    },
    {
      "course": "MATH 104B",
      "name": "MATH-104B",
      "subject": "M",
      "students": 13,
      "first_pass": 8,
      "passed": 8,
      "path": {
        "first": null,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 5,
        "A-": 0,
        "B+": 0,
        "B": 0,
        "B-": 0,
        "C+": 0,
        "C": 2,
        "C-": 0,
        "D+": 0,
        "D": 1,
        "D-": 0,
        "F": 4,
        "P": 0,
        "W": 1
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
      },
      "group": null
    },
    {
      "course": "MATH 202",
      "name": "INTRODUCTION TO STATISTICS",
      "subject": "M",
      "students": 13,
      "first_pass": 10,
      "passed": 10,
      "path": {
        "first": 10,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 2,
        "A-": 0,
        "B+": 0,
        "B": 1,
        "B-": 0,
        "C+": 0,
        "C": 7,
        "C-": 0,
        "D+": 0,
        "D": 0,
        "D-": 0,
        "F": 0,
        "P": 0,
        "W": 3
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
      },
      "group": null
    },
    {
      "course": "MATH 150",
      "name": "PRE-CALCULUS",
      "subject": "M",
      "students": 12,
      "first_pass": 12,
      "passed": 12,
      "path": {
        "first": 12,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "A": 5,
        "A-": 4,
        "B+": 1,
        "B": 0,
        "B-": 0,
        "C+": 0,
        "C": 1,
        "C-": 1,
        "D+": 0,
        "D": 0,
        "D-": 0,
        "F": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 12,
        "retained": 6,
        "rate": 0.5
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MATH 314",
      "name": "COLLEGE ALGEBRA MATH PATHWAY",
      "subject": "M",
      "students": 12,
      "first_pass": 12,
      "passed": 12,
      "path": {
        "first": 12,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "A": 11,
        "A-": 0,
        "B+": 0,
        "B": 1,
        "B-": 0,
        "C+": 0,
        "C": 0,
        "C-": 0,
        "D+": 0,
        "D": 0,
        "D-": 0,
        "F": 0,
        "P": 0,
        "W": 0
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
      },
      "group": null
    },
    {
      "course": "MTH 165",
      "name": "ELEMENTARY STATISTICS",
      "subject": "M",
      "students": 12,
      "first_pass": 5,
      "passed": 6,
      "path": {
        "first": null,
        "retook_passed": null,
        "retook_not": null,
        "no_retake": null
      },
      "grades": {
        "A": 3,
        "A-": 0,
        "B+": 0,
        "B": 1,
        "B-": 0,
        "C+": 0,
        "C": 2,
        "C-": 0,
        "D+": 0,
        "D": 0,
        "D-": 0,
        "F": 5,
        "P": 0,
        "W": 3
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
      },
      "group": null
    },
    {
      "course": "MTHM 168",
      "name": "\"STATISTICS\"",
      "subject": "M",
      "students": 12,
      "first_pass": 8,
      "passed": 9,
      "path": {
        "first": null,
        "retook_passed": null,
        "retook_not": null,
        "no_retake": null
      },
      "grades": {
        "A": 2,
        "A-": 0,
        "B+": 0,
        "B": 2,
        "B-": 0,
        "C+": 0,
        "C": 4,
        "C-": 0,
        "D+": 0,
        "D": 1,
        "D-": 0,
        "F": 1,
        "P": 0,
        "W": 4
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
      },
      "group": null
    },
    {
      "course": "ENG 11103",
      "name": "COMPOSITION I",
      "subject": "E",
      "students": 11,
      "first_pass": 8,
      "passed": 8,
      "path": {
        "first": null,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 0,
        "A-": 0,
        "B+": 0,
        "B": 0,
        "B-": 0,
        "C+": 0,
        "C": 0,
        "C-": 0,
        "D+": 0,
        "D": 0,
        "D-": 0,
        "F": 3,
        "P": 8,
        "W": 0
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
      },
      "group": null
    },
    {
      "course": "MTH 200",
      "name": "CALCULUS I",
      "subject": "M",
      "students": 11,
      "first_pass": 5,
      "passed": 6,
      "path": {
        "first": null,
        "retook_passed": null,
        "retook_not": null,
        "no_retake": null
      },
      "grades": {
        "A": 2,
        "A-": 0,
        "B+": 0,
        "B": 2,
        "B-": 0,
        "C+": 0,
        "C": 1,
        "C-": 0,
        "D+": 0,
        "D": 1,
        "D-": 0,
        "F": 2,
        "P": 0,
        "W": 6
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
      },
      "group": null
    },
    {
      "course": "MTH 101",
      "name": "QUANTITATIVE LITERACY",
      "subject": "M",
      "students": 10,
      "first_pass": 7,
      "passed": 7,
      "path": {
        "first": null,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": null
      },
      "grades": {
        "A": 2,
        "A-": 0,
        "B+": 0,
        "B": 2,
        "B-": 0,
        "C+": 0,
        "C": 2,
        "C-": 0,
        "D+": 0,
        "D": 1,
        "D-": 0,
        "F": 2,
        "P": 0,
        "W": 1
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
      },
      "group": null
    }
  ],
  "hidden_courses": 74,
  "left_out": 32,
  "pairs_considered": 34,
  "pairs": [
    {
      "courses": [
        "ENGL 101",
        "MA 119"
      ],
      "students": 41,
      "retained": 2,
      "rate": 0.0488,
      "others_rate": 0.3839,
      "gap": -33.51,
      "affected": -13.7,
      "likely_noise": false
    },
    {
      "courses": [
        "ENGL 101",
        "ST 100"
      ],
      "students": 22,
      "retained": 2,
      "rate": 0.0909,
      "others_rate": 0.3811,
      "gap": -29.02,
      "affected": -6.4,
      "likely_noise": false
    },
    {
      "courses": [
        "ENGL 101",
        "SOCY 101"
      ],
      "students": 17,
      "retained": 1,
      "rate": 0.0588,
      "others_rate": 0.3807,
      "gap": -32.19,
      "affected": -5.5,
      "likely_noise": false
    }
  ]
};

/** Fewer than 10 students match: no numbers. */
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
    "loaded_at": "2026-11-07T17:01:14",
    "flagged": true,
    "year_one": "2023-24",
    "retention_term": "next academic year",
    "retention_observed": true,
    "first_term": "Fall 2023",
    "compared": true,
    "min_pair_students": 10,
    "grade_scale": {
      "grades": [
        {
          "grade": "A",
          "points": "4.0",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "A-",
          "points": "3.7 to under 4.0",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "B+",
          "points": "3.3 to under 3.7",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "B",
          "points": "3.0 to under 3.3",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "B-",
          "points": "2.7 to under 3.0",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "C+",
          "points": "2.3 to under 2.7",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "C",
          "points": "2.0 to under 2.3",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "C-",
          "points": "1.7 to under 2.0",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "D+",
          "points": "1.3 to under 1.7",
          "dfw": true,
          "gateway_pass": true
        },
        {
          "grade": "D",
          "points": "1.0 to under 1.3",
          "dfw": true,
          "gateway_pass": true
        },
        {
          "grade": "D-",
          "points": "0.7 to under 1.0",
          "dfw": true,
          "gateway_pass": false
        },
        {
          "grade": "F",
          "points": "under 0.7, or the code F",
          "dfw": true,
          "gateway_pass": false
        },
        {
          "grade": "P",
          "points": "the code P (pass)",
          "dfw": false,
          "gateway_pass": true
        },
        {
          "grade": "W",
          "points": "the code W (withdrew)",
          "dfw": true,
          "gateway_pass": false
        }
      ],
      "left_out": "I (incomplete), A (audit), M or MIS (missing), O or OTH (other), and any code the PDP dictionary doesn't list, such as UW, aren't final grades, so neither page counts them."
    }
  },
  "status": "suppressed",
  "students": null,
  "cohort_retention": null,
  "courses": [],
  "hidden_courses": 0,
  "left_out": null,
  "pairs_considered": 0,
  "pairs": []
};
