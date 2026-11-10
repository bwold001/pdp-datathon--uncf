import type { ExplorerMeta } from "@/components/uncf/layout/explorer-api";

/** The answer from GET /uncf/credit-momentum (uncf/explorer_credits.py). Hidden numbers (under 10 students) are null. */
export type CreditsResponse = {
  meta: ExplorerMeta & {
    /** The fall term retention is measured in, e.g. Fall 2024. */
    retention_term: string;
  };
  status: "ok" | "suppressed";
  students: number | null;
  credits: {
    /** Students with both year-1 credit numbers in the cohort file. */
    counted: number;
    /** Students left out because a year-1 credit number is blank. */
    left_out: number | null;
    avg_attempted: number | null;
    avg_earned: number | null;
  } | null;
  /** The shared credit completion measure: the average of each student's earned ÷ attempted. */
  completion: { counted: number | null; ratio: number | null } | null;
  milestones: { credits: number; students: number; share: number | null }[];
  /** The starting term and the next fall or spring term. */
  terms: { label: string; enrolled: number | null; avg_attempted: number | null; avg_earned: number | null }[];
  tiers: { key: string; label: string; students: number | null; share: number | null; retained: number | null; rate: number | null }[];
};

/** Each tier's colors, from the design: the tier bar, its text, and the retention bar. */
export const tierStyle: Record<string, { fill: string; text: string; bar: string }> = {
  under_15: { fill: "var(--uncf-orange)", text: "#1b1d21", bar: "var(--uncf-orange)" },
  "15_29": { fill: "var(--uncf-blue-soft)", text: "var(--uncf-ink)", bar: "var(--uncf-blue-mid)" },
  "30_plus": { fill: "var(--uncf-blue)", text: "#fff", bar: "var(--uncf-blue)" },
};

/** The milestone labels, in the design's words. */
export const milestoneLabel: Record<number, string> = {
  12: "12 credits",
  24: "24 credits",
  30: "30 credits · on pace to graduate on time",
};
