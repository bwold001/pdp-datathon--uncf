"use client";

import { createContext, useContext, useEffect, useState } from "react";

type ExplorerContextValue = {
  studentCount: number | null;
  setStudentCount: (count: number | null) => void;
};

const ExplorerContext = createContext<ExplorerContextValue | null>(null);

/** Lets the current tab fill in the cohort bar's "Showing N students". */
export function ExplorerProvider({ children }: { children: React.ReactNode }) {
  const [studentCount, setStudentCount] = useState<number | null>(null);
  return <ExplorerContext value={{ studentCount, setStudentCount }}>{children}</ExplorerContext>;
}

/** The layout's shared state. Only works inside the Explorer layout. */
export function useExplorer(): ExplorerContextValue {
  const value = useContext(ExplorerContext);
  if (!value) throw new Error("useExplorer needs the Explorer layout (ExplorerProvider) around it.");
  return value;
}

/** Shows this tab's student count in the cohort bar ("Showing 1,114 students"). Pass null while it loads. */
export function useShowStudentCount(count: number | null) {
  const { setStudentCount } = useExplorer();
  useEffect(() => {
    setStudentCount(count);
    return () => setStudentCount(null);
  }, [count, setStudentCount]);
}
