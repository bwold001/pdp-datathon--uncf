import { type CohortFilterDefinition, cohortFilters, tabFilterDefaults } from "./explorer-config";

/** The cohort bar's choices: each filter's value by id, or null for "All". */
export type CohortFilters = Record<string, string | null>;

/** Anything with get(), like URLSearchParams or the result of useSearchParams(). */
type ReadableParams = Pick<URLSearchParams, "get">;

/** The URL value for "All", used only where a tab starts a filter somewhere else (Student paths: first-time). */
export const ALL = "all";

/** The filters one tab shows, with that tab's own starting values. */
export function cohortFiltersFor(pathname: string): CohortFilterDefinition[] {
  const defaults = Object.entries(tabFilterDefaults).find(([href]) => isOnTab(pathname, href))?.[1] ?? {};
  return cohortFilters
    .filter((definition) => !definition.tabs || definition.tabs.some((href) => isOnTab(pathname, href)))
    .map((definition) => (definition.id in defaults ? { ...definition, defaultValue: defaults[definition.id] } : definition));
}

/** Whether a page is the tab at href or one of its sub-pages. */
function isOnTab(pathname: string, href: string): boolean {
  return pathname === href || pathname.startsWith(`${href}/`);
}

/** Every filter at its default: the cohort's default year, and "All" for the rest. */
export function defaultCohortFilters(definitions: CohortFilterDefinition[] = cohortFilters): CohortFilters {
  return Object.fromEntries(definitions.map((definition) => [definition.id, definition.defaultValue ?? null]));
}

/** Each filter's value from the URL. A value the filter doesn't offer falls back to its default. */
export function readCohortFilters(
  params: ReadableParams,
  definitions: CohortFilterDefinition[] = cohortFilters,
): CohortFilters {
  const filters = defaultCohortFilters(definitions);
  for (const definition of definitions) {
    const value = params.get(definition.id);
    if (value === ALL && !definition.required) filters[definition.id] = null;
    else if (value !== null && definition.options.some((option) => option.value === value)) filters[definition.id] = value;
  }
  return filters;
}

/** The URL query for these filters. Defaults are left out, so an untouched bar keeps the address clean. */
export function cohortFiltersToUrl(
  filters: CohortFilters,
  definitions: CohortFilterDefinition[] = cohortFilters,
): URLSearchParams {
  const params = new URLSearchParams();
  for (const definition of definitions) {
    const value = filters[definition.id] ?? null;
    if (value !== (definition.defaultValue ?? null)) params.set(definition.id, value ?? ALL);
  }
  return params;
}

/**
 * The filters a tab link carries: only the ones set in the URL, so each tab starts the rest at its own defaults.
 * A filter another tab shows (the retention measure) travels too, so it's still set on the way back.
 */
export function carriedFilterQuery(params: ReadableParams): URLSearchParams {
  const carried = new URLSearchParams();
  for (const definition of cohortFilters) {
    const value = params.get(definition.id);
    const valid = (value === ALL && !definition.required) || definition.options.some((option) => option.value === value);
    if (value !== null && valid) carried.set(definition.id, value);
  }
  return carried;
}

/** The query a page sends its API: every filter with a value, defaults included, so the request never guesses. */
export function cohortFiltersToApiQuery(
  filters: CohortFilters,
  definitions: CohortFilterDefinition[] = cohortFilters,
): string {
  const params = new URLSearchParams();
  for (const definition of definitions) {
    const value = filters[definition.id];
    if (value != null) params.set(definition.id, value);
  }
  return params.toString();
}

/** How many filters are set away from their default. */
export function countChangedFilters(
  filters: CohortFilters,
  definitions: CohortFilterDefinition[] = cohortFilters,
): number {
  return definitions.filter((definition) => (filters[definition.id] ?? null) !== (definition.defaultValue ?? null)).length;
}

/** The label shown for a filter's value: "All" when nothing is picked. */
export function filterValueLabel(definition: CohortFilterDefinition, value: string | null): string {
  if (value === null) return "All";
  return definition.options.find((option) => option.value === value)?.label ?? value;
}
