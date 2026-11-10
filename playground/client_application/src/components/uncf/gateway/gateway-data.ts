import type { ExplorerMeta, RetentionBlock } from "@/components/uncf/layout/explorer-api";

/** Retention for a group of students, in the measure meta.retention_type names. Every number is null under 10. */
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
  d: number;
  f: number;
  df: number;
  w: number;
  /** Each outcome's share of the students, from the API. */
  shares: { passed: number; d: number; f: number; w: number };
  /** Students whose first attempt had no final grade (incomplete, audit, missing); null when under 10. */
  other: number | null;
  retained_if_passed: Retention;
  retained_if_not_passed: Retention;
};

/** Two courses taken together in the first term, with retention below the cohort's. */
export type CoursePair = { courses: [string, string]; students: number; retained: number; rate: number; gap: number };

/** The answer from GET /uncf/gateway (measures/breakdowns/gateway_courses.py). */
export type GatewayResponse = {
  meta: ExplorerMeta & {
    /** False when the institution flags no gateway courses this year, so they're inferred. */
    flagged: boolean;
    /** When retention is measured: a fall term for federal (Fall 2024), "next academic year" for school. */
    retention_term: string;
    retention_observed: boolean;
    /** The students' first term when they all share it, e.g. Fall 2023; null when start terms are mixed. */
    first_term: string | null;
    min_pair_students: number;
  };
  status: "ok" | "suppressed";
  students: number | null;
  /** The whole cohort's retention: the line the pairs are measured against. */
  cohort_retention: RetentionBlock | null;
  courses: GatewayCourse[];
  hidden_courses: number;
  /** First attempts at any gateway course (hidden ones too) with an incomplete, audit or missing grade; null under 10. */
  left_out: number | null;
  pairs: CoursePair[];
  pairs_considered: number;
};

/** The outcomes, in the design's order and colors, each with its share from the API's answer. */
export const outcomeStyle = [
  { key: "passed", label: "Passed (A–C)", color: "var(--uncf-blue)", text: "#fff", share: (c: GatewayCourse) => c.shares.passed },
  // The design shows D and F together; the API sends them apart.
  { key: "df", label: "D or F", color: "var(--uncf-orange)", text: "#1b1d21", share: (c: GatewayCourse) => c.shares.d + c.shares.f },
  { key: "w", label: "Withdrew", color: "var(--uncf-peach)", text: "var(--uncf-ink)", share: (c: GatewayCourse) => c.shares.w },
] as const;

export const subjectLabel = { E: "English", M: "Math" } as const;
