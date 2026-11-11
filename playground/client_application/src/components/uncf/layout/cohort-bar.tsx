"use client";

import { Info, X } from "lucide-react";
import { usePathname } from "next/navigation";
import { useMemo } from "react";

import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { cn } from "@/lib/utils";

import { type CohortFilters, cohortFiltersFor, defaultCohortFilters, filterChips, sentenceWord } from "./cohort-filters";
import { type CohortOptions, explorerLoader } from "./explorer-api";
import { type CohortFilterDefinition, cohortFilters } from "./explorer-config";
import { type StudentCount, useExplorer } from "./explorer-context";
import { explorerFontClass } from "./explorer-fonts";
import { explorerLinkButton, explorerWrap } from "./explorer-styles";
import { AddFilterMenu, FilterSheet, SentencePicker, type ValueCounts } from "./filter-menu";
import { hidesSmallGroups, privacyNote, tooFew } from "./small-groups";
import { useCohortFilters } from "./use-cohort-filters";
import { useExplorerResource } from "./use-explorer-resource";

/** The grey cohort bar under the tabs, wired to the URL and the API's counts. Every tab reads the same filters. */
export function CohortBar() {
  const { definitions, filters, setFilter, clearMenuFilters } = useCohortFilters();
  const { studentCount } = useExplorer();
  const cohort = filters.cohort ?? "";
  const load = useMemo(() => explorerLoader<CohortOptions>("/uncf/cohort-options", `cohort=${encodeURIComponent(cohort)}`), [cohort]);
  const { resource, current } = useExplorerResource(load);
  // Counts are optional: if they can't load, the bar still works without them. A past class year's counts aren't shown.
  const options = resource.status === "success" && current ? resource.data : undefined;
  return (
    <CohortBarView
      definitions={definitions}
      filters={filters}
      options={options}
      studentCount={studentCount}
      onChange={setFilter}
      onClearFilters={clearMenuFilters}
    />
  );
}

/** The cohort bar at its defaults, before the URL is read. Same size, so nothing jumps when it loads. */
export function CohortBarFallback() {
  const definitions = cohortFiltersFor(usePathname());
  return <CohortBarView definitions={definitions} filters={defaultCohortFilters(definitions)} studentCount={null} disabled />;
}

type CohortBarViewProps = {
  /** The filters on this tab, with its own starting values. Every filter when left out. */
  definitions?: CohortFilterDefinition[];
  filters: CohortFilters;
  /** The counts behind each choice; left out while they load. */
  options?: CohortOptions;
  /** The current tab's student count, "too few" when it hides its numbers, or null when it hasn't reported one. */
  studentCount: StudentCount;
  onChange?: (id: string, value: string | null) => void;
  /** Clears every "Add filter" filter, keeping the class year and enrollment type. */
  onClearFilters?: () => void;
  disabled?: boolean;
};

/**
 * The cohort bar drawn from props: one sentence that says who's shown ("1,627 first-time students who entered in
 * 2023-24"), its words opening their filters, then "Add filter" and a chip for each filter set. On a phone the filters
 * open in one sheet instead.
 */
export function CohortBarView({ definitions = cohortFilters, filters, options, studentCount, onChange, onClearFilters, disabled }: CohortBarViewProps) {
  const cohort = definitions.find((definition) => definition.id === "cohort")!;
  const enrollment = definitions.find((definition) => definition.id === "enrollment_type")!;
  const menu = definitions.filter((definition) => definition.place === "menu");
  // How a measure is counted (the retention measure), on the tabs that report it.
  const settings = definitions.filter((definition) => definition.place === "setting");
  const chips = filterChips(filters, definitions);
  const cohortYear = filters.cohort ?? "";
  const type = filters.enrollment_type ?? null;
  const count = countText(filters, chips.length, studentCount, options);
  const counts: Record<string, ValueCounts> | undefined = options?.filters;
  const minStudents = options?.min_students;
  const countsNote = `Counts are the ${cohortYear} class’s students with each value, before other filters.`;
  const change = (id: string, value: string | null) => onChange?.(id, value);
  const typePicker = (
    <SentencePicker definition={enrollment} value={type} counts={options?.filters.enrollment_type} minStudents={minStudents} onChange={(value) => change("enrollment_type", value)} disabled={disabled} />
  );
  const summary = `${count ?? "Showing"} ${type === null ? `students ${enrollment.allWord}` : `${sentenceWord(enrollment, type)} students`} who entered in ${cohortYear}`;

  return (
    <section aria-label="Who's shown" className="border-b border-(--uncf-line) bg-(--uncf-band)">
      <div className={cn(explorerWrap, "flex flex-col gap-2.5 py-3")}>
        <div className="flex flex-wrap items-center justify-between gap-x-5 gap-y-2">
          <p className="flex flex-wrap items-center gap-x-1 gap-y-0.5 text-[18px]" aria-live="polite">
            {/* The spaces keep the words apart for screen readers and copying; the flex gap spaces them on screen. */}
            <strong className="uncf-num mr-0.5 text-[20px] font-medium">{count ?? "Showing"}</strong>{" "}
            {type === null ? (
              <>
                <span>students</span> {typePicker}
              </>
            ) : (
              <>
                {typePicker} <span>students</span>
              </>
            )}{" "}
            <span>who entered in</span>{" "}
            <SentencePicker definition={cohort} value={cohortYear} counts={options?.cohorts} minStudents={minStudents} onChange={(value) => change("cohort", value)} disabled={disabled} />
            {minStudents !== undefined && hidesSmallGroups(minStudents) && <PrivacyNote minStudents={minStudents} />}
          </p>
          <div className="flex flex-wrap items-center gap-x-4 gap-y-2">
            {settings.map((definition) => (
              <span key={definition.id} className="inline-flex items-center gap-1 text-[15px] text-(--uncf-ink-2)">
                {definition.label}:
                <SentencePicker
                  definition={definition}
                  value={filters[definition.id] ?? null}
                  onChange={(value) => change(definition.id, value)}
                  disabled={disabled}
                />
              </span>
            ))}
            <div className="max-md:hidden">
              <AddFilterMenu definitions={menu} filters={filters} counts={counts} minStudents={minStudents} onChange={change} countsNote={countsNote} disabled={disabled} />
            </div>
          </div>
        </div>

        <div className={cn("flex items-center gap-2 max-md:overflow-x-auto md:flex-wrap", chips.length === 0 && "md:hidden")}>
          <div className="md:hidden">
            <FilterSheet
              definitions={menu}
              filters={filters}
              counts={counts}
              minStudents={minStudents}
              onChange={change}
              countsNote={countsNote}
              summary={summary}
              activeCount={chips.length}
              onClearAll={() => onClearFilters?.()}
              disabled={disabled}
            />
          </div>
          {chips.map((chip) => (
            <span
              key={chip.definition.id}
              className="inline-flex min-h-8.5 flex-none items-center gap-0.5 rounded-full border border-(--uncf-blue-soft) bg-(--uncf-blue-tint) pl-3 text-sm font-medium"
            >
              {chip.text}
              <button
                type="button"
                aria-label={`Remove ${chip.text}`}
                onClick={() => change(chip.definition.id, null)}
                disabled={disabled}
                className="inline-flex size-7.5 cursor-pointer items-center justify-center rounded-full text-(--uncf-blue) hover:bg-(--uncf-blue-soft)/50"
              >
                <X className="size-3.5" aria-hidden />
              </button>
            </span>
          ))}
          {chips.length > 0 && (
            <button type="button" className={cn(explorerLinkButton, "flex-none text-sm max-md:hidden")} onClick={() => onClearFilters?.()} disabled={disabled}>
              Clear filters
            </button>
          )}
        </div>
      </div>
    </section>
  );
}

/**
 * How many students the sentence counts: the tab's own count; or, before it reports one (the Chat tab never does),
 * the class's size from the cohort counts when no other filter narrows it. null when neither is known.
 */
function countText(filters: CohortFilters, chipCount: number, studentCount: StudentCount, options?: CohortOptions): string | null {
  if (studentCount === "too few") return tooFew(options?.min_students ?? 1, "").trimEnd();
  if (studentCount !== null) return studentCount.toLocaleString("en-US");
  if (!options || chipCount > 0) return null;
  const type = filters.enrollment_type ?? null;
  const size = type === null ? options.cohorts[filters.cohort ?? ""] : options.filters.enrollment_type?.[type];
  return size == null ? null : size.toLocaleString("en-US");
}

/** The ⓘ after the sentence: why some groups have no numbers. Only shown when the API hides small groups. */
function PrivacyNote({ minStudents }: { minStudents: number }) {
  return (
    <Popover>
      <PopoverTrigger aria-label="About hidden groups" className="inline-flex size-9 cursor-pointer items-center justify-center rounded-full text-(--uncf-ink-3) hover:bg-(--uncf-line)">
        <Info className="size-4" aria-hidden />
      </PopoverTrigger>
      <PopoverContent
        align="start"
        sideOffset={6}
        className={cn(explorerFontClass, "w-66 rounded-lg border-0 bg-(--uncf-ink) p-3 text-[13px] leading-snug text-white ring-0 [color-scheme:light]")}
      >
        {privacyNote(minStudents)} A filter value with under {minStudents} students can’t be picked.
      </PopoverContent>
    </Popover>
  );
}
