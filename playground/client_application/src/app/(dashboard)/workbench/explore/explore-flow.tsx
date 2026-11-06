"use client";

import { useCallback, useMemo, useState } from "react";
import Link from "next/link";
import { CircleX, Table2 } from "lucide-react";

import { EmptyState } from "@/components/empty-state";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button, buttonVariants } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { useContextPanel } from "@/components/workbench/context-panel/context-panel-provider";
import type { DataTableColumn } from "@/components/workbench/explore/data-table";
import { ExplorePage } from "@/components/workbench/explore/explore-page";
import { useApiResource } from "@/hooks/use-api-resource";
import { routes } from "@/lib/routes";
import { fieldId } from "@/services/workbench-mappers";
import { getTableRows } from "@/services/workbench";
import { useWorkbenchData } from "@/app/(dashboard)/workbench/workbench-data";

const TABLE = "student";
const PAGE_SIZE = 25;

type StudentRow = Record<string, unknown>;
type Mode = "plain" | "analyst";

/** Shows a cell's stored value; empty cells stay blank. */
function cellText(value: unknown) {
  return value === null || value === undefined ? "" : String(value);
}

/** Explore over the student table, a page at a time. Filters and comparisons wait for API support. */
export function ExploreFlow() {
  const { columns: dictionary, tables, hasData, refreshTables } = useWorkbenchData();
  const { view, fieldId: selectedFieldId, openField } = useContextPanel();
  const [mode, setMode] = useState<Mode>("plain");
  const [pageIndex, setPageIndex] = useState(0);

  const offset = pageIndex * PAGE_SIZE;
  const loadPage = useCallback(
    () => (hasData ? getTableRows(TABLE, PAGE_SIZE, offset) : Promise.resolve(null)),
    [hasData, offset],
  );
  const { resource: page, retry } = useApiResource(loadPage);

  // Headings come from the dictionary: its name in plain language, the source CSV column for analysts.
  const headings = useMemo(() => {
    const byColumn = new Map<string, { plain: string; analyst: string }>();
    if (dictionary.status !== "success") return byColumn;
    for (const column of dictionary.data) {
      if (column.table !== TABLE) continue;
      byColumn.set(column.column, {
        plain: column.dictionary_name ?? column.column,
        analyst: column.sources[0]?.source_column ?? column.column,
      });
    }
    return byColumn;
  }, [dictionary]);

  const rows = page.status === "success" && page.data ? page.data : null;
  const tableColumns = useMemo<DataTableColumn<StudentRow>[]>(
    () =>
      (rows?.columns ?? []).map((column) => ({
        id: column,
        header: headings.get(column)?.[mode] ?? column,
        accessorFn: (row: StudentRow) => cellText(row[column]),
      })),
    [rows?.columns, headings, mode],
  );

  if (tables.status === "loading") {
    return (
      <p className="flex items-center gap-2 text-sm text-muted-foreground" role="status">
        <Spinner aria-hidden />
        Checking the database…
      </p>
    );
  }
  if (tables.status === "error") {
    return (
      <Alert variant="destructive">
        <CircleX aria-hidden />
        <AlertTitle>The database can&apos;t be reached</AlertTitle>
        <AlertDescription>
          <p>{tables.message}</p>
          <Button variant="outline" onClick={() => void refreshTables()}>Try again</Button>
        </AlertDescription>
      </Alert>
    );
  }
  if (!hasData) {
    return (
      <EmptyState icon={Table2} title="No students to explore yet" description="Upload your files, or load the synthetic mock data from Home.">
        <Link href={routes.workbench} className={buttonVariants({ variant: "outline" })}>Go to Home</Link>
      </EmptyState>
    );
  }

  const totalRows = tables.status === "success"
    ? tables.data.find((table) => table.name === TABLE)?.row_count ?? 0
    : 0;
  // The previous page stays on screen while the next one loads; its offset says which page it is.
  // A null page was loaded before the table list confirmed data, so the real first page is still coming.
  const loading = page.status === "loading" || (page.status === "success" && rows === null) || (rows !== null && rows.offset !== offset);
  const prefix = `${TABLE}.`;
  const selectedColumnId = view === "field" && selectedFieldId.startsWith(prefix) ? selectedFieldId.slice(prefix.length) : null;

  return (
    <ExplorePage<StudentRow>
      mode={{ value: mode, onChange: setMode }}
      filters={[]}
      filterBar={{ onClearAll: () => {} }}
      stats={[]}
      summary={{ children: `${totalRows.toLocaleString("en-US")} synthetic students. Filters and comparisons are coming.` }}
      table={{
        columns: tableColumns,
        data: (rows?.rows ?? []) as StudentRow[],
        caption: "Synthetic students, not real findings",
        selectedColumnId,
        onHeaderClick: (column) => openField(fieldId({ table: TABLE, column })),
        loading,
        error: page.status === "error" ? page.message : undefined,
        onRetry: retry,
        emptyMessage: "No students in the table",
        pagination: {
          pageIndex,
          pageSize: PAGE_SIZE,
          totalRows,
          onPrevious: () => setPageIndex((index) => Math.max(index - 1, 0)),
          onNext: () => setPageIndex((index) => index + 1),
        },
      }}
    />
  );
}
