import { formatPercent } from "@/components/uncf/explorer/bars";
import { cn } from "@/lib/utils";

import type { CardContent } from "./card-model";

const UNKNOWN_FILL = "repeating-linear-gradient(135deg, #4338ca 0 3px, #c7d2fe 3px 6px)";
const STATE_TEXT = { hidden: "Hidden to protect privacy", not_yet: "Not available yet", not_reported: "Not reported" } as const;

type InsightCardProps = {
  content: CardContent;
  /** The user's takeaway; empty shows a placeholder so the preview never pretends a sentence was written. */
  takeaway: string;
  source: string;
  loadedAt: string;
};

/** One Letter page (8.5 × 11 in at 96 px per inch) that carries its own definition, limits and source. */
export function InsightCard({ content, takeaway, source, loadedAt }: InsightCardProps) {
  const many = content.rows.length > 6;
  const empty = takeaway.trim().length === 0;
  // Keep class years like "2022-23" on one line.
  const headline = empty ? "Your one-sentence takeaway goes here." : takeaway.replace(/(\d)-(\d)/g, "$1‑$2");
  return (
    <article
      aria-label="Insight card"
      className="flex h-[1056px] w-[816px] flex-col overflow-hidden bg-white px-[68px] pt-[52px] pb-[48px] text-[#0a0a0b]"
    >
      <header className="flex items-center justify-between gap-4 border-b border-zinc-300 pb-3.5">
        <span className="text-sm font-semibold tracking-tight">Student Success Explorer</span>
        <span className="flex items-center gap-2.5">
          <span className="text-xs font-medium text-zinc-600">Insight card</span>
          <span className="inline-flex items-center gap-1.5 rounded-full border border-amber-700 px-2.5 py-0.5 text-xs font-semibold text-amber-900">
            <span aria-hidden className="size-1.5 rounded-full bg-amber-700" />
            Synthetic sample data
          </span>
        </span>
      </header>

      <div className="mt-6 flex flex-col gap-2.5">
        <span className="text-[12.5px] font-semibold tracking-wide text-indigo-800">{content.eyebrow}</span>
        <h2 className={cn("text-balance font-semibold leading-tight tracking-tight", many || takeaway.length > 130 ? "text-[21px]" : "text-2xl", empty && "text-zinc-400")}>
          {headline}
        </h2>
      </div>

      <div className="mt-4 flex flex-wrap gap-2 text-[13px]">
        <span className="rounded-full bg-zinc-100 px-2.5 py-1 text-zinc-800"><strong className="font-semibold">Compared by</strong> {content.compared}</span>
        <span className="rounded-full bg-zinc-100 px-2.5 py-1 text-zinc-800"><strong className="font-semibold">{content.baseLabel}</strong> {content.baseCount}</span>
      </div>

      <figure className={cn("mt-4 flex flex-col rounded-2xl border border-zinc-300 px-5 py-4", many ? "gap-1.5" : "gap-2.5")}>
        <figcaption className="text-sm font-semibold text-zinc-900">{content.caption}</figcaption>
        {content.rows.map((row) => (
          <div key={row.key} className={cn("flex items-center gap-4", row.isAll && "border-t border-zinc-200 pt-2")}>
            <span className={cn("w-44 shrink-0 leading-tight", many ? "text-[13px]" : "text-[14.5px]", row.isAll ? "font-bold" : "font-semibold", row.isUnknown && "text-zinc-600")}>
              {row.label}
            </span>
            {row.state === "ok" && row.percent !== null ? (
              <>
                <span className={cn("relative flex-1 rounded-full border border-zinc-200 bg-zinc-100", many ? "h-2.5" : "h-4")}>
                  <span
                    className={cn("absolute inset-y-0 left-0 rounded-full", row.isAll ? "bg-zinc-700" : "bg-indigo-700")}
                    style={{ width: `${row.percent}%`, background: row.isUnknown ? UNKNOWN_FILL : undefined }}
                  />
                </span>
                <span className={cn("flex shrink-0 justify-end tabular-nums", many ? "w-40 flex-row items-baseline gap-2" : "w-28 flex-col items-end")}>
                  <span className={cn("font-semibold tracking-tight", many ? "text-[15px]" : "text-xl", row.isAll ? "text-zinc-900" : "text-indigo-800")}>
                    {formatPercent(row.percent)}
                  </span>
                  <span className="text-[11.5px] text-zinc-600">
                    {(row.numerator as number).toLocaleString("en-US")} of {(row.denominator as number).toLocaleString("en-US")}
                  </span>
                </span>
              </>
            ) : (
              <>
                <span className={cn("flex-1 rounded-full", many ? "h-2.5" : "h-4", row.state === "hidden" ? "border border-dashed border-zinc-500" : "bg-zinc-100")} />
                <span className={cn("shrink-0 text-right text-xs font-semibold text-zinc-800", many ? "w-40" : "w-28")}>{STATE_TEXT[row.state as keyof typeof STATE_TEXT]}</span>
              </>
            )}
          </div>
        ))}
        <span className="text-xs text-zinc-600">{content.footnote}</span>
      </figure>

      <div className={cn("grid grid-cols-2 gap-7", many ? "mt-3" : "mt-5")}>
        <div className="flex flex-col gap-1.5">
          <h3 className="text-xs font-semibold tracking-wider text-zinc-600 uppercase">What it means</h3>
          <p className={cn("leading-snug", many ? "text-[13.5px]" : "text-[15px]")}>{content.what}</p>
        </div>
        <div className="flex flex-col gap-1.5">
          <h3 className="text-xs font-semibold tracking-wider text-zinc-600 uppercase">Who is counted</h3>
          <p className={cn("leading-snug", many ? "text-[13.5px]" : "text-[15px]")}>{content.who}</p>
        </div>
      </div>

      <div className={cn("flex flex-col gap-1.5", many ? "mt-3" : "mt-4")}>
        <h3 className="text-xs font-semibold tracking-wider text-zinc-600 uppercase">Keep in mind</h3>
        <ul className={cn("flex list-disc flex-col gap-1 pl-4 leading-snug", many ? "text-[13.5px]" : "text-[15px]")}>
          {content.limits.map((limit) => (
            <li key={limit}>{limit}</li>
          ))}
        </ul>
      </div>

      <footer className="mt-auto grid grid-cols-3 gap-4 border-t border-zinc-300 pt-3.5 text-xs leading-snug text-zinc-600">
        <div className="flex flex-col">
          <strong className="font-semibold text-zinc-900">Source</strong>
          <span>{source}. Synthetic sample, not real students.</span>
        </div>
        <div className="flex flex-col">
          <strong className="font-semibold text-zinc-900">Data loaded</strong>
          <span>{loadedAt}. Small groups are hidden to protect privacy.</span>
        </div>
        <div className="flex flex-col">
          <strong className="font-semibold text-zinc-900">Made with</strong>
          <span>The Student Success Explorer</span>
        </div>
      </footer>
    </article>
  );
}
