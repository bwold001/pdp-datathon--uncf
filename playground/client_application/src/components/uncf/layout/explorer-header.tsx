import { cn } from "@/lib/utils";

import type { DataLabel } from "./explorer-api";

import { dataWords, explorerHeader } from "./explorer-config";
import { useDataLabel } from "./explorer-context";
import { explorerWrap } from "./explorer-styles";

/** The white bar at the top: the Explorer's name, its data source and what kind of data is loaded. */
export function ExplorerHeader() {
  const label = useDataLabel();
  return (
    <header className="bg-(--uncf-surface)">
      <div className={cn(explorerWrap, "flex flex-wrap items-center gap-4 py-4.5")}>
        <div className="flex min-w-0 items-center gap-3">
          <ExplorerMark />
          <h1 className="text-xl font-bold tracking-[-0.01em]">{explorerHeader.title}</h1>
        </div>
        <span className="text-sm text-(--uncf-ink-3)">{explorerHeader.source}</span>
        {label && <DataBadge label={label} />}
      </div>
    </header>
  );
}

/** The badge that says what kind of data the numbers come from: the synthetic sample or the school's own files. */
export function DataBadge({ label }: { label: DataLabel }) {
  return (
    <span className="rounded-full bg-(--uncf-warn-bg) px-3 py-0.75 text-[13px] font-semibold text-(--uncf-orange-ink)">
      {dataWords[label].badge}
    </span>
  );
}

/** The blue square logo from the design. */
export function ExplorerMark() {
  return (
    <svg width="34" height="34" viewBox="0 0 34 34" aria-hidden className="shrink-0">
      <rect width="34" height="34" rx="7" fill="var(--uncf-blue)" />
      <path
        d="M11 24h13M12 24l7-14h5"
        stroke="#fff"
        strokeWidth="2.6"
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

