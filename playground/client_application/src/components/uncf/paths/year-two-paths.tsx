"use client";

import { useMemo, useState } from "react";

import { loadPaths, type Cohort, type Dimension, type PathsQuery, type PathsResponse } from "@/app/(app)/uncf/data";
import { LoadError } from "@/components/load-error";
import { Skeleton } from "@/components/ui/skeleton";
import { cohortLabel } from "@/components/uncf/explorer/labels";
import type { DetailMode } from "@/components/uncf/explorer/explorer-controls";
import { useApiResource } from "@/hooks/use-api-resource";
import { cn } from "@/lib/utils";

import { buildPathGroups, PATHS, type PathGroup, shareOf } from "./paths-model";
import { YearTwoSankey, YearTwoTable } from "./year-two-sankey";

type YearTwoPathsProps = {
  cohort: Cohort;
  groupBy: Dimension[];
  mode: DetailMode;
  /** Stories pass their own; the page reads MOCK paths until an endpoint exists. */
  load?: (query: PathsQuery) => Promise<PathsResponse>;
};

/** "Where were they in year 2?": one chart for the class or a chosen group, plus every group's paths. */
export function YearTwoPaths({ cohort, groupBy, mode, load = loadPaths }: YearTwoPathsProps) {
  const loader = useMemo(() => () => load({ cohort, groupBy }), [load, cohort, groupBy]);
  const { resource, retry } = useApiResource(loader);
  return (
    <section aria-labelledby="paths-heading" className="flex min-w-0 flex-col gap-5 rounded-2xl border bg-card p-5 shadow-[0_12px_32px_-12px_rgba(79,70,229,0.14)] sm:p-6">
      <div className="flex flex-wrap items-center gap-2">
        <h2 id="paths-heading" className="text-sm font-semibold text-indigo-700 dark:text-indigo-300">
          Where were they in year 2?
        </h2>
        <span className="rounded-full border border-amber-400 bg-amber-50 px-2 py-0.5 text-[11px] font-semibold text-amber-900 dark:border-amber-600 dark:bg-amber-950 dark:text-amber-100">
          Mock data
        </span>
      </div>
      {resource.status === "loading" && <Skeleton className="h-96 rounded-xl" />}
      {resource.status === "error" && (
        <LoadError title="Year-2 paths couldn't load." message={resource.message} onRetry={retry} className="min-h-56" />
      )}
      {resource.status === "success" && <PathsBody response={resource.data} mode={mode} />}
    </section>
  );
}

/** The loaded paths: the chosen group's chart and definition, then a bar for every group. */
function PathsBody({ response, mode }: { response: PathsResponse; mode: DetailMode }) {
  const groups = buildPathGroups(response);
  const [viewKey, setViewKey] = useState("all");
  const [asTable, setAsTable] = useState(false);
  const view = groups.find((group) => group.key === viewKey) ?? groups[0];
  const cohortText = cohortLabel(response.meta.cohort);
  const hasGroups = groups.length > 1;

  return (
    <>
      <div className="flex flex-col gap-3">
        {view.shown ? (
          <p className="max-w-3xl text-2xl leading-snug font-medium tracking-tight text-balance text-muted-foreground">
            Of <span className="font-semibold text-foreground">{view.students.toLocaleString("en-US")}</span>{" "}
            {view.label === "All students" ? "students" : <span className="text-foreground">{view.label}</span>} who entered in {cohortText},{" "}
            <span className="font-semibold text-indigo-700 dark:text-indigo-300">{shareOf(view, "returned_here")}</span> came back or earned a
            credential here in year 2. Another <span className="font-semibold text-teal-700 dark:text-teal-300">{shareOf(view, "moved")}</span>{" "}
            moved to another college.
          </p>
        ) : null}
        {response.meta.provisional && (
          <p role="note" className="w-fit rounded-xl border border-amber-300 bg-amber-50 px-3.5 py-2 text-sm text-amber-950 dark:border-amber-700 dark:bg-amber-950/40 dark:text-amber-100">
            <strong className="font-semibold">Year 2 is still arriving for this class.</strong> The course file covers only part of it,
            so these numbers can still change.
          </p>
        )}
      </div>

      <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_17rem]">
        <div className="flex min-w-0 flex-col gap-3">
          <div className="flex flex-wrap items-center justify-between gap-3">
            {hasGroups ? (
              <label className="inline-flex items-center gap-2 text-sm text-muted-foreground">
                <span className="font-medium">Chart shows</span>
                <select
                  value={view.key}
                  onChange={(event) => setViewKey(event.target.value)}
                  className="h-9 max-w-xs rounded-full border border-foreground/40 bg-background px-3 text-sm font-medium text-foreground focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none"
                >
                  {groups.map((group) => (
                    <option key={group.key} value={group.key}>
                      {group.label} · {group.shown ? group.students.toLocaleString("en-US") : "size hidden"}
                    </option>
                  ))}
                </select>
              </label>
            ) : (
              <span />
            )}
            <button
              type="button"
              aria-pressed={asTable}
              onClick={() => setAsTable(!asTable)}
              className="text-xs font-medium text-muted-foreground underline underline-offset-4 hover:text-foreground"
            >
              Show as table
            </button>
          </div>
          {view.shown ? (
            asTable ? (
              <YearTwoTable group={view} cohortText={cohortText} />
            ) : (
              <>
                {/* Under about 600px the drawing gets too tight, so the table stands in. */}
                <div className="hidden sm:block">
                  <YearTwoSankey group={view} cohortText={cohortText} withCounts={mode === "analyst"} />
                </div>
                <div className="sm:hidden">
                  <YearTwoTable group={view} cohortText={cohortText} />
                </div>
              </>
            )
          ) : (
            <div className="flex min-h-56 flex-col items-center justify-center gap-2 rounded-xl bg-muted/60 p-6 text-center">
              <span className="rounded-full border border-dashed border-foreground/60 px-2.5 py-0.5 text-xs font-semibold">Hidden to protect privacy</span>
              <span className="max-w-sm text-sm text-muted-foreground">{view.label} has fewer than 10 students. Choose All students or a larger group.</span>
            </div>
          )}
          {view.split ? (
            <p className="text-xs text-muted-foreground">The last column splits the students who moved: its percentages are shares of them, not of everyone.</p>
          ) : view.shown ? (
            <p className="text-xs text-muted-foreground">Fewer than 10 students in this group moved, so they aren&apos;t split by college type.</p>
          ) : null}
        </div>

        <PathsDefinition response={response} view={view} />
      </div>

      {hasGroups && <PathBars groups={groups} selected={view.key} onSelect={setViewKey} />}
    </>
  );
}

/** What the paths mean, beside the chart. */
function PathsDefinition({ response, view }: { response: PathsResponse; view: PathGroup }) {
  return (
    <aside aria-label="What this chart means" className="flex flex-col gap-3 rounded-xl bg-muted/60 p-4 text-sm">
      <h3 className="text-[11px] font-semibold tracking-wider text-muted-foreground uppercase">What this means</h3>
      <p>Each student who entered, placed on one path in their second academic year.</p>
      <ul className="flex flex-col gap-1.5">
        {PATHS.map((path) => (
          <li key={path.key} className="flex items-baseline gap-2">
            <span aria-hidden className="size-2 shrink-0 rounded-full" style={{ background: path.color }} />
            <span>
              <strong className="font-semibold">{path.name}</strong>
              {path.key === "returned_here" && ": enrolled or earned a credential here (PDP retention). A student also at another college counts here."}
              {path.key === "moved" && ": at another college instead (PDP persistence without retention)."}
              {path.key === "no_enrollment" && ": no record here or in the Clearinghouse match, including students who blocked their records."}
            </span>
          </li>
        ))}
      </ul>
      <p className="text-muted-foreground">College type is the most recent other college on record, which can be after year 2.</p>
      <p className="text-xs text-amber-900 dark:text-amber-200">
        <strong className="font-semibold">Mock:</strong> no API serves these paths yet. The definitions and hiding rule here are a
        proposal for the team.
      </p>
      {view.shown && (
        <p className="text-xs text-muted-foreground tabular-nums">
          {view.label}: {PATHS.map((path) => `${view.counts[path.key].toLocaleString("en-US")} ${path.name.toLowerCase()}`).join(", ")}.
        </p>
      )}
      <p className="text-xs text-muted-foreground">Source: {response.meta.source}</p>
    </aside>
  );
}

/** Every group's three paths as one stacked bar, so groups compare at a glance. Picking one drives the chart. */
function PathBars({ groups, selected, onSelect }: { groups: PathGroup[]; selected: string; onSelect: (key: string) => void }) {
  return (
    <div className="flex flex-col gap-1 border-t pt-5">
      <div className="mb-1 flex flex-wrap items-baseline justify-between gap-2">
        <div>
          <h3 className="text-base font-semibold tracking-tight">Year-2 paths for each group</h3>
          <p className="text-xs text-muted-foreground">Pick a group to follow just those students in the chart.</p>
        </div>
        <div aria-hidden className="flex flex-wrap gap-3 text-xs text-muted-foreground">
          {PATHS.map((path) => (
            <span key={path.key} className="inline-flex items-center gap-1.5">
              <span className="size-2.5 rounded-sm" style={{ background: path.color }} />
              {path.name}
            </span>
          ))}
        </div>
      </div>
      {groups.map((group) => {
        const on = group.key === selected;
        return (
          <button
            key={group.key}
            type="button"
            aria-pressed={on}
            onClick={() => onSelect(group.key)}
            className={cn(
              "grid w-full grid-cols-[minmax(0,1fr)_auto] items-center gap-x-4 gap-y-1 rounded-lg px-3 py-2 text-left sm:grid-cols-[minmax(8rem,12rem)_minmax(0,1fr)_7rem]",
              "focus-visible:ring-[3px] focus-visible:ring-ring/50 focus-visible:outline-none",
              on ? "bg-indigo-50 shadow-[inset_3px_0_0_#4f46e5] dark:bg-indigo-950/50" : "hover:bg-muted/60",
            )}
          >
            <span className={cn("text-sm", on || group.key === "all" ? "font-semibold" : "font-medium")}>{group.label}</span>
            {group.shown ? (
              <span className="order-last col-span-2 flex flex-col gap-1 sm:order-none sm:col-span-1">
                <span aria-hidden className="flex h-3.5 gap-0.5 overflow-hidden rounded-full">
                  {PATHS.map((path) => (
                    <span key={path.key} style={{ width: `${(group.counts[path.key] / group.students) * 100}%`, background: path.color }} />
                  ))}
                </span>
                <span className="flex flex-wrap gap-x-3 text-xs text-muted-foreground tabular-nums">
                  {PATHS.map((path) => (
                    <span key={path.key} className="inline-flex items-center gap-1">
                      <span aria-hidden className="size-2 rounded-sm" style={{ background: path.color }} />
                      <span className="sr-only">{path.name}: </span>
                      {shareOf(group, path.key)}
                    </span>
                  ))}
                </span>
              </span>
            ) : (
              <span aria-hidden className="order-last col-span-2 h-3.5 rounded-full border border-dashed border-foreground/50 sm:order-none sm:col-span-1" />
            )}
            <span className="text-right text-xs text-muted-foreground tabular-nums">
              {group.shown ? `${group.students.toLocaleString("en-US")} students` : "Hidden"}
            </span>
          </button>
        );
      })}
    </div>
  );
}
