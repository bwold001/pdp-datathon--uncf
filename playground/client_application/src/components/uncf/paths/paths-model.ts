import type { CollegeTypeSplit, Dimension, PathsResponse, PathsRow } from "@/app/(app)/uncf/data";
import { formatPercent, percentOf } from "@/components/uncf/explorer/bars";
import { valueLabel, valueOrder } from "@/components/uncf/explorer/labels";

/** The three year-2 paths, in the order the chart draws them, with one color each everywhere. */
export const PATHS = [
  { key: "returned_here", name: "Returned here", color: "#4f46e5", ink: "#3730a3" },
  { key: "moved", name: "Moved to another college", color: "#0d9488", ink: "#0f766e" },
  { key: "no_enrollment", name: "No enrollment found", color: "#8b8b94", ink: "#3f3f46" },
] as const;

/** Where students who moved went, by the type of their most recent other college. */
export const COLLEGE_TYPES = [
  { key: "four_year", name: "4-year college", color: "#0f766e", ink: "#115e59" },
  { key: "two_year", name: "2-year college", color: "#14b8a6", ink: "#0f766e" },
  { key: "not_on_record", name: "Type not on record", color: "url(#paths-hatch)", ink: "#3f3f46" },
] as const;

export type PathKey = (typeof PATHS)[number]["key"];

export type PathGroup = {
  key: string;
  label: string;
  /** Hidden groups have no counts. */
  shown: boolean;
  students: number;
  counts: Record<PathKey, number>;
  split: CollegeTypeSplit | null;
};

/** The label for a paths row, e.g. "Pell grant · Full-time"; "All students" for everyone. */
function labelOf(row: PathsRow, groupBy: Dimension[]): string {
  if (Object.keys(row.group).length === 0) return "All students";
  return groupBy.map((dimension) => valueLabel(dimension, row.group[dimension] ?? "")).join(" · ");
}

/** Turn API rows into groups, everyone first, then each grouping's display order. */
export function buildPathGroups(response: PathsResponse): PathGroup[] {
  const groupBy = response.meta.group_by;
  const order = (row: PathsRow) => groupBy.map((dimension) => valueOrder(dimension, row.group[dimension] ?? ""));
  const sorted = [...response.rows].sort((a, b) => {
    const aEveryone = Object.keys(a.group).length === 0 ? -1 : 0;
    const bEveryone = Object.keys(b.group).length === 0 ? -1 : 0;
    if (aEveryone !== bEveryone) return aEveryone - bEveryone;
    const [aOrder, bOrder] = [order(a), order(b)];
    for (let index = 0; index < aOrder.length; index += 1) {
      if (aOrder[index] !== bOrder[index]) return aOrder[index] - bOrder[index];
    }
    return 0;
  });
  return sorted.map((row) => {
    const shown = row.status === "ok" && row.students !== null && row.students > 0;
    return {
      key: groupBy.map((dimension) => row.group[dimension] ?? "").join("|") || "all",
      label: labelOf(row, groupBy),
      shown,
      students: shown ? (row.students as number) : 0,
      counts: {
        returned_here: row.returned_here ?? 0,
        moved: row.moved ?? 0,
        no_enrollment: row.no_enrollment ?? 0,
      },
      split: shown ? row.college_type : null,
    };
  });
}

/** One path's share of the group, e.g. "13.1%". */
export function shareOf(group: PathGroup, key: PathKey): string {
  return formatPercent(percentOf(group.counts[key], group.students));
}

// ----- Sankey layout: a fixed 1000 x 380 drawing, so label spacing holds at every width -----

export const SANKEY_WIDTH = 1000;
export const SANKEY_HEIGHT = 380;
const TOP = 18;
const INNER = 344;
const GAP = 14;
const NODE = 14;
const COLUMN_ONE = 400;
const COLUMN_TWO = 770;

export type Ribbon = { key: string; d: string; fill: string };
export type SankeyNode = { key: string; x: number; y: number; height: number; fill: string; outlined: boolean };
export type SankeyLabel = { key: string; leftPercent: number; top: number; value: string; name: string; ink: string; size: number; narrow: boolean };

/** A filled ribbon from one node to another: top curve out, bottom curve back, so its width is exact. */
function ribbon(x0: number, top0: number, bottom0: number, x1: number, top1: number, bottom1: number): string {
  const middle = (x0 + x1) / 2;
  const f = (value: number) => value.toFixed(1);
  return (
    `M${x0} ${f(top0)} C${middle} ${f(top0)} ${middle} ${f(top1)} ${x1} ${f(top1)} ` +
    `L${x1} ${f(bottom1)} C${middle} ${f(bottom1)} ${middle} ${f(bottom0)} ${x0} ${f(bottom0)} Z`
  );
}

/** Keep labels a minimum gap apart; if the last would run off the bottom, move the stack up. */
function spread(centers: number[], gap: number): number[] {
  const positions: number[] = [];
  let last = -Infinity;
  for (const center of centers) {
    last = Math.max(center, last + gap);
    positions.push(last);
  }
  for (let index = positions.length - 1; index >= 0; index -= 1) {
    const limit = index === positions.length - 1 ? SANKEY_HEIGHT - 22 : positions[index + 1] - gap;
    positions[index] = Math.max(22, Math.min(positions[index], limit));
  }
  return positions;
}

/** Ribbons, nodes and labels for one group's year-2 flow, with the moved students split by college type. */
export function sankeyLayout(group: PathGroup, withCounts: boolean): { ribbons: Ribbon[]; nodes: SankeyNode[]; labels: SankeyLabel[] } {
  const ribbons: Ribbon[] = [];
  const nodes: SankeyNode[] = [];
  const labels: SankeyLabel[] = [];
  const total = group.students;
  const scale = (INNER - 2 * GAP) / total;
  const start = TOP + GAP;
  const name = (text: string, count: number) => (withCounts ? `${text} · ${count.toLocaleString("en-US")}` : text);

  nodes.push({ key: "entered", x: 0, y: start, height: total * scale, fill: "#312e81", outlined: false });
  labels.push({ key: "entered", leftPercent: 2.6, top: start + (total * scale) / 2, value: total.toLocaleString("en-US"), name: "entered", ink: "#1e1b4b", size: 24, narrow: false });

  let y = TOP;
  let from = start;
  const columnOne = PATHS.map((path) => {
    const height = group.counts[path.key] * scale;
    const node = { ...path, y, height };
    ribbons.push({ key: path.key, d: ribbon(NODE, from, from + height, COLUMN_ONE, y, y + height), fill: `url(#paths-${path.key})` });
    nodes.push({ key: path.key, x: COLUMN_ONE, y, height: Math.max(height, 3), fill: path.color, outlined: false });
    from += height;
    y += height + GAP;
    return node;
  });
  spread(columnOne.map((node) => node.y + node.height / 2), 50).forEach((top, index) => {
    const node = columnOne[index];
    labels.push({
      key: node.key,
      leftPercent: (COLUMN_ONE + 24) / 10,
      top,
      value: shareOf(group, node.key),
      name: name(node.name, group.counts[node.key]),
      ink: node.ink,
      size: 22,
      narrow: false,
    });
  });

  if (group.split) {
    const moved = columnOne[1];
    const split = group.split;
    const spacing = 40;
    const block = moved.height + 2 * spacing;
    let splitY = Math.min(Math.max(moved.y + moved.height / 2 - block / 2, TOP), TOP + INNER - block);
    let splitFrom = moved.y;
    const columnTwo = COLLEGE_TYPES.map((type) => {
      const height = split[type.key] * scale;
      const node = { ...type, y: splitY, height };
      ribbons.push({ key: type.key, d: ribbon(COLUMN_ONE + NODE, splitFrom, splitFrom + height, COLUMN_TWO, splitY, splitY + height), fill: `url(#paths-${type.key})` });
      nodes.push({ key: type.key, x: COLUMN_TWO, y: splitY, height: Math.max(height, 3), fill: type.color, outlined: type.key !== "four_year" });
      splitFrom += height;
      splitY += height + spacing;
      return node;
    });
    const movedCount = group.counts.moved;
    spread(columnTwo.map((node) => node.y + Math.min(node.height, 30) / 2), 48).forEach((top, index) => {
      const node = columnTwo[index];
      labels.push({
        key: node.key,
        leftPercent: (COLUMN_TWO + 24) / 10,
        top,
        value: formatPercent(percentOf(split[node.key], movedCount)),
        name: name(node.name, split[node.key]),
        ink: node.ink,
        size: 19,
        narrow: true,
      });
    });
  }
  return { ribbons, nodes, labels };
}

/** The chart's text alternative: every path and the college-type split in words. */
export function sankeyDescription(group: PathGroup, cohortText: string): string {
  const parts = PATHS.map((path) => `${group.counts[path.key].toLocaleString("en-US")} ${path.name.toLowerCase()}`).join(", ");
  const split = group.split
    ? ` Of the ${group.counts.moved.toLocaleString("en-US")} who moved: ${COLLEGE_TYPES.map((type) => `${(group.split as CollegeTypeSplit)[type.key].toLocaleString("en-US")} ${type.name.toLowerCase()}`).join(", ")}.`
    : "";
  return `Of ${group.students.toLocaleString("en-US")} students in ${group.label === "All students" ? "the class" : group.label} who entered in ${cohortText}: ${parts} in year 2.${split}`;
}
