"use client";

import type { ComponentProps, ReactNode } from "react";
import { SearchX } from "lucide-react";
import { columnVisibilityFeature, tableFeatures, useTable, type ColumnDef, type ColumnVisibilityState, type RowData } from "@tanstack/react-table";
import { EmptyState } from "@/components/empty-state";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { TablePagination } from "@/components/workbench/explore/table-pagination";

const features = tableFeatures({ columnVisibilityFeature });
const visibleColumns: ColumnVisibilityState = {};
export type DataTableColumn<T extends RowData> = ColumnDef<typeof features, T>;
export type DataTableProps<T extends RowData> = {
  columns: DataTableColumn<T>[];
  data: T[];
  caption: string;
  columnVisibility?: ColumnVisibilityState;
  selectedColumnId?: string | null;
  onHeaderClick?: (columnId: string) => void;
  loading?: boolean;
  error?: string;
  onRetry?: () => void;
  emptyMessage?: string;
  pagination?: ComponentProps<typeof TablePagination>;
};

/** Keeps loading, failed and empty rows separate from normal table rendering. */
function BodyRows({ children, columnCount, hasRows, loading, error, onRetry, emptyMessage }: {
  children: ReactNode;
  columnCount: number;
  hasRows: boolean;
  loading: boolean;
  error?: string;
  onRetry?: () => void;
  emptyMessage: string;
}) {
  if (loading) return (
    <TableRow>
      <TableCell colSpan={columnCount}>
        <span className="sr-only" role="status">Loading rows</span>
        <Skeleton className="h-24 w-full" />
      </TableCell>
    </TableRow>
  );
  if (error) return (
    <TableRow>
      <TableCell colSpan={columnCount}>
        <p role="alert">{error}</p>
        {onRetry && <Button variant="outline" onClick={onRetry}>Try again</Button>}
      </TableCell>
    </TableRow>
  );
  if (!hasRows) return (
    <TableRow>
      <TableCell colSpan={columnCount}>
        <EmptyState icon={SearchX} title={emptyMessage} description="Try removing a filter or choosing a different value." bordered={false} />
      </TableCell>
    </TableRow>
  );
  return children;
}

/** Renders supplied rows while the caller owns queries, paging and field selection. */
export function DataTable<T extends RowData>({ columns, data, caption, columnVisibility = visibleColumns, selectedColumnId, onHeaderClick, loading = false, error, onRetry, emptyMessage = "No students match", pagination }: DataTableProps<T>) {
  const table = useTable({ features, columns, data, state: { columnVisibility } });
  const rows = table.getRowModel().rows;
  const columnCount = Math.max(table.getVisibleLeafColumns().length, 1);
  return (
    <div className="flex min-w-0 flex-col gap-3">
      <div className="min-w-0 overflow-hidden rounded-xl border" aria-busy={loading}>
        <Table>
          <TableCaption>{caption}</TableCaption>
          <TableHeader>
            {table.getHeaderGroups().map((group) => (
              <TableRow key={group.id}>
                {group.headers.map((header) => (
                  <TableHead key={header.id} colSpan={header.colSpan} scope="col" data-selected={selectedColumnId === header.column.id || undefined} className="data-[selected=true]:bg-muted">
                    {!header.isPlaceholder && (onHeaderClick && header.subHeaders.length === 0 ? (
                      <Button variant="ghost" size="sm" aria-pressed={selectedColumnId === header.column.id} onClick={() => onHeaderClick(header.column.id)}>
                        <table.FlexRender header={header} />
                      </Button>
                    ) : (
                      <table.FlexRender header={header} />
                    ))}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            <BodyRows columnCount={columnCount} hasRows={rows.length > 0} loading={loading} error={error} onRetry={onRetry} emptyMessage={emptyMessage}>
              {rows.map((row) => (
                <TableRow key={row.id}>
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      <table.FlexRender cell={cell} />
                    </TableCell>
                  ))}
                </TableRow>
              ))}
            </BodyRows>
          </TableBody>
        </Table>
      </div>
      {pagination && <TablePagination {...pagination} disabled={pagination.disabled || loading || !!error} />}
    </div>
  );
}
