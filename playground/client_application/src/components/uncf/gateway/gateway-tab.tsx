"use client";

import { useMemo } from "react";

import { explorerLoader } from "@/components/uncf/layout/explorer-api";
import { useShowStudentCount } from "@/components/uncf/layout/explorer-context";
import { LoadingBlock, MessageCard } from "@/components/uncf/layout/explorer-parts";
import { useCohortFilters } from "@/components/uncf/layout/use-cohort-filters";
import { useApiResource } from "@/hooks/use-api-resource";

import type { GatewayResponse } from "./gateway-data";
import { GatewayView } from "./gateway-view";

/** The Gateway courses tab: loads the cohort bar's students' gateway outcomes and draws them. */
export function GatewayTab() {
  const { apiQuery } = useCohortFilters();
  const load = useMemo(() => explorerLoader<GatewayResponse>("/uncf/gateway", apiQuery), [apiQuery]);
  const { resource, retry } = useApiResource(load);
  useShowStudentCount(resource.status !== "success" ? null : resource.data.status === "suppressed" ? "too few" : resource.data.students);

  if (resource.status === "loading") return <GatewayLoading />;
  if (resource.status === "error") {
    return (
      <MessageCard title="The gateway courses couldn’t load." onRetry={retry}>
        {resource.message}
      </MessageCard>
    );
  }
  return <GatewayView data={resource.data} />;
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
