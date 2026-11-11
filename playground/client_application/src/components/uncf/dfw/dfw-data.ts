import type { ExplorerMeta, GradeScale } from "@/components/uncf/layout/explorer-api";
import { cohortFilters } from "@/components/uncf/layout/explorer-config";

/** The grades that count as a DFW, in the order the API sends and the page shows them. Every D letter is a D; a C- passes. */
export const dfwGrades = ["D", "F", "W"] as const;
export type DfwGrade = (typeof dfwGrades)[number];

/** D, F and W among a set of final grades, and each one's share of them, from the API. */
export type DfwSplit = {
  grades: Record<DfwGrade, number>;
  /** The D and F grades together. */
  DF: number;
  W: number;
  /** Final grades. */
  total: number;
  shares: Record<DfwGrade, number>;
};

/** Each DFW grade's label and color: D lighter than F, grey for a withdrawal. */
export const dfwGradeStyles: Record<DfwGrade, { label: string; color: string }> = {
  D: { label: "D", color: "var(--uncf-d)" },
  F: { label: "F", color: "var(--uncf-f)" },
  W: { label: "W", color: "var(--uncf-grey)" },
};

/** D-or-F, W and pass counts for a set of final grades. Every number is null under meta.min_students. */
export type DfwTally = {
  students: number | null;
  /** D, F and W grades. */
  num: number | null;
  /** Final grades. */
  den: number | null;
  rate: number | null;
  split: DfwSplit | null;
};

/** One course in the list. Courses with fewer than 10 final grades, or under meta.min_students, aren't listed. */
export type DfwCourseSummary = DfwTally & {
  course: string;
  names: { top: string[]; distinct: number };
  /** How many of the course's final grades were flagged as gateway math (M) or English (E). */
  gateway: { M: number; E: number };
  num: number;
  den: number;
  rate: number;
  split: DfwSplit;
};

/** The meta of a DFW answer: what every page says, plus the grade scale the numbers used. */
export type DfwMeta = ExplorerMeta & { grade_scale: GradeScale };

/** The answer from GET /uncf/dfw (measures/breakdowns/dfw_courses.py). */
export type DfwList = {
  meta: DfwMeta;
  status: "ok" | "suppressed";
  everyone: DfwTally;
  courses: DfwCourseSummary[];
  hidden_courses: number;
};

/** One value of a field within a course, e.g. Pell = Y, or delivery = Online, next to everyone else in the course. */
export type DfwPart = DfwTally & {
  value: string;
  /** The DFW rate of every other final grade in the course; null when they're under meta.min_students. */
  rest_rate: number | null;
  /** The part's rate minus rest_rate, in points. */
  gap: number | null;
};

/** The answer from GET /uncf/dfw/course: one course split by term, delivery method and student group. */
export type DfwCourseDetail = DfwTally & {
  meta: DfwMeta;
  course: string;
  names: { top: string[]; distinct: number };
  terms: DfwPart[];
  delivery: DfwPart[];
  groups: Record<string, DfwPart[]>;
};

/** The ways to compare students in a course, in the design's order. */
export const dfwDimensions: { id: string; label: string }[] = [
  { id: "pell", label: "Pell" },
  { id: "gender", label: "Gender" },
  { id: "race", label: "Race" },
  { id: "ethnicity", label: "Ethnicity" },
  { id: "age_band", label: "Age" },
  { id: "enrollment_intensity", label: "Full / part-time" },
  { id: "enrollment_type", label: "Enrollment type" },
  { id: "cohort_term", label: "Starting term" },
  { id: "delivery", label: "Delivery" },
  { id: "term", label: "Term taken" },
];

/** How each ranking orders the list, in the design's words. */
export const sortHints = {
  count: "Ranked by how many D, F and W grades a course gave. Big courses rise to the top: this is where the most grades are lost.",
  rate: "Ranked by the share of final grades that were a D, F or W, whatever the course’s size. Small courses can top this list.",
};

export type DfwSort = keyof typeof sortHints;

/** The size cutoffs offered: only courses with at least this many final grades. */
export const minimumGrades = [10, 30, 50, 100];

const ENROLLMENT_TYPES: Record<string, string> = { "First-time": "First-time", "Transfer-in": "Transfer-in", "Re-admit": "Re-admitted" };

/** A group value's label: the cohort bar's label where it has one (Pell recipient), else as stored. */
export function groupValueLabel(dimension: string, value: string): string {
  if (value === "UNKNOWN") return "Unknown";
  if (dimension === "enrollment_type") return ENROLLMENT_TYPES[value] ?? value;
  const filter = cohortFilters.find((definition) => definition.id === dimension);
  return filter?.options.find((option) => option.value === value)?.label ?? value;
}

/** The courses that pass the size cutoff, in the chosen order. */
export function rankCourses(courses: DfwCourseSummary[], sort: DfwSort, minimum: number): DfwCourseSummary[] {
  return courses
    .filter((course) => course.den >= minimum)
    .sort((a, b) => (sort === "count" ? b.num - a.num || b.rate - a.rate : b.rate - a.rate || b.num - a.num));
}

/** A rate from 0 to 1 as a percent with one decimal, e.g. 23.0%. */
export function percent(rate: number | null): string {
  return rate === null ? "–" : `${(rate * 100).toFixed(1)}%`;
}

/** A group compared with everyone else in the same course: its rate, theirs, and the gap in points. */
export type GroupComparison = { label: string; grades: number | null; rate: number | null; rest: number | null; gap: number | null };

/**
 * Each value of one field in the course, next to everyone else in the course, as the API compared them (rest_rate and
 * gap). Hidden groups have no numbers.
 */
export function groupRows(detail: DfwCourseDetail, dimension: string): GroupComparison[] {
  const parts = dimension === "delivery" ? detail.delivery : dimension === "term" ? detail.terms : (detail.groups[dimension] ?? []);
  return parts.map((part) => ({
    label: dimension === "delivery" || dimension === "term" ? part.value : groupValueLabel(dimension, part.value),
    grades: part.den,
    rate: part.rate,
    rest: part.rest_rate,
    gap: part.gap,
  }));
}

/** The share of final grades that were a D or an F (the D or F tile; the API sends them apart). */
export function dfShare(split: DfwSplit): number {
  return split.shares.D + split.shares.F;
}
