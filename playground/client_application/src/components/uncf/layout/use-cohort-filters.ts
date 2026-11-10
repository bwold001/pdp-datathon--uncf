"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useMemo } from "react";

import { type CohortFilters, cohortFiltersToApiQuery, cohortFiltersToUrl, defaultCohortFilters, readCohortFilters } from "./cohort-filters";
import { cohortFilters } from "./explorer-config";

const filterIds = new Set(cohortFilters.map((definition) => definition.id));

/**
 * The cohort bar's filters, read from and written to the URL, so a view can be shared and Back undoes a change.
 * It reads the URL, so render the component that calls it inside <Suspense>.
 */
export function useCohortFilters() {
  const searchParams = useSearchParams();
  const pathname = usePathname();
  const router = useRouter();

  const filters = useMemo(() => readCohortFilters(searchParams), [searchParams]);
  const apiQuery = useMemo(() => cohortFiltersToApiQuery(filters), [filters]);

  /** Go to the same page with these filters, keeping the page's own query values (a sort order, say). */
  function navigate(next: CohortFilters) {
    const params = cohortFiltersToUrl(next);
    searchParams.forEach((value, key) => {
      if (!filterIds.has(key)) params.append(key, value);
    });
    const query = params.toString();
    router.push(query ? `${pathname}?${query}` : pathname, { scroll: false });
  }

  return {
    /** Each filter's value by id; null means "All". */
    filters,
    /** The filters as query values for the page's API request, defaults included. */
    apiQuery,
    /** Set one filter; null clears it to "All". */
    setFilter: (id: string, value: string | null) => navigate({ ...filters, [id]: value }),
    /** Every filter back to its default. */
    reset: () => navigate(defaultCohortFilters()),
  };
}
