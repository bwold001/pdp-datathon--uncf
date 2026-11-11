"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useMemo } from "react";

import { explorerLoader } from "@/components/uncf/layout/explorer-api";
import { useShowStudentCount } from "@/components/uncf/layout/explorer-context";
import { LoadingBlock, MessageCard } from "@/components/uncf/layout/explorer-parts";
import { useCohortFilters } from "@/components/uncf/layout/use-cohort-filters";
import { useApiResource } from "@/hooks/use-api-resource";

import { type PathFocus, type PathsResponse, readPathFocus } from "./paths-data";
import { PathsView } from "./paths-view";

/** The Student paths tab: loads the cohort bar's students from the API and draws them. */
export function StudentPaths() {
  const { apiQuery } = useCohortFilters();
  const load = useMemo(() => explorerLoader<PathsResponse>("/uncf/student-paths", apiQuery), [apiQuery]);
  const { resource, retry } = useApiResource(load);
  useShowStudentCount(resource.status !== "success" ? null : resource.data.status === "suppressed" ? "too few" : resource.data.students);
  const [focus, setFocus] = usePathFocus();

  if (resource.status === "loading") return <PathsLoading />;
  if (resource.status === "error") {
    return (
      <MessageCard title="The student paths couldn’t load." onRetry={retry}>
        {resource.message}
      </MessageCard>
    );
  }
  return <PathsView data={resource.data} focus={focus} onFocusChange={setFocus} />;
}

// The URL keys for the students clicked in the flow: their status in the second term and in the third.
const FOCUS_NEXT = "path_next";
const FOCUS_YEAR2 = "path_year2";

/**
 * The students clicked in the flow, kept in the URL like the cohort bar's filters, so a focused view can be shared and
 * Back undoes a click. It's this tab's own value: tab links don't carry it.
 */
function usePathFocus(): [PathFocus | null, (focus: PathFocus | null) => void] {
  const searchParams = useSearchParams();
  const pathname = usePathname();
  const router = useRouter();
  const focus = useMemo(() => readPathFocus(searchParams.get(FOCUS_NEXT), searchParams.get(FOCUS_YEAR2)), [searchParams]);

  function setFocus(next: PathFocus | null) {
    const params = new URLSearchParams(searchParams.toString());
    params.delete(FOCUS_NEXT);
    params.delete(FOCUS_YEAR2);
    if (next?.next) params.set(FOCUS_NEXT, next.next);
    if (next?.year2) params.set(FOCUS_YEAR2, next.year2);
    const query = params.toString();
    router.push(query ? `${pathname}?${query}` : pathname, { scroll: false });
  }

  return [focus, setFocus];
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
