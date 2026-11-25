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
    "min_students": 1,
    "source": "PDP analysis-ready cohort and course files (synthetic sample)",
    "loaded_at": "2026-11-24T00:47:20",
    "flagged": true,
    "year_one": "2023-24",
    "retention_term": "next academic year",
    "retention_observed": true,
    "first_term": null,
    "compared": false,
    "min_pair_students": 1,
    "grade_scale": {
      "grades": [
        {
          "grade": "C or higher",
          "points": "2.0 and up",
          "counted": true
        },
        {
          "grade": "Below C",
          "points": "1.0 to under 2.0 (D, D+, C-)",
          "counted": false
        },
        {
          "grade": "Under 1.0",
          "points": "under 1.0 (D- or F), or the code F",
          "counted": false
        },
        {
          "grade": "P",
          "points": "the code P (pass)",
          "counted": true
        },
        {
          "grade": "W",
          "points": "the code W (withdrew)",
          "counted": false
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
      "first_pass": 281,
      "passed": 299,
      "path": {
        "first": 281,
        "retook_passed": 18,
        "retook_not": 9,
        "no_retake": 76
      },
      "grades": {
        "C or higher": 249,
        "Below C": 17,
        "Under 1.0": 65,
        "P": 50,
        "W": 31
      },
      "retained_if_passed": {
        "students": 299,
        "retained": 236,
        "rate": 0.7893
      },
      "retained_if_not_passed": {
        "students": 85,
        "retained": 24,
        "rate": 0.2824
      },
      "group": null
    },
    {
      "course": "ENGL 101",
      "name": "ENGLISH COMPOSITION I",
      "subject": "E",
      "students": 63,
      "first_pass": 45,
      "passed": 48,
      "path": {
        "first": 45,
        "retook_passed": 3,
        "retook_not": 2,
        "no_retake": 13
      },
      "grades": {
        "C or higher": 48,
        "Below C": 6,
        "Under 1.0": 6,
        "P": 0,
        "W": 8
      },
      "retained_if_passed": {
        "students": 48,
        "retained": 37,
        "rate": 0.7708
      },
      "retained_if_not_passed": {
        "students": 15,
        "retained": 6,
        "rate": 0.4
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
        "retook_passed": 2,
        "retook_not": 1,
        "no_retake": 14
      },
      "grades": {
        "C or higher": 42,
        "Below C": 0,
        "Under 1.0": 14,
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
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 8,
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
      "first_pass": 27,
      "passed": 29,
      "path": {
        "first": 27,
        "retook_passed": 2,
        "retook_not": 0,
        "no_retake": 7
      },
      "grades": {
        "C or higher": 29,
        "Below C": 1,
        "Under 1.0": 3,
        "P": 0,
        "W": 5
      },
      "retained_if_passed": {
        "students": 29,
        "retained": 21,
        "rate": 0.7241
      },
      "retained_if_not_passed": {
        "students": 7,
        "retained": 2,
        "rate": 0.2857
      },
      "group": null
    },
    {
      "course": "MTH 165",
      "name": "ELEMENTARY STATISTICS",
      "subject": "M",
      "students": 23,
      "first_pass": 14,
      "passed": 15,
      "path": {
        "first": 14,
        "retook_passed": 1,
        "retook_not": 0,
        "no_retake": 8
      },
      "grades": {
        "C or higher": 15,
        "Below C": 2,
        "Under 1.0": 2,
        "P": 0,
        "W": 5
      },
      "retained_if_passed": {
        "students": 15,
        "retained": 14,
        "rate": 0.9333
      },
      "retained_if_not_passed": {
        "students": 8,
        "retained": 4,
        "rate": 0.5
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
        "C or higher": 22,
        "Below C": 0,
        "Under 1.0": 0,
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
      "first_pass": 15,
      "passed": 16,
      "path": {
        "first": 15,
        "retook_passed": 1,
        "retook_not": 0,
        "no_retake": 5
      },
      "grades": {
        "C or higher": 17,
        "Below C": 5,
        "Under 1.0": 2,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 16,
        "retained": 12,
        "rate": 0.75
      },
      "retained_if_not_passed": {
        "students": 5,
        "retained": 3,
        "rate": 0.6
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
        "C or higher": 21,
        "Below C": 0,
        "Under 1.0": 0,
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
      "first_pass": 10,
      "passed": 10,
      "path": {
        "first": 10,
        "retook_passed": 0,
        "retook_not": 1,
        "no_retake": 9
      },
      "grades": {
        "C or higher": 10,
        "Below C": 1,
        "Under 1.0": 6,
        "P": 0,
        "W": 4
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
      },
      "group": null
    },
    {
      "course": "ENGL 161",
      "name": "COLLEGE COMPOSITION I",
      "subject": "E",
      "students": 18,
      "first_pass": 12,
      "passed": 14,
      "path": {
        "first": 12,
        "retook_passed": 2,
        "retook_not": 1,
        "no_retake": 3
      },
      "grades": {
        "C or higher": 14,
        "Below C": 1,
        "Under 1.0": 4,
        "P": 0,
        "W": 2
      },
      "retained_if_passed": {
        "students": 14,
        "retained": 13,
        "rate": 0.9286
      },
      "retained_if_not_passed": {
        "students": 4,
        "retained": 3,
        "rate": 0.75
      },
      "group": null
    },
    {
      "course": "ENG 102",
      "name": "FIRST-YEAR COMPOSITION",
      "subject": "E",
      "students": 17,
      "first_pass": 15,
      "passed": 15,
      "path": {
        "first": 15,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 2
      },
      "grades": {
        "C or higher": 15,
        "Below C": 1,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 15,
        "retained": 12,
        "rate": 0.8
      },
      "retained_if_not_passed": {
        "students": 2,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "MTH 103",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 17,
      "first_pass": 9,
      "passed": 9,
      "path": {
        "first": 9,
        "retook_passed": 0,
        "retook_not": 3,
        "no_retake": 5
      },
      "grades": {
        "C or higher": 9,
        "Below C": 3,
        "Under 1.0": 2,
        "P": 0,
        "W": 6
      },
      "retained_if_passed": {
        "students": 9,
        "retained": 6,
        "rate": 0.6667
      },
      "retained_if_not_passed": {
        "students": 8,
        "retained": 8,
        "rate": 1.0
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
        "first": 7,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 7
      },
      "grades": {
        "C or higher": 7,
        "Below C": 0,
        "Under 1.0": 5,
        "P": 0,
        "W": 2
      },
      "retained_if_passed": {
        "students": 7,
        "retained": 5,
        "rate": 0.7143
      },
      "retained_if_not_passed": {
        "students": 7,
        "retained": 4,
        "rate": 0.5714
      },
      "group": null
    },
    {
      "course": "MATH 120",
      "name": "MATH-120",
      "subject": "M",
      "students": 14,
      "first_pass": 10,
      "passed": 10,
      "path": {
        "first": 10,
        "retook_passed": 0,
        "retook_not": 1,
        "no_retake": 3
      },
      "grades": {
        "C or higher": 10,
        "Below C": 3,
        "Under 1.0": 2,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 10,
        "retained": 9,
        "rate": 0.9
      },
      "retained_if_not_passed": {
        "students": 4,
        "retained": 3,
        "rate": 0.75
      },
      "group": null
    },
    {
      "course": "MTH 101",
      "name": "QUANTITATIVE LITERACY",
      "subject": "M",
      "students": 14,
      "first_pass": 11,
      "passed": 11,
      "path": {
        "first": 11,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 3
      },
      "grades": {
        "C or higher": 11,
        "Below C": 1,
        "Under 1.0": 2,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 11,
        "retained": 7,
        "rate": 0.6364
      },
      "retained_if_not_passed": {
        "students": 3,
        "retained": 3,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "MATH 202",
      "name": "INTRODUCTION TO STATISTICS",
      "subject": "M",
      "students": 13,
      "first_pass": 6,
      "passed": 6,
      "path": {
        "first": 6,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 7
      },
      "grades": {
        "C or higher": 6,
        "Below C": 2,
        "Under 1.0": 2,
        "P": 0,
        "W": 3
      },
      "retained_if_passed": {
        "students": 6,
        "retained": 6,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 7,
        "retained": 4,
        "rate": 0.5714
      },
      "group": null
    },
    {
      "course": "MTH 107",
      "name": "BASIC STATISTICS",
      "subject": "M",
      "students": 13,
      "first_pass": 9,
      "passed": 9,
      "path": {
        "first": 9,
        "retook_passed": 0,
        "retook_not": 1,
        "no_retake": 3
      },
      "grades": {
        "C or higher": 9,
        "Below C": 2,
        "Under 1.0": 2,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 9,
        "retained": 8,
        "rate": 0.8889
      },
      "retained_if_not_passed": {
        "students": 4,
        "retained": 3,
        "rate": 0.75
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
        "first": 9,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 4
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 3,
        "P": 9,
        "W": 1
      },
      "retained_if_passed": {
        "students": 9,
        "retained": 7,
        "rate": 0.7778
      },
      "retained_if_not_passed": {
        "students": 4,
        "retained": 1,
        "rate": 0.25
      },
      "group": null
    },
    {
      "course": "MTH 140",
      "name": "PRECALCULUS",
      "subject": "M",
      "students": 12,
      "first_pass": 8,
      "passed": 10,
      "path": {
        "first": 8,
        "retook_passed": 2,
        "retook_not": 0,
        "no_retake": 2
      },
      "grades": {
        "C or higher": 8,
        "Below C": 1,
        "Under 1.0": 1,
        "P": 2,
        "W": 2
      },
      "retained_if_passed": {
        "students": 10,
        "retained": 9,
        "rate": 0.9
      },
      "retained_if_not_passed": {
        "students": 2,
        "retained": 1,
        "rate": 0.5
      },
      "group": null
    },
    {
      "course": "MTH 161",
      "name": "PRECALCULUS I",
      "subject": "M",
      "students": 12,
      "first_pass": 8,
      "passed": 8,
      "path": {
        "first": 8,
        "retook_passed": 0,
        "retook_not": 1,
        "no_retake": 3
      },
      "grades": {
        "C or higher": 8,
        "Below C": 1,
        "Under 1.0": 0,
        "P": 0,
        "W": 4
      },
      "retained_if_passed": {
        "students": 8,
        "retained": 7,
        "rate": 0.875
      },
      "retained_if_not_passed": {
        "students": 4,
        "retained": 1,
        "rate": 0.25
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
        "first": 9,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 2
      },
      "grades": {
        "C or higher": 9,
        "Below C": 0,
        "Under 1.0": 3,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 9,
        "retained": 6,
        "rate": 0.6667
      },
      "retained_if_not_passed": {
        "students": 2,
        "retained": 1,
        "rate": 0.5
      },
      "group": null
    },
    {
      "course": "MATH 116",
      "name": "MATH-116",
      "subject": "M",
      "students": 11,
      "first_pass": 4,
      "passed": 4,
      "path": {
        "first": 4,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 7
      },
      "grades": {
        "C or higher": 4,
        "Below C": 4,
        "Under 1.0": 3,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 4,
        "retained": 2,
        "rate": 0.5
      },
      "retained_if_not_passed": {
        "students": 7,
        "retained": 3,
        "rate": 0.4286
      },
      "group": null
    },
    {
      "course": "MATH 130",
      "name": "INTRODUCTION TO STATISTICS",
      "subject": "M",
      "students": 11,
      "first_pass": 7,
      "passed": 8,
      "path": {
        "first": 7,
        "retook_passed": 1,
        "retook_not": 1,
        "no_retake": 2
      },
      "grades": {
        "C or higher": 8,
        "Below C": 3,
        "Under 1.0": 1,
        "P": 0,
        "W": 2
      },
      "retained_if_passed": {
        "students": 8,
        "retained": 4,
        "rate": 0.5
      },
      "retained_if_not_passed": {
        "students": 3,
        "retained": 1,
        "rate": 0.3333
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
        "C or higher": 10,
        "Below C": 0,
        "Under 1.0": 0,
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
      "first_pass": 5,
      "passed": 5,
      "path": {
        "first": 5,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 5
      },
      "grades": {
        "C or higher": 5,
        "Below C": 2,
        "Under 1.0": 3,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 5,
        "retained": 4,
        "rate": 0.8
      },
      "retained_if_not_passed": {
        "students": 5,
        "retained": 0,
        "rate": 0.0
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
        "first": 7,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 3
      },
      "grades": {
        "C or higher": 7,
        "Below C": 0,
        "Under 1.0": 3,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 7,
        "retained": 6,
        "rate": 0.8571
      },
      "retained_if_not_passed": {
        "students": 3,
        "retained": 1,
        "rate": 0.3333
      },
      "group": null
    },
    {
      "course": "MATH 150",
      "name": "PRE-CALCULUS",
      "subject": "M",
      "students": 9,
      "first_pass": 9,
      "passed": 9,
      "path": {
        "first": 9,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 9,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 9,
        "retained": 5,
        "rate": 0.5556
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MATH 1130",
      "name": "SURVEY OF MATHEMATICS",
      "subject": "M",
      "students": 8,
      "first_pass": 4,
      "passed": 5,
      "path": {
        "first": 4,
        "retook_passed": 1,
        "retook_not": 0,
        "no_retake": 3
      },
      "grades": {
        "C or higher": 5,
        "Below C": 1,
        "Under 1.0": 1,
        "P": 0,
        "W": 2
      },
      "retained_if_passed": {
        "students": 5,
        "retained": 4,
        "rate": 0.8
      },
      "retained_if_not_passed": {
        "students": 3,
        "retained": 2,
        "rate": 0.6667
      },
      "group": null
    },
    {
      "course": "MTH 112",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 8,
      "first_pass": 7,
      "passed": 7,
      "path": {
        "first": 7,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 7,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 7,
        "retained": 4,
        "rate": 0.5714
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "MTH 142",
      "name": "GENERAL EDUCATION STATISTICS",
      "subject": "M",
      "students": 8,
      "first_pass": 8,
      "passed": 8,
      "path": {
        "first": 8,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 8,
        "W": 0
      },
      "retained_if_passed": {
        "students": 8,
        "retained": 8,
        "rate": 1.0
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
      "students": 8,
      "first_pass": 5,
      "passed": 5,
      "path": {
        "first": 5,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 3
      },
      "grades": {
        "C or higher": 5,
        "Below C": 2,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 5,
        "retained": 3,
        "rate": 0.6
      },
      "retained_if_not_passed": {
        "students": 3,
        "retained": 3,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "MTHM 168",
      "name": "STATISTICS",
      "subject": "M",
      "students": 8,
      "first_pass": 5,
      "passed": 5,
      "path": {
        "first": 5,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 3
      },
      "grades": {
        "C or higher": 5,
        "Below C": 1,
        "Under 1.0": 1,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 5,
        "retained": 5,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 3,
        "retained": 1,
        "rate": 0.3333
      },
      "group": null
    },
    {
      "course": "ENGL 162",
      "name": "\"COLLEGE COMPOSITION II\"",
      "subject": "E",
      "students": 7,
      "first_pass": 5,
      "passed": 5,
      "path": {
        "first": 5,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 2
      },
      "grades": {
        "C or higher": 5,
        "Below C": 1,
        "Under 1.0": 0,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 5,
        "retained": 4,
        "rate": 0.8
      },
      "retained_if_not_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "MAT 172",
      "name": "MATH FOR TCHRS I: NUM & OPR",
      "subject": "M",
      "students": 7,
      "first_pass": 4,
      "passed": 4,
      "path": {
        "first": 4,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 3
      },
      "grades": {
        "C or higher": 4,
        "Below C": 0,
        "Under 1.0": 2,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 4,
        "retained": 2,
        "rate": 0.5
      },
      "retained_if_not_passed": {
        "students": 3,
        "retained": 2,
        "rate": 0.6667
      },
      "group": null
    },
    {
      "course": "MTH 130",
      "name": "PRECALCULUS II",
      "subject": "M",
      "students": 7,
      "first_pass": 3,
      "passed": 3,
      "path": {
        "first": 3,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 4
      },
      "grades": {
        "C or higher": 3,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 4
      },
      "retained_if_passed": {
        "students": 3,
        "retained": 3,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 4,
        "retained": 3,
        "rate": 0.75
      },
      "group": null
    },
    {
      "course": "MATH 138",
      "name": "STATISTICS",
      "subject": "M",
      "students": 6,
      "first_pass": 6,
      "passed": 6,
      "path": {
        "first": 6,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 6,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 6,
        "retained": 3,
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
      "course": "MATH 140",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 6,
      "first_pass": 3,
      "passed": 4,
      "path": {
        "first": 3,
        "retook_passed": 1,
        "retook_not": 0,
        "no_retake": 2
      },
      "grades": {
        "C or higher": 4,
        "Below C": 1,
        "Under 1.0": 0,
        "P": 0,
        "W": 2
      },
      "retained_if_passed": {
        "students": 4,
        "retained": 3,
        "rate": 0.75
      },
      "retained_if_not_passed": {
        "students": 2,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "MATH 181",
      "name": "CALCULUS I",
      "subject": "M",
      "students": 6,
      "first_pass": 6,
      "passed": 6,
      "path": {
        "first": 6,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 6,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 6,
        "retained": 6,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTH 104",
      "name": "GENERAL EDUCATION MATHEMATICS",
      "subject": "M",
      "students": 6,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 4
      },
      "grades": {
        "C or higher": 2,
        "Below C": 1,
        "Under 1.0": 2,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 4,
        "retained": 2,
        "rate": 0.5
      },
      "group": null
    },
    {
      "course": "MTH 141",
      "name": "QUANTITATIVE LITERACY",
      "subject": "M",
      "students": 6,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 5
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 1,
        "W": 4
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 5,
        "retained": 3,
        "rate": 0.6
      },
      "group": null
    },
    {
      "course": "ENG 11103",
      "name": "COMPOSITION I",
      "subject": "E",
      "students": 5,
      "first_pass": 4,
      "passed": 4,
      "path": {
        "first": 4,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 4,
        "W": 1
      },
      "retained_if_passed": {
        "students": 4,
        "retained": 3,
        "rate": 0.75
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "MATH 1220",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 5,
      "first_pass": 5,
      "passed": 5,
      "path": {
        "first": 5,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 5,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 5,
        "retained": 4,
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
      "course": "MATH 145",
      "name": "BUSINESS CALCULUS",
      "subject": "M",
      "students": 5,
      "first_pass": 5,
      "passed": 5,
      "path": {
        "first": 5,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 5,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 5,
        "retained": 3,
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
      "course": "MATH 314",
      "name": "COLLEGE ALGEBRA MATH PATHWAY",
      "subject": "M",
      "students": 5,
      "first_pass": 5,
      "passed": 5,
      "path": {
        "first": 5,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 5,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 5,
        "retained": 5,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTH 114",
      "name": "APPLIED MATHEMATICS I",
      "subject": "M",
      "students": 5,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 3
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 2,
        "W": 2
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 3,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "MTHM 171",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 5,
      "first_pass": 4,
      "passed": 4,
      "path": {
        "first": 4,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 4,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 4,
        "retained": 3,
        "rate": 0.75
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "ENG 1113",
      "name": "ENGLISH COMPOSITION I",
      "subject": "E",
      "students": 4,
      "first_pass": 4,
      "passed": 4,
      "path": {
        "first": 4,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 4,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 4,
        "retained": 4,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "ENGL 1101",
      "name": "COLLEGE COMPOSITION",
      "subject": "E",
      "students": 4,
      "first_pass": 4,
      "passed": 4,
      "path": {
        "first": 4,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 4,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 4,
        "retained": 4,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MAT 141",
      "name": "COLLEGE MATHEMATICS",
      "subject": "M",
      "students": 4,
      "first_pass": 4,
      "passed": 4,
      "path": {
        "first": 4,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 4,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 4,
        "retained": 4,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MATH 387",
      "name": "COLLEGE ALGEBRA MATH PATHWAY",
      "subject": "M",
      "students": 4,
      "first_pass": 4,
      "passed": 4,
      "path": {
        "first": 4,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 4,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 4,
        "retained": 2,
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
      "course": "MTH 102",
      "name": "GENERAL EDUC STATISTICS",
      "subject": "M",
      "students": 4,
      "first_pass": 3,
      "passed": 3,
      "path": {
        "first": 3,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 3,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 3,
        "retained": 3,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "MTH 144",
      "name": "PRECALCULUS",
      "subject": "M",
      "students": 4,
      "first_pass": 4,
      "passed": 4,
      "path": {
        "first": 4,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 4,
        "W": 0
      },
      "retained_if_passed": {
        "students": 4,
        "retained": 3,
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
      "course": "MTH 145",
      "name": "CALCULUS & ANALYTIC GEOMETRY I",
      "subject": "M",
      "students": 4,
      "first_pass": 3,
      "passed": 3,
      "path": {
        "first": 3,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 3,
        "W": 1
      },
      "retained_if_passed": {
        "students": 3,
        "retained": 3,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "MTH 154",
      "name": "QUANTITATIVE REASONING",
      "subject": "M",
      "students": 4,
      "first_pass": 3,
      "passed": 3,
      "path": {
        "first": 3,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 3,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 3,
        "retained": 2,
        "rate": 0.6667
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "MTH 21404",
      "name": "INTRO PROBABILITY & STATISTICS",
      "subject": "M",
      "students": 4,
      "first_pass": 4,
      "passed": 4,
      "path": {
        "first": 4,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 4,
        "W": 0
      },
      "retained_if_passed": {
        "students": 4,
        "retained": 4,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTHM 181",
      "name": "\"CALCULUS I\"",
      "subject": "M",
      "students": 4,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 2
      },
      "grades": {
        "C or higher": 2,
        "Below C": 1,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 0,
        "rate": 0.0
      },
      "retained_if_not_passed": {
        "students": 2,
        "retained": 1,
        "rate": 0.5
      },
      "group": null
    },
    {
      "course": "MAT 1313",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 3,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 1,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 2,
        "Below C": 1,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "MAT 145",
      "name": "COLLEGE MATH WITH REVIEW",
      "subject": "M",
      "students": 3,
      "first_pass": 3,
      "passed": 3,
      "path": {
        "first": 3,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 3,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 3,
        "retained": 3,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MATH 1350",
      "name": "INTRO TO STAT",
      "subject": "M",
      "students": 3,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 2
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 2,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 2,
        "retained": 1,
        "rate": 0.5
      },
      "group": null
    },
    {
      "course": "MTH 122",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 3,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 2,
        "W": 1
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "MTH 134",
      "name": "CALCULUS/ BUSINESS&SOCIAL SCI",
      "subject": "M",
      "students": 3,
      "first_pass": 3,
      "passed": 3,
      "path": {
        "first": 3,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 3,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 3,
        "retained": 1,
        "rate": 0.3333
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "ENG 101A",
      "name": "FUNDAMENTALS OF ENGLISH I, ACCELERATED",
      "subject": "E",
      "students": 2,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 1,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "ENG 110",
      "name": "COMPOSITION I",
      "subject": "E",
      "students": 2,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "ENG 152",
      "name": "BUSINESS COMMUNICATION",
      "subject": "E",
      "students": 2,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 1,
        "Below C": 1,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "ENGL 100",
      "name": "COMPOSITION I",
      "subject": "E",
      "students": 2,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "ENGL 1010",
      "name": "COMPOSITION I",
      "subject": "E",
      "students": 2,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "ENGL 1113",
      "name": "FRESHMAN COMPOSITION I",
      "subject": "E",
      "students": 2,
      "first_pass": 0,
      "passed": 0,
      "path": {
        "first": 0,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 2
      },
      "grades": {
        "C or higher": 0,
        "Below C": 1,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": 2,
        "retained": 1,
        "rate": 0.5
      },
      "group": null
    },
    {
      "course": "ENGL 164",
      "name": "COLLEGE COMP II W/TECHN TOPICS",
      "subject": "E",
      "students": 2,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 2,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "ENGL 2210",
      "name": "PROFESSIONAL & TECHNICAL COMM",
      "subject": "E",
      "students": 2,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "ENGL 61",
      "name": "\"ACCELERATED WRITING REVIEW\"",
      "subject": "E",
      "students": 2,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "MAT 106",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 2,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 1,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "MAT 155",
      "name": "COLLEGE ALGEBRA/FUNCTION W REV",
      "subject": "M",
      "students": 2,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 2,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MATH 111",
      "name": "PRINCIPLES OF MATHEMATICS",
      "subject": "M",
      "students": 2,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 2,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 1,
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
      "course": "MATH 124",
      "name": "MATH-124",
      "subject": "M",
      "students": 2,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "MATH 132",
      "name": "MATHEMATICAL LITERACY",
      "subject": "M",
      "students": 2,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 2,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTH 109",
      "name": "ALGEBRA - BUSINESS/SOC SCIENCE",
      "subject": "M",
      "students": 2,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "MTH 201",
      "name": "CALCULUS II",
      "subject": "M",
      "students": 2,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 2,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 1,
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
      "course": "MTH 202",
      "name": "CALCULUS III",
      "subject": "M",
      "students": 2,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "MTH 222",
      "name": "BUSINESS STATISTICS",
      "subject": "M",
      "students": 2,
      "first_pass": 0,
      "passed": 0,
      "path": {
        "first": 0,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 2
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "MTH 225",
      "name": "BUSINESS STATISTICS",
      "subject": "M",
      "students": 2,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 2,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 1,
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
      "course": "MTH 263",
      "name": "CALCULUS I",
      "subject": "M",
      "students": 2,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 2,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTHM 155",
      "name": "\"TECHNICAL MATHEMATICS I\"",
      "subject": "M",
      "students": 2,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 2,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTHM 158",
      "name": "\"QUANTITATIVE REASONING\"",
      "subject": "M",
      "students": 2,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 2,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTHM 68",
      "name": "\"STATISTICS CO-REQUISITE\"",
      "subject": "M",
      "students": 2,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "AFED 175",
      "name": "PRE-COMPOSITION SKILLS",
      "subject": "M",
      "students": 1,
      "first_pass": 0,
      "passed": 0,
      "path": {
        "first": 0,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "ENG 1000",
      "name": "ENGLISH COMPOSITION I",
      "subject": "E",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "ENG 1001",
      "name": "ENGLISH COMPOSITION 1 PLUS",
      "subject": "E",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "ENG 130",
      "name": "BUSINESS WRITING",
      "subject": "E",
      "students": 1,
      "first_pass": 0,
      "passed": 0,
      "path": {
        "first": 0,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "ENG 153",
      "name": "TECHNICAL WRITING",
      "subject": "E",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "INRW 380",
      "name": "BASIC INTEGRATED READ & WRITE",
      "subject": "E",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "M 101",
      "name": "M 101 TECHNICAL MATH",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MAT 102",
      "name": "MATH CONCEPTS",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 1,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MAT 107",
      "name": "MATH FOR ELEM EDUC",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 1,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MAT 281",
      "name": "CALCULUS I",
      "subject": "M",
      "students": 1,
      "first_pass": 0,
      "passed": 0,
      "path": {
        "first": 0,
        "retook_passed": 0,
        "retook_not": 1,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 2,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "MATH 1010",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MATH 1030",
      "name": "INTRO TO STATISTICS",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MATH 126",
      "name": "MATH-126",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MATH 141",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MATH 143",
      "name": "PRECALCULUS I",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MATH 153",
      "name": "PRECALCULUS II",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTH 111",
      "name": "BASIC TECHNICAL MATHEMATICS",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTH 11505",
      "name": "MATH FOR EDUCATORS I",
      "subject": "M",
      "students": 1,
      "first_pass": 0,
      "passed": 0,
      "path": {
        "first": 0,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "MTH 121",
      "name": "MATH FOR ELEMENTARY TEACHING I",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 1,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTH 124",
      "name": "FINITE MATHEMATICS",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTH 1240",
      "name": "STATISTICS",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTH 1241",
      "name": "STATISTICS PLUS",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTH 221",
      "name": "MATH ELEMENTARY TEACHING II",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 1,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTH 224",
      "name": "CALC. FOR BUS. & SOC SCIENCE",
      "subject": "M",
      "students": 1,
      "first_pass": 0,
      "passed": 0,
      "path": {
        "first": 0,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    }
  ],
  "hidden_courses": 0,
  "left_out": 32,
  "pairs_considered": 1532,
  "pairs": [
    {
      "courses": [
        "ENG 101",
        "PHIL 102"
      ],
      "students": 4,
      "retained": 0,
      "rate": 0.0,
      "others_rate": 0.5221,
      "gap": -52.21,
      "affected": -2.1,
      "likely_noise": true
    },
    {
      "courses": [
        "ACC 201",
        "ENG 101"
      ],
      "students": 7,
      "retained": 2,
      "rate": 0.2857,
      "others_rate": 0.522,
      "gap": -23.62,
      "affected": -1.7,
      "likely_noise": true
    },
    {
      "courses": [
        "ACC 101",
        "ENG 101"
      ],
      "students": 3,
      "retained": 0,
      "rate": 0.0,
      "others_rate": 0.5219,
      "gap": -52.19,
      "affected": -1.6,
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
    "min_students": 1,
    "source": "PDP analysis-ready cohort and course files (synthetic sample)",
    "loaded_at": "2026-11-24T00:47:20",
    "flagged": true,
    "year_one": "2023-24",
    "retention_term": "Fall 2024",
    "retention_observed": true,
    "first_term": null,
    "compared": false,
    "min_pair_students": 1,
    "grade_scale": {
      "grades": [
        {
          "grade": "C or higher",
          "points": "2.0 and up",
          "counted": true
        },
        {
          "grade": "Below C",
          "points": "1.0 to under 2.0 (D, D+, C-)",
          "counted": false
        },
        {
          "grade": "Under 1.0",
          "points": "under 1.0 (D- or F), or the code F",
          "counted": false
        },
        {
          "grade": "P",
          "points": "the code P (pass)",
          "counted": true
        },
        {
          "grade": "W",
          "points": "the code W (withdrew)",
          "counted": false
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
      "first_pass": 281,
      "passed": 299,
      "path": {
        "first": 281,
        "retook_passed": 18,
        "retook_not": 9,
        "no_retake": 76
      },
      "grades": {
        "C or higher": 249,
        "Below C": 17,
        "Under 1.0": 65,
        "P": 50,
        "W": 31
      },
      "retained_if_passed": {
        "students": 299,
        "retained": 228,
        "rate": 0.7625
      },
      "retained_if_not_passed": {
        "students": 85,
        "retained": 22,
        "rate": 0.2588
      },
      "group": null
    },
    {
      "course": "ENGL 101",
      "name": "ENGLISH COMPOSITION I",
      "subject": "E",
      "students": 63,
      "first_pass": 45,
      "passed": 48,
      "path": {
        "first": 45,
        "retook_passed": 3,
        "retook_not": 2,
        "no_retake": 13
      },
      "grades": {
        "C or higher": 48,
        "Below C": 6,
        "Under 1.0": 6,
        "P": 0,
        "W": 8
      },
      "retained_if_passed": {
        "students": 48,
        "retained": 35,
        "rate": 0.7292
      },
      "retained_if_not_passed": {
        "students": 15,
        "retained": 3,
        "rate": 0.2
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
        "retook_passed": 2,
        "retook_not": 1,
        "no_retake": 14
      },
      "grades": {
        "C or higher": 42,
        "Below C": 0,
        "Under 1.0": 14,
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
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 8,
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
      "first_pass": 27,
      "passed": 29,
      "path": {
        "first": 27,
        "retook_passed": 2,
        "retook_not": 0,
        "no_retake": 7
      },
      "grades": {
        "C or higher": 29,
        "Below C": 1,
        "Under 1.0": 3,
        "P": 0,
        "W": 5
      },
      "retained_if_passed": {
        "students": 29,
        "retained": 4,
        "rate": 0.1379
      },
      "retained_if_not_passed": {
        "students": 7,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "MTH 165",
      "name": "ELEMENTARY STATISTICS",
      "subject": "M",
      "students": 23,
      "first_pass": 14,
      "passed": 15,
      "path": {
        "first": 14,
        "retook_passed": 1,
        "retook_not": 0,
        "no_retake": 8
      },
      "grades": {
        "C or higher": 15,
        "Below C": 2,
        "Under 1.0": 2,
        "P": 0,
        "W": 5
      },
      "retained_if_passed": {
        "students": 15,
        "retained": 13,
        "rate": 0.8667
      },
      "retained_if_not_passed": {
        "students": 8,
        "retained": 4,
        "rate": 0.5
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
        "C or higher": 22,
        "Below C": 0,
        "Under 1.0": 0,
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
      "first_pass": 15,
      "passed": 16,
      "path": {
        "first": 15,
        "retook_passed": 1,
        "retook_not": 0,
        "no_retake": 5
      },
      "grades": {
        "C or higher": 17,
        "Below C": 5,
        "Under 1.0": 2,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 16,
        "retained": 5,
        "rate": 0.3125
      },
      "retained_if_not_passed": {
        "students": 5,
        "retained": 1,
        "rate": 0.2
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
        "C or higher": 21,
        "Below C": 0,
        "Under 1.0": 0,
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
      "first_pass": 10,
      "passed": 10,
      "path": {
        "first": 10,
        "retook_passed": 0,
        "retook_not": 1,
        "no_retake": 9
      },
      "grades": {
        "C or higher": 10,
        "Below C": 1,
        "Under 1.0": 6,
        "P": 0,
        "W": 4
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
      },
      "group": null
    },
    {
      "course": "ENGL 161",
      "name": "COLLEGE COMPOSITION I",
      "subject": "E",
      "students": 18,
      "first_pass": 12,
      "passed": 14,
      "path": {
        "first": 12,
        "retook_passed": 2,
        "retook_not": 1,
        "no_retake": 3
      },
      "grades": {
        "C or higher": 14,
        "Below C": 1,
        "Under 1.0": 4,
        "P": 0,
        "W": 2
      },
      "retained_if_passed": {
        "students": 14,
        "retained": 13,
        "rate": 0.9286
      },
      "retained_if_not_passed": {
        "students": 4,
        "retained": 2,
        "rate": 0.5
      },
      "group": null
    },
    {
      "course": "ENG 102",
      "name": "FIRST-YEAR COMPOSITION",
      "subject": "E",
      "students": 17,
      "first_pass": 15,
      "passed": 15,
      "path": {
        "first": 15,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 2
      },
      "grades": {
        "C or higher": 15,
        "Below C": 1,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 15,
        "retained": 11,
        "rate": 0.7333
      },
      "retained_if_not_passed": {
        "students": 2,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "MTH 103",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 17,
      "first_pass": 9,
      "passed": 9,
      "path": {
        "first": 9,
        "retook_passed": 0,
        "retook_not": 3,
        "no_retake": 5
      },
      "grades": {
        "C or higher": 9,
        "Below C": 3,
        "Under 1.0": 2,
        "P": 0,
        "W": 6
      },
      "retained_if_passed": {
        "students": 9,
        "retained": 5,
        "rate": 0.5556
      },
      "retained_if_not_passed": {
        "students": 8,
        "retained": 8,
        "rate": 1.0
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
        "first": 7,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 7
      },
      "grades": {
        "C or higher": 7,
        "Below C": 0,
        "Under 1.0": 5,
        "P": 0,
        "W": 2
      },
      "retained_if_passed": {
        "students": 7,
        "retained": 7,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 7,
        "retained": 2,
        "rate": 0.2857
      },
      "group": null
    },
    {
      "course": "MATH 120",
      "name": "MATH-120",
      "subject": "M",
      "students": 14,
      "first_pass": 10,
      "passed": 10,
      "path": {
        "first": 10,
        "retook_passed": 0,
        "retook_not": 1,
        "no_retake": 3
      },
      "grades": {
        "C or higher": 10,
        "Below C": 3,
        "Under 1.0": 2,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 10,
        "retained": 8,
        "rate": 0.8
      },
      "retained_if_not_passed": {
        "students": 4,
        "retained": 3,
        "rate": 0.75
      },
      "group": null
    },
    {
      "course": "MTH 101",
      "name": "QUANTITATIVE LITERACY",
      "subject": "M",
      "students": 14,
      "first_pass": 11,
      "passed": 11,
      "path": {
        "first": 11,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 3
      },
      "grades": {
        "C or higher": 11,
        "Below C": 1,
        "Under 1.0": 2,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 11,
        "retained": 6,
        "rate": 0.5455
      },
      "retained_if_not_passed": {
        "students": 3,
        "retained": 2,
        "rate": 0.6667
      },
      "group": null
    },
    {
      "course": "MATH 202",
      "name": "INTRODUCTION TO STATISTICS",
      "subject": "M",
      "students": 13,
      "first_pass": 6,
      "passed": 6,
      "path": {
        "first": 6,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 7
      },
      "grades": {
        "C or higher": 6,
        "Below C": 2,
        "Under 1.0": 2,
        "P": 0,
        "W": 3
      },
      "retained_if_passed": {
        "students": 6,
        "retained": 6,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 7,
        "retained": 3,
        "rate": 0.4286
      },
      "group": null
    },
    {
      "course": "MTH 107",
      "name": "BASIC STATISTICS",
      "subject": "M",
      "students": 13,
      "first_pass": 9,
      "passed": 9,
      "path": {
        "first": 9,
        "retook_passed": 0,
        "retook_not": 1,
        "no_retake": 3
      },
      "grades": {
        "C or higher": 9,
        "Below C": 2,
        "Under 1.0": 2,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 9,
        "retained": 7,
        "rate": 0.7778
      },
      "retained_if_not_passed": {
        "students": 4,
        "retained": 3,
        "rate": 0.75
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
        "first": 9,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 4
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 3,
        "P": 9,
        "W": 1
      },
      "retained_if_passed": {
        "students": 9,
        "retained": 6,
        "rate": 0.6667
      },
      "retained_if_not_passed": {
        "students": 4,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "MTH 140",
      "name": "PRECALCULUS",
      "subject": "M",
      "students": 12,
      "first_pass": 8,
      "passed": 10,
      "path": {
        "first": 8,
        "retook_passed": 2,
        "retook_not": 0,
        "no_retake": 2
      },
      "grades": {
        "C or higher": 8,
        "Below C": 1,
        "Under 1.0": 1,
        "P": 2,
        "W": 2
      },
      "retained_if_passed": {
        "students": 10,
        "retained": 8,
        "rate": 0.8
      },
      "retained_if_not_passed": {
        "students": 2,
        "retained": 1,
        "rate": 0.5
      },
      "group": null
    },
    {
      "course": "MTH 161",
      "name": "PRECALCULUS I",
      "subject": "M",
      "students": 12,
      "first_pass": 8,
      "passed": 8,
      "path": {
        "first": 8,
        "retook_passed": 0,
        "retook_not": 1,
        "no_retake": 3
      },
      "grades": {
        "C or higher": 8,
        "Below C": 1,
        "Under 1.0": 0,
        "P": 0,
        "W": 4
      },
      "retained_if_passed": {
        "students": 8,
        "retained": 0,
        "rate": 0.0
      },
      "retained_if_not_passed": {
        "students": 4,
        "retained": 1,
        "rate": 0.25
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
        "first": 9,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 2
      },
      "grades": {
        "C or higher": 9,
        "Below C": 0,
        "Under 1.0": 3,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 9,
        "retained": 5,
        "rate": 0.5556
      },
      "retained_if_not_passed": {
        "students": 2,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "MATH 116",
      "name": "MATH-116",
      "subject": "M",
      "students": 11,
      "first_pass": 4,
      "passed": 4,
      "path": {
        "first": 4,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 7
      },
      "grades": {
        "C or higher": 4,
        "Below C": 4,
        "Under 1.0": 3,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 4,
        "retained": 3,
        "rate": 0.75
      },
      "retained_if_not_passed": {
        "students": 7,
        "retained": 2,
        "rate": 0.2857
      },
      "group": null
    },
    {
      "course": "MATH 130",
      "name": "INTRODUCTION TO STATISTICS",
      "subject": "M",
      "students": 11,
      "first_pass": 7,
      "passed": 8,
      "path": {
        "first": 7,
        "retook_passed": 1,
        "retook_not": 1,
        "no_retake": 2
      },
      "grades": {
        "C or higher": 8,
        "Below C": 3,
        "Under 1.0": 1,
        "P": 0,
        "W": 2
      },
      "retained_if_passed": {
        "students": 8,
        "retained": 4,
        "rate": 0.5
      },
      "retained_if_not_passed": {
        "students": 3,
        "retained": 1,
        "rate": 0.3333
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
        "C or higher": 10,
        "Below C": 0,
        "Under 1.0": 0,
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
      "first_pass": 5,
      "passed": 5,
      "path": {
        "first": 5,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 5
      },
      "grades": {
        "C or higher": 5,
        "Below C": 2,
        "Under 1.0": 3,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 5,
        "retained": 4,
        "rate": 0.8
      },
      "retained_if_not_passed": {
        "students": 5,
        "retained": 0,
        "rate": 0.0
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
        "first": 7,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 3
      },
      "grades": {
        "C or higher": 7,
        "Below C": 0,
        "Under 1.0": 3,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 7,
        "retained": 6,
        "rate": 0.8571
      },
      "retained_if_not_passed": {
        "students": 3,
        "retained": 1,
        "rate": 0.3333
      },
      "group": null
    },
    {
      "course": "MATH 150",
      "name": "PRE-CALCULUS",
      "subject": "M",
      "students": 9,
      "first_pass": 9,
      "passed": 9,
      "path": {
        "first": 9,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 9,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 9,
        "retained": 1,
        "rate": 0.1111
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MATH 1130",
      "name": "SURVEY OF MATHEMATICS",
      "subject": "M",
      "students": 8,
      "first_pass": 4,
      "passed": 5,
      "path": {
        "first": 4,
        "retook_passed": 1,
        "retook_not": 0,
        "no_retake": 3
      },
      "grades": {
        "C or higher": 5,
        "Below C": 1,
        "Under 1.0": 1,
        "P": 0,
        "W": 2
      },
      "retained_if_passed": {
        "students": 5,
        "retained": 3,
        "rate": 0.6
      },
      "retained_if_not_passed": {
        "students": 3,
        "retained": 2,
        "rate": 0.6667
      },
      "group": null
    },
    {
      "course": "MTH 112",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 8,
      "first_pass": 7,
      "passed": 7,
      "path": {
        "first": 7,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 7,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 7,
        "retained": 5,
        "rate": 0.7143
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "MTH 142",
      "name": "GENERAL EDUCATION STATISTICS",
      "subject": "M",
      "students": 8,
      "first_pass": 8,
      "passed": 8,
      "path": {
        "first": 8,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 8,
        "W": 0
      },
      "retained_if_passed": {
        "students": 8,
        "retained": 8,
        "rate": 1.0
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
      "students": 8,
      "first_pass": 5,
      "passed": 5,
      "path": {
        "first": 5,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 3
      },
      "grades": {
        "C or higher": 5,
        "Below C": 2,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 5,
        "retained": 3,
        "rate": 0.6
      },
      "retained_if_not_passed": {
        "students": 3,
        "retained": 3,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "MTHM 168",
      "name": "STATISTICS",
      "subject": "M",
      "students": 8,
      "first_pass": 5,
      "passed": 5,
      "path": {
        "first": 5,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 3
      },
      "grades": {
        "C or higher": 5,
        "Below C": 1,
        "Under 1.0": 1,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 5,
        "retained": 5,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 3,
        "retained": 2,
        "rate": 0.6667
      },
      "group": null
    },
    {
      "course": "ENGL 162",
      "name": "\"COLLEGE COMPOSITION II\"",
      "subject": "E",
      "students": 7,
      "first_pass": 5,
      "passed": 5,
      "path": {
        "first": 5,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 2
      },
      "grades": {
        "C or higher": 5,
        "Below C": 1,
        "Under 1.0": 0,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 5,
        "retained": 4,
        "rate": 0.8
      },
      "retained_if_not_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "MAT 172",
      "name": "MATH FOR TCHRS I: NUM & OPR",
      "subject": "M",
      "students": 7,
      "first_pass": 4,
      "passed": 4,
      "path": {
        "first": 4,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 3
      },
      "grades": {
        "C or higher": 4,
        "Below C": 0,
        "Under 1.0": 2,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 4,
        "retained": 1,
        "rate": 0.25
      },
      "retained_if_not_passed": {
        "students": 3,
        "retained": 2,
        "rate": 0.6667
      },
      "group": null
    },
    {
      "course": "MTH 130",
      "name": "PRECALCULUS II",
      "subject": "M",
      "students": 7,
      "first_pass": 3,
      "passed": 3,
      "path": {
        "first": 3,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 4
      },
      "grades": {
        "C or higher": 3,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 4
      },
      "retained_if_passed": {
        "students": 3,
        "retained": 3,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 4,
        "retained": 3,
        "rate": 0.75
      },
      "group": null
    },
    {
      "course": "MATH 138",
      "name": "STATISTICS",
      "subject": "M",
      "students": 6,
      "first_pass": 6,
      "passed": 6,
      "path": {
        "first": 6,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 6,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 6,
        "retained": 2,
        "rate": 0.3333
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
      "students": 6,
      "first_pass": 3,
      "passed": 4,
      "path": {
        "first": 3,
        "retook_passed": 1,
        "retook_not": 0,
        "no_retake": 2
      },
      "grades": {
        "C or higher": 4,
        "Below C": 1,
        "Under 1.0": 0,
        "P": 0,
        "W": 2
      },
      "retained_if_passed": {
        "students": 4,
        "retained": 2,
        "rate": 0.5
      },
      "retained_if_not_passed": {
        "students": 2,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "MATH 181",
      "name": "CALCULUS I",
      "subject": "M",
      "students": 6,
      "first_pass": 6,
      "passed": 6,
      "path": {
        "first": 6,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 6,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 6,
        "retained": 6,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTH 104",
      "name": "GENERAL EDUCATION MATHEMATICS",
      "subject": "M",
      "students": 6,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 4
      },
      "grades": {
        "C or higher": 2,
        "Below C": 1,
        "Under 1.0": 2,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 4,
        "retained": 2,
        "rate": 0.5
      },
      "group": null
    },
    {
      "course": "MTH 141",
      "name": "QUANTITATIVE LITERACY",
      "subject": "M",
      "students": 6,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 5
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 1,
        "W": 4
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 5,
        "retained": 3,
        "rate": 0.6
      },
      "group": null
    },
    {
      "course": "ENG 11103",
      "name": "COMPOSITION I",
      "subject": "E",
      "students": 5,
      "first_pass": 4,
      "passed": 4,
      "path": {
        "first": 4,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 4,
        "W": 1
      },
      "retained_if_passed": {
        "students": 4,
        "retained": 3,
        "rate": 0.75
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "MATH 1220",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 5,
      "first_pass": 5,
      "passed": 5,
      "path": {
        "first": 5,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 5,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 5,
        "retained": 1,
        "rate": 0.2
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MATH 145",
      "name": "BUSINESS CALCULUS",
      "subject": "M",
      "students": 5,
      "first_pass": 5,
      "passed": 5,
      "path": {
        "first": 5,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 5,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 5,
        "retained": 3,
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
      "course": "MATH 314",
      "name": "COLLEGE ALGEBRA MATH PATHWAY",
      "subject": "M",
      "students": 5,
      "first_pass": 5,
      "passed": 5,
      "path": {
        "first": 5,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 5,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 5,
        "retained": 4,
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
      "course": "MTH 114",
      "name": "APPLIED MATHEMATICS I",
      "subject": "M",
      "students": 5,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 3
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 2,
        "W": 2
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 3,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "MTHM 171",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 5,
      "first_pass": 4,
      "passed": 4,
      "path": {
        "first": 4,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 4,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 4,
        "retained": 2,
        "rate": 0.5
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "ENG 1113",
      "name": "ENGLISH COMPOSITION I",
      "subject": "E",
      "students": 4,
      "first_pass": 4,
      "passed": 4,
      "path": {
        "first": 4,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 4,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 4,
        "retained": 4,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "ENGL 1101",
      "name": "COLLEGE COMPOSITION",
      "subject": "E",
      "students": 4,
      "first_pass": 4,
      "passed": 4,
      "path": {
        "first": 4,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 4,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 4,
        "retained": 4,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MAT 141",
      "name": "COLLEGE MATHEMATICS",
      "subject": "M",
      "students": 4,
      "first_pass": 4,
      "passed": 4,
      "path": {
        "first": 4,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 4,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 4,
        "retained": 2,
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
      "course": "MATH 387",
      "name": "COLLEGE ALGEBRA MATH PATHWAY",
      "subject": "M",
      "students": 4,
      "first_pass": 4,
      "passed": 4,
      "path": {
        "first": 4,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 4,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 4,
        "retained": 1,
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
      "course": "MTH 102",
      "name": "GENERAL EDUC STATISTICS",
      "subject": "M",
      "students": 4,
      "first_pass": 3,
      "passed": 3,
      "path": {
        "first": 3,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 3,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 3,
        "retained": 2,
        "rate": 0.6667
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "MTH 144",
      "name": "PRECALCULUS",
      "subject": "M",
      "students": 4,
      "first_pass": 4,
      "passed": 4,
      "path": {
        "first": 4,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 4,
        "W": 0
      },
      "retained_if_passed": {
        "students": 4,
        "retained": 3,
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
      "course": "MTH 145",
      "name": "CALCULUS & ANALYTIC GEOMETRY I",
      "subject": "M",
      "students": 4,
      "first_pass": 3,
      "passed": 3,
      "path": {
        "first": 3,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 3,
        "W": 1
      },
      "retained_if_passed": {
        "students": 3,
        "retained": 3,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "MTH 154",
      "name": "QUANTITATIVE REASONING",
      "subject": "M",
      "students": 4,
      "first_pass": 3,
      "passed": 3,
      "path": {
        "first": 3,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 3,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 3,
        "retained": 0,
        "rate": 0.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "MTH 21404",
      "name": "INTRO PROBABILITY & STATISTICS",
      "subject": "M",
      "students": 4,
      "first_pass": 4,
      "passed": 4,
      "path": {
        "first": 4,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 4,
        "W": 0
      },
      "retained_if_passed": {
        "students": 4,
        "retained": 4,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTHM 181",
      "name": "\"CALCULUS I\"",
      "subject": "M",
      "students": 4,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 2
      },
      "grades": {
        "C or higher": 2,
        "Below C": 1,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 0,
        "rate": 0.0
      },
      "retained_if_not_passed": {
        "students": 2,
        "retained": 1,
        "rate": 0.5
      },
      "group": null
    },
    {
      "course": "MAT 1313",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 3,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 1,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 2,
        "Below C": 1,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 1,
        "rate": 0.5
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "MAT 145",
      "name": "COLLEGE MATH WITH REVIEW",
      "subject": "M",
      "students": 3,
      "first_pass": 3,
      "passed": 3,
      "path": {
        "first": 3,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 3,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 3,
        "retained": 3,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MATH 1350",
      "name": "INTRO TO STAT",
      "subject": "M",
      "students": 3,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 2
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 2,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "retained_if_not_passed": {
        "students": 2,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "MTH 122",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 3,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 2,
        "W": 1
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "MTH 134",
      "name": "CALCULUS/ BUSINESS&SOCIAL SCI",
      "subject": "M",
      "students": 3,
      "first_pass": 3,
      "passed": 3,
      "path": {
        "first": 3,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 3,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 3,
        "retained": 1,
        "rate": 0.3333
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "ENG 101A",
      "name": "FUNDAMENTALS OF ENGLISH I, ACCELERATED",
      "subject": "E",
      "students": 2,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 1,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "ENG 110",
      "name": "COMPOSITION I",
      "subject": "E",
      "students": 2,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "ENG 152",
      "name": "BUSINESS COMMUNICATION",
      "subject": "E",
      "students": 2,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 1,
        "Below C": 1,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "ENGL 100",
      "name": "COMPOSITION I",
      "subject": "E",
      "students": 2,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "ENGL 1010",
      "name": "COMPOSITION I",
      "subject": "E",
      "students": 2,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "ENGL 1113",
      "name": "FRESHMAN COMPOSITION I",
      "subject": "E",
      "students": 2,
      "first_pass": 0,
      "passed": 0,
      "path": {
        "first": 0,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 2
      },
      "grades": {
        "C or higher": 0,
        "Below C": 1,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "ENGL 164",
      "name": "COLLEGE COMP II W/TECHN TOPICS",
      "subject": "E",
      "students": 2,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 2,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "ENGL 2210",
      "name": "PROFESSIONAL & TECHNICAL COMM",
      "subject": "E",
      "students": 2,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "ENGL 61",
      "name": "\"ACCELERATED WRITING REVIEW\"",
      "subject": "E",
      "students": 2,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "MAT 106",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 2,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 1,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "MAT 155",
      "name": "COLLEGE ALGEBRA/FUNCTION W REV",
      "subject": "M",
      "students": 2,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 2,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MATH 111",
      "name": "PRINCIPLES OF MATHEMATICS",
      "subject": "M",
      "students": 2,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 2,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 1,
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
      "course": "MATH 124",
      "name": "MATH-124",
      "subject": "M",
      "students": 2,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "MATH 132",
      "name": "MATHEMATICAL LITERACY",
      "subject": "M",
      "students": 2,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 2,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTH 109",
      "name": "ALGEBRA - BUSINESS/SOC SCIENCE",
      "subject": "M",
      "students": 2,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "MTH 201",
      "name": "CALCULUS II",
      "subject": "M",
      "students": 2,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 2,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 1,
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
      "course": "MTH 202",
      "name": "CALCULUS III",
      "subject": "M",
      "students": 2,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "MTH 222",
      "name": "BUSINESS STATISTICS",
      "subject": "M",
      "students": 2,
      "first_pass": 0,
      "passed": 0,
      "path": {
        "first": 0,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 2
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "MTH 225",
      "name": "BUSINESS STATISTICS",
      "subject": "M",
      "students": 2,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 2,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 1,
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
      "course": "MTH 263",
      "name": "CALCULUS I",
      "subject": "M",
      "students": 2,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 2,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 0,
        "rate": 0.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTHM 155",
      "name": "\"TECHNICAL MATHEMATICS I\"",
      "subject": "M",
      "students": 2,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 2,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTHM 158",
      "name": "\"QUANTITATIVE REASONING\"",
      "subject": "M",
      "students": 2,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 2,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 1,
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
      "course": "MTHM 68",
      "name": "\"STATISTICS CO-REQUISITE\"",
      "subject": "M",
      "students": 2,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "AFED 175",
      "name": "PRE-COMPOSITION SKILLS",
      "subject": "M",
      "students": 1,
      "first_pass": 0,
      "passed": 0,
      "path": {
        "first": 0,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "ENG 1000",
      "name": "ENGLISH COMPOSITION I",
      "subject": "E",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "ENG 1001",
      "name": "ENGLISH COMPOSITION 1 PLUS",
      "subject": "E",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "ENG 130",
      "name": "BUSINESS WRITING",
      "subject": "E",
      "students": 1,
      "first_pass": 0,
      "passed": 0,
      "path": {
        "first": 0,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "ENG 153",
      "name": "TECHNICAL WRITING",
      "subject": "E",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "INRW 380",
      "name": "BASIC INTEGRATED READ & WRITE",
      "subject": "E",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "M 101",
      "name": "M 101 TECHNICAL MATH",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MAT 102",
      "name": "MATH CONCEPTS",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 1,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MAT 107",
      "name": "MATH FOR ELEM EDUC",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 1,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MAT 281",
      "name": "CALCULUS I",
      "subject": "M",
      "students": 1,
      "first_pass": 0,
      "passed": 0,
      "path": {
        "first": 0,
        "retook_passed": 0,
        "retook_not": 1,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 2,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "MATH 1010",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MATH 1030",
      "name": "INTRO TO STATISTICS",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MATH 126",
      "name": "MATH-126",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MATH 141",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MATH 143",
      "name": "PRECALCULUS I",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MATH 153",
      "name": "PRECALCULUS II",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTH 111",
      "name": "BASIC TECHNICAL MATHEMATICS",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTH 11505",
      "name": "MATH FOR EDUCATORS I",
      "subject": "M",
      "students": 1,
      "first_pass": 0,
      "passed": 0,
      "path": {
        "first": 0,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "MTH 121",
      "name": "MATH FOR ELEMENTARY TEACHING I",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 1,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTH 124",
      "name": "FINITE MATHEMATICS",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTH 1240",
      "name": "STATISTICS",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTH 1241",
      "name": "STATISTICS PLUS",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTH 221",
      "name": "MATH ELEMENTARY TEACHING II",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 1,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTH 224",
      "name": "CALC. FOR BUS. & SOC SCIENCE",
      "subject": "M",
      "students": 1,
      "first_pass": 0,
      "passed": 0,
      "path": {
        "first": 0,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    }
  ],
  "hidden_courses": 0,
  "left_out": 32,
  "pairs_considered": 1532,
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
      "likely_noise": true
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
    },
    {
      "courses": [
        "CCDM 114",
        "ENGL 1110"
      ],
      "students": 6,
      "retained": 0,
      "rate": 0.0,
      "others_rate": 0.4172,
      "gap": -41.72,
      "affected": -2.5,
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
    "min_students": 1,
    "source": "PDP analysis-ready cohort and course files (synthetic sample)",
    "loaded_at": "2026-11-24T00:47:20",
    "flagged": true,
    "year_one": "2023-24",
    "retention_term": "next academic year",
    "retention_observed": true,
    "first_term": null,
    "compared": true,
    "min_pair_students": 1,
    "grade_scale": {
      "grades": [
        {
          "grade": "C or higher",
          "points": "2.0 and up",
          "counted": true
        },
        {
          "grade": "Below C",
          "points": "1.0 to under 2.0 (D, D+, C-)",
          "counted": false
        },
        {
          "grade": "Under 1.0",
          "points": "under 1.0 (D- or F), or the code F",
          "counted": false
        },
        {
          "grade": "P",
          "points": "the code P (pass)",
          "counted": true
        },
        {
          "grade": "W",
          "points": "the code W (withdrew)",
          "counted": false
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
      "first_pass": 141,
      "passed": 148,
      "path": {
        "first": 141,
        "retook_passed": 7,
        "retook_not": 7,
        "no_retake": 44
      },
      "grades": {
        "C or higher": 129,
        "Below C": 7,
        "Under 1.0": 39,
        "P": 19,
        "W": 20
      },
      "retained_if_passed": {
        "students": 148,
        "retained": 118,
        "rate": 0.7973
      },
      "retained_if_not_passed": {
        "students": 51,
        "retained": 14,
        "rate": 0.2745
      },
      "group": {
        "status": "ok",
        "rate": 0.7085,
        "others_rate": 0.7568,
        "gap": -4.82,
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
        "retook_passed": 2,
        "retook_not": 0,
        "no_retake": 8
      },
      "grades": {
        "C or higher": 26,
        "Below C": 0,
        "Under 1.0": 8,
        "P": 0,
        "W": 2
      },
      "retained_if_passed": {
        "students": 26,
        "retained": 18,
        "rate": 0.6923
      },
      "retained_if_not_passed": {
        "students": 8,
        "retained": 2,
        "rate": 0.25
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
      "first_pass": 21,
      "passed": 23,
      "path": {
        "first": 21,
        "retook_passed": 2,
        "retook_not": 0,
        "no_retake": 8
      },
      "grades": {
        "C or higher": 23,
        "Below C": 3,
        "Under 1.0": 1,
        "P": 0,
        "W": 6
      },
      "retained_if_passed": {
        "students": 23,
        "retained": 18,
        "rate": 0.7826
      },
      "retained_if_not_passed": {
        "students": 8,
        "retained": 3,
        "rate": 0.375
      },
      "group": {
        "status": "ok",
        "rate": 0.6774,
        "others_rate": 0.75,
        "gap": -7.26,
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
        "no_retake": 9
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 6,
        "P": 14,
        "W": 3
      },
      "retained_if_passed": {
        "students": 14,
        "retained": 13,
        "rate": 0.9286
      },
      "retained_if_not_passed": {
        "students": 9,
        "retained": 4,
        "rate": 0.4444
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
      "first_pass": 13,
      "passed": 14,
      "path": {
        "first": 13,
        "retook_passed": 1,
        "retook_not": 0,
        "no_retake": 5
      },
      "grades": {
        "C or higher": 15,
        "Below C": 5,
        "Under 1.0": 2,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 14,
        "retained": 10,
        "rate": 0.7143
      },
      "retained_if_not_passed": {
        "students": 5,
        "retained": 3,
        "rate": 0.6
      },
      "group": {
        "status": "ok",
        "rate": 0.6842,
        "others_rate": 1.0,
        "gap": -31.58,
        "likely_noise": true
      }
    },
    {
      "course": "ENG 111",
      "name": "COLLEGE COMPOSITION I",
      "subject": "E",
      "students": 16,
      "first_pass": 10,
      "passed": 10,
      "path": {
        "first": 10,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 6
      },
      "grades": {
        "C or higher": 10,
        "Below C": 1,
        "Under 1.0": 1,
        "P": 0,
        "W": 4
      },
      "retained_if_passed": {
        "students": 10,
        "retained": 8,
        "rate": 0.8
      },
      "retained_if_not_passed": {
        "students": 6,
        "retained": 2,
        "rate": 0.3333
      },
      "group": {
        "status": "ok",
        "rate": 0.625,
        "others_rate": 0.85,
        "gap": -22.5,
        "likely_noise": true
      }
    },
    {
      "course": "ENG 102",
      "name": "FIRST-YEAR COMPOSITION",
      "subject": "E",
      "students": 11,
      "first_pass": 10,
      "passed": 10,
      "path": {
        "first": 10,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 10,
        "Below C": 1,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 10,
        "retained": 7,
        "rate": 0.7
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": {
        "status": "ok",
        "rate": 0.9091,
        "others_rate": 0.8333,
        "gap": 7.58,
        "likely_noise": true
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
        "C or higher": 10,
        "Below C": 0,
        "Under 1.0": 0,
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
    },
    {
      "course": "ENGL 161",
      "name": "COLLEGE COMPOSITION I",
      "subject": "E",
      "students": 9,
      "first_pass": 6,
      "passed": 7,
      "path": {
        "first": 6,
        "retook_passed": 1,
        "retook_not": 1,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 7,
        "Below C": 0,
        "Under 1.0": 3,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 7,
        "retained": 7,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 2,
        "retained": 1,
        "rate": 0.5
      },
      "group": {
        "status": "ok",
        "rate": 0.6667,
        "others_rate": 0.6667,
        "gap": 0.0,
        "likely_noise": true
      }
    },
    {
      "course": "MATH 120",
      "name": "MATH-120",
      "subject": "M",
      "students": 9,
      "first_pass": 6,
      "passed": 6,
      "path": {
        "first": 6,
        "retook_passed": 0,
        "retook_not": 1,
        "no_retake": 2
      },
      "grades": {
        "C or higher": 6,
        "Below C": 2,
        "Under 1.0": 2,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 6,
        "retained": 5,
        "rate": 0.8333
      },
      "retained_if_not_passed": {
        "students": 3,
        "retained": 2,
        "rate": 0.6667
      },
      "group": {
        "status": "ok",
        "rate": 0.6667,
        "others_rate": 0.8,
        "gap": -13.33,
        "likely_noise": true
      }
    },
    {
      "course": "MTH 165",
      "name": "ELEMENTARY STATISTICS",
      "subject": "M",
      "students": 9,
      "first_pass": 5,
      "passed": 5,
      "path": {
        "first": 5,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 4
      },
      "grades": {
        "C or higher": 5,
        "Below C": 1,
        "Under 1.0": 0,
        "P": 0,
        "W": 3
      },
      "retained_if_passed": {
        "students": 5,
        "retained": 5,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 4,
        "retained": 3,
        "rate": 0.75
      },
      "group": {
        "status": "ok",
        "rate": 0.5556,
        "others_rate": 0.6429,
        "gap": -8.73,
        "likely_noise": true
      }
    },
    {
      "course": "INRW 385",
      "name": "INTEGRATED READING AND WRITING",
      "subject": "E",
      "students": 8,
      "first_pass": 7,
      "passed": 7,
      "path": {
        "first": 7,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 7,
        "Below C": 0,
        "Under 1.0": 2,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 7,
        "retained": 5,
        "rate": 0.7143
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "group": {
        "status": "ok",
        "rate": 0.875,
        "others_rate": 0.6667,
        "gap": 20.83,
        "likely_noise": true
      }
    },
    {
      "course": "MAT 162",
      "name": "STATISTICAL REASONING",
      "subject": "M",
      "students": 8,
      "first_pass": 4,
      "passed": 4,
      "path": {
        "first": 4,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 4
      },
      "grades": {
        "C or higher": 4,
        "Below C": 0,
        "Under 1.0": 3,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 4,
        "retained": 2,
        "rate": 0.5
      },
      "retained_if_not_passed": {
        "students": 4,
        "retained": 2,
        "rate": 0.5
      },
      "group": {
        "status": "ok",
        "rate": 0.5,
        "others_rate": 0.5,
        "gap": 0.0,
        "likely_noise": true
      }
    },
    {
      "course": "MATH 202",
      "name": "INTRODUCTION TO STATISTICS",
      "subject": "M",
      "students": 8,
      "first_pass": 3,
      "passed": 3,
      "path": {
        "first": 3,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 5
      },
      "grades": {
        "C or higher": 3,
        "Below C": 1,
        "Under 1.0": 2,
        "P": 0,
        "W": 2
      },
      "retained_if_passed": {
        "students": 3,
        "retained": 3,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 5,
        "retained": 4,
        "rate": 0.8
      },
      "group": {
        "status": "ok",
        "rate": 0.375,
        "others_rate": 0.6,
        "gap": -22.5,
        "likely_noise": true
      }
    },
    {
      "course": "MTH 107",
      "name": "BASIC STATISTICS",
      "subject": "M",
      "students": 8,
      "first_pass": 6,
      "passed": 6,
      "path": {
        "first": 6,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 2
      },
      "grades": {
        "C or higher": 6,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 6,
        "retained": 6,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
      },
      "group": {
        "status": "ok",
        "rate": 0.75,
        "others_rate": 0.6,
        "gap": 15.0,
        "likely_noise": true
      }
    },
    {
      "course": "ENGL 121",
      "name": "COLLEGE COMPOSITION",
      "subject": "E",
      "students": 6,
      "first_pass": 6,
      "passed": 6,
      "path": {
        "first": 6,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 6,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 6,
        "retained": 5,
        "rate": 0.8333
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
    },
    {
      "course": "MAT 151",
      "name": "COLLEGE ALGEBRA/FUNCTIONS",
      "subject": "M",
      "students": 6,
      "first_pass": 6,
      "passed": 6,
      "path": {
        "first": 6,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 6,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 6,
        "retained": 3,
        "rate": 0.5
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
    },
    {
      "course": "MATH 103",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 6,
      "first_pass": 4,
      "passed": 4,
      "path": {
        "first": 4,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 2
      },
      "grades": {
        "C or higher": 4,
        "Below C": 1,
        "Under 1.0": 0,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 4,
        "retained": 3,
        "rate": 0.75
      },
      "retained_if_not_passed": {
        "students": 2,
        "retained": 1,
        "rate": 0.5
      },
      "group": {
        "status": "ok",
        "rate": 0.6667,
        "others_rate": 0.4286,
        "gap": 23.81,
        "likely_noise": true
      }
    },
    {
      "course": "MATH 1130",
      "name": "SURVEY OF MATHEMATICS",
      "subject": "M",
      "students": 6,
      "first_pass": 3,
      "passed": 3,
      "path": {
        "first": 3,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 3
      },
      "grades": {
        "C or higher": 3,
        "Below C": 1,
        "Under 1.0": 1,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 3,
        "retained": 2,
        "rate": 0.6667
      },
      "retained_if_not_passed": {
        "students": 3,
        "retained": 2,
        "rate": 0.6667
      },
      "group": {
        "status": "ok",
        "rate": 0.5,
        "others_rate": 0.5,
        "gap": 0.0,
        "likely_noise": true
      }
    },
    {
      "course": "MATH 116",
      "name": "MATH-116",
      "subject": "M",
      "students": 6,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 5
      },
      "grades": {
        "C or higher": 1,
        "Below C": 3,
        "Under 1.0": 2,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "retained_if_not_passed": {
        "students": 5,
        "retained": 2,
        "rate": 0.4
      },
      "group": {
        "status": "ok",
        "rate": 0.1667,
        "others_rate": 0.6,
        "gap": -43.33,
        "likely_noise": true
      }
    },
    {
      "course": "MATH 130",
      "name": "INTRODUCTION TO STATISTICS",
      "subject": "M",
      "students": 6,
      "first_pass": 4,
      "passed": 5,
      "path": {
        "first": 4,
        "retook_passed": 1,
        "retook_not": 1,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 5,
        "Below C": 3,
        "Under 1.0": 0,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 5,
        "retained": 3,
        "rate": 0.6
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "group": {
        "status": "ok",
        "rate": 0.6667,
        "others_rate": 0.6,
        "gap": 6.67,
        "likely_noise": true
      }
    },
    {
      "course": "MAT 172",
      "name": "MATH FOR TCHRS I: NUM & OPR",
      "subject": "M",
      "students": 5,
      "first_pass": 3,
      "passed": 3,
      "path": {
        "first": 3,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 2
      },
      "grades": {
        "C or higher": 3,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 3,
        "retained": 2,
        "rate": 0.6667
      },
      "retained_if_not_passed": {
        "students": 2,
        "retained": 1,
        "rate": 0.5
      },
      "group": {
        "status": "ok",
        "rate": 0.6,
        "others_rate": 0.5,
        "gap": 10.0,
        "likely_noise": true
      }
    },
    {
      "course": "MTH 103",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 5,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 1,
        "no_retake": 2
      },
      "grades": {
        "C or higher": 2,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 0,
        "W": 3
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 3,
        "retained": 3,
        "rate": 1.0
      },
      "group": {
        "status": "ok",
        "rate": 0.4,
        "others_rate": 0.5833,
        "gap": -18.33,
        "likely_noise": true
      }
    },
    {
      "course": "MTH 104",
      "name": "GENERAL EDUCATION MATHEMATICS",
      "subject": "M",
      "students": 5,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 4
      },
      "grades": {
        "C or higher": 1,
        "Below C": 1,
        "Under 1.0": 2,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 4,
        "retained": 2,
        "rate": 0.5
      },
      "group": {
        "status": "ok",
        "rate": 0.2,
        "others_rate": 1.0,
        "gap": -80.0,
        "likely_noise": true
      }
    },
    {
      "course": "MTH 152",
      "name": "STATISTICS (MA)",
      "subject": "M",
      "students": 5,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 3
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 3,
        "P": 2,
        "W": 0
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 3,
        "retained": 1,
        "rate": 0.3333
      },
      "group": {
        "status": "ok",
        "rate": 0.4,
        "others_rate": 0.875,
        "gap": -47.5,
        "likely_noise": true
      }
    },
    {
      "course": "MTH 161",
      "name": "PRECALCULUS I",
      "subject": "M",
      "students": 5,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 1,
        "no_retake": 2
      },
      "grades": {
        "C or higher": 2,
        "Below C": 1,
        "Under 1.0": 0,
        "P": 0,
        "W": 3
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 3,
        "retained": 1,
        "rate": 0.3333
      },
      "group": {
        "status": "ok",
        "rate": 0.4,
        "others_rate": 0.8571,
        "gap": -45.71,
        "likely_noise": true
      }
    },
    {
      "course": "MAT 141",
      "name": "COLLEGE MATHEMATICS",
      "subject": "M",
      "students": 4,
      "first_pass": 4,
      "passed": 4,
      "path": {
        "first": 4,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 4,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 4,
        "retained": 4,
        "rate": 1.0
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
      "course": "MATH 1220",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 4,
      "first_pass": 4,
      "passed": 4,
      "path": {
        "first": 4,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 4,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 4,
        "retained": 3,
        "rate": 0.75
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
    },
    {
      "course": "MATH 181",
      "name": "CALCULUS I",
      "subject": "M",
      "students": 4,
      "first_pass": 4,
      "passed": 4,
      "path": {
        "first": 4,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 4,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 4,
        "retained": 4,
        "rate": 1.0
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
    },
    {
      "course": "MATH 314",
      "name": "COLLEGE ALGEBRA MATH PATHWAY",
      "subject": "M",
      "students": 4,
      "first_pass": 4,
      "passed": 4,
      "path": {
        "first": 4,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 4,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 4,
        "retained": 4,
        "rate": 1.0
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
    },
    {
      "course": "MTH 101",
      "name": "QUANTITATIVE LITERACY",
      "subject": "M",
      "students": 4,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 2
      },
      "grades": {
        "C or higher": 2,
        "Below C": 0,
        "Under 1.0": 2,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 1,
        "rate": 0.5
      },
      "retained_if_not_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
      },
      "group": {
        "status": "ok",
        "rate": 0.5,
        "others_rate": 0.9,
        "gap": -40.0,
        "likely_noise": true
      }
    },
    {
      "course": "MTH 114",
      "name": "APPLIED MATHEMATICS I",
      "subject": "M",
      "students": 4,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 2
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 2,
        "W": 1
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 2,
        "retained": 0,
        "rate": 0.0
      },
      "group": {
        "status": "ok",
        "rate": 0.5,
        "others_rate": 0.0,
        "gap": 50.0,
        "likely_noise": true
      }
    },
    {
      "course": "MTH 140",
      "name": "PRECALCULUS",
      "subject": "M",
      "students": 4,
      "first_pass": 2,
      "passed": 4,
      "path": {
        "first": 2,
        "retook_passed": 2,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 4,
        "Below C": 1,
        "Under 1.0": 0,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 4,
        "retained": 4,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": {
        "status": "ok",
        "rate": 0.5,
        "others_rate": 0.75,
        "gap": -25.0,
        "likely_noise": true
      }
    },
    {
      "course": "MTHM 168",
      "name": "STATISTICS",
      "subject": "M",
      "students": 4,
      "first_pass": 3,
      "passed": 3,
      "path": {
        "first": 3,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 3,
        "Below C": 1,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 3,
        "retained": 3,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "group": {
        "status": "ok",
        "rate": 0.75,
        "others_rate": 0.5,
        "gap": 25.0,
        "likely_noise": true
      }
    },
    {
      "course": "ENG 1113",
      "name": "ENGLISH COMPOSITION I",
      "subject": "E",
      "students": 3,
      "first_pass": 3,
      "passed": 3,
      "path": {
        "first": 3,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 3,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 3,
        "retained": 3,
        "rate": 1.0
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
    },
    {
      "course": "MATH 1350",
      "name": "INTRO TO STAT",
      "subject": "M",
      "students": 3,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 2
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 2,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 2,
        "retained": 1,
        "rate": 0.5
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
      "course": "MATH 387",
      "name": "COLLEGE ALGEBRA MATH PATHWAY",
      "subject": "M",
      "students": 3,
      "first_pass": 3,
      "passed": 3,
      "path": {
        "first": 3,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 3,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 3,
        "retained": 1,
        "rate": 0.3333
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
    },
    {
      "course": "MTH 141",
      "name": "QUANTITATIVE LITERACY",
      "subject": "M",
      "students": 3,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 2
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 1,
        "W": 1
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
      },
      "group": {
        "status": "ok",
        "rate": 0.3333,
        "others_rate": 0.0,
        "gap": 33.33,
        "likely_noise": true
      }
    },
    {
      "course": "MTH 144",
      "name": "PRECALCULUS",
      "subject": "M",
      "students": 3,
      "first_pass": 3,
      "passed": 3,
      "path": {
        "first": 3,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 3,
        "W": 0
      },
      "retained_if_passed": {
        "students": 3,
        "retained": 3,
        "rate": 1.0
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
    },
    {
      "course": "MTH 154",
      "name": "QUANTITATIVE REASONING",
      "subject": "M",
      "students": 3,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 2,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 1,
        "rate": 0.5
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": {
        "status": "ok",
        "rate": 0.6667,
        "others_rate": 1.0,
        "gap": -33.33,
        "likely_noise": true
      }
    },
    {
      "course": "ENGL 2210",
      "name": "PROFESSIONAL & TECHNICAL COMM",
      "subject": "E",
      "students": 2,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
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
      "course": "MAT 106",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 2,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 1,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
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
      "course": "MAT 1313",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 2,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 1,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 1,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "group": {
        "status": "ok",
        "rate": 0.5,
        "others_rate": 1.0,
        "gap": -50.0,
        "likely_noise": true
      }
    },
    {
      "course": "MATH 104B",
      "name": "MATH-104B",
      "subject": "M",
      "students": 2,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 1,
        "Below C": 1,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": {
        "status": "ok",
        "rate": 0.5,
        "others_rate": 0.5,
        "gap": 0.0,
        "likely_noise": true
      }
    },
    {
      "course": "MATH 138",
      "name": "STATISTICS",
      "subject": "M",
      "students": 2,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 2,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 1,
        "rate": 0.5
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
    },
    {
      "course": "MATH 140",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 2,
      "first_pass": 0,
      "passed": 1,
      "path": {
        "first": 0,
        "retook_passed": 1,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 2
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": {
        "status": "ok",
        "rate": 0.0,
        "others_rate": 0.75,
        "gap": -75.0,
        "likely_noise": true
      }
    },
    {
      "course": "MTH 102",
      "name": "GENERAL EDUC STATISTICS",
      "subject": "M",
      "students": 2,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "group": {
        "status": "ok",
        "rate": 0.5,
        "others_rate": 1.0,
        "gap": -50.0,
        "likely_noise": true
      }
    },
    {
      "course": "MTH 122",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 2,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 1,
        "W": 1
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": {
        "status": "ok",
        "rate": 0.5,
        "others_rate": 1.0,
        "gap": -50.0,
        "likely_noise": true
      }
    },
    {
      "course": "MTH 129",
      "name": "PRECALCULUS I",
      "subject": "M",
      "students": 2,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": {
        "status": "ok",
        "rate": 0.5,
        "others_rate": 0.75,
        "gap": -25.0,
        "likely_noise": true
      }
    },
    {
      "course": "MTH 130",
      "name": "PRECALCULUS II",
      "subject": "M",
      "students": 2,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": {
        "status": "ok",
        "rate": 0.5,
        "others_rate": 0.4,
        "gap": 10.0,
        "likely_noise": true
      }
    },
    {
      "course": "MTH 142",
      "name": "GENERAL EDUCATION STATISTICS",
      "subject": "M",
      "students": 2,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 2,
        "W": 0
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
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
    },
    {
      "course": "MTH 200",
      "name": "CALCULUS I",
      "subject": "M",
      "students": 2,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "group": {
        "status": "ok",
        "rate": 0.5,
        "others_rate": 0.6667,
        "gap": -16.67,
        "likely_noise": true
      }
    },
    {
      "course": "MTH 222",
      "name": "BUSINESS STATISTICS",
      "subject": "M",
      "students": 2,
      "first_pass": 0,
      "passed": 0,
      "path": {
        "first": 0,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 2
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
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
      "course": "ENG 1001",
      "name": "ENGLISH COMPOSITION 1 PLUS",
      "subject": "E",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
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
      "course": "ENG 101A",
      "name": "FUNDAMENTALS OF ENGLISH I, ACCELERATED",
      "subject": "E",
      "students": 1,
      "first_pass": 0,
      "passed": 0,
      "path": {
        "first": 0,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": {
        "status": "ok",
        "rate": 0.0,
        "others_rate": 1.0,
        "gap": -100.0,
        "likely_noise": true
      }
    },
    {
      "course": "ENG 110",
      "name": "COMPOSITION I",
      "subject": "E",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": {
        "status": "ok",
        "rate": 1.0,
        "others_rate": 0.0,
        "gap": 100.0,
        "likely_noise": true
      }
    },
    {
      "course": "ENG 11103",
      "name": "COMPOSITION I",
      "subject": "E",
      "students": 1,
      "first_pass": 0,
      "passed": 0,
      "path": {
        "first": 0,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": {
        "status": "ok",
        "rate": 0.0,
        "others_rate": 1.0,
        "gap": -100.0,
        "likely_noise": false
      }
    },
    {
      "course": "ENG 130",
      "name": "BUSINESS WRITING",
      "subject": "E",
      "students": 1,
      "first_pass": 0,
      "passed": 0,
      "path": {
        "first": 0,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
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
      "course": "ENGL 100",
      "name": "COMPOSITION I",
      "subject": "E",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": {
        "status": "ok",
        "rate": 1.0,
        "others_rate": 0.0,
        "gap": 100.0,
        "likely_noise": true
      }
    },
    {
      "course": "ENGL 1101",
      "name": "COLLEGE COMPOSITION",
      "subject": "E",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
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
    },
    {
      "course": "ENGL 1113",
      "name": "FRESHMAN COMPOSITION I",
      "subject": "E",
      "students": 1,
      "first_pass": 0,
      "passed": 0,
      "path": {
        "first": 0,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 0,
        "Below C": 1,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "group": {
        "status": "ok",
        "rate": 0.0,
        "others_rate": 0.0,
        "gap": 0.0,
        "likely_noise": true
      }
    },
    {
      "course": "ENGL 162",
      "name": "\"COLLEGE COMPOSITION II\"",
      "subject": "E",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": {
        "status": "ok",
        "rate": 1.0,
        "others_rate": 0.6667,
        "gap": 33.33,
        "likely_noise": true
      }
    },
    {
      "course": "ENGL 164",
      "name": "COLLEGE COMP II W/TECHN TOPICS",
      "subject": "E",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
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
    },
    {
      "course": "ENGL 61",
      "name": "\"ACCELERATED WRITING REVIEW\"",
      "subject": "E",
      "students": 1,
      "first_pass": 0,
      "passed": 0,
      "path": {
        "first": 0,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "group": {
        "status": "ok",
        "rate": 0.0,
        "others_rate": 1.0,
        "gap": -100.0,
        "likely_noise": true
      }
    },
    {
      "course": "M 101",
      "name": "M 101 TECHNICAL MATH",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
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
      "course": "MAT 145",
      "name": "COLLEGE MATH WITH REVIEW",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
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
    },
    {
      "course": "MAT 155",
      "name": "COLLEGE ALGEBRA/FUNCTION W REV",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
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
    },
    {
      "course": "MAT 281",
      "name": "CALCULUS I",
      "subject": "M",
      "students": 1,
      "first_pass": 0,
      "passed": 0,
      "path": {
        "first": 0,
        "retook_passed": 0,
        "retook_not": 1,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 2,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
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
      "course": "MATH 124",
      "name": "MATH-124",
      "subject": "M",
      "students": 1,
      "first_pass": 0,
      "passed": 0,
      "path": {
        "first": 0,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "group": {
        "status": "ok",
        "rate": 0.0,
        "others_rate": 1.0,
        "gap": -100.0,
        "likely_noise": true
      }
    },
    {
      "course": "MATH 143",
      "name": "PRECALCULUS I",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
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
      "course": "MTH 109",
      "name": "ALGEBRA - BUSINESS/SOC SCIENCE",
      "subject": "M",
      "students": 1,
      "first_pass": 0,
      "passed": 0,
      "path": {
        "first": 0,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": {
        "status": "ok",
        "rate": 0.0,
        "others_rate": 1.0,
        "gap": -100.0,
        "likely_noise": true
      }
    },
    {
      "course": "MTH 111",
      "name": "BASIC TECHNICAL MATHEMATICS",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
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
      "course": "MTH 11505",
      "name": "MATH FOR EDUCATORS I",
      "subject": "M",
      "students": 1,
      "first_pass": 0,
      "passed": 0,
      "path": {
        "first": 0,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
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
      "course": "MTH 1241",
      "name": "STATISTICS PLUS",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
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
      "course": "MTH 21404",
      "name": "INTRO PROBABILITY & STATISTICS",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 1,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
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
    },
    {
      "course": "MTHM 155",
      "name": "\"TECHNICAL MATHEMATICS I\"",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
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
    },
    {
      "course": "MTHM 171",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": {
        "status": "ok",
        "rate": 1.0,
        "others_rate": 0.75,
        "gap": 25.0,
        "likely_noise": true
      }
    }
  ],
  "hidden_courses": 32,
  "left_out": 17,
  "pairs_considered": 919,
  "pairs": [
    {
      "courses": [
        "ENG 101",
        "MATH 126E"
      ],
      "students": 7,
      "retained": 2,
      "rate": 0.2857,
      "others_rate": 0.612,
      "gap": -32.63,
      "affected": -2.3,
      "likely_noise": true
    },
    {
      "courses": [
        "ENG 101",
        "MATH 26"
      ],
      "students": 7,
      "retained": 2,
      "rate": 0.2857,
      "others_rate": 0.612,
      "gap": -32.63,
      "affected": -2.3,
      "likely_noise": true
    },
    {
      "courses": [
        "ENG 111",
        "SDV 101"
      ],
      "students": 7,
      "retained": 2,
      "rate": 0.2857,
      "others_rate": 0.612,
      "gap": -32.63,
      "affected": -2.3,
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
    "min_students": 1,
    "source": "PDP analysis-ready cohort and course files (synthetic sample)",
    "loaded_at": "2026-11-24T00:47:20",
    "flagged": true,
    "year_one": "2024-25",
    "retention_term": "next academic year",
    "retention_observed": true,
    "first_term": null,
    "compared": false,
    "min_pair_students": 1,
    "grade_scale": {
      "grades": [
        {
          "grade": "C or higher",
          "points": "2.0 and up",
          "counted": true
        },
        {
          "grade": "Below C",
          "points": "1.0 to under 2.0 (D, D+, C-)",
          "counted": false
        },
        {
          "grade": "Under 1.0",
          "points": "under 1.0 (D- or F), or the code F",
          "counted": false
        },
        {
          "grade": "P",
          "points": "the code P (pass)",
          "counted": true
        },
        {
          "grade": "W",
          "points": "the code W (withdrew)",
          "counted": false
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
      "first_pass": 276,
      "passed": 282,
      "path": {
        "first": 276,
        "retook_passed": 6,
        "retook_not": 7,
        "no_retake": 77
      },
      "grades": {
        "C or higher": 230,
        "Below C": 15,
        "Under 1.0": 64,
        "P": 53,
        "W": 20
      },
      "retained_if_passed": {
        "students": 282,
        "retained": 203,
        "rate": 0.7199
      },
      "retained_if_not_passed": {
        "students": 84,
        "retained": 33,
        "rate": 0.3929
      },
      "group": null
    },
    {
      "course": "ENGL 101",
      "name": "ENGLISH COMPOSITION I",
      "subject": "E",
      "students": 76,
      "first_pass": 54,
      "passed": 54,
      "path": {
        "first": 54,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 22
      },
      "grades": {
        "C or higher": 54,
        "Below C": 5,
        "Under 1.0": 13,
        "P": 0,
        "W": 4
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
        "retook_passed": 1,
        "retook_not": 0,
        "no_retake": 17
      },
      "grades": {
        "C or higher": 36,
        "Below C": 0,
        "Under 1.0": 16,
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
        "retook_passed": 2,
        "retook_not": 1,
        "no_retake": 8
      },
      "grades": {
        "C or higher": 20,
        "Below C": 0,
        "Under 1.0": 9,
        "P": 0,
        "W": 3
      },
      "retained_if_passed": {
        "students": 20,
        "retained": 12,
        "rate": 0.6
      },
      "retained_if_not_passed": {
        "students": 9,
        "retained": 3,
        "rate": 0.3333
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
        "C or higher": 28,
        "Below C": 0,
        "Under 1.0": 0,
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
        "no_retake": 2
      },
      "grades": {
        "C or higher": 21,
        "Below C": 0,
        "Under 1.0": 2,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 21,
        "retained": 10,
        "rate": 0.4762
      },
      "retained_if_not_passed": {
        "students": 2,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "MATH 116",
      "name": "MATH-116",
      "subject": "M",
      "students": 22,
      "first_pass": 13,
      "passed": 14,
      "path": {
        "first": 13,
        "retook_passed": 1,
        "retook_not": 1,
        "no_retake": 7
      },
      "grades": {
        "C or higher": 14,
        "Below C": 2,
        "Under 1.0": 7,
        "P": 0,
        "W": 2
      },
      "retained_if_passed": {
        "students": 14,
        "retained": 12,
        "rate": 0.8571
      },
      "retained_if_not_passed": {
        "students": 8,
        "retained": 2,
        "rate": 0.25
      },
      "group": null
    },
    {
      "course": "ENG 102",
      "name": "FIRST-YEAR COMPOSITION",
      "subject": "E",
      "students": 19,
      "first_pass": 16,
      "passed": 16,
      "path": {
        "first": 16,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 3
      },
      "grades": {
        "C or higher": 16,
        "Below C": 1,
        "Under 1.0": 2,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 16,
        "retained": 10,
        "rate": 0.625
      },
      "retained_if_not_passed": {
        "students": 3,
        "retained": 2,
        "rate": 0.6667
      },
      "group": null
    },
    {
      "course": "ENGL 161",
      "name": "\"COLLEGE COMPOSITION I\"",
      "subject": "E",
      "students": 19,
      "first_pass": 13,
      "passed": 15,
      "path": {
        "first": 13,
        "retook_passed": 2,
        "retook_not": 1,
        "no_retake": 3
      },
      "grades": {
        "C or higher": 15,
        "Below C": 1,
        "Under 1.0": 3,
        "P": 0,
        "W": 3
      },
      "retained_if_passed": {
        "students": 15,
        "retained": 10,
        "rate": 0.6667
      },
      "retained_if_not_passed": {
        "students": 4,
        "retained": 2,
        "rate": 0.5
      },
      "group": null
    },
    {
      "course": "MATH 130",
      "name": "INTRODUCTION TO STATISTICS",
      "subject": "M",
      "students": 18,
      "first_pass": 11,
      "passed": 11,
      "path": {
        "first": 11,
        "retook_passed": 0,
        "retook_not": 4,
        "no_retake": 3
      },
      "grades": {
        "C or higher": 11,
        "Below C": 2,
        "Under 1.0": 6,
        "P": 0,
        "W": 3
      },
      "retained_if_passed": {
        "students": 11,
        "retained": 7,
        "rate": 0.6364
      },
      "retained_if_not_passed": {
        "students": 7,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "ENG 111",
      "name": "COLLEGE COMPOSITION I",
      "subject": "E",
      "students": 17,
      "first_pass": 12,
      "passed": 12,
      "path": {
        "first": 12,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 5
      },
      "grades": {
        "C or higher": 12,
        "Below C": 1,
        "Under 1.0": 2,
        "P": 0,
        "W": 3
      },
      "retained_if_passed": {
        "students": 12,
        "retained": 5,
        "rate": 0.4167
      },
      "retained_if_not_passed": {
        "students": 5,
        "retained": 0,
        "rate": 0.0
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
        "first": 8,
        "retook_passed": 0,
        "retook_not": 3,
        "no_retake": 6
      },
      "grades": {
        "C or higher": 8,
        "Below C": 0,
        "Under 1.0": 11,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 8,
        "retained": 5,
        "rate": 0.625
      },
      "retained_if_not_passed": {
        "students": 9,
        "retained": 3,
        "rate": 0.3333
      },
      "group": null
    },
    {
      "course": "MATH 103",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 17,
      "first_pass": 12,
      "passed": 12,
      "path": {
        "first": 12,
        "retook_passed": 0,
        "retook_not": 1,
        "no_retake": 4
      },
      "grades": {
        "C or higher": 12,
        "Below C": 1,
        "Under 1.0": 3,
        "P": 0,
        "W": 2
      },
      "retained_if_passed": {
        "students": 12,
        "retained": 8,
        "rate": 0.6667
      },
      "retained_if_not_passed": {
        "students": 5,
        "retained": 2,
        "rate": 0.4
      },
      "group": null
    },
    {
      "course": "MATH 140",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 17,
      "first_pass": 12,
      "passed": 12,
      "path": {
        "first": 12,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 5
      },
      "grades": {
        "C or higher": 12,
        "Below C": 2,
        "Under 1.0": 2,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 12,
        "retained": 5,
        "rate": 0.4167
      },
      "retained_if_not_passed": {
        "students": 5,
        "retained": 2,
        "rate": 0.4
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
        "first": 9,
        "retook_passed": 0,
        "retook_not": 2,
        "no_retake": 4
      },
      "grades": {
        "C or higher": 9,
        "Below C": 0,
        "Under 1.0": 4,
        "P": 0,
        "W": 4
      },
      "retained_if_passed": {
        "students": 9,
        "retained": 8,
        "rate": 0.8889
      },
      "retained_if_not_passed": {
        "students": 6,
        "retained": 4,
        "rate": 0.6667
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
        "no_retake": 3
      },
      "grades": {
        "C or higher": 11,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 0,
        "W": 2
      },
      "retained_if_passed": {
        "students": 11,
        "retained": 7,
        "rate": 0.6364
      },
      "retained_if_not_passed": {
        "students": 3,
        "retained": 1,
        "rate": 0.3333
      },
      "group": null
    },
    {
      "course": "MATH 104B",
      "name": "MATH-104B",
      "subject": "M",
      "students": 13,
      "first_pass": 7,
      "passed": 7,
      "path": {
        "first": 7,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 6
      },
      "grades": {
        "C or higher": 7,
        "Below C": 1,
        "Under 1.0": 4,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 7,
        "retained": 3,
        "rate": 0.4286
      },
      "retained_if_not_passed": {
        "students": 6,
        "retained": 3,
        "rate": 0.5
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
        "no_retake": 3
      },
      "grades": {
        "C or higher": 10,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 3
      },
      "retained_if_passed": {
        "students": 10,
        "retained": 7,
        "rate": 0.7
      },
      "retained_if_not_passed": {
        "students": 3,
        "retained": 1,
        "rate": 0.3333
      },
      "group": null
    },
    {
      "course": "MATH 150",
      "name": "PRE-CALCULUS",
      "subject": "M",
      "students": 12,
      "first_pass": 11,
      "passed": 11,
      "path": {
        "first": 11,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 11,
        "Below C": 1,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 11,
        "retained": 6,
        "rate": 0.5455
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
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
        "C or higher": 12,
        "Below C": 0,
        "Under 1.0": 0,
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
        "first": 5,
        "retook_passed": 1,
        "retook_not": 1,
        "no_retake": 5
      },
      "grades": {
        "C or higher": 6,
        "Below C": 0,
        "Under 1.0": 5,
        "P": 0,
        "W": 3
      },
      "retained_if_passed": {
        "students": 6,
        "retained": 5,
        "rate": 0.8333
      },
      "retained_if_not_passed": {
        "students": 6,
        "retained": 3,
        "rate": 0.5
      },
      "group": null
    },
    {
      "course": "MTHM 168",
      "name": "\"STATISTICS\"",
      "subject": "M",
      "students": 12,
      "first_pass": 7,
      "passed": 8,
      "path": {
        "first": 7,
        "retook_passed": 1,
        "retook_not": 1,
        "no_retake": 3
      },
      "grades": {
        "C or higher": 8,
        "Below C": 1,
        "Under 1.0": 1,
        "P": 0,
        "W": 4
      },
      "retained_if_passed": {
        "students": 8,
        "retained": 5,
        "rate": 0.625
      },
      "retained_if_not_passed": {
        "students": 4,
        "retained": 2,
        "rate": 0.5
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
        "first": 8,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 3
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 3,
        "P": 8,
        "W": 0
      },
      "retained_if_passed": {
        "students": 8,
        "retained": 5,
        "rate": 0.625
      },
      "retained_if_not_passed": {
        "students": 3,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "MTH 200",
      "name": "CALCULUS I",
      "subject": "M",
      "students": 11,
      "first_pass": 4,
      "passed": 5,
      "path": {
        "first": 4,
        "retook_passed": 1,
        "retook_not": 2,
        "no_retake": 4
      },
      "grades": {
        "C or higher": 5,
        "Below C": 1,
        "Under 1.0": 2,
        "P": 0,
        "W": 6
      },
      "retained_if_passed": {
        "students": 5,
        "retained": 4,
        "rate": 0.8
      },
      "retained_if_not_passed": {
        "students": 6,
        "retained": 2,
        "rate": 0.3333
      },
      "group": null
    },
    {
      "course": "MTH 101",
      "name": "QUANTITATIVE LITERACY",
      "subject": "M",
      "students": 10,
      "first_pass": 6,
      "passed": 6,
      "path": {
        "first": 6,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 4
      },
      "grades": {
        "C or higher": 6,
        "Below C": 1,
        "Under 1.0": 2,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 6,
        "retained": 5,
        "rate": 0.8333
      },
      "retained_if_not_passed": {
        "students": 4,
        "retained": 2,
        "rate": 0.5
      },
      "group": null
    },
    {
      "course": "INRW 385",
      "name": "INTEGRATED READING AND WRITING",
      "subject": "E",
      "students": 9,
      "first_pass": 9,
      "passed": 9,
      "path": {
        "first": 9,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 9,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 9,
        "retained": 2,
        "rate": 0.2222
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MATH 138",
      "name": "STATISTICS",
      "subject": "M",
      "students": 9,
      "first_pass": 8,
      "passed": 8,
      "path": {
        "first": 8,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 8,
        "Below C": 1,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 8,
        "retained": 6,
        "rate": 0.75
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "MTH 102",
      "name": "GENERAL EDUC STATISTICS",
      "subject": "M",
      "students": 9,
      "first_pass": 7,
      "passed": 7,
      "path": {
        "first": 7,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 2
      },
      "grades": {
        "C or higher": 6,
        "Below C": 1,
        "Under 1.0": 0,
        "P": 1,
        "W": 1
      },
      "retained_if_passed": {
        "students": 7,
        "retained": 4,
        "rate": 0.5714
      },
      "retained_if_not_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "ENGL 1101",
      "name": "COLLEGE COMPOSITION",
      "subject": "E",
      "students": 8,
      "first_pass": 4,
      "passed": 4,
      "path": {
        "first": 4,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 4
      },
      "grades": {
        "C or higher": 4,
        "Below C": 1,
        "Under 1.0": 3,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 4,
        "retained": 4,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 4,
        "retained": 3,
        "rate": 0.75
      },
      "group": null
    },
    {
      "course": "ENGL 112",
      "name": "COMPOSITION I",
      "subject": "E",
      "students": 8,
      "first_pass": 5,
      "passed": 5,
      "path": {
        "first": 5,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 3
      },
      "grades": {
        "C or higher": 5,
        "Below C": 0,
        "Under 1.0": 2,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 5,
        "retained": 1,
        "rate": 0.2
      },
      "retained_if_not_passed": {
        "students": 3,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "MATH 1130",
      "name": "SURVEY OF MATHEMATICS",
      "subject": "M",
      "students": 8,
      "first_pass": 3,
      "passed": 4,
      "path": {
        "first": 3,
        "retook_passed": 1,
        "retook_not": 0,
        "no_retake": 4
      },
      "grades": {
        "C or higher": 4,
        "Below C": 3,
        "Under 1.0": 2,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 4,
        "retained": 3,
        "rate": 0.75
      },
      "retained_if_not_passed": {
        "students": 4,
        "retained": 1,
        "rate": 0.25
      },
      "group": null
    },
    {
      "course": "MTH 107",
      "name": "BASIC STATISTICS",
      "subject": "M",
      "students": 8,
      "first_pass": 5,
      "passed": 5,
      "path": {
        "first": 5,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 3
      },
      "grades": {
        "C or higher": 5,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 3
      },
      "retained_if_passed": {
        "students": 5,
        "retained": 4,
        "rate": 0.8
      },
      "retained_if_not_passed": {
        "students": 3,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "MTH 152",
      "name": "STATISTICS (MA)",
      "subject": "M",
      "students": 8,
      "first_pass": 7,
      "passed": 7,
      "path": {
        "first": 7,
        "retook_passed": 0,
        "retook_not": 1,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 2,
        "P": 7,
        "W": 0
      },
      "retained_if_passed": {
        "students": 7,
        "retained": 5,
        "rate": 0.7143
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "MAT 141",
      "name": "COLLEGE MATHEMATICS",
      "subject": "M",
      "students": 7,
      "first_pass": 6,
      "passed": 6,
      "path": {
        "first": 6,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 6,
        "Below C": 1,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 6,
        "retained": 5,
        "rate": 0.8333
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "MATH 120",
      "name": "MATH-120",
      "subject": "M",
      "students": 7,
      "first_pass": 5,
      "passed": 5,
      "path": {
        "first": 5,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 2
      },
      "grades": {
        "C or higher": 5,
        "Below C": 1,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 5,
        "retained": 4,
        "rate": 0.8
      },
      "retained_if_not_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "MTH 134",
      "name": "CALCULUS/ BUSINESS&SOCIAL SCI",
      "subject": "M",
      "students": 7,
      "first_pass": 5,
      "passed": 5,
      "path": {
        "first": 5,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 2
      },
      "grades": {
        "C or higher": 5,
        "Below C": 1,
        "Under 1.0": 0,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 5,
        "retained": 2,
        "rate": 0.4
      },
      "retained_if_not_passed": {
        "students": 2,
        "retained": 1,
        "rate": 0.5
      },
      "group": null
    },
    {
      "course": "MTH 225",
      "name": "BUSINESS STATISTICS",
      "subject": "M",
      "students": 7,
      "first_pass": 6,
      "passed": 6,
      "path": {
        "first": 6,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 6,
        "Below C": 1,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 6,
        "retained": 5,
        "rate": 0.8333
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "ENG 1113",
      "name": "ENGLISH COMPOSITION I",
      "subject": "E",
      "students": 6,
      "first_pass": 3,
      "passed": 3,
      "path": {
        "first": 3,
        "retook_passed": 0,
        "retook_not": 1,
        "no_retake": 2
      },
      "grades": {
        "C or higher": 3,
        "Below C": 0,
        "Under 1.0": 3,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 3,
        "retained": 2,
        "rate": 0.6667
      },
      "retained_if_not_passed": {
        "students": 3,
        "retained": 1,
        "rate": 0.3333
      },
      "group": null
    },
    {
      "course": "MAT 145",
      "name": "COLLEGE MATH WITH REVIEW",
      "subject": "M",
      "students": 6,
      "first_pass": 5,
      "passed": 5,
      "path": {
        "first": 5,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 5,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 5,
        "retained": 4,
        "rate": 0.8
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "MATH 1030",
      "name": "INTRO TO STATISTICS",
      "subject": "M",
      "students": 6,
      "first_pass": 5,
      "passed": 5,
      "path": {
        "first": 5,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 5,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 5,
        "retained": 4,
        "rate": 0.8
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "MTH 201",
      "name": "CALCULUS II",
      "subject": "M",
      "students": 6,
      "first_pass": 5,
      "passed": 5,
      "path": {
        "first": 5,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 5,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 5,
        "retained": 4,
        "rate": 0.8
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "MTH 21404",
      "name": "INTRO PROBABILITY & STATISTICS",
      "subject": "M",
      "students": 6,
      "first_pass": 4,
      "passed": 4,
      "path": {
        "first": 4,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 2
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 2,
        "P": 4,
        "W": 0
      },
      "retained_if_passed": {
        "students": 4,
        "retained": 3,
        "rate": 0.75
      },
      "retained_if_not_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "MTHM 171",
      "name": "\"COLLEGE ALGEBRA\"",
      "subject": "M",
      "students": 6,
      "first_pass": 4,
      "passed": 4,
      "path": {
        "first": 4,
        "retook_passed": 0,
        "retook_not": 1,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 4,
        "Below C": 0,
        "Under 1.0": 2,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 4,
        "retained": 3,
        "rate": 0.75
      },
      "retained_if_not_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "ENG 1000",
      "name": "ENGLISH COMPOSITION I",
      "subject": "E",
      "students": 5,
      "first_pass": 4,
      "passed": 4,
      "path": {
        "first": 4,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 4,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 4,
        "retained": 3,
        "rate": 0.75
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "MAT 142",
      "name": "COLLEGE MATHEMATICS",
      "subject": "M",
      "students": 5,
      "first_pass": 5,
      "passed": 5,
      "path": {
        "first": 5,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 5,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 5,
        "retained": 2,
        "rate": 0.4
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MATH 1220",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 5,
      "first_pass": 3,
      "passed": 4,
      "path": {
        "first": 3,
        "retook_passed": 1,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 4,
        "Below C": 1,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 4,
        "retained": 4,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "MATH 124",
      "name": "MATH-124",
      "subject": "M",
      "students": 5,
      "first_pass": 3,
      "passed": 3,
      "path": {
        "first": 3,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 2
      },
      "grades": {
        "C or higher": 3,
        "Below C": 2,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 3,
        "retained": 2,
        "rate": 0.6667
      },
      "retained_if_not_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "MATH 126",
      "name": "MATH-126",
      "subject": "M",
      "students": 5,
      "first_pass": 3,
      "passed": 3,
      "path": {
        "first": 3,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 2
      },
      "grades": {
        "C or higher": 3,
        "Below C": 1,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 3,
        "retained": 2,
        "rate": 0.6667
      },
      "retained_if_not_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "MTH 112",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 5,
      "first_pass": 5,
      "passed": 5,
      "path": {
        "first": 5,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 5,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 5,
        "retained": 4,
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
      "course": "MATH 141",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 4,
      "first_pass": 4,
      "passed": 4,
      "path": {
        "first": 4,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 4,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 4,
        "retained": 3,
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
      "course": "MTH 104",
      "name": "BUSINESS MATHEMATICS",
      "subject": "M",
      "students": 4,
      "first_pass": 2,
      "passed": 3,
      "path": {
        "first": 2,
        "retook_passed": 1,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 3,
        "Below C": 1,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 3,
        "retained": 3,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "MTH 1241",
      "name": "STATISTICS PLUS",
      "subject": "M",
      "students": 4,
      "first_pass": 0,
      "passed": 1,
      "path": {
        "first": 0,
        "retook_passed": 1,
        "retook_not": 0,
        "no_retake": 3
      },
      "grades": {
        "C or higher": 1,
        "Below C": 2,
        "Under 1.0": 2,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "retained_if_not_passed": {
        "students": 3,
        "retained": 2,
        "rate": 0.6667
      },
      "group": null
    },
    {
      "course": "MTHM 68",
      "name": "\"STATISTICS CO-REQUISITE\"",
      "subject": "M",
      "students": 4,
      "first_pass": 4,
      "passed": 4,
      "path": {
        "first": 4,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 4,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 4,
        "retained": 4,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "ENG 1001",
      "name": "ENGLISH COMPOSITION 1 PLUS",
      "subject": "E",
      "students": 3,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 2,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "MAT 151",
      "name": "COLLEGE ALGEBRA/FUNCTIONS",
      "subject": "M",
      "students": 3,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 2,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 1,
        "rate": 0.5
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "MTH 140",
      "name": "PRECALCULUS",
      "subject": "M",
      "students": 3,
      "first_pass": 1,
      "passed": 2,
      "path": {
        "first": 1,
        "retook_passed": 1,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 2,
        "Below C": 1,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "MTH 222",
      "name": "BUSINESS STATISTICS",
      "subject": "M",
      "students": 3,
      "first_pass": 3,
      "passed": 3,
      "path": {
        "first": 3,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 3,
        "W": 0
      },
      "retained_if_passed": {
        "students": 3,
        "retained": 3,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTHM 181",
      "name": "\"CALCULUS I\"",
      "subject": "M",
      "students": 3,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 2,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 1,
        "rate": 0.5
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "MTHM 72",
      "name": "\"COLLEGE ALGEBRA CO-REQUISITE\"",
      "subject": "M",
      "students": 3,
      "first_pass": 3,
      "passed": 3,
      "path": {
        "first": 3,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 3,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 3,
        "retained": 3,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTHM 92",
      "name": "\"MATH FOUNDATIONS\"",
      "subject": "M",
      "students": 3,
      "first_pass": 3,
      "passed": 3,
      "path": {
        "first": 3,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 3,
        "W": 0
      },
      "retained_if_passed": {
        "students": 3,
        "retained": 2,
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
      "course": "ENGL 61",
      "name": "\"ACCELERATED WRITING REVIEW\"",
      "subject": "E",
      "students": 2,
      "first_pass": 0,
      "passed": 0,
      "path": {
        "first": 0,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 2
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 2,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": 2,
        "retained": 1,
        "rate": 0.5
      },
      "group": null
    },
    {
      "course": "MAT 106",
      "name": "MATH FOR HEALTH SCI",
      "subject": "M",
      "students": 2,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 2,
        "W": 0
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MAT 1313",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 2,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 2,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MAT 172",
      "name": "MATH FOR TCHRS I: NUM & OPR",
      "subject": "M",
      "students": 2,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "MATH 132",
      "name": "MATHEMATICAL LITERACY",
      "subject": "M",
      "students": 2,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 2,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MATH 143",
      "name": "PRECALCULUS I",
      "subject": "M",
      "students": 2,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 2,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 1,
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
      "course": "MATH 181",
      "name": "CALCULUS I",
      "subject": "M",
      "students": 2,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 2,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 0,
        "rate": 0.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTH 1240",
      "name": "STATISTICS",
      "subject": "M",
      "students": 2,
      "first_pass": 1,
      "passed": 2,
      "path": {
        "first": 1,
        "retook_passed": 1,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 2,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTH 130",
      "name": "PRECALCULUS II",
      "subject": "M",
      "students": 2,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 2,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTH 154",
      "name": "QUANTITATIVE REASONING",
      "subject": "M",
      "students": 2,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 2,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 2,
        "rate": 1.0
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
      "students": 2,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 1,
        "Below C": 1,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "MTH 220",
      "name": "DISCRETE MATHEMATICS",
      "subject": "M",
      "students": 2,
      "first_pass": 2,
      "passed": 2,
      "path": {
        "first": 2,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 2,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 2,
        "retained": 0,
        "rate": 0.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTHM 155",
      "name": "\"TECHNICAL MATHEMATICS I\"",
      "subject": "M",
      "students": 2,
      "first_pass": 0,
      "passed": 0,
      "path": {
        "first": 0,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 2
      },
      "grades": {
        "C or higher": 0,
        "Below C": 1,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": 2,
        "retained": 1,
        "rate": 0.5
      },
      "group": null
    },
    {
      "course": "MTHM 163",
      "name": "\"MATHEMATICS/ELEMENTARY TEACHER\"",
      "subject": "M",
      "students": 2,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "ENG 100",
      "name": "INTRO TO COLLEGE ENG",
      "subject": "E",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "ENG 101A",
      "name": "FUNDAMENTALS OF ENGLISH I, ACCELERATED",
      "subject": "E",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 1,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "ENG 110",
      "name": "COMPOSITION I",
      "subject": "E",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "ENG 130",
      "name": "BUSINESS WRITING",
      "subject": "E",
      "students": 1,
      "first_pass": 0,
      "passed": 0,
      "path": {
        "first": 0,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "ENG 152",
      "name": "BUSINESS COMMUNICATION",
      "subject": "E",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "ENGL 110",
      "name": "COLLEGE COMPOSITION I",
      "subject": "E",
      "students": 1,
      "first_pass": 0,
      "passed": 0,
      "path": {
        "first": 0,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "ENGL 1113",
      "name": "FRESHMAN COMPOSITION I",
      "subject": "E",
      "students": 1,
      "first_pass": 0,
      "passed": 0,
      "path": {
        "first": 0,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 0,
        "Below C": 1,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "ENGL 164",
      "name": "\"COLLEGE COMP II W/TECHN TOPICS\"",
      "subject": "E",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "ENGL 2221",
      "name": "WRITING HUMANITIES & SOC SCI",
      "subject": "E",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MAT 107",
      "name": "MATH FOR ELEM EDUC",
      "subject": "M",
      "students": 1,
      "first_pass": 0,
      "passed": 0,
      "path": {
        "first": 0,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "group": null
    },
    {
      "course": "MATH 100",
      "name": "COLLEGE MATH FOR BUSINESS",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MATH 1250",
      "name": "TRIG & PRE-CALC",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MATH 128",
      "name": "CONCEPTS OF MATH II",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MATH 145",
      "name": "BUSINESS CALCULUS",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MATH 1511",
      "name": "CALCULUS I",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MATH 1513",
      "name": "COLLEGE ALGEBRA",
      "subject": "M",
      "students": 1,
      "first_pass": 0,
      "passed": 0,
      "path": {
        "first": 0,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "MATH 324",
      "name": "COLLEGE ALGEBRA MATH PATHWAY",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTH 111",
      "name": "BASIC TECHNICAL MATHEMATICS",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTH 121",
      "name": "PRECALCULUS I",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 1,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
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
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTH 202",
      "name": "CALCULUS III",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTHM 158",
      "name": "\"QUANTITATIVE REASONING\"",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "MTHM 57",
      "name": "\"QUANTITATIVE REASONING CO-REQ\"",
      "subject": "M",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 1,
        "rate": 1.0
      },
      "retained_if_not_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "group": null
    },
    {
      "course": "STA 120",
      "name": "INTRODUCTION TO STATISTICS",
      "subject": "M",
      "students": 1,
      "first_pass": 0,
      "passed": 0,
      "path": {
        "first": 0,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 1,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    },
    {
      "course": "WRIT 101",
      "name": "WRIT 101 COLLEGE WRITING I",
      "subject": "E",
      "students": 1,
      "first_pass": 0,
      "passed": 0,
      "path": {
        "first": 0,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 1
      },
      "grades": {
        "C or higher": 0,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 1
      },
      "retained_if_passed": {
        "students": null,
        "retained": null,
        "rate": null
      },
      "retained_if_not_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
      },
      "group": null
    }
  ],
  "hidden_courses": 0,
  "left_out": 39,
  "pairs_considered": 1374,
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
      "likely_noise": true
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
      "likely_noise": true
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
    "min_students": 1,
    "source": "PDP analysis-ready cohort and course files (synthetic sample)",
    "loaded_at": "2026-11-24T00:47:20",
    "flagged": true,
    "year_one": "2023-24",
    "retention_term": "next academic year",
    "retention_observed": true,
    "first_term": "Fall 2023",
    "compared": true,
    "min_pair_students": 1,
    "grade_scale": {
      "grades": [
        {
          "grade": "C or higher",
          "points": "2.0 and up",
          "counted": true
        },
        {
          "grade": "Below C",
          "points": "1.0 to under 2.0 (D, D+, C-)",
          "counted": false
        },
        {
          "grade": "Under 1.0",
          "points": "under 1.0 (D- or F), or the code F",
          "counted": false
        },
        {
          "grade": "P",
          "points": "the code P (pass)",
          "counted": true
        },
        {
          "grade": "W",
          "points": "the code W (withdrew)",
          "counted": false
        }
      ],
      "left_out": "I (incomplete), A (audit), M or MIS (missing), O or OTH (other), and any code the PDP dictionary doesn't list, such as UW, aren't final grades, so neither page counts them."
    }
  },
  "status": "ok",
  "students": 2,
  "cohort_retention": {
    "type": "school",
    "status": "ok",
    "retained": 0,
    "students": 2,
    "numerator": 0,
    "denominator": 2,
    "rate": 0.0,
    "n_excluded": 0,
    "n_out_of_scope": 0
  },
  "courses": [
    {
      "course": "ENGL 121",
      "name": "COLLEGE COMPOSITION",
      "subject": "E",
      "students": 1,
      "first_pass": 1,
      "passed": 1,
      "path": {
        "first": 1,
        "retook_passed": 0,
        "retook_not": 0,
        "no_retake": 0
      },
      "grades": {
        "C or higher": 1,
        "Below C": 0,
        "Under 1.0": 0,
        "P": 0,
        "W": 0
      },
      "retained_if_passed": {
        "students": 1,
        "retained": 0,
        "rate": 0.0
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
  "hidden_courses": 108,
  "left_out": 0,
  "pairs_considered": 3,
  "pairs": []
};
