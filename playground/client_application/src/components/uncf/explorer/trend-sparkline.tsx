import type { Cohort } from "@/app/(app)/uncf/data";

import { formatPercent, type TrendPoint } from "./bars";
import { cohortLabel } from "./labels";

const WIDTH = 96;
const HEIGHT = 28;

type TrendSparklineProps = {
  points: TrendPoint[];
  /** The class on screen: its point is the large dark one. */
  current: Cohort;
  scale: [number, number];
  /** The all-students line is drawn in the foreground color; groups in indigo. */
  emphasis?: boolean;
};

/** A tiny line of one group's rate across entering classes, with its first and last values as text. */
export function TrendSparkline({ points, current, scale, emphasis = false }: TrendSparklineProps) {
  const shown = points.filter((point) => point.percent !== null);
  if (shown.length === 0) return null;
  const [low, high] = scale;
  const x = (index: number) => 4 + (index * (WIDTH - 8)) / Math.max(points.length - 1, 1);
  const y = (percent: number) => HEIGHT - 4 - ((percent - low) / (high - low || 1)) * (HEIGHT - 8);

  // Break the line at a missing class instead of drawing through it.
  let path = "";
  let penDown = false;
  points.forEach((point, index) => {
    if (point.percent === null) {
      penDown = false;
      return;
    }
    path += `${penDown ? " L" : " M"}${x(index).toFixed(1)} ${y(point.percent).toFixed(1)}`;
    penDown = true;
  });

  const first = shown[0];
  const last = shown[shown.length - 1];
  const readerText = `Trend across entering classes: ${points
    .map((point) => `${cohortLabel(point.cohort)} ${point.percent === null ? "not shown" : formatPercent(point.percent)}${point.provisional && point.percent !== null ? " (year 2 still arriving)" : ""}`)
    .join(", ")}.`;

  return (
    <span className="flex flex-col items-end gap-0.5">
      <svg width={WIDTH} height={HEIGHT} viewBox={`0 0 ${WIDTH} ${HEIGHT}`} aria-hidden className="overflow-visible">
        <path
          d={path.trim()}
          fill="none"
          strokeWidth={2}
          strokeLinecap="round"
          strokeLinejoin="round"
          className={emphasis ? "stroke-foreground/70" : "stroke-indigo-500 dark:stroke-indigo-300"}
        />
        {points.map((point, index) => {
          if (point.percent === null) return null;
          const isCurrent = point.cohort === current;
          const size = isCurrent ? 7 : 5;
          return (
            <rect
              key={point.cohort}
              x={x(index) - size / 2}
              y={y(point.percent) - size / 2}
              width={size}
              height={size}
              rx={3}
              strokeWidth={1.5}
              className={
                point.provisional
                  ? `fill-background ${isCurrent ? "stroke-indigo-700 dark:stroke-indigo-300" : "stroke-muted-foreground"}`
                  : isCurrent
                    ? "fill-indigo-700 dark:fill-indigo-300"
                    : "fill-muted-foreground"
              }
            />
          );
        })}
      </svg>
      {shown.length >= 2 && (
        <span aria-hidden className="text-[11px] whitespace-nowrap text-muted-foreground tabular-nums">
          {formatPercent(first.percent as number)} → {formatPercent(last.percent as number)}
        </span>
      )}
      <span className="sr-only">{readerText}</span>
    </span>
  );
}
