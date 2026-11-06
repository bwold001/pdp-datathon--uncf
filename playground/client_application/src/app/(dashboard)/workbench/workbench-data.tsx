"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

import type { GuideField } from "@/components/workbench/shared/dictionary-types";
import { useApiResource, type Resource } from "@/hooks/use-api-resource";
import { usePipelineRun, type PipelineRun } from "@/hooks/use-pipeline-run";
import { describeError } from "@/lib/errors";
import { hasStudentRows, toGuideField } from "@/services/workbench-mappers";
import { listColumns, listTables, type ColumnDefinition, type RunRequest, type TableSummary } from "@/services/workbench";

type WorkbenchData = {
  /** The dictionary's columns as the server sends them; kind detection reads their sources. */
  columns: Resource<ColumnDefinition[]>;
  /** The same columns as the field guide and context panel show them. */
  fields: GuideField[];
  tables: Resource<TableSummary[]>;
  /** True once the student table holds rows. */
  hasData: boolean;
  retryColumns: () => void;
  /** Reload the table list, keeping the current one on screen until it arrives. */
  refreshTables: () => Promise<void>;
  /** The current load run, kept here so it finishes and refreshes the tables even if its page closes. */
  run: PipelineRun;
};

const WorkbenchDataContext = createContext<WorkbenchData | null>(null);

/** Loads the dictionary and the table list once for every workbench page. */
export function WorkbenchDataProvider({ children }: { children: ReactNode }) {
  const loadColumns = useCallback(() => listColumns().then((list) => list.columns), []);
  const { resource: columns, retry: retryColumns } = useApiResource(loadColumns);

  const [tables, setTables] = useState<Resource<TableSummary[]>>({ status: "loading" });
  const refreshTables = useCallback(
    () =>
      listTables()
        .then((list) => setTables({ status: "success", data: list.tables }))
        .catch((error: unknown) => setTables({ status: "error", message: describeError(error) })),
    [],
  );
  useEffect(() => {
    refreshTables();
  }, [refreshTables]);

  const { state: runState, start: startLoad, reset: resetRun } = usePipelineRun();
  const startRun = useCallback(
    async (request?: RunRequest) => {
      const outcome = await startLoad(request);
      if (outcome.status === "succeeded") await refreshTables();
      return outcome;
    },
    [startLoad, refreshTables],
  );

  const value = useMemo<WorkbenchData>(() => {
    const fields = columns.status === "success" ? columns.data.map(toGuideField) : [];
    const hasData = tables.status === "success" && hasStudentRows(tables.data);
    const run = { state: runState, start: startRun, reset: resetRun };
    return { columns, fields, tables, hasData, retryColumns, refreshTables, run };
  }, [columns, tables, retryColumns, refreshTables, runState, startRun, resetRun]);

  return <WorkbenchDataContext.Provider value={value}>{children}</WorkbenchDataContext.Provider>;
}

/** The workbench's shared dictionary and table state. */
export function useWorkbenchData() {
  const data = useContext(WorkbenchDataContext);
  if (!data) throw new Error("useWorkbenchData must be used within WorkbenchDataProvider.");
  return data;
}
