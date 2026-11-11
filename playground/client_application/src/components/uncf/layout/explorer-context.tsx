"use client";

import { createContext, useContext, useEffect, useState } from "react";

/** The tab's student count: a number, "too few" when its numbers are hidden, or null while it loads. */
export type StudentCount = number | "too few" | null;

type ExplorerContextValue = {
  studentCount: StudentCount;
  setStudentCount: (count: StudentCount) => void;
};

const ExplorerContext = createContext<ExplorerContextValue | null>(null);

/** Lets the current tab fill in the cohort bar's "Showing N students". */
export function ExplorerProvider({ children }: { children: React.ReactNode }) {
  const [studentCount, setStudentCount] = useState<StudentCount>(null);
  return <ExplorerContext value={{ studentCount, setStudentCount }}>{children}</ExplorerContext>;
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
