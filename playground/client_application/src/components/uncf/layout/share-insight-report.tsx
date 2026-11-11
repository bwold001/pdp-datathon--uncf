import { cn } from "@/lib/utils";

import { cohortFiltersFor, filterValueLabel, readCohortFilters } from "./cohort-filters";
import { explorerHeader } from "./explorer-config";
import type { StudentCount } from "./explorer-context";
import { explorerFontClass } from "./explorer-fonts";
import { ExplorerMark } from "./explorer-header";
import { explorerWrap } from "./explorer-styles";

/** Who a shared tab counts, in words: the cohort, how many students, and each filter that isn't "All". */
export type ReportFacts = { cohort: string; students: string | null; filters: string[]; date: string };

/** The facts for the tab at this address, read the same way the cohort bar reads them. */
export function describeView(pathname: string, search: string, studentCount: StudentCount): ReportFacts {
  const definitions = cohortFiltersFor(pathname);
  const filters = readCohortFilters(new URLSearchParams(search), definitions);
  const picked = definitions.filter((definition) => !definition.required && filters[definition.id] != null);
  return {
    cohort: filters.cohort ?? "",
    students:
      studentCount === "under 10" ? "Fewer than 10 students" : studentCount === null ? null : `${studentCount.toLocaleString("en-US")} students`,
    filters: picked.map((definition) => `${definition.label}: ${filterValueLabel(definition, filters[definition.id] ?? null)}`),
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
        <div className={cn(explorerWrap, "flex items-baseline gap-6 py-4 text-sm")}>
          <p className="min-w-0 flex-1">
            <b className="font-semibold">{who}</b>
            <span className="text-(--uncf-ink-2)">
              {" · "}
              {facts.filters.length ? facts.filters.join(" · ") : "No filters"}
            </span>
          </p>
          <span className="shrink-0 text-(--uncf-ink-3)">Shared {facts.date}</span>
        </div>
      </section>
      <div ref={slotRef} />
      <p className={cn(explorerWrap, "pb-6 text-center text-[13px] text-(--uncf-ink-3)")}>{explorerHeader.disclaimer}</p>
    </div>
  );
}
