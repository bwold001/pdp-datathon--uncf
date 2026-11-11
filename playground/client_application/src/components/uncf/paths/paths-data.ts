import type { ExplorerMeta, RetentionBlock } from "@/components/uncf/layout/explorer-api";

/**
 * Where a student is in one term: took a course here, earned a credential here in an earlier year (and took no course
 * here), enrolled only at another college, or no record.
 */
export type PathStatus = "here" | "credential" | "elsewhere" | "stopped";

/** One term's counts. null means a group under meta.min_students, hidden. */
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

/** Students moving from one status to another between two terms. null under meta.min_students. */
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

/**
 * The students someone clicked in the flow: those with a status in the second term, in the third, or both (one band).
 * A bar sets one term, a band between the second and third terms sets both, and a band from the entering class sets
 * the second term's.
 */
export type PathFocus = { next: PathStatus | null; year2: PathStatus | null };

/** The focused students: how many, and how many had each status in the second and third terms. null under meta.min_students. */
export type FocusCounts = {
  students: number | null;
  next: Record<PathStatus, number | null>;
  year2: Record<PathStatus, number | null>;
  /** Of them, how many had no record in the second term and took a course here in the third. */
  returned: number | null;
};

/** Whether two focuses pick the same students. */
export function sameFocus(a: PathFocus | null, b: PathFocus | null): boolean {
  return a?.next === b?.next && a?.year2 === b?.year2;
}

/** Students moving from one status to another between the second and third terms: 0 when the API lists no such move. */
export function moveCount(data: PathsResponse, from: PathStatus, to: PathStatus): number | null {
  const move = data.moves?.find((m) => m.from === from && m.to === to);
  return move ? move.students : 0;
}

/** How many of the focused students moved from one status to the other: 0 when the focus leaves that move out. */
export function focusedMove(data: PathsResponse, focus: PathFocus, from: PathStatus, to: PathStatus): number | null {
  if ((focus.next && focus.next !== from) || (focus.year2 && focus.year2 !== to)) return 0;
  return moveCount(data, from, to);
}

/**
 * The focused students' counts, worked out from the API's columns and moves, so they add up with the whole flow. A
 * second-term bar counts its column (students whose third term isn't in the data yet too); its third-term split, and
 * everything about a third-term bar or a band, comes from the moves.
 */
export function focusCounts(data: PathsResponse, focus: PathFocus): FocusCounts {
  const columns = data.columns!;
  const students =
    focus.next && focus.year2
      ? moveCount(data, focus.next, focus.year2)
      : focus.next
        ? columns.next[focus.next]
        : columns.year2[focus.year2!];
  const split = (picked: PathStatus | null, count: (status: PathStatus) => number | null) =>
    Object.fromEntries(pathStatuses.map((status) => [status, picked ? (status === picked ? students : 0) : count(status)])) as Record<
      PathStatus,
      number | null
    >;
  return {
    students,
    next: split(focus.next, (status) => focusedMove(data, focus, status, focus.year2!)),
    year2: split(focus.year2, (status) => focusedMove(data, focus, focus.next!, status)),
    returned: focusedMove(data, focus, "stopped", "here"),
  };
}

/** The words for a focus, in the flow's hover text: "Stopped out by Spring 2024", "Returned after a term away". */
export function focusPhrase(data: PathsResponse, focus: PathFocus): string {
  const names = termNames(data);
  if (focus.next && focus.year2) return secondMovePhrase(focus.next, focus.year2, names.next, names.year2);
  return focus.next ? firstMovePhrase(focus.next, names.next) : firstMovePhrase(focus.year2!, names.year2);
}

/** The hover text for a band from the entering class into the second term, or for a bar in a term. */
export function firstMovePhrase(status: PathStatus, term: string): string {
  if (status === "here") return `Enrolled in ${term}`;
  if (status === "credential") return `Earned a credential by ${term}`;
  if (status === "elsewhere") return `Transferred out by ${term}`;
  return `Stopped out by ${term}`;
}

/** The hover text for a band from the second term into the third, in the design's words where it has them. */
export function secondMovePhrase(before: PathStatus, after: PathStatus, next: string, year2: string): string {
  if (before === "here" && after === "here") return `Stayed enrolled to ${year2}`;
  if (before === "here" && after === "elsewhere") return `Enrolled in ${next}, transferred by ${year2}`;
  if (before === "here" && after === "stopped") return `Enrolled in ${next}, stopped out by ${year2}`;
  if (before === "elsewhere" && after === "elsewhere") return "Still transferred out";
  if (before === "elsewhere" && after === "here") return `Came back from another college by ${year2}`;
  if (before === "elsewhere" && after === "stopped") return `Transferred out in ${next}, no record in ${year2}`;
  if (before === "stopped" && after === "here") return "Returned after a term away";
  if (before === "stopped" && after === "elsewhere") return `No record in ${next}, at another college in ${year2}`;
  if (before === "here" && after === "credential") return `Enrolled in ${next}, earned a credential by ${year2}`;
  if (before === "elsewhere" && after === "credential") return `Transferred out in ${next}, earned a credential here by ${year2}`;
  if (before === "stopped" && after === "credential") return `No record in ${next}, earned a credential by ${year2}`;
  if (before === "credential" && after === "credential") return "Still holds a credential";
  if (before === "credential" && after === "here") return `Earned a credential, took a course here in ${year2}`;
  if (before === "credential" && after === "elsewhere") return `Earned a credential, at another college in ${year2}`;
  if (before === "credential") return `Earned a credential, no record in ${year2}`;
  return "Still stopped out";
}

/** A focus from URL values; null when neither is a status. */
export function readPathFocus(next: string | null, year2: string | null): PathFocus | null {
  const status = (value: string | null) => (pathStatuses.includes(value as PathStatus) ? (value as PathStatus) : null);
  const focus = { next: status(next), year2: status(year2) };
  return focus.next || focus.year2 ? focus : null;
}
