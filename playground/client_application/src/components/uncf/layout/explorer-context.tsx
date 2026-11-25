"use client";

import { createContext, use, useContext, useEffect, useState } from "react";

import { apiRequest } from "@/lib/api-client";

import type { DataLabel } from "./explorer-api";
import { type CohortChoices, sampleCohorts } from "./explorer-config";

/** The tab's student count: a number, "too few" when its numbers are hidden, or null while it loads. */
export type StudentCount = number | "too few" | null;

type ExplorerContextValue = {
  studentCount: StudentCount;
  setStudentCount: (count: StudentCount) => void;
  /** What kind of data the API has loaded, or null until it says. */
  dataLabel: DataLabel | null;
  /** The loaded data's class years, once the API answers; null keeps the sample's years (stories). */
  cohortChoices: Promise<CohortChoices> | null;
};

const ExplorerContext = createContext<ExplorerContextValue | null>(null);

/**
 * Lets the current tab fill in the cohort bar's "Showing N students", and tells every part of the layout what kind
 * of data is loaded. dataLabel fixes the label (stories); left out, it comes from the API's /uncf/health.
 * cohortsFromApi (the app) offers the loaded data's class years from /uncf/options; without it, the sample's years.
 */
export function ExplorerProvider({
  children,
  dataLabel,
  cohortsFromApi = false,
}: {
  children: React.ReactNode;
  dataLabel?: DataLabel;
  cohortsFromApi?: boolean;
}) {
  const [studentCount, setStudentCount] = useState<StudentCount>(null);
  const fetched = useHealthDataLabel(dataLabel === undefined);
  // Asked once, in the browser only: the parts that need the years read the URL too, so they render there anyway.
  const [cohortChoices] = useState(() => (cohortsFromApi && typeof window !== "undefined" ? loadCohortChoices() : null));
  return (
    <ExplorerContext value={{ studentCount, setStudentCount, dataLabel: dataLabel ?? fetched, cohortChoices }}>
      {children}
    </ExplorerContext>
  );
}

/**
 * The loaded data's class years from /uncf/options, oldest first, starting on the API's default class (the latest
 * that isn't provisional). If the API can't answer or has no data, the sample's years, so the pages still draw and
 * show the API's own error.
 */
export async function loadCohortChoices(): Promise<CohortChoices> {
  try {
    const options = await apiRequest<{ cohorts: string[]; default_cohort?: string | null }>("/uncf/options", { cache: "no-store" });
    const years = [...options.cohorts].sort();
    if (!years.length) return sampleCohorts;
    const defaultYear = options.default_cohort && years.includes(options.default_cohort) ? options.default_cohort : years[years.length - 1];
    return { years, defaultYear };
  } catch {
    return sampleCohorts;
  }
}

/**
 * The class years the cohort picker offers. In the app it waits for the API (the component suspends, so its
 * Suspense fallback shows); outside the Explorer layout or in stories, the sample's years.
 */
export function useCohortChoices(): CohortChoices {
  const request = useContext(ExplorerContext)?.cohortChoices ?? null;
  return request ? use(request) : sampleCohorts;
}

/** The API's data_label from /uncf/health, once; null until it answers, or if it can't. */
function useHealthDataLabel(enabled: boolean): DataLabel | null {
  const [label, setLabel] = useState<DataLabel | null>(null);
  useEffect(() => {
    if (!enabled) return;
    let current = true;
    apiRequest<{ data_label?: DataLabel | null }>("/uncf/health", { cache: "no-store" })
      .then((health) => {
        if (current) setLabel(health.data_label ?? null);
      })
      .catch(() => {
        if (current) setLabel(null);
      });
    return () => {
      current = false;
    };
  }, [enabled]);
  return label;
}

/**
 * What kind of data is loaded, so the pages can say so: null while unknown, when nothing about the data is shown
 * rather than a label that could be wrong. Outside the Explorer layout (a story), null.
 */
export function useDataLabel(): DataLabel | null {
  return useContext(ExplorerContext)?.dataLabel ?? null;
}

/** The layout's shared state. Only works inside the Explorer layout. */
export function useExplorer(): ExplorerContextValue {
  const value = useContext(ExplorerContext);
  if (!value) throw new Error("useExplorer needs the Explorer layout (ExplorerProvider) around it.");
  return value;
}

/** The tab's student count, or null outside the Explorer layout (in a story). */
export function useStudentCount(): StudentCount {
  return useContext(ExplorerContext)?.studentCount ?? null;
}

/**
 * Shows this tab's student count in the cohort bar ("Showing 1,114 students"). Pass "too few" when the tab hides its
 * numbers for too few students (under the API's min_students), and null while it loads.
 */
export function useShowStudentCount(count: StudentCount) {
  const { setStudentCount } = useExplorer();
  useEffect(() => {
    setStudentCount(count);
    return () => setStudentCount(null);
  }, [count, setStudentCount]);
}
