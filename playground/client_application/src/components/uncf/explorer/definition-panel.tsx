import type { ResultsMeta } from "@/app/(app)/uncf/data";

import type { Bar, BarSection } from "./bars";
import type { DetailMode } from "./explorer-controls";

const MISSING_KEY = {
  hidden: { label: "Hidden", text: "Fewer than 10 students, so the number is hidden to protect privacy. It does not mean 0." },
  not_yet: { label: "Not available yet", text: "These students haven't reached this point yet." },
  not_reported: { label: "Not reported", text: "The school's file doesn't include what this needs yet." },
} as const;

type DefinitionPanelProps = {
  meta: ResultsMeta;
  everyone: Bar | null;
  sections: BarSection[];
  /** Students left out of the all-students rate, e.g. gateway requirement or result unknown. */
  leftOut: number | null;
  mode: DetailMode;
};

/** What the chart's number means, sitting beside the chart: definition, how it's counted, who, limits, and missing states. */
export function DefinitionPanel({ meta, everyone, sections, leftOut, mode }: DefinitionPanelProps) {
  const { definition } = meta;
  const states = new Set(sections.flatMap((section) => [...section.bars, ...section.hidden]).map((bar) => bar.state));
  if (everyone) states.add(everyone.state);
  const missing = (["hidden", "not_yet", "not_reported"] as const).filter((state) => states.has(state));

  return (
    <aside aria-labelledby="definition-heading" className="flex flex-col gap-5 self-start rounded-2xl border bg-card p-5 sm:p-6 lg:sticky lg:top-6">
      <div className="flex flex-col gap-2">
        <p className="text-[11px] font-semibold tracking-wider text-muted-foreground uppercase">What this means</p>
        <h2 id="definition-heading" className="text-xl font-semibold tracking-tight">
          {definition.name}
        </h2>
        <p className="text-xs text-muted-foreground">PDP name: {definition.pdp_name}</p>
        <p className="text-base leading-relaxed">{definition.what}</p>
      </div>

      <div className="flex flex-col gap-2 rounded-xl bg-muted/60 p-4">
        <h3 className="text-[11px] font-semibold tracking-wider text-muted-foreground uppercase">How it is worked out</h3>
        <p className="text-sm">{definition.how}</p>
        {everyone?.state === "ok" && (
          <p className="text-sm text-muted-foreground tabular-nums">
            All students: {(everyone.numerator as number).toLocaleString("en-US")} of{" "}
            {(everyone.denominator as number).toLocaleString("en-US")}
          </p>
        )}
      </div>

      <div className="flex flex-col gap-1.5">
        <h3 className="text-[11px] font-semibold tracking-wider text-muted-foreground uppercase">Who is counted</h3>
        <p className="text-sm text-muted-foreground">{definition.who}</p>
      </div>

      <div className="flex flex-col gap-1.5">
        <h3 className="text-[11px] font-semibold tracking-wider text-muted-foreground uppercase">Keep in mind</h3>
        <ul className="flex list-disc flex-col gap-1.5 pl-4 text-sm text-muted-foreground">
          {definition.limits.map((limit) => (
            <li key={limit}>{limit}</li>
          ))}
          {leftOut !== null && leftOut > 0 && (
            <li>
              {leftOut.toLocaleString("en-US")} students with an unknown requirement or result are left out of the rate, not
              counted as 0.
            </li>
          )}
          <li>A gap shows a difference between groups, not its cause.</li>
        </ul>
      </div>

      {missing.length > 0 && (
        <div className="flex flex-col gap-3 border-t pt-4">
          <h3 className="text-[11px] font-semibold tracking-wider text-muted-foreground uppercase">Why some numbers are missing</h3>
          {missing.map((state) => (
            <div key={state} className="flex items-start gap-2.5 text-sm">
              <span
                className={
                  state === "hidden"
                    ? "shrink-0 rounded-full border border-dashed border-foreground/60 px-2 py-0.5 text-xs font-semibold"
                    : "shrink-0 rounded-full bg-muted px-2 py-0.5 text-xs font-semibold"
                }
              >
                {MISSING_KEY[state].label}
              </span>
              <span className="text-muted-foreground">{MISSING_KEY[state].text}</span>
            </div>
          ))}
        </div>
      )}

      <dl className="grid gap-1 border-t pt-4 text-xs text-muted-foreground">
        <div>
          <dt className="inline font-medium text-foreground">Source: </dt>
          <dd className="inline">{meta.source}</dd>
        </div>
        <div>
          <dt className="inline font-medium text-foreground">Data loaded: </dt>
          <dd className="inline">{formatLoadedAt(meta.loaded_at)}</dd>
        </div>
        {mode === "analyst" && (
          <div>
            <dt className="inline font-medium text-foreground">Grouped by: </dt>
            <dd className="inline">{meta.group_by.join(" × ")}</dd>
          </div>
        )}
      </dl>
    </aside>
  );
}

/** "2026-11-08T22:57:20" -> "Nov 8, 2026". */
function formatLoadedAt(loadedAt: string): string {
  const date = new Date(loadedAt);
  return Number.isNaN(date.getTime())
    ? loadedAt
    : date.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}
