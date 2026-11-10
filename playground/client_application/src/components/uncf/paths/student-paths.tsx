"use client";

import { useMemo } from "react";

import { explorerLoader } from "@/components/uncf/layout/explorer-api";
import { useShowStudentCount } from "@/components/uncf/layout/explorer-context";
import { LoadingBlock, MessageCard } from "@/components/uncf/layout/explorer-parts";
import { useCohortFilters } from "@/components/uncf/layout/use-cohort-filters";
import { useApiResource } from "@/hooks/use-api-resource";

import type { PathsResponse } from "./paths-data";
import { PathsView } from "./paths-view";

/** The Student paths tab: loads the cohort bar's students from the API and draws them. */
export function StudentPaths() {
  const { apiQuery } = useCohortFilters();
  const load = useMemo(() => explorerLoader<PathsResponse>("/uncf/student-paths", apiQuery), [apiQuery]);
  const { resource, retry } = useApiResource(load);
  useShowStudentCount(resource.status === "success" ? resource.data.students : null);

  if (resource.status === "loading") return <PathsLoading />;
  if (resource.status === "error") {
    return (
      <MessageCard title="The student paths couldn’t load." onRetry={retry}>
        {resource.message}
      </MessageCard>
    );
  }
  return <PathsView data={resource.data} />;
}

/** Grey blocks in the shape of the tab while its numbers load. */
export function PathsLoading() {
  return (
    <div className="flex flex-col gap-7" aria-busy="true" aria-label="Loading student paths">
      <div className="grid gap-5 min-[481px]:grid-cols-2 min-[961px]:grid-cols-4">
        {[0, 1, 2, 3].map((n) => (
          <LoadingBlock key={n} className="h-38" />
        ))}
      </div>
      <LoadingBlock className="h-110" />
    </div>
  );
}
