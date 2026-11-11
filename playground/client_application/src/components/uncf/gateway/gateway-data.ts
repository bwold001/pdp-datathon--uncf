import type { ExplorerMeta, GradeScale } from "@/components/uncf/layout/explorer-api";

/** Retention for a group of students. Every number is null when the group is under meta.min_students. */
export type Retention = { students: number | null; retained: number | null; rate: number | null; [more: string]: unknown };

/** What happened after the first try, in year 1. A step is null when it has 1 to 9 students. */
export type GatewayPath = {
  first: number | null;
  retook_passed: number | null;
  retook_not: number | null;
  no_retake: number | null;
};

/** The filtered students' first-try pass rate against everyone else who took the course (the gap finder's math). */
export type GroupGap = {
  status: "ok" | "hidden";
  rate: number | null;
  others_rate: number | null;
  /** Percentage points; negative means the group passes on the first try less often. */
  gap: number | null;
  likely_noise: boolean | null;
};

/** One gateway course: its students' path through it in year 1, and retention by whether they passed. */
export type GatewayCourse = {
  course: string;
  name: string | null;
  /** E for gateway English, M for gateway math. */
  subject: "E" | "M";
  /** Students with a final grade in the course in year 1. */
  students: number;
  /** Passed on the first try: a grade of 1.0 or higher, or a pass. */
  first_pass: number;
  /** Passed on any try in year 1. */
  passed: number;
  path: GatewayPath;
  /** How many tries ended in each grade group (C or higher, D, Under 1.0, P, W), one per student per term. Null when hidden. */
  grades: Record<string, number | null>;
  retained_if_passed: Retention;
  retained_if_not_passed: Retention;
  /** null when no filter is set, so there is no group to compare. */
  group: GroupGap | null;
};

/** A gateway course and another course taken together in the first term, compared with everyone else. */
export type CoursePair = {
  courses: [string, string];
  students: number;
  retained: number;
  rate: number;
  others_rate: number;
  gap: number;
  /** Students the gap is worth: gap / 100 × students. */
  affected: number;
  likely_noise: boolean;
};

/** The answer from GET /uncf/gateway (measures/breakdowns/gateway_courses.py). */
export type GatewayResponse = {
  meta: ExplorerMeta & {
    /** False when the institution flags no gateway grades in year 1, so no course is listed. */
    flagged: boolean;
    /** The academic year counted: the cohort's first. */
    year_one: string;
    /** When retention is measured, e.g. Fall 2024, or "next academic year". */
    retention_term: string;
    retention_observed: boolean;
    /** The students' first term when they all share it, e.g. Fall 2023; null when start terms are mixed. */
    first_term: string | null;
    /** True when a filter is set, so each course has a group gap. */
    compared: boolean;
    min_pair_students: number;
    /** Every final grade, its grade points, and whether it passes a gateway course. */
    grade_scale: GradeScale;
  };
  status: "ok" | "suppressed";
  students: number | null;
  cohort_retention: Retention | null;
  courses: GatewayCourse[];
  hidden_courses: number;
  left_out: number | null;
  pairs: CoursePair[];
  pairs_considered: number;
};

/** The steps after the first try, in the design's order, words and colors. */
export const pathSteps = [
  { key: "first", label: "Passed on the first try", color: "var(--uncf-blue)" },
  { key: "retook_passed", label: "Retook it and passed", color: "var(--uncf-blue-mid)" },
  { key: "retook_not", label: "Retook it, still didn’t pass", color: "var(--uncf-f)" },
  { key: "no_retake", label: "Didn’t pass, didn’t retake", color: "var(--uncf-grey)" },
] as const;

export const subjectLabel = { E: "English", M: "Math" } as const;

/** How the course list can be sorted. "gap" needs a filter. */
export const gatewaySorts = {
  size: "Most students",
  first: "Lowest first-try pass",
  gap: "Group furthest behind",
} as const;
export type GatewaySort = keyof typeof gatewaySorts;

/** The courses in the chosen order. With no group gap, "gap" falls back to size. */
export function sortCourses(courses: GatewayCourse[], sort: GatewaySort): GatewayCourse[] {
  const gapOf = (course: GatewayCourse) => (course.group?.status === "ok" ? course.group.gap! : Infinity);
  const firstRate = (course: GatewayCourse) => course.first_pass / course.students;
  return [...courses].sort((a, b) => {
    if (sort === "gap") return gapOf(a) - gapOf(b) || b.students - a.students;
    if (sort === "first") return firstRate(a) - firstRate(b) || b.students - a.students;
    return b.students - a.students || a.course.localeCompare(b.course);
  });
}
