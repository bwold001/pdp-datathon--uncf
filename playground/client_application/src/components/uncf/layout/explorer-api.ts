import { apiRequest } from "@/lib/api-client";

/** What every Explorer endpoint says about its answer. */
export type ExplorerMeta = {
  cohort: string;
  filters: Record<string, string>;
  provisional: boolean;
  min_students: number;
  source: string;
  loaded_at: string;
};

/** The cohort bar's counts: students per cohort year, and per filter value in the chosen cohort. null = under 10. */
export type CohortOptions = {
  cohort: string;
  cohorts: Record<string, number | null>;
  filters: Record<string, Record<string, number | null>>;
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
