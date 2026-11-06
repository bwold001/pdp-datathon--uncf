"use client";

import { Button } from "@/components/ui/button";

export type TablePaginationProps = {
  pageIndex: number;
  pageSize: number;
  totalRows: number;
  noun?: string;
  disabled?: boolean;
  onPrevious: () => void;
  onNext: () => void;
};

/** Displays the supplied page range and disables actions beyond either end. */
export function TablePagination({ pageIndex, pageSize, totalRows, noun = "students", disabled = false, onPrevious, onNext }: TablePaginationProps) {
  const start = pageIndex * pageSize;
  const range = totalRows === 0 ? `No ${noun} match`
    : `${Math.min(start + 1, totalRows).toLocaleString("en-US")}–${Math.min(start + pageSize, totalRows).toLocaleString("en-US")} of ${totalRows.toLocaleString("en-US")} ${noun}`;
  return (
    <nav aria-label="Table pagination" className="flex flex-wrap items-center justify-between gap-3">
      <p role="status" className="text-sm text-muted-foreground">{range}</p>
      <div className="flex gap-2">
        <Button variant="outline" size="sm" disabled={disabled || pageIndex <= 0 || totalRows === 0} onClick={onPrevious}>
          Previous
        </Button>
        <Button variant="outline" size="sm" disabled={disabled || start + pageSize >= totalRows} onClick={onNext}>
          Next
        </Button>
      </div>
    </nav>
  );
}
