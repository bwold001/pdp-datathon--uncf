"use client";

import { Info } from "lucide-react";
import { useMemo } from "react";

import { useApiResource } from "@/hooks/use-api-resource";
import { cn } from "@/lib/utils";

import { type CohortFilters, countChangedFilters, defaultCohortFilters } from "./cohort-filters";
import { type CohortOptions, explorerLoader } from "./explorer-api";
import { cohortFilters } from "./explorer-config";
import { type StudentCount, useExplorer } from "./explorer-context";
import { explorerLinkButton, explorerWrap } from "./explorer-styles";
import { FilterSelect } from "./filter-select";
import { hidesSmallGroups, tooFew } from "./small-groups";
import { useCohortFilters } from "./use-cohort-filters";

/** The grey cohort bar under the tabs, wired to the URL and the API's counts. Every tab reads the same filters. */
export function CohortBar() {
  const { filters, setFilter, reset } = useCohortFilters();
  const { studentCount } = useExplorer();
  const cohort = filters.cohort ?? "";
  const load = useMemo(() => explorerLoader<CohortOptions>("/uncf/cohort-options", `cohort=${encodeURIComponent(cohort)}`), [cohort]);
  const { resource } = useApiResource(load);
  // Counts are optional: if they can't load, the bar still works without them.
  const options = resource.status === "success" ? resource.data : undefined;
  return <CohortBarView filters={filters} options={options} studentCount={studentCount} onChange={setFilter} onReset={reset} />;
}

/** The cohort bar at its defaults, before the URL is read. Same size, so nothing jumps when it loads. */
export function CohortBarFallback() {
  return <CohortBarView filters={defaultCohortFilters()} studentCount={null} disabled />;
}

type CohortBarViewProps = {
  filters: CohortFilters;
  /** The counts behind each choice; left out while they load. */
  options?: CohortOptions;
  /** The current tab's student count, "too few" when it hides its numbers, or null when it hasn't reported one. */
  studentCount: StudentCount;
  onChange?: (id: string, value: string | null) => void;
  onReset?: () => void;
  disabled?: boolean;
};

/** The cohort bar drawn from props. */
export function CohortBarView({ filters, options, studentCount, onChange, onReset, disabled }: CohortBarViewProps) {
  return (
    <section aria-label="Cohort filters" className="border-b border-(--uncf-line) bg-(--uncf-band)">
      <div className={cn(explorerWrap, "py-4.5")}>
        <div className="flex flex-wrap items-end gap-x-4 gap-y-3">
          <div className="w-full text-xs font-bold tracking-[0.08em] text-(--uncf-ink-2) md:w-auto md:pb-3">COHORT</div>
          {cohortFilters.map((definition) => (
            <FilterSelect
              key={definition.id}
              definition={definition}
              value={filters[definition.id] ?? null}
              onChange={(value) => onChange?.(definition.id, value)}
              counts={definition.id === "cohort" ? options?.cohorts : options?.filters[definition.id]}
              minStudents={options?.min_students}
              disabled={disabled}
            />
          ))}
          <button type="button" className={cn(explorerLinkButton, "pb-2.5")} onClick={onReset} disabled={disabled}>
            Reset
          </button>
        </div>
        <div className="mt-3 flex flex-wrap gap-x-5 gap-y-1 text-sm text-(--uncf-ink-3)">
          <span>{showingText(filters, studentCount, options)}</span>
          {options && hidesSmallGroups(options.min_students) && (
            <span className="inline-flex items-center gap-1.5">
              <Info className="size-4" aria-hidden />
              Groups under {options.min_students} students hidden
            </span>
          )}
        </div>
      </div>
    </section>
  );
}

/** "Showing 1,114 students · 2 filters set", or the whole cohort's size until the tab reports its count. */
function showingText(filters: CohortFilters, studentCount: StudentCount, options?: CohortOptions): string {
  const cohort = filters.cohort ?? "";
  const cohortSize = options?.cohorts[cohort];
  let showing = `${cohort} cohort`;
  // Never the cohort's size here: it would read as if that many students matched.
  if (studentCount === "too few") showing = `${tooFew(options?.min_students ?? 1)} match`;
  else if (studentCount !== null) showing = `Showing ${studentCount.toLocaleString("en-US")} students`;
  else if (cohortSize != null) showing = `${cohort} cohort: ${cohortSize.toLocaleString("en-US")} students`;
  const changed = countChangedFilters(filters);
  if (changed === 0) return showing;
  return `${showing} · ${changed} ${changed === 1 ? "filter" : "filters"} set`;
}
