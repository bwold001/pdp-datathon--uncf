import { cohorts, type Cohort, type Dimension, type ResultRow, type ResultsResponse } from "@/app/(app)/uncf/data";

import { dimensionInfo, measureNames, valueLabel, valueOrder } from "./labels";

/** Groups smaller than this are tagged and left out of the comparison sentence: their rates swing a lot. */
export const SMALL_GROUP = 30;

/** What a bar shows. Anything but "ok" is drawn as a state, never as a 0% bar. */
export type BarState = "ok" | "hidden" | "not_yet" | "not_reported";

export type Bar = {
  key: string;
  /** The row's group values, so the same group can be found in another class's results. */
  group: ResultRow["group"];
  label: string;
  state: BarState;
  /** The rate shown, in percent with one decimal, worked out from numerator and denominator. */
  percent: number | null;
  numerator: number | null;
  denominator: number | null;
  isUnknown: boolean;
  isSmall: boolean;
};

/** One block of bars. With two groupings, each value of the first gets its own section. */
export type BarSection = {
  key: string;
  heading: string | null;
  bars: Bar[];
  /** With two groupings, hidden combinations are listed together instead of one empty bar each. */
  hidden: Bar[];
};

/** The state for a row's status. */
export function stateOf(row: ResultRow): BarState {
  if (row.status === "not_yet_observable") return "not_yet";
  if (row.status === "not_reported") return "not_reported";
  if (row.status !== "ok" || row.numerator === null || row.denominator === null || row.denominator === 0) return "hidden";
  return "ok";
}

/** A rate in percent with one decimal, from the counts, so every screen rounds the same way. */
export function percentOf(numerator: number, denominator: number): number {
  return Math.round((numerator / denominator) * 1000) / 10;
}

/** "58.9%" for a shown bar. */
export function formatPercent(percent: number): string {
  return `${percent.toFixed(1)}%`;
}

/** The label for a row's group, e.g. "Full-time · Pell grant" for two groupings. */
function labelOf(row: ResultRow, groupBy: Dimension[]): string {
  if (groupBy.length === 0) return "All students";
  return groupBy.map((dimension) => valueLabel(dimension, row.group[dimension] ?? "")).join(" · ");
}

/** Turn one API row into a bar. */
export function toBar(row: ResultRow, groupBy: Dimension[]): Bar {
  const state = stateOf(row);
  const shown = state === "ok" && row.numerator !== null && row.denominator !== null;
  return {
    key: groupBy.map((dimension) => row.group[dimension] ?? "").join("|") || "all",
    group: row.group,
    label: labelOf(row, groupBy),
    state,
    percent: shown ? percentOf(row.numerator as number, row.denominator as number) : null,
    numerator: shown ? row.numerator : null,
    denominator: shown ? row.denominator : null,
    isUnknown: groupBy.some((dimension) => row.group[dimension] === "UNKNOWN"),
    isSmall: shown && (row.denominator as number) < SMALL_GROUP,
  };
}

/** True for the all-students row: it names no grouping. */
function isEveryone(row: ResultRow): boolean {
  return Object.keys(row.group).length === 0;
}

/** Sort rows by each grouping's display order. */
function compareRows(groupBy: Dimension[]) {
  return (a: ResultRow, b: ResultRow) => {
    for (const dimension of groupBy) {
      const difference = valueOrder(dimension, a.group[dimension] ?? "") - valueOrder(dimension, b.group[dimension] ?? "");
      if (difference !== 0) return difference;
    }
    return 0;
  };
}

/** The all-students bar and the sections of group bars for one response. */
export function buildBars(response: ResultsResponse): { everyone: Bar | null; sections: BarSection[] } {
  const groupBy = response.meta.group_by;
  const everyoneRow = response.rows.find(isEveryone);
  const groupRows = response.rows.filter((row) => !isEveryone(row)).sort(compareRows(groupBy));
  const everyone = everyoneRow ? toBar(everyoneRow, []) : null;

  if (groupBy.length < 2) {
    return { everyone, sections: [{ key: "all", heading: null, bars: groupRows.map((row) => toBar(row, groupBy)), hidden: [] }] };
  }

  // Two groupings: one section per value of the first, one bar per value of the second.
  const [first, second] = groupBy;
  const sections = new Map<string, BarSection>();
  for (const row of groupRows) {
    const value = row.group[first] ?? "";
    const section = sections.get(value) ?? { key: value, heading: valueLabel(first, value), bars: [], hidden: [] };
    // Label by the second grouping only (the section names the first), but an unknown in either counts.
    const bar = { ...toBar(row, [second]), isUnknown: groupBy.some((dimension) => row.group[dimension] === "UNKNOWN") };
    if (bar.state === "hidden") section.hidden.push(bar);
    else section.bars.push(bar);
    sections.set(value, section);
  }
  return { everyone, sections: [...sections.values()] };
}

/**
 * One plain sentence about the spread, from shown rates only. It leaves out unknown and small groups,
 * and it names groups only when there are exactly two to compare.
 */
export function comparisonSentence(response: ResultsResponse, everyone: Bar | null, sections: BarSection[]): string {
  const measureName = measureNames[response.meta.measure];
  const allText = everyone?.state === "ok" && everyone.percent !== null ? ` All students: ${formatPercent(everyone.percent)}.` : "";
  const eligible = sections
    .flatMap((section) => section.bars.map((bar) => ({ ...bar, label: section.heading ? `${section.heading} · ${bar.label}` : bar.label })))
    .filter((bar) => bar.state === "ok" && !bar.isUnknown && !bar.isSmall && bar.percent !== null)
    .sort((a, b) => (b.percent as number) - (a.percent as number));

  if (eligible.length < 2) {
    return `Too few groups have ${SMALL_GROUP} or more students to compare this year.${allText}`;
  }
  const high = eligible[0];
  const low = eligible[eligible.length - 1];
  const gap = (Math.round(((high.percent as number) - (low.percent as number)) * 10) / 10).toFixed(1);
  if (eligible.length === 2) {
    return `${measureName}: ${high.label} ${formatPercent(high.percent as number)}, ${low.label} ${formatPercent(low.percent as number)} (${gap} points apart).${allText}`;
  }
  const unit = response.meta.group_by.length === 2 ? "combinations" : "groups";
  return `Among ${unit} with ${SMALL_GROUP} or more students, ${measureName} ranges from ${formatPercent(low.percent as number)} to ${formatPercent(high.percent as number)}, ${gap} points apart.${allText}`;
}

/** "Returned here by Pell grant and full- or part-time status". */
export function chartTitle(response: ResultsResponse): string {
  const groupings = response.meta.group_by.map((dimension) => dimensionInfo[dimension].phrase);
  return `${measureNames[response.meta.measure]} by ${groupings.join(" and ")}`;
}

/** One point on a trend line: the same group's rate in one entering class. */
export type TrendPoint = { cohort: Cohort; percent: number | null; provisional: boolean };

/** The same group's shown rate in every class, oldest first. A hidden or missing rate is a gap, never 0. */
export function trendFor(group: ResultRow["group"], byCohort: Partial<Record<Cohort, ResultsResponse | null>>): TrendPoint[] {
  const wanted = Object.entries(group);
  return cohorts.map((cohort) => {
    const response = byCohort[cohort];
    const row = response?.rows.find(
      (candidate) => Object.keys(candidate.group).length === wanted.length && wanted.every(([dimension, value]) => candidate.group[dimension as Dimension] === value),
    );
    const shown = row && stateOf(row) === "ok";
    return {
      cohort,
      percent: shown ? percentOf(row.numerator as number, row.denominator as number) : null,
      provisional: Boolean(response?.meta.provisional),
    };
  });
}

/** One scale for every trend line in a chart, padded, and at least 12 points tall so small wiggles stay small. */
export function trendScale(lines: TrendPoint[][]): [number, number] {
  const values = lines.flat().flatMap((point) => (point.percent === null ? [] : [point.percent]));
  if (values.length === 0) return [0, 100];
  let low = Math.min(...values) - 3;
  let high = Math.max(...values) + 3;
  if (high - low < 12) {
    const middle = (high + low) / 2;
    low = middle - 6;
    high = middle + 6;
  }
  return [Math.max(0, low), Math.min(100, high)];
}
