import { apiRequest } from "@/lib/api-client";

/** What every Explorer endpoint says about its answer. */
export type ExplorerMeta = {
  cohort: string;
  filters: Record<string, string>;
  /** Which retention measure the answer's retention numbers use: the PDP flag (school) or fall to fall (federal). */
  retention_type: RetentionType;
  provisional: boolean;
  min_students: number;
  source: string;
  loaded_at: string;
};

/** One grade group a page shows, its grade points, and whether the page's rule counts it. */
export type GradeScaleRow = {
  /** The group a page shows, e.g. "D" or "C or higher". */
  grade: string;
  /** The grade points or code in it, e.g. "0.7 to under 1.7 (D-, D, D+)" or "the code W (withdrew)". */
  points: string;
  /** Under the page's rule: a DFW on the DFW page, a pass on the Gateway page. */
  counted: boolean;
};

/** The grade groups a page shows (measures/breakdowns/grade_scale.py), best first, and the codes left out. */
export type GradeScale = { grades: GradeScaleRow[]; left_out: string };

/** school: the PDP retention flag ("Returned here"). federal: fall to fall ("Back next fall"). */
export type RetentionType = "school" | "federal";

/** One retention number: students retained of the students counted, null under 10. */
export type RetentionBlock = {
  type: RetentionType;
  status: string;
  retained: number | null;
  students: number | null;
  numerator: number | null;
  denominator: number | null;
  rate: number | null;
  n_excluded: number | null;
  n_out_of_scope: number | null;
};

/** The cohort bar's counts: students per cohort year, and per filter value in the chosen cohort. null = under 10. */
export type CohortOptions = {
  cohort: string;
  cohorts: Record<string, number | null>;
  filters: Record<string, Record<string, number | null>>;
  /** Each filter's name in the API's words. */
  labels: Record<string, string>;
  retention_types: RetentionType[];
  min_students: number;
  source: string;
  loaded_at: string;
};

/**
 * A loader for one Explorer endpoint, e.g. explorerLoader<PathsResponse>("/uncf/student-paths", apiQuery).
 * Wrap it in useMemo so useApiResource only reloads when the query changes.
 */
export function explorerLoader<T>(path: string, query: string): () => Promise<T> {
  return () => apiRequest<T>(query ? `${path}?${query}` : path, { cache: "no-store" });
}
