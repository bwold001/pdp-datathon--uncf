"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useMemo } from "react";

import {
  type CohortFilters,
  cohortFiltersFor,
  cohortFiltersToApiQuery,
  cohortFiltersToUrl,
  defaultCohortFilters,
  readCohortFilters,
} from "./cohort-filters";
import { cohortFilters } from "./explorer-config";

const allFilterIds = new Set(cohortFilters.map((definition) => definition.id));

/**
 * The cohort bar's filters on this tab, read from and written to the URL, so a view can be shared and Back undoes a
 * change. It reads the URL, so render the component that calls it inside <Suspense>.
 */
export function useCohortFilters() {
  const searchParams = useSearchParams();
  const pathname = usePathname();
  const router = useRouter();

  const definitions = useMemo(() => cohortFiltersFor(pathname), [pathname]);
  const filters = useMemo(() => readCohortFilters(searchParams, definitions), [searchParams, definitions]);
  const apiQuery = useMemo(() => cohortFiltersToApiQuery(filters, definitions), [filters, definitions]);

  /** Go to the same page with these filters. keep says which other query values stay. */
  function navigate(next: CohortFilters, keep: (key: string) => boolean) {
    const params = cohortFiltersToUrl(next, definitions);
    searchParams.forEach((value, key) => {
      if (!params.has(key) && !definitions.some((definition) => definition.id === key) && keep(key)) params.append(key, value);
    });
    const query = params.toString();
    router.push(query ? `${pathname}?${query}` : pathname, { scroll: false });
  }

  return {
    /** The filters this tab shows, with its own starting values. */
    definitions,
    /** Each filter's value by id; null means "All". */
    filters,
    /** The filters as query values for the page's API request, defaults included. */
    apiQuery,
    /** Set one filter; null clears it to "All". Filters this tab doesn't show and the page's own values stay. */
    setFilter: (id: string, value: string | null) => navigate({ ...filters, [id]: value }, () => true),
    /**
     * Every "Add filter" filter back to its default. The class year, enrollment type, retention measure, filters
     * this tab doesn't show and the page's own values stay.
     */
    clearMenuFilters: () => {
      const cleared = definitions.filter((definition) => definition.place === "menu").map((definition) => [definition.id, definition.defaultValue ?? null]);
      navigate({ ...filters, ...Object.fromEntries(cleared) }, () => true);
    },
    /** Every filter back to its default, on every tab. The page's own query values (a sort order) stay. */
    reset: () => navigate(defaultCohortFilters(definitions), (key) => !allFilterIds.has(key)),
  };
}
