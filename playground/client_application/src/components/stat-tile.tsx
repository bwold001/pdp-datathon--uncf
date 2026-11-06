import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "cn";

const statTileClasses = "flex h-full min-h-32 flex-col gap-1 rounded-2xl border p-4 sm:p-5";

type StatTileProps = {
  /** The headline number, already formatted, e.g. "10,313". */
  value: React.ReactNode;
  /** A short unit after the number, e.g. "%". */
  unit?: string | null;
  label: React.ReactNode;
  detail?: React.ReactNode;
  className?: string;
};

/** One big number with what it counts underneath. Wrap tiles in a list when there are several. */
export function StatTile({ value, unit, label, detail, className }: StatTileProps) {
  return (
    <div data-slot="stat-tile" className={cn(statTileClasses, className)}>
      <p className="text-3xl font-semibold tracking-tight tabular-nums sm:text-4xl">
        {value}
        {unit && <span className="ml-1 text-base font-normal text-muted-foreground">{unit}</span>}
      </p>
      <p className="text-sm leading-snug font-medium">{label}</p>
      {detail && <p className="text-xs text-muted-foreground">{detail}</p>}
    </div>
  );
}

/** A StatTile-sized placeholder while the numbers load. */
export function StatTileSkeleton({ className }: { className?: string }) {
  return (
    <div data-slot="stat-tile-skeleton" className={cn(statTileClasses, className)}>
      <Skeleton className="h-full rounded-lg" />
    </div>
  );
}
