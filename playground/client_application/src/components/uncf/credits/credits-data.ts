import type { ExplorerMeta, RetentionBlock } from "@/components/uncf/layout/explorer-api";

/** The answer from GET /uncf/credit-momentum (measures/breakdowns/credit_momentum.py). Hidden numbers (under meta.min_students) are null. */
export type CreditsResponse = {
  meta: ExplorerMeta & {
    /** When retention is measured: a fall term for federal (Fall 2024), "next academic year" for school. */
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
  completion: { counted: number | null; ratio: number | null; status: string } | null;
  /** The cohort's retention, in the measure meta.retention_type names. */
  retention: RetentionBlock | null;
  /** Students who earned at least this many credits; null (and no share) when 1 to 9. */
  milestones: { credits: number; students: number | null; share: number | null }[];
  /** The starting term and the next fall or spring term. */
  terms: { label: string; enrolled: number | null; avg_attempted: number | null; avg_earned: number | null }[];
  tiers: { key: string; label: string; students: number | null; share: number | null; retained: number | null; rate: number | null }[];
  /** The design's page: meaningful progress toward a degree. null when the page is hidden. */
  progress: CreditProgress | null;
};

/** A number of students and their share of a total; both null when it's 1 to 9 students. */
export type CountedStudents = { students: number | null; share: number | null };

/** A year 1 group, in the design's order: on pace, did the minimum but slower, below it, stopped after the first term. */
export type ProgressBandKey = "pace" | "minimum" | "below" | "stopped";

/** Why a student still taking courses ended year 1 under the minimum. */
export type BelowReasonKey = "under" | "failed" | "withdrew" | "not_counted";

/**
 * Meaningful progress toward a degree (measures/breakdowns/credit_progress.py): the Credit momentum design without
 * major. Credits that count are earned credits in college-level (CU) and applicable developmental (CC) courses.
 */
export type CreditProgress = {
  /** The school's rules every number uses. */
  settings: {
    minimum: number;
    degree_credits: number;
    years: number;
    pace: number;
    higher_degree_credits: number;
    higher_pace: number;
    counting_course_types: string[];
  };
  /** The term "stopped" looks at, when every student under the minimum shares it, e.g. Spring 2023. */
  next_term: string | null;
  /** The academic year counted as year 2, e.g. 2023-24. */
  year_two: string;
  /** Did the minimum in year 1, of every student. */
  minimum: CountedStudents;
  /** On pace for the degree total, of every student. */
  pace: CountedStudents;
  /** On pace if the degree total were higher_degree_credits. */
  higher_pace: CountedStudents;
  /** Still on pace after two years; not yet observable while year 2 isn't in the data. */
  two_year_pace: CountedStudents & { status: "ok" | "not_yet_observable" };
  bands: (CountedStudents & { key: ProgressBandKey; retention: { students: number | null; retained: number | null; rate: number | null } })[];
  /** Under the minimum, but their next term isn't in the data yet (or their start term is unknown), so in no group. */
  unsorted: number | null;
  below: {
    students: number | null;
    /** Each reason's share is of the students below the minimum. */
    reasons: (CountedStudents & { key: BelowReasonKey })[];
    /** Below the minimum with no reason that fits: incomplete or missing grades, or an even split. */
    unexplained: number | null;
  };
  /** What the students who did the minimum in year 1 did in year 2; shares are of them. */
  year_two_follow_up: {
    status: "ok" | "not_yet_observable";
    students: number | null;
    again: CountedStudents;
    kept_taking_courses: CountedStudents;
    no_courses: CountedStudents;
  };
  /** Did the minimum in both years, of every student. */
  both_years: CountedStudents;
};
