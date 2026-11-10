import type { ExplorerMeta } from "@/components/uncf/layout/explorer-api";

/** Where a student is in one term: took a course here, enrolled only at another college, or no record. */
export type PathStatus = "here" | "elsewhere" | "stopped";

/** One term's counts. null means a group under 10 students, hidden. */
export type TermCounts = {
  here: number | null;
  elsewhere: number | null;
  anywhere: number | null;
  stopped: number | null;
  /** Students whose term isn't in the data yet (a recent class). */
  not_observed: number | null;
};

/** The answer from GET /uncf/student-paths (measures/breakdowns/student_paths.py). */
export type PathsResponse = {
  meta: ExplorerMeta & {
    /** The three terms' names when every student started in the same term; null when start terms are mixed. */
    terms: { entered: string; next: string; year2: string } | null;
  };
  status: "ok" | "suppressed";
  students: number | null;
  /** Students left out because their starting term is unknown. */
  left_out: number | null;
  columns: { next: TermCounts; year2: TermCounts } | null;
  /** Moves from the second term to the third, one per pair of statuses. */
  moves: { from: PathStatus; to: PathStatus; students: number | null }[] | null;
  transfers: { students: number | null; four_year: number | null; two_year: number | null; other: number | null } | null;
};

/** The order statuses are drawn and listed in. */
export const pathStatuses: PathStatus[] = ["here", "elsewhere", "stopped"];

/** Each status's name and colors, from the design. */
export const statusStyle: Record<PathStatus, { label: string; short: string; node: string; band: string }> = {
  here: { label: "Enrolled here", short: "Enrolled", node: "var(--uncf-blue)", band: "var(--uncf-blue-soft)" },
  elsewhere: { label: "Transferred out", short: "Transferred", node: "var(--uncf-grey)", band: "var(--uncf-grey-soft)" },
  stopped: { label: "Stopped out", short: "Stopped out", node: "var(--uncf-orange)", band: "var(--uncf-peach)" },
};

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
