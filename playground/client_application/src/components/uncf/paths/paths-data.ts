import type { ExplorerMeta, RetentionBlock } from "@/components/uncf/layout/explorer-api";

/**
 * Where a student is in one term: took a course here, earned a credential here in an earlier year (and took no course
 * here), enrolled only at another college, or no record.
 */
export type PathStatus = "here" | "credential" | "elsewhere" | "stopped";

/** One term's counts. null means a group under 10 students, hidden. */
export type TermCounts = {
  /** The term's place in the path (1 is the term after the start), and its name when every student shares it. */
  position: number;
  label: string | null;
  here: number | null;
  credential: number | null;
  elsewhere: number | null;
  /** Here or at another college that term (a credential alone isn't enrollment). */
  anywhere: number | null;
  stopped: number | null;
  /** Students whose term isn't in the data yet (a recent class). */
  not_observed: number | null;
  /** Each status's share of the entering students, from the API. null where the count is hidden. */
  shares: Record<PathStatus | "anywhere", number | null>;
};

/** Students moving from one status to another between two terms. null under 10. */
export type PathMove = { from: PathStatus; to: PathStatus; students: number | null };

/** The answer from GET /uncf/student-paths (measures/breakdowns/student_paths.py). */
export type PathsResponse = {
  meta: ExplorerMeta & {
    /** The filters the answer used, e.g. { enrollment_type: "First-time" }. */
    filters: Record<string, string>;
    /** The three terms' names when every student started in the same term; null when start terms are mixed. */
    terms: { entered: string; next: string; year2: string } | null;
    term_labels: string[] | null;
    group_by: string | null;
  };
  status: "ok" | "suppressed";
  students: number | null;
  /** Students left out because their starting term is unknown. */
  left_out: number | null;
  /** The cohort's retention, in the measure meta.retention_type names. */
  retention?: RetentionBlock | null;
  columns: { next: TermCounts; year2: TermCounts } | null;
  /** Every term after the start, in order (columns holds the first two). */
  path?: TermCounts[] | null;
  /** Moves from the second term to the third, one per pair of statuses. */
  moves: PathMove[] | null;
  /** Moves between each pair of neighbouring terms in path. */
  moves_by_step?: { from_position: number; to_position: number; moves: PathMove[] }[] | null;
  /** The same answer per value of meta.group_by, when one is asked for. */
  groups?: unknown[] | null;
  transfers: { students: number | null; four_year: number | null; two_year: number | null; other: number | null } | null;
};

/** The order statuses are drawn and listed in. */
export const pathStatuses: PathStatus[] = ["here", "credential", "elsewhere", "stopped"];

/** Each status's name and colors, from the design (credential is ours: the design has no such status). */
export const statusStyle: Record<PathStatus, { label: string; short: string; node: string; band: string }> = {
  here: { label: "Enrolled here", short: "Enrolled", node: "var(--uncf-blue)", band: "var(--uncf-blue-soft)" },
  credential: { label: "Earned a credential", short: "Credential", node: "var(--uncf-teal)", band: "var(--uncf-teal-soft)" },
  elsewhere: { label: "Transferred out", short: "Transferred", node: "var(--uncf-grey)", band: "var(--uncf-grey-soft)" },
  stopped: { label: "Stopped out", short: "Stopped out", node: "var(--uncf-orange)", band: "var(--uncf-peach)" },
};

/** Who the answer counts, for headings: "First-time", "Transfer-in", or "All enrollment types". */
export function studentsLabel(data: PathsResponse): string {
  const type = data.meta.filters.enrollment_type;
  if (!type) return "All enrollment types";
  return type === "UNKNOWN" ? "Enrollment type unknown" : type;
}

/** The three terms' names: real ones (Fall 2023) when every student shares them, else their place in the path. */
export function termNames(data: PathsResponse) {
  const terms = data.meta.terms;
  return {
    entered: terms?.entered ?? null,
    next: terms?.next ?? "the next term",
    year2: terms?.year2 ?? "the term after",
    /** Short name for the last term in tile labels, e.g. "Fall 2024" or "year 2". */
    year2Short: terms?.year2 ?? "year 2",
  };
}
