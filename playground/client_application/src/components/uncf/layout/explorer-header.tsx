import { cn } from "@/lib/utils";

import { explorerHeader } from "./explorer-config";
import { explorerWrap } from "./explorer-styles";

/** The white bar at the top: the Explorer's name, its data source, the sample-data badge and Export. */
export function ExplorerHeader() {
  return (
    <header className="bg-(--uncf-surface)">
      <div className={cn(explorerWrap, "flex flex-wrap items-center gap-4 py-4.5")}>
        <div className="flex min-w-0 items-center gap-3">
          <ExplorerMark />
          <h1 className="text-xl font-bold tracking-[-0.01em]">{explorerHeader.title}</h1>
        </div>
        <span className="text-sm text-(--uncf-ink-3)">{explorerHeader.source}</span>
        <span className="rounded-full bg-(--uncf-warn-bg) px-3 py-0.75 text-[13px] font-semibold text-(--uncf-orange-ink)">
          {explorerHeader.sampleBadge}
        </span>
        <span className="flex-1" />
        {/* Export isn't built yet, so the button is off until a tab wires it up. */}
        <button
          type="button"
          disabled
          title="Export isn't built yet."
          className="inline-flex items-center gap-2 rounded-md border border-(--uncf-line-2) bg-(--uncf-surface) px-4 py-2 font-medium whitespace-nowrap disabled:cursor-not-allowed disabled:opacity-60"
        >
          <DownloadIcon />
          {explorerHeader.exportLabel}
        </button>
      </div>
    </header>
  );
}

/** The blue square logo from the design. */
function ExplorerMark() {
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

/** The design's download arrow. */
function DownloadIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" aria-hidden>
      <path
        d="M8 2v8M4.5 6.5 8 10l3.5-3.5M2.5 13.5h11"
        stroke="currentColor"
        strokeWidth="1.6"
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
