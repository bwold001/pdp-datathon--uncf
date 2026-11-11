"use client";

import { useSearchParams } from "next/navigation";
import { useMemo } from "react";

import { carriedFilterQuery, filterValueLabel } from "@/components/uncf/layout/cohort-filters";
import { explorerLoader } from "@/components/uncf/layout/explorer-api";
import { useShowStudentCount } from "@/components/uncf/layout/explorer-context";
import { LoadingBlock, MessageCard } from "@/components/uncf/layout/explorer-parts";
import { useCohortFilters } from "@/components/uncf/layout/use-cohort-filters";
import { useExplorerResource } from "@/components/uncf/layout/use-explorer-resource";

import type { CreditsResponse } from "./credits-data";
import { CreditsView, ProgressIntro } from "./credits-view";

/** The Credit momentum tab: loads the cohort bar's students' progress and draws it. */
export function CreditsTab() {
  const { apiQuery, definitions, filters, clearMenuFilters } = useCohortFilters();
  const searchParams = useSearchParams();
  const load = useMemo(() => explorerLoader<CreditsResponse>("/uncf/credit-momentum", apiQuery), [apiQuery]);
  const { resource, retry, current } = useExplorerResource(load);
  useShowStudentCount(resource.status !== "success" || !current ? null : resource.data.status === "suppressed" ? "too few" : resource.data.students);

  // The "Add filter" filters someone set (the bar's chips), in words. The bar's sentence already names the class year
  // and enrollment type, and Clear filters keeps those, as the bar's Clear filters does.
  const picked = definitions.filter((definition) => definition.place === "menu" && (filters[definition.id] ?? null) !== (definition.defaultValue ?? null));
  const filterText = picked.map((definition) => filterValueLabel(definition, filters[definition.id] ?? null)).join(" · ");

  if (resource.status === "loading") return <CreditsLoading />;
  if (resource.status === "error") {
    return (
      <>
        <ProgressIntro />
        <MessageCard title="The credit numbers couldn’t load." onRetry={retry}>
          {resource.message}
        </MessageCard>
      </>
    );
  }
  return (
    <CreditsView
      data={resource.data}
      filters={picked.length ? { text: filterText, onClear: clearMenuFilters } : undefined}
      linkQuery={carriedFilterQuery(searchParams).toString()}
    />
  );
}

/** The heading, then grey blocks in the shape of the tab while its numbers load. */
export function CreditsLoading() {
  return (
    <div className="flex flex-col gap-6" aria-busy="true" aria-label="Loading credit momentum">
      <ProgressIntro />
      <div className="grid gap-5 min-[961px]:grid-cols-2">
        <LoadingBlock className="h-64" />
        <LoadingBlock className="h-64" />
      </div>
      <LoadingBlock className="h-90" />
    </div>
  );
}
