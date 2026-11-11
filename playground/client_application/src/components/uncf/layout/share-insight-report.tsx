import { cn } from "@/lib/utils";

import { cohortFiltersFor, filterValueLabel, readCohortFilters } from "./cohort-filters";
import { explorerHeader } from "./explorer-config";
import type { StudentCount } from "./explorer-context";
import { explorerFontClass } from "./explorer-fonts";
import { ExplorerMark } from "./explorer-header";
import { explorerWrap } from "./explorer-styles";

/** Who a shared tab counts, in words: the cohort, how many students, and each filter that isn't "All" (Retention too). */
export type ReportFacts = { cohort: string; students: string | null; filters: { label: string; value: string }[]; date: string };

/** The facts for the tab at this address, read the same way the cohort bar reads them. */
export function describeView(pathname: string, search: string, studentCount: StudentCount): ReportFacts {
  const definitions = cohortFiltersFor(pathname);
  const filters = readCohortFilters(new URLSearchParams(search), definitions);
  // The cohort leads the report on its own line; the retention measure changes the numbers, so it's listed.
  const picked = definitions.filter((definition) => definition.id !== "cohort" && filters[definition.id] != null);
  return {
    cohort: filters.cohort ?? "",
    students:
      studentCount === "too few" ? "Too few students to show" : studentCount === null ? null : `${studentCount.toLocaleString("en-US")} students`,
    filters: picked.map((definition) => ({ label: definition.label, value: filterValueLabel(definition, filters[definition.id] ?? null) })),
    date: new Date().toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }),
  };
}

type ShareInsightReportProps = {
  facts: ReportFacts;
  /** The page's width, so the tab lays out as it does on screen. Fills its container when left out. */
  width?: number;
  /** The report, which Share Insight draws. */
  ref?: React.Ref<HTMLDivElement>;
  /** Where the copy of the tab goes. */
  slotRef?: React.Ref<HTMLDivElement>;
};

/**
 * What a shared PDF shows: the Explorer's name and source, who's counted in words instead of the cohort bar's
 * dropdowns, then a copy of the tab.
 */
export function ShareInsightReport({ facts, width, ref, slotRef }: ShareInsightReportProps) {
  const who = [`Cohort ${facts.cohort}`, facts.students].filter(Boolean).join(" · ");
  return (
    <div ref={ref} style={{ width }} className={cn(explorerFontClass, "bg-(--uncf-bg) text-[15px] leading-normal text-(--uncf-ink)")}>
      <header className="border-b border-(--uncf-line) bg-(--uncf-surface)">
        <div className={cn(explorerWrap, "flex items-center gap-4 py-5")}>
          <ExplorerMark />
          <div className="min-w-0">
            <p className="text-xl font-bold tracking-[-0.01em]">{explorerHeader.title}</p>
            <p className="text-sm text-(--uncf-ink-3)">{explorerHeader.source}</p>
          </div>
          <span className="flex-1" />
          <span className="rounded-full bg-(--uncf-warn-bg) px-3 py-0.75 text-[13px] font-semibold text-(--uncf-orange-ink)">
            {explorerHeader.sampleBadge}
          </span>
        </div>
      </header>
      <section className="border-b border-(--uncf-line) bg-(--uncf-band)">
        <div className={cn(explorerWrap, "flex flex-col gap-3 py-4.5")}>
          <div className="flex items-baseline gap-6">
            <p className="min-w-0 flex-1 text-[17px] font-semibold">{who}</p>
            <span className="shrink-0 text-sm text-(--uncf-ink-3)">Shared {facts.date}</span>
          </div>
          {/* Read-only pills, not the cohort bar's dropdowns: what was picked, for someone who can't change it. */}
          <div className="flex flex-wrap items-center gap-2 text-sm">
            <span className="mr-1 text-xs font-bold tracking-[0.08em] text-(--uncf-ink-2) uppercase">Filters</span>
            {facts.filters.length ? (
              facts.filters.map(({ label, value }) => (
                <span key={label} className="rounded-full border border-(--uncf-line-2) bg-(--uncf-surface) px-3 py-1">
                  <span className="text-(--uncf-ink-3)">{label}:</span> <b className="font-semibold">{value}</b>
                </span>
              ))
            ) : (
              <span className="text-(--uncf-ink-2)">None. Every student in the cohort.</span>
            )}
          </div>
        </div>
      </section>
      <div ref={slotRef} />
      <p className={cn(explorerWrap, "pb-6 text-center text-[13px] text-(--uncf-ink-3)")}>{explorerHeader.disclaimer}</p>
    </div>
  );
}
