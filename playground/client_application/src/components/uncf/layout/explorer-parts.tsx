// The design's building blocks for a tab: cards, number tiles, legends, bars, tables and the "how it's counted" note.
import { cn } from "@/lib/utils";

import type { RetentionType } from "./explorer-api";
import { hiddenCount } from "./small-groups";

/** A white card with a border, the design's main container. */
export function Card({ className, children }: { className?: string; children: React.ReactNode }) {
  return (
    <section className={cn("min-w-0 rounded-[10px] border border-(--uncf-line) bg-(--uncf-surface) p-5 md:px-7.5 md:py-6.5", className)}>
      {children}
    </section>
  );
}

type CardHeadProps = { title: string; subtitle?: React.ReactNode; aside?: React.ReactNode; className?: string };

/** A card's title, an optional line under it, and anything that sits on the right, like a legend. */
export function CardHead({ title, subtitle, aside, className }: CardHeadProps) {
  return (
    <div className={cn("mb-5 flex flex-wrap items-start justify-between gap-x-6 gap-y-3", className)}>
      <div className="min-w-0">
        <h3 className="text-[21px] font-semibold">{title}</h3>
        {subtitle && <p className="mt-1 text-(--uncf-ink-3)">{subtitle}</p>}
      </div>
      {aside}
    </div>
  );
}

/** A row of number tiles: four or three across on a wide screen, fewer on a narrow one. */
export function KpiGrid({ columns, children }: { columns: 3 | 4; children: React.ReactNode }) {
  return (
    <div className={cn("grid gap-5", columns === 4 ? "grid-cols-1 min-[481px]:grid-cols-2 min-[961px]:grid-cols-4" : "grid-cols-1 min-[961px]:grid-cols-3")}>
      {children}
    </div>
  );
}

type KpiProps = { label: string; value: string; note: React.ReactNode; tone?: "blue" | "warn" };

/** One number tile: what it is, the number, and a note under it. */
export function Kpi({ label, value, note, tone }: KpiProps) {
  return (
    <div className="min-w-0 rounded-[10px] border border-(--uncf-line) bg-(--uncf-surface) px-6.5 py-5.5">
      <div className="font-medium text-(--uncf-ink-2)">{label}</div>
      <div
        className={cn(
          "uncf-num my-1.5 text-[42px] leading-tight font-medium tracking-[-0.02em]",
          tone === "blue" && "text-(--uncf-blue)",
          tone === "warn" && "text-(--uncf-orange-ink)",
        )}
      >
        {value}
      </div>
      <div className="text-sm text-(--uncf-ink-3)">{note}</div>
    </div>
  );
}

/** A chart's key: a small color square per series. Colors are CSS values, e.g. "var(--uncf-blue)". */
export function Legend({ items }: { items: { label: string; color: string }[] }) {
  return (
    <div className="flex flex-wrap gap-x-4.5 gap-y-1 text-sm text-(--uncf-ink-3)">
      {items.map((item) => (
        <span key={item.label} className="inline-flex items-center">
          <i className="mr-1.5 inline-block size-3 rounded-[3px]" style={{ background: item.color }} aria-hidden />
          {item.label}
        </span>
      ))}
    </div>
  );
}

/** The note at the foot of a card that says how its numbers are counted. */
export function Counted({ lead = "How it’s counted:", children }: { lead?: string; children: React.ReactNode }) {
  return (
    <div className="mt-6 border-t border-(--uncf-line) pt-4.5 text-sm text-(--uncf-ink-2)">
      <b className="font-semibold text-(--uncf-ink)">{lead}</b> {children}
    </div>
  );
}

type TrackBarProps = { share: number | null; color: string; height?: number; label: string };

/** A horizontal bar on a grey track, filled to a share from 0 to 1. A hidden share leaves the track empty. */
export function TrackBar({ share, color, height = 14, label }: TrackBarProps) {
  return (
    <div
      className="overflow-hidden rounded-[3px] bg-(--uncf-track)"
      style={{ height }}
      role="img"
      aria-label={label}
    >
      {share !== null && <div className="h-full rounded-[3px]" style={{ width: `${Math.min(share, 1) * 100}%`, background: color }} />}
    </div>
  );
}

/** Two cards side by side on a wide screen, stacked on a narrow one. */
export function TwoColumns({ children }: { children: React.ReactNode }) {
  return <div className="grid gap-5 min-[961px]:grid-cols-2">{children}</div>;
}

/** A table cell's classes: numbers line up on the right. */
export const tableClasses = {
  table: "w-full border-collapse tabular-nums",
  th: "border-b border-(--uncf-line-2) py-2 text-left text-sm font-semibold text-(--uncf-ink-2)",
  td: "border-b border-(--uncf-line) py-3.5 [tr:last-child_&]:border-b-0",
  right: "text-right",
};

/** A grey placeholder block for content that is still loading. */
export function LoadingBlock({ className }: { className?: string }) {
  return <div className={cn("animate-pulse rounded-[10px] bg-(--uncf-band) motion-reduce:animate-none", className)} aria-hidden />;
}

type MessageCardProps = { title: string; children?: React.ReactNode; onRetry?: () => void };

/** A card that explains why there are no numbers: too few students, or the data couldn't load. */
export function MessageCard({ title, children, onRetry }: MessageCardProps) {
  return (
    <Card className="flex flex-col items-start gap-2">
      <h3 className="text-[19px] font-semibold">{title}</h3>
      {children && <div className="max-w-[70ch] text-(--uncf-ink-2)">{children}</div>}
      {onRetry && (
        <button
          type="button"
          data-pdf-skip
          onClick={onRetry}
          className="mt-2 cursor-pointer rounded-md border border-(--uncf-line-2) bg-(--uncf-surface) px-4 py-2 font-medium hover:border-(--uncf-ink-3)"
        >
          Try again
        </button>
      )}
    </Card>
  );
}

/** A count for display: 1,234, or "Under 10" when it's hidden (minStudents is the answer's meta.min_students). */
export function formatCount(count: number | null, minStudents: number): string {
  return count === null ? hiddenCount(minStudents) : count.toLocaleString("en-US");
}

/**
 * How a page names the retention measure an answer used (its meta.retention_type), in the shared definitions' words
 * (measures/definitions.py): retention is "Returned here", federal_retention is "Back next fall".
 */
export function retentionWords(type: RetentionType | undefined, term: string) {
  if (type === "federal") {
    return { name: "Back next fall", lower: "back next fall", how: `took a course here in ${term}, the fall after year 1` };
  }
  return {
    name: "Returned here",
    lower: "returned here",
    how: "enrolled here again in the next academic year, or earned a credential here by then (the PDP retention flag)",
  };
}

/** A share from 0 to 1 as a whole percent, e.g. 47%; an en dash when it's hidden. */
export function formatShare(share: number | null): string {
  return share === null ? "–" : `${Math.round(share * 100)}%`;
}

/** count ÷ total, or null when either is hidden or the total is 0. */
export function shareOf(count: number | null, total: number | null): number | null {
  return count === null || !total ? null : count / total;
}

/** The design's orange notice, for something the reader must know before reading the numbers. */
export function Notice({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div role="note" className="flex items-start gap-3.5 rounded-lg bg-(--uncf-warn-bg) px-5.5 py-4 text-(--uncf-orange-ink)">
      <svg width="22" height="22" viewBox="0 0 22 22" aria-hidden className="mt-px shrink-0">
        <path d="M11 3 2 19h18L11 3Z" stroke="currentColor" strokeWidth="1.6" fill="none" strokeLinejoin="round" />
        <path d="M11 9v5M11 16.3v.1" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      </svg>
      <div>
        <b className="font-semibold">{title}</b> {children}
      </div>
    </div>
  );
}
