"use client";

import { useMemo } from "react";

import { type Resource, useApiResource } from "@/hooks/use-api-resource";

/**
 * useApiResource for an Explorer endpoint, plus `current`: false while a new filter's answer is still loading and
 * `resource` still holds the last filters' answer. Report a count only when it's current, so the cohort bar never
 * pairs the old number with the new filters.
 */
export function useExplorerResource<T>(load: () => Promise<T>) {
  // Each answer remembers the loader (the filters) it came from.
  const tagged = useMemo(() => () => load().then((data) => ({ load, data })), [load]);
  const { resource: answer, retry } = useApiResource(tagged);
  const resource = useMemo<Resource<T>>(() => (answer.status === "success" ? { status: "success", data: answer.data.data } : answer), [answer]);
  const current = answer.status !== "success" || answer.data.load === load;
  return { resource, retry, current };
}
