"use client";

import { useMemo } from "react";

import { explorerLoader } from "@/components/uncf/layout/explorer-api";
import { useShowStudentCount } from "@/components/uncf/layout/explorer-context";
import { LoadingBlock, MessageCard } from "@/components/uncf/layout/explorer-parts";
import { useCohortFilters } from "@/components/uncf/layout/use-cohort-filters";
import { useApiResource } from "@/hooks/use-api-resource";

import type { CreditsResponse } from "./credits-data";
import { CreditsView } from "./credits-view";

/** The Credit momentum tab: loads the cohort bar's students' credits and draws them. */
export function CreditsTab() {
  const { apiQuery } = useCohortFilters();
  const load = useMemo(() => explorerLoader<CreditsResponse>("/uncf/credit-momentum", apiQuery), [apiQuery]);
  const { resource, retry } = useApiResource(load);
  useShowStudentCount(resource.status !== "success" ? null : resource.data.status === "suppressed" ? "too few" : resource.data.students);

  if (resource.status === "loading") return <CreditsLoading />;
  if (resource.status === "error") {
    return (
      <MessageCard title="The credit numbers couldn’t load." onRetry={retry}>
        {resource.message}
      </MessageCard>
    );
  }
  return <CreditsView data={resource.data} />;
}

/** Grey blocks in the shape of the tab while its numbers load. */
export function CreditsLoading() {
  return (
    <div className="flex flex-col gap-7" aria-busy="true" aria-label="Loading credit momentum">
      <div className="grid gap-5 min-[961px]:grid-cols-3">
        {[0, 1, 2].map((n) => (
          <LoadingBlock key={n} className="h-38" />
        ))}
      </div>
      <div className="grid gap-5 min-[961px]:grid-cols-2">
        <LoadingBlock className="h-90" />
        <LoadingBlock className="h-90" />
      </div>
    </div>
  );
}
