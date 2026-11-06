"use client";

import type { ComponentProps } from "react";
import type { RowData } from "@tanstack/react-table";
import { PageIntro } from "@/components/page-intro";
import { ComparisonStatCard } from "@/components/workbench/explore/comparison-stat-card";
import { DataTable } from "@/components/workbench/explore/data-table";
import { FilterBar, FilterChipMenu } from "@/components/workbench/explore/filter-chip-menu";
import { FilteredStudentsSummary } from "@/components/workbench/explore/filtered-students-summary";
import { TableLanguageToggle } from "@/components/workbench/explore/table-language-toggle";

export type ExplorePageProps<T extends RowData> = {
  mode: ComponentProps<typeof TableLanguageToggle>;
  filters: (ComponentProps<typeof FilterChipMenu> & { id: string })[];
  filterBar: Omit<ComponentProps<typeof FilterBar>, "children" | "hasFilters">;
  stats: (ComponentProps<typeof ComparisonStatCard> & { id: string })[];
  summary: ComponentProps<typeof FilteredStudentsSummary>;
  table: ComponentProps<typeof DataTable<T>>;
};

/** Composes a controlled snapshot of filters, summary cards and student rows. */
export function ExplorePage<T extends RowData>({ mode, filters, filterBar, stats, summary, table }: ExplorePageProps<T>) {
  const hasFilters = filters.some((filter) => filter.selectedValues.length > 0);
  return (
    <div className="flex min-w-0 flex-col gap-6">
      <PageIntro size="sm" title="Explore data">
        <p>Filter students and click a column heading to read what its field means.</p>
      </PageIntro>
      <TableLanguageToggle {...mode} />
      {/* Filters and comparisons are skipped until the API can filter and summarize. */}
      {filters.length > 0 && (
        <FilterBar {...filterBar} hasFilters={hasFilters}>
          {filters.map(({ id, ...filter }) => (
            <FilterChipMenu key={id} {...filter} />
          ))}
        </FilterBar>
      )}
      {stats.length > 0 && (
        <ul aria-label="This group compared with all students" className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          {stats.map(({ id, ...stat }) => (
            <li key={id}>
              <ComparisonStatCard {...stat} />
            </li>
          ))}
        </ul>
      )}
      <FilteredStudentsSummary {...summary} />
      <DataTable {...table} />
      <p className="text-xs text-muted-foreground">Mock data is synthetic, not a finding about real students or institutions.</p>
    </div>
  );
}
