import { type Cohort, isGatewayMeasure, type Measure } from "@/app/(app)/uncf/data";
import { cn } from "@/lib/utils";

import { type Bar, type BarSection, formatPercent, SMALL_GROUP, type TrendPoint } from "./bars";
import type { DetailMode } from "./explorer-controls";
import { TrendSparkline } from "./trend-sparkline";

/** Unknown groups are marked by a pattern, not a lighter color, so they read in grayscale too. */
const UNKNOWN_FILL = "repeating-linear-gradient(135deg, var(--color-indigo-600) 0 3px, var(--color-indigo-200) 3px 6px)";

const STATE_TEXT: Record<Exclude<Bar["state"], "ok">, string> = {
  hidden: "Hidden",
  not_yet: "Not available yet",
  not_reported: "Not reported",
};

const STATE_FOR_READERS: Record<Exclude<Bar["state"], "ok">, string> = {
  hidden: "Hidden to protect privacy. This does not mean 0.",
  not_yet: "Not available yet: these students haven't reached this point.",
  not_reported: "Not reported: the school's file doesn't include what this needs yet.",
};

/** Each bar's trend across entering classes, on one shared scale. */
export type ChartTrends = { current: Cohort; scale: [number, number]; of: (bar: Bar) => TrendPoint[] };

type ResultsChartProps = {
  measure: Measure;
  everyone: Bar | null;
  sections: BarSection[];
  mode: DetailMode;
  trends?: ChartTrends | null;
};

/** Label, bar, rate, then trend from medium screens up; on a phone the bar drops under the label. */
const ROW_GRID = "grid grid-cols-[minmax(0,1fr)_auto] sm:grid-cols-[minmax(8rem,13rem)_minmax(0,1fr)_8rem] md:grid-cols-[minmax(8rem,13rem)_minmax(0,1fr)_7.5rem_7rem]";

/** Rate by group as horizontal bars, with all students on top and a marker at their rate on every bar. */
export function ResultsChart({ measure, everyone, sections, mode, trends = null }: ResultsChartProps) {
  const reference = everyone?.state === "ok" ? everyone.percent : null;
  const isGateway = isGatewayMeasure(measure);
  return (
    <div className="flex flex-col gap-4">
      <div
        aria-hidden
        className={cn(ROW_GRID, "hidden gap-x-4 px-3 text-[11px] font-semibold tracking-wider text-muted-foreground uppercase sm:grid")}
      >
        <span />
        <span>0% to 100%</span>
        <span className="text-right">Rate</span>
        <span className="hidden text-right md:block">{trends ? "Trend" : ""}</span>
      </div>
      {everyone && (
        <ul aria-label="All students" className="flex flex-col">
          <BarRow bar={everyone} reference={null} mode={mode} isGateway={isGateway} trends={trends} emphasis />
        </ul>
      )}
      {sections.map((section) => (
        <section key={section.key} aria-label={section.heading ?? undefined} className="flex flex-col gap-1">
          {section.heading && <h3 className="px-3 pt-2 text-sm font-semibold">{section.heading}</h3>}
          <ul className="flex flex-col divide-y">
            {section.bars.map((bar) => (
              <BarRow key={bar.key} bar={bar} reference={reference} mode={mode} isGateway={isGateway} trends={trends} />
            ))}
          </ul>
          {section.hidden.length > 0 && (
            <p className="flex flex-wrap items-center gap-2 px-3 py-2 text-xs text-muted-foreground">
              <span className="rounded-full border border-dashed border-foreground/60 px-2 py-0.5 font-semibold text-foreground">Hidden</span>
              <span>
                {section.hidden.map((bar) => bar.label).join(", ")}:{" "}
                {section.hidden.length === 1 ? "fewer than 10 students, so it is" : "fewer than 10 students each, so they are"} hidden
                to protect privacy. Hidden does not mean 0.
              </span>
            </p>
          )}
        </section>
      ))}
      <ChartKey sections={sections} hasReference={reference !== null} trends={trends} />
    </div>
  );
}

type BarRowProps = { bar: Bar; reference: number | null; mode: DetailMode; isGateway: boolean; trends: ChartTrends | null; emphasis?: boolean };

/** One group: its name, its bar (or its state), and its rate with the student count. */
function BarRow({ bar, reference, mode, isGateway, trends, emphasis = false }: BarRowProps) {
  const shown = bar.state === "ok" && bar.percent !== null;
  return (
    <li
      className={cn(
        ROW_GRID,
        "items-center gap-x-4 gap-y-1.5 px-3 py-2.5",
        emphasis && "rounded-xl bg-muted/60",
      )}
    >
      <span className={cn("flex flex-wrap items-center gap-x-2 gap-y-0.5 text-sm", emphasis ? "font-semibold" : "font-medium", bar.isUnknown && "text-muted-foreground")}>
        {bar.label}
        {bar.isSmall && (
          <span className="rounded-full bg-muted px-1.5 py-px text-[11px] font-semibold text-muted-foreground">Small group</span>
        )}
      </span>

      <div aria-hidden className="relative order-last col-span-2 h-3 sm:order-none sm:col-span-1">
        {shown ? (
          <>
            <div className="h-full overflow-hidden rounded-full bg-muted">
              <div
                className={cn("h-full rounded-full transition-[width] duration-500", emphasis ? "bg-foreground/80" : "bg-indigo-600 dark:bg-indigo-400")}
                style={{ width: `${bar.percent}%`, background: bar.isUnknown ? UNKNOWN_FILL : undefined }}
              />
            </div>
            {reference !== null && (
              <span
                className="absolute -top-1 h-5 w-0.5 -translate-x-1/2 rounded-full bg-foreground"
                style={{ left: `${reference}%` }}
              />
            )}
          </>
        ) : (
          <div
            className={cn(
              "h-full rounded-full",
              bar.state === "hidden" && "border border-dashed border-foreground/50",
              bar.state === "not_yet" && "bg-muted",
              bar.state === "not_reported" && "bg-[repeating-linear-gradient(135deg,var(--color-muted)_0_6px,transparent_6px_12px)]",
            )}
          />
        )}
      </div>

      <span className="flex flex-col items-end text-right tabular-nums">
        {shown ? (
          <>
            <span className={cn("text-base font-semibold", !emphasis && "text-indigo-800 dark:text-indigo-200")}>
              {formatPercent(bar.percent as number)}
            </span>
            <span className="text-xs text-muted-foreground">{countText(bar, mode, isGateway)}</span>
          </>
        ) : (
          <>
            <span
              className={cn(
                "rounded-full px-2 py-0.5 text-xs font-semibold",
                bar.state === "hidden" ? "border border-dashed border-foreground/60" : "bg-muted",
              )}
            >
              {STATE_TEXT[bar.state as Exclude<Bar["state"], "ok">]}
            </span>
            <span className="sr-only">{STATE_FOR_READERS[bar.state as Exclude<Bar["state"], "ok">]}</span>
          </>
        )}
      </span>

      <span className="hidden justify-end md:flex">
        {trends && <TrendSparkline points={trends.of(bar)} current={trends.current} scale={trends.scale} emphasis={emphasis} />}
      </span>
    </li>
  );
}

/** "873 students" in plain language; "514 of 873" for analysts. */
function countText(bar: Bar, mode: DetailMode, isGateway: boolean): string {
  const denominator = (bar.denominator as number).toLocaleString("en-US");
  if (mode === "analyst") return `${(bar.numerator as number).toLocaleString("en-US")} of ${denominator}`;
  return isGateway ? `${denominator} required` : `${denominator} students`;
}

/** Explains the marks on the chart that are actually there. */
function ChartKey({ sections, hasReference, trends }: { sections: BarSection[]; hasReference: boolean; trends: ChartTrends | null }) {
  const bars = sections.flatMap((section) => section.bars);
  const hasUnknown = bars.some((bar) => bar.isUnknown && bar.state === "ok");
  const hasSmall = bars.some((bar) => bar.isSmall);
  return (
    <div aria-hidden className="flex flex-wrap items-center gap-x-5 gap-y-1.5 px-3 text-xs text-muted-foreground">
      {hasReference && (
        <span className="inline-flex items-center gap-1.5">
          <span className="h-3 w-0.5 rounded-full bg-foreground" />
          All students
        </span>
      )}
      {hasUnknown && (
        <span className="inline-flex items-center gap-1.5">
          <span className="h-2.5 w-4 rounded-sm" style={{ background: UNKNOWN_FILL }} />
          Unknown: the value is missing from the file
        </span>
      )}
      {hasSmall && <span>Small group: fewer than {SMALL_GROUP} students, so the rate can swing a lot from year to year</span>}
      {trends && (
        <span className="hidden md:inline">
          Trend: one point per entering class; the large point is {trends.current.replace("-", "–")}. A hollow point means that
          class&apos;s year 2 is still arriving.
        </span>
      )}
    </div>
  );
}
