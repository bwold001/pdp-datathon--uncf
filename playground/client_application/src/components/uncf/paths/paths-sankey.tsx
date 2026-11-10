import { formatShare } from "@/components/uncf/layout/explorer-parts";

import { type PathStatus, type PathsResponse, type TermCounts, pathStatuses, statusStyle, studentsLabel, termNames } from "./paths-data";

// The drawing's grid, in viewBox units: three columns, bars this wide, and this much room for the column titles.
const COLUMN_X = [0, 440, 860];
const NODE_WIDTH = 12;
const TOP = 50;
const COHORT_HEIGHT = 260;
const NODE_GAP = 14;
const WIDTH = 1040;

type Node = { status: PathStatus; count: number; share: number | null; top: number; height: number };
type Band = { key: string; title: string; fill: string; opacity: number; from: [number, number, number]; to: [number, number, number] };

/** The student flow from the design: everyone who entered, then each status in the next two terms. */
export function PathsSankey({ data }: { data: PathsResponse }) {
  if (!data.students || !data.columns || !data.moves) return null;
  const total = data.students;
  const scale = COHORT_HEIGHT / total;
  const names = termNames(data);
  const next = stack(data.columns.next, scale);
  const year2 = stack(data.columns.year2, scale);
  const bands: Band[] = [];

  // Everyone who entered splits into the second term's statuses.
  let cohortTop = 0;
  for (const node of next) {
    bands.push({
      key: `entered-${node.status}`,
      title: `${firstMovePhrase(node.status, names.next)} · ${node.count.toLocaleString("en-US")}`,
      fill: statusStyle[node.status].band,
      opacity: 0.75,
      from: [0, cohortTop, cohortTop + node.height],
      to: [1, node.top, node.top + node.height],
    });
    cohortTop += node.height;
  }

  // Each second-term status splits into the third term's: leaving in status order, arriving in status order.
  const leaving = new Map(next.map((node) => [node.status, node.top]));
  const arriving = new Map(year2.map((node) => [node.status, node.top]));
  for (const before of pathStatuses) {
    for (const after of pathStatuses) {
      const move = data.moves.find((m) => m.from === before && m.to === after);
      const count = move?.students;
      if (!count || !leaving.has(before) || !arriving.has(after)) continue;
      const height = count * scale;
      const from = leaving.get(before)!;
      const to = arriving.get(after)!;
      const returned = before === "stopped" && after === "here";
      bands.push({
        key: `${before}-${after}`,
        title: `${secondMovePhrase(before, after, names.next, names.year2)} · ${count.toLocaleString("en-US")}`,
        fill: returned ? "var(--uncf-blue-mid)" : statusStyle[after].band,
        opacity: returned ? 0.9 : 0.75,
        from: [1, from, from + height],
        to: [2, to, to + height],
      });
      leaving.set(before, from + height);
      arriving.set(after, to + height);
    }
  }
  // Moves are drawn in the order above, so bands arriving at a node stack by where they came from.
  const height = TOP + Math.max(COHORT_HEIGHT, columnHeight(next), columnHeight(year2)) + 12;
  const titles = [names.entered ? `Entered · ${names.entered}` : "Entered", capitalize(names.next), `${capitalize(names.year2)} · year 2`];

  return (
    <svg
      viewBox={`0 0 ${WIDTH} ${height}`}
      role="img"
      aria-label={summary(data)}
      className="group/sankey block h-auto w-full min-w-180"
    >
      {titles.map((title, column) => (
        <text key={title} x={COLUMN_X[column]} y={18} className="fill-(--uncf-ink-2) text-[15px] font-semibold">
          {title}
        </text>
      ))}
      {bands.map((band) => (
        <path
          key={band.key}
          d={ribbon(band)}
          fill={band.fill}
          fillOpacity={band.opacity}
          className="cursor-pointer transition-opacity group-hover/sankey:opacity-45 hover:opacity-100! motion-reduce:transition-none"
        >
          <title>{band.title}</title>
        </path>
      ))}
      <rect x={COLUMN_X[0]} y={TOP} width={NODE_WIDTH} height={COHORT_HEIGHT} rx={2} fill="var(--uncf-ink)" />
      {[...next.map((node) => ({ node, column: 1 })), ...year2.map((node) => ({ node, column: 2 }))].map(({ node, column }) => (
        <rect
          key={`${column}-${node.status}`}
          x={COLUMN_X[column]}
          y={TOP + node.top}
          width={NODE_WIDTH}
          height={Math.max(node.height, 1)}
          rx={2}
          fill={statusStyle[node.status].node}
        />
      ))}
      <text x={24} y={TOP + COHORT_HEIGHT / 2 + 5} className={labelClass}>
        {total.toLocaleString("en-US")} students
      </text>
      {spread(next, 20).map(({ node, y }, index) => (
        <text
          key={node.status}
          x={COLUMN_X[1] + NODE_WIDTH + 10}
          y={TOP + y + 5}
          className={index === 0 ? labelClass : `${labelClass} text-[14px]! font-medium!`}
        >
          {statusStyle[node.status].short} · {node.count.toLocaleString("en-US")}
          {index === 0 && node.share !== null ? ` (${formatShare(node.share)})` : ""}
        </text>
      ))}
      {spread(year2, 42).map(({ node, y }) => (
        <g key={node.status}>
          <text x={COLUMN_X[2] + NODE_WIDTH + 14} y={TOP + y} className={labelClass}>
            {statusStyle[node.status].short === "Transferred" ? "Transferred out" : statusStyle[node.status].short}
          </text>
          <text x={COLUMN_X[2] + NODE_WIDTH + 14} y={TOP + y + 19} className="uncf-num fill-(--uncf-ink-3) text-[14px]">
            {node.count.toLocaleString("en-US")}
            {node.share !== null ? ` · ${formatShare(node.share)}` : ""}
          </text>
        </g>
      ))}
    </svg>
  );
}

// Labels sit on the bands, so a white outline keeps them readable.
const labelClass =
  "fill-(--uncf-ink) text-[15px] font-semibold [paint-order:stroke] stroke-(--uncf-surface) [stroke-width:4px] [stroke-linejoin:round]";

/** A column's bars, top to bottom in status order. Hidden counts (under 10) and empty ones get no bar. */
function stack(counts: TermCounts, scale: number): Node[] {
  const nodes: Node[] = [];
  let top = 0;
  for (const status of pathStatuses) {
    const count = counts[status];
    if (!count) continue;
    const height = count * scale;
    nodes.push({ status, count, share: counts.shares[status], top, height });
    top += height + NODE_GAP;
  }
  return nodes;
}

/** How tall a column's bars are, gaps included. */
function columnHeight(nodes: Node[]): number {
  const last = nodes.at(-1);
  return last ? last.top + last.height : 0;
}

/** Each bar's label position: its middle, pushed down when it would overlap the label above. */
function spread(nodes: Node[], spacing: number): { node: Node; y: number }[] {
  let lowest = -Infinity;
  return nodes.map((node) => {
    const y = Math.max(node.top + node.height / 2, lowest + spacing);
    lowest = y;
    return { node, y };
  });
}

/** The SVG path of a band from one bar to another: a curved ribbon between two vertical spans. */
function ribbon({ from, to }: Band): string {
  const [fromColumn, fromTop, fromBottom] = from;
  const [toColumn, toTop, toBottom] = to;
  const x0 = COLUMN_X[fromColumn] + NODE_WIDTH;
  const x1 = COLUMN_X[toColumn];
  const middle = (x0 + x1) / 2;
  const y = (value: number) => TOP + value;
  return [
    `M${x0},${y(fromTop)}`,
    `C${middle},${y(fromTop)} ${middle},${y(toTop)} ${x1},${y(toTop)}`,
    `L${x1},${y(toBottom)}`,
    `C${middle},${y(toBottom)} ${middle},${y(fromBottom)} ${x0},${y(fromBottom)}`,
    "Z",
  ].join(" ");
}

/** The hover text for a band from the entering class into the second term. */
function firstMovePhrase(status: PathStatus, next: string): string {
  if (status === "here") return `Enrolled in ${next}`;
  if (status === "credential") return `Earned a credential by ${next}`;
  if (status === "elsewhere") return `Transferred out by ${next}`;
  return `Stopped out by ${next}`;
}

/** The hover text for a band from the second term into the third, in the design's words where it has them. */
function secondMovePhrase(before: PathStatus, after: PathStatus, next: string, year2: string): string {
  if (before === "here" && after === "here") return `Stayed enrolled to ${year2}`;
  if (before === "here" && after === "elsewhere") return `Enrolled in ${next}, transferred by ${year2}`;
  if (before === "here" && after === "stopped") return `Enrolled in ${next}, stopped out by ${year2}`;
  if (before === "elsewhere" && after === "elsewhere") return "Still transferred out";
  if (before === "elsewhere" && after === "here") return `Came back from another college by ${year2}`;
  if (before === "elsewhere" && after === "stopped") return `Transferred out in ${next}, no record in ${year2}`;
  if (before === "stopped" && after === "here") return "Returned after a term away";
  if (before === "stopped" && after === "elsewhere") return `No record in ${next}, at another college in ${year2}`;
  if (before === "here" && after === "credential") return `Enrolled in ${next}, earned a credential by ${year2}`;
  if (before === "elsewhere" && after === "credential") return `Transferred out in ${next}, earned a credential here by ${year2}`;
  if (before === "stopped" && after === "credential") return `No record in ${next}, earned a credential by ${year2}`;
  if (before === "credential" && after === "credential") return "Still holds a credential";
  if (before === "credential" && after === "here") return `Earned a credential, took a course here in ${year2}`;
  if (before === "credential" && after === "elsewhere") return `Earned a credential, at another college in ${year2}`;
  if (before === "credential") return `Earned a credential, no record in ${year2}`;
  return "Still stopped out";
}

/** The chart's text alternative: who entered and where they were in the third term. */
function summary(data: PathsResponse): string {
  const names = termNames(data);
  const year2 = data.columns!.year2;
  const part = (count: number | null, words: string) => `${count === null ? "under 10" : count.toLocaleString("en-US")} ${words}`;
  return `Flow of ${data.students!.toLocaleString("en-US")} students (${studentsLabel(data)}) through ${names.next} and ${names.year2}: ${part(year2.here, "enrolled here")}, ${part(year2.credential, "with a credential")}, ${part(year2.elsewhere, "transferred out")}, ${part(year2.stopped, "stopped out")} by ${names.year2}.`;
}

/** The text with its first letter in capitals. */
function capitalize(text: string): string {
  return text.charAt(0).toUpperCase() + text.slice(1);
}
