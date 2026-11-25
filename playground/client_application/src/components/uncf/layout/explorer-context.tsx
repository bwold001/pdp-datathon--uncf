"use client";

import { createContext, useContext, useEffect, useState } from "react";

import { apiRequest } from "@/lib/api-client";

import type { DataLabel } from "./explorer-api";

/** The tab's student count: a number, "too few" when its numbers are hidden, or null while it loads. */
export type StudentCount = number | "too few" | null;

type ExplorerContextValue = {
  studentCount: StudentCount;
  setStudentCount: (count: StudentCount) => void;
  /** What kind of data the API has loaded, or null until it says. */
  dataLabel: DataLabel | null;
};

const ExplorerContext = createContext<ExplorerContextValue | null>(null);

/**
 * Lets the current tab fill in the cohort bar's "Showing N students", and tells every part of the layout what kind
 * of data is loaded. dataLabel fixes the label (stories); left out, it comes from the API's /uncf/health.
 */
export function ExplorerProvider({ children, dataLabel }: { children: React.ReactNode; dataLabel?: DataLabel }) {
  const [studentCount, setStudentCount] = useState<StudentCount>(null);
  const fetched = useHealthDataLabel(dataLabel === undefined);
  return (
    <ExplorerContext value={{ studentCount, setStudentCount, dataLabel: dataLabel ?? fetched }}>{children}</ExplorerContext>
  );
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
