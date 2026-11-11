import { formatShare } from "@/components/uncf/layout/explorer-parts";
import { hiddenCount } from "@/components/uncf/layout/small-groups";
import { cn } from "@/lib/utils";

import {
  type PathFocus,
  type PathStatus,
  type PathsResponse,
  type TermCounts,
  firstMovePhrase,
  focusedMove,
  pathStatuses,
  sameFocus,
  secondMovePhrase,
  statusStyle,
  studentsLabel,
  termNames,
} from "./paths-data";

// The drawing's grid, in viewBox units: three columns, bars this wide, and this much room for the column titles.
const COLUMN_X = [0, 440, 860];
const NODE_WIDTH = 12;
const TOP = 50;
const COHORT_HEIGHT = 260;
const NODE_GAP = 14;
const WIDTH = 1040;

type Node = { status: PathStatus; count: number; share: number | null; top: number; height: number };
type Band = {
  key: string;
  title: string;
  fill: string;
  opacity: number;
  from: [number, number, number];
  to: [number, number, number];
  /** The students a click on it focuses on. */
  focus: PathFocus;
};

type PathsSankeyProps = {
  data: PathsResponse;
  /** The students the page is focused on, or null for everyone. */
  focus?: PathFocus | null;
  /** Called with a clicked band's or bar's students, or null to show everyone again. Without it, nothing is clickable. */
  onFocusChange?: (focus: PathFocus | null) => void;
};

/**
 * The student flow from the design: everyone who entered, then each status in the next two terms. Clicking a band or a
 * bar focuses the page on its students, and clicking it again (or the entering bar, or Escape) shows everyone.
 */
export function PathsSankey({ data, focus = null, onFocusChange }: PathsSankeyProps) {
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
      focus: { next: node.status, year2: null },
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
        focus: { next: before, year2: after },
      });
      leaving.set(before, from + height);
      arriving.set(after, to + height);
    }
  }
  // Moves are drawn in the order above, so bands arriving at a node stack by where they came from.
  const height = TOP + Math.max(COHORT_HEIGHT, columnHeight(next), columnHeight(year2)) + 12;
  const titles = [names.entered ? `Entered · ${names.entered}` : "Entered", capitalize(names.next), `${capitalize(names.year2)} · year 2`];

  const nodes = [
    ...next.map((node) => ({ node, column: 1, focus: { next: node.status, year2: null } })),
    ...year2.map((node) => ({ node, column: 2, focus: { next: null, year2: node.status } })),
  ];
  const clickable = Boolean(onFocusChange);
  /** Focus on these students, or show everyone again when they're already the focus. */
  const pick = (target: PathFocus) => onFocusChange?.(sameFocus(focus, target) ? null : target);
  /** Props that make a band or bar a toggle for its students. Its label (a text one) is clickable too, not focusable. */
  const toggle = (target: PathFocus, label: string) =>
    clickable
      ? {
          role: "button",
          tabIndex: 0,
          "aria-label": label,
          "aria-pressed": sameFocus(focus, target),
          onClick: () => pick(target),
          onKeyDown: (event: React.KeyboardEvent) => {
            if (event.key !== "Enter" && event.key !== " ") return;
            event.preventDefault();
            pick(target);
          },
        }
      : {};

  return (
    <svg
      viewBox={`0 0 ${WIDTH} ${height}`}
      role={clickable ? "group" : "img"}
      aria-label={summary(data)}
      className={cn("block h-auto w-full min-w-180", !focus && "group/sankey")}
      onKeyDown={(event) => {
        if (event.key === "Escape" && focus) onFocusChange?.(null);
      }}
    >
      {titles.map((title, column) => (
        <text key={title} x={COLUMN_X[column]} y={18} className="fill-(--uncf-ink-2) text-[15px] font-semibold">
          {title}
        </text>
      ))}
      {bands.map((band) => {
        const picked = sameFocus(focus, band.focus);
        return (
          <path
            key={band.key}
            d={ribbon(band)}
            fill={band.fill}
            fillOpacity={band.opacity}
            // A band from the entering class picks the same students as the bar it reaches, so only that bar is a button.
            {...(band.focus.year2 ? toggle(band.focus, band.title) : { onClick: () => pick(band.focus) })}
            className={cn(
              "outline-none transition-opacity focus-visible:stroke-(--uncf-ink) focus-visible:[stroke-width:2px] motion-reduce:transition-none",
              clickable && "cursor-pointer",
              !focus && "group-hover/sankey:opacity-45 hover:opacity-100!",
              focus && !bandInFocus(data, focus, band.focus) && "opacity-15 hover:opacity-45",
              picked && "stroke-(--uncf-ink) [stroke-width:1.5px]",
            )}
          >
            <title>{band.title}</title>
          </path>
        );
      })}
      <rect
        x={COLUMN_X[0]}
        y={TOP}
        width={NODE_WIDTH}
        height={COHORT_HEIGHT}
        rx={2}
        fill="var(--uncf-ink)"
        className={cn(focus && "cursor-pointer")}
        onClick={() => onFocusChange?.(null)}
      />
      {nodes.map(({ node, column, focus: target }) => {
        const title = `${firstMovePhrase(node.status, column === 1 ? names.next : names.year2)} · ${node.count.toLocaleString("en-US")}`;
        return (
          <g
            key={`${column}-${node.status}`}
            {...toggle(target, title)}
            className={cn(
              "group/bar outline-none transition-opacity motion-reduce:transition-none",
              clickable && "cursor-pointer",
              focus && !barInFocus(data, focus, target) && "opacity-30",
            )}
          >
            <title>{title}</title>
            {/* A wider, invisible target, since the bar itself is thin. */}
            <rect x={COLUMN_X[column] - 6} y={TOP + node.top} width={NODE_WIDTH + 12} height={Math.max(node.height, 12)} fill="transparent" />
            <rect
              x={COLUMN_X[column]}
              y={TOP + node.top}
              width={NODE_WIDTH}
              height={Math.max(node.height, 1)}
              rx={2}
              fill={statusStyle[node.status].node}
              className={cn(
                "group-focus-visible/bar:stroke-(--uncf-ink) group-focus-visible/bar:[stroke-width:2px]",
                sameFocus(focus, target) && "stroke-(--uncf-ink) [stroke-width:1.5px]",
              )}
            />
          </g>
        );
      })}
      <text x={24} y={TOP + COHORT_HEIGHT / 2 + 5} className={cn(labelClass, "pointer-events-none")}>
        {total.toLocaleString("en-US")} students
      </text>
      {spread(next, 20).map(({ node, y }, index) => (
        <text
          key={node.status}
          x={COLUMN_X[1] + NODE_WIDTH + 10}
          y={TOP + y + 5}
          className={cn(labelClass, index !== 0 && "text-[14px]! font-medium!", clickable && "cursor-pointer")}
          onClick={() => pick({ next: node.status, year2: null })}
        >
          {statusStyle[node.status].short} · {node.count.toLocaleString("en-US")}
          {index === 0 && node.share !== null ? ` (${formatShare(node.share)})` : ""}
        </text>
      ))}
      {spread(year2, 42).map(({ node, y }) => (
        <g key={node.status} className={cn(clickable && "cursor-pointer")} onClick={() => pick({ next: null, year2: node.status })}>
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

/** A column's bars, top to bottom in status order. Hidden counts (under min_students) and empty ones get no bar. */
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

/** Whether a band carries any of the focused students. */
function bandInFocus(data: PathsResponse, focus: PathFocus, band: PathFocus): boolean {
  if (band.year2) return focusedMove(data, focus, band.next!, band.year2) !== 0;
  // A band from the entering class carries a second-term bar's students: in focus when any of them are.
  return barInFocus(data, focus, band);
}

/** Whether a bar holds any of the focused students. */
function barInFocus(data: PathsResponse, focus: PathFocus, bar: PathFocus): boolean {
  if (bar.next) {
    if (focus.next) return focus.next === bar.next;
    return focusedMove(data, focus, bar.next, focus.year2!) !== 0;
  }
  if (focus.year2) return focus.year2 === bar.year2;
  return focusedMove(data, focus, focus.next!, bar.year2!) !== 0;
}

/** The chart's text alternative: who entered and where they were in the third term. */
function summary(data: PathsResponse): string {
  const names = termNames(data);
  const year2 = data.columns!.year2;
  const part = (count: number | null, words: string) => `${count === null ? hiddenCount(data.meta.min_students).toLowerCase() : count.toLocaleString("en-US")} ${words}`;
  return `Flow of ${data.students!.toLocaleString("en-US")} students (${studentsLabel(data)}) through ${names.next} and ${names.year2}: ${part(year2.here, "enrolled here")}, ${part(year2.credential, "with a credential")}, ${part(year2.elsewhere, "transferred out")}, ${part(year2.stopped, "stopped out")} by ${names.year2}.`;
}

/** The text with its first letter in capitals. */
function capitalize(text: string): string {
  return text.charAt(0).toUpperCase() + text.slice(1);
}
