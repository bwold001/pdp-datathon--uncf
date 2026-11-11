"use client";

import { useMemo } from "react";

import { type CohortFilters, filterValueLabel } from "@/components/uncf/layout/cohort-filters";
import { explorerLoader } from "@/components/uncf/layout/explorer-api";
import { cohortFilters } from "@/components/uncf/layout/explorer-config";
import { useShowStudentCount } from "@/components/uncf/layout/explorer-context";
import { LoadingBlock, MessageCard } from "@/components/uncf/layout/explorer-parts";
import { useCohortFilters } from "@/components/uncf/layout/use-cohort-filters";
import { useExplorerResource } from "@/components/uncf/layout/use-explorer-resource";

import type { GatewayResponse } from "./gateway-data";
import { GatewayView } from "./gateway-view";

/** The Gateway courses tab: loads the cohort bar's students' gateway outcomes and draws them. */
export function GatewayTab() {
  const { apiQuery, filters } = useCohortFilters();
  const groupLabel = useMemo(() => describeGroup(filters), [filters]);
  const load = useMemo(() => explorerLoader<GatewayResponse>("/uncf/gateway", apiQuery), [apiQuery]);
  const { resource, retry, current } = useExplorerResource(load);
  useShowStudentCount(resource.status !== "success" || !current ? null : resource.data.status === "suppressed" ? "too few" : resource.data.students);

  if (resource.status === "loading") return <GatewayLoading />;
  if (resource.status === "error") {
    return (
      <MessageCard title="The gateway courses couldn’t load." onRetry={retry}>
        {resource.message}
      </MessageCard>
    );
  }
  return <GatewayView data={resource.data} groupLabel={groupLabel} />;
}

/** The student filters as a group name, e.g. "Pell (year 1): Pell recipient"; null when none is set. */
export function describeGroup(filters: CohortFilters): string | null {
  // Required filters (the cohort year, the retention measure) always have a value, so they don't pick a group.
  const parts = cohortFilters
    .filter((definition) => !definition.required && filters[definition.id] != null)
    .map((definition) => `${definition.label}: ${filterValueLabel(definition, filters[definition.id])}`);
  return parts.length ? parts.join(" + ") : null;
}

/** Grey blocks in the shape of the tab while its numbers load. */
export function GatewayLoading() {
  return (
    <div className="flex flex-col gap-7" aria-busy="true" aria-label="Loading gateway courses">
      <LoadingBlock className="h-130" />
      <LoadingBlock className="h-64" />
    </div>
  );
}
