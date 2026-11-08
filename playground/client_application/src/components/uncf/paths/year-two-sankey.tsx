import { cn } from "@/lib/utils";

import { COLLEGE_TYPES, PATHS, type PathGroup, SANKEY_HEIGHT, SANKEY_WIDTH, sankeyDescription, sankeyLayout } from "./paths-model";

type YearTwoSankeyProps = {
  group: PathGroup;
  cohortText: string;
  withCounts: boolean;
};

// Gradients run from the entering class's indigo to each path's color.
const GRADIENTS = [
  { key: "returned_here", from: "#6366f1", to: "#4f46e5", x1: 14, x2: 400, opacity: [0.2, 0.62] },
  { key: "moved", from: "#6366f1", to: "#0d9488", x1: 14, x2: 400, opacity: [0.16, 0.62] },
  { key: "no_enrollment", from: "#6366f1", to: "#8b8b94", x1: 14, x2: 400, opacity: [0.12, 0.55] },
  { key: "four_year", from: "#0d9488", to: "#0f766e", x1: 414, x2: 770, opacity: [0.32, 0.7] },
  { key: "two_year", from: "#0d9488", to: "#14b8a6", x1: 414, x2: 770, opacity: [0.28, 0.72] },
  { key: "not_on_record", from: "#0d9488", to: "#94a3b8", x1: 414, x2: 770, opacity: [0.24, 0.6] },
];

/** Where one group's students were in year 2, as filled ribbons. Hover a ribbon to bring it forward. */
export function YearTwoSankey({ group, cohortText, withCounts }: YearTwoSankeyProps) {
  const { ribbons, nodes, labels } = sankeyLayout(group, withCounts);
  return (
    <div className="flex flex-col gap-3">
      <div aria-hidden className="relative h-7 text-[11px] font-semibold tracking-wider uppercase">
        <span className="absolute left-0 rounded-full bg-indigo-50 px-2.5 py-1 text-indigo-900 dark:bg-indigo-950 dark:text-indigo-200">Entered {cohortText}</span>
        <span className="absolute left-[40%] rounded-full bg-muted px-2.5 py-1 text-muted-foreground">Year 2</span>
        {group.split && (
          <span className="absolute right-0 rounded-full bg-teal-50 px-2.5 py-1 text-teal-900 dark:bg-teal-950 dark:text-teal-200">Of those who moved</span>
        )}
      </div>
      {/* The drawing stretches sideways but keeps a fixed height, so labels placed in pixels never collide. */}
      <div className="group/sankey relative" style={{ height: SANKEY_HEIGHT }}>
        <svg
          viewBox={`0 0 ${SANKEY_WIDTH} ${SANKEY_HEIGHT}`}
          preserveAspectRatio="none"
          width="100%"
          height={SANKEY_HEIGHT}
          role="img"
          aria-label={sankeyDescription(group, cohortText)}
          className="block overflow-visible"
        >
          <defs>
            {GRADIENTS.map((gradient) => (
              <linearGradient key={gradient.key} id={`paths-${gradient.key}`} gradientUnits="userSpaceOnUse" x1={gradient.x1} y1={0} x2={gradient.x2} y2={0}>
                <stop offset={0} stopColor={gradient.from} stopOpacity={gradient.opacity[0]} />
                <stop offset={1} stopColor={gradient.to} stopOpacity={gradient.opacity[1]} />
              </linearGradient>
            ))}
            <pattern id="paths-hatch" patternUnits="userSpaceOnUse" width={6} height={6} patternTransform="rotate(45)">
              <rect width={6} height={6} fill="#f0fdfa" />
              <rect width={2.5} height={6} fill="#0f766e" />
            </pattern>
          </defs>
          {ribbons.map((ribbon) => (
            <path
              key={ribbon.key}
              d={ribbon.d}
              fill={ribbon.fill}
              className="transition-opacity duration-200 group-hover/sankey:opacity-30 hover:!opacity-100 motion-safe:animate-in motion-safe:fade-in motion-safe:duration-700"
            />
          ))}
          {nodes.map((node) => (
            <rect
              key={node.key}
              x={node.x}
              y={node.y}
              width={14}
              height={node.height}
              rx={4}
              fill={node.fill}
              stroke={node.outlined ? "#0f766e" : "none"}
              strokeWidth={node.outlined ? 1 : 0}
              vectorEffect="non-scaling-stroke"
            />
          ))}
        </svg>
        <div aria-hidden className="pointer-events-none absolute inset-0">
          {labels.map((label) => (
            <span
              key={label.key}
              className={cn(
                "absolute flex -translate-y-1/2 flex-col rounded-lg bg-background/85 px-2 py-0.5 leading-tight backdrop-blur-sm motion-safe:animate-in motion-safe:fade-in motion-safe:duration-700",
                label.narrow ? "max-w-[21%]" : "whitespace-nowrap",
              )}
              style={{ left: `${label.leftPercent}%`, top: label.top }}
            >
              <span className="font-bold tracking-tight tabular-nums" style={{ fontSize: label.size, color: label.ink }}>
                {label.value}
              </span>
              <span className="text-[12.5px] font-medium text-muted-foreground">{label.name}</span>
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}

/** The chart as a table, for anyone who prefers rows, and for narrow screens. */
export function YearTwoTable({ group, cohortText }: { group: PathGroup; cohortText: string }) {
  const share = (count: number, base: number) => `${(Math.round((count / base) * 1000) / 10).toFixed(1)}%`;
  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse text-sm">
        <caption className="pb-2 text-left text-xs text-muted-foreground">
          {group.label} · entered {cohortText} · year 2
        </caption>
        <thead>
          <tr className="border-b text-left">
            <th scope="col" className="py-2 pr-3 font-semibold">Where students were</th>
            <th scope="col" className="py-2 pr-3 text-right font-semibold">Students</th>
            <th scope="col" className="py-2 text-right font-semibold">Share</th>
          </tr>
        </thead>
        <tbody>
          {PATHS.map((path) => (
            <tr key={path.key} className="border-b border-muted">
              <td className="py-2 pr-3">{path.name}</td>
              <td className="py-2 pr-3 text-right tabular-nums">{group.counts[path.key].toLocaleString("en-US")}</td>
              <td className="py-2 text-right tabular-nums">{share(group.counts[path.key], group.students)}</td>
            </tr>
          ))}
          {group.split &&
            COLLEGE_TYPES.map((type) => (
              <tr key={type.key} className="border-b border-muted">
                <td className="py-2 pr-3 text-muted-foreground">Moved: {type.name}</td>
                <td className="py-2 pr-3 text-right tabular-nums">{(group.split as NonNullable<PathGroup["split"]>)[type.key].toLocaleString("en-US")}</td>
                <td className="py-2 text-right tabular-nums">
                  {share((group.split as NonNullable<PathGroup["split"]>)[type.key], group.counts.moved)} of those who moved
                </td>
              </tr>
            ))}
        </tbody>
      </table>
    </div>
  );
}
