import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";
import type { FieldProfile } from "./dictionary-types";

/** Each bar is a share of all supplied rows, including rows without a value. */
export function ValueDistribution({ profile, compact = false }: { profile: FieldProfile; compact?: boolean }) {
  return (
    <div className={cn("flex flex-col gap-3", compact && "text-sm")}>
      <p className="text-sm text-muted-foreground">{profile.fillPercent}% of rows have a value · {profile.distinctCount.toLocaleString()} distinct</p>
      <ul className="flex flex-col gap-2">
        {profile.topValues.map(({ value, count }) => (
          <li key={value} className="grid grid-cols-[minmax(0,1fr)_minmax(0,2fr)_auto] items-center gap-2">
            <code className="truncate" title={value}>{value || "(blank)"}</code>
            <Progress aria-label={`${value || "Blank"}: share of all rows`} value={profile.totalRows > 0 ? Math.min(100, Math.max(0, count / profile.totalRows * 100)) : 0} />
            <span className="tabular-nums">{count.toLocaleString()}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
