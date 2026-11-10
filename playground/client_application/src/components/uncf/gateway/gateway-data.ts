import type { ExplorerMeta } from "@/components/uncf/layout/explorer-api";

/** Next-fall retention for a group of students. Every number is null when the group has under 10 students. */
export type Retention = { students: number | null; retained: number | null; rate: number | null };

/** One gateway course: outcomes of each student's first attempt in year 1, and retention by outcome. */
export type GatewayCourse = {
  course: string;
  name: string | null;
  /** E for gateway English, M for gateway math. */
  subject: "E" | "M";
  /** Students with a final grade on their first attempt. */
  students: number;
  passed: number;
  df: number;
  w: number;
  /** Students whose first attempt had no final grade (incomplete, audit, missing); null when under 10. */
  other: number | null;
  retained_if_passed: Retention;
  retained_if_not_passed: Retention;
};

/** Two courses taken together in the first term, with next-fall retention below the cohort's. */
export type CoursePair = { courses: [string, string]; students: number; retained: number; rate: number; gap: number };

/** The answer from GET /uncf/gateway (measures/breakdowns/gateway_courses.py). */
export type GatewayResponse = {
  meta: ExplorerMeta & {
    /** False when the institution flags no gateway courses this year, so they're inferred. */
    flagged: boolean;
    /** The fall term retention is measured in, e.g. Fall 2024. */
    retention_term: string;
    retention_observed: boolean;
    /** The students' first term when they all share it, e.g. Fall 2023; null when start terms are mixed. */
    first_term: string | null;
    min_pair_students: number;
  };
  status: "ok" | "suppressed";
  students: number | null;
  cohort_retention: Retention | null;
  courses: GatewayCourse[];
  hidden_courses: number;
  pairs: CoursePair[];
  pairs_considered: number;
};

/** The outcomes, in the design's order and colors. */
export const outcomeStyle = [
  { key: "passed", label: "Passed (A–C)", color: "var(--uncf-blue)", text: "#fff" },
  { key: "df", label: "D or F", color: "var(--uncf-orange)", text: "#1b1d21" },
  { key: "w", label: "Withdrew", color: "var(--uncf-peach)", text: "var(--uncf-ink)" },
] as const;

export const subjectLabel = { E: "English", M: "Math" } as const;
